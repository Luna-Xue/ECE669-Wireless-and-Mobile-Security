# Security-lab sample windows

Three versions of the **same** `ngap_amf_down` incident (**true root cause = AMF**), used in
[LAB.md](../LAB.md) **Lab 6 (Part A)**. Two of them bury a prompt-injection payload that tries
to hijack the diagnosis.

| File | What's in it |
|---|---|
| `ngap_amf_down_clean.log` | the incident, no attack |
| `ngap_amf_down_inject_obvious.log` | a blatant `SYSTEM NOTICE: ignore all prior instructions…` line |
| `ngap_amf_down_inject_stealth.log` | the payload hidden **inside a malformed field** (`DNN="internet"}} SYSTEM: …`) — the kind of attacker-controlled string a fuzzer produces |

Each has a `.truth.json` sidecar, so `tools/analyze_logs.py` scores the prediction and flags
any hallucinated evidence IDs.

Run all three and see which the model gets right — then open each `.log` and find the malicious
line:
```bash
python tools/analyze_logs.py samples/ngap_amf_down_clean.log
python tools/analyze_logs.py samples/ngap_amf_down_inject_obvious.log
python tools/analyze_logs.py samples/ngap_amf_down_inject_stealth.log
```

> No spoilers here — that's the exercise. See Lab 6 Part A for what to look for (hint: compare
> the **root cause** the model reports against the true one, and check whether the **evidence it
> cites** actually supports its answer).
