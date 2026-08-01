---
title: '[COIN] MACD cross below signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-01'
updated: '2026-08-01'
provenance: deterministic-market-monitor
content_hash: 639eeb2b117c06bce49d2d2a94ec2ef67923c3ef4208794ad0f64ec7114247aa
classifier_decision: ingest
classifier_reason: Material bearish MACD transition with an 11.6% decline over the
  validated period merits durable wiki ingestion.
related_entity_ids:
- security_37ddcbdaad296ad831f2
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_37ddcbdaad296ad831f2
  trigger: macd_cross_below_signal
  transition: entered
  as_of_date: '2026-07-31'
  period_start: '2026-07-02'
  period_end: '2026-07-31'
  latest_close: '146.25999450683594'
  return_period: '-0.1161469767762662652627794137'
  strength: '0.745636526355693836409115017'
  previous_strength: '0'
  source_price_hash: e1651044890635a944ee7b073558b4ead37fa9dc5f6717ed6b2973ad47738363
---

# [COIN] MACD cross below signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_37ddcbdaad296ad831f2|COIN — Coinbase Global, Inc. Class A common stock]] (`security_37ddcbdaad296ad831f2`)
- Trigger: `macd_cross_below_signal`
- Transition: `entered`
- Period: 2026-07-02 through 2026-07-31
- Latest adjusted close: 146.25999450683594
- Period return: -0.1161469767762662652627794137
- Trigger strength: 0.745636526355693836409115017
- Previous strength: 0
- Source price hash: `e1651044890635a944ee7b073558b4ead37fa9dc5f6717ed6b2973ad47738363`

## Classifier disposition

- Decision: `ingest`
- Reason: Material bearish MACD transition with an 11.6% decline over the validated period merits durable wiki ingestion.
