---
title: '[MSFT] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: de9b04e0f3e9ed74b635f90003a527f0067f278a7e26acb44bce2ce15bf04df8
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a 17.4% period return and
  warrants durable review.
related_entity_ids:
- security_204be2a44063993de1a8
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_204be2a44063993de1a8
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '451.1000061035156'
  return_period: '0.173883646134274502642375095'
  strength: '1.07043305'
  previous_strength: '0'
  source_price_hash: 614ab5c4bb9a35aa3ad370da5372ab26fb3d2e33257877b7f1eee33ea7901c2c
---

# [MSFT] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: MSFT — Microsoft Corporation common stock (`security_204be2a44063993de1a8`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 451.1000061035156
- Period return: 0.173883646134274502642375095
- Trigger strength: 1.07043305
- Previous strength: 0
- Source price hash: `614ab5c4bb9a35aa3ad370da5372ab26fb3d2e33257877b7f1eee33ea7901c2c`

## Classifier disposition

- Decision: `ingest`
- Reason: Material volume anomaly coincides with a 17.4% period return and warrants durable review.
