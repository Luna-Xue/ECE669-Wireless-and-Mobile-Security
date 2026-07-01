"""Generate notebooks/train_explainer.ipynb (stdlib json only).

Run:  python notebooks/build_ipynb.py
Editing the notebook? Edit the cell sources here and regenerate.
"""
from __future__ import annotations

import json
from pathlib import Path

MD = "markdown"
CODE = "code"

cells = []


def md(src: str) -> None:
    cells.append((MD, src))


def code(src: str) -> None:
    cells.append((CODE, src))


md(
    "# Train your own AI-RAN explainer (Colab, free GPU)\n"
    "\n"
    "Fine-tune a small open model to turn O-RAN/5GC logs into a root-cause "
    "diagnosis. No API key, no local GPU.\n"
    "\n"
    "**Before you start:**\n"
    "1. Runtime -> Change runtime type -> **T4 GPU**.\n"
    "2. Build the dataset locally with `python make_dataset.py --augment` "
    "(harder, less memorizable data -> `train.jsonl`, `val.jsonl`).\n"
    "3. Run the config cell — it mounts Google Drive. Put the two JSONL in the printed "
    "`DATA_DIR` (or upload them when the next cell prompts). The trained adapter is saved to "
    "Drive (`OUTPUT_DIR`), so it survives Colab disconnects.\n"
    "\n"
    "The model learns the same `(logs -> diagnosis JSON)` task the API explainer "
    "does, so it's a drop-in local replacement."
)

code("!pip -q install -U transformers peft accelerate datasets bitsandbytes")

code(
    "# --- config + Google Drive storage (so data + adapter survive Colab disconnects) ---\n"
    "from google.colab import drive\n"
    'drive.mount("/content/drive")   # standard mount point; files live under /content/drive/MyDrive/\n'
    "\n"
    "import os\n"
    'MODEL = "Qwen/Qwen2.5-1.5B-Instruct"   # ungated, fits a free T4. Try -3B-Instruct for more quality.\n'
    "MAX_LEN = 2560   # headroom so the assistant JSON (at the end) is never truncated\n"
    "EPOCHS = 3       # with early stopping below; raise only if val loss is still falling\n"
    "\n"
    'PROJECT_DIR = "/content/drive/MyDrive/ORAN_Agent"   # your Drive: My Drive/ORAN_Agent\n'
    'DATA_DIR = os.path.join(PROJECT_DIR, "data")\n'
    'OUTPUT_DIR = os.path.join(PROJECT_DIR, "explainer-lora")\n'
    "os.makedirs(DATA_DIR, exist_ok=True)\n"
    "os.makedirs(OUTPUT_DIR, exist_ok=True)\n"
    'TRAIN_FILE = os.path.join(DATA_DIR, "train.jsonl")\n'
    'VAL_FILE = os.path.join(DATA_DIR, "val.jsonl")\n'
    'print("DATA_DIR:", DATA_DIR)\n'
    'print("OUTPUT_DIR:", OUTPUT_DIR)'
)

code(
    "# --- make sure train.jsonl / val.jsonl are in DATA_DIR (Drive) ---\n"
    "# First run: upload them here and they're copied into your Drive. Later runs reuse them.\n"
    "import os, shutil\n"
    "for fname, dst in ((\"train.jsonl\", TRAIN_FILE), (\"val.jsonl\", VAL_FILE)):\n"
    "    if not os.path.exists(dst):\n"
    "        from google.colab import files\n"
    '        print(f"{fname} not in DATA_DIR — upload it now:")\n'
    "        up = files.upload()\n"
    "        src = fname if os.path.exists(fname) else next(iter(up))\n"
    "        shutil.move(src, dst)\n"
    'print("train:", sum(1 for _ in open(TRAIN_FILE)), "| val:", sum(1 for _ in open(VAL_FILE)))'
)

