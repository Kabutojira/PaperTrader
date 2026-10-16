---
title: TDY — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-24'
updated: '2026-09-24'
provenance: deterministic-market-monitor
content_hash: 7c3c0efa78c42aed85c090bff667a8ffd1113a167358575d29328b296625073f
classifier_decision: ingest
classifier_reason: New volume anomaly transition with a validated security and dated
  price context merits durable monitoring evidence.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_ad5917642acbba28c1f2
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_ad5917642acbba28c1f2
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-23'
  period_start: '2026-08-25'
  period_end: '2026-09-23'
  latest_close: '621.0499877929688'
  return_period: '-0.0093316898919592275436100994'
  strength: '0.412252965'
  previous_strength: '0'
  source_price_hash: 1ce914804b5b1642ffae6b75f0baef3cd211b5bc3507227e769f49242de63ac7
---

# TDY — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_ad5917642acbba28c1f2|TDY — Teledyne Technologies Incorporated common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-25 through 2026-09-23
- Latest adjusted close: 621.0499877929688
- Period return: -0.0093316898919592275436100994
- Trigger strength: 0.412252965
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: New volume anomaly transition with a validated security and dated price context merits durable monitoring evidence.
