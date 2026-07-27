---
title: '[TX] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-27'
updated: '2026-07-27'
provenance: deterministic-market-monitor
content_hash: 9327af26235b643c494c5fd7a9173540374c046dc880e1db7cb50d502b55dd41
classifier_decision: blocked
classifier_reason: classifier.command is not configured
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2c779e81c27b78c556bb
  trigger: bollinger_above_upper
  transition: strengthened
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '47.29999923706055'
  return_period: '0.042539130496197428346979332'
  strength: '0.0009664226650468261686498285667'
  previous_strength: '0'
  source_price_hash: b137b98d7c2dcea315f3255e61529f2fcb74362230e0d49dae85af433f2108fe
---

# [TX] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_2c779e81c27b78c556bb|TX — Ternium S.A. ADS]] (`security_2c779e81c27b78c556bb`)
- Trigger: `bollinger_above_upper`
- Transition: `strengthened`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 47.29999923706055
- Period return: 0.042539130496197428346979332
- Trigger strength: 0.0009664226650468261686498285667
- Previous strength: 0
- Source price hash: `b137b98d7c2dcea315f3255e61529f2fcb74362230e0d49dae85af433f2108fe`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier.command is not configured
