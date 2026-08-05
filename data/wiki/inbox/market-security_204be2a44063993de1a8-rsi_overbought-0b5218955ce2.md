---
title: '[MSFT] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: 0b5218955ce2ee2ba362e01d637b0bf8335217acc865c3e8c0230897ffa86b1e
classifier_decision: ingest
classifier_reason: Material RSI overbought strengthening with a 26.7% period return
  warrants durable wiki ingestion.
related_entity_ids:
- security_204be2a44063993de1a8
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_204be2a44063993de1a8
  trigger: rsi_overbought
  transition: strengthened
  as_of_date: '2026-08-04'
  period_start: '2026-07-07'
  period_end: '2026-08-04'
  latest_close: '492.80999755859375'
  return_period: '0.267385048348668987185256598'
  strength: '0.301055852'
  previous_strength: '0.1506381353333333333333333333'
  source_price_hash: e354fa93eb6033e6c2dc33b6a4c8611ae875396ba3cd688bb5be912712418324
---

# [MSFT] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_204be2a44063993de1a8|MSFT — Microsoft Corporation common stock]] (`security_204be2a44063993de1a8`)
- Trigger: `rsi_overbought`
- Transition: `strengthened`
- Period: 2026-07-07 through 2026-08-04
- Latest adjusted close: 492.80999755859375
- Period return: 0.267385048348668987185256598
- Trigger strength: 0.301055852
- Previous strength: 0.1506381353333333333333333333
- Source price hash: `e354fa93eb6033e6c2dc33b6a4c8611ae875396ba3cd688bb5be912712418324`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought strengthening with a 26.7% period return warrants durable wiki ingestion.
