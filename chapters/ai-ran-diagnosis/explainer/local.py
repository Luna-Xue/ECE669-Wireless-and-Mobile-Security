"""Local explainer: the SAME diagnose() contract as the API path, powered by a
fine-tuned model (base + LoRA adapter) instead of Claude. No API key.

Loads on CPU/MPS WITHOUT 4-bit quantization (bitsandbytes is CUDA-only) — fine
for a 1.5B model. Heavy deps (torch/transformers/peft) live in
requirements-local.txt; install them before using this.

Prompt + log framing come from core.prompt, identical to what the model was
trained on (training/dataset.py) and to the API explainer.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

from core.diagnosis import DiagnosisResult
from core.log_event import LogEvent
from core.prompt import SYSTEM_PROMPT, build_user_message

DEFAULT_BASE = os.environ.get("ORAN_LOCAL_BASE", "Qwen/Qwen2.5-1.5B-Instruct")


def _default_adapter() -> str:
    """ORAN_LOCAL_ADAPTER if set, else the first adapter dir that exists.
    Avoids silently running BASE-only when the adapter sits at the repo root."""
    env = os.environ.get("ORAN_LOCAL_ADAPTER")
    if env:
        return env
    _repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for cand in (os.path.join(_repo, "explainer-lora"), "explainer-lora", "models/explainer-lora"):
        if os.path.isdir(cand):
            return cand
    return "models/explainer-lora"


DEFAULT_ADAPTER = _default_adapter()


def _extract_json(text: str) -> Optional[dict]:
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < 0:
        return None
    try:
        return json.loads(text[i:j + 1])
    except Exception:
        return None


def _actions_from_narrative(narr: str) -> List[str]:
    """The local model often folds the actions into the narrative under a
    'What to check:' heading instead of emitting recommended_actions. Recover them."""
    out, capture = [], False
    for line in (narr or "").splitlines():
        s = line.strip()
        if s.lower().startswith("what to check"):
            capture = True
        elif capture and s.startswith("-"):
            out.append(s.lstrip("-* ").strip())
    return out


def _backfill(obj: dict) -> dict:
    """Tolerate the model omitting non-root fields so a valid root-cause call
    isn't lost to a missing optional field."""
    obj.setdefault("root_cause_summary", "")
    obj.setdefault("causal_chain", [])
    obj.setdefault("narrative", obj.get("root_cause_summary", ""))
    if not obj.get("recommended_actions"):
        obj["recommended_actions"] = (
            _actions_from_narrative(obj.get("narrative", "")) or ["Investigate the root-cause component."]
        )
    obj.setdefault("confidence", "medium")
    return obj


class LocalExplainer:
    """Loads base + LoRA adapter once; call .diagnose(logs) per window."""

    def __init__(
        self,
        adapter_path: str = DEFAULT_ADAPTER,
        base_model: str = DEFAULT_BASE,
        device: Optional[str] = None,
        max_new_tokens: int = 1024,  # 5-step chain + narrative can exceed 512 -> truncated JSON
    ):
        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "local inference needs torch/transformers/peft — "
                "`pip install -r requirements-local.txt`"
            ) from exc

        self._torch = torch
        if device is None:
            device = "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu"
        self.device = device
        # MPS fp16 produces NaNs/garbage for this model — fp16 only on CUDA.
        dtype = torch.float16 if device == "cuda" else torch.float32

        self.tok = AutoTokenizer.from_pretrained(base_model)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token

        model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=dtype)
        if adapter_path and os.path.isdir(adapter_path):
            model = PeftModel.from_pretrained(model, adapter_path)
        else:
            print(f"[LocalExplainer] adapter not found at {adapter_path!r} — running BASE model only "
                  "(set ORAN_LOCAL_ADAPTER or pass adapter_path).")
        self.model = model.to(device).eval()
        self.max_new_tokens = max_new_tokens

    def _generate(self, logs: List[LogEvent]) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(logs)},
        ]
        prompt = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tok(prompt, return_tensors="pt").to(self.device)
        with self._torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.1,
                eos_token_id=self.tok.eos_token_id,
                pad_token_id=self.tok.pad_token_id,
            )
        return self.tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    def diagnose(self, logs: List[LogEvent]) -> DiagnosisResult:
        text = self._generate(logs)
        obj = _extract_json(text)
        if obj is None:
            raise RuntimeError("model output was not parseable JSON:\n" + text[:500])
        return DiagnosisResult.model_validate(_backfill(obj))


# Module-level convenience mirroring explainer.diagnose: cache one explainer.
_default: Optional[LocalExplainer] = None


def diagnose(logs: List[LogEvent], **kwargs) -> DiagnosisResult:
    global _default
    if _default is None:
        _default = LocalExplainer(**kwargs)
    return _default.diagnose(logs)
