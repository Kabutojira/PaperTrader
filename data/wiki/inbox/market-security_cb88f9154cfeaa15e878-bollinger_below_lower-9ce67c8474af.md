---
title: '[VRT] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 9ce67c8474affc529f76287cc4e7f6b8c02c5dab913ad0b7fe9e21edfa5137ee
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cb88f9154cfeaa15e878
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '270'
  return_period: '-0.1204352251805956519296635757'
  strength: '0.01896830978955694896352110355'
  previous_strength: '0'
  source_price_hash: 6015c26eb2013ddf6be465a59f79002760b86741ddb67f56aad5fd23a0f1fd38
---

# [VRT] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: VRT — Vertiv Holdings Co Class A common stock (`security_cb88f9154cfeaa15e878`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 270
- Period return: -0.1204352251805956519296635757
- Trigger strength: 0.01896830978955694896352110355
- Previous strength: 0
- Source price hash: `6015c26eb2013ddf6be465a59f79002760b86741ddb67f56aad5fd23a0f1fd38`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
