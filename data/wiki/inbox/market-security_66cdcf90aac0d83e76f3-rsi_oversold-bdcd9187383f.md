---
title: '[ALB] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-29'
updated: '2026-07-29'
provenance: deterministic-market-monitor
content_hash: bdcd9187383ffc3e298e115845009aa20fabf2c430f2a2561a321200efde8ca1
classifier_decision: blocked
classifier_reason: 'classifier exited 2: Hermes classifier invocation failed: [Errno
  2] No such file or directory: ''hermes'''
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_66cdcf90aac0d83e76f3
  trigger: rsi_oversold
  transition: strengthened
  as_of_date: '2026-07-28'
  period_start: '2026-06-29'
  period_end: '2026-07-28'
  latest_close: '113.7094'
  return_period: '-0.1234243067378868615573888829'
  strength: '0.141476086'
  previous_strength: '0.073143163'
  source_price_hash: 96016d92b17159d477177686b7f12c3a4f1ac59d0da19cdd7bb5080fc6c89aa9
---

# [ALB] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_66cdcf90aac0d83e76f3|ALB — Albemarle Corporation common stock]] (`security_66cdcf90aac0d83e76f3`)
- Trigger: `rsi_oversold`
- Transition: `strengthened`
- Period: 2026-06-29 through 2026-07-28
- Latest adjusted close: 113.7094
- Period return: -0.1234243067378868615573888829
- Trigger strength: 0.141476086
- Previous strength: 0.073143163
- Source price hash: `96016d92b17159d477177686b7f12c3a4f1ac59d0da19cdd7bb5080fc6c89aa9`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier exited 2: Hermes classifier invocation failed: [Errno 2] No such file or directory: 'hermes'
