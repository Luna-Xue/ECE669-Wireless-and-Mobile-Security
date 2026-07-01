"""Training-data builder invariants — every gold target must be schema-valid
and evidence-grounded (this is what the model imitates)."""
from core.diagnosis import DiagnosisResult
from generator import generate
from training.dataset import build_dataset, to_target


def test_targets_validate_against_schema():
    train, val = build_dataset(train_seeds=range(0, 2), val_seeds=range(2, 3))
    assert train and val
    for r in train + val:
        # raises if the assistant target is missing a required field
        DiagnosisResult.model_validate_json(r["messages"][-1]["content"])


def test_examples_have_three_turns():
    train, _ = build_dataset(train_seeds=range(0, 1), val_seeds=range(0, 0))
    roles = [m["role"] for m in train[0]["messages"]]
    assert roles == ["system", "user", "assistant"]


def test_to_target_evidence_is_grounded():
    g = generate("ngap_amf_down", seed=5, noise_level=8)
    t = to_target(g)
    real = {l.id for l in g.logs}
    for step in t.causal_chain:
        for lid in step.evidence_log_ids:
            assert lid in real


def test_loso_split_excludes_scenario():
    others = [s for s in ("prb_exhaustion", "ngap_amf_down", "sync_loss") if s != "sync_loss"]
    train, _ = build_dataset(scenarios=others, train_seeds=range(0, 2), val_seeds=range(0, 0))
    roots = {DiagnosisResult.model_validate_json(r["messages"][-1]["content"]).root_cause_component
             for r in train}
    assert "O-RU" not in roots  # sync_loss (root O-RU) was excluded
