# PaperTrader wiki maintenance report

## Maintenance identity and execution date

- maintenance identity: wiki-maintenance:2026-W36
- execution date: 2026-08-31

## Native llm-wiki identity

- native llm-wiki version: 2.1.0
- native llm-wiki sha256: a37ae04745b04b8e9bbd8de37cdcbc2b2187ccafb68418e436a46ebb1e491ee5

## Pages inspected

The exact inspected path set was the union of the following explicit paths and direct-child path sets; every Markdown path in each stated set was opened or parsed, for 633 pages total:

- `data/wiki/SCHEMA.md`
- `data/wiki/index.md`
- `data/wiki/log.md`
- `data/wiki/model-portfolio.md`
- `data/wiki/performance.md`
- `data/wiki/research-catalog.md`
- `data/wiki/security-catalog.md`
- `data/wiki/signals.md`
- `data/wiki/system-status.md`
- `data/wiki/_archive/log-2026.md`
- every one of the 34 paths matching `data/wiki/daily-reports/*.md`
- every one of the 28 paths matching `data/wiki/ideas/*.md`
- every one of the 418 paths matching `data/wiki/inbox/*.md`
- every one of the 18 paths matching `data/wiki/podcasts/*.md`
- every one of the 46 paths matching `data/wiki/relationships/*.md`
- every one of the 78 paths matching `data/wiki/securities/*.md`
- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md`

Orientation was completed first by reading `data/wiki/SCHEMA.md`, `data/wiki/index.md`, `data/wiki/research-catalog.md`, and the recent tail of `data/wiki/log.md`. The raw-source inventory was also inspected and contains only `data/wiki/raw/.gitkeep`, which is not a Markdown page.

## Pages changed

- `data/wiki/securities/security_47a0b06f6c6c478d7c1e.md`
- `data/wiki/securities/security_ed7d5b616a196969c815.md`
- `data/wiki/log.md`
- `data/runs/daily-20260831T083100Z/wiki-maintenance/wiki_maintenance_report.md`

No other path was changed by this maintenance operation.

## Orphan pages

None. Every non-archived maintained page has at least one inbound internal link, and every non-archived page is reachable from `data/wiki/index.md` through the index/catalog link graph. The archived log was evaluated as an archive rather than as an active catalog page.

## Broken or ambiguous links

None found. The scan resolved all wikilinks across the 633 pages and all local Markdown links in `data/wiki/index.md` and `data/wiki/research-catalog.md`. Repeated human-readable titles on dated inbox packets do not create ambiguous targets because maintained links use path-qualified, immutable packet names.

## Index or catalog omissions

None. The index reaches all non-archived maintained pages through its navigation and catalog links. `data/wiki/research-catalog.md` directly links every one of the 629 in-scope pages other than `SCHEMA.md`, the index, the catalog itself, and the archived log. No safe index or catalog insertion was required.

## Frontmatter and tag findings

- No missing or malformed required frontmatter was found.
- No tag outside the `data/wiki/SCHEMA.md` taxonomy was found.
- No maintained idea, security, relationship, strategy, concept, comparison, or query page lacked its confidence field.
- Two security pages had stale `next_review` frontmatter that contradicted a later date already stated in the same page's maintained disposition. Safe metadata-only repairs aligned `security_47a0b06f6c6c478d7c1e` from 2026-08-25 to 2026-09-17 and `security_ed7d5b616a196969c815` from 2026-08-15 to 2026-09-11. No claim, assessment, rating, allocation status, or strategy state changed.

## Stale pages

No page has an `updated` date more than 90 days before 2026-08-31, and there is no retained raw Markdown source whose newer date can make a maintained page stale.

Fifty-three pages retain genuinely overdue review dates after the two safe metadata repairs. One additional page, `data/wiki/securities/security_3853e54c619d597dcaa1.md`, is due on the execution date rather than overdue. The overdue paths are:

- Ideas: `data/wiki/ideas/idea_ai_infrastructure_power.md` (2026-08-26); `data/wiki/ideas/idea_energy_refining.md` (2026-08-12); `data/wiki/ideas/idea_macro_hedge_gold.md` (2026-08-28); `data/wiki/ideas/idea_solar_storage_grid_flexibility_reset.md` (2026-08-24).
- Relationships: `data/wiki/relationships/relationship_1655ac715c33506ec7da.md` (2026-08-27); `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` (2026-08-14); `data/wiki/relationships/relationship_297f9e36fb4e93a808e8.md` (2026-08-14); `data/wiki/relationships/relationship_392da6d90e7c969945a2.md` (2026-07-30); `data/wiki/relationships/relationship_510158d3d515d91d5c14.md` (2026-08-07); `data/wiki/relationships/relationship_670ed88c8e4616316a19.md` (2026-08-15); `data/wiki/relationships/relationship_7e9fd9486e494dd05bb5.md` (2026-08-01); `data/wiki/relationships/relationship_871e21ff73620ab8eb14.md` (2026-08-06); `data/wiki/relationships/relationship_87b95f713a902d531f2f.md` (2026-08-04); `data/wiki/relationships/relationship_9befaccc50d8cd94372b.md` (2026-08-15); `data/wiki/relationships/relationship_9e7b4700174908755cbc.md` (2026-08-10); `data/wiki/relationships/relationship_ad2f37b49980dbc73a08.md` (2026-08-15); `data/wiki/relationships/relationship_afac7205cd7e09800edf.md` (2026-08-27); `data/wiki/relationships/relationship_c829dae21648bb133cc7.md` (2026-08-10); `data/wiki/relationships/relationship_cbdd07edda84994325d6.md` (2026-08-26); `data/wiki/relationships/relationship_d9c8f578040386a487be.md` (2026-08-14); `data/wiki/relationships/relationship_def43e5b4e13577e2b99.md` (2026-08-26); `data/wiki/relationships/relationship_e5f55616b9beaf661080.md` (2026-08-14); `data/wiki/relationships/relationship_f2efab6050df0edcb762.md` (2026-08-14); `data/wiki/relationships/relationship_solar_storage_grid_atkr.md` (2026-08-15); `data/wiki/relationships/relationship_solar_storage_grid_enph.md` (2026-08-15); `data/wiki/relationships/relationship_solar_storage_grid_flnc.md` (2026-08-15).
- Securities: `data/wiki/securities/security_0a56aa634d077fe5796f.md` (2026-08-26); `data/wiki/securities/security_0cf8075039299094d614.md` (2026-08-19); `data/wiki/securities/security_1c055eb9b2bb1f5a8ff2.md` (2026-08-19); `data/wiki/securities/security_2010347f1a0a5ea60f47.md` (2026-08-20); `data/wiki/securities/security_22c2b9d782a62d7a9b86.md` (2026-08-15); `data/wiki/securities/security_2c779e81c27b78c556bb.md` (2026-08-20); `data/wiki/securities/security_33d9c44facc75c726c7d.md` (2026-08-19); `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` (2026-08-15); `data/wiki/securities/security_55c9ce2fdcd32dad6b8c.md` (2026-08-22); `data/wiki/securities/security_61567714298b9563d1a9.md` (2026-08-20); `data/wiki/securities/security_664f93a7eaca72e76e9b.md` (2026-08-19); `data/wiki/securities/security_66cdcf90aac0d83e76f3.md` (2026-08-20); `data/wiki/securities/security_6f9a1450edceb9307c9a.md` (2026-08-23); `data/wiki/securities/security_7bf8f4c9cc12ae410e40.md` (2026-08-24); `data/wiki/securities/security_7ca095d63423c55a90e3.md` (2026-08-23); `data/wiki/securities/security_98470cfc01bbcde78fc2.md` (2026-08-19); `data/wiki/securities/security_9b0db3bc77914b23a307.md` (2026-08-29); `data/wiki/securities/security_a9eb9838940ef5ceaa0c.md` (2026-08-20); `data/wiki/securities/security_bdc2f87dadf134760c3a.md` (2026-08-25); `data/wiki/securities/security_c120e9f26ebb6159adf9.md` (2026-08-24); `data/wiki/securities/security_ce9b78a4d0773c950765.md` (2026-08-20); `data/wiki/securities/security_d08d763780400dfbffce.md` (2026-08-20); `data/wiki/securities/security_dfa34d4b9050964b465e.md` (2026-08-20); `data/wiki/securities/security_eca976f0076a425ea1bb.md` (2026-08-20); `data/wiki/securities/security_f2b9760d847b2ba59324.md` (2026-08-29); `data/wiki/securities/security_fb87fac302a5446a1ced.md` (2026-08-15).
- Strategy: `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md` (2026-08-04).

These dates are research-age findings, not evidence that the conclusions are false. They were not advanced without current evidence.

## Contested or contradictory content

No unresolved cross-page material contradiction and no `contested: true` or `contradictions:` frontmatter was found. The wiki does preserve contrary evidence and dated supersession statements. For example, `data/wiki/ideas/idea_structural_silver_deficit.md` retains evidence that weaker photovoltaic demand, thrifting, substitution, and recycling contradict an unqualified shortage narrative; this is appropriate explicit counterevidence, not a defect to erase.

The only definite internal inconsistencies found were the two stale `next_review` metadata values described above, and both were aligned to dates already present in their pages. Potential disagreements requiring fresh external evidence were not resolved or rewritten.

## Low-confidence or weakly sourced claims

Fifteen maintained pages explicitly carry low, low-medium, or medium-low confidence:

- `data/wiki/ideas/idea_cable_broadband_convergence.md`
- `data/wiki/ideas/idea_humanoid_robotics_embodied_ai_components.md`
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md`
- `data/wiki/relationships/relationship_9e7b4700174908755cbc.md`
- `data/wiki/relationships/relationship_afac7205cd7e09800edf.md`
- `data/wiki/relationships/relationship_ai_drug_nvda.md`
- `data/wiki/relationships/relationship_c829dae21648bb133cc7.md`
- `data/wiki/relationships/relationship_terafab_intc.md`
- `data/wiki/relationships/relationship_terafab_samsung_common_gdr.md`
- `data/wiki/relationships/relationship_wide_bandgap_nvda.md`
- `data/wiki/securities/security_3853e54c619d597dcaa1.md`
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md`
- `data/wiki/securities/security_664f93a7eaca72e76e9b.md`
- `data/wiki/securities/security_ed7d5b616a196969c815.md`
- `data/wiki/securities/security_fb87fac302a5446a1ced.md`

Each page labels the limitation and names evidence, missing economics, or invalidation gates. No single-source maintained domain page omitted confidence metadata, and no empty source/evidence frontmatter field was found. Weak confidence is therefore surfaced rather than silently hardened into fact. Current corroboration would require bounded research; no source was fetched and no claim was upgraded.

## Raw-source drift findings

None assessable and none found. `data/wiki/raw/` contains only `data/wiki/raw/.gitkeep`; there is no raw Markdown source with a `sha256` frontmatter value to recompute. The immutable raw directory was not changed.

## Oversized or archival candidates

Forty-four pages exceed the native 200-line review threshold:

- `data/wiki/_archive/log-2026.md`
- `data/wiki/daily-reports/daily-report_20260726.md`, `data/wiki/daily-reports/daily-report_20260727.md`, `data/wiki/daily-reports/daily-report_20260728.md`, `data/wiki/daily-reports/daily-report_20260729.md`, `data/wiki/daily-reports/daily-report_20260730.md`, `data/wiki/daily-reports/daily-report_20260731.md`, `data/wiki/daily-reports/daily-report_20260801.md`, `data/wiki/daily-reports/daily-report_20260803.md`, `data/wiki/daily-reports/daily-report_20260805.md`, `data/wiki/daily-reports/daily-report_20260806.md`, `data/wiki/daily-reports/daily-report_20260807.md`, `data/wiki/daily-reports/daily-report_20260808.md`, `data/wiki/daily-reports/daily-report_20260809.md`, `data/wiki/daily-reports/daily-report_20260810.md`, `data/wiki/daily-reports/daily-report_20260811.md`, `data/wiki/daily-reports/daily-report_20260812.md`, `data/wiki/daily-reports/daily-report_20260813.md`, `data/wiki/daily-reports/daily-report_20260815.md`, `data/wiki/daily-reports/daily-report_20260816.md`, `data/wiki/daily-reports/daily-report_20260817.md`, `data/wiki/daily-reports/daily-report_20260818.md`, `data/wiki/daily-reports/daily-report_20260819.md`, `data/wiki/daily-reports/daily-report_20260820.md`, `data/wiki/daily-reports/daily-report_20260821.md`, `data/wiki/daily-reports/daily-report_20260822.md`, `data/wiki/daily-reports/daily-report_20260823.md`, `data/wiki/daily-reports/daily-report_20260824.md`, `data/wiki/daily-reports/daily-report_20260825.md`, `data/wiki/daily-reports/daily-report_20260826.md`, `data/wiki/daily-reports/daily-report_20260828.md`, `data/wiki/daily-reports/daily-report_20260829.md`, and `data/wiki/daily-reports/daily-report_20260830.md`.
- `data/wiki/log.md`
- `data/wiki/research-catalog.md`
- `data/wiki/securities/security_099561384c0f5e697727.md`
- `data/wiki/securities/security_204be2a44063993de1a8.md`
- `data/wiki/securities/security_59304f90c440def31dc5.md`
- `data/wiki/securities/security_715bde20b6e1e1320c1a.md`
- `data/wiki/securities/security_96ba305ee7cd586bc348.md`
- `data/wiki/securities/security_a5dc16f3f4b245e6c168.md`
- `data/wiki/securities/security_dc7a111e297be528d96b.md`
- `data/wiki/securities/security_f2b9760d847b2ba59324.md`
- `data/wiki/system-status.md`

The daily reports and status/catalog pages are canonical or generated views, and the archived log is already archived; they were not split or rewritten. The eight oversized security pages are candidates for a later evidence-preserving structural split, but automatic splitting could alter provenance or investment meaning and was not safe in this operation.

The current `data/wiki/log.md` has 68 dated action entries after recording this lint, below the native 500-entry rotation threshold. Its 2,664 physical lines do not independently require rotation. The page also states the repository's configured 5,000-line policy. No log rotation is required.

## Safe repairs applied

- Corrected `next_review` in `data/wiki/securities/security_47a0b06f6c6c478d7c1e.md` to 2026-09-17, matching the maintained disposition already on that page.
- Corrected `next_review` in `data/wiki/securities/security_ed7d5b616a196969c815.md` to 2026-09-11, matching the maintained disposition already on that page.
- Appended the required lint record to `data/wiki/log.md` and advanced only the log's own `updated` date to 2026-08-31.
- Created this report at the user-specified path.

No sourced claim was deleted, no material contradiction was resolved without evidence, no page was archived or consolidated, and no structured or generated state was changed.

## Suggested PaperTrader research follow-ups

These are bounded recommendations only. Nothing was enqueued.

- `idea_research`: existing entities `idea_ai_infrastructure_power`, `idea_energy_refining`, `idea_macro_hedge_gold`, and `idea_solar_storage_grid_flexibility_reset`, because their maintained review dates are overdue.
- `relationship_research`: existing entities `relationship_1655ac715c33506ec7da`, `relationship_250194f6a9e3a1817632`, `relationship_297f9e36fb4e93a808e8`, `relationship_392da6d90e7c969945a2`, `relationship_510158d3d515d91d5c14`, `relationship_670ed88c8e4616316a19`, `relationship_7e9fd9486e494dd05bb5`, `relationship_871e21ff73620ab8eb14`, `relationship_87b95f713a902d531f2f`, `relationship_9befaccc50d8cd94372b`, `relationship_9e7b4700174908755cbc`, `relationship_ad2f37b49980dbc73a08`, `relationship_afac7205cd7e09800edf`, `relationship_c829dae21648bb133cc7`, `relationship_cbdd07edda84994325d6`, `relationship_d9c8f578040386a487be`, `relationship_def43e5b4e13577e2b99`, `relationship_e5f55616b9beaf661080`, `relationship_f2efab6050df0edcb762`, `relationship_solar_storage_grid_atkr`, `relationship_solar_storage_grid_enph`, and `relationship_solar_storage_grid_flnc`, because their maintained review dates are overdue.
- `security_research`: existing entities `security_0a56aa634d077fe5796f`, `security_0cf8075039299094d614`, `security_1c055eb9b2bb1f5a8ff2`, `security_2010347f1a0a5ea60f47`, `security_22c2b9d782a62d7a9b86`, `security_2c779e81c27b78c556bb`, `security_33d9c44facc75c726c7d`, `security_3853e54c619d597dcaa1`, `security_4627aea1bf7d8943d3d8`, `security_55c9ce2fdcd32dad6b8c`, `security_61567714298b9563d1a9`, `security_664f93a7eaca72e76e9b`, `security_66cdcf90aac0d83e76f3`, `security_6f9a1450edceb9307c9a`, `security_7bf8f4c9cc12ae410e40`, `security_7ca095d63423c55a90e3`, `security_98470cfc01bbcde78fc2`, `security_9b0db3bc77914b23a307`, `security_a9eb9838940ef5ceaa0c`, `security_bdc2f87dadf134760c3a`, `security_c120e9f26ebb6159adf9`, `security_ce9b78a4d0773c950765`, `security_d08d763780400dfbffce`, `security_dfa34d4b9050964b465e`, `security_eca976f0076a425ea1bb`, `security_f2b9760d847b2ba59324`, and `security_fb87fac302a5446a1ced`, because their maintained review dates are overdue or due on 2026-08-31.
- `strategy_research`: existing entity `strategy_bd005fc3733b1475b6f9`, because its maintained review date is overdue.
- `wiki_ingest`: None. No raw Markdown source or registered-source packet was available for bounded drift remediation in this network-free operation.

## Unresolved blockers

- Current evidence is required before any overdue or due research conclusion can be refreshed; network access and source retrieval were expressly excluded.
- Fifteen explicitly low-confidence pages remain appropriately bounded by their stated evidence gaps and cannot be upgraded through formatting maintenance.
- Eight oversized security pages cannot be split safely without an evidence-preserving, entity-specific review of anchors, provenance, catalog links, and generated consumers.
- Deterministic controller validation and repository-delta enforcement remain pending by contract.

## Exact validation results

- `uv run papertrader schema validate --strict` — PASSED
- `uv run papertrader integrity --strict` — PASSED
- `uv run papertrader wiki lint --strict` — PASSED
- `uv run papertrader advice validate --strict` — PASSED
