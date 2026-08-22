---
title: SQM — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-22'
updated: '2026-08-22'
provenance: deterministic-market-monitor
content_hash: a3da4875cd675639960dd0df0fc12aacdb0e1ea191403ff3980d876209524813
classifier_decision: ingest
classifier_reason: Material 19.2% period return coincides with a newly entered volume
  anomaly and merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_9d4049ed6669a52815d6
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_9d4049ed6669a52815d6
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-21'
  period_start: '2026-07-24'
  period_end: '2026-08-21'
  latest_close: '81.95999908447266'
  return_period: '0.192492289849486751976123666'
  strength: '0.023418695'
  previous_strength: '0'
  source_price_hash: 49fd8cb5aa6164693e4c276890c5ce435f1b2e8c96642f6ee2d7538a4098df71
---

# SQM — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_9d4049ed6669a52815d6|SQM — Sociedad Quimica y Minera de Chile S.A. American depositary shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-24 through 2026-08-21
- Latest adjusted close: 81.95999908447266
- Period return: 0.192492289849486751976123666
- Trigger strength: 0.023418695
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material 19.2% period return coincides with a newly entered volume anomaly and merits durable review.
