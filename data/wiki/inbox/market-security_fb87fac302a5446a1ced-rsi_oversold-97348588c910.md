---
title: '[LAC] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-26'
updated: '2026-07-26'
provenance: deterministic-market-monitor
content_hash: 97348588c9107e9f7287470be7711e96c4c411be63fd2196422a2c2e2f4fc42e
classifier_decision: blocked
classifier_reason: classifier.command is not configured
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_fb87fac302a5446a1ced
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '2.8315'
  return_period: '-0.2645454363276849880708190354'
  strength: '0.18793564'
  previous_strength: '0'
  source_price_hash: 3b5f09f994d20b608998f76606b4fd2682f1ff3f08e15dceb5ed38ad24a293b9
---

# [LAC] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_fb87fac302a5446a1ced|LAC — Lithium Americas Corp. common shares]] (`security_fb87fac302a5446a1ced`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 2.8315
- Period return: -0.2645454363276849880708190354
- Trigger strength: 0.18793564
- Previous strength: 0
- Source price hash: `3b5f09f994d20b608998f76606b4fd2682f1ff3f08e15dceb5ed38ad24a293b9`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier.command is not configured
