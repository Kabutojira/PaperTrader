---
title: RXRX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-19'
updated: '2026-08-19'
provenance: deterministic-market-monitor
content_hash: b14430f3a3ebd7f379df377f5d9ddec0f44ea2720cce6ace4f12c1c547f569c8
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a 17.45% price gain over
  the validated period and merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ed7d5b616a196969c815
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ed7d5b616a196969c815
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-19'
  period_start: '2026-07-22'
  period_end: '2026-08-19'
  latest_close: '3.5'
  return_period: '0.174496636777937747993264504'
  strength: '0.31451288'
  previous_strength: '0'
  source_price_hash: 1b8be8ffd746ca849aff78ce4309e43a7abfc943c30621c153b3bd8d2c30a8ee
---

# RXRX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ed7d5b616a196969c815|RXRX — Recursion Pharmaceuticals, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-22 through 2026-08-19
- Latest adjusted close: 3.5
- Period return: 0.174496636777937747993264504
- Trigger strength: 0.31451288
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material volume anomaly coincides with a 17.45% price gain over the validated period and merits durable review.
