---
title: LMND — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: bdf6ee56417ef499ac6227f815ff65716b4ef9b37327049b9a178b4558a752e0
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly coincides with an approximately
  9.7% decline over the validated period, warranting durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_8d11e65cd0de084ee461
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_8d11e65cd0de084ee461
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '43.86000061035156'
  return_period: '-0.0969734221549639642868109671'
  strength: '0.010399025'
  previous_strength: '0'
  source_price_hash: 0171ff84232ac409c40a1ee04329dc704c01ac930710ab4afd3873e33bdefbd2
---

# LMND — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: LMND — Lemonade, Inc. common stock
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 43.86000061035156
- Period return: -0.0969734221549639642868109671
- Trigger strength: 0.010399025
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly coincides with an approximately 9.7% decline over the validated period, warranting durable review.
