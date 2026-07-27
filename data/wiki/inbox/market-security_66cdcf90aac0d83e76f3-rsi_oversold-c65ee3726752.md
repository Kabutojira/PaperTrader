---
title: '[ALB] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-26'
updated: '2026-07-27'
provenance: deterministic-market-monitor
content_hash: c65ee37267521e1793057696650bf98df1662de482aa0e0671383d265e28f68e
classifier_decision: ingest
classifier_reason: Material 18.5% decline with a newly entered RSI-oversold condition
  merits durable wiki review.
related_entity_ids:
- security_66cdcf90aac0d83e76f3
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_66cdcf90aac0d83e76f3
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '115'
  return_period: '-0.1846862991006022415214755387'
  strength: '0.159321905'
  previous_strength: '0'
  source_price_hash: 2dea6c9b3166d832613e3d9021d9afe936956993f06680ab200556b136c66fe7
---

# [ALB] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_66cdcf90aac0d83e76f3|ALB — Albemarle Corporation common stock]] (`security_66cdcf90aac0d83e76f3`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 115
- Period return: -0.1846862991006022415214755387
- Trigger strength: 0.159321905
- Previous strength: 0
- Source price hash: `2dea6c9b3166d832613e3d9021d9afe936956993f06680ab200556b136c66fe7`

## Classifier disposition

- Decision: `ingest`
- Reason: Material 18.5% decline with a newly entered RSI-oversold condition merits durable wiki review.
