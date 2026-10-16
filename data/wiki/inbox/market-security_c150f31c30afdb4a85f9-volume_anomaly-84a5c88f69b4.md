---
title: CROX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-18'
updated: '2026-09-18'
provenance: deterministic-market-monitor
content_hash: 84a5c88f69b47234e099ae48bc786da4e29a86bd34a5e3263c4efef4e85d07b5
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition with a negative period return merits
  durable review for potential material market activity.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_c150f31c30afdb4a85f9
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c150f31c30afdb4a85f9
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-17'
  period_start: '2026-08-19'
  period_end: '2026-09-17'
  latest_close: '123'
  return_period: '-0.0217132210613517748740997813'
  strength: '0.521341285'
  previous_strength: '0'
  source_price_hash: 189e62d19c95a3a4cbd98cff3228e7e73d9eae92d94782ecd09c4cfff4d62a5f
---

# CROX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c150f31c30afdb4a85f9|CROX — Crocs, Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-19 through 2026-09-17
- Latest adjusted close: 123
- Period return: -0.0217132210613517748740997813
- Trigger strength: 0.521341285
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly transition with a negative period return merits durable review for potential material market activity.
