---
title: MELI — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-17'
updated: '2026-09-17'
provenance: deterministic-market-monitor
content_hash: e34640d59bdb4abdaa2e70e93a268e00cc2220508c5ecdebbd939f769c5d7b05
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with a material 3.4% period
  return and warrants durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_4935c6e39e38273a1731
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_4935c6e39e38273a1731
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-16'
  period_start: '2026-08-18'
  period_end: '2026-09-16'
  latest_close: '1839.7099609375'
  return_period: '0.034044507902898958916177778'
  strength: '0.633598085'
  previous_strength: '0'
  source_price_hash: df1ab604048bdff63854e4de2288c2ee0a3b6e52b8f4bbf76bf7cbadca0550d3
---

# MELI — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_4935c6e39e38273a1731|MELI — MercadoLibre, Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-18 through 2026-09-16
- Latest adjusted close: 1839.7099609375
- Period return: 0.034044507902898958916177778
- Trigger strength: 0.633598085
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with a material 3.4% period return and warrants durable review.
