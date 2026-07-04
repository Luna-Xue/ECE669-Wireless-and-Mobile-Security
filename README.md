# ECE 669 — Wireless and Mobile Security

Hands-on labs and demos for **ECE 669: Wireless and Mobile Security**.

The course runs one arc: **use AI to quickly build a tool for a wireless system — then break
it, and harden it.** Wireless & mobile is the *domain* (what you attack and defend); AI
security is the *method* (how). Full week-by-week plan → **[SYLLABUS.md](SYLLABUS.md)**.

Each chapter is a **self-contained module** — `cd` into it and follow that chapter's own
`README.md`. Chapters are designed to run on a laptop (no GPU, no paid API keys required).

> Instructor: **Xiaochan Xue** · University of Hawaii at Manoa

---

## Chapters

The five modules of the course (16 weeks). See **[SYLLABUS.md](SYLLABUS.md)** for the schedule,
assessment, and AI-use policy.

| # | Chapter | Weeks | What you build / learn | Status |
|---|---|---|---|---|
| 1 | [Wireless & Mobile Security: Foundations](chapters/wireless-foundations/) | 1–3 | The attack surface (incl. the physical layer), the protocol stack as shared vocabulary, authentication / identity / subscriber PII. | 🚧 outline |
| 2 | [Security × AI-Assisted Engineering](chapters/security-and-ai-engineering/) | 4–6 | Fuzzing wireless protocol parsers; using AI to build & test faster; and the security problems that speed drags in. | 🚧 outline |
| 3 | [Train an Agent in a System](chapters/train-an-agent/) | 7–10 | The reusable *generate → fine-tune → evaluate* recipe. Fork the [**AI-RAN explainer**](chapters/ai-ran-diagnosis/) to build your own wireless agent. | ✅ scaffold ready |
| 4 | [Red Team: Attack a Peer's Agent](chapters/red-team-agents/) | 11–13 | AI-security in practice: prompt injection, jailbreak, data extraction; measure attack-success-rate. | 🚧 outline |
| 5 | [Blue Team + Capstone](chapters/blue-team-capstone/) | 14–16 | Harden your agent (grounding verifiers, guardrails, human-in-the-loop); report before/after ASR; present. | 🚧 outline |

**Runnable today:** the Ch.3 scaffold — the [**AI-RAN Log Diagnosis**](chapters/ai-ran-diagnosis/)
explainer (fine-tune a 1.5 B model to read O-RAN/5G-core logs and cite the evidence for each
root cause). The other modules are landing pages + outlines for now.

---

## Quickest zero-install look

Open [`chapters/ai-ran-diagnosis/ui/index.html`](chapters/ai-ran-diagnosis/ui/index.html) in
any browser — a full interactive demo, no install. Pick a scenario → read the log window →
click a step in the causal chain and watch the evidence log lines light up.

---

## How to use this repo

```bash
git clone https://github.com/Luna-Xue/ECE669-Wireless-and-Mobile-Security.git
cd ECE669-Wireless-and-Mobile-Security
# read the plan:
open SYLLABUS.md
# run the current chapter:
cd chapters/ai-ran-diagnosis     # then follow its README.md
```

---

## Repository layout

```
ECE669-Wireless-and-Mobile-Security/
├── README.md                        # you are here — course overview + chapter index
├── SYLLABUS.md                      # full 16-week plan, schedule, assessment, AI-use policy
└── chapters/
    ├── wireless-foundations/        # Ch.1 — foundations (outline)
    ├── security-and-ai-engineering/ # Ch.2 — security × AI-assisted engineering (outline)
    ├── train-an-agent/              # Ch.3 — build-your-own-agent project brief
    ├── ai-ran-diagnosis/            #   └─ Ch.3 worked example / scaffold (runnable)
    ├── red-team-agents/             # Ch.4 — red team (outline)
    └── blue-team-capstone/          # Ch.5 — blue team + capstone (outline)
```
