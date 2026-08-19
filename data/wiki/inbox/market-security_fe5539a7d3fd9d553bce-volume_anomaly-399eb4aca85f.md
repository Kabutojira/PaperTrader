---
title: MSTR — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-19'
updated: '2026-08-19'
provenance: deterministic-market-monitor
content_hash: 399eb4aca85f4221504b65649e30cf57aee9eb2c311c37112be9b261e469c07c
classifier_decision: ingest
classifier_reason: A new volume-anomaly trigger with a material 4.24% period return
  warrants durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_fe5539a7d3fd9d553bce
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fe5539a7d3fd9d553bce
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-19'
  period_start: '2026-07-22'
  period_end: '2026-08-19'
  latest_close: '104.25'
  return_period: '0.042395738158208802602666486'
  strength: '0.85462057'
  previous_strength: '0'
  source_price_hash: 9c536fec7c458641d18c6bc032b0634c2ad8cdba98f6f47ab1e9122e37b5dce5
---

# MSTR — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_fe5539a7d3fd9d553bce|MSTR — Strategy Inc Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-22 through 2026-08-19
- Latest adjusted close: 104.25
- Period return: 0.042395738158208802602666486
- Trigger strength: 0.85462057
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly trigger with a material 4.24% period return warrants durable review.
