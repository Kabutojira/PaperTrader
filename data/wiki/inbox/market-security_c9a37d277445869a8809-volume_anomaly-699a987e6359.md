---
title: RBLX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-15'
updated: '2026-09-15'
provenance: deterministic-market-monitor
content_hash: 699a987e635982b19341e28cc7e5a43f777fa17e07a014e123fcc7f2ab69a52f
classifier_decision: ingest
classifier_reason: Entered volume-anomaly state with a large reported period return,
  warranting durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_c9a37d277445869a8809
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c9a37d277445869a8809
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-14'
  period_start: '2026-08-14'
  period_end: '2026-09-14'
  latest_close: '51.290000915527344'
  return_period: '0.341616571532060411125647305'
  strength: '0.1554254'
  previous_strength: '0'
  source_price_hash: ec0cbf8af8b3099705dfd57645d0194c73e568261918d125948e19429889b741
---

# RBLX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c9a37d277445869a8809|RBLX — Roblox Corporation Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-14 through 2026-09-14
- Latest adjusted close: 51.290000915527344
- Period return: 0.341616571532060411125647305
- Trigger strength: 0.1554254
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Entered volume-anomaly state with a large reported period return, warranting durable review.
