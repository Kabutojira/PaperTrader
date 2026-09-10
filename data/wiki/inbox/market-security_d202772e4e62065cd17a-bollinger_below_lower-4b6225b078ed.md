---
title: FISV — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-10'
updated: '2026-09-10'
provenance: deterministic-market-monitor
content_hash: 4b6225b078ed389cc8bca234fdc7508c357001bd2170f46a5438c52604ad3817
classifier_decision: ingest
classifier_reason: 'Material downside transition: price fell 7.72% over the period
  and entered a Bollinger-below-lower condition.'
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
  as_of_date: '2026-09-09'
  period_start: '2026-08-11'
  period_end: '2026-09-09'
  latest_close: '48.650001525878906'
  return_period: '-0.0772002959139904500543840364'
  strength: '0.02120024658544487446919912349'
  previous_strength: '0'
  source_price_hash: a6cd0060d85532b2107d88d9cadda54de74761242de5018e8e8b05e9cee6c5cb
---

# FISV — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_d202772e4e62065cd17a|FISV — Fiserv, Inc. common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-11 through 2026-09-09
- Latest adjusted close: 48.650001525878906
- Period return: -0.0772002959139904500543840364
- Trigger strength: 0.02120024658544487446919912349
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material downside transition: price fell 7.72% over the period and entered a bollinger-below-lower condition.
