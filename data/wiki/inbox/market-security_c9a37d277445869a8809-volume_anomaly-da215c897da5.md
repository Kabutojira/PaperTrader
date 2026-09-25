---
title: RBLX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-25'
updated: '2026-09-25'
provenance: deterministic-market-monitor
content_hash: da215c897da5f59442fe5eb0d4f0ffbf9659de5e8b42821fd982e94afb22cf6e
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier response is not JSON'
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c9a37d277445869a8809
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-24'
  period_start: '2026-08-26'
  period_end: '2026-09-24'
  latest_close: '48.83000183105469'
  return_period: '0.300053249353121468097723011'
  strength: '0.089797015'
  previous_strength: '0'
  source_price_hash: 1dd37515bb333b4bf802c2c77440589ca468567e5f3e4beed0cb743d0b4967ed
---

# RBLX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c9a37d277445869a8809|RBLX — Roblox Corporation Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-26 through 2026-09-24
- Latest adjusted close: 48.83000183105469
- Period return: 0.300053249353121468097723011
- Trigger strength: 0.089797015
- Previous strength: 0

## Research disposition

- Decision: Blocked
- Reason: Classifier exited 2: hermes classifier response is not json
