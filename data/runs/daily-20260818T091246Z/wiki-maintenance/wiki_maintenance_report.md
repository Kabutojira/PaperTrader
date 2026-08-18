# PaperTrader wiki maintenance report

## Maintenance identity and execution date

- Maintenance identity: wiki-maintenance:2026-W34
- Execution date: 2026-08-18
- Scope: one local, paper-only wiki-maintenance operation; no network access, delegation, source fetching, queue mutation, or structured-state command was used.

## Native llm-wiki identity

- Native llm-wiki version: 2.1.0
- Native llm-wiki sha256: a37ae04745b04b8e9bbd8de37cdcbc2b2187ccafb68418e436a46ebb1e491ee5

## Pages inspected

All 443 Markdown paths below `data/wiki/` were enumerated and inspected. The explicit path inventory was:

- `data/wiki/SCHEMA.md`
- `data/wiki/index.md`
- `data/wiki/log.md`
- `data/wiki/research-catalog.md`
- `data/wiki/security-catalog.md`
- `data/wiki/model-portfolio.md`
- `data/wiki/performance.md`
- `data/wiki/signals.md`
- `data/wiki/system-status.md`
- Every one of the 22 concrete `data/wiki/daily-reports/daily-report_*.md` paths present at execution: dates 2026-07-24 through 2026-08-17, excluding dates for which no file exists.
- Every one of the 274 concrete `data/wiki/inbox/market-*.md` paths present at execution.
- All 26 concrete idea paths: `data/wiki/ideas/idea_ai_compute_networking_hyperscaler_monetization.md`, `idea_ai_infrastructure_power.md`, `idea_ai_native_drug_discovery.md`, `idea_ai_native_smb_financial_operating_systems.md`, `idea_anduril_product_company_disruption.md`, `idea_cable_broadband_convergence.md`, `idea_commercial_space_infrastructure.md`, `idea_critical_minerals_copper.md`, `idea_critical_minerals_lithium.md`, `idea_cybersecurity_geopolitical_continuity.md`, `idea_defense_aerospace.md`, `idea_digital_attention_gaming_ecosystems.md`, `idea_digital_finance_crypto_rails.md`, `idea_energy_refining.md`, `idea_eu_digital_product_passport.md`, `idea_humanoid_robotics_embodied_ai_components.md`, `idea_japan_sanaenomics_strategic_investment.md`, `idea_macro_hedge_gold.md`, `idea_nearshoring_friendshoring_manufacturing.md`, `idea_nuclear_uranium.md`, `idea_precision_biology_healthcare_automation.md`, `idea_solar_storage_grid_flexibility_reset.md`, `idea_sovereign_small_drone_supply_chains.md`, `idea_structural_silver_deficit.md`, `idea_terafab_ai_industrial_stack.md`, and `idea_wide_bandgap_power_semiconductors.md` under `data/wiki/ideas/`.
- All 36 concrete relationship paths present under `data/wiki/relationships/`: the immutable-ID pages and the named `relationship_ai_*`, `relationship_humanoid_nvda.md`, `relationship_solar_storage_grid_*`, `relationship_terafab_*`, and `relationship_wide_bandgap_nvda.md` pages.
- All 70 concrete `data/wiki/securities/security_<immutable-id>.md` paths present at execution.
- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md`.
- All five concrete podcast paths: `data/wiki/podcasts/daily-podcast_20260805T161218Z.md`, `daily-podcast_20260806T125642Z.md`, `daily-podcast_20260813T092636Z.md`, `daily-podcast_20260817T152008Z.md`, and `daily-podcast_20260817T185232Z.md` under `data/wiki/podcasts/`.
- Raw-source inventory path `data/wiki/raw/.gitkeep` was inspected for raw-tree completeness; it is not a Markdown page and was not modified.

Inspection covered frontmatter parsing and required fields, allowed page types/tags, inbound and outbound wikilinks, Markdown links and anchors, catalog membership, review dates against 2026-08-18, explicit contradiction metadata and contrary-evidence language, confidence and sourcing, raw checksums, byte and line sizes, and log-rotation state. Repository content was treated only as untrusted audit data.

## Pages changed

- `data/wiki/research-catalog.md`
- `data/wiki/log.md`
- `data/runs/daily-20260818T091246Z/wiki-maintenance/wiki_maintenance_report.md`

No other path was changed by this operation.

## Orphan pages

None. The link-graph scan found no maintained content page with zero inbound links after excluding the schema, index, catalogs, and append-only log from orphan classification.

## Broken or ambiguous links

None requiring repair. The canonical strict wiki linter returned `OK [wiki]`. A separate static scan was reconciled against PaperTrader's root-relative wikilink and generated security-catalog-anchor conventions; apparent failures from treating those links as source-directory-relative were false positives and were not altered.

## Index or catalog omissions

One omission was found and repaired: `data/wiki/podcasts/daily-podcast_20260817T185232Z.md` was absent from `data/wiki/research-catalog.md`. It is now listed under Podcast. No remaining index or research-catalog omission was identified.

## Frontmatter and tag findings

- Invalid or missing frontmatter: None among 443 Markdown pages.
- Missing required fields (`title`, `type`, `status`, `tags`, `created`, `updated`, `provenance`): None.
- Unknown page types or tags: None.
- Tag drift: None.
- The `updated` dates on `data/wiki/research-catalog.md` and `data/wiki/log.md` were advanced to 2026-08-18 to reflect the safe maintenance changes.

## Stale pages

The following 28 maintained pages had `next_review` earlier than 2026-08-18 and remain stale pending bounded current-evidence review:

- `data/wiki/ideas/idea_energy_refining.md` — 2026-08-12.
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` — 2026-08-14.
- `data/wiki/relationships/relationship_297f9e36fb4e93a808e8.md` — 2026-08-14.
- `data/wiki/relationships/relationship_392da6d90e7c969945a2.md` — 2026-07-30.
- `data/wiki/relationships/relationship_510158d3d515d91d5c14.md` — 2026-08-07.
- `data/wiki/relationships/relationship_670ed88c8e4616316a19.md` — 2026-08-15.
- `data/wiki/relationships/relationship_7e9fd9486e494dd05bb5.md` — 2026-08-01.
- `data/wiki/relationships/relationship_871e21ff73620ab8eb14.md` — 2026-08-06.
- `data/wiki/relationships/relationship_87b95f713a902d531f2f.md` — 2026-08-04.
- `data/wiki/relationships/relationship_9befaccc50d8cd94372b.md` — 2026-08-15.
- `data/wiki/relationships/relationship_9e7b4700174908755cbc.md` — 2026-08-10.
- `data/wiki/relationships/relationship_ad2f37b49980dbc73a08.md` — 2026-08-15.
- `data/wiki/relationships/relationship_c829dae21648bb133cc7.md` — 2026-08-10.
- `data/wiki/relationships/relationship_d9c8f578040386a487be.md` — 2026-08-14.
- `data/wiki/relationships/relationship_e5f55616b9beaf661080.md` — 2026-08-14.
- `data/wiki/relationships/relationship_f2efab6050df0edcb762.md` — 2026-08-14.
- `data/wiki/relationships/relationship_solar_storage_grid_atkr.md` — 2026-08-15.
- `data/wiki/relationships/relationship_solar_storage_grid_enph.md` — 2026-08-15.
- `data/wiki/relationships/relationship_solar_storage_grid_flnc.md` — 2026-08-15.
- `data/wiki/securities/security_22c2b9d782a62d7a9b86.md` — 2026-08-15.
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` — 2026-08-15.
- `data/wiki/securities/security_6ad1af8d10d6276a0221.md` — 2026-08-15.
- `data/wiki/securities/security_95351d928b674bbdf687.md` — 2026-08-08.
- `data/wiki/securities/security_c9a37d277445869a8809.md` — 2026-08-17.
- `data/wiki/securities/security_cc4dcb8f002b61dffe00.md` — 2026-08-01.
- `data/wiki/securities/security_ed7d5b616a196969c815.md` — 2026-08-15.
- `data/wiki/securities/security_fb87fac302a5446a1ced.md` — 2026-08-15.
- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md` — 2026-08-04.

