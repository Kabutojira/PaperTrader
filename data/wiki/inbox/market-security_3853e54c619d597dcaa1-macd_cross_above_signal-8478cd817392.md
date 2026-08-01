---
title: '[NIB.F] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 8478cd817392416f42b6e358bced7434a00c274bfbaadd6daa81e5871b028bec
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a material indicator transition
  for the security despite the recent negative return.
related_entity_ids:
- security_3853e54c619d597dcaa1
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_3853e54c619d597dcaa1
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-07-31'
  period_start: '2026-07-03'
  period_end: '2026-07-31'
  latest_close: '13.807999610900879'
  return_period: '-0.0615740215326623374173458845'
  strength: '0.03337384995987465728525130122'
  previous_strength: '0'
  source_price_hash: 4afb7dab31d30f3eb990a2d987f393d748c38cc35b11ad114e51e6d8de6e8a78
---

# [NIB.F] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: NIB.F — Nidec Corporation Frankfurt ordinary shares (`security_3853e54c619d597dcaa1`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-03 through 2026-07-31
- Latest adjusted close: 13.807999610900879
- Period return: -0.0615740215326623374173458845
- Trigger strength: 0.03337384995987465728525130122
- Previous strength: 0
- Source price hash: `4afb7dab31d30f3eb990a2d987f393d748c38cc35b11ad114e51e6d8de6e8a78`

## Classifier disposition

- Decision: `ingest`
- Reason: A new MACD bullish crossover is a material indicator transition for the security despite the recent negative return.
