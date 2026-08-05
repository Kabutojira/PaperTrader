---
title: '[TX] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: fab436606247cc3c3245f20518a519851c9f291764259783c064c3b3f1d0b474
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a 25.2% one-month return
  and merits durable review.
related_entity_ids:
- security_2c779e81c27b78c556bb
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2c779e81c27b78c556bb
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '53.709999084472656'
  return_period: '0.252273253644196547167429413'
  strength: '0.20739593'
  previous_strength: '0'
  source_price_hash: 7ee4570e35c66ddb262959d2b5b113993b4d641019caf73e86af15b901fbf42b
---

# [TX] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2c779e81c27b78c556bb|TX — Ternium S.A. ADS]] (`security_2c779e81c27b78c556bb`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 53.709999084472656
- Period return: 0.252273253644196547167429413
- Trigger strength: 0.20739593
- Previous strength: 0
- Source price hash: `7ee4570e35c66ddb262959d2b5b113993b4d641019caf73e86af15b901fbf42b`

## Classifier disposition

- Decision: `ingest`
- Reason: Material volume anomaly coincides with a 25.2% one-month return and merits durable review.
