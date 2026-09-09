---
title: BE — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-09'
updated: '2026-09-09'
provenance: deterministic-market-monitor
content_hash: c24bef51ddb5c44b09d16a1f65b2315d05bf453b2fcbeac022c852332ecc94c6
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with a material 31.6%
  price increase over the period, warranting durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_3e597863f00753e8c65c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_3e597863f00753e8c65c
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-08'
  period_start: '2026-08-10'
  period_end: '2026-09-08'
  latest_close: '277.2200012207031'
  return_period: '0.316146772986778640390708446'
  strength: '0.75182059'
  previous_strength: '0'
  source_price_hash: aeed94d46946d4d268c8ded358e2283d71dd1ce8d4b5ce18caa6abba6e4637b1
---

# BE — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_3e597863f00753e8c65c|BE — Bloom Energy Corporation Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-10 through 2026-09-08
- Latest adjusted close: 277.2200012207031
- Period return: 0.316146772986778640390708446
- Trigger strength: 0.75182059
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with a material 31.6% price increase over the period, warranting durable review.
