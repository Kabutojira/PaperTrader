---
title: RXRX — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-05'
updated: '2026-09-05'
provenance: deterministic-market-monitor
content_hash: 95a27682c8f296632af3d32b16d115f75cd9d24a9e463e4f1c2e00a507e9d535
classifier_decision: ingest
classifier_reason: New volume-anomaly transition coincides with a material 12.7% price
  increase over the validated period.
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
  as_of_date: '2026-09-04'
  period_start: '2026-08-07'
  period_end: '2026-09-04'
  latest_close: '3.630000114440918'
  return_period: '0.127329218070736133211395029'
  strength: '0.095567765'
  previous_strength: '0'
  source_price_hash: afc62f4cd2e844921dd54249d320bf1eaaa1553dc508645938f596424dfbdcff
---

# RXRX — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ed7d5b616a196969c815|RXRX — Recursion Pharmaceuticals, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-07 through 2026-09-04
- Latest adjusted close: 3.630000114440918
- Period return: 0.127329218070736133211395029
- Trigger strength: 0.095567765
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New volume-anomaly transition coincides with a material 12.7% price increase over the validated period.
