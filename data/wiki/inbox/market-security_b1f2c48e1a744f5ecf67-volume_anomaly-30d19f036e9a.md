---
title: '[LH] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 30d19f036e9acb5f26d312d83561c78099f91ab6f3e4d0d00fcab8b68c9d946a
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition coincides with an 11.1% monthly
  price increase and merits durable review.
related_entity_ids:
- security_b1f2c48e1a744f5ecf67
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_b1f2c48e1a744f5ecf67
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '315.5299987792969'
  return_period: '0.111490747330195805628358084'
  strength: '0.002604165'
  previous_strength: '0'
  source_price_hash: 9c78f83e4556c3d92cc0a4e9e6bdb5ee48f713316b7fc182a6607be4663bcb5c
---

# [LH] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_b1f2c48e1a744f5ecf67|LH — Labcorp Holdings Inc. common stock]] (`security_b1f2c48e1a744f5ecf67`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 315.5299987792969
- Period return: 0.111490747330195805628358084
- Trigger strength: 0.002604165
- Previous strength: 0
- Source price hash: `9c78f83e4556c3d92cc0a4e9e6bdb5ee48f713316b7fc182a6607be4663bcb5c`

## Classifier disposition

- Decision: `ingest`
- Reason: A new volume-anomaly transition coincides with an 11.1% monthly price increase and merits durable review.
