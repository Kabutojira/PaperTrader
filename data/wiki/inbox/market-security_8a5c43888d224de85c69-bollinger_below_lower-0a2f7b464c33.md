---
title: PLS.AX — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-11'
updated: '2026-09-11'
provenance: deterministic-market-monitor
content_hash: 0a2f7b464c332be8aa526168fbeb4c1720d565cf8a18d6e6edf2301ac081aae7
classifier_decision: ingest
classifier_reason: 'Material downside transition: price entered below the lower Bollinger
  Band after a 7.2% decline over the measured period.'
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_8a5c43888d224de85c69
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_8a5c43888d224de85c69
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-11'
  period_start: '2026-08-14'
  period_end: '2026-09-11'
  latest_close: '4.519999980926514'
  return_period: '-0.071868565268433795618579054'
  strength: '0.02046789320603614298820543001'
  previous_strength: '0'
  source_price_hash: 76c9567707755f50094daefaa0f5242e40a74130b63046f5d0f8b04eef1e4d29
---

# PLS.AX — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_8a5c43888d224de85c69|PLS.AX — PLS Group Limited ordinary shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-14 through 2026-09-11
- Latest adjusted close: 4.519999980926514
- Period return: -0.071868565268433795618579054
- Trigger strength: 0.02046789320603614298820543001
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material downside transition: price entered below the lower bollinger band after a 7.2% decline over the measured period.
