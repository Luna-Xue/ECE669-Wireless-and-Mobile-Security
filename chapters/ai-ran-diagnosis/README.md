# AI-RAN Diagnosis Lab

**O-RAN / 5G-core logs in → a human-readable, evidence-cited root-cause diagnosis out.**

A small, self-contained teaching repo. A causal-DAG **generator** mints realistic
OAI/Open5GS-flavored logs *with ground truth* (so labels are free and accuracy is
measurable); a fine-tuned **1.5 B model** reads a log window and explains *what broke,
why, and which log lines prove it*.

> ✅ **No API key.** ✅ **No GPU required** — a pre-trained adapter runs on your laptop
> (CPU/MPS). Fine-tuning is an optional free-Colab bonus.

---

## 👀 30-second look — zero install

**Double-click [`ui/index.html`](ui/index.html)** (or open it in any browser). It launches
in **demo mode** with all 5 failure scenarios baked in — no Python, no install, no network.

Pick a scenario → read the log window → **click a step in the causal chain** and watch the
exact evidence log lines light up. That interaction *is* the point of the whole project: the
model doesn't just assert a cause, it **points at the logs that justify each step**.

<p align="center"><em>Everything below is for going deeper — running the real model on new logs, and the guided labs.</em></p>

---

## What's in the box

```
core/          shared contract:  LogEvent (input)  +  DiagnosisResult (output)
generator/     causal-DAG synthetic log generator (logs + ground truth)
training/      turn generated scenarios -> supervised chat examples
notebooks/     train_explainer.ipynb — QLoRA fine-tune on free Colab GPU
explainer/     local.py = base model + LoRA adapter (no key) · explainer.py = Claude API (optional)
ui/            index.html (visual explainer)  +  server.py (serves it live w/ your model)
tools/         gen_logs.py / analyze_logs.py — mint & score fresh .log files
tests/         pytest invariants (no model, no network, <1s)
demo.py        generate -> (optionally) diagnose -> check vs ground truth
make_dataset.py / eval.py / eval_metrics.py     build data · score the model
LAB.md         👈 the guided, self-paced student labs (start here for hands-on)
```

## The 5 failure scenarios

| Scenario | Root cause | Reproducible on a real OAI+Open5GS testbed? |
|---|---|---|
| `prb_exhaustion`  | O-DU | ✅ load the cell with iperf3 |
| `ngap_amf_down`   | AMF  | ✅ stop the AMF |
| `f1_setup_failure`| O-DU | ✅ break F1 between CU/DU |
| `auth_failure`    | UDM  | ✅ misprovision a subscriber |
| `sync_loss`       | O-RU | ❌ needs a real O-RU + 7.2 fronthaul + PTP — synthetic-only |

---

## Three ways to run it

### 0) The visual demo — no install
Double-click [`ui/index.html`](ui/index.html). (Covered above.) Great for exploring the idea in class.

### 1) Offline — generate & read labelled data *(pydantic only, ~seconds to set up)*
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U -r requirements.txt          # just pydantic

python demo.py                               # list the 5 scenarios
python demo.py sync_loss --truth             # one log window + the ground-truth diagnosis
python make_dataset.py                       # -> data/train.jsonl, data/val.jsonl
```

### 2) Run the **real fine-tuned model** locally *(no GPU — CPU/MPS)*
```bash
pip install -U -r requirements-local.txt     # torch / transformers / peft (~GB, one-time)
```
Then get the trained LoRA adapter and put it at **`./explainer-lora/`** — either:
- **Download** `explainer-lora.zip` (~68 MB) from 👉 **https://drive.google.com/drive/folders/1nXW_ZWwUZ9T-kdjysV3GFMWvJpcJV_ML?usp=sharing** 👈,
  then unzip it at the repo root so that `./explainer-lora/adapter_config.json` and
  `./explainer-lora/adapter_model.safetensors` exist, **or**
- **Train your own** free on Colab (see [LAB.md](LAB.md) Lab 3 / [`notebooks/train_explainer.ipynb`](notebooks/train_explainer.ipynb)).

```bash
python demo.py prb_exhaustion --local --truth   # the model diagnoses, then auto-checks vs truth
python ui/server.py                              # live UI: open http://127.0.0.1:8000  (use 127.0.0.1, not localhost)
```
> First diagnose loads the model (~40 s on CPU/MPS); it's fast after that. The base model
> `Qwen2.5-1.5B-Instruct` downloads once from HuggingFace on first run (no key). Force offline
> afterwards with `export HF_HUB_OFFLINE=1`.

### 3) *(Optional)* Big-model comparison via the Claude API — needs a key
```bash
pip install -U -r requirements-api.txt
cp .env.example .env      # put your ANTHROPIC_API_KEY in it (or just export it)
python demo.py prb_exhaustion --llm --truth
```
Same `logs → diagnosis JSON` contract as the local path, so `--llm` and `--local` are drop-in swaps.

---

## 🧪 Guided hands-on labs → [LAB.md](LAB.md)

The self-paced student walkthrough. All **no-GPU** (Lab 3 fine-tuning is an optional Colab bonus):

1. **Generate & read labelled logs** — cause vs. symptom.
2. **The dataset & the contract** — why structured, evidence-cited JSON.
3. **Fine-tune your own model** *(optional, Colab GPU)*.
4. **Run your model + the UI** — click a causal step, see the evidence.
5. **Evaluate like a scientist** — accuracy *and* evidence grounding, hallucination, leave-one-scenario-out.
6. **Break it & extend it** — prompt injection, distractor noise, add a brand-new failure scenario.

## Run the tests anytime
```bash
pip install -r requirements-dev.txt && pytest -q     # ~25 checks, no model/network, <1s
```

---

## Caveats (say these out loud)
- Trained on **synthetic** logs → it reads synthetic-style logs well, not (yet) messy real
  OAI/Open5GS logs. Close the gap by training on logs captured from *induced* failures on a
  real testbed (you caused them → you have the labels).
- A 1.5 B model learns the **format and the patterns** reliably; it won't reason like a
  frontier model. Bump to 3 B or add scenarios/data if accuracy falls short.
- The adapter is **not** committed to this repo (model weights don't belong in git) — grab it
  from the shared link or train your own (step 2 above).
