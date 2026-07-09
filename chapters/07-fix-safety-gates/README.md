# Chapter 7: Fix It — Safety Gates Before Control

> **Fix It.** Put verifiable gates between the AI's recommendation and any control surface,
> then re-run the attacks and show the before/after difference.

**ECE 669 · [Course README](../../README.md) · [Syllabus](../../SYLLABUS.md)**

> 🚧 **Status:** landing page + outline.

## Topics — the gates

- **Grounding verifier** — reject a conclusion its own cited evidence does not support.
- **Policy gate** — enforce the agent's stated rules (scope, allowed outputs).
- **Wireless / PLS validator** — sanity-check any power/beam/secrecy-related recommendation.
- **ISAC validator** — check sensing confidence and cross-source agreement.
- **Robot-safety validator** — block recommendations that would be unsafe in the simulated
  robot-car scenario.
- **Human approval** — a person signs off before anything consequential.
- **Principle:** *LLM-in-the-loop, not LLM-in-control.*

## Lab — Fix It (before/after)

Add the gates to your defended configuration, re-run the [Ch. 6](../06-break-red-team/)
attacks, and report **attack-success before vs. after**. The delta — not a claim — is the
result.

---

← [Chapter 6](../06-break-red-team/) ·
Next → [Chapter 8: Wireless / PLS / ISAC Consequences](../08-wireless-pls-isac-consequences/)
