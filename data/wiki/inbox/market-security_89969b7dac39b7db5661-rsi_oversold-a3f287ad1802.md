---
title: '[YEC.F] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: a3f287ad180265bc2384046a59a6e07645da79eeae88c739ab700e1ad2612d60
classifier_decision: ingest
classifier_reason: Material new RSI oversold transition with a severe period decline
  for the identified security.
related_entity_ids:
- security_89969b7dac39b7db5661
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_89969b7dac39b7db5661
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-29'
  period_start: '2026-07-01'
  period_end: '2026-07-29'
  latest_close: '25'
  return_period: '-0.3622449103716458498917658084'
  strength: '0.05207951633333333333333333333'
  previous_strength: '0'
  source_price_hash: 13913fe9f36b6c39970bc802b6f80acc2755effa73cd8b31d7606adf7e8f16a8
---

# [YEC.F] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_89969b7dac39b7db5661|YEC.F — YASKAWA Electric Corporation Frankfurt ordinary shares]] (`security_89969b7dac39b7db5661`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-29
- Latest adjusted close: 25
- Period return: -0.3622449103716458498917658084
- Trigger strength: 0.05207951633333333333333333333
- Previous strength: 0
- Source price hash: `13913fe9f36b6c39970bc802b6f80acc2755effa73cd8b31d7606adf7e8f16a8`

## Classifier disposition

- Decision: `ingest`
- Reason: Material new RSI oversold transition with a severe period decline for the identified security.
