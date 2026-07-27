---
title: '[RTX] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-26'
updated: '2026-07-26'
provenance: deterministic-market-monitor
content_hash: 22069206cbf52bc8f3c469dedb9daedf3a24d8d906960dfc34ec4146ab485e32
classifier_decision: blocked
classifier_reason: classifier.command is not configured
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_59304f90c440def31dc5
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '211.5'
  return_period: '0.133501281692511259596804542'
  strength: '0.1070968283333333333333333333'
  previous_strength: '0'
  source_price_hash: 67e4f6c67810fbf8b15203707d7c3be75ac5edd61740d920efdbcf4c82adb9b1
---

# [RTX] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_59304f90c440def31dc5|RTX — RTX Corporation common stock]] (`security_59304f90c440def31dc5`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 211.5
- Period return: 0.133501281692511259596804542
- Trigger strength: 0.1070968283333333333333333333
- Previous strength: 0
- Source price hash: `67e4f6c67810fbf8b15203707d7c3be75ac5edd61740d920efdbcf4c82adb9b1`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier.command is not configured
