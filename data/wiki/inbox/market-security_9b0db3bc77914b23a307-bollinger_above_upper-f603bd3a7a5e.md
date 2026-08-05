---
title: '[CSL] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: f603bd3a7a5e6d04f14c381b4d46fad87b6e99902da9aebf5a6cc54d2a316836
classifier_decision: ingest
classifier_reason: Material bullish volatility transition with a 9.2% period return
  and entry above the upper Bollinger Band.
related_entity_ids:
- security_9b0db3bc77914b23a307
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_9b0db3bc77914b23a307
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '386.42999267578125'
  return_period: '0.092011184920640669936179306'
  strength: '0.02630573834499371223378447745'
  previous_strength: '0'
  source_price_hash: c7961936fc94bd2cd46a765da704c01c6b5ff5d8680bee44f9fcec9c5726c536
---

# [CSL] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_9b0db3bc77914b23a307|CSL — Carlisle Companies Incorporated common stock]] (`security_9b0db3bc77914b23a307`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 386.42999267578125
- Period return: 0.092011184920640669936179306
- Trigger strength: 0.02630573834499371223378447745
- Previous strength: 0
- Source price hash: `c7961936fc94bd2cd46a765da704c01c6b5ff5d8680bee44f9fcec9c5726c536`

## Classifier disposition

- Decision: `ingest`
- Reason: Material bullish volatility transition with a 9.2% period return and entry above the upper Bollinger Band.
