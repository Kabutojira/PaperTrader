---
title: RXRX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-18'
updated: '2026-09-18'
provenance: deterministic-market-monitor
content_hash: 0e83e1927d71867b7d7f5e15d65c32a6208d0b0961dd768fbd96fc2e30c55bb2
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition is a durable, security-specific
  market signal warranting wiki review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ed7d5b616a196969c815
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ed7d5b616a196969c815
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-17'
  period_start: '2026-08-19'
  period_end: '2026-09-17'
  latest_close: '3.5399999618530273'
  return_period: '0.011428560529436371428571429'
  strength: '0.06683862'
  previous_strength: '0'
  source_price_hash: 99fbe630ea146c0b1f097d96c1e6349612be92eae2df9d7f0e4efab910eda52f
---

# RXRX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ed7d5b616a196969c815|RXRX — Recursion Pharmaceuticals, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-19 through 2026-09-17
- Latest adjusted close: 3.5399999618530273
- Period return: 0.011428560529436371428571429
- Trigger strength: 0.06683862
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly transition is a durable, security-specific market signal warranting wiki review.
