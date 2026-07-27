---
title: '[RTX] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-27'
updated: '2026-07-27'
provenance: deterministic-market-monitor
content_hash: fac3019c410117ed77dfd518e8be9b7da6a00a6a9c1f0043faca1c96c8fb706e
classifier_decision: blocked
classifier_reason: classifier.command is not configured
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_59304f90c440def31dc5
  trigger: rsi_overbought
  transition: strengthened
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '212.7899932861328'
  return_period: '0.140414799627292645939915873'
  strength: '0.134651872'
  previous_strength: '0.1070968283333333333333333333'
  source_price_hash: 94734cb3ae46f9c1344318cefff3a33ecf3386d2efc1748f7530f8cc5bb615b1
---

# [RTX] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_59304f90c440def31dc5|RTX — RTX Corporation common stock]] (`security_59304f90c440def31dc5`)
- Trigger: `rsi_overbought`
- Transition: `strengthened`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 212.7899932861328
- Period return: 0.140414799627292645939915873
- Trigger strength: 0.134651872
- Previous strength: 0.1070968283333333333333333333
- Source price hash: `94734cb3ae46f9c1344318cefff3a33ecf3386d2efc1748f7530f8cc5bb615b1`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier.command is not configured
