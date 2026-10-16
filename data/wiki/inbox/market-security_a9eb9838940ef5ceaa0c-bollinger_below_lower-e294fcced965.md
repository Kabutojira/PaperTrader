---
title: FLNC — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-18'
updated: '2026-09-18'
provenance: deterministic-market-monitor
content_hash: e294fcced965eb55bf41c7095f20feabdf040d2414015188dd5b50a0f69869e8
classifier_decision: ingest
classifier_reason: New Bollinger lower-band breach with a substantial negative period
  return merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_a9eb9838940ef5ceaa0c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_a9eb9838940ef5ceaa0c
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-17'
  period_start: '2026-08-19'
  period_end: '2026-09-17'
  latest_close: '7.659999847412109'
  return_period: '-0.3653686792803464832078091105'
  strength: '0.09574370254185482276057390853'
  previous_strength: '0'
  source_price_hash: 6b8a1dee6fc4a029566cd7f41ae7fcf549836ce86a9ef8231ae6ee48c002404a
---

# FLNC — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_a9eb9838940ef5ceaa0c|FLNC — Fluence Energy, Inc. Class A common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-19 through 2026-09-17
- Latest adjusted close: 7.659999847412109
- Period return: -0.3653686792803464832078091105
- Trigger strength: 0.09574370254185482276057390853
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger lower-band breach with a substantial negative period return merits durable review.
