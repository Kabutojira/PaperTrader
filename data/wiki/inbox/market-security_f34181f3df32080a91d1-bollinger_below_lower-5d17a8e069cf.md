---
title: DPZ — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-10'
updated: '2026-09-10'
provenance: deterministic-market-monitor
content_hash: 5d17a8e069cf4f802f49ed6029034f9ecedf6d890376b1b478e9ef421870aa64
classifier_decision: ingest
classifier_reason: 'Material bearish transition: price entered below the lower Bollinger
  Band after a roughly 10% period decline.'
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_f34181f3df32080a91d1
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_f34181f3df32080a91d1
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-09'
  period_start: '2026-08-11'
  period_end: '2026-09-09'
  latest_close: '321.4599914550781'
  return_period: '-0.1004085891602388151464954139'
  strength: '0.01479279543796265454224239419'
  previous_strength: '0'
  source_price_hash: 88c1b63752b6ad586f528429147c70739d6b4b4a670483820d1bb977cfd02db5
---

# DPZ — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_f34181f3df32080a91d1|DPZ — Domino's Pizza, Inc. common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-11 through 2026-09-09
- Latest adjusted close: 321.4599914550781
- Period return: -0.1004085891602388151464954139
- Trigger strength: 0.01479279543796265454224239419
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material bearish transition: price entered below the lower bollinger band after a roughly 10% period decline.
