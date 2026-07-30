---
title: '[LAC] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 2aef2a392f639d8668f6a489c8bb3801ffd6afaf8353d10c76b330fe6e060ec8
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fb87fac302a5446a1ced
  trigger: rsi_oversold
  transition: strengthened
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '2.8'
  return_period: '-0.2572944259506672170918874379'
  strength: '0.10839506'
  previous_strength: '0.041799304'
  source_price_hash: 73a1b3522099eda6de06ac88f7d135270a9dc1b8ab5c841b67acbb5104e1a1ce
---

# [LAC] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_fb87fac302a5446a1ced|LAC — Lithium Americas Corp. common shares]] (`security_fb87fac302a5446a1ced`)
- Trigger: `rsi_oversold`
- Transition: `strengthened`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 2.8
- Period return: -0.2572944259506672170918874379
- Trigger strength: 0.10839506
- Previous strength: 0.041799304
- Source price hash: `73a1b3522099eda6de06ac88f7d135270a9dc1b8ab5c841b67acbb5104e1a1ce`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
