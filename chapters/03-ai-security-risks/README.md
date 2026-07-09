# Chapter 3: AI Security Risks in Engineering Contexts

> The failure modes that appear once an AI reads untrusted evidence and produces
> recommendations — demonstrated safely against the sandbox agent.

**ECE 669 · [Course README](../../README.md) · [Syllabus](../../SYLLABUS.md)**

> 🚧 **Status:** landing page + outline. Risk-class catalog lab coming.

## Topics

- **Prompt injection through logs and retrieved context** — instructions hidden in data the
  agent is asked to read.
- **Context manipulation** — reshaping what the agent "knows" by controlling its inputs.
- **Fake telemetry and poisoned evidence** — plausible but fabricated measurements.
- **Hallucinated or unsupported explanations** — conclusions the cited evidence does not
  actually support.
- **Unsafe tool-use or control recommendations** — outputs that, if followed, would touch a
  control surface.
- **Policy bypass** — getting the agent to ignore its own stated rules.

## Lab

**Risk-class catalog** — reproduce each risk class above against the **sandbox** explainer
using **synthetic logs and mock telemetry**, and record how it manifests. This is the
vocabulary you weaponize (safely) in [Ch. 6](../06-break-red-team/) and defend against in
[Ch. 7](../07-fix-safety-gates/).

> **Sandbox only.** These risks are studied against the classroom agent's context and decision
> chain — never a real system. See the
> [Sandbox Safety Boundary](../../README.md#sandbox-safety-boundary).

---

← [Chapter 2](../02-ai-assisted-engineering/) ·
Next → [Chapter 4: AI-RAN System Evidence and Trust Boundaries](../04-evidence-trust-boundaries/)
