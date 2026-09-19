---
title: GEV — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: 914881877326931a3a004b8bed5cc39a8e0303a374537549d5a29be83eefd00b
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly with a 2.66% period decline is a
  material, time-bounded market transition worth recording for review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_4b61970aa8f574446819
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_4b61970aa8f574446819
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '940.3300170898438'
  return_period: '-0.02658356788871341377085441'
  strength: '0.101671655'
  previous_strength: '0'
  source_price_hash: 9ecccec8170700f7966aa39fc5fad0a989cf894cc51461f3d31b83c4aeeb58fe
---

# GEV — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_4b61970aa8f574446819|GEV — GE Vernova Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 940.3300170898438
- Period return: -0.02658356788871341377085441
- Trigger strength: 0.101671655
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly with a 2.66% period decline is a material, time-bounded market transition worth recording for review.
