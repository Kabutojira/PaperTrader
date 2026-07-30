---
title: '[LH] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: ed7fba71f5427854c05ad07a1cb7606ca83125e9710141c292493a6aaef1c0b4
classifier_decision: ingest
classifier_reason: Material 12.4% period return with a new Bollinger-band breakout
  transition merits durable review.
related_entity_ids:
- security_b1f2c48e1a744f5ecf67
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_b1f2c48e1a744f5ecf67
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '314.23'
  return_period: '0.123935957836445827446144971'
  strength: '0.03449460410934637252467577291'
  previous_strength: '0'
  source_price_hash: 18c3bbb40ddcb0e9a286214e693bebeaea80016728504f9a827770dd637201e5
---

# [LH] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_b1f2c48e1a744f5ecf67|LH — Labcorp Holdings Inc. common stock]] (`security_b1f2c48e1a744f5ecf67`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 314.23
- Period return: 0.123935957836445827446144971
- Trigger strength: 0.03449460410934637252467577291
- Previous strength: 0
- Source price hash: `18c3bbb40ddcb0e9a286214e693bebeaea80016728504f9a827770dd637201e5`

## Classifier disposition

- Decision: `ingest`
- Reason: Material 12.4% period return with a new Bollinger-band breakout transition merits durable review.
