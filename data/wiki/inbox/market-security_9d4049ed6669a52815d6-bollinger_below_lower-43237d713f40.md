---
title: SQM — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-14'
updated: '2026-09-14'
provenance: deterministic-market-monitor
content_hash: 43237d713f40d6e96a9416daa103e1fbdc5943bcb5ad50b890bcdf993e625056
classifier_decision: ingest
classifier_reason: New downside Bollinger-band transition with a material negative
  period return merits durable monitoring context.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_9d4049ed6669a52815d6
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_9d4049ed6669a52815d6
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-09-11'
  period_start: '2026-08-13'
  period_end: '2026-09-11'
  latest_close: '69.87999725341797'
  return_period: '-0.0315965395368822919407220445'
  strength: '0.01456944518323851957927671439'
  previous_strength: '0'
  source_price_hash: 269aac5ec10a4fc3691dfb835d7d705db4ff7db4dda0d73c7b7828f677c400a3
---

# SQM — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_9d4049ed6669a52815d6|SQM — Sociedad Quimica y Minera de Chile S.A. American depositary shares]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-08-13 through 2026-09-11
- Latest adjusted close: 69.87999725341797
- Period return: -0.0315965395368822919407220445
- Trigger strength: 0.01456944518323851957927671439
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New downside bollinger-band transition with a material negative period return merits durable monitoring context.
