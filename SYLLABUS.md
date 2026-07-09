# ECE 669 — Wireless and Mobile Security

**Syllabus · Spring 2027 (draft)**

| | |
|---|---|
| **Meets** | Mondays & Wednesdays, 75 min · Jan 11 – May 5, 2027 |
| **Instructor** | Xiaochan Xue · University of Hawaii at Manoa |
| **Office hours / contact / room** | _TBD_ |
| **Final exam period** | May 10–14, 2027 (capstone presentations / overflow — see Assessment) |

> **No-holiday sessions:** MLK Day (Mon Jan 18) and Presidents' Day (Mon Feb 15) → those
> weeks meet **Wednesday only**. **Spring Recess** Mar 15–19 → no class.
> _Dates follow the posted academic calendar; confirm against the official UH Manoa calendar
> before publishing._

This syllabus follows the **Chapter 0–10** structure in the
[repository README](README.md); each chapter's detail lives in its own
[`chapters/`](chapters/) folder.

---

## 1. Course description

Traditional wireless and mobile security problems remain important — but **AI-assisted
engineering is opening new paths into them**. This course sits at the intersection of three
things:

> **Traditional wireless/mobile security · AI-assisted engineering · AI security for
> AI-RAN / ISAC / cyber-physical systems.**

It is neither a pure AI course nor a pure wireless course. Students first learn wireless and
mobile security **foundations**, then learn how AI changes the engineering **workflow**, the
**attack path**, the **trust boundary**, and the **defense process** — and how those AI
failures turn back into concrete **wireless consequences** (power, beam, scheduling, handover,
physical-layer secrecy, ISAC sensing, and a *simulated* robot-car).

The spine of the course is a **Build It / Break It / Fix It** arc on a **classroom sandbox**:
synthetic logs, mock telemetry, simulated RF/ISAC evidence, and a built-in
before-defense/defended explainer agent. **No external LLM API, GPU, SDR, 5G testbed, or
production O-RAN is required.**

### Learning outcomes

By the end of the course you will be able to:

1. Map the wireless/mobile **attack surface** (incl. the physical layer) and reason about
   identity, authentication, subscriber privacy, and protocol **trust boundaries**.
2. Use AI to **assist** security engineering (scripts, tests, debugging, log analysis,
   system explanation) — and **verify** its output rather than trust it as evidence.
3. Recognize **AI-security risks** in engineering contexts: prompt injection, context
   manipulation, fake telemetry, hallucinated explanations, unsafe recommendations, policy
   bypass.
4. Assemble an **evidence window** with provenance, and **build/configure** an
   evidence-grounded explainer agent that makes *diagnostic recommendations only*.
5. **Red-team** the agent's context and decision chain **in the sandbox**, and measure
   **attack success**.
6. **Add safety gates** (grounding, policy, wireless/PLS, ISAC, robot-safety, human approval)
   and demonstrate **before/after** defense behavior.
7. Tie AI failures to concrete **wireless / PLS / ISAC consequences**, including a simulated
   robot-car scenario.
8. Report findings with **evidence** — before/after behavior and attack-success comparison,
   not claims.

### Required vs. optional background

**Required** — basic **cybersecurity** *or* **AI/ML** background (either); basic or interested
**wireless / networking** background; **programming** ability (Python, command line, `git`).

**Not required** — a personal **GPU**, **SDR**, real **5G testbed**, or production **O-RAN**.

**Optional** — **local LLM** exploration using **lab GPU** resources (Chapter 10).

---

## 2. How the course runs

- **Chapters 0–10** grouped into four arcs: **Foundations** (Ch. 0–1), **AI in the workflow**
  (Ch. 2–4), **Build / Break / Fix** (Ch. 5–7), and **Consequences, Assessment & Extensions**
  (Ch. 8–10).
- **Everything runs on a laptop** with **synthetic/mock data** and a **local** explainer — no
  API key, no GPU. The runnable sandbox core is
  [`chapters/ai-ran-diagnosis/`](chapters/ai-ran-diagnosis/).
- **The repo is the textbook.** Each chapter starts at its own `README.md`.

### Sandbox safety boundary

