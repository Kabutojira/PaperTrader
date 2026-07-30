---
title: '[SPOT] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: fbb3838f144ddee8a376f7bd2239b94b34b73d99ad115e7dbd81085d2dcd68db
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2010347f1a0a5ea60f47
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '511.25'
  return_period: '0.105907526769141783589357609'
  strength: '0.01316309762256726300027470786'
  previous_strength: '0'
  source_price_hash: 77106c2d0040d89826c4a2bab5f7aec737b9937540497c477fe8efa7226f2e43
---

# [SPOT] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: SPOT — Spotify Technology S.A. ordinary shares (`security_2010347f1a0a5ea60f47`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 511.25
- Period return: 0.105907526769141783589357609
- Trigger strength: 0.01316309762256726300027470786
- Previous strength: 0
- Source price hash: `77106c2d0040d89826c4a2bab5f7aec737b9937540497c477fe8efa7226f2e43`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
