---
title: '[TX] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: bfbf989faebd7b47f17ae5220755915f73cf93862b3bdc70d747e016f0ea480c
classifier_decision: ingest
classifier_reason: Material RSI overbought transition after a 13.35% one-month gain
  merits durable wiki ingestion for review.
related_entity_ids:
- security_2c779e81c27b78c556bb
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2c779e81c27b78c556bb
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '49.33'
  return_period: '0.133501826312592923608568384'
  strength: '0.017429371'
  previous_strength: '0'
  source_price_hash: 63545778e6269646e58130dc3ec3d9a44780c65e6701f114fcf73ac3ea637c89
---

# [TX] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2c779e81c27b78c556bb|TX — Ternium S.A. ADS]] (`security_2c779e81c27b78c556bb`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 49.33
- Period return: 0.133501826312592923608568384
- Trigger strength: 0.017429371
- Previous strength: 0
- Source price hash: `63545778e6269646e58130dc3ec3d9a44780c65e6701f114fcf73ac3ea637c89`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought transition after a 13.35% one-month gain merits durable wiki ingestion for review.
