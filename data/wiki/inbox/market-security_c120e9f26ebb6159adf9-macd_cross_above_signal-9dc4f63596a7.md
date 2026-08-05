---
title: '[ABBNY] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 9dc4f63596a7efd91e964319a8a23f8ef690d6915c642be1ce4439678906145b
classifier_decision: ignore
classifier_reason: A weak MACD crossover with a modest negative period return does
  not provide sufficient evidence of a material, durable market transition.
related_entity_ids:
- security_c120e9f26ebb6159adf9
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c120e9f26ebb6159adf9
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '101.56999969482422'
  return_period: '-0.0135003826923893692244102316'
  strength: '0.2090271211012819997995761484'
  previous_strength: '0'
  source_price_hash: 0112eb6e81e4e59adf877317fa5f70e1af46185267e063e8dc6d97ac3f9326e6
---

# [ABBNY] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c120e9f26ebb6159adf9|ABBNY — ABB Ltd sponsored ADR]] (`security_c120e9f26ebb6159adf9`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 101.56999969482422
- Period return: -0.0135003826923893692244102316
- Trigger strength: 0.2090271211012819997995761484
- Previous strength: 0
- Source price hash: `0112eb6e81e4e59adf877317fa5f70e1af46185267e063e8dc6d97ac3f9326e6`

## Classifier disposition

- Decision: `ignore`
- Reason: A weak MACD crossover with a modest negative period return does not provide sufficient evidence of a material, durable market transition.
