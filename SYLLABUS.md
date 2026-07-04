# ECE 669 — Wireless and Mobile Security

**Syllabus · Spring 2027 (draft)**

| | |
|---|---|
| **Meets** | Mondays & Wednesdays, 75 min · Jan 11 – May 5, 2027 |
| **Instructor** | Xiaochan Xue · University of Hawai‘i at Mānoa |
| **Office hours / contact / room** | _TBD_ |
| **Final exam period** | May 10–14, 2027 (used for makeup / overflow only — see Assessment) |

> **No-holiday sessions:** MLK Day (Mon Jan 18), Presidents’ Day (Mon Feb 15) → those weeks meet **Wednesday only**. **Spring Recess** Mar 15–19 → no class.
> _Dates follow the posted academic calendar; confirm against the official UH Mānoa calendar before publishing._

---

## 1. What this course is about

Wireless and mobile systems are being rebuilt around AI — networks that diagnose
themselves, agents that operate the RAN, models that read logs no human has time to.
That shift creates a **new security surface**: the AI in the loop can be fooled,
jailbroken, leaked from, and turned against the system it was meant to protect.

This course is organized around one arc:

> **Use AI to quickly build a tool for a wireless system — then break it, and harden it.**

**Wireless & mobile is the domain** (what you attack and defend); **AI security is the
method** (how you attack and defend). You will finish the term having *built* a small,
evidence-grounded AI agent for a wireless/mobile system, *attacked* a peer team’s agent,
and *defended* your own — measuring everything like a scientist.

### Learning outcomes

By the end of the course you will be able to:

1. **Map the wireless/mobile attack surface** across PHY → protocol (NAS/RRC/GTP, 802.11/EAP)
   → core (5GC) → O-RAN, and reason about trust boundaries, identity, and subscriber PII.
2. **Use AI to accelerate secure engineering** — generate fuzz harnesses, tests, and code
   reviews with AI assistants — *and* recognize the risks AI drags into the dev loop
   (insecure generated code, hallucinated dependencies, prompt injection, data leakage).
3. **Apply security testing (fuzzing)** to real wireless protocol-parsing code.
4. **Train a small, evidence-grounded AI agent** for a wireless/mobile system using a
   reproducible recipe (generate labeled data → fine-tune → evaluate), and evaluate it
   scientifically (accuracy, evidence grounding, hallucination, generalization).
5. **Red-team an AI agent** — execute prompt-injection, jailbreak, and data-extraction
   attacks, and quantify attack-success-rate (ASR).
6. **Defend an AI agent** — design and measure mitigations (input isolation, grounding
   verification, guardrails, human-in-the-loop) and report before/after ASR.

### Prerequisites _(proposed — tune to cohort)_

- Programming in **Python**; comfort with the command line and `git`.
- An intro **networking or wireless-communications** course (or equivalent background).
- **Machine learning is helpful but not required** — the default project path needs no ML
  background (you fork and extend a provided scaffold); a from-scratch path rewards ML experience.

---

## 2. How the course runs

- **Five modules over 16 weeks.** The first two are taught + hands-on labs; the last three
  are one continuous **semester project**: *build → red team → blue team*.
- **Everything runs on a laptop.** No GPU and no paid API keys are required. Model
  fine-tuning uses free Colab; inference runs on CPU/MPS. This is a hard design constraint
  of every lab.
- **The repo is the textbook.** Each module lives in
  [`chapters/`](chapters/); start each one at its own `README.md` / `LAB.md`.
- **Wireless is required, not decorative.** Every AI technique in this course targets or
  defends a wireless/mobile system — including the agent you build (see §4).

---

## 3. The five modules

### Ch.1 — Wireless & Mobile Security: Foundations  · **Weeks 1–3**

Establish the domain and the vocabulary the whole course reuses.

- **Wk 1** — The wireless attack surface. Open on real attacks: IMSI catchers / rogue base
  stations, Wi-Fi KRACK, protocol downgrade, **PHY-layer attacks (jamming, GPS spoofing,
  eavesdropping)**. Why the RF medium makes wireless uniquely exposed. Threat modeling.
- **Wk 2** — The stack as shared vocabulary: **PHY/RF** → MAC → NAS/RRC/GTP (cellular) /
  802.11 mgmt + EAP (Wi-Fi) → 5G core (AMF/SMF/UPF/UDM) → **O-RAN** disaggregation and why
  one fault cascades. PHY security as attack surface: jamming, spoofing, **RF fingerprinting**.
- **Wk 3** — Authentication, identity, and privacy: 5G-AKA, SUPI/SUCI, EAP, mobile-device
  identity. Sets up the PII / trust-boundary theme used throughout.
- **Hands-on:** analyze a provided call-flow / packet capture; label the identities and mark
  the trust boundaries.

> **PHY note:** we cover PHY security as *attack surface* and (later) as an *AI-diagnosable*
> domain — **not** as an information-theoretic secrecy module (wiretap channel / secrecy
> capacity / artificial noise). Those are pointed to as optional reading and, for a
> comms-heavy cohort, an optional project track.