code(
    "# --- load tokenizer + 4-bit model + LoRA ---\n"
    "import torch\n"
    "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\n"
    "from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training\n"
    "\n"
    "bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type=\"nf4\",\n"
    "                         bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)\n"
    "tok = AutoTokenizer.from_pretrained(MODEL)\n"
    "if tok.pad_token is None:\n"
    "    tok.pad_token = tok.eos_token\n"
    'tok.padding_side = "right"\n'
    "model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map=\"auto\")\n"
    "model = prepare_model_for_kbit_training(model)\n"
    "# Lower rank (r=8) + higher dropout = less capacity to memorize the templates.\n"
    "model = get_peft_model(model, LoraConfig(\n"
    "    r=8, lora_alpha=16, lora_dropout=0.1, bias=\"none\", task_type=\"CAUSAL_LM\",\n"
    "    target_modules=[\"q_proj\",\"k_proj\",\"v_proj\",\"o_proj\",\"gate_proj\",\"up_proj\",\"down_proj\"]))\n"
    "model.print_trainable_parameters()"
)

code(
    "# --- chat template + COMPLETION-ONLY masking (train on the diagnosis, not the prompt) ---\n"
    "# The prompt-only text is a token-prefix of the full text, so we mask those tokens to -100;\n"
    "# only the assistant JSON + its closing <|im_end|> stay supervised -> the model learns BOTH\n"
    "# to produce the JSON and to STOP. This is the fix for the systemsystem... degeneration.\n"
    "from datasets import load_dataset\n"
    'raw = load_dataset("json", data_files={"train": TRAIN_FILE, "val": VAL_FILE})\n\n'
    "\n"
    "def tokenize(ex):\n"
    '    msgs = ex["messages"]\n'
    "    full = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)\n"
    "    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)\n"
    '    full_ids = tok(full, add_special_tokens=False, truncation=True, max_length=MAX_LEN)["input_ids"]\n'
    '    prompt_ids = tok(prompt, add_special_tokens=False, truncation=True, max_length=MAX_LEN)["input_ids"]\n'
    "    labels = list(full_ids)\n"
    "    for i in range(min(len(prompt_ids), len(labels))):\n"
    "        labels[i] = -100   # mask system+user; supervise only the assistant diagnosis\n"
    '    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}\n'
    "\n"
    'ds = raw.map(tokenize, remove_columns=raw["train"].column_names)\n'
    'ex0 = ds["train"][0]\n'
    "print(\"seq len:\", len(ex0[\"input_ids\"]),\n"
    "      \"| supervised tokens (non -100):\", sum(1 for x in ex0[\"labels\"] if x != -100))"
)

code(
    "# --- train (QLoRA, completion-only loss) with eval + early stopping ---\n"
    "# Anti-overfit: evaluate on val each epoch, keep the BEST checkpoint (lowest val\n"
    "# loss), and stop early if val loss stops improving -> we don't ship the last\n"
    "# (most over-fit) epoch. Watch train loss vs eval loss: a widening gap = overfit.\n"
    "from transformers import (TrainingArguments, Trainer, DataCollatorForSeq2Seq,\n"
    "                          EarlyStoppingCallback)\n"
    "args = TrainingArguments(\n"
    "    output_dir=OUTPUT_DIR, per_device_train_batch_size=1, gradient_accumulation_steps=8,\n"
    "    num_train_epochs=EPOCHS, learning_rate=2e-4, warmup_ratio=0.03, lr_scheduler_type=\"cosine\",\n"
    "    weight_decay=0.01, fp16=True, logging_steps=10,\n"
    "    eval_strategy=\"epoch\", save_strategy=\"epoch\", save_total_limit=2,\n"
    "    load_best_model_at_end=True, metric_for_best_model=\"eval_loss\", greater_is_better=False,\n"
    "    report_to=\"none\", optim=\"paged_adamw_8bit\")\n"
    "collator = DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100)\n"
    "trainer = Trainer(model=model, args=args, train_dataset=ds[\"train\"], eval_dataset=ds[\"val\"],\n"
    "                  data_collator=collator,\n"
    "                  callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])\n"
    "trainer.train()\n"
    "# If you see eval_loss bottom out then rise, that's the overfit point — early\n"
    "# stopping already rolled back to the best checkpoint for you."
)