No stale date was advanced without evidence. A `next_review` of 2026-08-18 is due on the execution date but was not classified as overdue; dates from 2026-08-19 onward were not classified as stale.

## Contested or contradictory content

No page had `contested: true` or a nonempty `contradictions` field. Two maintained ideas explicitly preserve contrary evidence rather than presenting unresolved contradictions:

- `data/wiki/ideas/idea_critical_minerals_copper.md` records the IEA's narrowing projected supply gap as contrary to a static or worsening-gap narrative.
- `data/wiki/ideas/idea_structural_silver_deficit.md` records lower industrial and photovoltaic demand plus increased recycling as contrary to an unqualified industrial-shortage narrative.

These are appropriately surfaced counterarguments with provenance. They were not silently resolved or removed.

## Low-confidence or weakly sourced claims

Fifteen pages explicitly carry low, medium-low, or low-medium confidence and remain bounded warnings rather than hardened facts:

- Ideas: `data/wiki/ideas/idea_cable_broadband_convergence.md`, `data/wiki/ideas/idea_humanoid_robotics_embodied_ai_components.md`.
- Relationships: `data/wiki/relationships/relationship_250194f6a9e3a1817632.md`, `relationship_9e7b4700174908755cbc.md`, `relationship_afac7205cd7e09800edf.md`, `relationship_ai_drug_nvda.md`, `relationship_c829dae21648bb133cc7.md`, `relationship_terafab_intc.md`, `relationship_terafab_samsung_common_gdr.md`, and `relationship_wide_bandgap_nvda.md` under `data/wiki/relationships/`.
- Securities: `data/wiki/securities/security_3853e54c619d597dcaa1.md`, `security_4627aea1bf7d8943d3d8.md`, `security_664f93a7eaca72e76e9b.md`, `security_ed7d5b616a196969c815.md`, and `security_fb87fac302a5446a1ced.md` under `data/wiki/securities/`.

