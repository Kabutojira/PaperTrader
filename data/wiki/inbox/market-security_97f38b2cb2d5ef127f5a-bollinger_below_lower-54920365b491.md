---
title: PL — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-28'
updated: '2026-08-28'
provenance: deterministic-market-monitor
content_hash: 54920365b4919337827086191f044bb13684afb6d470a8444669682ecaf69431
classifier_decision: ingest
classifier_reason: New Bollinger-below-lower transition with a negative period return
  merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_97f38b2cb2d5ef127f5a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_97f38b2cb2d5ef127f5a
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-08-28'
  period_start: '2026-07-31'
  period_end: '2026-08-28'
  latest_close: '19.979999542236328'
  return_period: '-0.0244140630456968334100432744'
  strength: '0.006368644896013800762041067726'
  previous_strength: '0'
  source_price_hash: 1cfd25d542ef2fd9b2bed6e477fed431e64d31cdad831ff577cdf37d3e9740ad
---

# PL — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_97f38b2cb2d5ef127f5a|PL — Planet Labs PBC Class A common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-31 through 2026-08-28
- Latest adjusted close: 19.979999542236328
- Period return: -0.0244140630456968334100432744
- Trigger strength: 0.006368644896013800762041067726
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-below-lower transition with a negative period return merits durable review.
