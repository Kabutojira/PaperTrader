---
title: '[AMZN] Volume anomaly'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-07-31'
updated: '2026-07-31'
provenance: deterministic-market-monitor
content_hash: e61b5356f36f3e481f784ecb296aa8107ffabf810a1272e4d12b7153005eb7e7
classifier_decision: ingest
classifier_reason: A strong newly entered volume anomaly with a material negative
  monthly return merits durable review.
related_entity_ids:
- security_2433a056eb0c55961fcc
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_2433a056eb0c55961fcc
  trigger: volume_anomaly
  transition: entered
  as_of_date: '2026-07-30'
  period_start: '2026-07-01'
  period_end: '2026-07-30'
  latest_close: '235.5'
  return_period: '-0.0256516219550051195028470107'
  strength: '0.98033297'
  previous_strength: '0'
  source_price_hash: 200396dbbd81b7ec09a5b79863cf355c888217931d18c42885ebbc2590a8917f
---

# [AMZN] Volume anomaly

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: AMZN — Amazon.com, Inc. common stock (`security_2433a056eb0c55961fcc`)
- Trigger: `volume_anomaly`
- Transition: `entered`
- Period: 2026-07-01 through 2026-07-30
- Latest adjusted close: 235.5
- Period return: -0.0256516219550051195028470107
- Trigger strength: 0.98033297
- Previous strength: 0
- Source price hash: `200396dbbd81b7ec09a5b79863cf355c888217931d18c42885ebbc2590a8917f`

## Classifier disposition

- Decision: `ingest`
- Reason: A strong newly entered volume anomaly with a material negative monthly return merits durable review.
