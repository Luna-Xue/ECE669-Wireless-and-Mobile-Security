"""Standalone test for a trained explainer (base + LoRA adapter).

Loads the adapter from disk, runs the held-out val set, prints raw output for a
few examples, and reports valid-JSON rate + root-cause accuracy. Self-contained:
needs only torch / transformers / peft + val.jsonl + the adapter — NO project
imports, so it runs unchanged on Colab or locally. Because it loads from disk, it
works after a Colab disconnect as long as the adapter is in Drive (no retrain).

Colab:
    # adapter in My Drive/ORAN_Agent/explainer-lora, val in .../data/val.jsonl
    !python test_explainer.py
Local (Mac, after downloading the adapter):
    pip install -r requirements-local.txt
    python test_explainer.py --adapter models/explainer-lora --val data/val.jsonl

Paths auto-detect the Colab Drive layout first, then the local layout; override
with --adapter / --val.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import List, Optional

# Required fields of a valid diagnosis (mirrors core.diagnosis.DiagnosisResult).
# Kept inline so this script stays self-contained / Colab-portable.
_REQUIRED = ["root_cause_component", "root_cause_summary", "causal_chain",
             "narrative", "recommended_actions", "confidence"]


def _first_existing(paths: List[str]) -> str:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return paths[-1]  # report the last candidate even if missing, for a clear error


def _extract_json(text: str) -> Optional[dict]:
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < 0:
        return None
    try:
        return json.loads(text[i:j + 1])
    except Exception:
        return None


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Test a trained explainer on the val set.")
    ap.add_argument("--base", default="Qwen/Qwen2.5-1.5B-Instruct", help="base model id")
    ap.add_argument("--adapter", default=None, help="LoRA adapter dir (auto-detected if omitted)")
    ap.add_argument("--val", default=None, help="val.jsonl path (auto-detected if omitted)")
    ap.add_argument("--n", type=int, default=20, help="how many val examples to test")
    ap.add_argument("--show", type=int, default=2, help="how many raw generations to print in full")
    ap.add_argument("--max-new-tokens", type=int, default=1024)
    args = ap.parse_args(argv)

    adapter = args.adapter or _first_existing([
        "/content/drive/MyDrive/ORAN_Agent/explainer-lora",
        "models/explainer-lora",
    ])
    val = args.val or _first_existing([
        "/content/drive/MyDrive/ORAN_Agent/data/val.jsonl",
        "data/val.jsonl",
    ])
    if not os.path.exists(val):
        print(f"val file not found: {val} (pass --val)")
        return 2
    print(f"base    = {args.base}")
    print(f"adapter = {adapter}")
    print(f"val     = {val}\n")

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        print(f"missing deps ({exc}). Install: pip install -r requirements-local.txt")
        return 1

    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32  # MPS fp16 -> garbage; use fp32 locally
    print(f"device  = {device} ({dtype})\n")

    tok = AutoTokenizer.from_pretrained(args.base)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.base, torch_dtype=dtype)
    if os.path.isdir(adapter):
        model = PeftModel.from_pretrained(model, adapter)
    else:
        print(f"WARNING: adapter dir not found at {adapter} — testing the BASE model only.\n")
    model = model.to(device).eval()
    model.config.use_cache = True

    def predict(messages_wo_assistant) -> str:
        prompt = tok.apply_chat_template(messages_wo_assistant, tokenize=False, add_generation_prompt=True)
        inp = tok(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inp,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,  # greedy; no repetition_penalty (it distorts structured JSON)
                eos_token_id=tok.eos_token_id,
                pad_token_id=tok.pad_token_id,
            )
        return tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)

    rows = [json.loads(l) for l in open(val, encoding="utf-8")][: args.n]
    n = ok = valid = schema_ok = halluc_examples = 0
    for k, ex in enumerate(rows):
        gold = json.loads(ex["messages"][-1]["content"])["root_cause_component"]
        # real log IDs in this window — to catch hallucinated evidence citations
        real_ids = set(re.findall(r"\[(L\d+)\]", ex["messages"][-2]["content"]))
        raw = predict(ex["messages"][:-1])
        if k < args.show:
            print(f"--- RAW OUTPUT [{k}] (gold={gold}, chars={len(raw)}) ---")
            print(raw)
            print("--- end ---\n")
        obj = _extract_json(raw)
        pred = (obj or {}).get("root_cause_component", "<parse-fail>")
        if obj is not None:
            valid += 1
        # schema-lite: all required fields present (test_explainer used to skip this,
        # which is how the missing-recommended_actions bug went unnoticed)
        has_schema = obj is not None and all(key in obj for key in _REQUIRED)
        schema_ok += int(has_schema)
        # evidence hallucination: any cited ID not in the actual logs
        cited = [i for s in (obj or {}).get("causal_chain", []) for i in s.get("evidence_log_ids", [])]
        halluc = [i for i in cited if i not in real_ids]
        halluc_examples += int(bool(halluc))
        hit = str(pred).strip().lower() == gold.strip().lower()
        n += 1
        ok += int(hit)
        flag = "" if not halluc else f"  HALLUC={','.join(halluc)}"
        sflag = "" if has_schema else "  [schema!]"
        print(f"[{'PASS' if hit else 'FAIL'}] pred={str(pred):<14} gold={gold}{sflag}{flag}")

    print(f"\nvalid JSON       : {valid}/{n} ({100 * valid / max(n, 1):.0f}%)")
    print(f"schema-valid     : {schema_ok}/{n} ({100 * schema_ok / max(n, 1):.0f}%)  (all required fields)")
    print(f"root-cause acc.  : {ok}/{n} ({100 * ok / max(n, 1):.0f}%)")
    print(f"evidence halluc. : {halluc_examples}/{n} example(s) cited a non-existent log ID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
