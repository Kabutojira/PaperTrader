---
title: TXN — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-25'
updated: '2026-08-25'
provenance: deterministic-market-monitor
content_hash: b8f290fffde5d02c515e51603fe6e11d62da26ebd753e2bd736830534d8c169c
classifier_decision: ingest
classifier_reason: 'Material new downside transition: price fell 6.85% and entered
  below the lower Bollinger Band, warranting durable review.'
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_83a56943e18793f685b0
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_83a56943e18793f685b0
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-08-24'
  period_start: '2026-07-27'
  period_end: '2026-08-24'
  latest_close: '258.94000244140625'
  return_period: '-0.0685165595426447579488922467'
  strength: '0.007613006830531621072183620843'
  previous_strength: '0'
  source_price_hash: 710c147fd1e432bac7a4e41859c3bb55964fb384ebcc14a91a2bdca9fad65245
---

# TXN — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_83a56943e18793f685b0|TXN — Texas Instruments Incorporated common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-27 through 2026-08-24
- Latest adjusted close: 258.94000244140625
- Period return: -0.0685165595426447579488922467
- Trigger strength: 0.007613006830531621072183620843
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material new downside transition: price fell 6.85% and entered below the lower bollinger band, warranting durable review.
