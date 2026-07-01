"""Batch eval: run an explainer over scenarios x seeds, score multi-metric quality.

  python eval.py [--seeds N] [--noise N] [--scenarios a,b,c] [--inject] [--local]

Default backend is the Claude API explainer (needs ANTHROPIC_API_KEY).
--local uses your fine-tuned model (explainer/local.py; needs requirements-local.txt
and a trained adapter). Labels come from the generator's ground truth.

Beyond root-cause accuracy this also scores causal-chain component precision/recall,
EVIDENCE grounding (cited log IDs vs gold, plus hallucinated IDs), schema-valid
rate, and a per-component breakdown + confusion matrix (see eval_metrics.py).
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import List

from eval_metrics import aggregate, format_report, score_one
from generator import SCENARIOS, generate


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Score an explainer's diagnosis quality on generated data.")
    ap.add_argument("--seeds", type=int, default=3, help="seeds per scenario (0..N-1)")
    ap.add_argument("--noise", type=int, default=8)
    ap.add_argument("--scenarios", default=None, help="comma-separated; default all")
    ap.add_argument("--inject", action="store_true", help="bury a prompt-injection line in every run")
    ap.add_argument("--local", action="store_true", help="use the local fine-tuned explainer instead of the API")
    args = ap.parse_args(argv)

    names = args.scenarios.split(",") if args.scenarios else list(SCENARIOS)
    unknown = [n for n in names if n not in SCENARIOS]
    if unknown:
        print(f"unknown scenarios: {unknown}; choose from {', '.join(SCENARIOS)}")
        return 2

    if args.local:
        from explainer.local import diagnose as run_diagnose
        backend = "local model"
    else:
        from explainer import diagnose as run_diagnose
        backend = "Claude API"

    print(f"backend: {backend} | {len(names)} scenarios x {args.seeds} seeds "
          f"(noise={args.noise}, inject={args.inject})\n")

    records = []  # for aggregate()
    for name in names:
        for seed in range(args.seeds):
            gen = generate(name, seed=seed, noise_level=args.noise, inject=args.inject)
            truth = gen.ground_truth.root_cause_component
            log_ids = [l.id for l in gen.logs]
            t0 = time.monotonic()
            try:
                r = run_diagnose(gen.logs)
            except Exception as exc:  # a bad example is a data point, not a fatal abort
                print(f"  [ERR ] {name:<18} seed={seed}  diagnosis failed: {str(exc)[:60]}")
                records.append({"gold": truth, "pred": None, "parsed": False, "metrics": None})
                continue
            dt = time.monotonic() - t0
            m = score_one(r, gen.ground_truth, log_ids)
            records.append({"gold": truth, "pred": r.root_cause_component, "parsed": True, "metrics": m})
            mark = "PASS" if m["root_hit"] else "FAIL"
            halluc = f" HALLUC={','.join(m['hallucinated'])}" if m["hallucinated"] else ""
            print(f"  [{mark}] {name:<18} seed={seed}  pred={r.root_cause_component:<10} "
                  f"truth={truth:<10} ev_r={m['evidence_recall']*100:3.0f}% conf={r.confidence:<6} {dt:5.1f}s{halluc}")

    print("\n" + "=" * 60)
    print(format_report(aggregate(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
