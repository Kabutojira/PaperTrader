---
title: '[PWR] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 0f8044b1c3409862cdb288e966a01f4947d46efc430c751d654aab244bbb5fd0
classifier_decision: ingest
classifier_reason: Strengthened volume anomaly is a material market transition for
  the tracked security.
related_entity_ids:
- security_488a9d7f7a8573597724
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_488a9d7f7a8573597724
  trigger: volume_anomaly
  transition: strengthened
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '657.97998046875'
  return_period: '-0.048336769981509367404261585'
  strength: '0.770033745'
  previous_strength: '0.602805435'
  source_price_hash: 4b95b3735e882350250b08937d588648c201a0733c83477977c6fb895e453485
---

# [PWR] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_488a9d7f7a8573597724|PWR — Quanta Services, Inc. common stock]] (`security_488a9d7f7a8573597724`)
- Trigger: `volume_anomaly`
- Transition: `strengthened`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 657.97998046875
- Period return: -0.048336769981509367404261585
- Trigger strength: 0.770033745
- Previous strength: 0.602805435
- Source price hash: `4b95b3735e882350250b08937d588648c201a0733c83477977c6fb895e453485`

## Classifier disposition

- Decision: `ingest`
- Reason: Strengthened volume anomaly is a material market transition for the tracked security.
