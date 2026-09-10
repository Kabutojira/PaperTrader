---
title: ALB — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-10'
updated: '2026-09-10'
provenance: deterministic-market-monitor
content_hash: cb81fea9c205fed559c61dc82bf2505d32e1bff72b3d6c9744b1b5b140df2ad1
classifier_decision: ingest
classifier_reason: New Bollinger-band breach after a 4.85% decline is a material security-specific
  market transition warranting review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_66cdcf90aac0d83e76f3
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_66cdcf90aac0d83e76f3
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-10'
  period_start: '2026-08-12'
  period_end: '2026-09-10'
  latest_close: '122.11000061035156'
  return_period: '-0.0485429009296281192675849734'
  strength: '0.01358109538142653067307790192'
  previous_strength: '0'
  source_price_hash: 0fade2898c0ee5a1d6b33861d4904cc000767e956df7400022c186a7dc5d5cdf
---

# ALB — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_66cdcf90aac0d83e76f3|ALB — Albemarle Corporation common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-12 through 2026-09-10
- Latest adjusted close: 122.11000061035156
- Period return: -0.0485429009296281192675849734
- Trigger strength: 0.01358109538142653067307790192
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach after a 4.85% decline is a material security-specific market transition warranting review.
