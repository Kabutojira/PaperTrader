---
title: '[META] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 4573b7d5179670375be0d67d7a4e3d74a59cd7ec05273c37bd5881344b9cd1ac
classifier_decision: ingest
classifier_reason: Material new Bollinger-band breach with a 12.05% monthly decline
  warrants durable review.
related_entity_ids:
- security_d12e746b3c9d392183cc
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_d12e746b3c9d392183cc
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '539.030029296875'
  return_period: '-0.1205396340160946639517203922'
  strength: '0.02191114086450073329319034629'
  previous_strength: '0'
  source_price_hash: d65403f874aadc7c48ae543142923e398eaf6aefc4faa6b229af2709c1a4ddc0
---

# [META] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: META — Meta Platforms, Inc. Class A common stock (`security_d12e746b3c9d392183cc`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 539.030029296875
- Period return: -0.1205396340160946639517203922
- Trigger strength: 0.02191114086450073329319034629
- Previous strength: 0
- Source price hash: `d65403f874aadc7c48ae543142923e398eaf6aefc4faa6b229af2709c1a4ddc0`

## Classifier disposition

- Decision: `ingest`
- Reason: Material new Bollinger-band breach with a 12.05% monthly decline warrants durable review.
