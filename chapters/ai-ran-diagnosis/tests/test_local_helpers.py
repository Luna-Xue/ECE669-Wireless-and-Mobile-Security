"""Local-inference robustness helpers — the regressions that bit us live here:
truncated/odd model JSON and the model omitting recommended_actions."""
from explainer.local import _actions_from_narrative, _backfill, _extract_json


def test_extract_json_from_surrounding_text():
    assert _extract_json('blah {"a": 1, "b": [2,3]} trailing') == {"a": 1, "b": [2, 3]}


def test_extract_json_none_when_absent():
    assert _extract_json("no json at all") is None


def test_actions_from_narrative():
    narr = "Root cause.\n\nWhat to check:\n- check the N2 link\n- verify AMF config\n"
    assert _actions_from_narrative(narr) == ["check the N2 link", "verify AMF config"]


def test_backfill_recovers_actions_from_narrative():
    obj = {
        "root_cause_component": "AMF",
        "narrative": "stuff\nWhat to check:\n- restart AMF\n",
        "confidence": "high",
    }
    out = _backfill(obj)
    assert out["recommended_actions"] == ["restart AMF"]
    assert "causal_chain" in out and "root_cause_summary" in out


def test_backfill_defaults_when_nothing_to_recover():
    out = _backfill({"root_cause_component": "AMF"})
    assert out["recommended_actions"]            # non-empty fallback
    assert out["confidence"] == "medium"          # default
