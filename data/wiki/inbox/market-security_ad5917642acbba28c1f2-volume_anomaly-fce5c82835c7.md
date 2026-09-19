---
title: TDY — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: fce5c82835c74489adaf95b27858d108c3905fd4d367a752d7840c56a2d5c514
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with a material five percent
  decline over the observed period and merits durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ad5917642acbba28c1f2
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ad5917642acbba28c1f2
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '603.4600219726562'
  return_period: '-0.0480952593221463346990596125'
  strength: '0.05972758'
  previous_strength: '0'
  source_price_hash: 80c9170390cfdd0fa89c28a3eeb2718973090e4bfb3e8954a7eaf7ae56848e83
---

# TDY — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ad5917642acbba28c1f2|TDY — Teledyne Technologies Incorporated common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 603.4600219726562
- Period return: -0.0480952593221463346990596125
- Trigger strength: 0.05972758
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with a material five percent decline over the observed period and merits durable review.
