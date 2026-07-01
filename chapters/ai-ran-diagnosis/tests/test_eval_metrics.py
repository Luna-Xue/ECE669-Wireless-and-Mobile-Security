"""Scoring math for eval.py — exercised without a model."""
from eval_metrics import aggregate, score_one


def test_perfect_score():
    gold = {"root_cause_component": "O-RU",
            "chain": [{"component": "O-RU", "log_ids": ["L1", "L2"]},
                      {"component": "O-DU", "log_ids": ["L4"]}]}
    pred = {"root_cause_component": "O-RU",
            "causal_chain": [{"component": "O-RU", "evidence_log_ids": ["L1", "L2"]},
                             {"component": "O-DU", "evidence_log_ids": ["L4"]}]}
    m = score_one(pred, gold, ["L1", "L2", "L3", "L4"])
    assert m["root_hit"]
    assert m["chain_recall"] == 1.0 and m["evidence_recall"] == 1.0
    assert m["hallucinated"] == [] and m["hallucination_rate"] == 0.0


def test_hallucination_and_miss():
    gold = {"root_cause_component": "O-RU", "chain": [{"component": "O-RU", "log_ids": ["L1"]}]}
    pred = {"root_cause_component": "O-DU",
            "causal_chain": [{"component": "O-DU", "evidence_log_ids": ["L9"]}]}
    m = score_one(pred, gold, ["L1"])          # L9 is not a real line
    assert not m["root_hit"]
    assert m["hallucinated"] == ["L9"] and m["hallucination_rate"] == 1.0
    assert m["evidence_recall"] == 0.0


def test_root_cause_normalization():
    gold = {"root_cause_component": "O_RU", "chain": []}
    pred = {"root_cause_component": "o-ru", "causal_chain": []}
    assert score_one(pred, gold, [])["root_hit"]   # O_RU == o-ru after normalization


def test_aggregate_counts_unparsed_against_schema_rate():
    recs = [
        {"gold": "O-RU", "pred": "O-RU", "parsed": True,
         "metrics": {"root_hit": True, "chain_precision": 1, "chain_recall": 1,
                     "evidence_precision": 1, "evidence_recall": 1,
                     "hallucination_rate": 0, "hallucinated": []}},
        {"gold": "AMF", "pred": None, "parsed": False, "metrics": None},
    ]
    agg = aggregate(recs)
    assert agg["n"] == 2
    assert agg["schema_valid_rate"] == 0.5
    assert agg["root_cause_accuracy"] == 1.0          # over parsed only
    assert agg["per_component"]["amf"]["recall"] == 0.0