Students attack the **agent's context and decision chain**, using synthetic evidence —
**never a real wireless system**. Nothing transmits RF, connects to a network, or actuates
control; power/beam/scheduling and the robot-car are **simulated**. Jailbreak-style testing is
confined to the sandbox and exists only to justify the safety gates of Chapter 7. Full text:
[Sandbox Safety Boundary](README.md#sandbox-safety-boundary). **Principle: LLM-in-the-loop,
not LLM-in-control.**

---

## 3. 16-week schedule

| Wk | Dates (2027) | Chapter(s) | Focus | Deliverable |
|---|---|---|---|---|
| 1 | Jan 11–15 | **Ch. 0** + **Ch. 1** | Overview & learning path; wireless foundations begin | — |
| 2 | Jan 18–22 · *MLK, Wed only* | Ch. 1 | Threat models; physical-layer attack surface | — |
| 3 | Jan 25–29 | Ch. 1 | Identity/auth/privacy; protocol trust boundaries | **Lab 1** — trust-boundary map |
| 4 | Feb 1–5 | **Ch. 2** | AI for scripts/tests/debugging/log analysis | — |
| 5 | Feb 8–12 | Ch. 2 | LLM system explanation; verifying AI artifacts | **Lab 2** — AI artifact + verification |
| 6 | Feb 15–19 · *Pres. Day, Wed only* | **Ch. 3** | Prompt injection, context manipulation | — |
| 7 | Feb 22–26 | Ch. 3 | Fake telemetry, hallucination, unsafe rec, policy bypass | **Lab 3** — risk-class catalog |
| 8 | Mar 1–5 | **Ch. 4** | System maps, evidence, RF/ISAC, provenance | **Lab 4** — evidence window |
| 9 | Mar 8–12 | **Ch. 5 · Build It** | Explainer agent; before-defense vs. defended baseline | **Build-It checkpoint** |
| — | *Mar 15–19* | — | *Spring Recess — no class* | — |
| 10 | Mar 22–26 | **Ch. 6 · Break It** | Hidden log injection, fake telemetry, sensing confusion | — |
| 11 | Mar 29–Apr 2 | Ch. 6 · Break It | Sandbox jailbreak tests; seeded issues; measure ASR | **Red-Team report** |
| 12 | Apr 5–9 | **Ch. 7 · Fix It** | Grounding verifier; policy gate | — |
| 13 | Apr 12–16 | Ch. 7 · Fix It | Wireless/PLS/ISAC/robot-safety validators; human approval | **Before/after ASR** |
| 14 | Apr 19–23 | **Ch. 8** | Wireless/PLS/ISAC consequences; confused robot-car (sim) | Consequence scenarios |
| 15 | Apr 26–30 | **Ch. 9** (+ **Ch. 10** optional) | Capstone assembly; optional extensions showcase | Draft capstone |
| 16 | May 3–7 | Ch. 9 | **Blue-Team capstone presentations** | **Capstone report + demo** |

> Spring Recess falls **after Build It (Wk 9)** and **before Break It (Wk 10)** — you enter the
> break with a working baseline agent.

---

## 4. Build It / Break It / Fix It + capstone

The middle of the term is one continuous arc on the **shared sandbox agent**:

- **Build It (Ch. 5):** run and configure the explainer; capture baseline behavior in the
  *before-defense* and *defended* configurations.
- **Break It (Ch. 6):** red-team the agent's context/decision chain in the sandbox; measure
  **attack-success (ASR)** per risk class; write the **Red-Team report**.
- **Fix It (Ch. 7):** add safety gates; re-run the attacks; report **before/after ASR**.
- **Consequences (Ch. 8):** tie each attack/gate to a simulated wireless/PLS/ISAC outcome.
- **Capstone (Ch. 9):** a Build/Break/Fix write-up + demo, graded on **evidence**.

Teams of _[TBD, ~2–3]_. Work may be done on the shared sandbox with instructor-seeded issues;
no student ever touches a real wireless system.

---

## 5. Assessment _(proposed weights — instructor to finalize)_

| Component | Weight | Chapters |
|---|---|---|
| Foundations & AI-in-workflow labs (Labs 1–4) | 25% | Ch. 1–4 |
| Build-It checkpoint | 15% | Ch. 5 |
| Red-Team report (attacks + measured ASR) | 20% | Ch. 6 |
| Fix-It + consequences (before/after ASR) | 30% | Ch. 7–8 |
| Participation / reading responses | 10% | all |
| Advanced extensions | *optional bonus* | Ch. 10 |

- **No traditional final exam.** The **capstone presentation + report** is the culminating
  assessment; the May 10–14 period is used for presentations / overflow.
- **Graded on process and evidence** — before/after behavior, measured attack-success,
  evidence quality, and the consequence explanation — **not** on whether an attack or defense
  "won."
- Late policy, regrade policy, and per-lab rubrics: _TBD_.

---

## 6. Use of AI in this course _(policy)_

This course **teaches** using AI to accelerate engineering, so AI assistance is **expected**,
not merely permitted. With that come three rules:

1. **You own what you submit.** You must understand, and be able to explain and defend, every
   line you turn in — including AI-generated code and text. "The AI wrote it" is not a defense.
2. **Disclose it.** Note where AI meaningfully shaped your work (which tool, for what).
3. **Never fabricate results.** AI may help you build and analyze; it may not invent data,
   metrics, or evidence. Grounding and honest evaluation are graded — and are the whole point.

Institution-specific academic-integrity language: _TBD_.

---

## 7. Logistics _(to be completed)_

- **Accessibility / accommodations:** _TBD_
- **Communication / discussion forum:** _TBD_
- **Required/optional readings:** posted per chapter _(TBD)_
- **Software setup:** per-chapter `README.md`; all labs are laptop-only, no GPU, no API key,
  synthetic/mock data.

---

_This syllabus is a living draft. The schedule may shift with the official academic calendar
and class pace._
