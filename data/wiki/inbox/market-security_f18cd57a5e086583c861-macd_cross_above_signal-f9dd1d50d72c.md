---
title: PRLB — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-17'
updated: '2026-09-17'
provenance: deterministic-market-monitor
content_hash: f9dd1d50d72cbb0f23b98d1aafb5a7930c2387135462109bd2a9a30206fac21a
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a validated market-state transition
  for the security and merits durable monitoring context despite the negative period
  return.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_f18cd57a5e086583c861
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_f18cd57a5e086583c861
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-09-16'
  period_start: '2026-08-18'
  period_end: '2026-09-16'
  latest_close: '83.23999786376953'
  return_period: '-0.0193213883449130304287178521'
  strength: '0.2713279122749633882183504354'
  previous_strength: '0'
  source_price_hash: 68fea177a4920f10d49310768efb6c1aa0103e211d451c8554c80671968548ae
---

# PRLB — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PRLB — Proto Labs, Inc. common stock
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-18 through 2026-09-16
- Latest adjusted close: 83.23999786376953
- Period return: -0.0193213883449130304287178521
- Trigger strength: 0.2713279122749633882183504354
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A new macd bullish crossover is a validated market-state transition for the security and merits durable monitoring context despite the negative period return.
