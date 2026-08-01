---
title: '[PL] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 45073f63c222860b5d67264fd5d5d5dc2df0dc3a46d6e1f0e4682f11b8f0a015
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover is a durable, security-specific market
  transition despite the recent negative return.
related_entity_ids:
- security_97f38b2cb2d5ef127f5a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_97f38b2cb2d5ef127f5a
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-07-31'
  period_start: '2026-07-02'
  period_end: '2026-07-31'
  latest_close: '20.479999542236328'
  return_period: '-0.3473550003200187994126980591'
  strength: '0.01080185058516329801481619538'
  previous_strength: '0'
  source_price_hash: 472200283b7036f4a8fd8256cfdf5921d250604c64af329e59a6f5e2fdb80f9d
---

# [PL] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_97f38b2cb2d5ef127f5a|PL — Planet Labs PBC Class A common stock]] (`security_97f38b2cb2d5ef127f5a`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-02 through 2026-07-31
- Latest adjusted close: 20.479999542236328
- Period return: -0.3473550003200187994126980591
- Trigger strength: 0.01080185058516329801481619538
- Previous strength: 0
- Source price hash: `472200283b7036f4a8fd8256cfdf5921d250604c64af329e59a6f5e2fdb80f9d`

## Classifier disposition

- Decision: `ingest`
- Reason: A new MACD bullish crossover is a durable, security-specific market transition despite the recent negative return.
