"""Canonical log-event contract shared across the project.

This is the schema the explainer CONSUMES and that every producer emits — the
synthetic generator now, the OAI/Open5GS ingestion layer later. Keeping it in
one place is the whole point: swap the data source, and the explainer is
untouched.

Uses typing.List (not `list[...]`) so the Pydantic model resolves on Python 3.9.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class LogEvent(BaseModel):
    id: str        # stable line ID, e.g. "L010" -> lets the LLM cite evidence
    ts: str        # timestamp string (normalized; real generator/ingestion emits this)
    component: str  # e.g. "O-RU", "O-DU", "O-CU-CP", "O-CU-UP", "AMF", "SMF", "UPF"
    severity: str   # INFO | WARN | ERROR | CRITICAL
    message: str


def render_logs(logs: List[LogEvent]) -> str:
    """Flatten logs into the text block the LLM reads strictly as DATA.

    Stable [ID] prefixes are what make the model's evidence citations point at
    real lines.
    """
    return "\n".join(
        f"[{e.id}] {e.ts} {e.severity:<8} {e.component:<12} {e.message}"
        for e in logs
    )
