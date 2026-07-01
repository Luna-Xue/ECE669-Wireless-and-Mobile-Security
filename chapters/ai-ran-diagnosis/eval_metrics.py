"""Pure scoring of explainer output against generator ground truth.

No model, no I/O, no heavy deps — so these functions are unit-testable and are
reused by eval.py and the pytest suite. Inputs may be DiagnosisResult/GroundTruth
objects OR plain dicts (so tests can build cases without pydantic).

Metrics computed per example:
  - root_hit              : root_cause_component matches (normalized)
  - chain_precision/recall: causal-chain COMPONENT sets vs gold chain components
  - evidence_precision/recall: cited evidence_log_ids vs gold log_ids (sets)
  - hallucinated          : cited IDs that aren't in the actual log window
  - hallucination_rate    : len(hallucinated) / cited

aggregate() rolls these up + a per-component precision/recall/F1 and a confusion
matrix on the root-cause call.
"""
from __future__ import annotations

from typing import Dict, Iterable, List


def _g(obj, attr, default=None):
    """Attribute or dict-key access, so objects and dicts both work."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _norm(s) -> str:
    return (s or "").strip().lower().replace("_", "-")


def _chain_components(obj, key: str) -> List[str]:
    return [_norm(_g(s, "component")) for s in (_g(obj, key) or [])]


def _evidence_ids(obj, chain_key: str, id_key: str) -> set:
    ids = set()
    for step in (_g(obj, chain_key) or []):
        for i in (_g(step, id_key) or []):
            ids.add(i)
    return ids


def _pr(pred_set: set, gold_set: set):
    inter = len(pred_set & gold_set)
    precision = inter / len(pred_set) if pred_set else 0.0
    recall = inter / len(gold_set) if gold_set else 0.0
    return precision, recall


def score_one(pred, gold, log_ids: Iterable[str]) -> Dict:
    """Score one diagnosis against ground truth + the real log-id set."""
    real = set(log_ids)

    pred_chain = set(_chain_components(pred, "causal_chain"))
    gold_chain = set(_chain_components(gold, "chain"))
    chain_p, chain_r = _pr(pred_chain, gold_chain)

    pred_ev = _evidence_ids(pred, "causal_chain", "evidence_log_ids")
    gold_ev = _evidence_ids(gold, "chain", "log_ids")
    ev_p, ev_r = _pr(pred_ev, gold_ev)

    halluc = sorted(i for i in pred_ev if i not in real)

    return {
        "root_hit": _norm(_g(pred, "root_cause_component")) == _norm(_g(gold, "root_cause_component")),
        "chain_precision": chain_p,
        "chain_recall": chain_r,
        "evidence_precision": ev_p,
        "evidence_recall": ev_r,
        "hallucinated": halluc,
        "hallucination_rate": (len(halluc) / len(pred_ev)) if pred_ev else 0.0,
    }


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def aggregate(records: List[Dict]) -> Dict:
    """records: [{"gold": comp, "pred": comp|None, "parsed": bool, "metrics": dict|None}].

    `parsed=False` means the model output didn't yield a valid diagnosis (counts
    against schema-valid rate; excluded from the quality means).
    """
    n = len(records)
    parsed = [r for r in records if r.get("parsed")]
    m = [r["metrics"] for r in parsed if r.get("metrics")]

    labels = sorted({_norm(r["gold"]) for r in records} |
                    {_norm(r["pred"]) for r in parsed if r.get("pred")})
    per_comp, confusion = {}, {}
    for c in labels:
        tp = sum(1 for r in parsed if _norm(r["gold"]) == c and _norm(r["pred"]) == c)
        fp = sum(1 for r in parsed if _norm(r["gold"]) != c and _norm(r["pred"]) == c)
        fn = sum(1 for r in records if _norm(r["gold"]) == c and not
                 (r.get("parsed") and _norm(r["pred"]) == c))
        support = sum(1 for r in records if _norm(r["gold"]) == c)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_comp[c] = {"precision": prec, "recall": rec, "f1": f1, "support": support}
    for r in records:
        g = _norm(r["gold"])
        p = _norm(r["pred"]) if r.get("parsed") and r.get("pred") else "<no-parse>"
        confusion.setdefault(g, {}).setdefault(p, 0)
        confusion[g][p] += 1

    return {
        "n": n,
        "schema_valid_rate": len(parsed) / n if n else 0.0,
        "root_cause_accuracy": _mean([1.0 if r["metrics"]["root_hit"] else 0.0 for r in parsed if r.get("metrics")]),
        "chain_precision": _mean([x["chain_precision"] for x in m]),
        "chain_recall": _mean([x["chain_recall"] for x in m]),
        "evidence_precision": _mean([x["evidence_precision"] for x in m]),
        "evidence_recall": _mean([x["evidence_recall"] for x in m]),
        "hallucination_rate": _mean([x["hallucination_rate"] for x in m]),
        "examples_with_hallucination": sum(1 for x in m if x["hallucinated"]),
        "per_component": per_comp,
        "confusion": confusion,
    }


def format_report(agg: Dict) -> str:
    """Human-readable multi-metric report."""
    lines = []
    lines.append(f"examples            : {agg['n']}")
    lines.append(f"schema-valid rate   : {agg['schema_valid_rate']*100:.0f}%")
    lines.append(f"root-cause accuracy : {agg['root_cause_accuracy']*100:.0f}%")
    lines.append(f"chain  precision/recall (components) : {agg['chain_precision']*100:.0f}% / {agg['chain_recall']*100:.0f}%")
    lines.append(f"evidence precision/recall (log IDs)  : {agg['evidence_precision']*100:.0f}% / {agg['evidence_recall']*100:.0f}%")
    lines.append(f"evidence hallucination rate          : {agg['hallucination_rate']*100:.0f}%  "
                 f"({agg['examples_with_hallucination']} example(s) cited a non-existent ID)")
    lines.append("\nper-component (root cause):")
    lines.append(f"  {'component':<12} {'prec':>5} {'recall':>7} {'f1':>5} {'support':>8}")
    for c, s in sorted(agg["per_component"].items()):
        lines.append(f"  {c:<12} {s['precision']*100:>4.0f}% {s['recall']*100:>6.0f}% {s['f1']*100:>4.0f}% {s['support']:>8}")
    lines.append("\nconfusion (gold -> predicted):")
    for g, preds in sorted(agg["confusion"].items()):
        cells = ", ".join(f"{p}:{c}" for p, c in sorted(preds.items()))
        lines.append(f"  {g:<12} -> {cells}")
    return "\n".join(lines)
