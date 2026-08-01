---
title: '[ETN] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 4d01b00f7097d4f617e594f262e91a9335e072a5dce214c3787b47a50dc84094
classifier_decision: ingest
classifier_reason: Materially strengthened volume anomaly with a 4.19% period return
  merits durable wiki ingestion.
related_entity_ids:
- security_18a3ab0ee6086ee85d0f
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_18a3ab0ee6086ee85d0f
  trigger: volume_anomaly
  transition: strengthened
  as_of_date: '2026-07-31'
  period_start: '2026-07-02'
  period_end: '2026-07-31'
  latest_close: '415.20001220703125'
  return_period: '0.041854922345657079919226865'
  strength: '0.1564304'
  previous_strength: '0.014594865'
  source_price_hash: c10ce68bccbe348b676b6fb56c4abf35eaab50b8df7757a59ee0342093d038d9
---

# [ETN] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_18a3ab0ee6086ee85d0f|ETN — Eaton Corporation plc ordinary shares]] (`security_18a3ab0ee6086ee85d0f`)
- Trigger: `volume_anomaly`
- Transition: `strengthened`
- Period: 2026-07-02 through 2026-07-31
- Latest adjusted close: 415.20001220703125
- Period return: 0.041854922345657079919226865
- Trigger strength: 0.1564304
- Previous strength: 0.014594865
- Source price hash: `c10ce68bccbe348b676b6fb56c4abf35eaab50b8df7757a59ee0342093d038d9`

## Classifier disposition

- Decision: `ingest`
- Reason: Materially strengthened volume anomaly with a 4.19% period return merits durable wiki ingestion.
