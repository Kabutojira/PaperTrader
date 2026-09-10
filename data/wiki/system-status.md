---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-09-10"
updated: "2026-09-10"
provenance: deterministic-decision-projection
snapshot_id: "decision_3e0d79f008e7f74f8a18"
as_of: "2026-09-10T20:30:56Z"
---

# System status and audit

**As of:** `2026-09-10T20:30:56Z`
**Investment data:** Unsafe to publish — portfolio, accounting, or active-order state requires attention
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

Publication validation confirms that this generated artifact is internally consistent. Investment and operations health below describe the current canonical inputs.

## Current investment health

- Assessments: 52/83
- Fresh-evidence assessments: 48/83
- Relationship reviews: 20/83
- Accepted relationships: 19
- Market success/failure: 0/91
- Candidate FX gaps: 0
- Last successful daily run: 2026-09-10

## Queue and execution health

- Ready or active strategies: 4
- Active signals: 1
- Pending orders: 1
- Queued remediation operations: 0
- Operations are claimed and executed strictly sequentially.

## Sequential research backlog

- Research backlog: 344

## Publication health

- Snapshot schema and derived CSV equality: validated
- Portfolio accounting reconciliation: validated

## Current issues by investment impact

Current unresolved issues: **118**.
Resolved and superseded issues remain in the canonical audit but are not current health.

### Affects Candidate (112)

