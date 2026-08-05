---
title: '[ANET] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 5023765017be89b65ed522b45f49dccb8a0734db60a3fc522bc749ba5572c52a
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a 14.4% return over the
  validated period.
related_entity_ids:
- security_6f9a1450edceb9307c9a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_6f9a1450edceb9307c9a
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '190.50999450683594'
  return_period: '0.144479074990720998038315433'
  strength: '0.29663296'
  previous_strength: '0'
  source_price_hash: 48684b017d673413a4e371c384795d535d16c328688390035aae202012b50005
---

# [ANET] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_6f9a1450edceb9307c9a|ANET — Arista Networks, Inc. common stock]] (`security_6f9a1450edceb9307c9a`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 190.50999450683594
- Period return: 0.144479074990720998038315433
- Trigger strength: 0.29663296
- Previous strength: 0
- Source price hash: `48684b017d673413a4e371c384795d535d16c328688390035aae202012b50005`

## Classifier disposition

- Decision: `ingest`
- Reason: Material volume anomaly coincides with a 14.4% return over the validated period.
