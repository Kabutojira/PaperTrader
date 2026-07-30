---
title: '[ASML] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-30'
provenance: deterministic-market-monitor
content_hash: f5f33a74b0ad7723c95f12ebbdade0a8acc879a5243f21926432bd47f7af2ad5
classifier_decision: ingest
classifier_reason: Material 15.4% decline with a new Bollinger lower-band breach warrants
  durable review.
related_entity_ids:
- security_ef35e41886220d51c22c
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ef35e41886220d51c22c
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '1590.18'
  return_period: '-0.1544576919057611809125953582'
  strength: '0.02181422065465641499032014172'
  previous_strength: '0'
  source_price_hash: 03461855cc0d161211343f15bfd344f9a6dc5276a1edc50de8d288d2d7b11ef3
---

# [ASML] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ef35e41886220d51c22c|ASML — ASML Holding N.V. New York registered shares]] (`security_ef35e41886220d51c22c`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 1590.18
- Period return: -0.1544576919057611809125953582
- Trigger strength: 0.02181422065465641499032014172
- Previous strength: 0
- Source price hash: `03461855cc0d161211343f15bfd344f9a6dc5276a1edc50de8d288d2d7b11ef3`

## Classifier disposition

- Decision: `ingest`
- Reason: Material 15.4% decline with a new Bollinger lower-band breach warrants durable review.
