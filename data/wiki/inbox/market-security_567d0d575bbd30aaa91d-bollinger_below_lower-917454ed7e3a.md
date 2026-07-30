---
title: '[SSU.VI] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 917454ed7e3a7ab02934f72d22ec15b27935a8d0fe855b154ea7b186f3a67aca
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_567d0d575bbd30aaa91d
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-29'
  period_start: '2026-07-01'
  period_end: '2026-07-29'
  latest_close: '3220'
  return_period: '-0.2614678899082568807339449541'
  strength: '0.01710176860570747080249783746'
  previous_strength: '0'
  source_price_hash: 6eb025c45adfb61e4cb0d75f20bfdcf333ee0fbfc604998f4160f0fedb16fcdb
---

# [SSU.VI] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: SSU.VI — Samsung Electronics common GDR (`security_567d0d575bbd30aaa91d`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-29
- Latest adjusted close: 3220
- Period return: -0.2614678899082568807339449541
- Trigger strength: 0.01710176860570747080249783746
- Previous strength: 0
- Source price hash: `6eb025c45adfb61e4cb0d75f20bfdcf333ee0fbfc604998f4160f0fedb16fcdb`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
