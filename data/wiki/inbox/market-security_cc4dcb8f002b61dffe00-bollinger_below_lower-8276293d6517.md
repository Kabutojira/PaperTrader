---
title: '[PARRO.PA] Bollinger below lower'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-27'
updated: '2026-07-27'
provenance: deterministic-market-monitor
content_hash: 8276293d6517ddda4f13e161b6af638f2a3379b4a132350bc8c88b79f8937e5d
classifier_decision: ignore
classifier_reason: Minor one-month decline with weak trigger strength; insufficient
  evidence of a material transition for durable wiki ingestion.
related_entity_ids:
- security_cc4dcb8f002b61dffe00
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cc4dcb8f002b61dffe00
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-07-27'
  period_start: '2026-06-29'
  period_end: '2026-07-27'
  latest_close: '9.649999618530273'
  return_period: '-0.0061792398950546552587875625'
  strength: '0.01671748883642404546414836886'
  previous_strength: '0'
  source_price_hash: c2263e45b4275cf5d39d3d86066a789ecda89ef443e08d9871645866c623a134
---

# [PARRO.PA] Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_cc4dcb8f002b61dffe00|PARRO.PA — Parrot S.A. ordinary shares]] (`security_cc4dcb8f002b61dffe00`)
- Trigger: `bollinger_below_lower`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-27
- Latest adjusted close: 9.649999618530273
- Period return: -0.0061792398950546552587875625
- Trigger strength: 0.01671748883642404546414836886
- Previous strength: 0
- Source price hash: `c2263e45b4275cf5d39d3d86066a789ecda89ef443e08d9871645866c623a134`

## Classifier disposition

- Decision: `ignore`
- Reason: Minor one-month decline with weak trigger strength; insufficient evidence of a material transition for durable wiki ingestion.
