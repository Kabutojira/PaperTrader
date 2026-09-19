---
title: FISV — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: e596867de9823d28b3c2f33e633e15f18491e6c06e25e95f0287602c7421de00
classifier_decision: ingest
classifier_reason: New Bollinger-band breach with an 8.15% period decline is a material
  market transition for the security.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_d202772e4e62065cd17a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_d202772e4e62065cd17a
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '47.189998626708984'
  return_period: '-0.0815492867711602662103746167'
  strength: '0.01291851648038103476577810327'
  previous_strength: '0'
  source_price_hash: ac1b12e616f31003f7acd4ce2e9e0597e5dca5a82b6d7021e47be7a294f997ba
---

# FISV — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_d202772e4e62065cd17a|FISV — Fiserv, Inc. common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 47.189998626708984
- Period return: -0.0815492867711602662103746167
- Trigger strength: 0.01291851648038103476577810327
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger-band breach with an 8.15% period decline is a material market transition for the security.
