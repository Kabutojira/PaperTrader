---
title: RTX — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-21'
updated: '2026-08-21'
provenance: deterministic-market-monitor
content_hash: 19de952490e0e3ee388e9d83fea1956d8e68820caefbc692256ef4b646c2566b
classifier_decision: ingest
classifier_reason: A new Bollinger Band lower-bound breach with a negative period
  return is a material indicator transition for the security.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_59304f90c440def31dc5
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_59304f90c440def31dc5
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-08-21'
  period_start: '2026-07-24'
  period_end: '2026-08-21'
  latest_close: '209.91000366210938'
  return_period: '-0.0135344222702746076006683724'
  strength: '0.005623870668764772503225665201'
  previous_strength: '0'
  source_price_hash: 580a3499652a8349e435e9643d781fd8f74d3e2eb3d5d94ad59685732d843f93
---

# RTX — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_59304f90c440def31dc5|RTX — RTX Corporation common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-24 through 2026-08-21
- Latest adjusted close: 209.91000366210938
- Period return: -0.0135344222702746076006683724
- Trigger strength: 0.005623870668764772503225665201
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new bollinger band lower-bound breach with a negative period return is a material indicator transition for the security.
