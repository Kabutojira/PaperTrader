---
title: VRT — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-06'
updated: '2026-08-06'
provenance: deterministic-market-monitor
content_hash: d2200e5084d73fc49be4a6282e4d60e9f97e4bee4f65eaacdce74641c67c886a
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a durable indicator transition
  for the tracked security despite the negative period return.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_cb88f9154cfeaa15e878
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_cb88f9154cfeaa15e878
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-08-06'
  period_start: '2026-07-09'
  period_end: '2026-08-06'
  latest_close: '275.1700134277344'
  return_period: '-0.1505001172484699877089596156'
  strength: '0.02610268854179093999767945267'
  previous_strength: '0'
  source_price_hash: ba00dabb473fac6775cfe02de0ba9a568cfded86c113f6b161a1789f8f049441
---

# VRT — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_cb88f9154cfeaa15e878|VRT — Vertiv Holdings Co Class A common stock]]
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-07-09 through 2026-08-06
- Latest adjusted close: 275.1700134277344
- Period return: -0.1505001172484699877089596156
- Trigger strength: 0.02610268854179093999767945267
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new macd bullish crossover is a durable indicator transition for the tracked security despite the negative period return.
