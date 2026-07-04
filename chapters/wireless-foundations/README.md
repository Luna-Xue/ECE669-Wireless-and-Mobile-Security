# Ch.1 — Wireless & Mobile Security: Foundations

> The domain and the vocabulary the rest of the course reuses: the wireless attack
> surface from the RF medium up to O-RAN, and the identity/PII that lives in it.

**Module of [ECE 669 — Wireless and Mobile Security](../../SYLLABUS.md) · Weeks 1–3**

> 🚧 **Status:** landing page + outline. Runnable lab (capture analysis) coming.

## What this module is about

Wireless is different from wired because the medium itself — radio — is shared,
broadcast, and attackable. This module establishes:

- **The attack surface**, opened with real attacks: IMSI catchers / rogue base stations,
  Wi-Fi KRACK, protocol downgrade, and **physical-layer attacks** (jamming, GPS spoofing,
  eavesdropping).
- **The stack as shared vocabulary** — PHY/RF → MAC → NAS/RRC/GTP (cellular) /
  802.11 + EAP (Wi-Fi) → 5G core (AMF/SMF/UPF/UDM) → **O-RAN** disaggregation, and why one
  fault cascades into many symptoms.
- **Authentication, identity & privacy** — 5G-AKA, SUPI/SUCI, EAP, mobile-device identity —
  which sets up the subscriber-PII / trust-boundary theme used all term.

## Physical-layer security — scope

We treat PHY as **attack surface** (jamming, spoofing, eavesdropping, RF fingerprinting) and
later as an **AI-diagnosable domain** (see [Ch.3](../train-an-agent/)). We do **not** build an
information-theoretic secrecy module (wiretap channel / secrecy capacity / artificial noise);
those are optional reading, and an optional project track for a comms-heavy cohort.

## Hands-on (planned)

- Analyze a provided call-flow / packet capture; label the identities present and mark the
  trust boundaries.

## Weekly

- **Wk 1** — attack surface + PHY attacks + threat modeling
- **Wk 2** — the stack as vocabulary; cellular security evolution; RF fingerprinting
- **Wk 3** — authentication, identity & privacy: 5G-AKA, SUPI/SUCI, EAP

---

Next → [Ch.2 — Security × AI-Assisted Engineering](../security-and-ai-engineering/) ·
[Syllabus](../../SYLLABUS.md)
