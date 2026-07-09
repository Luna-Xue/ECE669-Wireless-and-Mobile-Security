# Chapter 6: Break It — Red-Team the AI-Assisted Workflow

> **Break It.** Attack the agent's **context and decision chain** in the sandbox — not a real
> wireless system — and measure how often it can be misled.

**ECE 669 · [Course README](../../README.md) · [Syllabus](../../SYLLABUS.md)**

> 🚧 **Status:** landing page + outline. Uses the sandbox core in [`../ai-ran-diagnosis/`](../ai-ran-diagnosis/); its
> `samples/` (obvious vs. stealth injection) are the warm-up targets.

## ⚠️ Sandbox only

You are red-teaming a **classroom AI agent's inputs**, using **synthetic logs and mock
telemetry**. Nothing here touches a real network, transmits RF, or actuates control.
Jailbreak-style testing exists **only** to justify the gates you build in
[Ch. 7](../07-fix-safety-gates/). Read the
[Sandbox Safety Boundary](../../README.md#sandbox-safety-boundary) first.

## Topics

- **Hidden log injection** — instructions buried in synthetic log fields.
- **Fake telemetry** — fabricated counters that steer the diagnosis.
- **Sensing confusion** — contradictory or misleading simulated ISAC evidence.
- **Privacy-sensitive logs** — why identity-bearing evidence must stay local.
- **Jailbreak-style testing (sandbox only)** — attempts to bypass the agent's stated policy.
- **Surprise seeded issues** — instructor-planted problems to find and document.

## Lab — Break It report

Run the attacks above against your Ch. 5 baseline; record **attack-success** for each class
and the exact evidence that fooled the agent. This becomes the exploit report you defend
against in [Ch. 7](../07-fix-safety-gates/).

---

← [Chapter 5](../05-build-explainer-agent/) ·
Next → [Chapter 7: Fix It — Safety Gates Before Control](../07-fix-safety-gates/)
