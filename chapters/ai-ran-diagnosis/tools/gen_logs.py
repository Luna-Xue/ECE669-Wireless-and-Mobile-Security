"""Freely synthesize new O-RAN/5GC log windows — simulate "newly collected logs".

Each window is written as a clean .log file (just the log lines, no answer) that
looks like captured output. An optional <name>.truth.json sidecar records the
ground truth (root cause + causal chain) so you can score the model afterwards.
Feed any .log back through tools/analyze_logs.py, or paste it into the UI.

Examples:
  python tools/gen_logs.py sync_loss --seed 123 --noise 8          # one window -> stdout
  python tools/gen_logs.py sync_loss --seed 123 --out collected/win1.log
  python tools/gen_logs.py --all --seeds 100-109 --outdir collected/
  python tools/gen_logs.py --random 20 --outdir collected/         # 20 varied windows
  python tools/gen_logs.py --list                                  # show scenarios
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

# repo importable no matter where this is launched from
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from core.log_event import render_logs          # noqa: E402
from generator import SCENARIOS, generate        # noqa: E402


def _parse_seeds(spec: str):
    if spec is None:
        return None
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def _truth(gen, seed, noise, inject) -> dict:
    gt = gen.ground_truth
    return {
        "scenario": gen.name, "seed": seed, "noise": noise, "inject": inject,
        "root_cause_component": gt.root_cause_component,
        "root_cause_summary": gt.root_cause_summary,
        "causal_chain": [
            {"component": s.component, "event": s.event, "evidence_log_ids": s.log_ids}
            for s in gt.chain
        ],
        "recommended_actions": gt.recommended_actions,
    }


def _write(gen, path, fmt, seed, noise, inject, want_truth) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump([l.model_dump() for l in gen.logs], f, ensure_ascii=False, indent=1)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_logs(gen.logs) + "\n")
    if want_truth:
        base = path[:-len(".log")] if path.endswith(".log") else os.path.splitext(path)[0]
        with open(base + ".truth.json", "w", encoding="utf-8") as f:
            json.dump(_truth(gen, seed, noise, inject), f, ensure_ascii=False, indent=2)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Synthesize new O-RAN log windows (simulate collected logs).")
    ap.add_argument("scenario", nargs="?", help="scenario name (omit with --all/--random)")
    ap.add_argument("--list", action="store_true", help="list scenarios and exit")
    ap.add_argument("--all", action="store_true", help="every scenario")
    ap.add_argument("--random", type=int, metavar="N", help="N windows: random scenario/seed/noise/inject")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", help="range or list, e.g. 100-109 or 1,4,9 (overrides --seed)")
    ap.add_argument("--noise", type=int, default=6, help="background noise lines")
    ap.add_argument("--noise-range", help="for --random, e.g. 2-14", default="2-14")
    ap.add_argument("--inject", action="store_true", help="bury a prompt-injection line")
    ap.add_argument("--augment", action="store_true",
                    help="harder data: distractor WARN/ERROR noise + time jitter + paraphrases")
    ap.add_argument("--rng", type=int, help="seed the randomizer for a reproducible --random batch")
    ap.add_argument("--out", help="write a single window to this .log file")
    ap.add_argument("--outdir", help="write a batch of windows into this directory")
    ap.add_argument("--format", choices=["txt", "json"], default="txt")
    ap.add_argument("--no-truth", action="store_true", help="do not write the .truth.json sidecar")
    args = ap.parse_args(argv)

    if args.list or (not args.scenario and not args.all and not args.random):
        print("scenarios:", ", ".join(SCENARIOS))
        if not args.list:
            print("\npick one, or use --all / --random N. See --help.")
        return 0

    rng = random.Random(args.rng)
    want_truth = not args.no_truth

    # build the job list: (scenario, seed, noise, inject)
    jobs = []
    if args.random:
        nlo, nhi = _parse_seeds(args.noise_range)[0], _parse_seeds(args.noise_range)[-1]
        names = list(SCENARIOS)
        for _ in range(args.random):
            jobs.append((rng.choice(names), rng.randint(0, 1_000_000),
                         rng.randint(nlo, nhi), rng.random() < 0.15))
    else:
        names = list(SCENARIOS) if args.all else [args.scenario]
        for n in names:
            if n not in SCENARIOS:
                print(f"unknown scenario {n!r}; choose from {', '.join(SCENARIOS)}")
                return 2
        seeds = _parse_seeds(args.seeds) or [args.seed]
        for n in names:
            for s in seeds:
                jobs.append((n, s, args.noise, args.inject))

    # single window to stdout when no destination is given
    if len(jobs) == 1 and not args.out and not args.outdir:
        n, s, noise, inj = jobs[0]
        gen = generate(n, seed=s, noise_level=noise, inject=inj, augment=args.augment)
        print(render_logs(gen.logs))
        if want_truth:
            print(f"\n# ground truth: root_cause={gen.ground_truth.root_cause_component} "
                  f"(scenario={n} seed={s} noise={noise} inject={inj})", file=sys.stderr)
        return 0

    if len(jobs) == 1 and args.out:
        n, s, noise, inj = jobs[0]
        gen = generate(n, seed=s, noise_level=noise, inject=inj, augment=args.augment)
        _write(gen, args.out, args.format, s, noise, inj, want_truth)
        print(f"wrote {args.out}" + ("" if not want_truth else " (+ .truth.json)"))
        return 0

    # batch -> outdir
    outdir = args.outdir or "collected"
    os.makedirs(outdir, exist_ok=True)
    ext = "json" if args.format == "json" else "log"
    written = 0
    for i, (n, s, noise, inj) in enumerate(jobs):
        gen = generate(n, seed=s, noise_level=noise, inject=inj, augment=args.augment)
        tag = f"{n}_s{s}_n{noise}{'_inj' if inj else ''}"
        path = os.path.join(outdir, f"{i:03d}_{tag}.{ext}")
        _write(gen, path, args.format, s, noise, inj, want_truth)
        written += 1
    print(f"wrote {written} windows to {outdir}/" + ("" if not want_truth else " (+ .truth.json sidecars)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
