---
title: '[LUNR] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 55b68c110daa564497ed71d436f9067b7a6a4f71f9f7c5befdec5145084635bc
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_a5dc16f3f4b245e6c168
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '12.3599'
  return_period: '-0.4105913016349625603967619382'
  strength: '0.07053970066666666666666666667'
  previous_strength: '0'
  source_price_hash: 3c216cd8e71f6e517a8e3e4fa076a216c0a0907221dc613d1c164cb02d9efe51
---

# [LUNR] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: LUNR — Intuitive Machines, Inc. Class A common stock (`security_a5dc16f3f4b245e6c168`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 12.3599
- Period return: -0.4105913016349625603967619382
- Trigger strength: 0.07053970066666666666666666667
- Previous strength: 0
- Source price hash: `3c216cd8e71f6e517a8e3e4fa076a216c0a0907221dc613d1c164cb02d9efe51`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
