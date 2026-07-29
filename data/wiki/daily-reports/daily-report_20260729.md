---
title: "PaperTrader daily report — 2026-07-29"
type: daily-report
status: maintained
tags:
  - daily-report
created: "2026-07-29"
updated: "2026-07-29"
provenance: deterministic-report-generator
run_id: "youtube-bootstrap-20260729"
snapshot_id: "decision_d2bc1d724ae1b108c0fb"
---

# PaperTrader daily report — 2026-07-29

## 1. Investor decision summary

<!-- papertrader-investor-brief:start -->
# No trade — hold 100% cash

- **Investment data:** Degraded — review investment data gaps
- **Operations:** Current
- **As of:** `2026-07-29T14:30:18Z`
- **Snapshot:** `decision_d2bc1d724ae1b108c0fb`
- **Cash:** 10000 EUR (100%)
- **Gross exposure:** 0 EUR
- **Approved target cash:** 10000 EUR (100%)
- **Actionable signals:** 0

## Approved target changes

No approved target changes.

## Actionable signals

No actionable trade signals.

## Price action alerts

- **[PARRO.PA — Parrot S.A.](securities/security_cc4dcb8f002b61dffe00): Bollinger Below Lower** (`2026-07-28`)
  - Research: **succeeded**
  - Decision: Classified Parrot's 2026-06-29 through 2026-07-27 lower-Bollinger transition as noise, not a fundamental opportunity or material risk signal. The adjusted close declined only 0.6179% over the exact period and ended 1.6717% below the lower band after no trigger on the prior session. Parrot's primary publication index showed no time-matched issuer release, while the current thesis already records unresolved valuation, order-concentration, component-provenance, and durable cash-conversion gates. No wiki update or follow-up was warranted because a bounded security revalidation is already ready ahead of the half-year evidence checkpoint.
- **[ALB — Albemarle Corporation](securities/security_66cdcf90aac0d83e76f3): Rsi Oversold** (`2026-07-27`)
  - Research: **succeeded**
  - Decision: Classified Albemarle's 2026-07-24 oversold-RSI transition as unresolved commodity and earnings risk, not a buy signal. The 18.47% observation-period decline coincided with lithium-price repricing, while the issuer supplied no new operating result during the window and Q1 sensitivity remained dominated by lithium price, contract lag, capital needs, and dilution. Enqueued one post-Q2 security review for 2026-08-06.
- **[RTX — RTX Corporation](securities/security_59304f90c440def31dc5): Bollinger Above Upper** (`2026-07-27`)
  - Research: **skipped**
  - Decision: Queue triage disposition
- **[RTX — RTX Corporation](securities/security_59304f90c440def31dc5): Rsi Overbought** (`2026-07-27`)
  - Research: **skipped**
  - Decision: Queue triage disposition
- **[LAC — Lithium Americas Corp.](securities/security_fb87fac302a5446a1ced): Rsi Oversold** (`2026-07-27`)
  - Research: **succeeded**
  - Decision: Classified Lithium Americas' 2026-07-24 oversold-RSI transition as fundamental and commodity risk, not a contrarian opportunity. The 26.45% observation-period decline occurred without a material issuer project update and leaves a pre-revenue, construction-stage equity exposed to lithium pricing, remaining capex, conditional funding, warrants, dilution, commissioning, and schedule risk. No follow-up was created because the current security review already defines those gates and the next evidence checkpoint is a substantive construction disclosure.

## Top blocker or near miss

- **ISRG — Intuitive Surgical, Inc.:** Base-case upside is below the configured entry minimum.
<!-- papertrader-investor-brief:end -->

### Deterministic reasons

- The reconciled model portfolio is entirely cash.
- No strategy has produced a current actionable trade signal.

## 2. Model portfolio and approved changes

- Current equity: 10000 EUR
- Current cash: 10000 EUR (100%)
- Current gross exposure: 0 EUR
- Approved target cash: 10000 EUR (100%)
- Pending-order targets are estimates at the snapshot mark; only fills change accounting.

| Holding | Sleeve | Current weight | Approved target | Current value | Target value | Action | State |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Cash | cash | 100% | 100% | 10000  | 10000  | No trade | No action |

## 3. Actionable signals and pending orders

No actionable trade signals.

No pending paper orders.

## 4. Candidates and near misses

| Candidate | State | Score | Base upside | Main reason |
| --- | --- | ---: | ---: | --- |
| [ISRG — Intuitive Surgical, Inc.](securities/security_1f9cce545ede94cd6349) | Valuation unattractive | 63 | 2.5% | Base-case upside is below the configured entry minimum. |
| [GEV — GE Vernova Inc.](securities/security_4b61970aa8f574446819) | Valuation unattractive | 45.2 | 2% | Base-case upside is below the configured entry minimum. |
| [ANET — Arista Networks, Inc.](securities/security_6f9a1450edceb9307c9a) | Valuation unattractive | 38.4 | 2.2% | Base-case upside is below the configured entry minimum. |
| [PLTR — Palantir Technologies Inc.](securities/security_bdc2f87dadf134760c3a) | Valuation unattractive | 34.6 | -18.9% | The assessed base case has no positive upside. |
| [RBLX — Roblox Corporation](securities/security_c9a37d277445869a8809) | Valuation unattractive | 30.6 | -19.9% | The assessed base case has no positive upside. |

