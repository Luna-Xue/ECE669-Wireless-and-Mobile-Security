"""Declarative model for a synthetic failure scenario.

A scenario is a causal DAG: each FaultNode is an event at a component that emits
log line(s); `caused_by` wires the cause->effect edges. The generator walks this
to (a) render interleaved logs and (b) emit ground truth (root cause + causal
chain + which log IDs justify each step + recommended actions) for free — which
is exactly what makes free, fully-labelled training data possible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from core.log_event import LogEvent


@dataclass
class FaultNode:
    key: str                  # unique within a scenario
    component: str            # O-RAN / 5GC node, e.g. "O-DU", "AMF"
    severity: str             # INFO | WARN | ERROR | CRITICAL
    label: str                # short human description (used in the ground-truth chain)
    messages: List[str]       # one log line each, OAI/Open5GS-flavored text
    caused_by: Optional[str] = None  # parent node key; None => this is the root cause
    delay_ms: int = 300       # emission delay after the parent node
    # Optional alternate phrasings of `messages`, used only with generate(augment=True),
    # to fight lexical memorization. Each entry is a full alternate message list; the
    # canonical `messages` is always one of the choices. May contain {cell}/{rnti}/...
    # placeholders (filled by the generator). Ground truth is unaffected.
    paraphrases: Optional[List[List[str]]] = None


@dataclass
class Scenario:
    name: str
    summary: str              # one-line statement of the root cause
    nodes: List[FaultNode]
    note: str = ""            # e.g. reproducibility caveat on a real testbed
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class ChainStep:
    component: str
    event: str                # node label
    log_ids: List[str]        # IDs of the generated lines that came from this node


@dataclass
class GroundTruth:
    root_cause_component: str
    root_cause_summary: str
    chain: List[ChainStep]    # in causal order, root first
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class GeneratedScenario:
    name: str
    logs: List[LogEvent]      # explainer-facing view — NO ground truth leaked in
    ground_truth: GroundTruth
    note: str = ""
