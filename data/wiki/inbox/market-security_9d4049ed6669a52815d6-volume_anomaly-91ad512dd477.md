---
title: '[SQM] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 91ad512dd477d95d5dd1ecfa045f883c4b70522049d8c84674fd17ea489ea540
classifier_decision: ingest
classifier_reason: New volume anomaly coincides with a material 7.8% decline over
  the period and merits durable review.
related_entity_ids:
- security_9d4049ed6669a52815d6
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_9d4049ed6669a52815d6
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '68.43000030517578'
  return_period: '-0.0780113287563819400665433286'
  strength: '0.01854665'
  previous_strength: '0'
  source_price_hash: 50d8d4b3cc530dac62a1b9fc0b75b2b24eb271813ba5568f5f626eb60a05c8cc
---

# [SQM] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_9d4049ed6669a52815d6|SQM — Sociedad Quimica y Minera de Chile S.A. American depositary shares]] (`security_9d4049ed6669a52815d6`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 68.43000030517578
- Period return: -0.0780113287563819400665433286
- Trigger strength: 0.01854665
- Previous strength: 0
- Source price hash: `50d8d4b3cc530dac62a1b9fc0b75b2b24eb271813ba5568f5f626eb60a05c8cc`

## Classifier disposition

- Decision: `ingest`
- Reason: New volume anomaly coincides with a material 7.8% decline over the period and merits durable review.