### Ch.2 — Security × AI-Assisted Engineering  · **Weeks 4–6**

Learn to use AI to build and test faster — and see the security problems that speed drags in.
Fuzzing is one classic technique here, not the whole point.

- **Wk 4** — Finding bugs, the classic way: vulnerability classes, sanitizers, and
  **fuzzing** (mutation / coverage-guided). Targets are **wireless protocol parsers**
  (NAS/RRC/GTP/NGAP).
- **Wk 5** — *AI fastens development.* AI coding assistants; using AI to generate fuzz
  harnesses, seed corpora, and tests; LLM-as-reviewer for vulnerability triage. You will use
  AI to generate the very harness from Wk 4.
- **Wk 6** — *…and drags in new problems.* Insecure AI-generated code, hallucinated
  dependencies / supply-chain (“slopsquatting”), **indirect prompt injection** into dev tools,
  data leakage of proprietary code/PII, over-trust / automation bias.
- **Hands-on:** use an AI assistant to generate a fuzz harness for a protocol parser and
  produce a crash; then review a block of AI-generated code and find the vulnerability /
  hallucinated dependency it introduced.

> **Bridge to Ch.3:** the skills you practice here — using AI to generate data, harnesses, and
> evaluation code — are exactly what you’ll use next to build your own agent. And the
> *adversarial-input* mindset escalates cleanly: a fuzzer’s malformed field (Wk 4) → a prompt
> injection aimed at an LLM (Wk 6) → the stealth injection your agent must survive (Ch.3).

### Ch.3 — Train an Agent in a System  · **Weeks 7–10**

Learn what it means to *train an agent inside a system*, using the provided **AI-RAN
diagnosis explainer** ([`chapters/ai-ran-diagnosis`](chapters/ai-ran-diagnosis/)) as a fully
worked example — then build your own for a wireless/mobile problem you choose.

**The reusable recipe (the explainer is one instance of all five steps):**

| Step | In the explainer | For your system |
|---|---|---|
| ① Define the system & problem | Read O-RAN logs, find root cause | What does your agent read / do? What is ground truth? |
| ② Build a labeled-data generator | Causal-DAG generator (labels free, accuracy measurable) | Write a generator for your problem |
| ③ Define the I/O contract | `logs → evidence-cited diagnosis JSON` | Your structured, checkable output |
| ④ Fine-tune a small model | QLoRA on a 1.5 B model (free Colab) | Same LoRA flow |
| ⑤ Evaluate scientifically | accuracy + evidence grounding + hallucination + LOSO | Your own metrics |

- **Wk 7** — Walk the explainer end-to-end: run the demo/UI, internalize the 5-step recipe,
  structured/evidence-grounded output, and why the model runs locally (PII).
- **Wk 8** — Scope **your own wireless/mobile problem**; **fork the scaffold** and swap in your
  domain. *(Proposal check.)*
- **Wk 9** — Generate data and start training (Spring Recess = training time).
  **Hard checkpoint: your agent must emit valid structured output** — teams that miss it fall
  back to the pure fork.
- **Wk 10** — Evaluate and report baseline metrics. **Hand in your agent; teams swap.**

**Default path = fork the explainer** (it is built for extension — adding a scenario flows
automatically through generator → dataset → UI → eval). **From-scratch pipeline = advanced
opt-in.**

**Your agent must target a wireless/mobile system.** Pick from (or propose near) this menu:

- fault-diagnosis agent for Wi-Fi / 5G core / IoT / transport
- network **configuration-audit** agent
- **alert triage / correlation** agent
- **protocol-compliance** checker
- **wireless task agent** — one that takes network actions (e.g., RIC xApp / config)
- **PHY/RF anomaly** agent — sync loss, jamming, RF-fingerprint anomaly
- **mobile device/OS** log-diagnosis agent

### Ch.4 — Red Team: Attack a Peer’s Agent  · **Weeks 11–13**

Learn AI-security systematically, then weaponize it against another team’s agent.

- **Wk 11** — *AI-security primer.* Jailbreaks; prompt injection (direct & indirect); PII /
  training-data / system-prompt extraction; the attack taxonomy; how to measure **ASR**.
  (You’ve already met these as *instances* in Ch.2/Ch.3 — now they become a system.)
- **Wk 12–13** — Attack the agent you received: **black-box first, then white-box**. Quantify
  ASR; write an exploit report and **return it to the owning team**.

### Ch.5 — Blue Team + Capstone  · **Weeks 14–16**

Harden your own agent against the exploit report you get back, and present.

- **Wk 14–15** — Defenses: input isolation / delimiting, **grounding/evidence verifiers**
  (reject a conclusion its own cited evidence doesn’t support), guardrail models,
  human-in-the-loop for consequential actions, adversarial fine-tuning on attack samples.
  **Re-measure ASR and report before/after.**
- **Wk 16** — Final presentation: your wireless system, your agent, how it was broken, and how
  you closed the gap.

