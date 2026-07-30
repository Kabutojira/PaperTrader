---
title: '[FCX] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-30'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: 97d02f6c8190322558f45b18ff88cb9c35c3b37f85731b4b04fa217fe4f6179f
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition coincides with a material one-month
  decline and merits durable review.
related_entity_ids:
- security_2dbe878dfc899d7ee867
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2dbe878dfc899d7ee867
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-29'
  period_start: '2026-06-30'
  period_end: '2026-07-29'
  latest_close: '59.9900016784668'
  return_period: '-0.0437969763201708427459937719'
  strength: '0.00020024'
  previous_strength: '0'
  source_price_hash: a7eb845fdc9ec53269f4648c73619c7f149dcee990fcc7f2ecb943a1fab9b1de
---

# [FCX] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2dbe878dfc899d7ee867|FCX — Freeport-McMoRan Inc. common stock]] (`security_2dbe878dfc899d7ee867`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-06-30 through 2026-07-29
- Latest adjusted close: 59.9900016784668
- Period return: -0.0437969763201708427459937719
- Trigger strength: 0.00020024
- Previous strength: 0
- Source price hash: `a7eb845fdc9ec53269f4648c73619c7f149dcee990fcc7f2ecb943a1fab9b1de`

## Classifier disposition

- Decision: `ingest`
- Reason: A new volume-anomaly transition coincides with a material one-month decline and merits durable review.
