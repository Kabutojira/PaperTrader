---
title: NIB.F — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 1249876a4ec16c89e539292cd3fc7409c89c7bf99d7a448feee1be5911297524
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with an 8.36% price increase
  over the validated period.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_3853e54c619d597dcaa1
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_3853e54c619d597dcaa1
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '15.447999954223633'
  return_period: '0.083613946791580872235884267'
  strength: '0.62313253'
  previous_strength: '0'
  source_price_hash: 59a44014342dd26c542299f8128daea26aee036dcbfd3a2eac68e2ffc2d90807
---

# NIB.F — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_3853e54c619d597dcaa1|NIB.F — Nidec Corporation Frankfurt ordinary shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 15.447999954223633
- Period return: 0.083613946791580872235884267
- Trigger strength: 0.62313253
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material volume anomaly coincides with an 8.36% price increase over the validated period.
