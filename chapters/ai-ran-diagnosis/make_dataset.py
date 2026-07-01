"""Build the supervised dataset (logs -> diagnosis JSON) for training the explainer.

  python make_dataset.py [--train-seeds N] [--val-seeds N] [--out data]

Pure offline — no API, no GPU. Writes data/train.jsonl and data/val.jsonl;
upload those two files to the Colab notebook to fine-tune your own explainer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from core.diagnosis import DiagnosisResult
from generator import SCENARIOS
from training.dataset import build_dataset


def _write(path: Path, rows: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Build train/val JSONL for fine-tuning the explainer.")
    ap.add_argument("--train-seeds", type=int, default=40)
    ap.add_argument("--val-seeds", type=int, default=8)
    ap.add_argument("--out", default="data")
    ap.add_argument("--exclude", default=None,
                    help="leave one scenario OUT of train/val and write it as test_<scenario>.jsonl "
                         "(leave-one-scenario-out: measures generalization to an UNSEEN failure type)")
    ap.add_argument("--augment", action="store_true",
                    help="harder, less template-y data (distractor noise / time jitter / paraphrases). "
                         "Retrain to benefit — see generator.generate.")
    args = ap.parse_args(argv)

    if args.exclude and args.exclude not in SCENARIOS:
        print(f"unknown --exclude {args.exclude!r}; choose from {', '.join(SCENARIOS)}")
        return 2

    scenarios = [s for s in SCENARIOS if s != args.exclude] if args.exclude else None
    train, val = build_dataset(
        scenarios=scenarios,
        train_seeds=range(0, args.train_seeds),
        val_seeds=range(args.train_seeds, args.train_seeds + args.val_seeds),
        augment=args.augment,
    )

    # Sanity: every assistant target must validate against the schema.
    for r in train + val:
        DiagnosisResult.model_validate_json(r["messages"][-1]["content"])

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    _write(out / "train.jsonl", train)
    _write(out / "val.jsonl", val)
    print(f"wrote {len(train)} train / {len(val)} val examples to {out}/")

    if args.exclude:
        # The held-out scenario across all seeds becomes the LOSO test set. Train on
        # Colab with the train/val above, then score with: analyze_logs / test_explainer
        # / eval --scenarios on this file — it's a failure type the model never saw.
        held, _ = build_dataset(
            scenarios=[args.exclude],
            train_seeds=range(0, args.train_seeds + args.val_seeds),
            val_seeds=range(0, 0),
            augment=args.augment,
        )
        for r in held:
            DiagnosisResult.model_validate_json(r["messages"][-1]["content"])
        test_path = out / f"test_{args.exclude}.jsonl"
        _write(test_path, held)
        print(f"LOSO: excluded {args.exclude!r} from train/val; wrote {len(held)} held-out examples to {test_path}")

    sample = train[0]["messages"]
    print("\n--- sample example ---")
    print("USER (truncated):\n" + sample[1]["content"][:300] + " ...")
    print("\nASSISTANT target (truncated):\n" + sample[2]["content"][:500] + " ...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
