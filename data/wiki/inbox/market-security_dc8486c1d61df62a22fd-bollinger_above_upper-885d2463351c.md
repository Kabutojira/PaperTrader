---
title: '[SU] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 885d2463351cfaf5ca53e6452ecca7fe32ea72194891957f5641bee7e5949e79
classifier_decision: ingest
classifier_reason: A new Bollinger-band breakout is a material, validated price transition
  for the tracked security and merits durable review.
related_entity_ids:
- security_dc8486c1d61df62a22fd
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_dc8486c1d61df62a22fd
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-02'
  period_end: '2026-07-30'
  latest_close: '283.45001220703125'
  return_period: '0.027365054286226479633309835'
  strength: '0.0086133900511457313153877592'
  previous_strength: '0'
  source_price_hash: 27b9aa3eb7e69d21b7f3b8ba0bce0a3bb59b0a0f9b8bea611a4ae7f2245979ca
---

# [SU] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: SU — Schneider Electric SE ordinary shares (`security_dc8486c1d61df62a22fd`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-02 through 2026-07-30
- Latest adjusted close: 283.45001220703125
- Period return: 0.027365054286226479633309835
- Trigger strength: 0.0086133900511457313153877592
- Previous strength: 0
- Source price hash: `27b9aa3eb7e69d21b7f3b8ba0bce0a3bb59b0a0f9b8bea611a4ae7f2245979ca`

## Classifier disposition

- Decision: `ingest`
- Reason: A new Bollinger-band breakout is a material, validated price transition for the tracked security and merits durable review.
