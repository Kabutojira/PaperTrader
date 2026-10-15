---
title: MP — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 8f9be7e1d8b0b48d44dd64e1012a4cb1cf7cf180b4e44a217507b0aced87b26b
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with a material period
  decline and merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_cd492d97064d8574156e
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cd492d97064d8574156e
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '39.95000076293945'
  return_period: '-0.1845274669484409683393452313'
  strength: '0.25074968'
  previous_strength: '0'
  source_price_hash: 99534bed2ef9adbfead3b28c2644e532ee293f2c7845c375acd64c7ccf6f3819
---

# MP — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_cd492d97064d8574156e|MP — MP Materials Corp. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 39.95000076293945
- Period return: -0.1845274669484409683393452313
- Trigger strength: 0.25074968
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with a material period decline and merits durable review.
