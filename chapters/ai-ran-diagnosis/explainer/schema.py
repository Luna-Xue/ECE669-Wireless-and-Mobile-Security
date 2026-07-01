"""Re-export of the diagnosis schema (canonical home: core/diagnosis.py).

Kept so existing `explainer.schema` imports keep working unchanged.
"""
from core.diagnosis import CausalStep, DiagnosisResult  # noqa: F401

__all__ = ["CausalStep", "DiagnosisResult"]
