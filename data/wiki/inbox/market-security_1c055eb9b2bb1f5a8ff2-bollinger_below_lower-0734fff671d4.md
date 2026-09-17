---
title: RIO — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-17'
updated: '2026-09-17'
provenance: deterministic-market-monitor
content_hash: 0734fff671d435393c40d5b0379999dd1d6e335eb2a958ddc397e88c13cd2cb1
classifier_decision: ingest
classifier_reason: New Bollinger-band breach transition with negative return warrants
  durable monitoring context.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_1c055eb9b2bb1f5a8ff2
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_1c055eb9b2bb1f5a8ff2
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-16'
  period_start: '2026-08-18'
  period_end: '2026-09-16'
  latest_close: '95.79000091552734'
  return_period: '-0.0093081135914161061351408846'
  strength: '0.007156090520718895567004494606'
  previous_strength: '0'
  source_price_hash: 0a9fac13524ebbdcddf731be59d3af018dbb2575163396b94f732d36ead1ca91
---

# RIO — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_1c055eb9b2bb1f5a8ff2|RIO — Rio Tinto plc sponsored ADR]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-18 through 2026-09-16
- Latest adjusted close: 95.79000091552734
- Period return: -0.0093081135914161061351408846
- Trigger strength: 0.007156090520718895567004494606
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach transition with negative return warrants durable monitoring context.
