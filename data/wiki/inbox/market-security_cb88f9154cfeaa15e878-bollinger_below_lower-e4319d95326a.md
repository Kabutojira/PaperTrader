---
title: VRT — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: e4319d95326afe61e1080836f6808c985281353eff3fed686f1565d214b96e0e
classifier_decision: ingest
classifier_reason: New Bollinger-band breach after a material 6.9% decline warrants
  durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_cb88f9154cfeaa15e878
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cb88f9154cfeaa15e878
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '222.8300018310547'
  return_period: '-0.0692535883105988248155786735'
  strength: '0.03701879799186160318466606189'
  previous_strength: '0'
  source_price_hash: 931c64b5d807788f6aefdec6be8f38588c778eace8e81061cb65d72b35e58e20
---

# VRT — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_cb88f9154cfeaa15e878|VRT — Vertiv Holdings Co Class A common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 222.8300018310547
- Period return: -0.0692535883105988248155786735
- Trigger strength: 0.03701879799186160318466606189
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach after a material 6.9% decline warrants durable review.
