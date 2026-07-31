---
title: '[LH] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 0cbd43273f8abc6742ce0ec9d6d4033f81ed57a24b315bd979434b9d1ebaf56c
classifier_decision: ingest
classifier_reason: Material entry above the upper Bollinger Band after an 11.1% period
  return merits durable review.
related_entity_ids:
- security_b1f2c48e1a744f5ecf67
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_b1f2c48e1a744f5ecf67
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '315.5299987792969'
  return_period: '0.111490747330195805628358084'
  strength: '0.009698060433551013120248936506'
  previous_strength: '0'
  source_price_hash: 9c78f83e4556c3d92cc0a4e9e6bdb5ee48f713316b7fc182a6607be4663bcb5c
---

# [LH] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_b1f2c48e1a744f5ecf67|LH — Labcorp Holdings Inc. common stock]] (`security_b1f2c48e1a744f5ecf67`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 315.5299987792969
- Period return: 0.111490747330195805628358084
- Trigger strength: 0.009698060433551013120248936506
- Previous strength: 0
- Source price hash: `9c78f83e4556c3d92cc0a4e9e6bdb5ee48f713316b7fc182a6607be4663bcb5c`

## Classifier disposition

- Decision: `ingest`
- Reason: Material entry above the upper Bollinger Band after an 11.1% period return merits durable review.
