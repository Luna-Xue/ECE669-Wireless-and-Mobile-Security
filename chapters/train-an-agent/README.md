# Ch.3 — Train an Agent in a System

> Learn what it means to train an agent *inside a system* — using the AI-RAN diagnosis
> explainer as a fully worked example — then build your own for a wireless/mobile problem
> you choose.

**Module of [ECE 669 — Wireless and Mobile Security](../../SYLLABUS.md) · Weeks 7–10**

> ✅ **Worked example / scaffold is ready:** [`../ai-ran-diagnosis/`](../ai-ran-diagnosis/)
> (runnable, no GPU, no API key). This page is the **build-your-own project brief**.

## Start from the worked example

Run [**`../ai-ran-diagnosis/`**](../ai-ran-diagnosis/) end-to-end (its `README.md` +
`LAB.md`). It is one complete instance of the recipe below: a causal-DAG generator mints
labeled O-RAN/5G logs, a fine-tuned 1.5 B model reads a window and explains the root cause
with **cited evidence**, and it is evaluated scientifically.

## The reusable recipe

| Step | In the explainer | For your system |
|---|---|---|
| ① Define the system & problem | read O-RAN logs, find root cause | what does your agent read / do? what's ground truth? |
| ② Build a labeled-data generator | causal-DAG generator (labels free, accuracy measurable) | write one for your problem |
| ③ Define the I/O contract | `logs → evidence-cited diagnosis JSON` | your structured, checkable output |
| ④ Fine-tune a small model | QLoRA on a 1.5 B model (free Colab) | same LoRA flow |
| ⑤ Evaluate scientifically | accuracy + evidence grounding + hallucination + LOSO | your own metrics |

## Your agent must target a wireless/mobile system

Pick from (or propose near) this menu:

- fault-diagnosis agent for **Wi-Fi / 5G core / IoT / transport**
- network **configuration-audit** agent
- **alert triage / correlation** agent
- **protocol-compliance** checker
- **wireless task agent** — one that takes network actions (e.g., RIC xApp / config)
- **PHY/RF anomaly** agent — sync loss, jamming, RF-fingerprint anomaly
- **mobile device/OS** log-diagnosis agent

## Build path

- **Default = fork the explainer** ([`../ai-ran-diagnosis/`](../ai-ran-diagnosis/)). It is
  built for extension: adding a `Scenario` flows automatically through generator → dataset →
  UI → eval (see that chapter's `LAB.md`, Lab 6C).
- **From-scratch pipeline = advanced opt-in.**
- **Wk 9 hard checkpoint:** your agent must emit valid structured output — teams that miss it
  fall back to the pure fork, so everyone enters [Ch.4](../red-team-agents/) with an agent
  worth attacking.

## Deliverable → hands to Ch.4

At **Wk 10** hand in (a) the trained agent (adapter + I/O contract + a runner) and (b) a
one-page **spec sheet** (what it does, its system rules, its baseline metrics). Teams swap;
[Ch.4](../red-team-agents/) begins.

## Weekly

- **Wk 7** — the explainer as worked example; the 5-step recipe
- **Wk 8** — scope your wireless problem; fork the scaffold *(proposal check)*
- **Wk 9** — generate data + start training *(checkpoint)*
- **Wk 10** — evaluate; report baseline; **hand in & swap**

---

← [Ch.2](../security-and-ai-engineering/) · Next → [Ch.4](../red-team-agents/) ·
[Syllabus](../../SYLLABUS.md)
