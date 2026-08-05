---
title: '[PATH] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: d6eb134c708926640c477f911dd17872389c6c2d92b61acef3e86c81eff76988
classifier_decision: ingest
classifier_reason: Material entered RSI-overbought transition after a 21.03% period
  return; durable wiki ingestion is warranted.
related_entity_ids:
- security_eca976f0076a425ea1bb
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_eca976f0076a425ea1bb
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '14.100000381469727'
  return_period: '0.210300501559032525123365815'
  strength: '0.04023774733333333333333333333'
  previous_strength: '0'
  source_price_hash: 5834724c840fe582815a49fe7197e00f37f120b2c999abbd4f8beb1451f17c7e
---

# [PATH] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PATH — UiPath, Inc. Class A common stock (`security_eca976f0076a425ea1bb`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 14.100000381469727
- Period return: 0.210300501559032525123365815
- Trigger strength: 0.04023774733333333333333333333
- Previous strength: 0
- Source price hash: `5834724c840fe582815a49fe7197e00f37f120b2c999abbd4f8beb1451f17c7e`

## Classifier disposition

- Decision: `ingest`
- Reason: Material entered RSI-overbought transition after a 21.03% period return; durable wiki ingestion is warranted.
