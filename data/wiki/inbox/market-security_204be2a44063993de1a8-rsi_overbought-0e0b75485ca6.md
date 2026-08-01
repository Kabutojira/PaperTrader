---
title: '[MSFT] RSI overbought'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 0e0b75485ca677bbdb243b824534b37d06681709ffe7553ea3cb21ebafcac98a
classifier_decision: ingest
classifier_reason: Material RSI overbought strengthening with a 19.0% period return
  merits durable wiki ingestion.
related_entity_ids:
- security_204be2a44063993de1a8
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_204be2a44063993de1a8
  trigger: rsi_overbought
  transition: strengthened
  as_of_date: '2026-07-31'
  period_start: '2026-07-02'
  period_end: '2026-07-31'
  latest_close: '464.7200012207031'
  return_period: '0.190094529546774539950370347'
  strength: '0.1506381353333333333333333333'
  previous_strength: '0.060914146'
  source_price_hash: b7700aee2b0ab96eb1fad001ae88ee6acb3cf17f755e71cfe44d6cf96dd92a02
---

# [MSFT] RSI overbought

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_204be2a44063993de1a8|MSFT — Microsoft Corporation common stock]] (`security_204be2a44063993de1a8`)
- Trigger: `rsi_overbought`
- Transition: `strengthened`
- Period: 2026-07-02 through 2026-07-31
- Latest adjusted close: 464.7200012207031
- Period return: 0.190094529546774539950370347
- Trigger strength: 0.1506381353333333333333333333
- Previous strength: 0.060914146
- Source price hash: `b7700aee2b0ab96eb1fad001ae88ee6acb3cf17f755e71cfe44d6cf96dd92a02`

## Classifier disposition

- Decision: `ingest`
- Reason: Material RSI overbought strengthening with a 19.0% period return merits durable wiki ingestion.
