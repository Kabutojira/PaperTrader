---
title: EVK — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-11'
updated: '2026-09-11'
provenance: deterministic-market-monitor
content_hash: 30a03b792ae756fdce15161109a90b024e9acd2092e558c2554d68cc4a1f81dc
classifier_decision: ingest
classifier_reason: New Bollinger-band breach transition with a negative 28-day return
  merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ccb25582c0392492fe9e
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ccb25582c0392492fe9e
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-11'
  period_start: '2026-08-14'
  period_end: '2026-09-11'
  latest_close: '17.860000610351562'
  return_period: '-0.0099778434612413235633017791'
  strength: '0.001386214532495139444660168685'
  previous_strength: '0'
  source_price_hash: cac60b8a132aaafe05a05f990d57817f433280a73f9b62f00b80a5a55f2fa498
---

# EVK — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: EVK — Evonik Industries AG registered shares
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-14 through 2026-09-11
- Latest adjusted close: 17.860000610351562
- Period return: -0.0099778434612413235633017791
- Trigger strength: 0.001386214532495139444660168685
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach transition with a negative 28-day return merits durable review.
