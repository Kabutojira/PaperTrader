---
title: FUC.F — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-20'
updated: '2026-08-20'
provenance: deterministic-market-monitor
content_hash: 7a90cf00ae431a137dba0b7f2dd1616e39daf50731e691c7d4a6a7b1316391d1
classifier_decision: ingest
classifier_reason: Material Bollinger lower-band breach accompanied by a 12.4% decline
  over the measured period merits durable review.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_96ba305ee7cd586bc348
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_96ba305ee7cd586bc348
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-08-20'
  period_start: '2026-07-23'
  period_end: '2026-08-20'
  latest_close: '32.599998474121094'
  return_period: '-0.1238914464869005360513350864'
  strength: '0.007497629222381714620634182917'
  previous_strength: '0'
  source_price_hash: 2f1052c3dbcb90354f2345b90af0c18360ed77d53003108f01c8624255f1ae7d
---

# FUC.F — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_96ba305ee7cd586bc348|FUC.F — Fanuc Corporation Frankfurt ordinary shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-23 through 2026-08-20
- Latest adjusted close: 32.599998474121094
- Period return: -0.1238914464869005360513350864
- Trigger strength: 0.007497629222381714620634182917
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material bollinger lower-band breach accompanied by a 12.4% decline over the measured period merits durable review.