- Error **ETN — Eaton Corporation plc: Hermes operation validation failed: Quick check research for ETN on 2026-08-11** — agent result schema: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment; post-run integrity: agent result data/runs/Daily report for 2026-08-11/Quick check research for ETN on 2026-08-11/agent\_result.json: 'cd57fc97df50efa0657881b253fc96d4467881b253fc96d4467881b253fc96d446' does not match '^\[a-f0-9\]{64}$'
- Error **FUC.F — Fanuc Corporation: FANUC assessment source operation is ambiguous within one run** — The schema-v2 FANUC full-review assessment could not be accepted because the deterministic research applier found both the completed quick\_check\_research operation and this running security\_research operation for the same security and run\_id, then rejected the immutable assessment request with no assessment-state changes. The mandatory security context succeeded; both issuer PDFs were rechecked with unchanged hashes, source history and the security summary were updated through validated commands
- Error **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Hermes operation validation failed: Quick check research for KTOS on 2026-08-12** — Hermes timed out after 600s; agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for KTOS on 2026-08-12/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Hermes operation validation failed: Quick check research for HOOD on 2026-08-15** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-15/Quick check research for HOOD on 2026-08-15
- Error **RKLB — Rocket Lab Corporation: Hermes operation validation failed: Quick check research for RKLB on 2026-08-18** — commands\_run claims commands without deterministic CLI audit receipts: \['scripts/papertrader research assessment upsert --request data/runs/Daily report for 2026-08-18/Quick check research for RKLB on 2026-08-18/assessment\_upsert\_request.json', 'scripts/papertrader research security-context --security-id RKLB'\]
- Error **Hermes operation validation failed: Quick check research for SPOT on 2026-08-16** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Security research for WTI on 2026-08-18** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Security research for WTI on 2026-08-18/agent\_result.json
- Error **XMTR — Xometry, Inc.: Xometry security review blocked by issuer identity conflict** — The validated operation payload identifies XMTR with issuer\_id issuer\_0b3fe347955c2ce31e63, while canonical data/tables/securities.csv binds the same immutable security\_id to issuer\_dbdde9b294689a9af3d5. The validated security upsert correctly failed closed with an immutable-identity conflict. Four current primary sources were retained, but no security row, research page, assessment, strategy, signal, order, allocation or accounting state was changed. Resolve the canonic
- Error **Hermes operation validation failed: Security research for SGML on 2026-08-17** — operation artifact directory is not empty: /\_\_w/PaperTrader/PaperTrader/data/runs/Daily report for 2026-08-17/Security research for SGML on 2026-08-17
- Error **Hermes operation validation failed: Security research for YEC.F on 2026-08-22** — Hermes timed out after 1800s; agent result is missing or a symlink: data/runs/Daily report for 2026-09-07/Security research for YEC.F on 2026-08-22/agent\_result.json
- Error **Hermes operation validation failed: Security research for ANIC.L on 2026-07-29** — agent result schema: 'insufficient\_observations' is not one of \['single\_value', 'insufficient\_comparability', 'insufficient\_history', 'recorded source', 'not\_decision\_relevant', 'no\_page\_change'\]; post-run integrity: agent result data/runs/Daily report for 2026-09-09/Security research for ANIC.L on 2026-07-29/agent\_result.json: 'insufficient\_observations' is not one of \['single\_value', 'insufficient\_comparability', 'insufficient\_history', 'recorded source', 'not\_decision\_relevant', 'no\_page\_change'\]
- Error **ABBNY — ABB Ltd: ABB assessment provenance does not match corrected final research page** — Operation Security research for ABBNY on 2026-09-03 accepted immutable assessment assessment\_a3946a163695f1a9f51f while the security page still carried the prior prose disposition. Deterministic derivation changed the current disposition from Sell / Avoid to Hold / Watch at the lower mark, so the page and structured security summary were corrected after the immutable assessment was written. The current assessment and final page now agree economically, and exactly one assessment version names this operation, bu
- Error **Hermes operation validation failed: Security research for ABBNY on 2026-09-03** — files\_changed claims paths absent from the actual delta: \['data/operations/operations\_TODO.csv'\]
- Error **Hermes operation validation failed: Quick check research for TWST on 2026-08-05** — agent result was written before completed change: data/runs/Daily report for 2026-08-12/Quick check research for TWST on 2026-08-05/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **ASML — ASML Holding N.V.: ASML assessment rejected after security row update** — The retry operation refreshed the ASML page and security row to the 2026-08-19 USD 1,751.73 mark, but the schema-v2 assessment request was rejected before assessment state changed because valuation\_template\_rationale is a required field and was omitted. The routed-operation no-retry rule forbids correcting and invoking a second assessment request after this rejection. The canonical assessment therefore remains the prior unsupported version, the prepared relationship and idea follow-up requests w
- Error **WTI — W&amp;T Offshore, Inc.: Hermes operation validation failed: Quick check research for WTI on 2026-08-18** — completed security research requires this run's comparable assessment
- Warning **TCEHY — Tencent Holdings Limited: Daily preparation degraded: TCEHY** — TCEHY: ModuleNotFoundError: No module named 'scipy'
- Warning **HOOD — Robinhood Markets, Inc.: Daily preparation degraded: HOOD** — HOOD: ModuleNotFoundError: No module named 'scipy'
- Warning **AD — Koninklijke Ahold Delhaize N.V.: Daily preparation degraded: AD** — AD: ModuleNotFoundError: No module named 'scipy'
- Warning **CROX — Crocs, Inc.: Daily preparation degraded: CROX** — CROX: ModuleNotFoundError: No module named 'scipy'
- Warning **WTI — W&amp;T Offshore, Inc.: Daily preparation degraded: WTI** — WTI: ModuleNotFoundError: No module named 'scipy'
- Warning **FCX — Freeport-McMoRan Inc.: Daily preparation degraded: FCX** — FCX: ModuleNotFoundError: No module named 'scipy'
- Warning **DLO — DLocal Limited: Daily preparation degraded: DLO** — DLO: ModuleNotFoundError: No module named 'scipy'
- Warning **Daily preparation degraded: FX AUD/EUR** — FX AUD/EUR: ModuleNotFoundError: No module named 'scipy'
- Warning **ATKR — Atkore Inc.: Daily preparation degraded: ATKR** — ATKR: ModuleNotFoundError: No module named 'scipy'
- Warning **PLS.AX — PLS Group Limited: Daily preparation degraded: PLS.AX** — PLS.AX: ModuleNotFoundError: No module named 'scipy'
- Warning **GEV — GE Vernova Inc.: Daily preparation degraded: GEV** — GEV: ModuleNotFoundError: No module named 'scipy'
- Warning **XMTR — Xometry, Inc.: Daily preparation degraded: XMTR** — XMTR: ModuleNotFoundError: No module named 'scipy'
- Warning **Daily preparation degraded: FX USD/EUR** — FX USD/EUR: ModuleNotFoundError: No module named 'scipy'
- Warning **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Daily preparation degraded: KTOS** — KTOS: ModuleNotFoundError: No module named 'scipy'
- Warning **RIO — Rio Tinto plc: Daily preparation degraded: RIO** — RIO: ModuleNotFoundError: No module named 'scipy'
- Warning **SOFI — SoFi Technologies, Inc.: Daily preparation degraded: SOFI** — SOFI: ModuleNotFoundError: No module named 'scipy'
- Warning **TSLA — Tesla, Inc.: Daily preparation degraded: TSLA** — TSLA: ModuleNotFoundError: No module named 'scipy'
- Warning **CSL — Carlisle Companies Incorporated: Daily preparation degraded: CSL** — CSL: ModuleNotFoundError: No module named 'scipy'
- Warning **SGML — Sigma Lithium Corporation: Daily preparation degraded: SGML** — SGML: ModuleNotFoundError: No module named 'scipy'
- Warning **PYPL — PayPal Holdings, Inc.: Daily preparation degraded: PYPL** — PYPL: ModuleNotFoundError: No module named 'scipy'
- Warning **RKLB — Rocket Lab Corporation: Daily preparation degraded: RKLB** — RKLB: ModuleNotFoundError: No module named 'scipy'
- Warning **ETN — Eaton Corporation plc: Daily preparation degraded: ETN** — ETN: ModuleNotFoundError: No module named 'scipy'
- Warning **ISRG — Intuitive Surgical, Inc.: Daily preparation degraded: ISRG** — ISRG: ModuleNotFoundError: No module named 'scipy'
- Warning **INTC — Intel Corporation: Daily preparation degraded: INTC** — INTC: ModuleNotFoundError: No module named 'scipy'
- Warning **DPZ — Domino's Pizza, Inc.: Daily preparation degraded: DPZ** — DPZ: ModuleNotFoundError: No module named 'scipy'
- Warning **TWST — Twist Bioscience Corporation: Daily preparation degraded: TWST** — TWST: ModuleNotFoundError: No module named 'scipy'
- Warning **RBLX — Roblox Corporation: Daily preparation degraded: RBLX** — RBLX: ModuleNotFoundError: No module named 'scipy'
- Warning **FUC.F — Fanuc Corporation: Daily preparation degraded: FUC.F** — FUC.F: ModuleNotFoundError: No module named 'scipy'
- Warning **VALE — Vale S.A.: Daily preparation degraded: VALE** — VALE: ModuleNotFoundError: No module named 'scipy'
- Warning **DNA — Ginkgo Bioworks Holdings, Inc.: Daily preparation degraded: DNA** — DNA: ModuleNotFoundError: No module named 'scipy'
- Warning **EVK — Evonik Industries AG: Daily preparation degraded: EVK** — EVK: ModuleNotFoundError: No module named 'scipy'
- Warning **ANIC.L — Agronomics Limited: Daily preparation degraded: ANIC.L** — ANIC.L: ModuleNotFoundError: No module named 'scipy'
- Warning **GOOGL — Alphabet Inc.: Daily preparation degraded: GOOGL** — GOOGL: ModuleNotFoundError: No module named 'scipy'
- Warning **BE — Bloom Energy Corporation: Daily preparation degraded: BE** — BE: ModuleNotFoundError: No module named 'scipy'
- Warning **TXN — Texas Instruments Incorporated: Daily preparation degraded: TXN** — TXN: ModuleNotFoundError: No module named 'scipy'
- Warning **VLO — Valero Energy Corporation: Daily preparation degraded: VLO** — VLO: ModuleNotFoundError: No module named 'scipy'
- Warning **QCOM — QUALCOMM Incorporated: Daily preparation degraded: QCOM** — QCOM: ModuleNotFoundError: No module named 'scipy'
- Warning **MP — MP Materials Corp.: Daily preparation degraded: MP** — MP: ModuleNotFoundError: No module named 'scipy'
- Warning **ANET — Arista Networks, Inc.: Daily preparation degraded: ANET** — ANET: ModuleNotFoundError: No module named 'scipy'
- Warning **Daily preparation degraded: FX KRW/EUR** — FX KRW/EUR: ModuleNotFoundError: No module named 'scipy'
- Warning **108490 — ROBOTIS Co., Ltd.: Daily preparation degraded: 108490** — 108490: ModuleNotFoundError: No module named 'scipy'
- Warning **PARRO.PA — Parrot S.A.: Daily preparation degraded: PARRO.PA** — PARRO.PA: ModuleNotFoundError: No module named 'scipy'
- Warning **TSM — Taiwan Semiconductor Manufacturing Company Limited: Daily preparation degraded: TSM** — TSM: ModuleNotFoundError: No module named 'scipy'
- Warning **PL — Planet Labs PBC: Daily preparation degraded: PL** — PL: ModuleNotFoundError: No module named 'scipy'
- Warning **PATH — UiPath, Inc.: Daily preparation degraded: PATH** — PATH: ModuleNotFoundError: No module named 'scipy'
- Warning **ABCL — AbCellera Biologics Inc.: Daily preparation degraded: ABCL** — ABCL: ModuleNotFoundError: No module named 'scipy'
- Warning **RTX — RTX Corporation: Daily preparation degraded: RTX** — RTX: ModuleNotFoundError: No module named 'scipy'
- Warning **ENPH — Enphase Energy, Inc.: Daily preparation degraded: ENPH** — ENPH: ModuleNotFoundError: No module named 'scipy'
- Warning **Daily preparation degraded: FX HKD/EUR** — FX HKD/EUR: ModuleNotFoundError: No module named 'scipy'
- Warning **LUNR — Intuitive Machines, Inc.: Daily preparation degraded: LUNR** — LUNR: ModuleNotFoundError: No module named 'scipy'
- Warning **MSTR — Strategy Inc: Daily preparation degraded: MSTR** — MSTR: ModuleNotFoundError: No module named 'scipy'
- Warning **MTLS — Materialise NV: Daily preparation degraded: MTLS** — MTLS: ModuleNotFoundError: No module named 'scipy'
- Warning **SPCX — Space Exploration Technologies Corp.: Daily preparation degraded: SPCX** — SPCX: ModuleNotFoundError: No module named 'scipy'
- Warning **NBIS — Nebius Group N.V.: Daily preparation degraded: NBIS** — NBIS: ModuleNotFoundError: No module named 'scipy'
- Warning **CRWD — CrowdStrike Holdings, Inc.: Daily preparation degraded: CRWD** — CRWD: ModuleNotFoundError: No module named 'scipy'
- Warning **SSU.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: SSU.VI** — SSU.VI: ModuleNotFoundError: No module named 'scipy'
- Warning **ASML — ASML Holding N.V.: Daily preparation degraded: ASML** — ASML: ModuleNotFoundError: No module named 'scipy'
- Warning **SU — Schneider Electric SE: Daily preparation degraded: SU** — SU: ModuleNotFoundError: No module named 'scipy'
- Warning **Daily preparation degraded: FX GBP/EUR** — FX GBP/EUR: ModuleNotFoundError: No module named 'scipy'
- Warning **LH — Labcorp Holdings Inc.: Daily preparation degraded: LH** — LH: ModuleNotFoundError: No module named 'scipy'
- Warning **TX — Ternium S.A.: Daily preparation degraded: TX** — TX: ModuleNotFoundError: No module named 'scipy'
- Warning **YEC.F — YASKAWA Electric Corporation: Daily preparation degraded: YEC.F** — YEC.F: ModuleNotFoundError: No module named 'scipy'
- Warning **META — Meta Platforms, Inc.: Daily preparation degraded: META** — META: ModuleNotFoundError: No module named 'scipy'
- Warning **VRT — Vertiv Holdings Co: Daily preparation degraded: VRT** — VRT: ModuleNotFoundError: No module named 'scipy'
- Warning **CRSR — Corsair Gaming, Inc.: Daily preparation degraded: CRSR** — CRSR: ModuleNotFoundError: No module named 'scipy'
- Warning **RXRX — Recursion Pharmaceuticals, Inc.: Daily preparation degraded: RXRX** — RXRX: ModuleNotFoundError: No module named 'scipy'
- Warning **SCCO — Southern Copper Corporation: Daily preparation degraded: SCCO** — SCCO: ModuleNotFoundError: No module named 'scipy'
- Warning **MSFT — Microsoft Corporation: Daily preparation degraded: MSFT** — MSFT: ModuleNotFoundError: No module named 'scipy'
- Warning **ABBNY — ABB Ltd: Daily preparation degraded: ABBNY** — ABBNY: ModuleNotFoundError: No module named 'scipy'
- Warning **SSUN.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: SSUN.VI** — SSUN.VI: ModuleNotFoundError: No module named 'scipy'
- Warning **PRLB — Proto Labs, Inc.: Daily preparation degraded: PRLB** — PRLB: ModuleNotFoundError: No module named 'scipy'
- Warning **UBER — Uber Technologies, Inc.: Daily preparation degraded: UBER** — UBER: ModuleNotFoundError: No module named 'scipy'
- Warning **PRX — Prosus N.V.: Daily preparation degraded: PRX** — PRX: ModuleNotFoundError: No module named 'scipy'
- Warning **FISV — Fiserv, Inc.: Daily preparation degraded: FISV** — FISV: ModuleNotFoundError: No module named 'scipy'
- Warning **TDY — Teledyne Technologies Incorporated: Daily preparation degraded: TDY** — TDY: ModuleNotFoundError: No module named 'scipy'
- Warning **PWR — Quanta Services, Inc.: Daily preparation degraded: PWR** — PWR: ModuleNotFoundError: No module named 'scipy'
- Warning **PLTR — Palantir Technologies Inc.: Daily preparation degraded: PLTR** — PLTR: ModuleNotFoundError: No module named 'scipy'
- Warning **AMAT — Applied Materials, Inc.: Daily preparation degraded: AMAT** — AMAT: ModuleNotFoundError: No module named 'scipy'
- Warning **BAS — BASF SE: Daily preparation degraded: BAS** — BAS: ModuleNotFoundError: No module named 'scipy'
- Warning **NIB.F — Nidec Corporation: Daily preparation degraded: NIB.F** — NIB.F: ModuleNotFoundError: No module named 'scipy'
- Warning **NOMD — Nomad Foods Limited: Daily preparation degraded: NOMD** — NOMD: ModuleNotFoundError: No module named 'scipy'
- Warning **COIN — Coinbase Global, Inc.: Daily preparation degraded: COIN** — COIN: ModuleNotFoundError: No module named 'scipy'
- Warning **CSIQ — Canadian Solar Inc.: Daily preparation degraded: CSIQ** — CSIQ: ModuleNotFoundError: No module named 'scipy'
- Warning **03388 — Shenzhen Creality 3D Technology Co., Ltd.: Daily preparation degraded: 03388** — 03388: ModuleNotFoundError: No module named 'scipy'
- Warning **POWL — Powell Industries, Inc.: Daily preparation degraded: POWL** — POWL: ModuleNotFoundError: No module named 'scipy'
- Warning **AMZN — Amazon.com, Inc.: Daily preparation degraded: AMZN** — AMZN: ModuleNotFoundError: No module named 'scipy'
- Warning **ALB — Albemarle Corporation: Daily preparation degraded: ALB** — ALB: ModuleNotFoundError: No module named 'scipy'
- Warning **SQM — Sociedad Quimica y Minera de Chile S.A.: Daily preparation degraded: SQM** — SQM: ModuleNotFoundError: No module named 'scipy'
- Warning **SPOT — Spotify Technology S.A.: Daily preparation degraded: SPOT** — SPOT: ModuleNotFoundError: No module named 'scipy'
- Warning **AKE — Arkema S.A.: Daily preparation degraded: AKE** — AKE: ModuleNotFoundError: No module named 'scipy'
- Warning **FLNC — Fluence Energy, Inc.: Daily preparation degraded: FLNC** — FLNC: ModuleNotFoundError: No module named 'scipy'
- Warning **LAC — Lithium Americas Corp.: Daily preparation degraded: LAC** — LAC: ModuleNotFoundError: No module named 'scipy'
- Warning **DDD — 3D Systems Corporation: Daily preparation degraded: DDD** — DDD: ModuleNotFoundError: No module named 'scipy'
- Warning **MELI — MercadoLibre, Inc.: Daily preparation degraded: MELI** — MELI: ModuleNotFoundError: No module named 'scipy'
- Warning **NVDA — NVIDIA Corporation: Daily preparation degraded: NVDA** — NVDA: ModuleNotFoundError: No module named 'scipy'
- Warning **SSYS — Stratasys Ltd.: Daily preparation degraded: SSYS** — SSYS: ModuleNotFoundError: No module named 'scipy'

