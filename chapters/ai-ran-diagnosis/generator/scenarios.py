"""Hand-authored failure DAGs + a background-noise pool.

Scenarios are chosen to match what an OAI gNB (CU/DU) + Open5GS testbed can
actually exhibit. `sync_loss` is kept for the demo but flagged synthetic-only
(it needs a real O-RU + 7.2 fronthaul + PTP, which RFsim/USRP setups don't have).

Message text mimics OAI ([SUBSYSTEM] tags) and Open5GS ([nf] tags) phrasing so
the generated logs look like the real ingestion target.

Each FaultNode also carries `paraphrases` — alternate wordings used only with
generate(augment=True) to fight lexical memorization. The canonical `messages`
are unchanged (default output is byte-identical); paraphrases may use
{cell}/{rnti}/{ip}/{drift}/{supi}/{rate} placeholders, filled by the generator.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .models import FaultNode as N
from .models import Scenario


# --- Scenario 1: PRB exhaustion at the O-DU scheduler ------------------------
_prb = Scenario(
    name="prb_exhaustion",
    summary="A traffic surge saturated the PRBs of cell 5; the O-DU scheduler "
    "ran out of radio resources, so admission control and downstream sessions failed.",
    recommended_actions=[
        "Check cell 5 offered load and PRB utilization (NR_MAC counters).",
        "Verify admission-control and scheduler limits; consider raising capacity.",
        "Offload cell 5 to a neighbor via an A1 policy or add a carrier.",
    ],
    nodes=[
        N("root", "O-DU", "WARN", "Traffic surge saturates PRBs on cell 5",
          ["[NR_MAC] cell 5 PRB utilization 92% and rising",
           "[NR_MAC] cell 5 PRB utilization 100% (saturated) for 1500ms"],
          paraphrases=[
              ["[NR_MAC] cell {cell} PRB utilization rising past 90%",
               "[NR_MAC] cell {cell} radio resources exhausted (PRB=100%) sustained"],
              ["[MAC] cell {cell} DL grant pressure high, PRB ~{rate}%",
               "[MAC] cell {cell} no free PRBs, scheduler fully booked >1s"],
          ]),
        N("admit", "O-DU", "ERROR", "Admission control rejects new bearers (no PRB)",
          ["[NR_MAC] admission control: no PRB available, rejecting DRB setup"],
          caused_by="root", delay_ms=700,
          paraphrases=[
              ["[NR_MAC] DRB setup rejected: no PRB for new bearer on cell {cell}"],
              ["[MAC] admission control denial — radio resource budget exhausted"],
          ]),
        N("rrc", "O-CU-CP", "WARN", "RRC setup failures rise on cell 5",
          ["[RRC] UE RRC setup failure, cause=radio-resources-unavailable"],
          caused_by="admit", delay_ms=400,
          paraphrases=[
              ["[RRC] RRCSetup rejected on cell {cell}: radio-resources-unavailable"],
              ["[RRC] connection setup failing, cause=no-radio-resources"],
          ]),
        N("upf", "UPF", "WARN", "Downlink buffering / discards build up at the UPF",
          ["[upf] WARNING: GTP-U downlink buffer high, packets being discarded"],
          caused_by="admit", delay_ms=500,
          paraphrases=[
              ["[upf] WARNING: N3 DL buffer filling, discard timer active"],
              ["[upf] WARNING: GTP-U downlink queue high, dropping packets"],
          ]),
    ],
)

# --- Scenario 2: AMF unreachable -> NGAP/N2 loss on the gNB ------------------
_ngap = Scenario(
    name="ngap_amf_down",
    summary="The AMF became unreachable; the gNB lost its NGAP/N2 (SCTP) "
    "association, so NG setup retries failed and new UE registrations were rejected.",
    recommended_actions=[
        "Check the AMF process health and the N2 SCTP association.",
        "Verify the gNB's AMF IP/port config and network reachability.",
        "Restore the AMF, then confirm NG Setup succeeds.",
    ],
    nodes=[
        N("root", "AMF", "ERROR", "AMF becomes unreachable (process down / N2 reset)",
          ["[amf] ERROR: ngap socket error on 127.0.0.5:38412, terminating association"],
          paraphrases=[
              ["[amf] ERROR: NGAP/SCTP shutdown on {ip}:38412, association terminated"],
              ["[amf] CRITICAL: AMF NGAP listener down ({ip}:38412) after peer reset"],
          ]),
        N("sctp", "O-CU-CP", "CRITICAL", "gNB loses SCTP/NGAP association to the AMF",
          ["[SCTP] association to peer 127.0.0.5 (AMF) is DOWN",
           "[NGAP] lost connection to AMF, no active NG association"],
          caused_by="root", delay_ms=250,
          paraphrases=[
              ["[SCTP] peer {ip} (AMF) association DOWN",
               "[NGAP] N2 link lost, no active NG association"],
              ["[SCTP] heartbeat to AMF {ip} failed, association closed",
               "[NGAP] AMF connection dropped, NG interface down"],
          ]),
        N("ngsetup", "O-CU-CP", "ERROR", "NG setup retries fail; no AMF available",
          ["[NGAP] NG Setup Request timeout, no AMF available",
           "[NGAP] retrying NG setup in 5000ms"],
          caused_by="sctp", delay_ms=5000,
          paraphrases=[
              ["[NGAP] NG Setup timed out — no AMF responding",
               "[NGAP] scheduling NG setup retry (backoff 5s)"],
              ["[NGAP] NGSetupRequest unanswered, AMF unavailable",
               "[NGAP] will retry NG setup shortly"],
          ]),
        N("reject", "O-CU-CP", "WARN", "New UE registrations rejected (core down)",
          ["[RRC] rejecting RRCSetup: AMF unavailable, cannot forward NAS"],
          caused_by="sctp", delay_ms=900,
          paraphrases=[
              ["[RRC] cannot forward NAS — AMF down, rejecting RRCSetup"],
              ["[RRC] new UE registration refused: no core connectivity"],
          ]),
        N("du", "O-DU", "INFO", "DU sees UE attach attempts stall after RA",
          ["[NR_MAC] UE RA success but RRC setup not completing (no core)"],
          caused_by="reject", delay_ms=600,
          paraphrases=[
              ["[NR_MAC] RA ok but RRC never completes (core unreachable)"],
              ["[MAC] UEs stuck after preamble — no NAS path to AMF"],
          ]),
    ],
)

# --- Scenario 3: F1 setup failure between O-DU and O-CU ----------------------
_f1 = Scenario(
    name="f1_setup_failure",
    summary="The O-DU offered an invalid cell configuration over F1; the O-CU "
    "rejected the F1 setup, so the cell never came up and no UE could attach.",
    recommended_actions=[
        "Inspect the O-DU served-cell config (PRACH/SSB params) in the F1 Setup Request.",
        "Compare the DU cell config against what the CU supports.",
        "Fix the cell config and re-establish F1.",
    ],
    nodes=[
        N("root", "O-DU", "ERROR", "O-DU sends F1 Setup Request with invalid cell config",
          ["[F1AP] sending F1 Setup Request (1 served cell)",
           "[F1AP] served cell 1 config: PRACH/SSB parameters out of range"],
          paraphrases=[
              ["[F1AP] DU sending F1 Setup Request to CU",
               "[F1AP] served cell {cell} PRACH/SSB params out of supported range"],
              ["[F1AP] initiating F1 setup (1 cell offered)",
               "[F1AP] cell {cell} config invalid: SSB/PRACH out of range"],
          ]),
        N("reject", "O-CU-CP", "ERROR", "O-CU rejects the F1 setup",
          ["[F1AP] F1 Setup Failure sent to DU, cause=cell-config-not-supported"],
          caused_by="root", delay_ms=300,
          paraphrases=[
              ["[F1AP] CU rejected F1 setup: cell-config-not-supported"],
              ["[F1AP] F1 Setup Failure -> DU (unsupported cell config)"],
          ]),
        N("celldown", "O-DU", "WARN", "O-DU cannot bring up the cell without F1",
          ["[F1AP] F1 Setup Failure received, cell 1 not served",
           "[NR_MAC] cell 1 remains DOWN (no F1 association)"],
          caused_by="reject", delay_ms=250,
          paraphrases=[
              ["[F1AP] DU got F1 Setup Failure, cell {cell} not brought up",
               "[NR_MAC] cell {cell} stays DOWN (no F1 association)"],
              ["[F1AP] F1 setup failed at DU; cell {cell} unserved",
               "[MAC] cell {cell} cannot activate without F1"],
          ]),
        N("noaccess", "O-CU-CP", "INFO", "No served cell -> no UE access",
          ["[RRC] no served cells available for UE access"],
          caused_by="reject", delay_ms=450,
          paraphrases=[
              ["[RRC] no served cell available — UEs cannot access"],
              ["[RRC] cell out of service, blocking UE access"],
          ]),
    ],
)

# --- Scenario 4: PTP/sync loss at the O-RU (synthetic-only) ------------------
_sync = Scenario(
    name="sync_loss",
    summary="The O-RU lost its PTP lock to the grandmaster clock and went into "
    "holdover; fronthaul timing drifted, the O-DU deactivated the cell, and UEs dropped.",
    note="Requires a real O-RU + 7.2 fronthaul + PTP to reproduce; synthetic-only "
    "on an RFsim/USRP testbed.",
    recommended_actions=[
        "Check grandmaster reachability and the O-RU PTP/SyncE lock state.",
        "Verify fronthaul S-plane timing and holdover status.",
        "Restore GM lock, then re-activate the affected cell.",
    ],
    nodes=[
        N("root", "O-RU", "CRITICAL", "PTP grandmaster clock lost at the O-RU",
          ["[FHI72] PTP: lost lock to grandmaster 10.0.0.1 (Announce timeout)",
           "[FHI72] clock entering HOLDOVER, free-running on local oscillator"],
          paraphrases=[
              ["[FHI72] S-plane: PTP Announce timeout from GM {ip}, sync lost",
               "[FHI72] servo unlocked -> HOLDOVER (local OCXO free-running)"],
              ["[PTP] BMCA: grandmaster {ip} unreachable, clock state=HOLDOVER",
               "[FHI72] phase/frequency holdover engaged, drift accumulating"],
          ]),
        N("fh", "O-DU", "ERROR", "Fronthaul timing windows start missing",
          ["[FHI72] DL T1a window miss on eAxC 0..7",
           "[PHY] eCPRI U-plane out of sync with O-RU (drift > 1.1us)"],
          caused_by="root", delay_ms=600,
          paraphrases=[
              ["[FHI72] DL T1a transmit window missed on eAxC 0..7",
               "[PHY] eCPRI U-plane desynchronized (drift > {drift}us)"],
              ["[FHI72] fronthaul DL timing window misses accumulating",
               "[PHY] U-plane out of sync with O-RU, drift {drift}us"],
          ]),
        N("cell", "O-DU", "ERROR", "Cell deactivated on persistent timing fault",
          ["[NR_MAC] cell 12 DEACTIVATED: timing fault, TA budget exceeded"],
          caused_by="fh", delay_ms=1300,
          paraphrases=[
              ["[NR_MAC] cell {cell} DEACTIVATED — timing fault, TA budget blown"],
              ["[MAC] cell {cell} taken down: persistent fronthaul timing error"],
          ]),
        N("rlf", "O-CU-CP", "WARN", "UEs drop with radio link failure",
          ["[RRC] UE context release surge on cell 12, cause=radioLinkFailure"],
          caused_by="fh", delay_ms=1000,
          paraphrases=[
              ["[RRC] surge of UE releases on cell {cell} (radioLinkFailure)"],
              ["[RRC] mass radioLinkFailure on cell {cell}, UEs dropping"],
          ]),
        N("core", "AMF", "INFO", "Core observes the UE context releases",
          ["[amf] INFO: UE context release (radio) for multiple SUPIs"],
          caused_by="rlf", delay_ms=500,
          paraphrases=[
              ["[amf] INFO: UE context releases (radio) for several SUPIs"],
              ["[amf] INFO: multiple UE context release (radio) events"],
          ]),
    ],
)

# --- Scenario 5: subscriber auth failure (provisioning error) ---------------
_auth = Scenario(
    name="auth_failure",
    summary="A subscriber key/OPc mismatch in the UDM caused 5G-AKA to fail at "
    "the AUSF, so the AMF rejected registration and the gNB released the UE.",
    recommended_actions=[
        "Check the subscriber's K/OPc provisioning in the UDM/UDR.",
        "Verify AUSF<->UDM connectivity and the configured auth method.",
        "Re-provision the subscriber and retry registration.",
    ],
    nodes=[
        N("root", "UDM", "ERROR", "Subscriber key/OPc mismatch in the UDM (provisioning error)",
          ["[udm] ERROR: authentication vector mismatch for imsi-999700000001234"],
          paraphrases=[
              ["[udm] ERROR: auth vector mismatch for {supi}"],
              ["[udm] ERROR: K/OPc mismatch computing AV for {supi}"],
          ]),
        N("ausf", "AUSF", "WARN", "AUSF confirms 5G-AKA authentication failure",
          ["[ausf] WARNING: 5G-AKA authentication failure (MAC failure)"],
          caused_by="root", delay_ms=200,
          paraphrases=[
              ["[ausf] WARNING: 5G-AKA failed (MAC failure)"],
              ["[ausf] WARNING: authentication rejected — AV verification failed"],
          ]),
        N("amf", "AMF", "WARN", "AMF rejects the registration",
          ["[amf] WARNING: Registration reject (cause=Illegal UE, auth failure)"],
          caused_by="ausf", delay_ms=250,
          paraphrases=[
              ["[amf] WARNING: Registration reject (Illegal UE, auth failure)"],
              ["[amf] WARNING: registration denied — authentication failure"],
          ]),
        N("rel", "O-CU-CP", "INFO", "gNB releases the UE after NAS auth reject",
          ["[RRC] releasing UE after NAS authentication failure"],
          caused_by="amf", delay_ms=400,
          paraphrases=[
              ["[RRC] releasing UE after NAS auth failure"],
              ["[RRC] UE released following authentication reject"],
          ]),
    ],
)


SCENARIOS: Dict[str, Scenario] = {
    s.name: s for s in (_prb, _ngap, _f1, _sync, _auth)
}


# Background routine lines, interleaved as noise. (component, severity, template)
# Templates may use {rnti} / {supi}; the generator fills both.
NOISE_TEMPLATES: List[Tuple[str, str, str]] = [
    ("O-DU", "INFO", "[NR_MAC] UE 0x{rnti} HARQ ACK/NACK stats nominal"),
    ("O-DU", "INFO", "[NR_RRC] periodic CSI report received from UE 0x{rnti}"),
    ("O-CU-CP", "INFO", "[RRC] UE context modification complete (UE 0x{rnti})"),
    ("O-CU-UP", "INFO", "[GTPU] DL tunnel stats nominal"),
    ("AMF", "INFO", "[amf] INFO: Registration complete for {supi}"),
    ("SMF", "INFO", "[smf] INFO: PDU session established ({supi}, IPv4)"),
    ("UPF", "INFO", "[upf] INFO: PFCP heartbeat OK"),
    ("AMF", "INFO", "[amf] INFO: periodic NG heartbeat to gNB OK"),
    ("O-DU", "INFO", "[NR_MAC] cell 7 PRB utilization 38% nominal"),
]

# DISTRACTOR noise: WARN/ERROR lines that are NOT the root cause. Mixed in only
# with generate(augment=True). Their purpose is to break the "loudest severity ==
# root cause" shortcut, so the model must reason about dependencies/ordering, not
# just grep for ERROR. These never appear in ground truth.
DISTRACTOR_TEMPLATES: List[Tuple[str, str, str]] = [
    ("O-DU", "WARN", "[NR_MAC] UE 0x{rnti} RLC retransmission rate elevated (transient)"),
    ("O-DU", "WARN", "[NR_MAC] cell {cell} PRB utilization {rate}% (busy hour)"),
    ("O-CU-UP", "WARN", "[GTPU] DL tunnel jitter spike on bearer, recovered"),
    ("O-CU-CP", "ERROR", "[RRC] UE 0x{rnti} measurement report decode error, retried OK"),
    ("SMF", "WARN", "[smf] WARNING: PFCP retransmit to UPF (seq mismatch), recovered"),
    ("UPF", "ERROR", "[upf] ERROR: transient nexthop ARP miss on N6, resolved"),
    ("AMF", "WARN", "[amf] WARNING: NAS timer T3550 expiry for {supi}, UE retried"),
    ("O-RU", "WARN", "[FHI72] CU-plane SFP RX power low margin (within spec)"),
]
