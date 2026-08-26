---
title: PARRO.PA — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-26'
updated: '2026-08-26'
provenance: deterministic-market-monitor
content_hash: 673e6a91061d231d8b693eb5c7192dd0dce71e4d58847fe4db7f78733f7c708a
classifier_decision: ingest
classifier_reason: A new Bollinger lower-band breach coincides with a material negative
  period return and merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_cc4dcb8f002b61dffe00
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cc4dcb8f002b61dffe00
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-08-26'
  period_start: '2026-07-29'
  period_end: '2026-08-26'
  latest_close: '9.199999809265137'
  return_period: '-0.0495868265266472610969942958'
  strength: '0.01568839422757197921063659811'
  previous_strength: '0'
  source_price_hash: 8ce0b2c196e48a698b4af0204b0c6ea9c4654e2bdc3d7e8f77d9a349f7bf9356
---

# PARRO.PA — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_cc4dcb8f002b61dffe00|PARRO.PA — Parrot S.A. ordinary shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-29 through 2026-08-26
- Latest adjusted close: 9.199999809265137
- Period return: -0.0495868265266472610969942958
- Trigger strength: 0.01568839422757197921063659811
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new bollinger lower-band breach coincides with a material negative period return and merits durable review.
