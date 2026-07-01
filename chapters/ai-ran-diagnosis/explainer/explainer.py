"""The API explanation layer: O-RAN logs in, root-cause diagnosis out, via Claude.

The LLM only understands and proposes — it is pinned to the DiagnosisResult
schema and never emits free-form commands. Prompt + log framing come from
core.prompt, shared with the local explainer and the training-data builder.
"""
from __future__ import annotations

import os
from typing import List, Optional

import anthropic

from core.diagnosis import DiagnosisResult
from core.log_event import LogEvent
from core.prompt import SYSTEM_PROMPT, build_user_message

# Default per the Claude API reference; override for cheaper runs etc.
DEFAULT_MODEL = os.environ.get("ORAN_EXPLAINER_MODEL", "claude-opus-4-8")


def diagnose(
    logs: List[LogEvent],
    *,
    model: str = DEFAULT_MODEL,
    client: Optional[anthropic.Anthropic] = None,
) -> DiagnosisResult:
    """Translate a window of O-RAN logs into a root-cause diagnosis via Claude."""
    client = client or anthropic.Anthropic()

    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},  # root-cause tracing is multi-step reasoning
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(logs)}],
        output_format=DiagnosisResult,
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Model refused to diagnose this input (safety stop).")

    result = response.parsed_output
    if result is None:
        raise RuntimeError("Model did not return a parseable diagnosis.")
    return result
