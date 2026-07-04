# Ch.2 — Security × AI-Assisted Engineering

> Use AI to build and test faster — and see the security problems that speed drags in.
> Fuzzing is one classic technique here, not the whole point.

**Module of [ECE 669 — Wireless and Mobile Security](../../SYLLABUS.md) · Weeks 4–6**

> 🚧 **Status:** landing page + outline. Runnable labs coming.

## What this module is about

The course's future-of-engineering thesis lives here: **AI makes engineering faster, and
that speed introduces new security problems.**

- **Finding bugs, the classic way** — vulnerability classes, sanitizers, **fuzzing**
  (mutation / coverage-guided), targeting **wireless protocol parsers** (NAS/RRC/GTP/NGAP).
- **AI fastens development** — AI coding assistants; using AI to generate fuzz harnesses,
  seed corpora, and tests; LLM-as-reviewer for vulnerability triage.
- **…and drags in new problems** — insecure AI-generated code, hallucinated dependencies /
  supply-chain ("slopsquatting"), **indirect prompt injection** into dev tools, data leakage
  of proprietary code/PII, over-trust / automation bias.

## Hands-on (planned)

- Use an AI assistant to generate a fuzz harness for a protocol parser and produce a crash.
- Review a block of AI-generated code; find the vulnerability / hallucinated dependency it
  introduced.

## Bridge to the rest of the course

The skills here — using AI to generate data, harnesses, and evaluation code — are exactly what
you'll use in [Ch.3](../train-an-agent/) to build your own agent. And the **adversarial-input
mindset escalates**: a fuzzer's malformed field → a prompt injection aimed at an LLM → the
stealth injection your agent must survive.

## Weekly

- **Wk 4** — fuzzing wireless protocol parsers
- **Wk 5** — using AI to generate harnesses / tests / seeds
- **Wk 6** — AI's own risks: insecure code, hallucinated deps, indirect injection

---

← [Ch.1](../wireless-foundations/) · Next → [Ch.3](../train-an-agent/) ·
[Syllabus](../../SYLLABUS.md)
