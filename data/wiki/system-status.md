---
title: "PaperTrader system status and audit"
type: system-status
status: maintained
tags:
  - system-status
created: "2026-08-05"
updated: "2026-08-05"
provenance: deterministic-decision-projection
snapshot_id: "decision_ffbf228dca49bf71406d"
as_of: "2026-08-05T22:34:36Z"
---

# System status and audit

**Publication snapshot:** `decision_ffbf228dca49bf71406d`
**As of:** `2026-08-05T22:34:36Z`
**Investment data:** Degraded — review investment data gaps
**Operations:** Attention required
**Publication validation:** Snapshot and exports validated
**Portfolio reconciliation:** Reconciled

## Coverage

- Assessments: 55/57
- Fresh-evidence assessments: 54/57
- Relationship reviews: 21/57
- Accepted relationships: 19
- Ready or active strategies: 0
- Active signals: 0
- Pending orders: 0
- Market success/failure: 72/0
- Candidate FX gaps: 0
- Research backlog: 390
- Last successful daily run: `2026-08-05T20:06:58Z`

## Current issues by investment impact

### Affects Candidate

- `error` **RIO — Rio Tinto plc: Rio Tinto assessment source operation is ambiguous within one run** — The required schema-v2 assessment for security\_1c055eb9b2bb1f5a8ff2 could not be written. The deterministic assessment applier found both predecessor quick\_check\_research 01KYVJ62SRF4GAV27YA2TP6892 and current security\_research 01KZ3E6S3RNXTH5SN041P14F6W claimed by run gha-30798126914-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- `error` **RBLX — Roblox Corporation: Assessment source operation is ambiguous within one run** — The required schema-v2 assessment for security\_c9a37d277445869a8809 could not be written. The deterministic assessment applier found both predecessor quick\_check\_research 01KYVJ62SRG31KASASEYZ2476N and current security\_research 01KZ38VCQRDKQK4SD081XKZNB3 claimed by run gha-30793143744-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- `error` **PWR — Quanta Services, Inc.: Assessment source operation is ambiguous within one run** — The required schema-v2 assessment for security\_488a9d7f7a8573597724 could not be written. The deterministic assessment applier found both predecessor quick\_check\_research 01KYVJ62SR384EB58S06SFPK5G and current security\_research 01KZ35CPR03SHK78B81ZSEV4JT claimed by run gha-30788518712-1 and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope code
- `error` **RTX — RTX Corporation: RTX assessment source operation is ambiguous within one run** — The required schema-v2 assessment for security\_59304f90c440def31dc5 could not be written. The deterministic assessment applier found both predecessor quick\_check\_research 01KYY98DWGST45EN32F928GMGG and current security\_research 01KZA04098D4DF0J4SFMJK1TDD claimed by run daily-20260805T220920Z and rejects any count greater than one as an ambiguous source operation. The assessment request has no source-operation field, so this operation cannot repair the provenance ambiguity without an out-of-scope
- `warning` **LAC — Lithium Americas Corp.: Daily preparation degraded: security\_fb87fac302a5446a1ced** — security\_fb87fac302a5446a1ced: YFTzMissingError: $LAC: possibly delisted; no timezone found
- `warning` **HOOD — Robinhood Markets, Inc.: Daily preparation degraded: security\_ad3b1f8f59fd599f079a** — security\_ad3b1f8f59fd599f079a: price cache is empty
- `warning` **CROX — Crocs, Inc.: Daily preparation degraded: security\_c150f31c30afdb4a85f9** — security\_c150f31c30afdb4a85f9: price cache is empty
- `warning` **WTI — W&amp;T Offshore, Inc.: Daily preparation degraded: security\_61567714298b9563d1a9** — security\_61567714298b9563d1a9: price cache is empty
- `warning` **FCX — Freeport-McMoRan Inc.: Daily preparation degraded: security\_2dbe878dfc899d7ee867** — security\_2dbe878dfc899d7ee867: YFTzMissingError: $FCX: possibly delisted; no timezone found
- `warning` **DLO — DLocal Limited: Daily preparation degraded: security\_715bde20b6e1e1320c1a** — security\_715bde20b6e1e1320c1a: price cache is empty
- `warning` **TX — Ternium S.A.: Daily preparation degraded: security\_2c779e81c27b78c556bb** — security\_2c779e81c27b78c556bb: YFTzMissingError: $TX: possibly delisted; no timezone found
- `warning` **GEV — GE Vernova Inc.: Daily preparation degraded: security\_4b61970aa8f574446819** — security\_4b61970aa8f574446819: YFTzMissingError: $GEV: possibly delisted; no timezone found
- `warning` **ATKR — Atkore Inc.: Daily preparation degraded: security\_22c2b9d782a62d7a9b86** — security\_22c2b9d782a62d7a9b86: YFTzMissingError: $ATKR: possibly delisted; no timezone found
- `warning` **PLS.AX — PLS Group Limited: Daily preparation degraded: security\_8a5c43888d224de85c69** — security\_8a5c43888d224de85c69: price cache is empty
- `warning` **KTOS — Kratos Defense &amp; Security Solutions, Inc.: Daily preparation degraded: security\_0cf8075039299094d614** — security\_0cf8075039299094d614: price cache is empty
- `warning` **RIO — Rio Tinto plc: Daily preparation degraded: security\_1c055eb9b2bb1f5a8ff2** — security\_1c055eb9b2bb1f5a8ff2: YFTzMissingError: $RIO: possibly delisted; no timezone found
- `warning` **PYPL — PayPal Holdings, Inc.: Daily preparation degraded: security\_1e8fbdb0f45f2b413e00** — security\_1e8fbdb0f45f2b413e00: price cache is empty
- `warning` **ETN — Eaton Corporation plc: Daily preparation degraded: security\_18a3ab0ee6086ee85d0f** — security\_18a3ab0ee6086ee85d0f: YFTzMissingError: $ETN: possibly delisted; no timezone found
- `warning` **SOFI — SoFi Technologies, Inc.: Daily preparation degraded: security\_98470cfc01bbcde78fc2** — security\_98470cfc01bbcde78fc2: price cache is empty
- `warning` **CSL — Carlisle Companies Incorporated: Daily preparation degraded: security\_9b0db3bc77914b23a307** — security\_9b0db3bc77914b23a307: price cache is empty
- `warning` **SGML — Sigma Lithium Corporation: Daily preparation degraded: security\_4627aea1bf7d8943d3d8** — security\_4627aea1bf7d8943d3d8: YFTzMissingError: $SGML: possibly delisted; no timezone found
- `warning` **RKLB — Rocket Lab Corporation: Daily preparation degraded: security\_7ca095d63423c55a90e3** — security\_7ca095d63423c55a90e3: YFTzMissingError: $RKLB: possibly delisted; no timezone found
- `warning` **ISRG — Intuitive Surgical, Inc.: Daily preparation degraded: security\_1f9cce545ede94cd6349** — security\_1f9cce545ede94cd6349: YFTzMissingError: $ISRG: possibly delisted; no timezone found
- `warning` **INTC — Intel Corporation: Daily preparation degraded: security\_dfa34d4b9050964b465e** — security\_dfa34d4b9050964b465e: price cache is empty
- `warning` **TWST — Twist Bioscience Corporation: Daily preparation degraded: security\_6cf75bd0ec0aa2a20148** — security\_6cf75bd0ec0aa2a20148: price cache is empty
- `warning` **RBLX — Roblox Corporation: Daily preparation degraded: security\_c9a37d277445869a8809** — security\_c9a37d277445869a8809: YFTzMissingError: $RBLX: possibly delisted; no timezone found
- `warning` **FUC.F — Fanuc Corporation: Daily preparation degraded: security\_96ba305ee7cd586bc348** — security\_96ba305ee7cd586bc348: price cache is empty
- `warning` **TSLA — Tesla, Inc.: Daily preparation degraded: security\_dc7a111e297be528d96b** — security\_dc7a111e297be528d96b: price cache is empty
- `warning` **VALE — Vale S.A.: Daily preparation degraded: security\_b2116dcf976c96974d7b** — security\_b2116dcf976c96974d7b: price cache is empty
- `warning` **ALB — Albemarle Corporation: Daily preparation degraded: security\_66cdcf90aac0d83e76f3** — security\_66cdcf90aac0d83e76f3: YFTzMissingError: $ALB: possibly delisted; no timezone found
- `warning` **ANIC.L — Agronomics Limited: Daily preparation degraded: security\_fe4648901e7675f157fd** — security\_fe4648901e7675f157fd: price cache is empty
- `warning` **GOOGL — Alphabet Inc.: Daily preparation degraded: security\_c86bb4e75658c07142cf** — security\_c86bb4e75658c07142cf: price cache is empty
- `warning` **ABCL — AbCellera Biologics Inc.: Daily preparation degraded: security\_7bf8f4c9cc12ae410e40** — security\_7bf8f4c9cc12ae410e40: price cache is empty
- `warning` **TXN — Texas Instruments Incorporated: Daily preparation degraded: security\_83a56943e18793f685b0** — security\_83a56943e18793f685b0: price cache is empty
- `warning` **VLO — Valero Energy Corporation: Daily preparation degraded: security\_c5a9e460d3350284d157** — security\_c5a9e460d3350284d157: price cache is empty
- `warning` **QCOM — QUALCOMM Incorporated: Daily preparation degraded: security\_3a75fc1ccca2ee7c937a** — security\_3a75fc1ccca2ee7c937a: price cache is empty
- `warning` **MP — MP Materials Corp.: Daily preparation degraded: security\_cd492d97064d8574156e** — security\_cd492d97064d8574156e: price cache is empty
- `warning` **ANET — Arista Networks, Inc.: Daily preparation degraded: security\_6f9a1450edceb9307c9a** — security\_6f9a1450edceb9307c9a: YFTzMissingError: $ANET: possibly delisted; no timezone found
- `warning` **PARRO.PA — Parrot S.A.: Daily preparation degraded: security\_cc4dcb8f002b61dffe00** — security\_cc4dcb8f002b61dffe00: YFTzMissingError: $PARRO.PA: possibly delisted; no timezone found
- `warning` **TSM — Taiwan Semiconductor Manufacturing Company Limited: Daily preparation degraded: security\_ce9b78a4d0773c950765** — security\_ce9b78a4d0773c950765: price cache is empty
- `warning` **PATH — UiPath, Inc.: Daily preparation degraded: security\_eca976f0076a425ea1bb** — security\_eca976f0076a425ea1bb: price cache is empty
- `warning` **RTX — RTX Corporation: Daily preparation degraded: security\_59304f90c440def31dc5** — security\_59304f90c440def31dc5: YFTzMissingError: $RTX: possibly delisted; no timezone found
- `warning` **ASML — ASML Holding N.V.: Daily preparation degraded: security\_ef35e41886220d51c22c** — security\_ef35e41886220d51c22c: price cache is empty
- `warning` **ENPH — Enphase Energy, Inc.: Daily preparation degraded: security\_f2b9760d847b2ba59324** — security\_f2b9760d847b2ba59324: YFTzMissingError: $ENPH: possibly delisted; no timezone found
- `warning` **MSTR — Strategy Inc: Daily preparation degraded: security\_fe5539a7d3fd9d553bce** — security\_fe5539a7d3fd9d553bce: price cache is empty
- `warning` **SPCX — Space Exploration Technologies Corp.: Daily preparation degraded: security\_664f93a7eaca72e76e9b** — security\_664f93a7eaca72e76e9b: price cache is empty
- `warning` **NBIS — Nebius Group N.V.: Daily preparation degraded: security\_47a0b06f6c6c478d7c1e** — security\_47a0b06f6c6c478d7c1e: price cache is empty
- `warning` **CRWD — CrowdStrike Holdings, Inc.: Daily preparation degraded: security\_8472507d7d320aa388a7** — security\_8472507d7d320aa388a7: YFTzMissingError: $CRWD: possibly delisted; no timezone found
- `warning` **SQM — Sociedad Quimica y Minera de Chile S.A.: Daily preparation degraded: security\_9d4049ed6669a52815d6** — security\_9d4049ed6669a52815d6: YFTzMissingError: $SQM: possibly delisted; no timezone found
- `warning` **YEC.F — YASKAWA Electric Corporation: Daily preparation degraded: security\_89969b7dac39b7db5661** — security\_89969b7dac39b7db5661: price cache is empty
- `warning` **META — Meta Platforms, Inc.: Daily preparation degraded: security\_d12e746b3c9d392183cc** — security\_d12e746b3c9d392183cc: price cache is empty
- `warning` **RXRX — Recursion Pharmaceuticals, Inc.: Daily preparation degraded: security\_ed7d5b616a196969c815** — security\_ed7d5b616a196969c815: YFTzMissingError: $RXRX: possibly delisted; no timezone found
- `warning` **SCCO — Southern Copper Corporation: Daily preparation degraded: security\_6ad1af8d10d6276a0221** — security\_6ad1af8d10d6276a0221: YFTzMissingError: $SCCO: possibly delisted; no timezone found
- `warning` **MSFT — Microsoft Corporation: Daily preparation degraded: security\_204be2a44063993de1a8** — security\_204be2a44063993de1a8: price cache is empty
- `warning` **ABBNY — ABB Ltd: Daily preparation degraded: security\_c120e9f26ebb6159adf9** — security\_c120e9f26ebb6159adf9: YFTzMissingError: $ABBNY: possibly delisted; no timezone found
- `warning` **SSUN.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: security\_d08d763780400dfbffce** — security\_d08d763780400dfbffce: price cache is empty
- `warning` **VRT — Vertiv Holdings Co: Daily preparation degraded: security\_cb88f9154cfeaa15e878** — security\_cb88f9154cfeaa15e878: price cache is empty
- `warning` **LH — Labcorp Holdings Inc.: Daily preparation degraded: security\_b1f2c48e1a744f5ecf67** — security\_b1f2c48e1a744f5ecf67: price cache is empty
- `warning` **PL — Planet Labs PBC: Daily preparation degraded: security\_97f38b2cb2d5ef127f5a** — security\_97f38b2cb2d5ef127f5a: price cache is empty
- `warning` **TDY — Teledyne Technologies Incorporated: Daily preparation degraded: security\_ad5917642acbba28c1f2** — security\_ad5917642acbba28c1f2: price cache is empty
- `warning` **PLTR — Palantir Technologies Inc.: Daily preparation degraded: security\_bdc2f87dadf134760c3a** — security\_bdc2f87dadf134760c3a: YFTzMissingError: $PLTR: possibly delisted; no timezone found
- `warning` **AMAT — Applied Materials, Inc.: Daily preparation degraded: security\_0a56aa634d077fe5796f** — security\_0a56aa634d077fe5796f: price cache is empty
- `warning` **NIB.F — Nidec Corporation: Daily preparation degraded: security\_3853e54c619d597dcaa1** — security\_3853e54c619d597dcaa1: price cache is empty
- `warning` **LUNR — Intuitive Machines, Inc.: Daily preparation degraded: security\_a5dc16f3f4b245e6c168** — security\_a5dc16f3f4b245e6c168: price cache is empty
- `warning` **COIN — Coinbase Global, Inc.: Daily preparation degraded: security\_37ddcbdaad296ad831f2** — security\_37ddcbdaad296ad831f2: YFTzMissingError: $COIN: possibly delisted; no timezone found
- `warning` **DNA — Ginkgo Bioworks Holdings, Inc.: Daily preparation degraded: security\_95351d928b674bbdf687** — security\_95351d928b674bbdf687: price cache is empty
- `warning` **CSIQ — Canadian Solar Inc.: Daily preparation degraded: security\_099561384c0f5e697727** — security\_099561384c0f5e697727: price cache is empty
- `warning` **AMZN — Amazon.com, Inc.: Daily preparation degraded: security\_2433a056eb0c55961fcc** — security\_2433a056eb0c55961fcc: price cache is empty
- `warning` **SPOT — Spotify Technology S.A.: Daily preparation degraded: security\_2010347f1a0a5ea60f47** — security\_2010347f1a0a5ea60f47: price cache is empty
- `warning` **SSU.VI — Samsung Electronics Co., Ltd.: Daily preparation degraded: security\_567d0d575bbd30aaa91d** — security\_567d0d575bbd30aaa91d: price cache is empty
- `warning` **FLNC — Fluence Energy, Inc.: Daily preparation degraded: security\_a9eb9838940ef5ceaa0c** — security\_a9eb9838940ef5ceaa0c: YFTzMissingError: $FLNC: possibly delisted; no timezone found
- `warning` **CRSR — Corsair Gaming, Inc.: Daily preparation degraded: security\_55c9ce2fdcd32dad6b8c** — security\_55c9ce2fdcd32dad6b8c: price cache is empty
- `warning` **NVDA — NVIDIA Corporation: Daily preparation degraded: security\_33d9c44facc75c726c7d** — security\_33d9c44facc75c726c7d: price cache is empty

