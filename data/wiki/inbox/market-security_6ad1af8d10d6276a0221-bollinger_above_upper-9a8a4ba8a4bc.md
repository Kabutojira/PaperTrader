---
title: '[SCCO] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 9a8a4ba8a4bc68df822146941f91fe2976759cecaddf8b884f4aa1a84b819658
classifier_decision: ingest
classifier_reason: 'Material bullish breakout: price rose 14.97% over the period and
  newly crossed above the upper Bollinger Band.'
related_entity_ids:
- security_6ad1af8d10d6276a0221
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_6ad1af8d10d6276a0221
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '195.16000366210938'
  return_period: '0.149690743223030220913107511'
  strength: '0.00441032056147351498858904824'
  previous_strength: '0'
  source_price_hash: 2562e7435edf8fdcf9b79bc78ce9defa4f2680ea34502256e2acfd7d48becd7b
---

# [SCCO] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_6ad1af8d10d6276a0221|SCCO — Southern Copper Corporation common stock]] (`security_6ad1af8d10d6276a0221`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 195.16000366210938
- Period return: 0.149690743223030220913107511
- Trigger strength: 0.00441032056147351498858904824
- Previous strength: 0
- Source price hash: `2562e7435edf8fdcf9b79bc78ce9defa4f2680ea34502256e2acfd7d48becd7b`

## Classifier disposition

- Decision: `ingest`
- Reason: Material bullish breakout: price rose 14.97% over the period and newly crossed above the upper Bollinger Band.
