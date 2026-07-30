---
title: '[TSLA] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 3b8a9ff5dca273809547fd0c987af30b468b97138f7a84e3027babae56b92c2a
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_dc7a111e297be528d96b
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '306.86'
  return_period: '-0.2549048107793801079554905291'
  strength: '0.1024457156666666666666666667'
  previous_strength: '0'
  source_price_hash: 9913c5340953f6c4e54865acd6585a21684f8f9eab95f4eafc1a7ca1f49e5c87
---

# [TSLA] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: TSLA — Tesla, Inc. common stock (`security_dc7a111e297be528d96b`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 306.86
- Period return: -0.2549048107793801079554905291
- Trigger strength: 0.1024457156666666666666666667
- Previous strength: 0
- Source price hash: `9913c5340953f6c4e54865acd6585a21684f8f9eab95f4eafc1a7ca1f49e5c87`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
