---
title: TSM — MACD cross above signal
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-05'
updated: '2026-09-05'
provenance: deterministic-market-monitor
content_hash: 79ce1d3d4f49326875c5e270b749ae97c549923298205732363d58c7180c8f30
classifier_decision: ingest
classifier_reason: New MACD bullish crossover with positive 2.1% period return merits
  durable monitoring context.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ce9b78a4d0773c950765
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ce9b78a4d0773c950765
  trigger: macd_cross_above_signal
  transition: entered
  as_of_date: '2026-09-04'
  period_start: '2026-08-07'
  period_end: '2026-09-04'
  latest_close: '428.9100036621094'
  return_period: '0.021117024418493894828056264'
  strength: '13.59450487335497813731361993'
  previous_strength: '0'
  source_price_hash: af14a2becccd2a71141568e6d9bbe942d4fbbef8c1e9a6da361a7b3086e7672a
---

# TSM — MACD cross above signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ce9b78a4d0773c950765|TSM — Taiwan Semiconductor Manufacturing Company Limited sponsored ADR]]
- Alert: MACD cross above signal
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-07 through 2026-09-04
- Latest adjusted close: 428.9100036621094
- Period return: 0.021117024418493894828056264
- Trigger strength: 13.59450487335497813731361993
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New macd bullish crossover with positive 2.1% period return merits durable monitoring context.
