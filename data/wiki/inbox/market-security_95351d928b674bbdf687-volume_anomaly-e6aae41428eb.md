---
title: DNA — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-18'
updated: '2026-09-18'
provenance: deterministic-market-monitor
content_hash: e6aae41428ebd771cb8c030ffe4f365fa762e888b49c5395749d5204c83af7b5
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly is a material market-data transition
  for the identified security and merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_95351d928b674bbdf687
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_95351d928b674bbdf687
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-17'
  period_start: '2026-08-19'
  period_end: '2026-09-17'
  latest_close: '7.840000152587891'
  return_period: '0.016861233955604794234612285'
  strength: '0.5884823'
  previous_strength: '0'
  source_price_hash: a05fe1502db57491655ff13895322066e4321faec0120566a9a99e537f50b2a7
---

# DNA — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_95351d928b674bbdf687|DNA — Ginkgo Bioworks Holdings, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-19 through 2026-09-17
- Latest adjusted close: 7.840000152587891
- Period return: 0.016861233955604794234612285
- Trigger strength: 0.5884823
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly is a material market-data transition for the identified security and merits durable review.