## 5. Performance and risk

- Daily return: 0%
- Cumulative return: 0%
- Running drawdown: 0%
- Realized P/L: 0 EUR
- Unrealized P/L: 0 EUR
- Largest position weight: 0%
- Largest sector weight: 0%


## 6. Research changes

- [[ideas/idea_ai_infrastructure_power]]
- [[model-portfolio]]
- [[performance]]
- [[research-catalog]]
- [[security-catalog]]
- [[signals]]
- [[system-status]]

## 7. Data-quality and coverage impact

- Investment data status: **degraded**
- Operations status: **current**
- Assessments: 24/24
- Fresh-evidence assessments: 24/24
- Relationship reviews: 24/24
- Accepted relationships: 22
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market-data success/failure: 24/0
- Research alerts (not trade signals): 5

### Current system impacts

- **affects candidate** — HOOD Robinhood Markets, Inc.: Daily preparation degraded: security\_ad3b1f8f59fd599f079a
- **affects candidate** — CROX Crocs, Inc.: Daily preparation degraded: security\_c150f31c30afdb4a85f9
- **affects candidate** — WTI W&amp;T Offshore, Inc.: Daily preparation degraded: security\_61567714298b9563d1a9
- **affects candidate** — DLO DLocal Limited: Daily preparation degraded: security\_715bde20b6e1e1320c1a
- **affects candidate** — PLS.AX PLS Group Limited: Daily preparation degraded: security\_8a5c43888d224de85c69
- **affects candidate** — KTOS Kratos Defense &amp; Security Solutions, Inc.: Daily preparation degraded: security\_0cf8075039299094d614
- **affects candidate** — PYPL PayPal Holdings, Inc.: Daily preparation degraded: security\_1e8fbdb0f45f2b413e00
- **affects candidate** — SOFI SoFi Technologies, Inc.: Daily preparation degraded: security\_98470cfc01bbcde78fc2
- **affects candidate** — CSL Carlisle Companies Incorporated: Daily preparation degraded: security\_9b0db3bc77914b23a307
- **affects candidate** — INTC Intel Corporation: Daily preparation degraded: security\_dfa34d4b9050964b465e
- **affects candidate** — TWST Twist Bioscience Corporation: Daily preparation degraded: security\_6cf75bd0ec0aa2a20148
- **affects candidate** — FUC.F Fanuc Corporation: Daily preparation degraded: security\_96ba305ee7cd586bc348
- **affects candidate** — TSLA Tesla, Inc.: Daily preparation degraded: security\_dc7a111e297be528d96b
- **affects candidate** — VALE Vale S.A.: Daily preparation degraded: security\_b2116dcf976c96974d7b
- **affects candidate** — ANIC.L Agronomics Limited: Daily preparation degraded: security\_fe4648901e7675f157fd
- **affects candidate** — GOOGL Alphabet Inc.: Daily preparation degraded: security\_c86bb4e75658c07142cf
- **affects candidate** — ABCL AbCellera Biologics Inc.: Daily preparation degraded: security\_7bf8f4c9cc12ae410e40
- **affects candidate** — TXN Texas Instruments Incorporated: Daily preparation degraded: security\_83a56943e18793f685b0
- **affects candidate** — VLO Valero Energy Corporation: Daily preparation degraded: security\_c5a9e460d3350284d157
- **affects candidate** — QCOM QUALCOMM Incorporated: Daily preparation degraded: security\_3a75fc1ccca2ee7c937a
- **affects candidate** — MP MP Materials Corp.: Daily preparation degraded: security\_cd492d97064d8574156e
- **affects candidate** — TSM Taiwan Semiconductor Manufacturing Company Limited: Daily preparation degraded: security\_ce9b78a4d0773c950765
- **affects candidate** — PATH UiPath, Inc.: Daily preparation degraded: security\_eca976f0076a425ea1bb
- **affects candidate** — ASML ASML Holding N.V.: Daily preparation degraded: security\_ef35e41886220d51c22c
- **affects candidate** — MSTR Strategy Inc: Daily preparation degraded: security\_fe5539a7d3fd9d553bce
- **affects candidate** — SPCX Space Exploration Technologies Corp.: Daily preparation degraded: security\_664f93a7eaca72e76e9b
- **affects candidate** — NBIS Nebius Group N.V.: Daily preparation degraded: security\_47a0b06f6c6c478d7c1e
- **affects candidate** — YEC.F YASKAWA Electric Corporation: Daily preparation degraded: security\_89969b7dac39b7db5661
- **affects candidate** — META Meta Platforms, Inc.: Daily preparation degraded: security\_d12e746b3c9d392183cc
- **affects candidate** — MSFT Microsoft Corporation: Daily preparation degraded: security\_204be2a44063993de1a8
- **affects candidate** — SSUN.VI Samsung Electronics Co., Ltd.: Daily preparation degraded: security\_d08d763780400dfbffce
- **affects candidate** — VRT Vertiv Holdings Co: Daily preparation degraded: security\_cb88f9154cfeaa15e878
- **affects candidate** — LH Labcorp Holdings Inc.: Daily preparation degraded: security\_b1f2c48e1a744f5ecf67
- **affects candidate** — PL Planet Labs PBC: Daily preparation degraded: security\_97f38b2cb2d5ef127f5a
- **affects candidate** — TDY Teledyne Technologies Incorporated: Daily preparation degraded: security\_ad5917642acbba28c1f2
- **affects candidate** — AMAT Applied Materials, Inc.: Daily preparation degraded: security\_0a56aa634d077fe5796f
- **affects candidate** — NIB.F Nidec Corporation: Daily preparation degraded: security\_3853e54c619d597dcaa1
- **affects candidate** — LUNR Intuitive Machines, Inc.: Daily preparation degraded: security\_a5dc16f3f4b245e6c168
- **affects candidate** — DNA Ginkgo Bioworks Holdings, Inc.: Daily preparation degraded: security\_95351d928b674bbdf687
- **affects candidate** — CSIQ Canadian Solar Inc.: Daily preparation degraded: security\_099561384c0f5e697727
- **affects candidate** — AMZN Amazon.com, Inc.: Daily preparation degraded: security\_2433a056eb0c55961fcc
- **affects candidate** — SPOT Spotify Technology S.A.: Daily preparation degraded: security\_2010347f1a0a5ea60f47
- **affects candidate** — SSU.VI Samsung Electronics Co., Ltd.: Daily preparation degraded: security\_567d0d575bbd30aaa91d
- **affects candidate** — CRSR Corsair Gaming, Inc.: Daily preparation degraded: security\_55c9ce2fdcd32dad6b8c
- **affects candidate** — NVDA NVIDIA Corporation: Daily preparation degraded: security\_33d9c44facc75c726c7d

