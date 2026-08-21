---
title: HOOD — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-21'
updated: '2026-08-21'
provenance: deterministic-market-monitor
content_hash: d8fb77d9bd9b3168b03dd48d9396081627272fbc682426a1d08211d4c16a0840
classifier_decision: ingest
classifier_reason: A new volume-anomaly transition coincides with a material 13.9%
  price increase over the validated period.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ad3b1f8f59fd599f079a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ad3b1f8f59fd599f079a
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-21'
  period_start: '2026-07-24'
  period_end: '2026-08-21'
  latest_close: '108.12999725341797'
  return_period: '0.139289780647078050302318011'
  strength: '0.732882585'
  previous_strength: '0'
  source_price_hash: ecd5df7f2bd95e02a6fde1d8202e8b64622432f0de8f136c8440e522cb5dd9e9
---

# HOOD — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ad3b1f8f59fd599f079a|HOOD — Robinhood Markets, Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-07-24 through 2026-08-21
- Latest adjusted close: 108.12999725341797
- Period return: 0.139289780647078050302318011
- Trigger strength: 0.732882585
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new volume-anomaly transition coincides with a material 13.9% price increase over the validated period.
