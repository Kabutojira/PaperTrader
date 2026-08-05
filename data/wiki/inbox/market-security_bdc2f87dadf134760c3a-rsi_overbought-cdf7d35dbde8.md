---
title: '[PLTR] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: cdf7d35dbde87e670f3ebf239d8becc4dcfbad8b4a20d56969713eda4cd32ccf
classifier_decision: ingest
classifier_reason: Material RSI overbought transition after a 21.1% period return
  warrants durable review.
related_entity_ids:
- security_bdc2f87dadf134760c3a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_bdc2f87dadf134760c3a
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '162.66000366210938'
  return_period: '0.210538137775843795926265422'
  strength: '0.093319028'
  previous_strength: '0'
  source_price_hash: ad8a2a97c4bb28084f0693497b2e0bf1e7c5976fd93fe7ce40dc81f8861fea7a
---

# [PLTR] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_bdc2f87dadf134760c3a|PLTR — Palantir Technologies Inc. Class A common stock]] (`security_bdc2f87dadf134760c3a`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 162.66000366210938
- Period return: 0.210538137775843795926265422
- Trigger strength: 0.093319028
- Previous strength: 0
- Source price hash: `ad8a2a97c4bb28084f0693497b2e0bf1e7c5976fd93fe7ce40dc81f8861fea7a`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought transition after a 21.1% period return warrants durable review.
