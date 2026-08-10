---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-08-10"
updated: "2026-08-10"
provenance: deterministic-decision-projection
snapshot_id: "decision_008cd109f31b5035709b"
as_of: "2026-08-10T17:35:48Z"
---

# System status and audit

**As of:** `2026-08-10T17:35:48Z`
**Investment data:** Degraded — review investment data gaps
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

## Coverage

- Assessments: 68/68
- Fresh-evidence assessments: 68/68
- Relationship reviews: 25/68
- Accepted relationships: 22
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market success/failure: 71/1
- Candidate FX gaps: 0
- Research backlog: 335
- Last successful daily run: 2026-08-10

## Current issues by investment impact

### Affects Candidate

- Error **DNA — Ginkgo Bioworks Holdings, Inc.: Local harness operation validation failed: [[securities/security_95351d928b674bbdf687|Quick check research for DNA on 2026-08-07]]** — completed security research requires exactly one immutable assessment version; files_changed contains an unchanged old value: data/wiki/log.md; files_changed contains an unchanged old value: data/wiki/research-catalog.md; files_changed is stale or incomplete: reported=['data/runs/[[daily-reports/daily-report_20260807|Daily report for 2026-08-07]]/[[securities/security_95351d928b674bbdf687|Quick check research for DNA on 2026-08-07]]/assessment_upsert_request.json', 'data/runs/[[daily-reports/daily-report_20260807|Daily report for 2026-08-07]]/[[securities/security_95351d928b674bbdf687|Quick check research for DNA on 2026-08-07]]/assessment_upsert_retry01_request.json', 'data/runs/local-daily
- Error **RIO — Rio Tinto plc: Rio Tinto assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_1c055eb9b2bb1f5a8ff2|RIO]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_1c055eb9b2bb1f5a8ff2|Quick check research for RIO on 2026-08-03]] and current security_research [[securities/security_1c055eb9b2bb1f5a8ff2|Security research for RIO on 2026-08-05]] claimed by run gha-30798126914-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- Error **ABBNY — ABB Ltd: ABB assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_c120e9f26ebb6159adf9|ABBNY]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_c120e9f26ebb6159adf9|Quick check research for ABBNY on 2026-08-09]] and current security_research [[securities/security_c120e9f26ebb6159adf9|Security research for ABBNY on 2026-08-10]] claimed by run [[daily-reports/daily-report_20260809|Daily report for 2026-08-09]] and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- Error **RBLX — Roblox Corporation: Assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_c9a37d277445869a8809|RBLX]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_c9a37d277445869a8809|Quick check research for RBLX on 2026-08-03]] and current security_research [[securities/security_c9a37d277445869a8809|Security research for RBLX on 2026-08-03]] claimed by run gha-30793143744-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- Error **LUNR — Intuitive Machines, Inc.: Intuitive Machines assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_a5dc16f3f4b245e6c168|LUNR]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_a5dc16f3f4b245e6c168|Quick check research for LUNR on 2026-08-08]] and current security_research [[securities/security_a5dc16f3f4b245e6c168|Security research for LUNR on 2026-08-08]] claimed by run [[daily-reports/daily-report_20260808|Daily report for 2026-08-08]] and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- Error **PWR — Quanta Services, Inc.: Assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_488a9d7f7a8573597724|PWR]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_488a9d7f7a8573597724|Quick check research for PWR on 2026-08-03]] and current security_research [[securities/security_488a9d7f7a8573597724|Security research for PWR on 2026-08-03]] claimed by run gha-30788518712-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- Error **Hermes operation validation failed: [[securities/security_7bf8f4c9cc12ae410e40|Security research for ABCL on 2026-08-07]]** — completed security research requires exactly one immutable assessment version
- Error **Hermes operation validation failed: [[securities/security_66cdcf90aac0d83e76f3|Quick check research for ALB on 2026-08-09]]** — Hermes timed out after 600s; agent result was written before completed change: data/runs/[[daily-reports/daily-report_20260809|Daily report for 2026-08-09]]/[[securities/security_66cdcf90aac0d83e76f3|Quick check research for ALB on 2026-08-09]]/command_audit.json; commands_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment
- Error **Local harness operation validation failed: [[securities/security_4627aea1bf7d8943d3d8|Quick check research for SGML on 2026-08-06]]** — completed security research requires exactly one immutable assessment version
- Error **Hermes operation validation failed: [[securities/security_c9a37d277445869a8809|Quick check research for RBLX on 2026-08-05]]** — agent result schema: Additional properties are not allowed ('operation_id' was unexpected); agent result schema: Additional properties are not allowed ('source_ref' was unexpected); agent result schema: Additional properties are not allowed ('source_refs' was unexpected); commands_run does not exactly match deterministic CLI audit receipts; completed security research requires this run's comparable assessment; post-run integrity: agent result data/runs/[[daily-reports/daily-report_20260810|Daily report for 2026-08-10]]/01KZ9ZJVERX5NYGBGE6Z
- Error **COIN — Coinbase Global, Inc.: Coinbase assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_37ddcbdaad296ad831f2|COIN]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_37ddcbdaad296ad831f2|Quick check research for COIN on 2026-08-09]] and current security_research [[securities/security_37ddcbdaad296ad831f2|Security research for COIN on 2026-08-09]] claimed by run [[daily-reports/daily-report_20260809|Daily report for 2026-08-09]] and rejects more than one same-security source operation as ambiguous. The assessment request has no source-operation selector, so this routed operation cannot repair provenance without an out-of-scope code 
- Error **RKLB — Rocket Lab Corporation: Rocket Lab assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_7ca095d63423c55a90e3|RKLB]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_7ca095d63423c55a90e3|Quick check research for RKLB on 2026-08-09]] and current security_research [[securities/security_7ca095d63423c55a90e3|Security research for RKLB on 2026-08-09]] claimed by run [[daily-reports/daily-report_20260809|Daily report for 2026-08-09]] and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- Error **Hermes operation validation failed: [[securities/security_1e8fbdb0f45f2b413e00|Quick check research for PYPL on 2026-08-08]]** — repeat security research page requires a Changes since prior review section
- Error **RTX — RTX Corporation: RTX assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_59304f90c440def31dc5|RTX]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_59304f90c440def31dc5|Quick check research for RTX on 2026-08-05]] and current security_research [[securities/security_59304f90c440def31dc5|Security research for RTX on 2026-08-06]] claimed by run [[daily-reports/daily-report_20260805|Daily report for 2026-08-05]] and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- Error **PL — Planet Labs PBC: Planet Labs assessment source operation is ambiguous within one run** — The required schema-v2 assessment for [[securities/security_97f38b2cb2d5ef127f5a|PL]] could not be written. The deterministic assessment applier found both predecessor quick_check_research [[securities/security_97f38b2cb2d5ef127f5a|Quick check research for PL on 2026-08-09]] and current security_research [[securities/security_97f38b2cb2d5ef127f5a|Security research for PL on 2026-08-09]] claimed by run [[daily-reports/daily-report_20260809|Daily report for 2026-08-09]] and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- Warning **LAC — Lithium Americas Corp.: Daily preparation degraded: [[securities/security_fb87fac302a5446a1ced|LAC]]** — [[securities/security_fb87fac302a5446a1ced|LAC]]: YFTzMissingError: $LAC: possibly delisted; no timezone found
- Warning **HOOD — Robinhood Markets, Inc.: Daily preparation degraded: [[securities/security_ad3b1f8f59fd599f079a|HOOD]]** — [[securities/security_ad3b1f8f59fd599f079a|HOOD]]: price cache is empty
- Warning **CROX — Crocs, Inc.: Daily preparation degraded: [[securities/security_c150f31c30afdb4a85f9|CROX]]** — [[securities/security_c150f31c30afdb4a85f9|CROX]]: price cache is empty
- Warning **WTI — W&T Offshore, Inc.: Daily preparation degraded: [[securities/security_61567714298b9563d1a9|WTI]]** — [[securities/security_61567714298b9563d1a9|WTI]]: price cache is empty
- Warning **FCX — Freeport-McMoRan Inc.: Daily preparation degraded: [[securities/security_2dbe878dfc899d7ee867|FCX]]** — [[securities/security_2dbe878dfc899d7ee867|FCX]]: YFTzMissingError: $FCX: possibly delisted; no timezone found
- Warning **DLO — DLocal Limited: Daily preparation degraded: [[securities/security_715bde20b6e1e1320c1a|DLO]]** — [[securities/security_715bde20b6e1e1320c1a|DLO]]: price cache is empty
- Warning **TX — Ternium S.A.: Daily preparation degraded: [[securities/security_2c779e81c27b78c556bb|TX]]** — [[securities/security_2c779e81c27b78c556bb|TX]]: YFTzMissingError: $TX: possibly delisted; no timezone found
- Warning **GEV — GE Vernova Inc.: Daily preparation degraded: [[securities/security_4b61970aa8f574446819|GEV]]** — [[securities/security_4b61970aa8f574446819|GEV]]: YFTzMissingError: $GEV: possibly delisted; no timezone found
- Warning **ATKR — Atkore Inc.: Daily preparation degraded: [[securities/security_22c2b9d782a62d7a9b86|ATKR]]** — [[securities/security_22c2b9d782a62d7a9b86|ATKR]]: YFTzMissingError: $ATKR: possibly delisted; no timezone found
- Warning **PLS.AX — PLS Group Limited: Daily preparation degraded: [[security-catalog#security-security_8a5c43888d224de85c69|PLS.AX]]** — [[security-catalog#security-security_8a5c43888d224de85c69|PLS.AX]]: price cache is empty
- Warning **KTOS — Kratos Defense & Security Solutions, Inc.: Daily preparation degraded: [[securities/security_0cf8075039299094d614|KTOS]]** — [[securities/security_0cf8075039299094d614|KTOS]]: price cache is empty
- Warning **RIO — Rio Tinto plc: Daily preparation degraded: [[securities/security_1c055eb9b2bb1f5a8ff2|RIO]]** — [[securities/security_1c055eb9b2bb1f5a8ff2|RIO]]: YFTzMissingError: $RIO: possibly delisted; no timezone found
- Warning **PYPL — PayPal Holdings, Inc.: Daily preparation degraded: [[securities/security_1e8fbdb0f45f2b413e00|PYPL]]** — [[securities/security_1e8fbdb0f45f2b413e00|PYPL]]: price cache is empty
- Warning **ETN — Eaton Corporation plc: Daily preparation degraded: [[securities/security_18a3ab0ee6086ee85d0f|ETN]]** — [[securities/security_18a3ab0ee6086ee85d0f|ETN]]: YFTzMissingError: $ETN: possibly delisted; no timezone found
- Warning **SOFI — SoFi Technologies, Inc.: Daily preparation degraded: [[securities/security_98470cfc01bbcde78fc2|SOFI]]** — [[securities/security_98470cfc01bbcde78fc2|SOFI]]: price cache is empty
- Warning **CSL — Carlisle Companies Incorporated: Daily preparation degraded: [[securities/security_9b0db3bc77914b23a307|CSL]]** — [[securities/security_9b0db3bc77914b23a307|CSL]]: price cache is empty
- Warning **SGML — Sigma Lithium Corporation: Daily preparation degraded: [[securities/security_4627aea1bf7d8943d3d8|SGML]]** — [[securities/security_4627aea1bf7d8943d3d8|SGML]]: YFTzMissingError: $SGML: possibly delisted; no timezone found
- Warning **RKLB — Rocket Lab Corporation: Daily preparation degraded: [[securities/security_7ca095d63423c55a90e3|RKLB]]** — [[securities/security_7ca095d63423c55a90e3|RKLB]]: YFTzMissingError: $RKLB: possibly delisted; no timezone found
- Warning **ISRG — Intuitive Surgical, Inc.: Daily preparation degraded: [[securities/security_1f9cce545ede94cd6349|ISRG]]** — [[securities/security_1f9cce545ede94cd6349|ISRG]]: YFTzMissingError: $ISRG: possibly delisted; no timezone found
- Warning **INTC — Intel Corporation: Daily preparation degraded: [[securities/security_dfa34d4b9050964b465e|INTC]]** — [[securities/security_dfa34d4b9050964b465e|INTC]]: price cache is empty
- Warning **TWST — Twist Bioscience Corporation: Daily preparation degraded: [[securities/security_6cf75bd0ec0aa2a20148|TWST]]** — [[securities/security_6cf75bd0ec0aa2a20148|TWST]]: price cache is empty
- Warning **RBLX — Roblox Corporation: Daily preparation degraded: [[securities/security_c9a37d277445869a8809|RBLX]]** — [[securities/security_c9a37d277445869a8809|RBLX]]: YFTzMissingError: $RBLX: possibly delisted; no timezone found
- Warning **FUC.F — Fanuc Corporation: Daily preparation degraded: [[securities/security_96ba305ee7cd586bc348|FUC.F]]** — [[securities/security_96ba305ee7cd586bc348|FUC.F]]: price cache is empty
- Warning **TSLA — Tesla, Inc.: Daily preparation degraded: [[securities/security_dc7a111e297be528d96b|TSLA]]** — [[securities/security_dc7a111e297be528d96b|TSLA]]: price cache is empty
- Warning **VALE — Vale S.A.: Daily preparation degraded: [[security-catalog#security-security_b2116dcf976c96974d7b|VALE]]** — [[security-catalog#security-security_b2116dcf976c96974d7b|VALE]]: price cache is empty
- Warning **ALB — Albemarle Corporation: Daily preparation degraded: [[securities/security_66cdcf90aac0d83e76f3|ALB]]** — [[securities/security_66cdcf90aac0d83e76f3|ALB]]: YFTzMissingError: $ALB: possibly delisted; no timezone found
- Warning **ANIC.L — Agronomics Limited: Daily preparation degraded: [[security-catalog#security-security_fe4648901e7675f157fd|ANIC.L]]** — [[security-catalog#security-security_fe4648901e7675f157fd|ANIC.L]]: price cache is empty
- Warning **GOOGL — Alphabet Inc.: Daily preparation degraded: [[securities/security_c86bb4e75658c07142cf|GOOGL]]** — [[securities/security_c86bb4e75658c07142cf|GOOGL]]: price cache is empty
- Warning **ABCL — AbCellera Biologics Inc.: Daily preparation degraded: [[securities/security_7bf8f4c9cc12ae410e40|ABCL]]** — [[securities/security_7bf8f4c9cc12ae410e40|ABCL]]: price cache is empty
- Warning **TXN — Texas Instruments Incorporated: Daily preparation degraded: [[securities/security_83a56943e18793f685b0|TXN]]** — [[securities/security_83a56943e18793f685b0|TXN]]: price cache is empty
- Warning **VLO — Valero Energy Corporation: Daily preparation degraded: [[security-catalog#security-security_c5a9e460d3350284d157|VLO]]** — [[security-catalog#security-security_c5a9e460d3350284d157|VLO]]: price cache is empty
- Warning **QCOM — QUALCOMM Incorporated: Daily preparation degraded: [[securities/security_3a75fc1ccca2ee7c937a|QCOM]]** — [[securities/security_3a75fc1ccca2ee7c937a|QCOM]]: price cache is empty
- Warning **MP — MP Materials Corp.: Daily preparation degraded: [[securities/security_cd492d97064d8574156e|MP]]** — [[securities/security_cd492d97064d8574156e|MP]]: price cache is empty
- Warning **ANET — Arista Networks, Inc.: Daily preparation degraded: [[securities/security_6f9a1450edceb9307c9a|ANET]]** — [[securities/security_6f9a1450edceb9307c9a|ANET]]: YFTzMissingError: $ANET: possibly delisted; no timezone found
- Warning **PARRO.PA — Parrot S.A.: Daily preparation degraded: [[securities/security_cc4dcb8f002b61dffe00|PARRO.PA]]** — [[securities/security_cc4dcb8f002b61dffe00|PARRO.PA]]: YFTzMissingError: $PARRO.PA: possibly delisted; no timezone found
- Warning **TSM — Taiwan Semiconductor Manufacturing Company Limited: Daily preparation degraded: [[securities/security_ce9b78a4d0773c950765|TSM]]** — [[securities/security_ce9b78a4d0773c950765|TSM]]: price cache is empty
- Warning **PATH — UiPath, Inc.: Daily preparation degraded: [[securities/security_eca976f0076a425ea1bb|PATH]]** — [[securities/security_eca976f0076a425ea1bb|PATH]]: price cache is empty
- Warning **RTX — RTX Corporation: Daily preparation degraded: [[securities/security_59304f90c440def31dc5|RTX]]** — [[securities/security_59304f90c440def31dc5|RTX]]: YFTzMissingError: $RTX: possibly delisted; no timezone found
- Warning **ASML — ASML Holding N.V.: Daily preparation degraded: [[securities/security_ef35e41886220d51c22c|ASML]]** — [[securities/security_ef35e41886220d51c22c|ASML]]: price cache is empty
- Warning **ENPH — Enphase Energy, Inc.: Daily preparation degraded: [[securities/security_f2b9760d847b2ba59324|ENPH]]** — [[securities/security_f2b9760d847b2ba59324|ENPH]]: YFTzMissingError: $ENPH: possibly delisted; no timezone found
- Warning **MSTR — Strategy Inc: Daily preparation degraded: [[securities/security_fe5539a7d3fd9d553bce|MSTR]]** — [[securities/security_fe5539a7d3fd9d553bce|MSTR]]: price cache is empty
- Warning **SPCX — Space Exploration Technologies Corp.: Daily preparation degraded: [[securities/security_664f93a7eaca72e76e9b|SPCX]]** — [[securities/security_664f93a7eaca72e76e9b|SPCX]]: price cache is empty
- Warning **NBIS — Nebius Group N.V.: Daily preparation degraded: [[securities/security_47a0b06f6c6c478d7c1e|NBIS]]** — [[securities/security_47a0b06f6c6c478d7c1e|NBIS]]: price cache is empty
- Warning **CRWD — CrowdStrike Holdings, Inc.: Daily preparation degraded: [[securities/security_8472507d7d320aa388a7|CRWD]]** — [[securities/security_8472507d7d320aa388a7|CRWD]]: YFTzMissingError: $CRWD: possibly delisted; no timezone found
- Warning **SQM — Sociedad Quimica y Minera de Chile S.A.: Daily preparation degraded: [[securities/security_9d4049ed6669a52815d6|SQM]]** — [[securities/security_9d4049ed6669a52815d6|SQM]]: YFTzMissingError: $SQM: possibly delisted; no timezone found
- Warning **YEC.F — YASKAWA Electric Corporation: Daily preparation degraded: [[securities/security_89969b7dac39b7db5661|YEC.F]]** — [[securities/security_89969b7dac39b7db5661|YEC.F]]: price cache is empty
- Warning **META — Meta Platforms, Inc.: Daily preparation degraded: [[securities/security_d12e746b3c9d392183cc|META]]** — [[securities/security_d12e746b3c9d392183cc|META]]: price cache is empty
- Warning **RXRX — Recursion Pharmaceuticals, Inc.: Daily preparation degraded: [[securities/security_ed7d5b616a196969c815|RXRX]]** — [[securities/security_ed7d5b616a196969c815|RXRX]]: YFTzMissingError: $RXRX: possibly delisted; no timezone found
- Warning **SCCO — Southern Copper Corporation: Daily preparation degraded: [[securities/security_6ad1af8d10d6276a0221|SCCO]]** — [[securities/security_6ad1af8d10d6276a0221|SCCO]]: MarketDataError: provider returned no valid sessions for [[securities/security_6ad1af8d10d6276a0221|SCCO]]
- Warning **MSFT — Microsoft Corporation: Daily preparation degraded: [[securities/security_204be2a44063993de1a8|MSFT]]** — [[securities/security_204be2a44063993de1a8|MSFT]]: price cache is empty
- Warning **ABBNY — ABB Ltd: Daily preparation degraded: [[securities/security_c120e9f26ebb6159adf9|ABBNY]]** — [[securities/security_c120e9f26ebb6159adf9|ABBNY]]: YFTzMissingError: $ABBNY: possibly delisted; no timezone found
- Warning **SSUN.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: [[securities/security_d08d763780400dfbffce|SSUN.VI]]** — [[securities/security_d08d763780400dfbffce|SSUN.VI]]: price cache is empty
- Warning **VRT — Vertiv Holdings Co: Daily preparation degraded: [[securities/security_cb88f9154cfeaa15e878|VRT]]** — [[securities/security_cb88f9154cfeaa15e878|VRT]]: price cache is empty
- Warning **LH — Labcorp Holdings Inc.: Daily preparation degraded: [[securities/security_b1f2c48e1a744f5ecf67|LH]]** — [[securities/security_b1f2c48e1a744f5ecf67|LH]]: price cache is empty
- Warning **PL — Planet Labs PBC: Daily preparation degraded: [[securities/security_97f38b2cb2d5ef127f5a|PL]]** — [[securities/security_97f38b2cb2d5ef127f5a|PL]]: price cache is empty
- Warning **TDY — Teledyne Technologies Incorporated: Daily preparation degraded: [[securities/security_ad5917642acbba28c1f2|TDY]]** — [[securities/security_ad5917642acbba28c1f2|TDY]]: price cache is empty
- Warning **PLTR — Palantir Technologies Inc.: Daily preparation degraded: [[securities/security_bdc2f87dadf134760c3a|PLTR]]** — [[securities/security_bdc2f87dadf134760c3a|PLTR]]: YFTzMissingError: $PLTR: possibly delisted; no timezone found
- Warning **AMAT — Applied Materials, Inc.: Daily preparation degraded: [[securities/security_0a56aa634d077fe5796f|AMAT]]** — [[securities/security_0a56aa634d077fe5796f|AMAT]]: price cache is empty
- Warning **NIB.F — Nidec Corporation: Daily preparation degraded: [[securities/security_3853e54c619d597dcaa1|NIB.F]]** — [[securities/security_3853e54c619d597dcaa1|NIB.F]]: price cache is empty
- Warning **LUNR — Intuitive Machines, Inc.: Daily preparation degraded: [[securities/security_a5dc16f3f4b245e6c168|LUNR]]** — [[securities/security_a5dc16f3f4b245e6c168|LUNR]]: price cache is empty
- Warning **COIN — Coinbase Global, Inc.: Daily preparation degraded: [[securities/security_37ddcbdaad296ad831f2|COIN]]** — [[securities/security_37ddcbdaad296ad831f2|COIN]]: YFTzMissingError: $COIN: possibly delisted; no timezone found
- Warning **DNA — Ginkgo Bioworks Holdings, Inc.: Daily preparation degraded: [[securities/security_95351d928b674bbdf687|DNA]]** — [[securities/security_95351d928b674bbdf687|DNA]]: price cache is empty
- Warning **CSIQ — Canadian Solar Inc.: Daily preparation degraded: [[securities/security_099561384c0f5e697727|CSIQ]]** — [[securities/security_099561384c0f5e697727|CSIQ]]: price cache is empty
- Warning **AMZN — Amazon.com, Inc.: Daily preparation degraded: [[securities/security_2433a056eb0c55961fcc|AMZN]]** — [[securities/security_2433a056eb0c55961fcc|AMZN]]: price cache is empty
- Warning **SPOT — Spotify Technology S.A.: Daily preparation degraded: [[securities/security_2010347f1a0a5ea60f47|SPOT]]** — [[securities/security_2010347f1a0a5ea60f47|SPOT]]: price cache is empty
- Warning **SSU.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: [[securities/security_567d0d575bbd30aaa91d|SSU.VI]]** — [[securities/security_567d0d575bbd30aaa91d|SSU.VI]]: price cache is empty
- Warning **FLNC — Fluence Energy, Inc.: Daily preparation degraded: [[securities/security_a9eb9838940ef5ceaa0c|FLNC]]** — [[securities/security_a9eb9838940ef5ceaa0c|FLNC]]: YFTzMissingError: $FLNC: possibly delisted; no timezone found
- Warning **CRSR — Corsair Gaming, Inc.: Daily preparation degraded: [[securities/security_55c9ce2fdcd32dad6b8c|CRSR]]** — [[securities/security_55c9ce2fdcd32dad6b8c|CRSR]]: price cache is empty
- Warning **NVDA — NVIDIA Corporation: Daily preparation degraded: [[securities/security_33d9c44facc75c726c7d|NVDA]]** — [[securities/security_33d9c44facc75c726c7d|NVDA]]: price cache is empty

### Operational Only

- Error **Hermes operation validation failed: [[daily-reports/daily-report_20260806|Daily podcast for Daily report for 2026-08-06 on 2026-08-06]]** — Committed Telegram delivery is awaiting a bounded retry.
- Error **Hermes operation validation failed: [[securities/security_1c055eb9b2bb1f5a8ff2|Security research for RIO on 2026-08-05]]** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/[[daily-reports/daily-report_20260805|Daily report for 2026-08-05]]/[[securities/security_1c055eb9b2bb1f5a8ff2|Security research for RIO on 2026-08-05]]/agent_result.json
- Error **Hermes operation validation failed: [[daily-reports/daily-report_20260805|Daily podcast for Daily report for 2026-08-05 on 2026-08-05]]** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/[[daily-reports/daily-report_20260805|Daily report for 2026-08-05]]/[[daily-reports/daily-report_20260805|Daily podcast for Daily report for 2026-08-05 on 2026-08-05]]/agent_result.json
- Error **Hermes operation validation failed: [[securities/security_89969b7dac39b7db5661|Quick check research for YEC.F on 2026-08-05]]** — Hermes timed out after 1800s; agent result is missing or a symlink: data/runs/[[daily-reports/daily-report_20260810|Daily report for 2026-08-10]]/[[securities/security_89969b7dac39b7db5661|Quick check research for YEC.F on 2026-08-05]]/agent_result.json
- Error **Hermes operation validation failed: [[daily-reports/daily-report_20260806|Daily podcast for Daily report for 2026-08-06 on 2026-08-06]]** — Committed Telegram delivery is awaiting a bounded retry.
- Warning **Daily preparation degraded: FX AUD/EUR** — FX AUD/EUR: YFTzMissingError: $AUDEUR=X: possibly delisted; no timezone found
- Warning **YouTube discovery failed for UCrTTBSUr0zhPU56UQljag5A** — @Value-Investing: 4JmCb5FmTA4 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html
- Warning **YouTube discovery failed for UCOOSDCjFzHfnGoV8iNLC65A** — @ConnectingODots: Ejsft2oPCtM This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html
- Warning **Daily preparation degraded: FX USD/EUR** — FX USD/EUR: YFTzMissingError: $USDEUR=X: possibly delisted; no timezone found
- Warning **Daily podcast failed: [[daily-reports/daily-report_20260806|Daily report for 2026-08-06]]** — Committed Telegram delivery is awaiting a bounded retry.
- Warning **YouTube discovery failed for UCS01CiRDAiyhR_mTHXDW23A** — @DumbMoneyLive: u-AXyF9kY9k This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html
- Warning **YouTube discovery failed for UCIFn7ONIJHyC-lMnb7Fm_jw** — @thelimitingfactor: SuSYegb8iK0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html
- Warning **Daily podcast failed: [[daily-reports/daily-report_20260806|Daily report for 2026-08-06]]** — Committed Telegram delivery is awaiting a bounded retry.
- Warning **Daily preparation degraded: FX GBP/EUR** — FX GBP/EUR: YFTzMissingError: $GBPEUR=X: possibly delisted; no timezone found
- Warning **YouTube discovery failed for UCrGLm-Drgv0vbbemwwHeXJw** — @CouchInvestor: MsNPz0dBYDw This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html
- Warning **Daily podcast failed: [[daily-reports/daily-report_20260805|Daily report for 2026-08-05]]** — Committed Telegram delivery is awaiting a bounded retry.
- Warning **YouTube discovery failed for UCESLZhusAkFfsNsApnjF_Cg** — @allin: TqNiSTeNtb0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po_token.html

## Bounded active operation queue

Showing 20 of 335 active operations.

<details><summary>Active research work</summary>

- Ready — [[security-catalog#security-security_8a5c43888d224de85c69|Security research for PLS.AX on 2026-07-29]]
- Ready — [[security-catalog#security-security_b2116dcf976c96974d7b|Security research for VALE on 2026-07-29]]
- Ready — [[security-catalog#security-security_fe4648901e7675f157fd|Security research for ANIC.L on 2026-07-29]]
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=9ePWIYadju4)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=J2ZqFVpMb5M)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=6006vpLlaVw)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=e2C_hgXiyzM)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=h7XVJ64IhY4)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=4JmCb5FmTA4)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=yUq0O-pDHCE)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=k77X47h6OVU)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=yAtpMMC3aiw)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=3c9iLgtDdKM)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=Cbbmj0dqP-M)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=-ILKiOU5iAQ)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=oyjpF7xPiC4)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=u-AXyF9kY9k)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=wcV0SRPFK9s)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=Ejsft2oPCtM)
- Ready — [Wiki ingest for www.youtube.com on 2026-07-29](https://www.youtube.com/watch?v=pVaKoDHW9iY)

</details>

## Audit links

- [[research-catalog|Complete research catalog]]
- [[security-catalog|Tracked securities]]
- [[SCHEMA|Wiki schema]]
- [[log|Append-only research log]]
- [Decision snapshot JSON](data/decision_snapshot.json)
- [Model portfolio CSV](data/model_portfolio.csv)
- [Actionable signals CSV](data/actionable_signals.csv)

[[index|Back to today's decision]]
