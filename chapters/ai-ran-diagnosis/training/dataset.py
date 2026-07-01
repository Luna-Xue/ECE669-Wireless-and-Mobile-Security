"""Turn generated scenarios into supervised chat examples for fine-tuning.

Each example is {"messages": [system, user(logs), assistant(diagnosis JSON)]} —
the SAME framing the explainer uses at inference (core.prompt), so a model
trained here is a drop-in local replacement. Targets are built deterministically
from the generator's ground truth (no API, no human labels).

Imports only core + generator (NOT explainer.explainer), so no anthropic dep.
"""
from __future__ import annotations

import random
from typing import Dict, Iterable, List, Optional, Tuple

from core.diagnosis import CausalStep, DiagnosisResult
from core.prompt import SYSTEM_PROMPT, build_user_message
from generator import SCENARIOS, generate
from generator.models import GeneratedScenario


def _narrative(gt) -> str:
    lines = [f"**Root cause — {gt.root_cause_component}.** {gt.root_cause_summary}", "", "How it unfolded:"]
    for i, step in enumerate(gt.chain, 1):
        ev = ", ".join(step.log_ids) if step.log_ids else "—"
        lines.append(f"{i}. [{step.component}] {step.event} (evidence: {ev})")
    if gt.recommended_actions:
        lines += ["", "What to check:"] + [f"- {a}" for a in gt.recommended_actions]
    return "\n".join(lines)


def to_target(gen: GeneratedScenario) -> DiagnosisResult:
    """Gold DiagnosisResult for a generated scenario, from its ground truth."""
    gt = gen.ground_truth
    return DiagnosisResult(
        root_cause_component=gt.root_cause_component,
        root_cause_summary=gt.root_cause_summary,
        causal_chain=[
            CausalStep(component=s.component, event=s.event, evidence_log_ids=s.log_ids)
            for s in gt.chain
        ],
        narrative=_narrative(gt),
        recommended_actions=gt.recommended_actions or ["Investigate the root-cause component."],
        confidence="high",
    )


def build_example(gen: GeneratedScenario) -> Dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(gen.logs)},
            {"role": "assistant", "content": to_target(gen).model_dump_json(indent=2)},
        ]
    }


def build_dataset(
    *,
    scenarios: Optional[List[str]] = None,
    train_seeds: Iterable[int] = range(0, 40),
    val_seeds: Iterable[int] = range(40, 48),
    noise_levels: Tuple[int, ...] = (4, 10),
    inject_ratio: float = 0.1,
    shuffle_seed: int = 0,
    augment: bool = False,
) -> Tuple[List[Dict], List[Dict]]:
    """Return (train, val) lists of chat examples.

    Val uses held-out seeds (same scenarios) -> measures generalization to unseen
    log instances, not unseen failure types.

    augment: harder, less template-y data (distractor noise / time jitter /
    paraphrases) — see generator.generate. Off by default.
    """
    names = scenarios or list(SCENARIOS)
    rng = random.Random(shuffle_seed)

    def make(seeds: Iterable[int]) -> List[Dict]:
        out: List[Dict] = []
        for name in names:
            for s in seeds:
                for nl in noise_levels:
                    inject = rng.random() < inject_ratio
                    out.append(build_example(
                        generate(name, seed=s, noise_level=nl, inject=inject, augment=augment)))
        rng.shuffle(out)
        return out

    return make(train_seeds), make(val_seeds)
