---
title: MSTR — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: 1042437afdf488a76f2ad191a797acce32c9695fd4ecd9c8bef30c9f2a17bf9c
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover coincides with a material positive
  period return for the tracked security.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_fe5539a7d3fd9d553bce
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fe5539a7d3fd9d553bce
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '153.9199981689453'
  return_period: '0.369516852076092598193187615'
  strength: '0.02722400631462923439640721445'
  previous_strength: '0'
  source_price_hash: c60162faee1ec0125d656b10b021336107258ebb68cbabe441d7e832be4d43bc
---

# MSTR — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_fe5539a7d3fd9d553bce|MSTR — Strategy Inc Class A common stock]]
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 153.9199981689453
- Period return: 0.369516852076092598193187615
- Trigger strength: 0.02722400631462923439640721445
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new macd bullish crossover coincides with a material positive period return for the tracked security.