code(
    "# --- evaluate: root-cause accuracy on held-out val ---\n"
    "import json, torch\n"
    'val_raw = [json.loads(l) for l in open(VAL_FILE)]\n'
    "\n"
    "def extract_json(t):\n"
    '    i, j = t.find("{"), t.rfind("}")\n'
    "    if i < 0 or j < 0:\n"
    "        return None\n"
    "    try:\n"
    "        return json.loads(t[i:j+1])\n"
    "    except Exception:\n"
    "        return None\n"
    "\n"
    "def predict(messages_wo_assistant):\n"
    "    prompt = tok.apply_chat_template(messages_wo_assistant, tokenize=False, add_generation_prompt=True)\n"
    '    inp = tok(prompt, return_tensors="pt").to(model.device)\n'
    "    with torch.no_grad():\n"
    "        out = model.generate(**inp, max_new_tokens=768, do_sample=False,\n"
    "                             repetition_penalty=1.1, eos_token_id=tok.eos_token_id, pad_token_id=tok.pad_token_id)\n"
    '    return tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)\n'
    "\n"
    "n = ok = 0\n"
    "for ex in val_raw[:20]:\n"
    '    gold = json.loads(ex["messages"][-1]["content"])["root_cause_component"]\n'
    '    pred_obj = extract_json(predict(ex["messages"][:-1]))\n'
    '    pred = (pred_obj or {}).get("root_cause_component", "<parse-fail>")\n'
    "    hit = pred.strip().lower() == gold.strip().lower()\n"
    "    n += 1; ok += int(hit)\n"
    '    print(("PASS" if hit else "FAIL"), "pred=", pred, "| gold=", gold)\n'
    'print(f"\\nroot-cause accuracy: {ok}/{n} ({100*ok/max(n,1):.0f}%)")'
)

code(
    "# --- one full prediction, end to end ---\n"
    'print(predict(val_raw[0]["messages"][:-1])[:1000])'
)

code(
    "# --- save the LoRA adapter to Drive (persists across disconnects) ---\n"
    "model.save_pretrained(OUTPUT_DIR)\n"
    "tok.save_pretrained(OUTPUT_DIR)\n"
    'print("saved adapter to", OUTPUT_DIR)\n'
    "# Reload later:\n"
    "#   from peft import PeftModel\n"
    "#   base = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map=\"auto\")\n"
    "#   model = PeftModel.from_pretrained(base, OUTPUT_DIR)"
)

md(
    "## Notes & caveats\n"
    "- Trained on **synthetic** logs -> it diagnoses synthetic-style logs well, but "
    "won't automatically generalize to messy real OAI/Open5GS logs. Same demo->real "
    "gap as the API path; close it by training on logs captured from induced failures.\n"
    "- A 1.5B model learns the *format* and *patterns* reliably; it doesn't reason like "
    "a frontier model. Bump to 3B (or more data / scenarios) if accuracy is short.\n"
    "- Want harder, less memorizable data? `python make_dataset.py --augment "
    "--train-seeds 80` (distractor noise + time jitter + paraphrases) and re-upload.\n"
    "- Test generalization to an UNSEEN failure type: "
    "`python make_dataset.py --exclude sync_loss` trains on the other 4 and writes "
    "`test_sync_loss.jsonl`; after training, score it with `analyze_logs.py` / `eval.py` "
    "— a big drop vs in-distribution accuracy is the real overfitting signal.\n"
    "- This local model is a drop-in for the Claude call: same system prompt, same "
    "`(logs -> diagnosis JSON)` contract."
)


def to_nb():
    out = []
    for kind, src in cells:
        cell = {"cell_type": kind, "metadata": {}, "source": src}
        if kind == CODE:
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {
        "cells": out,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"provenance": [], "gpuType": "T4"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "train_explainer.ipynb"
    path.write_text(json.dumps(to_nb(), indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", path)
