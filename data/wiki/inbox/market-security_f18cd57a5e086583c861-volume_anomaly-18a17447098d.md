---
title: PRLB — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-25'
updated: '2026-09-25'
provenance: deterministic-market-monitor
content_hash: 18a17447098dc4b34400ce4c4395f4594efef206b7a0c1442bb8042ea9f46709
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier response is not JSON'
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_f18cd57a5e086583c861
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-24'
  period_start: '2026-08-26'
  period_end: '2026-09-24'
  latest_close: '92.97000122070312'
  return_period: '0.179074229801237904723653934'
  strength: '0.202512435'
  previous_strength: '0'
  source_price_hash: 50910ce44d2ab354393e2a7bd04ff6301eb0d9a045c6bfd1ff16af530f2cbe65
---

# PRLB — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PRLB — Proto Labs, Inc. common stock
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-26 through 2026-09-24
- Latest adjusted close: 92.97000122070312
- Period return: 0.179074229801237904723653934
- Trigger strength: 0.202512435
- Previous strength: 0

## Research disposition

- Decision: Blocked
- Reason: Classifier exited 2: hermes classifier response is not json
