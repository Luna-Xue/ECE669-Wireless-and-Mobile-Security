"""Run YOUR trained model on collected log files and print the analysis.

Reads windows produced by tools/gen_logs.py — either the .log text format
(`[ID] ts SEVERITY COMPONENT message`) or a JSON list of log dicts — loads
base + your LoRA adapter via explainer.local, and prints the diagnosis. If a
<name>.truth.json sidecar is present, it scores the root cause and flags any
hallucinated evidence IDs (cited line that isn't in the window).

Examples:
  python tools/analyze_logs.py collected/win1.log
  python tools/analyze_logs.py collected/*.log
  python tools/gen_logs.py sync_loss --seed 7 | python tools/analyze_logs.py -
  python tools/analyze_logs.py collected/win1.log --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("ORAN_LOCAL_ADAPTER", os.path.join(_REPO, "explainer-lora"))

from core.log_event import LogEvent              # noqa: E402

_LINE = re.compile(r"^\[([^\]]+)\]\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)$")


def parse_logs(text: str):
    text = text.strip()
    if not text:
        return []
    if text[0] in "[{":
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "logs" in data:
                data = data["logs"]
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return [LogEvent(**d) for d in data]
        except Exception:
            pass  # not JSON logs — fall through to text parsing
    logs = []
    for line in text.splitlines():
        m = _LINE.match(line.strip())
        if m:
            logs.append(LogEvent(id=m.group(1), ts=m.group(2), severity=m.group(3),
                                 component=m.group(4), message=m.group(5)))
    return logs


def _truth_path(path: str):
    base = path[:-4] if path.endswith(".log") else os.path.splitext(path)[0]
    cand = base + ".truth.json"
    return cand if os.path.exists(cand) else None


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Diagnose collected log files with your trained model.")
    ap.add_argument("files", nargs="+", help="log files (.log/.json), or '-' for stdin")
    ap.add_argument("--json", help="write the diagnosis JSON here (single-file mode)")
    ap.add_argument("--quiet", action="store_true", help="one line per file (verdict only)")
    args = ap.parse_args(argv)

    from explainer.local import diagnose  # lazy: loads torch/model on first call

    n = ok = scored = 0
    for path in args.files:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        logs = parse_logs(text)
        label = "stdin" if path == "-" else os.path.basename(path)
        if not logs:
            print(f"[{label}] no parseable log lines — skipping")
            continue
        res = diagnose(logs)
        n += 1

        truth = None
        tp = None if path == "-" else _truth_path(path)
        if tp:
            truth = json.load(open(tp, encoding="utf-8"))

        verdict = ""
        if truth:
            scored += 1
            hit = res.root_cause_component.strip().lower() == truth["root_cause_component"].strip().lower()
            ok += int(hit)
            verdict = f"  [{'PASS' if hit else 'FAIL'} vs truth {truth['root_cause_component']}]"

        if args.quiet:
            print(f"[{label}] root_cause={res.root_cause_component} conf={res.confidence}{verdict}")
            continue

        print(f"\n=== {label} ({len(logs)} lines) ===")
        print(f"ROOT CAUSE : {res.root_cause_component} — {res.root_cause_summary}")
        print(f"confidence : {res.confidence}{verdict}")
        print("causal chain:")
        real_ids = {l.id for l in logs}
        halluc = []
        for i, step in enumerate(res.causal_chain, 1):
            bad = [e for e in step.evidence_log_ids if e not in real_ids]
            halluc += bad
            print(f"  {i}. [{step.component}] {step.event}  (evidence: {', '.join(step.evidence_log_ids) or '—'})")
        if halluc:
            print(f"  ⚠ hallucinated evidence IDs (not in the logs): {', '.join(halluc)}")
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                f.write(res.model_dump_json(indent=2))
            print(f"(diagnosis written to {args.json})")

    if scored:
        print(f"\nroot-cause accuracy on scored files: {ok}/{scored} ({100*ok/scored:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
