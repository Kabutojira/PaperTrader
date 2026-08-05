---
title: '[NIB.F] Bollinger above upper'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 7c97de19e971cb8062cb966b251c82883cce5f756d6a58681126a1372f381d9f
classifier_decision: ingest
classifier_reason: New Bollinger-above-upper transition with an 8.36% period return
  is a material market-state change for the security.
related_entity_ids:
- security_3853e54c619d597dcaa1
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_3853e54c619d597dcaa1
  trigger: bollinger_above_upper
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '15.447999954223633'
  return_period: '0.083613946791580872235884267'
  strength: '0.04263596881861282312185923673'
  previous_strength: '0'
  source_price_hash: 59a44014342dd26c542299f8128daea26aee036dcbfd3a2eac68e2ffc2d90807
---

# [NIB.F] Bollinger above upper

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_3853e54c619d597dcaa1|NIB.F — Nidec Corporation Frankfurt ordinary shares]] (`security_3853e54c619d597dcaa1`)
- Trigger: `bollinger_above_upper`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 15.447999954223633
- Period return: 0.083613946791580872235884267
- Trigger strength: 0.04263596881861282312185923673
- Previous strength: 0
- Source price hash: `59a44014342dd26c542299f8128daea26aee036dcbfd3a2eac68e2ffc2d90807`

## Classifier disposition

- Decision: `ingest`
- Reason: New Bollinger-above-upper transition with an 8.36% period return is a material market-state change for the security.
