---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-09-03"
updated: "2026-09-03"
provenance: deterministic-decision-projection
snapshot_id: "decision_5e7bac4afb088c8d8e73"
as_of: "2026-09-03T09:57:19Z"
---

# System status and audit

**As of:** `2026-09-03T09:57:19Z`
**Investment data:** Portfolio state safe — research gaps remain
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

Publication validation confirms that this generated artifact is internally consistent. Investment and operations health below describe the current canonical inputs.

## Coverage

- Assessments: 47/80
- Fresh-evidence assessments: 46/80
- Relationship reviews: 19/80
- Accepted relationships: 18
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market success/failure: 81/0
- Candidate FX gaps: 0
- Research backlog: 254
- Last successful daily run: 2026-09-03

## Current issues by investment impact

Current unresolved issues: **35**.
Resolved and superseded issues remain in the canonical audit but are not current health.

### Affects Candidate (14)

- Error **ETN — Eaton Corporation plc: Hermes operation validation failed: Quick check research for ETN on 2026-08-11** — agent result schema: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment; post-run integrity: agent result data/runs/Daily report for 2026-08-11/Quick check research for ETN on 2026-08-11/agent\_result.json: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'
- Error **AMAT — Applied Materials, Inc.: Applied Materials assessment source operation is ambiguous within one run** — The schema-v2 Applied Materials assessment could not be accepted because the deterministic research applier found both the completed quick\_check\_research operation and this running security\_research operation for the same security and run\_id, then rejected the assessment as having an ambiguous source operation. The first immutable assessment request was rejected without state changes for two non-canonical soft-gap names; retry01 corrected those names but exposed the run-level ambiguity. A bounde
- Error **FUC.F — Fanuc Corporation: FANUC assessment source operation is ambiguous within one run** — The schema-v2 FANUC full-review assessment could not be accepted because the deterministic research applier found both the completed quick\_check\_research operation and this running security\_research operation for the same security and run\_id, then rejected the immutable assessment request with no assessment-state changes. The mandatory security context succeeded; both issuer PDFs were rechecked with unchanged hashes, source history and the security summary were updated through validated commands
- Error **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Hermes operation validation failed: Quick check research for KTOS on 2026-08-12** — Hermes timed out after 600s; agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for KTOS on 2026-08-12/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Hermes operation validation failed: Quick check research for HOOD on 2026-08-15** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-15/Quick check research for HOOD on 2026-08-15
- Error **RKLB — Rocket Lab Corporation: Hermes operation validation failed: Quick check research for RKLB on 2026-08-18** — commands\_run claims commands without deterministic CLI audit receipts: \['scripts/papertrader research assessment upsert --request data/runs/Daily report for 2026-08-18/Quick check research for RKLB on 2026-08-18/assessment\_upsert\_request.json', 'scripts/papertrader research security-context --security-id RKLB'\]
- Error **Hermes operation validation failed: Quick check research for SPOT on 2026-08-16** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **CROX — Crocs, Inc.: Hermes operation validation failed: Security research for CROX on 2026-08-25** — visualization\_review charts do not match chart ids in changed research pages: expected \[('data/wiki/securities/CROX.md', 'crox-valuation-scenarios-20260903'), ('data/wiki/securities/CROX.md', 'q2-revenue-and-adjusted-operating-income')\], got \[('data/wiki/securities/CROX.md', 'crox-scenario-fair-values-20260903'), ('data/wiki/securities/CROX.md', 'q2-revenue-and-adjusted-operating-income')\]
- Error **Hermes operation validation failed: Security research for SGML on 2026-08-17** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-17/Security research for SGML on 2026-08-17
- Error **ALB — Albemarle Corporation: Hermes operation validation failed: Quick check research for ALB on 2026-08-09** — Hermes timed out after 600s; agent result was written before completed change: data/runs/Daily report for 2026-08-09/Quick check research for ALB on 2026-08-09/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Hermes operation validation failed: Security research for ABBNY on 2026-08-17** — files\_changed claims paths absent from the actual delta: \['data/operations/operations\_TODO.csv'\]
- Error **Hermes operation validation failed: Quick check research for TWST on 2026-08-05** — agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for TWST on 2026-08-05/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **ASML — ASML Holding N.V.: ASML assessment rejected after security row update** — The retry operation refreshed the ASML page and security row to the 2026-08-19 USD 1,751.73 mark, but the schema-v2 assessment request was rejected before assessment state changed because valuation\_template\_rationale is a required field and was omitted. The routed-operation no-retry rule forbids correcting and invoking a second assessment request after this rejection. The canonical assessment therefore remains the prior unsupported version, the prepared relationship and idea follow-up requests w
- Error **WTI — W&amp;T Offshore, Inc.: Hermes operation validation failed: Quick check research for WTI on 2026-08-18** — completed security research requires this run's comparable assessment

### Publication Only (14)

- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — Hermes timed out after 1200s; agent result was written before completed change: data/runs/Daily report for 2026-08-17/Daily podcast for Daily report for 2026-08-17 on 2026-08-17/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-05 on 2026-08-05** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/Daily report for 2026-08-05/Daily podcast for Daily report for 2026-08-05 on 2026-08-05/agent\_result.json
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — cannot restore rejected path data/wiki/daily-reports/daily-report\_20260806.md: pre-run path cannot be restored because Git metadata is unavailable; daily podcast spoken transcript must label paper trading
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — non-successful daily podcast must not retain a transcript page
- Warning **Daily podcast failed: Daily report for 2026-08-25** — Reviewed both successful developments in the frozen context. The Parrot lower-band check was excluded as routine unchanged maintenance, and the Vale volume review was excluded because its non-substantive filing amendment, unchanged Hold / Watch conclusion, copper optionality, valuation, and volume-without-new-fundamentals lesson substantially repeat recent episodes. No audience-relevant chapter survived, so no transcript, report link, outline, or render was created. The operation could not finis
- Warning **Daily podcast failed: Daily report for 2026-08-26** — Drafted and preflighted one 2,895-word standalone episode with chapters on Bloom Energy and dLocal. Bloom was selected as novel research; dLocal was retained only for the new buy-zone and payoff-gate change. Vale and Parrot were excluded because their window updates were unchanged, low-value, and substantially covered in earlier episodes. The exact frozen transcript path passed deterministic preflight, and the single audited draft render succeeded at 1,246 seconds. The required strict integrity
- Warning **Daily podcast failed: Daily report for 2026-08-17** — retry\_exhausted:agent\_validation\_failed:Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17
- Warning **Daily podcast failed: Daily report for 2026-08-06** — retry\_exhausted:agent\_validation\_failed:Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06
- Warning **Daily podcast blocked: Daily report for 2026-08-19** — agent\_result:blocked:Blocked the daily podcast before drafting because frozen context version three declares SHA-256 recorded source state for the previous successful podcast context, while the referenced repository file hashes to recorded source state. This frozen provenance conflict must be resolved deterministically before novelty review or synthesis. No transcript or daily-report link was created, script pr
- Warning **Daily podcast failed: Daily report for 2026-08-17** — retry\_exhausted:agent\_validation\_failed:Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17
- Warning **Daily podcast blocked: Daily report for 2026-08-19** — agent\_result:blocked:Blocked because the frozen payload requires data/wiki/podcasts/daily-podcast\_20260819T221156Z.md while the deterministic podcast validator binds daily cycle Daily report for 2026-08-19 to data/wiki/podcasts/daily-podcast\_20260819T212147Z.md. The required page therefore failed deterministic preflight before rendering. The candidate slate selected Twist Bioscience and Ginkgo Bioworks for one synthetic-biology-economics chapter and Coinbase for one crypto-rails chapter; Nidec was ex
- Warning **Daily podcast failed: Daily report for 2026-08-06** — retry\_exhausted:agent\_validation\_failed:Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06
- Warning **Daily podcast failed: Daily report for 2026-08-05** — retry\_exhausted:agent\_validation\_failed:Hermes operation validation failed: Daily podcast for Daily report for 2026-08-05 on 2026-08-05

### Operational Only (7)

- Error **Local harness operation validation failed: \[Wiki ingest for www.youtube.com on 2026-08-12\](https://www.youtube.com/watch?v=fO5sC7qS04E)** — files\_changed is stale or incomplete: reported=\['data/runs/local-youtube-20260812T090946Z-03/\[Wiki ingest for www.youtube.com on 2026-08-12\](https://www.youtube.com/watch?v=fO5sC7qS04E)/agent\_result.json'\], actual=\[\]
- Warning **YouTube discovery failed for UCrTTBSUr0zhPU56UQljag5A** — @Value-Investing: 4JmCb5FmTA4 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- Warning **YouTube discovery failed for UCOOSDCjFzHfnGoV8iNLC65A** — @ConnectingODots: Ejsft2oPCtM This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- Warning **YouTube discovery failed for UCS01CiRDAiyhR\_mTHXDW23A** — @DumbMoneyLive: u-AXyF9kY9k This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- Warning **YouTube discovery failed for UCIFn7ONIJHyC-lMnb7Fm\_jw** — @thelimitingfactor: SuSYegb8iK0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- Warning **YouTube discovery failed for UCrGLm-Drgv0vbbemwwHeXJw** — @CouchInvestor: YouTube Data API video duration is malformed
- Warning **YouTube discovery failed for UCESLZhusAkFfsNsApnjF\_Cg** — @allin: TqNiSTeNtb0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html

## Sequential research backlog

- Active research operations: **254**
- Backlog size is research capacity information; it does not by itself block a safe portfolio projection or a validated action.

## Audit links

- [[research-catalog|Complete research catalog]]
- [[security-catalog|Tracked securities]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]
