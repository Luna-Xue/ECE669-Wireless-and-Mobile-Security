# Chapter 5: Build It — System Explainer Agent

> **Build It.** Stand up the sandbox explainer agent and establish how it behaves *before* any
> defense — the baseline you will attack and then harden.

**ECE 669 · [Course README](../../README.md) · [Syllabus](../../SYLLABUS.md)**

> ✅ **Runnable core:** [`../ai-ran-diagnosis/`](../ai-ran-diagnosis/) (local, no GPU, no API
> key). ISAC / robot-car / safety-gate modules are added in later chapters.

## Topics

- **Built-in LLM explorer** — a local explainer; **no external API required**.
- **Before-defense vs. defended explainer** — two configurations of the same agent, so you can
  measure the difference later.
- **Prompt and grounding configuration** — how the agent is told to cite evidence.
- **Evidence window** — the system map + synthetic logs / mock telemetry / RF-ISAC features
  from [Ch. 4](../04-evidence-trust-boundaries/).
- **Diagnostic recommendations only** — the agent *explains and recommends*; it never acts on
  a control surface.

## Lab — Build It checkpoint

Run and configure the explainer on the sandbox evidence window; capture its **baseline**
behavior in both the *before-defense* and *defended* configurations. Start here:

```bash
cd ../ai-ran-diagnosis && open ui/index.html   # or follow its README.md / LAB.md
```

Carry the baseline into [Ch. 6 — Break It](../06-break-red-team/).

---

← [Chapter 4](../04-evidence-trust-boundaries/) ·
Next → [Chapter 6: Break It — Red-Team the AI-Assisted Workflow](../06-break-red-team/)
