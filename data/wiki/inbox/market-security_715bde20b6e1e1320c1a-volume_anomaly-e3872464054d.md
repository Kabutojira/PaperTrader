---
title: DLO — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-19'
updated: '2026-08-19'
provenance: deterministic-market-monitor
content_hash: e3872464054d9f05e9860ebe5ede380c1f6aa774ff47071b6fb003454659ebad
classifier_decision: ignore
classifier_reason: Volume anomaly is weak and the period return is negligible, so
  this transition does not merit durable wiki ingestion.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_715bde20b6e1e1320c1a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_715bde20b6e1e1320c1a
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-19'
  period_start: '2026-07-22'
  period_end: '2026-08-19'
  latest_close: '14.300000190734863'
  return_period: '0.002805046368233018034620951'
  strength: '0.21322168'
  previous_strength: '0'
  source_price_hash: 12f1ba28d42bc8c540ac4114200284327503649d1602a4f1ad4c86fa64360a35
---

# DLO — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_715bde20b6e1e1320c1a|DLO — DLocal Limited Class A common shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-22 through 2026-08-19
- Latest adjusted close: 14.300000190734863
- Period return: 0.002805046368233018034620951
- Trigger strength: 0.21322168
- Previous strength: 0

## Research disposition

- Decision: Ignore
- Reason: Volume anomaly is weak and the period return is negligible, so this transition does not merit durable wiki ingestion.
