---
title: PLS.AX — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 5700ad1f4743a24abc80b811dccab835e56287c4af66e656341072d088be5ef2
classifier_decision: ingest
classifier_reason: 'Material downside transition: price entered below the lower Bollinger
  Band after a roughly 29.6% decline over the review period.'
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
  as_of_date: '2026-10-15'
  period_start: '2026-09-17'
  period_end: '2026-10-15'
  latest_close: '2.9700000286102295'
  return_period: '-0.2962084890351741328111319355'
  strength: '0.02282271277618048591979338116'
  previous_strength: '0'
  source_price_hash: 52892630417258111580000a243e9117dd68f3ca8f1882ddaa33f9c203dc3bcf
---

# PLS.AX — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_8a5c43888d224de85c69|PLS.AX — PLS Group Limited ordinary shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-17 through 2026-10-15
- Latest adjusted close: 2.9700000286102295
- Period return: -0.2962084890351741328111319355
- Trigger strength: 0.02282271277618048591979338116
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material downside transition: price entered below the lower bollinger band after a roughly 29.6% decline over the review period.
