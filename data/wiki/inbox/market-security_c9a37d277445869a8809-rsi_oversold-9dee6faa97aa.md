---
title: '[RBLX] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 9dee6faa97aa99493cc1cf18c3da1cb02e32bfc7693e9787d3082739a5a39ee7
classifier_decision: ingest
classifier_reason: Material RSI oversold transition strengthened during a 34.34% period
  decline, warranting durable review.
related_entity_ids:
- security_c9a37d277445869a8809
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c9a37d277445869a8809
  trigger: rsi_oversold
  transition: strengthened
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '36.189998626708984'
  return_period: '-0.3434325230769465121470087777'
  strength: '0.03100286333333333333333333333'
  previous_strength: '0.002335562666666666666666666667'
  source_price_hash: c062a7a5e5ce41f0e88f9b737fe1059fe91b8fbde535c3feeeb67858444647d7
---

# [RBLX] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c9a37d277445869a8809|RBLX — Roblox Corporation Class A common stock]] (`security_c9a37d277445869a8809`)
- Trigger: `rsi_oversold`
- Transition: `strengthened`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 36.189998626708984
- Period return: -0.3434325230769465121470087777
- Trigger strength: 0.03100286333333333333333333333
- Previous strength: 0.002335562666666666666666666667
- Source price hash: `c062a7a5e5ce41f0e88f9b737fe1059fe91b8fbde535c3feeeb67858444647d7`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI oversold transition strengthened during a 34.34% period decline, warranting durable review.