### Publication Only (6)

- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — Hermes timed out after 1200s; agent result was written before completed change: data/runs/Daily report for 2026-08-17/Daily podcast for Daily report for 2026-08-17 on 2026-08-17/command\_audit.json; commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — commands\_run does not exactly match deterministic CLI audit receipts
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-05 on 2026-08-05** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/Daily report for 2026-08-05/Daily podcast for Daily report for 2026-08-05 on 2026-08-05/agent\_result.json
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-06 on 2026-08-06** — cannot restore rejected path data/wiki/daily-reports/daily-report\_20260806.md: pre-run path cannot be restored because Git metadata is unavailable; daily podcast spoken transcript must label paper trading
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-08-17 on 2026-08-17** — non-successful daily podcast must not retain a transcript page
- Error **Hermes operation validation failed: Daily podcast for Daily report for 2026-09-06 on 2026-09-06** — Hermes exited with status 1; agent result is missing or a symlink: data/runs/Daily report for 2026-09-06/Daily podcast for Daily report for 2026-09-06 on 2026-09-06/agent\_result.json

## Historical audit health

- Resolved and superseded incidents remain visible in canonical issue and operation history.
- No unresolved issue is hidden or aged out.

## Audit links

- [[research-catalog|Complete research catalog]]
- [[security-catalog|Tracked securities]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]
