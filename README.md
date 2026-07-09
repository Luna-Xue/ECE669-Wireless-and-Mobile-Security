# ECE 669 — Wireless and Mobile Security

Hands-on, evidence-based labs for **ECE 669: Wireless and Mobile Security**.

Traditional wireless and mobile security problems have not gone away — but **AI-assisted
engineering is opening new paths into them**. This course sits deliberately at the
intersection of three things:

> **Traditional wireless/mobile security · AI-assisted engineering · AI security for
> AI-RAN / ISAC / cyber-physical systems.**

It is *not* a pure AI course and *not* a pure wireless course. Students first learn wireless
and mobile security foundations, then learn how AI changes the engineering workflow, the
attack path, the trust boundary, and the defense process — and how those AI failures turn
back into **real wireless consequences** (power, beam, scheduling, handover, physical-layer
secrecy, ISAC sensing, and a *simulated* robot-car).

> **Everything runs on synthetic data and mock systems.** The core lab needs **no external
> LLM API, no GPU, no SDR, no 5G testbed, and no production O-RAN**. See the
> [Sandbox Safety Boundary](#sandbox-safety-boundary) before you begin.

---

## Who this is for — required vs. optional background

**Required**

- Basic **cybersecurity** *or* **AI/ML** background (either is fine).
- Basic or *interested* **wireless / networking** background.
- **Programming** ability (Python; comfort with the command line and `git`).

**Not required**

- A personal **GPU**, a software-defined radio (**SDR**), a real **5G testbed**, or a
  production **O-RAN** system.

**Optional**

- **Local LLM** exploration using **lab GPU** resources (see
  [Chapter 10](chapters/10-advanced-extensions/)).

---

## The core lab, in one paragraph

The default lab is a **classroom sandbox**: synthetic O-RAN/5G logs, mock telemetry,
simulated RF / ISAC evidence, and a **built-in "before-defense vs. defended" explainer
agent**. Students run the agent, **red-team its context and decision chain**, then add
**safety gates** and measure the difference — all without touching a real wireless system and
without sending any data to an external model. The runnable core lives in
[`chapters/ai-ran-diagnosis/`](chapters/ai-ran-diagnosis/).

---

## Build It / Break It / Fix It

The middle of the course is a three-step arc on the **same sandbox agent**:

| Step | Chapter | You... | Outcome |
|---|---|---|---|
| 🔨 **Build It** | [Ch. 5](chapters/05-build-explainer-agent/) | run and configure the explainer agent; establish baseline behavior | a working, *undefended* explainer + baseline |
| 💥 **Break It** | [Ch. 6](chapters/06-break-red-team/) | red-team the agent's context/decision chain (synthetic injections, fake telemetry, sensing confusion) | a measured **attack-success** picture |
| 🛡️ **Fix It** | [Ch. 7](chapters/07-fix-safety-gates/) | add grounding / policy / wireless / ISAC / robot-safety gates + human approval | **before/after** defense comparison |

The point is **evidence-based reasoning**: you don't just claim the agent is unsafe or safe —
you *show* it, with before/after behavior on the same synthetic inputs.

---

## Sandbox Safety Boundary

This repository is a **teaching sandbox for safe classroom reasoning** — not an attack
toolkit. Read this before running anything.

- **Synthetic & mock only.** All logs, telemetry, RF/ISAC evidence, and system maps are
  **generated or mocked**. No real subscriber data, no captured traffic, no live spectrum.
- **You attack the *agent*, not a network.** In "Break It," the target is the AI agent's
  **context and decision chain** — the words and evidence it reads — never a real wireless
  system, base station, handset, or control plane.
- **No transmission, no actuation.** Nothing here transmits RF, connects to a network, or
  actuates control. Power/beam/scheduling/handover effects and the **robot-car are
  simulated** for consequence reasoning only.
- **No external model required.** The core lab uses a **local, built-in** explainer; no data
  leaves your machine and no API key is needed. (Cloud/API comparison is optional and uses
  **synthetic data only** — see Ch. 10.)
- **Jailbreak-style testing is confined to the sandbox** and exists solely to demonstrate why
  **safety gates and human approval** are required before any AI output influences control.
- **Principle:** *LLM-in-the-loop, not LLM-in-control.*

---

## Repository structure

```
ECE669-Wireless-and-Mobile-Security/
├── README.md          # you are here — course map, safety boundary, chapter index
├── SYLLABUS.md        # week-by-week schedule, assessment, AI-use policy
└── chapters/
    ├── 00-course-overview/               # Ch.0  Course overview & learning path
    ├── 01-wireless-foundations/          # Ch.1  Wireless & mobile security foundations
    ├── 02-ai-assisted-engineering/       # Ch.2  AI-assisted engineering for security
    ├── 03-ai-security-risks/             # Ch.3  AI security risks in engineering contexts
    ├── 04-evidence-trust-boundaries/     # Ch.4  AI-RAN evidence & trust boundaries
    ├── 05-build-explainer-agent/         # Ch.5  Build It — system explainer agent
    ├── 06-break-red-team/                # Ch.6  Break It — red-team the workflow
    ├── 07-fix-safety-gates/              # Ch.7  Fix It — safety gates before control
    ├── 08-wireless-pls-isac-consequences/# Ch.8  Wireless / PLS / ISAC consequences
    ├── 09-assessment-reporting/          # Ch.9  Assessment & evidence-based reporting
    ├── 10-advanced-extensions/           # Ch.10 Advanced extensions (optional)
    └── ai-ran-diagnosis/                 # runnable sandbox core (used by Ch.4–8)
```

Each chapter folder has its own `README.md` (the chapter title is that page's top-level
heading). Start at [Chapter 0](chapters/00-course-overview/).

---

## Chapters

| # | Chapter | Focus |
|---|---|---|
| 0 | [Course Overview and Learning Path](chapters/00-course-overview/) | Goals, required vs. optional background, how wireless security and AI security connect, the Build/Break/Fix model. |
| 1 | [Wireless and Mobile Security Foundations](chapters/01-wireless-foundations/) | Threat models, physical-layer attack surface, identity/auth/privacy, protocol trust boundaries, control consequences. |
| 2 | [AI-Assisted Engineering for Security Workflows](chapters/02-ai-assisted-engineering/) | AI for scripts/tests/debugging/log analysis; LLM system explanation; human verification; why AI output is not evidence. |
| 3 | [AI Security Risks in Engineering Contexts](chapters/03-ai-security-risks/) | Prompt injection, context manipulation, fake telemetry, hallucinated explanations, unsafe recommendations, policy bypass. |
| 4 | [AI-RAN System Evidence and Trust Boundaries](chapters/04-evidence-trust-boundaries/) | System maps, synthetic logs, mock telemetry, RF features, ISAC evidence, provenance & cross-source verification. |
| 5 | [**Build It** — System Explainer Agent](chapters/05-build-explainer-agent/) | Built-in explorer; before-defense vs. defended; grounding config; evidence window; **diagnostic recommendations only**. |
| 6 | [**Break It** — Red-Team the AI-Assisted Workflow](chapters/06-break-red-team/) | Hidden log injection, fake telemetry, sensing confusion, privacy-sensitive logs, sandbox-only jailbreak tests, seeded issues. |
| 7 | [**Fix It** — Safety Gates Before Control](chapters/07-fix-safety-gates/) | Grounding verifier, policy gate, wireless/PLS/ISAC/robot-safety validators, human approval. |
| 8 | [Wireless / PLS / ISAC Consequences](chapters/08-wireless-pls-isac-consequences/) | Unsafe power/beam, scheduling/mobility risk, secrecy risk, sensing/blockage uncertainty, confused robot-car scenario. |
| 9 | [Assessment and Evidence-Based Reporting](chapters/09-assessment-reporting/) | Build-It checkpoint, Red-Team report, Blue-Team capstone; before/after behavior; attack-success & evidence quality. |
| 10 | [Advanced Extensions](chapters/10-advanced-extensions/) | *(Optional)* Local LLMs + lab GPU, API comparison (synthetic only), O-RAN/xApp/rApp, ISAC & robot-car sim, research ideas. |

---

## Chapter → lab mapping

All labs use **synthetic logs, mock telemetry, and simulated RF/ISAC evidence**. The core lab
is the sandbox explainer in [`chapters/ai-ran-diagnosis/`](chapters/ai-ran-diagnosis/).

| Chapter | Lab | What you produce | Data |
|---|---|---|---|
| 1 | Trust-boundary map | annotate a synthetic capture/log: identities, trust boundaries | synthetic |
| 2 | AI-assisted artifact + verification | draft a parser/test with AI, then verify it and find its flaw | synthetic |
| 3 | Risk-class catalog | reproduce each AI-security risk against the sandbox agent | synthetic / mock |
| 4 | Evidence window | assemble a system map + evidence with tagged provenance | synthetic / mock |
| 5 | **Build It** checkpoint | baseline behavior of before-defense vs. defended explainer | sandbox |
| 6 | **Break It** report | attacks on the agent's context/decision chain + attack-success | sandbox |
| 7 | **Fix It** gates | safety gates + before/after attack-success comparison | sandbox |
| 8 | Consequence scenarios | simulated wireless/PLS/ISAC + robot-car outcomes | simulation |
| 9 | Capstone report | Build/Break/Fix write-up with evidence and consequences | — |
| 10 | *(optional)* extensions | local-LLM / API / O-RAN / ISAC / research explorations | synthetic |

---

## Optional advanced extensions

For students with lab resources or research interest — **all optional**, none required to
pass the course (see [Chapter 10](chapters/10-advanced-extensions/)):

- **Local LLMs** on lab GPU resources (explore larger open models against the sandbox).
- **API-based model comparison** — compare a cloud model to the local one **on synthetic
  data only** (never real telemetry or subscriber data).
- **O-RAN / xApp / rApp** boundary extensions — map the sandbox onto near-RT/non-RT RIC roles.
- **ISAC & robot-car simulation** extensions — richer sensing-confusion and consequence
  scenarios.
- **Research projects** — new attack classes, new gates, new evidence types, transfer to
  captured-but-labelled data from *induced* failures.

---

## Getting started

```bash
git clone https://github.com/Luna-Xue/ECE669-Wireless-and-Mobile-Security.git
cd ECE669-Wireless-and-Mobile-Security
# 1) read the map and the safety boundary:
open README.md
# 2) start the learning path:
open chapters/00-course-overview/README.md
# 3) the quickest zero-install look at the sandbox agent:
open chapters/ai-ran-diagnosis/ui/index.html
```

> **Full week-by-week schedule, assessment, and AI-use policy → [`SYLLABUS.md`](SYLLABUS.md)**
> (aligned to this Chapter 0–10 structure).

---

> Instructor: **Xiaochan Xue** · University of Hawaii at Manoa
