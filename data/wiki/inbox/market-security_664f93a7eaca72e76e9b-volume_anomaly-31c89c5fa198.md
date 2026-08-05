---
title: '[SPCX] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 31c89c5fa198846cb8b30a8dc7a1311e031d4d5f24de07b32f39a74c142b7c86
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a significant 16.15% decline
  over the period and warrants durable review.
related_entity_ids:
- security_664f93a7eaca72e76e9b
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_664f93a7eaca72e76e9b
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '125.33000183105469'
  return_period: '-0.1615039753294977147446250858'
  strength: '0.729401635'
  previous_strength: '0'
  source_price_hash: 3ab632885320598f45206107e33a118d023f63b7dc9f3bb9b7451f07c5b6ae62
---

# [SPCX] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: SPCX — Space Exploration Technologies Corp. listed equity (`security_664f93a7eaca72e76e9b`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 125.33000183105469
- Period return: -0.1615039753294977147446250858
- Trigger strength: 0.729401635
- Previous strength: 0
- Source price hash: `3ab632885320598f45206107e33a118d023f63b7dc9f3bb9b7451f07c5b6ae62`

## Classifier disposition

- Decision: `ingest`
- Reason: Material volume anomaly coincides with a significant 16.15% decline over the period and warrants durable review.