### Publication Only

- `warning` **Telegram podcast audio delivery unavailable** — Committed Telegram delivery is awaiting a bounded retry.

### Operational Only

- `error` **Hermes operation validation failed: 01KZ3E6S3RNXTH5SN041P14F6W** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/daily-20260805T065913Z/01KZ3E6S3RNXTH5SN041P14F6W/agent\_result.json
- `error` **Hermes operation validation failed: 01KZ8VJY48VNMCFW638QQJZGJH** — Hermes exited with status 2; agent result is missing or a symlink: data/runs/daily-20260805T065913Z/01KZ8VJY48VNMCFW638QQJZGJH/agent\_result.json
- `warning` **Daily preparation degraded: FX AUD/EUR** — FX AUD/EUR: YFTzMissingError: $AUDEUR=X: possibly delisted; no timezone found
- `warning` **YouTube discovery failed for UCrTTBSUr0zhPU56UQljag5A** — @Value-Investing: 4JmCb5FmTA4 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- `warning` **YouTube discovery failed for UCOOSDCjFzHfnGoV8iNLC65A** — @ConnectingODots: Ejsft2oPCtM This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- `warning` **Daily preparation degraded: FX USD/EUR** — FX USD/EUR: YFTzMissingError: $USDEUR=X: possibly delisted; no timezone found
- `warning` **YouTube discovery failed for UCS01CiRDAiyhR\_mTHXDW23A** — @DumbMoneyLive: u-AXyF9kY9k This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- `warning` **YouTube discovery failed for UCIFn7ONIJHyC-lMnb7Fm\_jw** — @thelimitingfactor: SuSYegb8iK0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- `warning` **Daily preparation degraded: FX GBP/EUR** — FX GBP/EUR: YFTzMissingError: $GBPEUR=X: possibly delisted; no timezone found
- `warning` **YouTube discovery failed for UCrGLm-Drgv0vbbemwwHeXJw** — @CouchInvestor: MsNPz0dBYDw This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html
- `warning` **Daily podcast failed: daily-20260805T065913Z** — Committed Telegram delivery is awaiting a bounded retry.
- `warning` **YouTube discovery failed for UCESLZhusAkFfsNsApnjF\_Cg** — @allin: TqNiSTeNtb0 This request was detected as a bot. DO NOT OPEN AN ISSUE! See more details at https://pytubefix.readthedocs.io/en/latest/user/po\_token.html

