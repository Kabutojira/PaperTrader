---
title: FUC.F — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-21'
updated: '2026-09-21'
provenance: deterministic-market-monitor
content_hash: c911620244a049ca7ffa8adc4ca27f9f234a7c2847f95369aaa33bb19cfa061e
classifier_decision: ingest
classifier_reason: A newly entered volume anomaly with a measurable 2.7% period return
  merits durable monitoring context for the security.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_96ba305ee7cd586bc348
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_96ba305ee7cd586bc348
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-21'
  period_start: '2026-08-24'
  period_end: '2026-09-21'
  latest_close: '33.150001525878906'
  return_period: '0.027269942845740529353689849'
  strength: '0.266715665'
  previous_strength: '0'
  source_price_hash: 468d32937bdf3c1101e155e2325adcd7bef884a7d89f29ee466296d8a3d81996
---

# FUC.F — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_96ba305ee7cd586bc348|FUC.F — Fanuc Corporation Frankfurt ordinary shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-24 through 2026-09-21
- Latest adjusted close: 33.150001525878906
- Period return: 0.027269942845740529353689849
- Trigger strength: 0.266715665
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume anomaly with a measurable 2.7% period return merits durable monitoring context for the security.
