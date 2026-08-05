---
title: '[TSM] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 02538665a30b4d33ece2fcb154fe989a18e671066558dc5b4265628d96466498
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a durable, security-specific market
  transition despite the recent negative return.
related_entity_ids:
- security_ce9b78a4d0773c950765
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ce9b78a4d0773c950765
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '417.1700134277344'
  return_period: '-0.0356011596637160895791823798'
  strength: '0.04952257779117493800268232252'
  previous_strength: '0'
  source_price_hash: 23680e1081b20c6eee063ca3d67dfdaada83b2d952b928c7caea00b524a36f15
---

# [TSM] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: TSM — Taiwan Semiconductor Manufacturing Company Limited sponsored ADR (`security_ce9b78a4d0773c950765`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 417.1700134277344
- Period return: -0.0356011596637160895791823798
- Trigger strength: 0.04952257779117493800268232252
- Previous strength: 0
- Source price hash: `23680e1081b20c6eee063ca3d67dfdaada83b2d952b928c7caea00b524a36f15`

## Classifier disposition

- Decision: `ingest`
- Reason: A new MACD bullish crossover is a durable, security-specific market transition despite the recent negative return.
