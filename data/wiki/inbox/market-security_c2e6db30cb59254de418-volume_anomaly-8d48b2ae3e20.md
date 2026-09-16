---
title: XMTR — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-16'
updated: '2026-09-16'
provenance: deterministic-market-monitor
content_hash: 8d48b2ae3e20df15dd0e91139a79523c67f342b00506b246e71fd8d2d1f2d45c
classifier_decision: ingest
classifier_reason: A newly entered high-strength volume anomaly with a negative multi-week
  return merits durable review for potential material price or risk context.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_c2e6db30cb59254de418
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c2e6db30cb59254de418
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-15'
  period_start: '2026-08-17'
  period_end: '2026-09-15'
  latest_close: '87.58499908447266'
  return_period: '-0.023905095199076370389188045'
  strength: '0.969042485'
  previous_strength: '0'
  source_price_hash: a6904761f05e4a922cd5ae1427849cf47c820c90769269812d9700c7de927d66
---

# XMTR — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c2e6db30cb59254de418|XMTR — Xometry, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-17 through 2026-09-15
- Latest adjusted close: 87.58499908447266
- Period return: -0.023905095199076370389188045
- Trigger strength: 0.969042485
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered high-strength volume anomaly with a negative multi-week return merits durable review for potential material price or risk context.
