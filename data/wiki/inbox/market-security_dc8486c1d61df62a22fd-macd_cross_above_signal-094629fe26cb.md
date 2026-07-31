---
title: '[SU] MACD cross above signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: 094629fe26cbfebc154af85924a3e68b697a5a4de8c4e791e0b0041decd0ad13
classifier_decision: ingest
classifier_reason: A new MACD bullish crossover with a positive 2.7% period return
  is a material indicator transition for the security.
related_entity_ids:
- security_dc8486c1d61df62a22fd
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_dc8486c1d61df62a22fd
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-02'
  period_end: '2026-07-30'
  latest_close: '283.45001220703125'
  return_period: '0.027365054286226479633309835'
  strength: '0.2767094858885180534637187821'
  previous_strength: '0'
  source_price_hash: 27b9aa3eb7e69d21b7f3b8ba0bce0a3bb59b0a0f9b8bea611a4ae7f2245979ca
---

# [SU] MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: SU — Schneider Electric SE ordinary shares (`security_dc8486c1d61df62a22fd`)
- Trigger: `macd_cross_above_signal`
- Transition: `entered`
- Period: 2026-07-02 through 2026-07-30
- Latest adjusted close: 283.45001220703125
- Period return: 0.027365054286226479633309835
- Trigger strength: 0.2767094858885180534637187821
- Previous strength: 0
- Source price hash: `27b9aa3eb7e69d21b7f3b8ba0bce0a3bb59b0a0f9b8bea611a4ae7f2245979ca`

## Classifier disposition

- Decision: `ingest`
- Reason: A new MACD bullish crossover with a positive 2.7% period return is a material indicator transition for the security.
