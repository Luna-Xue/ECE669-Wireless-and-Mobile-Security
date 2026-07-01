"""Re-export of the canonical LogEvent contract (now lives in core/).

Kept so existing `explainer.log_event` imports keep working unchanged.
"""
from core.log_event import LogEvent, render_logs  # noqa: F401

__all__ = ["LogEvent", "render_logs"]
