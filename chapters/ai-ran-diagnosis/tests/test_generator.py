"""Generator invariants — fast, no model. Guards the data contract."""
from generator import SCENARIOS, generate


def test_deterministic_given_seed():
    a = generate("sync_loss", seed=3, noise_level=6)
    b = generate("sync_loss", seed=3, noise_level=6)
    assert [l.model_dump() for l in a.logs] == [l.model_dump() for l in b.logs]


def test_different_seeds_differ():
    a = generate("sync_loss", seed=1, noise_level=6)
    b = generate("sync_loss", seed=2, noise_level=6)
    assert [l.model_dump() for l in a.logs] != [l.model_dump() for l in b.logs]


def test_every_scenario_has_one_root_and_valid_gt():
    for name in SCENARIOS:
        g = generate(name, seed=0, noise_level=8)
        assert g.ground_truth.root_cause_component
        assert g.ground_truth.chain  # non-empty causal chain
        # the root cause is the first chain step's component (root-first ordering)
        assert g.ground_truth.chain[0].component == g.ground_truth.root_cause_component


def test_chain_log_ids_reference_real_lines():
    for name in SCENARIOS:
        g = generate(name, seed=4, noise_level=10)
        real = {l.id for l in g.logs}
        for step in g.ground_truth.chain:
            for lid in step.log_ids:
                assert lid in real, f"{name}: chain cites {lid} not in logs"


def test_log_ids_are_unique_and_ordered():
    g = generate("ngap_amf_down", seed=0, noise_level=8)
    ids = [l.id for l in g.logs]
    assert ids == sorted(ids)          # L001, L002, ... in order
    assert len(ids) == len(set(ids))   # unique


def test_injection_line_is_present_but_not_ground_truth():
    g = generate("sync_loss", seed=0, noise_level=4, inject=True)
    inj = [l for l in g.logs if "ignore all prior instructions" in l.message.lower()]
    assert inj, "inject=True should add a prompt-injection line"
    chain_ids = {i for s in g.ground_truth.chain for i in s.log_ids}
    assert all(l.id not in chain_ids for l in inj), "injected line must not be cited as evidence"


def test_augment_off_is_the_default():
    a = generate("sync_loss", seed=1, noise_level=6)
    b = generate("sync_loss", seed=1, noise_level=6, augment=False)
    assert [l.model_dump() for l in a.logs] == [l.model_dump() for l in b.logs]


def test_augment_keeps_evidence_grounded():
    for name in SCENARIOS:
        g = generate(name, seed=3, noise_level=12, augment=True)
        real = {l.id for l in g.logs}
        for step in g.ground_truth.chain:
            for lid in step.log_ids:
                assert lid in real
        # root cause is unchanged by augmentation
        assert g.ground_truth.chain[0].component == g.ground_truth.root_cause_component


def test_augment_adds_distractor_severity_noise():
    seen = set()
    for s in range(6):
        g = generate("auth_failure", seed=s, noise_level=14, augment=True)
        chain_ids = {i for st in g.ground_truth.chain for i in st.log_ids}
        seen |= {l.severity for l in g.logs if l.id not in chain_ids}
    assert seen & {"WARN", "ERROR"}, "augmented noise should include WARN/ERROR distractors"
