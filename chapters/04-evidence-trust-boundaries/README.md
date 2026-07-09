# Chapter 4: AI-RAN System Evidence and Trust Boundaries

> What counts as evidence in an AI-RAN setting, where it comes from, and how to verify it
> across sources — the foundation the explainer agent stands on.

**ECE 669 · [Course README](../../README.md) · [Syllabus](../../SYLLABUS.md)**

> 🚧 **Status:** landing page + outline. Uses the sandbox core in [`../ai-ran-diagnosis/`](../ai-ran-diagnosis/).

## Topics

- **System maps** — the components and links the agent reasons over (O-DU/O-CU/AMF/…).
- **Synthetic logs** — labelled, generated event streams (no real subscriber data).
- **Mock telemetry** — simulated KPIs/counters.
- **RF features** — simulated physical-layer signals/measurements.
- **Sensing / ISAC evidence** — simulated integrated sensing-and-communication observations.
- **Provenance and cross-source verification** — where each datum came from, and how to
  corroborate a claim across independent sources.

## Lab

**Evidence window** — assemble a system map plus a window of synthetic logs / mock telemetry /
simulated RF-ISAC evidence, and **tag the provenance** of each item. This evidence window is
what the agent explains in [Ch. 5](../05-build-explainer-agent/) and what attacks target in
[Ch. 6](../06-break-red-team/).

---

← [Chapter 3](../03-ai-security-risks/) ·
Next → [Chapter 5: Build It — System Explainer Agent](../05-build-explainer-agent/)
