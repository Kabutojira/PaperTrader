---
title: '[TX] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: e4ef2a75b52367a384a1d640b01d0ed7ca4b591498dde2845a307e651f4dc5ae
classifier_decision: ingest
classifier_reason: New RSI overbought transition after a material 25.2% period return
  merits durable wiki review.
related_entity_ids:
- security_2c779e81c27b78c556bb
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2c779e81c27b78c556bb
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '53.709999084472656'
  return_period: '0.252273253644196547167429413'
  strength: '0.2691640916666666666666666667'
  previous_strength: '0'
  source_price_hash: 7ee4570e35c66ddb262959d2b5b113993b4d641019caf73e86af15b901fbf42b
---

# [TX] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2c779e81c27b78c556bb|TX — Ternium S.A. ADS]] (`security_2c779e81c27b78c556bb`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 53.709999084472656
- Period return: 0.252273253644196547167429413
- Trigger strength: 0.2691640916666666666666666667
- Previous strength: 0
- Source price hash: `7ee4570e35c66ddb262959d2b5b113993b4d641019caf73e86af15b901fbf42b`

## Classifier disposition

- Decision: `ingest`
- Reason: New RSI overbought transition after a material 25.2% period return merits durable wiki review.
