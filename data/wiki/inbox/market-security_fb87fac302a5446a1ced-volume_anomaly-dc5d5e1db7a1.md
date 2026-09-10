---
title: LAC — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-10'
updated: '2026-09-10'
provenance: deterministic-market-monitor
content_hash: dc5d5e1db7a121215d3a64fc2b16af3b775050bd263a60797a286982ec26e7c3
classifier_decision: ingest
classifier_reason: A new strong volume-anomaly transition with a recent negative return
  merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_fb87fac302a5446a1ced
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fb87fac302a5446a1ced
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-09'
  period_start: '2026-08-11'
  period_end: '2026-09-09'
  latest_close: '3.190000057220459'
  return_period: '-0.0184615208552433846153846154'
  strength: '0.836989955'
  previous_strength: '0'
  source_price_hash: 71140c6c76487da427d2f9313c3b2c66bf5eaf12b611d1ce3a00289f993b1881
---

# LAC — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_fb87fac302a5446a1ced|LAC — Lithium Americas Corp. common shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-11 through 2026-09-09
- Latest adjusted close: 3.190000057220459
- Period return: -0.0184615208552433846153846154
- Trigger strength: 0.836989955
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new strong volume-anomaly transition with a recent negative return merits durable review.
