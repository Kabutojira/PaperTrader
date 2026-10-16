---
title: SSU.VI — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 6f69e9b235448d78c4192d6f6ce6a7a3b0c46eb162dddbc4cf1635fb72c7d692
classifier_decision: ingest
classifier_reason: New Bollinger-band breach with a 3.96% decline over the measured
  period merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_567d0d575bbd30aaa91d
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_567d0d575bbd30aaa91d
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '3880'
  return_period: '-0.0396039603960396039603960396'
  strength: '0.01088087188982299192031011084'
  previous_strength: '0'
  source_price_hash: f937a30eb4d88b0b8eb034bd9fa1d6730b2d012cfbf4a4ac85ec180e23acc416
---

# SSU.VI — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_567d0d575bbd30aaa91d|SSU.VI — Samsung Electronics common GDR]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 3880
- Period return: -0.0396039603960396039603960396
- Trigger strength: 0.01088087188982299192031011084
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach with a 3.96% decline over the measured period merits durable review.
