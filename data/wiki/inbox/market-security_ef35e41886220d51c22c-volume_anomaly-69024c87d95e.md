---
title: ASML — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 69024c87d95ee946bf4553816d0ecc0755d8c763f2680932cf55a11b8f313a78
classifier_decision: ingest
classifier_reason: New volume-anomaly transition with a material 28-day price move
  merits durable security monitoring.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ef35e41886220d51c22c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ef35e41886220d51c22c
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '1650'
  return_period: '0.029821142022032723456666341'
  strength: '0.481767415'
  previous_strength: '0'
  source_price_hash: f51c9a7381293af39c1d895abd62fe3aec0a9ab4bab4645dc87e600cae8c85ae
---

# ASML — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ef35e41886220d51c22c|ASML — ASML Holding N.V. New York registered shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 1650
- Period return: 0.029821142022032723456666341
- Trigger strength: 0.481767415
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New volume-anomaly transition with a material 28-day price move merits durable security monitoring.
