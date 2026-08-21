---
title: TXN — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-21'
updated: '2026-08-21'
provenance: deterministic-market-monitor
content_hash: 943760b250da03d95fe80c91285ef238ebabce538c8c953cba84281e78786635
classifier_decision: ingest
classifier_reason: Strengthened lower-Bollinger breach with a material negative period
  return merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_83a56943e18793f685b0
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_83a56943e18793f685b0
  trigger: bollinger_below_lower
  transition: strengthened
  as_of_date: '2026-08-20'
  period_start: '2026-07-23'
  period_end: '2026-08-20'
  latest_close: '265.6000061035156'
  return_period: '-0.0632656551552521797027918476'
  strength: '0.0006627576087722613065891282594'
  previous_strength: '0.0001461990795511793522399440696'
  source_price_hash: 0e829b05a93a1a8d391b1547ec722a31e20476390090bc9f7fb898c7af2a044e
---

# TXN — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_83a56943e18793f685b0|TXN — Texas Instruments Incorporated common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Strengthened
- Period: 2026-07-23 through 2026-08-20
- Latest adjusted close: 265.6000061035156
- Period return: -0.0632656551552521797027918476
- Trigger strength: 0.0006627576087722613065891282594
- Previous strength: 0.0001461990795511793522399440696

## Research disposition

- Decision: Ingest
- Reason: Strengthened lower-bollinger breach with a material negative period return merits durable review.
