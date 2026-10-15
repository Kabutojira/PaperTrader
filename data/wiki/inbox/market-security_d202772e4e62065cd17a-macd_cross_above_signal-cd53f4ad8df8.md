---
title: FISV — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: cd53f4ad8df85278e9f34ef2febebce2dbb949e35ad5fa90865dea28fd6d807e
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a material indicator transition
  for the identified security despite the recent negative return.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_d202772e4e62065cd17a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_d202772e4e62065cd17a
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '46.06999969482422'
  return_period: '-0.0683518911216759510853117654'
  strength: '0.2174773545186214394162680273'
  previous_strength: '0'
  source_price_hash: a6e8c61fbec648ba11840b61631704dbcb9a02adabdd59ef1eadaf975a9e5122
---

# FISV — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_d202772e4e62065cd17a|FISV — Fiserv, Inc. common stock]]
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 46.06999969482422
- Period return: -0.0683518911216759510853117654
- Trigger strength: 0.2174773545186214394162680273
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new macd bullish crossover is a material indicator transition for the identified security despite the recent negative return.
