# ECE 669 — Wireless and Mobile Security

Hands-on labs and demos for **ECE 669: Wireless and Mobile Security**.

Each chapter is a **self-contained, runnable module** — clone the repo, `cd` into a
chapter, and follow that chapter's own `README.md`. Chapters are designed to run on a
laptop (no GPU, no paid API keys required).

> Instructor: **Xiaochan Xue** · University of Hawaii at Manoa

---

## Chapters

| Chapter | What you build / learn | Security angle |
|---|---|---|
| [**AI-RAN Log Diagnosis**](chapters/ai-ran-diagnosis/) | Fine-tune a small (1.5 B) LLM to read O-RAN / 5G-core logs and explain *what broke, why, and which log lines prove it* — with a causal-DAG data generator, structured/evidence-cited output, and scientific evaluation (accuracy, evidence grounding, hallucination, leave-one-scenario-out). | **Prompt-injection robustness** ("logs are *data*, not instructions"), trustworthy/evidence-grounded AI for network operations, and the sim-to-real gap. No GPU, no API key. |

*More chapters to come.*

---

## How to use this repo

```bash
git clone https://github.com/Luna-Xue/ECE669-Wireless-and-Mobile-Security.git
cd ECE669-Wireless-and-Mobile-Security/chapters/ai-ran-diagnosis
# then follow chapters/ai-ran-diagnosis/README.md
```

**Quickest zero-install look** at the current chapter: open
[`chapters/ai-ran-diagnosis/ui/index.html`](chapters/ai-ran-diagnosis/ui/index.html)
in any browser — it runs a full interactive demo with no install.

---

## Repository layout

```
ECE669-Wireless-and-Mobile-Security/
├── README.md                     # you are here — course overview + chapter index
└── chapters/
    └── ai-ran-diagnosis/         # Chapter: AI-RAN log diagnosis (start at its README.md)
        ├── README.md             #   chapter landing page + setup
        ├── LAB.md                #   guided, self-paced student labs
        ├── ui/index.html         #   zero-install interactive demo
        └── ...                   #   generator / model / eval / tests
```
