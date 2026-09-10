---
title: LH — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-10'
updated: '2026-09-10'
provenance: deterministic-market-monitor
content_hash: 387c39664e550730760c0f74fa63536cfccd616b34cc98710f14c2cf5475af16
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition with a recent negative return merits
  recording for durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_b1f2c48e1a744f5ecf67
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_b1f2c48e1a744f5ecf67
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-09'
  period_start: '2026-08-11'
  period_end: '2026-09-09'
  latest_close: '321.1000061035156'
  return_period: '-0.0040940613772248347166016697'
  strength: '0.081128065'
  previous_strength: '0'
  source_price_hash: 783111eb8b7e150c49b2fa0cdc951280e8beaf3cc13baf2c3dd3524e598247be
---

# LH — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_b1f2c48e1a744f5ecf67|LH — Labcorp Holdings Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-11 through 2026-09-09
- Latest adjusted close: 321.1000061035156
- Period return: -0.0040940613772248347166016697
- Trigger strength: 0.081128065
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly transition with a recent negative return merits recording for durable review.