## 8. Audit appendix

### Run diagnostics

- Run ID: `youtube-bootstrap-20260729`
- Run status: `degraded`
- Generated (UTC): `2026-07-29T14:30:18Z`
- Decision snapshot: `decision_d2bc1d724ae1b108c0fb`

### Complete market freshness

| Security ID | Price date | Retrieved at | Status | Error |
| --- | --- | --- | --- | --- |
| security_18a3ab0ee6086ee85d0f | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_1c055eb9b2bb1f5a8ff2 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_1f9cce545ede94cd6349 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_22c2b9d782a62d7a9b86 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_2c779e81c27b78c556bb | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_2dbe878dfc899d7ee867 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_37ddcbdaad296ad831f2 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_4627aea1bf7d8943d3d8 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_4b61970aa8f574446819 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_59304f90c440def31dc5 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_66cdcf90aac0d83e76f3 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_6ad1af8d10d6276a0221 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_6f9a1450edceb9307c9a | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_7ca095d63423c55a90e3 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_8472507d7d320aa388a7 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_9d4049ed6669a52815d6 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_a9eb9838940ef5ceaa0c | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_bdc2f87dadf134760c3a | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_c120e9f26ebb6159adf9 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_c9a37d277445869a8809 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_cc4dcb8f002b61dffe00 | 2026-07-28 | 2026-07-28T16:30:00Z | ok | — |
| security_ed7d5b616a196969c815 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_f2b9760d847b2ba59324 | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |
| security_fb87fac302a5446a1ced | 2026-07-27 | 2026-07-28T16:30:00Z | ok | — |

### Orders and executions

| Order ID | Strategy ID | Fill policy | Status | Created |
| --- | --- | --- | --- | --- |
| — | — | — | no orders | — |

| Execution ID | Order ID | Security ID | Side | Quantity | Fill | Fees |
| --- | --- | --- | --- | ---: | ---: | ---: |
| — | — | — | — | 0 | no executions | 0 |

### Allocation audit

- Plan ID: `allocation_plan_4834e38fb71e6631e320`
- Mode: `active`
- Deployment budget: 1500 EUR
- Capital allocated: 0 EUR
- Capital unallocated: 6000 EUR

| Rank | Security ID | Target weight | Disposition | Machine reasons |
| ---: | --- | ---: | --- | --- |
| — | security_18a3ab0ee6086ee85d0f | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_1c055eb9b2bb1f5a8ff2 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle |
| — | security_1f9cce545ede94cd6349 | 0% | excluded | base_upside_below_minimum\|upside_downside_ratio_below_minimum |
| — | security_22c2b9d782a62d7a9b86 | 0% | excluded | base_upside_below_minimum\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_2c779e81c27b78c556bb | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_2dbe878dfc899d7ee867 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_37ddcbdaad296ad831f2 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_4627aea1bf7d8943d3d8 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:accounting_uncertain,solvency_risk,valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_4b61970aa8f574446819 | 0% | excluded | base_upside_below_minimum\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_59304f90c440def31dc5 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_66cdcf90aac0d83e76f3 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_6ad1af8d10d6276a0221 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_6f9a1450edceb9307c9a | 0% | excluded | base_upside_below_minimum\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_7ca095d63423c55a90e3 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_8472507d7d320aa388a7 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_9d4049ed6669a52815d6 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_a9eb9838940ef5ceaa0c | 0% | excluded | base_upside_below_minimum\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_bdc2f87dadf134760c3a | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_c120e9f26ebb6159adf9 | 0% | excluded | base_upside_not_positive\|relationship_missing_or_stale\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_c9a37d277445869a8809 | 0% | excluded | base_upside_not_positive\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_cc4dcb8f002b61dffe00 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_ed7d5b616a196969c815 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_f2b9760d847b2ba59324 | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |
| — | security_fb87fac302a5446a1ced | 0% | excluded | assessment_ineligible\|base_upside_not_positive\|confidence_below_minimum\|hard_blocker:valuation_unsupported\|score_below_cash_hurdle\|upside_downside_ratio_below_minimum |