## Bounded active operation queue

Showing 20 of 390 active operations.

<details><summary>Technical queue identifiers</summary>

- `ready` `01KYPB26Z023E3AMG9Z8KSPW9D` — `security_research` for `security_7bf8f4c9cc12ae410e40`
- `ready` `01KYPB27Y84W38J6MDDEF7PHG0` — `security_research` for `security_83a56943e18793f685b0`
- `ready` `01KYPB29WRNJGPJTTY2DB72JWG` — `security_research` for `security_8a5c43888d224de85c69`
- `ready` `01KYPB2KN8R1RGAPDZQ2AN9P2V` — `security_research` for `security_b2116dcf976c96974d7b`
- `ready` `01KYPB2XDRKAMP0ZX3MWA7Y1JH` — `security_research` for `security_fe4648901e7675f157fd`
- `ready` `01KYPB2YD02XHRSSW68JA9MCG7` — `security_research` for `security_fe5539a7d3fd9d553bce`
- `ready` `01KYQ49D1G2RNAXKS9RP0MY1R9` — `wiki_ingest` for `youtube_9ePWIYadju4`
- `ready` `01KYQ49D1G3CHJ4YE6BKXP9RX9` — `wiki_ingest` for `youtube_J2ZqFVpMb5M`
- `ready` `01KYQ49D1G3QX14JS5VBH76HN0` — `wiki_ingest` for `youtube_6006vpLlaVw`
- `ready` `01KYQ49D1G663ZCTKEG5CJHK7B` — `wiki_ingest` for `youtube_e2C_hgXiyzM`
- `ready` `01KYQ49D1G6RHZ9VJYDV5NKPTT` — `wiki_ingest` for `youtube_h7XVJ64IhY4`
- `ready` `01KYQ49D1G889B5DYTST65N0EW` — `wiki_ingest` for `youtube_4JmCb5FmTA4`
- `ready` `01KYQ49D1GAXYP4Y8RR9C5G3KN` — `wiki_ingest` for `youtube_yUq0O-pDHCE`
- `ready` `01KYQ49D1GB9057VRBFHJ9Y1NX` — `wiki_ingest` for `youtube_k77X47h6OVU`
- `ready` `01KYQ49D1GCWM22YHNBNMM75XE` — `wiki_ingest` for `youtube_yAtpMMC3aiw`
- `ready` `01KYQ49D1GD05JQFX2ZE5MTRWZ` — `wiki_ingest` for `youtube_3c9iLgtDdKM`
- `ready` `01KYQ49D1GENTSWY2QD1D1RREE` — `wiki_ingest` for `youtube_Cbbmj0dqP-M`
- `ready` `01KYQ49D1GETPHJ2B8PYVG9FE0` — `wiki_ingest` for `youtube_-ILKiOU5iAQ`
- `ready` `01KYQ49D1GF9JD930JH9N49P07` — `wiki_ingest` for `youtube_oyjpF7xPiC4`
- `ready` `01KYQ49D1GFY1PFRCMBZ41Q88C` — `wiki_ingest` for `youtube_u-AXyF9kY9k`

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
