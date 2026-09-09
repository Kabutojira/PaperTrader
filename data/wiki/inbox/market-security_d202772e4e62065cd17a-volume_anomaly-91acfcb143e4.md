---
title: FISV — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-09'
updated: '2026-09-09'
provenance: deterministic-market-monitor
content_hash: 91acfcb143e47e6d332efc8409c6b17dfd5de0eac520dbf7cca698e3893e5b10
classifier_decision: ingest
classifier_reason: A new strong volume anomaly coincides with a material negative
  period return and warrants durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_d202772e4e62065cd17a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_d202772e4e62065cd17a
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-08'
  period_start: '2026-08-10'
  period_end: '2026-09-08'
  latest_close: '50.86000061035156'
  return_period: '-0.0260436725116808230278556171'
  strength: '0.74157957'
  previous_strength: '0'
  source_price_hash: 719d744701fade6b016eafa3afbb6127db0fe838397395fba219f5f3e1fae2eb
---

# FISV — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_d202772e4e62065cd17a|FISV — Fiserv, Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-10 through 2026-09-08
- Latest adjusted close: 50.86000061035156
- Period return: -0.0260436725116808230278556171
- Trigger strength: 0.74157957
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new strong volume anomaly coincides with a material negative period return and warrants durable review.
