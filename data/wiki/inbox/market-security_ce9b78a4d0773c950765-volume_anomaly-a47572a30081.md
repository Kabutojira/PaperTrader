---
title: TSM — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: a47572a30081efb98f08deb0a19622838b2122da4f1d476583d3402500e17345
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition with a material price move merits
  durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ce9b78a4d0773c950765
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ce9b78a4d0773c950765
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '430'
  return_period: '0.029397679650031268118356593'
  strength: '0.21267291'
  previous_strength: '0'
  source_price_hash: 20c6573c43b1e6b1efc84c195a9625fc8f183b77c8fdc82fb9597c14361b9270
---

# TSM — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ce9b78a4d0773c950765|TSM — Taiwan Semiconductor Manufacturing Company Limited sponsored ADR]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 430
- Period return: 0.029397679650031268118356593
- Trigger strength: 0.21267291
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly transition with a material price move merits durable review.
