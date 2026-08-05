---
title: '[KTOS] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: b87f3649b640f0f1a5e1fbcfcff6e76bd655effc07ce776cbbbb396b274ae18a
classifier_decision: ingest
classifier_reason: New Bollinger-above-upper transition with a positive 3.04% period
  return merits durable review.
related_entity_ids:
- security_0cf8075039299094d614
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_0cf8075039299094d614
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '51.869998931884766'
  return_period: '0.030393301046071242019173548'
  strength: '0.0011737163292323983162767724'
  previous_strength: '0'
  source_price_hash: 7b463eb275bd79a21a8579cb5403f6321989606cf4e0001d7d4ceaac6322b032
---

# [KTOS] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: KTOS — Kratos Defense & Security Solutions, Inc. common stock (`security_0cf8075039299094d614`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 51.869998931884766
- Period return: 0.030393301046071242019173548
- Trigger strength: 0.0011737163292323983162767724
- Previous strength: 0
- Source price hash: `7b463eb275bd79a21a8579cb5403f6321989606cf4e0001d7d4ceaac6322b032`

## Classifier disposition

- Decision: `ingest`
- Reason: New Bollinger-above-upper transition with a positive 3.04% period return merits durable review.