---

## 4. 16-week schedule at a glance

| Wk | Dates (2027) | Module | Focus | Deliverable |
|---|---|---|---|---|
| 1 | Jan 11–15 | Ch.1 | Wireless attack surface + PHY attacks + threat model | — |
| 2 | Jan 18–22 · *MLK, Wed only* | Ch.1 | The stack as vocabulary; cellular security evolution | — |
| 3 | Jan 25–29 | Ch.1 | Auth, identity & privacy: 5G-AKA, SUPI/SUCI, EAP | Lab: label trust boundaries in a capture |
| 4 | Feb 1–5 | Ch.2 | Fuzzing wireless protocol parsers | — |
| 5 | Feb 8–12 | Ch.2 | Using AI to generate harnesses / tests / seeds | — |
| 6 | Feb 15–19 · *Pres. Day, Wed only* | Ch.2 | AI’s own risks: insecure code, hallucinated deps, injection | Lab: AI-generate a harness → crash; audit AI code |
| 7 | Feb 22–26 | Ch.3 | The explainer as worked example; the 5-step recipe | — |
| 8 | Mar 1–5 | Ch.3 | Scope your wireless problem; fork the scaffold | **Project proposal** |
| 9 | Mar 8–12 | Ch.3 | Generate data + start training | **Checkpoint: valid structured output** |
| — | *Mar 15–19* | — | *Spring Recess — training time* | — |
| 10 | Mar 22–26 | Ch.3 | Evaluate; report baseline | **Hand in agent → teams swap** |
| 11 | Mar 29–Apr 2 | Ch.4 | AI-security primer: jailbreak / injection / PII / ASR | — |
| 12 | Apr 5–9 | Ch.4 | Attack the peer agent: black-box | Exploit log |
| 13 | Apr 12–16 | Ch.4 | Attack: white-box; quantify ASR | **Exploit report → owning team** |
| 14 | Apr 19–23 | Ch.5 | Harden: isolation / verifier / guardrails / re-tune | — |
| 15 | Apr 26–30 | Ch.5 | Continue hardening; re-measure ASR | **Before/after ASR** |
| 16 | May 3–7 | Ch.5 | Final presentations | **System + agent + attack/defense writeup** |

---

## 5. The semester project (Ch.3–5)

The back half is one continuous, team-based project.

- **Teams** of _[TBD, ~2–3]_. You build one agent per team, then attack another team’s agent,
  then defend your own.
- **Swap mechanics:** at the Wk 10 hand-in, each team delivers (a) the trained agent
  (adapter + I/O contract + a runner) and (b) a one-page **spec sheet** (what it does, its
  system rules, its baseline metrics). Teams are paired; each attacks the other’s agent.
- **Guaranteed floor:** because the default path forks a working scaffold and the Wk 9
  checkpoint enforces valid output, every team enters the red-team phase with an agent worth
  attacking. A team that can’t ship its own may be assigned a provided agent so red/blue still
  runs.
- **Graded on process, not on who wins.** Your defense grade does **not** depend on how hard
  your opponent hit you. What’s graded: did you measure ASR before *and* after, document your
  exploits and mitigations, and reason honestly about what generalizes? (Sequential model:
  everyone attacks in Ch.4, everyone defends in Ch.5. A simultaneous CTF-style variant is
  possible but harder to grade fairly.)

---

## 6. Assessment _(proposed weights — instructor to finalize)_

| Component | Weight | Module |
|---|---|---|
| Foundations & AI-engineering labs | 20% | Ch.1–2 |
| Agent build + baseline evaluation | 25% | Ch.3 |
| Red team (attacks + exploit report) | 20% | Ch.4 |
| Blue team (defenses + before/after ASR) | 25% | Ch.5 |
| Participation / reading responses | 10% | all |

- **No traditional final exam.** The capstone presentation + writeup is the culminating
  assessment; the May 10–14 exam period is reserved for makeup / overflow only.
- Late policy, regrade policy, and per-lab rubrics: _TBD_.

---

## 7. Use of AI in this course _(policy)_

This course **teaches** using AI to accelerate engineering, so AI assistance is **expected**,
not merely permitted. With that come three rules:

1. **You own what you submit.** You must understand, and be able to explain and defend, every
   line you turn in — including AI-generated code and text. “The AI wrote it” is not a defense.
2. **Disclose it.** Note where AI meaningfully shaped your work (which tool, for what).
3. **Never fabricate results.** AI may help you build and analyze; it may not invent data,
   metrics, or evidence. Grounding and honest evaluation are graded — and are the whole point.

Institution-specific academic-integrity language: _TBD_.

---

## 8. Logistics _(to be completed)_

- **Accessibility / accommodations:** _TBD_
- **Communication / discussion forum:** _TBD_
- **Required/optional readings:** posted per module _(TBD)_
- **Software setup:** per-module `README.md`; all labs are laptop-only, no GPU, no API key.

---

_This syllabus is a living draft. The schedule may shift with the official academic calendar
and class pace._
