---
title: '[SPOT] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 78a51b6daf0eb4d04ad5844324b54907f3598cbd36d61d3b2b45acf2ff85ec1c
classifier_decision: ingest
classifier_reason: Material volume anomaly coincides with a 3.2% decline over the
  review period and warrants durable security context.
related_entity_ids:
- security_2010347f1a0a5ea60f47
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2010347f1a0a5ea60f47
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '478.1700134277344'
  return_period: '-0.0319465500340607660786145644'
  strength: '0.61683892'
  previous_strength: '0'
  source_price_hash: 1e4f582d291a00c189884396774810beba95ef80c554241a65d9920f97151671
---

# [SPOT] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2010347f1a0a5ea60f47|SPOT — Spotify Technology S.A. ordinary shares]] (`security_2010347f1a0a5ea60f47`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 478.1700134277344
- Period return: -0.0319465500340607660786145644
- Trigger strength: 0.61683892
- Previous strength: 0
- Source price hash: `1e4f582d291a00c189884396774810beba95ef80c554241a65d9920f97151671`

## Classifier disposition

- Decision: `ingest`
- Reason: Material volume anomaly coincides with a 3.2% decline over the review period and warrants durable security context.
