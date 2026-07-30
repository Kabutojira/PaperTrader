---
title: '[PYPL] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: c697a1ba1bf01c2d0a255011884f47ef11f12ace81f0d02b46d6bb016d538dcb
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_1e8fbdb0f45f2b413e00
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '58.3474'
  return_period: '0.314722816487709130736626942'
  strength: '0.2996448963333333333333333333'
  previous_strength: '0'
  source_price_hash: 28fde8ad1c74ff9e60779077d4000d42815135942213a61b2bdba2a2855eef14
---

# [PYPL] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PYPL — PayPal Holdings, Inc. common stock (`security_1e8fbdb0f45f2b413e00`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 58.3474
- Period return: 0.314722816487709130736626942
- Trigger strength: 0.2996448963333333333333333333
- Previous strength: 0
- Source price hash: `28fde8ad1c74ff9e60779077d4000d42815135942213a61b2bdba2a2855eef14`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
