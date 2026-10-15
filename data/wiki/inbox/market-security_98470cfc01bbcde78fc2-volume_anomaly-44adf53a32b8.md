---
title: SOFI — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-10-15'
updated: '2026-10-15'
provenance: deterministic-market-monitor
content_hash: 44adf53a32b89d41c3f278ad5a5e8a0ddeaa4b26c9e9cd2618548b146ece5cb3
classifier_decision: ingest
classifier_reason: Material entered volume-anomaly transition with a substantial decline
  over the validated period, warranting durable review.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_98470cfc01bbcde78fc2
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_98470cfc01bbcde78fc2
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-10-14'
  period_start: '2026-09-16'
  period_end: '2026-10-14'
  latest_close: '14.220000267028809'
  return_period: '-0.1555819395379549360923920063'
  strength: '0.181266815'
  previous_strength: '0'
  source_price_hash: 075cdac1830d46761ca1a02a3902a0111243e72326bfdb45ae0c8e13374b9727
---

# SOFI — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_98470cfc01bbcde78fc2|SOFI — SoFi Technologies, Inc. common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-09-16 through 2026-10-14
- Latest adjusted close: 14.220000267028809
- Period return: -0.1555819395379549360923920063
- Trigger strength: 0.181266815
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: Material entered volume-anomaly transition with a substantial decline over the validated period, warranting durable review.
