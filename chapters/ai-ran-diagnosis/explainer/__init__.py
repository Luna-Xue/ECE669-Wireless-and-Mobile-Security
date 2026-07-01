"""AI-RAN explainer: O-RAN logs -> human-readable root-cause diagnosis."""
# The API path needs `anthropic`; the local path (explainer.local) must not. Guard
# the import so `from explainer.local import ...` works without anthropic installed.
try:
    from .explainer import DEFAULT_MODEL, diagnose
except ImportError:  # anthropic not installed (local-only setup)
    DEFAULT_MODEL = None

    def diagnose(*_a, **_k):  # type: ignore[misc]
        raise RuntimeError(
            "API explainer unavailable (`pip install anthropic` + ANTHROPIC_API_KEY). "
            "For local inference use explainer.local.diagnose instead."
        )

from .log_event import LogEvent, render_logs
from .schema import CausalStep, DiagnosisResult

__all__ = [
    "diagnose",
    "DEFAULT_MODEL",
    "LogEvent",
    "render_logs",
    "DiagnosisResult",
    "CausalStep",
]
