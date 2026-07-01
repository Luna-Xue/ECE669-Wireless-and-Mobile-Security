"""Diagnosis schema — the LLM (or fine-tuned model) output contract.

Canonical home in core/ because it is shared: the explainer emits it, the
training pipeline builds gold targets in it, and any future model consumes it.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal  # type: ignore


class CausalStep(BaseModel):
    """One node on the root-cause -> downstream-symptom chain."""

    component: str = Field(description="O-RAN/5GC component, e.g. 'O-RU', 'O-DU', 'AMF'.")
    event: str = Field(description="What happened at this component, in plain language.")
    evidence_log_ids: List[str] = Field(
        description="IDs of the log lines that justify this step, e.g. ['L010','L012']."
    )


class DiagnosisResult(BaseModel):
    """Full diagnosis for one window of logs."""

    root_cause_component: str = Field(
        description="The single component where the failure originates."
    )
    root_cause_summary: str = Field(description="One sentence stating the root cause.")
    causal_chain: List[CausalStep] = Field(
        description="Ordered steps from the root cause to the observed symptoms."
    )
    narrative: str = Field(
        description="Human-readable markdown explanation shown to the operator."
    )
    recommended_actions: List[str] = Field(
        description="Concrete next steps an engineer should take."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence in the diagnosis given the evidence."
    )
