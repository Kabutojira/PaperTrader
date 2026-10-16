---
title: 108490 — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: db9010273355d312ebb90378419d8bd336ca9d01fefab4d93b9c409432f9455c
classifier_decision: ingest
classifier_reason: 'Material new downside transition: price entered below the lower
  Bollinger Band after a 32.8% period decline.'
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_0c8b3c4291cd97f56d8c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_0c8b3c4291cd97f56d8c
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-15'
  period_start: '2026-09-11'
  period_end: '2026-10-15'
  latest_close: '217500'
  return_period: '-0.3276661514683153013910355487'
  strength: '0.08265998643706258486300463606'
  previous_strength: '0'
  source_price_hash: 44b33da4de4f9514b92247273f99ec30813c51008c821cd094a27735de29ee1c
---

# 108490 — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_0c8b3c4291cd97f56d8c|108490 — ROBOTIS Co., Ltd. common shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-11 through 2026-10-15
- Latest adjusted close: 217500
- Period return: -0.3276661514683153013910355487
- Trigger strength: 0.08265998643706258486300463606
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material new downside transition: price entered below the lower bollinger band after a 32.8% period decline.
