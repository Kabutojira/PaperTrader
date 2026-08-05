---
title: '[CRSR] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 1f18981b3fff15ce712bba8271c867601c3f468b08a7023d8446425187322f32
classifier_decision: ingest
classifier_reason: Material 26.4% period return with a newly entered volume anomaly
  warrants durable review.
related_entity_ids:
- security_55c9ce2fdcd32dad6b8c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_55c9ce2fdcd32dad6b8c
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '11.199999809265137'
  return_period: '0.264108379600711877990273399'
  strength: '0.053972925'
  previous_strength: '0'
  source_price_hash: 0266cc03b3f704975c9d818425e035b2fe369f0d25a4e0f9c9d0225ef5c95a6a
---

# [CRSR] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_55c9ce2fdcd32dad6b8c|CRSR — Corsair Gaming, Inc. common stock]] (`security_55c9ce2fdcd32dad6b8c`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 11.199999809265137
- Period return: 0.264108379600711877990273399
- Trigger strength: 0.053972925
- Previous strength: 0
- Source price hash: `0266cc03b3f704975c9d818425e035b2fe369f0d25a4e0f9c9d0225ef5c95a6a`

## Classifier disposition

- Decision: `ingest`
- Reason: Material 26.4% period return with a newly entered volume anomaly warrants durable review.
