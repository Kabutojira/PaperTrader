---
title: '[SGML] RSI oversold'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-27'
updated: '2026-07-27'
provenance: deterministic-market-monitor
content_hash: e0b5f3290c6e511ee50fc76f63e53b17fc60c3aec032fcdac7a978ad7b1c1b39
classifier_decision: blocked
classifier_reason: classifier.command is not configured
related_entity_ids: []
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_4627aea1bf7d8943d3d8
  trigger: rsi_oversold
  transition: entered
  as_of_date: '2026-07-24'
  period_start: '2026-06-25'
  period_end: '2026-07-24'
  latest_close: '9.630000114440918'
  return_period: '-0.2074073731036204934670989592'
  strength: '0.02920823666666666666666666667'
  previous_strength: '0'
  source_price_hash: 301592c165694b81b3e31cbfef1c19bd3defd70841d3e62a522974a8dfeeda17
---

# [SGML] RSI oversold

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_4627aea1bf7d8943d3d8|SGML — Sigma Lithium Corporation common shares]] (`security_4627aea1bf7d8943d3d8`)
- Trigger: `rsi_oversold`
- Transition: `entered`
- Period: 2026-06-25 through 2026-07-24
- Latest adjusted close: 9.630000114440918
- Period return: -0.2074073731036204934670989592
- Trigger strength: 0.02920823666666666666666666667
- Previous strength: 0
- Source price hash: `301592c165694b81b3e31cbfef1c19bd3defd70841d3e62a522974a8dfeeda17`

## Classifier disposition

- Decision: `blocked`
- Reason: classifier.command is not configured
