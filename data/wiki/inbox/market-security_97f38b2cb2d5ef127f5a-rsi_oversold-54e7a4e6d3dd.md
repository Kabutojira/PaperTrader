---
title: '[PL] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 54e7a4e6d3dd52f5bc20cb80b496cf6f16e8fa8eefd1d1dfe4ee8c2b7fb15b8f
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_97f38b2cb2d5ef127f5a
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '20.2'
  return_period: '-0.3542199630249987706188779555'
  strength: '0.03823666133333333333333333333'
  previous_strength: '0'
  source_price_hash: 7ab9f36f1bba068eaa6d42bd40ae774f3083f26fb652c90927f5304142dcac3f
---

# [PL] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PL — Planet Labs PBC Class A common stock (`security_97f38b2cb2d5ef127f5a`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 20.2
- Period return: -0.3542199630249987706188779555
- Trigger strength: 0.03823666133333333333333333333
- Previous strength: 0
- Source price hash: `7ab9f36f1bba068eaa6d42bd40ae774f3083f26fb652c90927f5304142dcac3f`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
