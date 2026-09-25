---
title: BAS — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-25'
updated: '2026-09-25'
provenance: deterministic-market-monitor
content_hash: 9d507689394575fe41d9db28e8d97a16e06180d7effee6535db53fe6fa5bca9b
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier response is not JSON'
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ef418f5ccc7dc5be8e65
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-25'
  period_start: '2026-08-28'
  period_end: '2026-09-25'
  latest_close: '50.41999816894531'
  return_period: '-0.0399848109389711767006932241'
  strength: '0.129473205'
  previous_strength: '0'
  source_price_hash: 041a5b825995215e01c5cf6e203bcd14fd001717df5032f2fb6acb62c0a2b3ab
---

# BAS — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: BAS — BASF SE registered shares
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-28 through 2026-09-25
- Latest adjusted close: 50.41999816894531
- Period return: -0.0399848109389711767006932241
- Trigger strength: 0.129473205
- Previous strength: 0

## Research disposition

- Decision: Blocked
- Reason: Classifier exited 2: hermes classifier response is not json
