---
title: PRLB — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-14'
updated: '2026-09-14'
provenance: deterministic-market-monitor
content_hash: 3882d9f8f534243cddfc14b367c49c821ce9b0d7b7da303f619233584dc8696a
classifier_decision: ingest
classifier_reason: A newly entered MACD bullish crossover after a material negative-period
  return is a decision-relevant market transition for the security.
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
  as_of_date: '2026-09-11'
  period_start: '2026-08-13'
  period_end: '2026-09-11'
  latest_close: '81.9800033569336'
  return_period: '-0.1120016938049266060251261356'
  strength: '0.04174332095566068992678505088'
  previous_strength: '0'
  source_price_hash: 57549a515f517d4dce7c5d436fbe9a17092af2e5a8ef7a96065406597eeeeea0
---

# PRLB — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: PRLB — Proto Labs, Inc. common stock
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-13 through 2026-09-11
- Latest adjusted close: 81.9800033569336
- Period return: -0.1120016938049266060251261356
- Trigger strength: 0.04174332095566068992678505088
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered macd bullish crossover after a material negative-period return is a decision-relevant market transition for the security.
