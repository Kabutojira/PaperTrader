---
title: '[LH] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: f8935339ca1b875bfd798483e2f7fa7cfb5791579cac8f368a72fe5c7db55eb2
classifier_decision: ingest
classifier_reason: Material RSI overbought transition after a 12.4% monthly gain warrants
  durable review.
related_entity_ids:
- security_b1f2c48e1a744f5ecf67
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_b1f2c48e1a744f5ecf67
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '314.23'
  return_period: '0.123935957836445827446144971'
  strength: '0.3185397063333333333333333333'
  previous_strength: '0'
  source_price_hash: 18c3bbb40ddcb0e9a286214e693bebeaea80016728504f9a827770dd637201e5
---

# [LH] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_b1f2c48e1a744f5ecf67|LH — Labcorp Holdings Inc. common stock]] (`security_b1f2c48e1a744f5ecf67`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 314.23
- Period return: 0.123935957836445827446144971
- Trigger strength: 0.3185397063333333333333333333
- Previous strength: 0
- Source price hash: `18c3bbb40ddcb0e9a286214e693bebeaea80016728504f9a827770dd637201e5`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought transition after a 12.4% monthly gain warrants durable review.
