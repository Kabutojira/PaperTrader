---
title: TXN — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: e89fe9b4e144ca44e2a1246554db03470ed5ece5879d2e006d940d2b7e6b6cc5
classifier_decision: ingest
classifier_reason: New volume-anomaly transition with meaningful signal strength warrants
  recording for security review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_83a56943e18793f685b0
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_83a56943e18793f685b0
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '266.6400146484375'
  return_period: '0.003915694732765045608925877'
  strength: '1.056977235'
  previous_strength: '0'
  source_price_hash: 954efb3db297a5320415bd04d0cc34020a9f54587bcb4116439b198d7b470ae1
---

# TXN — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_83a56943e18793f685b0|TXN — Texas Instruments Incorporated common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 266.6400146484375
- Period return: 0.003915694732765045608925877
- Trigger strength: 1.056977235
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New volume-anomaly transition with meaningful signal strength warrants recording for security review.
