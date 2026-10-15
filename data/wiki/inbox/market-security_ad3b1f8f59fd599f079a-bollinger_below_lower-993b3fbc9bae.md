---
title: HOOD — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 993b3fbc9bae69387392c7c275beef61e4f240e02d96ea333095e97252f21201
classifier_decision: ingest
classifier_reason: A new Bollinger lower-band breach with a roughly 3.2% period decline
  is a material security-specific market transition warranting durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ad3b1f8f59fd599f079a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ad3b1f8f59fd599f079a
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '101.08000183105469'
  return_period: '-0.0319861750283380176287991772'
  strength: '0.01006908756745964901748833298'
  previous_strength: '0'
  source_price_hash: 20661346b5e0cea1d8ad2f7b32dda5c8ffcd969dd9af1c7607f05de0d5bdc8bb
---

# HOOD — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ad3b1f8f59fd599f079a|HOOD — Robinhood Markets, Inc. Class A common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 101.08000183105469
- Period return: -0.0319861750283380176287991772
- Trigger strength: 0.01006908756745964901748833298
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new bollinger lower-band breach with a roughly 3.2% period decline is a material security-specific market transition warranting durable review.