### Curated YouTube discovery

- Status: `succeeded`
- Operations queued: `30`
- Channel failures: `0`

| Channel | Status | Discovered | Queued | Reason |
| --- | --- | ---: | ---: | --- |
| @allin | succeeded | 5 | 5 | — |
| @thelimitingfactor | succeeded | 5 | 5 | — |
| @ConnectingODots | succeeded | 5 | 5 | — |
| @DumbMoneyLive | succeeded | 5 | 5 | — |
| @CouchInvestor | succeeded | 5 | 5 | — |
| @Value-Investing | succeeded | 5 | 5 | — |


### Research-operation audit

| Operation ID | Type | Entity ID | Disposition | Machine reason |
| --- | --- | --- | --- | --- |
| — | — | — | no completed operations | — |

### Complete active queue

- `waiting` `01KYEWGWBRV9EV6YN1WQA6G3WF` — `security_research` for `security_cb88f9154cfeaa15e878`
- `waiting` `01KYEXAGNREGCP02XCC9VBV80V` — `security_research` for `security_c5a9e460d3350284d157`
- `waiting` `01KYFXFKB04HSHKYVSPNGXVJX0` — `security_research` for `security_66cdcf90aac0d83e76f3`
- `ready` `01KYPB1PBRCRHY63XGVY8SV80F` — `security_research` for `security_099561384c0f5e697727`
- `ready` `01KYPB1QB0JP4AER2BTKE8CNDB` — `security_research` for `security_0a56aa634d077fe5796f`
- `ready` `01KYPB1RA8KCC272M9J5G94CHK` — `security_research` for `security_0cf8075039299094d614`
- `ready` `01KYPB1S9GWCXMNQ8KBD1GT79W` — `security_research` for `security_1e8fbdb0f45f2b413e00`
- `ready` `01KYPB1T8RTD7VTFS9GRC6JBJC` — `security_research` for `security_2010347f1a0a5ea60f47`
- `ready` `01KYPB1V80Z3NV79GVG54DMFMT` — `security_research` for `security_204be2a44063993de1a8`
- `ready` `01KYPB1W78HSRT5KNG39B7SPBX` — `security_research` for `security_2433a056eb0c55961fcc`
- `ready` `01KYPB1X6GMJJD0DTCRTYAGTBE` — `security_research` for `security_33d9c44facc75c726c7d`
- `ready` `01KYPB1Y5R4NFAMSPZZX3YAS1E` — `security_research` for `security_3853e54c619d597dcaa1`
- `ready` `01KYPB1Z50955WQSMSWYR16957` — `security_research` for `security_3a75fc1ccca2ee7c937a`
- `ready` `01KYPB2048VWN4VV7YYF4Y60TX` — `security_research` for `security_47a0b06f6c6c478d7c1e`
- `ready` `01KYPB213GFWH1QMBGJT4A5KDA` — `security_research` for `security_55c9ce2fdcd32dad6b8c`
- `ready` `01KYPB222RS736JB5G655TEAP0` — `security_research` for `security_567d0d575bbd30aaa91d`
- `ready` `01KYPB2320KM60TB1XB6840QEB` — `security_research` for `security_61567714298b9563d1a9`
- `ready` `01KYPB241838ZBZ6FE9EQCEJYW` — `security_research` for `security_664f93a7eaca72e76e9b`
- `ready` `01KYPB250GCWY1ZB0GD3QC2DBX` — `security_research` for `security_6cf75bd0ec0aa2a20148`
- `ready` `01KYPB25ZR2Q5MGTH3P47XVCJ5` — `security_research` for `security_715bde20b6e1e1320c1a`
- `ready` `01KYPB26Z023E3AMG9Z8KSPW9D` — `security_research` for `security_7bf8f4c9cc12ae410e40`
- `ready` `01KYPB27Y84W38J6MDDEF7PHG0` — `security_research` for `security_83a56943e18793f685b0`
- `ready` `01KYPB28XGJ631HDJC853RGBJJ` — `security_research` for `security_89969b7dac39b7db5661`
- `ready` `01KYPB29WRNJGPJTTY2DB72JWG` — `security_research` for `security_8a5c43888d224de85c69`
- `ready` `01KYPB2AW0SJ35EAKMPQM8QVAH` — `security_research` for `security_95351d928b674bbdf687`
- `ready` `01KYPB2BV8XK4AAREZ3257MDE0` — `security_research` for `security_96ba305ee7cd586bc348`
- `ready` `01KYPB2BV8R4KE0M2GGGTY4MCA` — `security_research` for `security_97f38b2cb2d5ef127f5a`
- `ready` `01KYPB2DSRFNQ0NE6AY81GQZKR` — `security_research` for `security_98470cfc01bbcde78fc2`
- `ready` `01KYPB2ES0F7XVNM442WFYF32Z` — `security_research` for `security_9b0db3bc77914b23a307`
- `ready` `01KYPB2FR822FVSNTSDF6Z7735` — `security_research` for `security_a5dc16f3f4b245e6c168`
- `ready` `01KYPB2GQGHN1J2S82EFKN1CAH` — `security_research` for `security_ad3b1f8f59fd599f079a`
- `ready` `01KYPB2HPR71QC8BBTPA3HMW8R` — `security_research` for `security_ad5917642acbba28c1f2`
- `ready` `01KYPB2JP0EAQ643PE2MQAZJAE` — `security_research` for `security_b1f2c48e1a744f5ecf67`
- `ready` `01KYPB2KN8R1RGAPDZQ2AN9P2V` — `security_research` for `security_b2116dcf976c96974d7b`
- `ready` `01KYPB2MMG5E7Y3EVH2XS3MV0G` — `security_research` for `security_c150f31c30afdb4a85f9`
- `ready` `01KYPB2NKR40C7V30WG552P7WP` — `security_research` for `security_c86bb4e75658c07142cf`
- `ready` `01KYPB2PK0R0ZXAHGNGZ6X5FM8` — `security_research` for `security_cd492d97064d8574156e`
- `ready` `01KYPB2PK0N1W5XHVXFXW43JSZ` — `security_research` for `security_ce9b78a4d0773c950765`
- `ready` `01KYPB2QJ8QGJJAGXQ71MT7GWW` — `security_research` for `security_d08d763780400dfbffce`
- `ready` `01KYPB2RHG2WF001VJFAJXH5S6` — `security_research` for `security_d12e746b3c9d392183cc`
- `ready` `01KYPB2SGR9CYX2QDN613D7T59` — `security_research` for `security_dc7a111e297be528d96b`
- `ready` `01KYPB2TG0W0FFP83ZG7KC45YP` — `security_research` for `security_dfa34d4b9050964b465e`
- `ready` `01KYPB2VF8GSJR3R78FTPFE8YM` — `security_research` for `security_eca976f0076a425ea1bb`
- `ready` `01KYPB2WEG34EDYWPNKJ7QQVC7` — `security_research` for `security_ef35e41886220d51c22c`
- `ready` `01KYPB2XDRKAMP0ZX3MWA7Y1JH` — `security_research` for `security_fe4648901e7675f157fd`
- `ready` `01KYPB2YD02XHRSSW68JA9MCG7` — `security_research` for `security_fe5539a7d3fd9d553bce`
- `ready` `01KYPFC140X5NVAEQ8276H0MRZ` — `idea_research` for `idea_ai_infrastructure_power`
- `ready` `01KYQ49D1GWY55GJNJNBQRCJ74` — `wiki_ingest` for `youtube_TqNiSTeNtb0`
- `ready` `01KYQ49D1GGA0W6TAYFVSGQXR3` — `wiki_ingest` for `youtube_wcV0SRPFK9s`
- `ready` `01KYQ49D1GS4CXMK0S510Y67TM` — `wiki_ingest` for `youtube_OY2Sjbjd_VE`
- `ready` `01KYQ49D1GJ32KP17XS3Z8DJ00` — `wiki_ingest` for `youtube_9IMwRIei-Xc`
- `ready` `01KYQ49D1GETPHJ2B8PYVG9FE0` — `wiki_ingest` for `youtube_-ILKiOU5iAQ`
- `ready` `01KYQ49D1GRCPWM612C0NAM0Z1` — `wiki_ingest` for `youtube_SuSYegb8iK0`
- `ready` `01KYQ49D1G6RHZ9VJYDV5NKPTT` — `wiki_ingest` for `youtube_h7XVJ64IhY4`
- `ready` `01KYQ49D1GWWHW1JFKE6VSSHB7` — `wiki_ingest` for `youtube_pVwvxybnwdg`
- `ready` `01KYQ49D1GNQZG7ZW58JW442R5` — `wiki_ingest` for `youtube_TyMn7wknYTU`
- `ready` `01KYQ49D1GF9JD930JH9N49P07` — `wiki_ingest` for `youtube_oyjpF7xPiC4`
- `ready` `01KYQ49D1GGG62YPWBRNTM1WFD` — `wiki_ingest` for `youtube_Ejsft2oPCtM`
- `ready` `01KYQ49D1GB9057VRBFHJ9Y1NX` — `wiki_ingest` for `youtube_k77X47h6OVU`
- `ready` `01KYQ49D1GAXYP4Y8RR9C5G3KN` — `wiki_ingest` for `youtube_yUq0O-pDHCE`
- `ready` `01KYQ49D1G2RNAXKS9RP0MY1R9` — `wiki_ingest` for `youtube_9ePWIYadju4`
- `ready` `01KYQ49D1GYV061JMYPWWGR6E4` — `wiki_ingest` for `youtube_yG-bk8QEjsA`
- `ready` `01KYQ49D1GFY1PFRCMBZ41Q88C` — `wiki_ingest` for `youtube_u-AXyF9kY9k`
- `ready` `01KYQ49D1GNN84QQ53F97HDY1P` — `wiki_ingest` for `youtube_AK_aWcM-VAY`
- `ready` `01KYQ49D1GZK4Z8RANH5XP9TC0` — `wiki_ingest` for `youtube_t3RTJJ6KM_I`
- `ready` `01KYQ49D1G3QX14JS5VBH76HN0` — `wiki_ingest` for `youtube_6006vpLlaVw`
- `ready` `01KYQ49D1GXYX0SF93BMTNHYM8` — `wiki_ingest` for `youtube_-lUsDKvZJu0`
- `ready` `01KYQ49D1GKPX5A7WGCV9GPG8X` — `wiki_ingest` for `youtube_65IABPxBJ9M`
- `ready` `01KYQ49D1GX6X7ACXB1A6KFTR4` — `wiki_ingest` for `youtube_OcXcgIlJGRw`
- `ready` `01KYQ49D1GNF94BPJNDE0ZFWSK` — `wiki_ingest` for `youtube_a0l7VDnN1bg`
- `ready` `01KYQ49D1GD05JQFX2ZE5MTRWZ` — `wiki_ingest` for `youtube_3c9iLgtDdKM`
- `ready` `01KYQ49D1GHSHA6ZVKD6N2VFBG` — `wiki_ingest` for `youtube_pVaKoDHW9iY`
- `ready` `01KYQ49D1G889B5DYTST65N0EW` — `wiki_ingest` for `youtube_4JmCb5FmTA4`
- `ready` `01KYQ49D1GCWM22YHNBNMM75XE` — `wiki_ingest` for `youtube_yAtpMMC3aiw`
- `ready` `01KYQ49D1GENTSWY2QD1D1RREE` — `wiki_ingest` for `youtube_Cbbmj0dqP-M`
- `ready` `01KYQ49D1G663ZCTKEG5CJHK7B` — `wiki_ingest` for `youtube_e2C_hgXiyzM`
- `ready` `01KYQ49D1G3CHJ4YE6BKXP9RX9` — `wiki_ingest` for `youtube_J2ZqFVpMb5M`

