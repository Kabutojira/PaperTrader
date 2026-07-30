---
title: '[GEV] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 9c7be5f40cd0baa9bb36e524450d988fa86065371a50b272c6b8a8a98570d8d1
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_4b61970aa8f574446819
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '946'
  return_period: '-0.1419579036737239090224033804'
  strength: '0.01020799019027844734925744084'
  previous_strength: '0'
  source_price_hash: 468a1ad56cf1a146163b86fc7a6372182c9066c9c52e34a29fc7d1290f4e9606
---

# [GEV] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_4b61970aa8f574446819|GEV — GE Vernova Inc. common stock]] (`security_4b61970aa8f574446819`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 946
- Period return: -0.1419579036737239090224033804
- Trigger strength: 0.01020799019027844734925744084
- Previous strength: 0
- Source price hash: `468a1ad56cf1a146163b86fc7a6372182c9066c9c52e34a29fc7d1290f4e9606`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
