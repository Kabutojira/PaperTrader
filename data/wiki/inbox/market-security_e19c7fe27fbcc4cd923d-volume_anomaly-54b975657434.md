---
title: AD — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-18'
updated: '2026-09-18'
provenance: deterministic-market-monitor
content_hash: 54b975657434eabb21fee2e7088c1e364e56f1d2f7aa61e57103003337c476fe
classifier_decision: ingest
classifier_reason: A newly entered volume-anomaly trigger is a validated market transition
  for the tracked security and merits durable monitoring context.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_e19c7fe27fbcc4cd923d
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_e19c7fe27fbcc4cd923d
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-21'
  period_end: '2026-09-18'
  latest_close: '31.600000381469727'
  return_period: '0.018041219375810352523937181'
  strength: '0.376830255'
  previous_strength: '0'
  source_price_hash: e35329bc985874f3e541303467a25dfb607683e8858b7cd3ff0dbd8f59bb121f
---

# AD — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_e19c7fe27fbcc4cd923d|AD — Koninklijke Ahold Delhaize N.V. ordinary shares]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-21 through 2026-09-18
- Latest adjusted close: 31.600000381469727
- Period return: 0.018041219375810352523937181
- Trigger strength: 0.376830255
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume-anomaly trigger is a validated market transition for the tracked security and merits durable monitoring context.
