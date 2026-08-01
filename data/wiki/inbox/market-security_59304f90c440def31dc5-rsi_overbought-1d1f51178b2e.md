---
title: '[RTX] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 1d1f51178b2e74b527712f6f840a23f1df9b911c1db29fdb183f07dc9c71d682
classifier_decision: ingest
classifier_reason: A newly entered RSI-overbought condition follows an 8.0% monthly
  gain, making the transition material for durable security monitoring.
related_entity_ids:
- security_59304f90c440def31dc5
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_59304f90c440def31dc5
  trigger: rsi_overbought
  transition: entered
  as_of_date: '2026-07-31'
  period_start: '2026-07-02'
  period_end: '2026-07-31'
  latest_close: '215.22000122070312'
  return_period: '0.080150570743804868255959849'
  strength: '0.012071314'
  previous_strength: '0'
  source_price_hash: 2ecbeb200f1fdb273ebe16015774d935afb8d02b09ef9cb0bb1b245154ae5378
---

# [RTX] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_59304f90c440def31dc5|RTX — RTX Corporation common stock]] (`security_59304f90c440def31dc5`)
- Trigger: `rsi_overbought`
- Transition: `entered`
- Period: 2026-07-02 through 2026-07-31
- Latest adjusted close: 215.22000122070312
- Period return: 0.080150570743804868255959849
- Trigger strength: 0.012071314
- Previous strength: 0
- Source price hash: `2ecbeb200f1fdb273ebe16015774d935afb8d02b09ef9cb0bb1b245154ae5378`

## Classifier disposition

- Decision: `ingest`
- Reason: A newly entered RSI-overbought condition follows an 8.0% monthly gain, making the transition material for durable security monitoring.