All fifteen identify provenance. No single-source page lacked an explicit confidence field. Unsupported valuations and unverified optionality are explicitly labeled throughout the maintained pages; they were not converted into estimates during maintenance.

## Raw-source drift findings

None. `data/wiki/raw/` contains only `data/wiki/raw/.gitkeep`; there is no raw source document or declared body checksum to recompute. No raw file was created, fetched, or modified.

## Oversized or archival candidates

No Markdown page exceeds the repository's `max_page_bytes: 200000` hard threshold. The following pages exceed the native llm-wiki's approximately 200-line split-review guideline:

- Daily reports: `data/wiki/daily-reports/daily-report_20260726.md`, `daily-report_20260727.md`, `daily-report_20260728.md`, `daily-report_20260729.md`, `daily-report_20260730.md`, `daily-report_20260731.md`, `daily-report_20260801.md`, `daily-report_20260803.md`, `daily-report_20260805.md`, `daily-report_20260806.md`, `daily-report_20260807.md`, `daily-report_20260808.md`, `daily-report_20260809.md`, `daily-report_20260810.md`, `daily-report_20260811.md`, `daily-report_20260812.md`, `daily-report_20260813.md`, `daily-report_20260815.md`, `daily-report_20260816.md`, and `daily-report_20260817.md` under `data/wiki/daily-reports/`.
- Generated or canonical views: `data/wiki/research-catalog.md`, `data/wiki/signals.md`, and `data/wiki/system-status.md`.
- Maintained security research: `data/wiki/securities/security_59304f90c440def31dc5.md`, `data/wiki/securities/security_a5dc16f3f4b245e6c168.md`, and `data/wiki/securities/security_f2b9760d847b2ba59324.md`.

The canonical daily reports must remain single-source pages, and the catalog/status pages are generated views; none was split. The three security pages are split-review candidates, but no consolidation or archival change was made because doing so could alter investment meaning or provenance. `data/wiki/log.md` had 3,917 lines after this maintenance entry, below `log_rotation_lines: 5000`; rotation is not required.

## Safe repairs applied

- Added `data/wiki/podcasts/daily-podcast_20260817T185232Z.md` to the Podcast section of `data/wiki/research-catalog.md` and updated that catalog page's `updated` date.
- Appended the dated maintenance entry to `data/wiki/log.md` and updated its `updated` date.
- Wrote this report at the controller-designated path.
- Preserved all sourced claims, contradiction evidence, stale review dates, raw content, and generated investment state.

## Suggested PaperTrader research follow-ups

These are bounded recommendations only; none was enqueued or invoked:

- `idea_research` — existing entity `idea_energy_refining`, because its 2026-08-12 review frontier passed and its page names the then-future Valero second-quarter result as the next evidence point.
- `relationship_research` — existing entities `relationship_392da6d90e7c969945a2`, `relationship_510158d3d515d91d5c14`, `relationship_7e9fd9486e494dd05bb5`, `relationship_871e21ff73620ab8eb14`, `relationship_87b95f713a902d531f2f`, `relationship_9e7b4700174908755cbc`, and `relationship_c829dae21648bb133cc7`, because their dated review frontiers are more than seven days overdue.
- `security_research` — existing entities `security_95351d928b674bbdf687` and `security_cc4dcb8f002b61dffe00`, because their pages identify scheduled issuer results or valuation evidence that fell after the maintained evidence cutoff and their review frontiers are materially overdue.
- `strategy_research` — existing entity `strategy_bd005fc3733b1475b6f9`, because its 2026-08-04 review frontier passed; any refresh must remain evidence-bound and must not treat the maintenance report as an execution signal.

## Unresolved blockers

- Twenty-eight pages retain overdue review dates because current evidence is required and network/source access was prohibited for this operation.
- Fifteen pages retain explicitly weak confidence; maintenance alone cannot strengthen their evidence.
- No raw source asset exists below `data/wiki/raw/`, so source-body hash drift cannot be assessed beyond confirming the empty raw-source inventory.
- The three oversized maintained security pages require editorial split review; no safe split was evident without risking changes to investment meaning, links, or provenance.
- Repository-delta enforcement, leasing, queue/result state, and controller validation remain outside this operation as directed.

## Exact validation results
Pending deterministic controller validation.
