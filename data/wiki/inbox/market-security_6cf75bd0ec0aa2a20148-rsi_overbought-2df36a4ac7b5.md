---
title: '[TWST] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 2df36a4ac7b5e9db643a4c11e828204772518d15317da3a66902863e4c2a664f
classifier_decision: ingest
classifier_reason: Material RSI overbought transition coincides with a 28.7% period
  return and merits durable security-level context.
related_entity_ids:
- security_6cf75bd0ec0aa2a20148
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_6cf75bd0ec0aa2a20148
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '115.01000213623047'
  return_period: '0.286753252074332391938035041'
  strength: '0.02858827533333333333333333333'
  previous_strength: '0'
  source_price_hash: 9facb698cf75a5f6ee94966b77920922545557b565572613841d563961a6eb9c
---

# [TWST] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_6cf75bd0ec0aa2a20148|TWST — Twist Bioscience Corporation common stock]] (`security_6cf75bd0ec0aa2a20148`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 115.01000213623047
- Period return: 0.286753252074332391938035041
- Trigger strength: 0.02858827533333333333333333333
- Previous strength: 0
- Source price hash: `9facb698cf75a5f6ee94966b77920922545557b565572613841d563961a6eb9c`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought transition coincides with a 28.7% period return and merits durable security-level context.
