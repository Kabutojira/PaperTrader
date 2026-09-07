---
title: ANIC.L — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-07'
updated: '2026-09-07'
provenance: deterministic-market-monitor
content_hash: 479448d9d62b4fb6d9f7631177e195af7c7061863701357a73ea61c3d3b85480
classifier_decision: ingest
classifier_reason: New Bollinger lower-band breach with a material one-month decline
  merits durable review for security fe4648901e7675f157fd.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_fe4648901e7675f157fd
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fe4648901e7675f157fd
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-07'
  period_start: '2026-08-07'
  period_end: '2026-09-07'
  latest_close: '0.050999999046325684'
  return_period: '-0.0555555898956795663710910852'
  strength: '0.001211686012954793860859384899'
  previous_strength: '0'
  source_price_hash: 0811a9e487637ae77f3f615be7d9e04e0ad3aee55edf8b34f41215aa7e3b3acf
---

# ANIC.L — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: ANIC.L — Agronomics Limited ordinary shares
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-07 through 2026-09-07
- Latest adjusted close: 0.050999999046325684
- Period return: -0.0555555898956795663710910852
- Trigger strength: 0.001211686012954793860859384899
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger lower-band breach with a material one-month decline merits durable review for security fe4648901e7675f157fd.