### Open issues and delivery failures

- `warning` **`issue_0452943dbcb7cbcd404b`** — Daily preparation degraded: security\_ad3b1f8f59fd599f079a: security\_ad3b1f8f59fd599f079a: price cache is empty
- `warning` **`issue_10ff1797ec43b252e279`** — Daily preparation degraded: security\_c150f31c30afdb4a85f9: security\_c150f31c30afdb4a85f9: price cache is empty
- `warning` **`issue_1285e87ea97cc268036a`** — Daily preparation degraded: security\_61567714298b9563d1a9: security\_61567714298b9563d1a9: price cache is empty
- `warning` **`issue_1ad34e45aa4568f4a522`** — Daily preparation degraded: security\_715bde20b6e1e1320c1a: security\_715bde20b6e1e1320c1a: price cache is empty
- `warning` **`issue_2873eb4075f12fa65306`** — Daily preparation degraded: security\_8a5c43888d224de85c69: security\_8a5c43888d224de85c69: price cache is empty
- `warning` **`issue_3135d82d86a9c902250b`** — Daily preparation degraded: security\_0cf8075039299094d614: security\_0cf8075039299094d614: price cache is empty
- `warning` **`issue_3387fb684632341a351b`** — Daily preparation degraded: security\_1e8fbdb0f45f2b413e00: security\_1e8fbdb0f45f2b413e00: price cache is empty
- `warning` **`issue_38d1e37f3d5d6e110e08`** — Daily preparation degraded: security\_98470cfc01bbcde78fc2: security\_98470cfc01bbcde78fc2: price cache is empty
- `warning` **`issue_3a4655b66f410a1836dc`** — Daily preparation degraded: security\_9b0db3bc77914b23a307: security\_9b0db3bc77914b23a307: price cache is empty
- `warning` **`issue_4cea078fdac19d342c04`** — Daily preparation degraded: security\_dfa34d4b9050964b465e: security\_dfa34d4b9050964b465e: price cache is empty
- `warning` **`issue_50e28d602eb0feb06784`** — Daily preparation degraded: security\_6cf75bd0ec0aa2a20148: security\_6cf75bd0ec0aa2a20148: price cache is empty
- `warning` **`issue_55f958632a0f142a3925`** — Daily preparation degraded: security\_96ba305ee7cd586bc348: security\_96ba305ee7cd586bc348: price cache is empty
- `warning` **`issue_568a09e6aa89b220ac34`** — Daily preparation degraded: security\_dc7a111e297be528d96b: security\_dc7a111e297be528d96b: price cache is empty
- `warning` **`issue_5f40235a5598fc72203e`** — Daily preparation degraded: security\_b2116dcf976c96974d7b: security\_b2116dcf976c96974d7b: price cache is empty
- `warning` **`issue_6b3c8e68ec789ffd7037`** — Daily preparation degraded: security\_fe4648901e7675f157fd: security\_fe4648901e7675f157fd: price cache is empty
- `warning` **`issue_6c93f0fd88af720b0060`** — Daily preparation degraded: security\_c86bb4e75658c07142cf: security\_c86bb4e75658c07142cf: price cache is empty
- `warning` **`issue_74ca76f4c9de18775121`** — Daily preparation degraded: security\_7bf8f4c9cc12ae410e40: security\_7bf8f4c9cc12ae410e40: price cache is empty
- `warning` **`issue_74e89bf248810ee20ffe`** — Daily preparation degraded: security\_83a56943e18793f685b0: security\_83a56943e18793f685b0: price cache is empty
- `warning` **`issue_76d5e90287daac4b0075`** — Daily preparation degraded: security\_c5a9e460d3350284d157: security\_c5a9e460d3350284d157: price cache is empty
- `warning` **`issue_7a77bfdb512efe271402`** — Daily preparation degraded: security\_3a75fc1ccca2ee7c937a: security\_3a75fc1ccca2ee7c937a: price cache is empty
- `warning` **`issue_7b47b2b9113e25dccd6b`** — Daily preparation degraded: security\_cd492d97064d8574156e: security\_cd492d97064d8574156e: price cache is empty
- `warning` **`issue_82988148270c1671878b`** — Daily preparation degraded: security\_ce9b78a4d0773c950765: security\_ce9b78a4d0773c950765: price cache is empty
- `warning` **`issue_8839071e805e6a9f69c4`** — Daily preparation degraded: security\_eca976f0076a425ea1bb: security\_eca976f0076a425ea1bb: price cache is empty
- `warning` **`issue_8ada3995ac26a38446f5`** — Daily preparation degraded: security\_ef35e41886220d51c22c: security\_ef35e41886220d51c22c: price cache is empty
- `warning` **`issue_94374052817041f82969`** — Daily preparation degraded: security\_fe5539a7d3fd9d553bce: security\_fe5539a7d3fd9d553bce: price cache is empty
- `warning` **`issue_97455cd9fdcd489ca07f`** — Daily preparation degraded: security\_664f93a7eaca72e76e9b: security\_664f93a7eaca72e76e9b: price cache is empty
- `warning` **`issue_97953d4d2c1016441831`** — Daily preparation degraded: security\_47a0b06f6c6c478d7c1e: security\_47a0b06f6c6c478d7c1e: price cache is empty
- `warning` **`issue_a8ebff7b7d828f3d7e93`** — Daily preparation degraded: security\_89969b7dac39b7db5661: security\_89969b7dac39b7db5661: price cache is empty
- `warning` **`issue_a95ee10bec8dac18764c`** — Daily preparation degraded: security\_d12e746b3c9d392183cc: security\_d12e746b3c9d392183cc: price cache is empty
- `warning` **`issue_ad9eb2e31cc57f9f4f03`** — Daily preparation degraded: security\_204be2a44063993de1a8: security\_204be2a44063993de1a8: price cache is empty
- `warning` **`issue_b179d981c051d3993456`** — Daily preparation degraded: security\_d08d763780400dfbffce: security\_d08d763780400dfbffce: price cache is empty
- `warning` **`issue_b20b8e588a6dab63737a`** — Daily preparation degraded: security\_cb88f9154cfeaa15e878: security\_cb88f9154cfeaa15e878: price cache is empty
- `warning` **`issue_b257fa5df338d5ef2c65`** — Daily preparation degraded: security\_b1f2c48e1a744f5ecf67: security\_b1f2c48e1a744f5ecf67: price cache is empty
- `warning` **`issue_b9604572acf8d22dc6fd`** — Daily preparation degraded: security\_97f38b2cb2d5ef127f5a: security\_97f38b2cb2d5ef127f5a: price cache is empty
- `warning` **`issue_c571edbf5e35494198e7`** — Daily preparation degraded: security\_ad5917642acbba28c1f2: security\_ad5917642acbba28c1f2: price cache is empty
- `warning` **`issue_c74eab1422fff8b4584c`** — Daily preparation degraded: security\_0a56aa634d077fe5796f: security\_0a56aa634d077fe5796f: price cache is empty
- `warning` **`issue_cb9347f5eb1a1055de4e`** — Daily preparation degraded: security\_3853e54c619d597dcaa1: security\_3853e54c619d597dcaa1: price cache is empty
- `warning` **`issue_cf17771fb2fc5b9395ba`** — Daily preparation degraded: security\_a5dc16f3f4b245e6c168: security\_a5dc16f3f4b245e6c168: price cache is empty
- `warning` **`issue_d24d52684b3794870e5d`** — Daily preparation degraded: security\_95351d928b674bbdf687: security\_95351d928b674bbdf687: price cache is empty
- `warning` **`issue_d36bf9b837165bacac8a`** — Daily preparation degraded: security\_099561384c0f5e697727: security\_099561384c0f5e697727: price cache is empty
- `warning` **`issue_e1b48875d46f1bd3debb`** — Daily preparation degraded: security\_2433a056eb0c55961fcc: security\_2433a056eb0c55961fcc: price cache is empty
- `warning` **`issue_e8012ba9cfff70e45781`** — Daily preparation degraded: security\_2010347f1a0a5ea60f47: security\_2010347f1a0a5ea60f47: price cache is empty
- `warning` **`issue_ed85ad36a02af2fdfc33`** — Daily preparation degraded: security\_567d0d575bbd30aaa91d: security\_567d0d575bbd30aaa91d: price cache is empty
- `warning` **`issue_fc3830c067fcea6132aa`** — Daily preparation degraded: security\_55c9ce2fdcd32dad6b8c: security\_55c9ce2fdcd32dad6b8c: price cache is empty
- `warning` **`issue_fe482d25304c03ce4d28`** — Daily preparation degraded: security\_33d9c44facc75c726c7d: security\_33d9c44facc75c726c7d: price cache is empty

