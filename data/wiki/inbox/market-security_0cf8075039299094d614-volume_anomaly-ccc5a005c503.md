---
title: KTOS — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: ccc5a005c503f4258153e6974508e484240eed56ad24c1645910d53ee2240a4a
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with a material 15.5%
  decline over the measured period, warranting durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_0cf8075039299094d614
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_0cf8075039299094d614
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '47.459999084472656'
  return_period: '-0.1552154000237654544274716787'
  strength: '0.20201336'
  previous_strength: '0'
  source_price_hash: 64615f476eb1f546cd99648d185393ab4eda1fdda515a30c7bcc8c2e5d714382
---

# KTOS — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_0cf8075039299094d614|KTOS — Kratos Defense & Security Solutions, Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 47.459999084472656
- Period return: -0.1552154000237654544274716787
- Trigger strength: 0.20201336
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with a material 15.5% decline over the measured period, warranting durable review.
