---
title: '[FUC.F] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 3076adb7c502172d837d8815655fb0c01fe2e8a3f305388ae68421d9742fa406
classifier_decision: ingest
classifier_reason: New MACD bullish crossover is a validated market-state transition
  for the security and merits durable tracking despite the recent negative return.
related_entity_ids:
- security_96ba305ee7cd586bc348
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_96ba305ee7cd586bc348
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '35.959999084472656'
  return_period: '-0.0299433671294727385908606417'
  strength: '0.001360479525198566647056572561'
  previous_strength: '0'
  source_price_hash: 20c79ccb05957caa272b377ce01b842f64ca1c74fd7696606987e23ab44fb46f
---

# [FUC.F] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: FUC.F — Fanuc Corporation Frankfurt ordinary shares (`security_96ba305ee7cd586bc348`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 35.959999084472656
- Period return: -0.0299433671294727385908606417
- Trigger strength: 0.001360479525198566647056572561
- Previous strength: 0
- Source price hash: `20c79ccb05957caa272b377ce01b842f64ca1c74fd7696606987e23ab44fb46f`

## Classifier disposition

- Decision: `ingest`
- Reason: New MACD bullish crossover is a validated market-state transition for the security and merits durable tracking despite the recent negative return.
