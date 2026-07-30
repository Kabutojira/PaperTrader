---
title: '[SQM] MACD cross below signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: 9e986cb6222e03927cc213206fba55ac87eb62d1388ceb1923337ea2cdd8b491
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_9d4049ed6669a52815d6
  trigger: macd_cross_below_signal
  transition: entered
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '66.87'
  return_period: '-0.0427998938481044663895653578'
  strength: '0.003185175805893855836221952748'
  previous_strength: '0'
  source_price_hash: b1c6696baeeb3715701a889baed72a5e63f73b06e30fb81a728bfdf8d9414284
---

# [SQM] MACD cross below signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_9d4049ed6669a52815d6|SQM — Sociedad Quimica y Minera de Chile S.A. American depositary shares]] (`security_9d4049ed6669a52815d6`)
- Trigger: `macd_cross_below_signal`
- Transition: `entered`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 66.87
- Period return: -0.0427998938481044663895653578
- Trigger strength: 0.003185175805893855836221952748
- Previous strength: 0
- Source price hash: `b1c6696baeeb3715701a889baed72a5e63f73b06e30fb81a728bfdf8d9414284`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
