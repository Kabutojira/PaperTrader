---
title: DDD — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: e77080f9ff88675da8ab9321c7ec81f16987fa2109818c302eb0af18076653a0
classifier_decision: ingest
classifier_reason: New Bollinger lower-band breach with a material 6.7% decline over
  the observed period merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_6ac6a6268ca7c08829ae
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_6ac6a6268ca7c08829ae
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '2.930000066757202'
  return_period: '-0.0668789908060788677247488524'
  strength: '0.05689122141197492162444348375'
  previous_strength: '0'
  source_price_hash: f54aed50866bb465bb1cde2fe97c0a44bfb39be58e549b1145d1ddd118e9afd4
---

# DDD — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: DDD — 3D Systems Corporation common stock
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 2.930000066757202
- Period return: -0.0668789908060788677247488524
- Trigger strength: 0.05689122141197492162444348375
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger lower-band breach with a material 6.7% decline over the observed period merits durable review.