### Machine decision provenance

- `portfolio_all_cash` — The reconciled model portfolio is entirely cash.
- `no_actionable_signals` — No strategy has produced a current actionable trade signal.
- `allocation_targets`: `1f2f0e96ad9a9e26b4fc921cf6f9faed6e9ebe7faf9ea3ac20aea511130d81e6`
- `cash_ledger`: `680c5eba138f06e3afc99fbd8919ef0999b97aa6cc567edaf9a11cbece564029`
- `configuration`: `3e835d84ebd56078a57326d1a1ff256b4365fd70d480ba906ed56e775e9ea553`
- `csv_contracts`: `ca848cb3d9d5196f4a5e48bf3227ab5353f1532f70fd364a3bbe9e33780e9650`
- `decision_schema`: `db3885765b1881feae19b9833e0dcfa6baf1fe486110a7b340477d137453482a`
- `executions`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `fx_aud_eur`: `dc0ca2b710dd7b8cb9171d07515387eb9a66804fccd0950fa09cf15ac95e4f2d`
- `fx_gbp_eur`: `f6f1ce84fed173cf9e0cfca3604d82a3170d5eb03eb67f8bf9b9277ee95e7d59`
- `fx_usd_eur`: `c3d254a978e85e4103358474e046f63da2838424fd92774ed1ef2add0711e6ed`
- `indicators`: `7353ca14e663363f09759dd5c5878507dbb97e45210e2af7dd501d41f821077e`
- `issues`: `17e054e05d21fede99f508c88579de296e52ed6ecdcebad924507f36b0824c6c`
- `market_latest`: `2bc4417d2ca0acfb3f8ce0f21a6771599d34cfcf4780ae61e0d41aa5c473e6ce`
- `operation_payloads`: `b2b892910a76d127a55aad25449ec74890ea02183cea07337c9ea95a1b3fd328`
- `operations_history`: `d5be3ee47c49870b64dcc7e0a9daecff02e871fb5e9c269d4b843806a544e54a`
- `operations_todo`: `96635bce5823dcab44a9753e16422f3db324b5f14f3ec59ca58dd6f637debfc7`
- `order_legs`: `3512aeb3a497f47ab696f3794bd08b84fbf86957e471550449c0a70530347040`
- `orders`: `ed876ae7f67d9632296d12497cb334ed5c925843ac65f9691907bf7a8613a3c0`
- `performance_daily`: `093387c75b44a24e065ca7538c9faa547e7e4c4789da85d670ad742601c07f4b`
- `performance_epochs`: `bc47865ef0a04d0e2b97b9395a4276b3db677cbcfc1471469d24df7f367ac327`
- `portfolio`: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `relationships`: `a6a9995dacd90bf43997b579c49c1b9ea6ac82cf73cd578dbd97559ae54394d3`
- `runs`: `9edf5b2d6e4e9fbb1f12580f0de2e13856f8ced991f3735ab721b83f0f698725`
- `securities`: `eae80093281bb39b825157ccb07d8c58a09b5228464f4fedc701118b91c76cd2`
- `security_assessments`: `a6bc3581e9ce6e6be6ed94a60aa0c2c791f84c0dc5f57b7fb63dbf9deb67ec75`
- `signals`: `874d3deab149ff6c97a32ad6e61f2d243a5f96559acf815dfc1cd3dc91595f41`
- `source_registry`: `58999055ab38fb916c74fcda948ecfa38ecf3546a573d1d6ade2eeac5f8626ef`
- `strategies`: `5ed9f7cb50e7da9cad149dba066c4e8429a9b21ee4446bdd837fc1b0a5923e0b`
- `strategy_legs`: `c814365d6571e84fc619f0905e14a9b7671dd7e312222d4505c732719d26dddf`
- `wiki_inbox`: `fd3661e378cded9d695dbae451625b4a1b1a6f5da5a2b1a485da03997311012b`

### Links

- [[index|Investor dashboard]]
- [[model-portfolio|Model portfolio]]
- [[signals|Signals]]
- [[system-status|System status]]
- GitHub report: https://github.com/Kabutojira/PaperTrader/blob/main/data/wiki/daily-reports/daily-report_20260729.md
