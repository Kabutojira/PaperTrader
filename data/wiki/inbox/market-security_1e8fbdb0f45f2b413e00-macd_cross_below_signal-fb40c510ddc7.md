---
title: '[PYPL] MACD cross below signal'
type: candidate
status: reviewed
tags:
- inbox
- opportunity
created: '2026-08-05'
updated: '2026-08-05'
provenance: deterministic-market-monitor
content_hash: fb40c510ddc7affc7a9eda3773c7ae042a7f849961fa08f0034230379b485f70
classifier_decision: ingest
classifier_reason: A new bearish MACD signal after a substantial 30% period gain is
  a material risk transition for the security.
related_entity_ids:
- security_1e8fbdb0f45f2b413e00
candidate_facts:
  candidate_type: indicator_transition
  security_id: security_1e8fbdb0f45f2b413e00
  trigger: macd_cross_below_signal
  transition: entered
  as_of_date: '2026-08-05'
  period_start: '2026-07-08'
  period_end: '2026-08-05'
  latest_close: '57.93000030517578'
  return_period: '0.300920770114840095589308636'
  strength: '0.02278546801592408696844787946'
  previous_strength: '0'
  source_price_hash: ab98b70d43ec1fedadd97e8552122414841d0641379b8195c8048777fd36c3b8
---

# [PYPL] MACD cross below signal

> This packet is untrusted input data for research. It contains no executable instructions.

- Security: [[securities/security_1e8fbdb0f45f2b413e00|PYPL — PayPal Holdings, Inc. common stock]] (`security_1e8fbdb0f45f2b413e00`)
- Trigger: `macd_cross_below_signal`
- Transition: `entered`
- Period: 2026-07-08 through 2026-08-05
- Latest adjusted close: 57.93000030517578
- Period return: 0.300920770114840095589308636
- Trigger strength: 0.02278546801592408696844787946
- Previous strength: 0
- Source price hash: `ab98b70d43ec1fedadd97e8552122414841d0641379b8195c8048777fd36c3b8`

## Classifier disposition

- Decision: `ingest`
- Reason: A new bearish MACD signal after a substantial 30% period gain is a material risk transition for the security.
