---
title: ANET — Bollinger below lower
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 76a7a2c93402bc188852da27a3144c9d9794cb62094362bde7aa3d4cf1292ad0
classifier_decision: ingest
classifier_reason: New Bollinger lower-band breach is a durable indicator transition
  for the security.
alert_direction: bullish
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_6f9a1450edceb9307c9a
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_6f9a1450edceb9307c9a
  trigger: bollinger_below_lower
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '195.4199981689453'
  return_period: '-0.010731979291488223935415743'
  strength: '0.0005148055173002846668884657074'
  previous_strength: '0'
  source_price_hash: 0ef05509ec172764be9691586b52cd9116c1030913691589dac6d88617a20289
---

# ANET — Bollinger below lower

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_6f9a1450edceb9307c9a|ANET — Arista Networks, Inc. common stock]]
- Alert: Bollinger below lower
- Direction: Bullish
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 195.4199981689453
- Period return: -0.010731979291488223935415743
- Trigger strength: 0.0005148055173002846668884657074
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New bollinger lower-band breach is a durable indicator transition for the security.
