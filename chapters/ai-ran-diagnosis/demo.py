"""End-to-end harness on GENERATED data.

  python demo.py <scenario> [--seed N] [--noise N] [--inject] [--truth] [--llm]

Offline by default (no API key needed): generates a labelled log window and
prints it. Add --llm to also run the explainer and auto-check its root-cause
call against the generator's ground truth (a tiny built-in eval).
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from core.log_event import render_logs
from generator import SCENARIOS, generate

_RULE = "=" * 72


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate labelled O-RAN/5GC logs and (optionally) diagnose them.")
    parser.add_argument("scenario", nargs="?", help="scenario name (omit to list)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--noise", type=int, default=6, help="background noise lines")
    parser.add_argument("--inject", action="store_true", help="bury a prompt-injection line")
    parser.add_argument("--truth", action="store_true", help="print ground truth")
    parser.add_argument("--llm", action="store_true", help="run the API explainer (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--local", action="store_true", help="run the locally fine-tuned explainer (no API)")
    args = parser.parse_args(argv)

    if not args.scenario:
        print("scenarios:", ", ".join(SCENARIOS))
        return 0
    if args.scenario not in SCENARIOS:
        print(f"unknown scenario {args.scenario!r}; choose from: {', '.join(SCENARIOS)}")
        return 2

    gen = generate(args.scenario, seed=args.seed, noise_level=args.noise, inject=args.inject)

    print(_RULE)
    print(f"GENERATED LOGS  scenario={gen.name} seed={args.seed} noise={args.noise} "
          f"inject={args.inject}  ({len(gen.logs)} lines)")
    if gen.note:
        print(f"note: {gen.note}")
    print(_RULE)
    print(render_logs(gen.logs))

    if args.truth:
        gt = gen.ground_truth
        print("\n" + "-" * 72)
        print("GROUND TRUTH")
        print("-" * 72)
        print(f"root cause component : {gt.root_cause_component}")
        print(f"summary              : {gt.root_cause_summary}")
        print("causal chain:")
        for i, step in enumerate(gt.chain, 1):
            print(f"  {i}. [{step.component}] {step.event}  (logs: {', '.join(step.log_ids)})")

    backend = "local" if args.local else ("api" if args.llm else None)
    if backend:
        print("\n" + _RULE)
        print(f"EXPLAINER DIAGNOSIS  ({'local model' if backend == 'local' else 'Claude API'})")
        print(_RULE)
        try:
            if backend == "local":
                from explainer.local import diagnose as run_diagnose
            else:
                from explainer import diagnose as run_diagnose
            result = run_diagnose(gen.logs)
        except Exception as exc:
            print(f"diagnosis failed: {exc}")
            return 1

        print(f"root cause : {result.root_cause_component} — {result.root_cause_summary}")
        print(f"confidence : {result.confidence}")
        print("\nnarrative:\n" + result.narrative)

        predicted = result.root_cause_component.strip().lower()
        truth = gen.ground_truth.root_cause_component.strip().lower()
        verdict = "PASS" if predicted == truth else "FAIL"
        print(f"\n[eval] root-cause component: predicted={result.root_cause_component!r} "
              f"truth={gen.ground_truth.root_cause_component!r} -> {verdict}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
