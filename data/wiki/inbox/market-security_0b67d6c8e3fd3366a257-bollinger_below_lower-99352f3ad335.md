---
title: POWL — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 99352f3ad33531da07a8aa6ab2504a29efc6c2225c491de3fc9c6ee5ada52f07
classifier_decision: ingest
classifier_reason: A new Bollinger-band breach with a material negative return merits
  durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_0b67d6c8e3fd3366a257
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_0b67d6c8e3fd3366a257
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '169.52999877929688'
  return_period: '-0.04603009186613244053225264'
  strength: '0.02574738363192617136997927436'
  previous_strength: '0'
  source_price_hash: fa13f15e7ae541601c9b3b4a21bce4fc65ffc87c7bd58c8f1a643ae586a4a30b
---

# POWL — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_0b67d6c8e3fd3366a257|POWL — Powell Industries, Inc. common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 169.52999877929688
- Period return: -0.04603009186613244053225264
- Trigger strength: 0.02574738363192617136997927436
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new bollinger-band breach with a material negative return merits durable review.
