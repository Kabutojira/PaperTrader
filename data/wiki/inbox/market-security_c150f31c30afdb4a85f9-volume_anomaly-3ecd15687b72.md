---
title: '[CROX] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 3ecd15687b720ccc9d07b54802974653aedad6266d19a290473d37dfca499663
classifier_decision: ingest
classifier_reason: High-strength volume anomaly transition merits durable review for
  the security.
related_entity_ids:
- security_c150f31c30afdb4a85f9
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c150f31c30afdb4a85f9
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '123.66000366210938'
  return_period: '-0.0041072281094989876201816448'
  strength: '0.93041873'
  previous_strength: '0'
  source_price_hash: 6cbdf40a812232ae34a5ae4b8e69e78fc649911237e36c745488e43bfa461277
---

# [CROX] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: CROX — Crocs, Inc. common stock (`security_c150f31c30afdb4a85f9`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 123.66000366210938
- Period return: -0.0041072281094989876201816448
- Trigger strength: 0.93041873
- Previous strength: 0
- Source price hash: `6cbdf40a812232ae34a5ae4b8e69e78fc649911237e36c745488e43bfa461277`

## Classifier disposition

- Decision: `ingest`
- Reason: High-strength volume anomaly transition merits durable review for the security.
