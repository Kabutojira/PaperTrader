---
title: GOOGL — Volume anomaly
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-09-19'
updated: '2026-09-19'
provenance: deterministic-market-monitor
content_hash: 01b3b07ed5adfabffd6ba590eff5966a38881f28f100c9d036af98b2bb385353
classifier_decision: ingest
classifier_reason: A newly entered volume-anomaly transition with meaningful strength
  and a validated market period merits durable review context.
alert_direction: neutral
research_gate: eligible
research_gate_reason: ''
related_entity_ids:
- security_c86bb4e75658c07142cf
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_c86bb4e75658c07142cf
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-09-18'
  period_start: '2026-08-20'
  period_end: '2026-09-18'
  latest_close: '349.5400085449219'
  return_period: '0.02603691187240074788269019'
  strength: '0.61358093'
  previous_strength: '0'
  source_price_hash: 6b2292981446d5c49eb8f1ca48a0c263b130d5051a885e050ca9453e384a6288
---

# GOOGL — Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_c86bb4e75658c07142cf|GOOGL — Alphabet Inc. Class A common stock]]
- Alert: Volume anomaly
- Direction: Neutral
- Transition: Entered
- Period: 2026-08-20 through 2026-09-18
- Latest adjusted close: 349.5400085449219
- Period return: 0.02603691187240074788269019
- Trigger strength: 0.61358093
- Previous strength: 0

## Research disposition

- Decision: Ingest
- Reason: A newly entered volume-anomaly transition with meaningful strength and a validated market period merits durable review context.
