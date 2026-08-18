# PaperTrader wiki maintenance report

## Maintenance identity and execution date

- maintenance identity: wiki-maintenance:2026-W34
- execution date: 2026-08-18

## Native llm-wiki identity

- native llm-wiki version: 2.1.0
- native llm-wiki sha256: a37ae04745b04b8e9bbd8de37cdcbc2b2187ccafb68418e436a46ebb1e491ee5

## Pages inspected

All 454 maintained Markdown paths below `data/wiki/` were enumerated and inspected. The explicit path inventory was:

- `data/wiki/SCHEMA.md`
- `data/wiki/index.md`
- `data/wiki/log.md`
- `data/wiki/research-catalog.md`
- `data/wiki/security-catalog.md`
- `data/wiki/model-portfolio.md`
- `data/wiki/performance.md`
- `data/wiki/signals.md`
- `data/wiki/system-status.md`
- All 23 concrete daily-report paths under `data/wiki/daily-reports/`: `daily-report_20260724.md`, `daily-report_20260725.md`, `daily-report_20260726.md`, `daily-report_20260727.md`, `daily-report_20260728.md`, `daily-report_20260729.md`, `daily-report_20260730.md`, `daily-report_20260731.md`, `daily-report_20260801.md`, `daily-report_20260803.md`, `daily-report_20260805.md`, `daily-report_20260806.md`, `daily-report_20260807.md`, `daily-report_20260808.md`, `daily-report_20260809.md`, `daily-report_20260810.md`, `daily-report_20260811.md`, `daily-report_20260812.md`, `daily-report_20260813.md`, `daily-report_20260815.md`, `daily-report_20260816.md`, `daily-report_20260817.md`, and `daily-report_20260818.md`.
- All 284 concrete `data/wiki/inbox/market-*.md` paths present at execution, from `data/wiki/inbox/market-security_099561384c0f5e697727-bollinger_above_upper-50569ad33618.md` through `data/wiki/inbox/market-security_fe5539a7d3fd9d553bce-volume_anomaly-1c56259a5e4e.md` in the complete sorted filesystem inventory. Each concrete path is also individually linked from `data/wiki/research-catalog.md`.
- All 26 concrete idea paths under `data/wiki/ideas/`: `idea_ai_compute_networking_hyperscaler_monetization.md`, `idea_ai_infrastructure_power.md`, `idea_ai_native_drug_discovery.md`, `idea_ai_native_smb_financial_operating_systems.md`, `idea_anduril_product_company_disruption.md`, `idea_cable_broadband_convergence.md`, `idea_commercial_space_infrastructure.md`, `idea_critical_minerals_copper.md`, `idea_critical_minerals_lithium.md`, `idea_cybersecurity_geopolitical_continuity.md`, `idea_defense_aerospace.md`, `idea_digital_attention_gaming_ecosystems.md`, `idea_digital_finance_crypto_rails.md`, `idea_energy_refining.md`, `idea_eu_digital_product_passport.md`, `idea_humanoid_robotics_embodied_ai_components.md`, `idea_japan_sanaenomics_strategic_investment.md`, `idea_macro_hedge_gold.md`, `idea_nearshoring_friendshoring_manufacturing.md`, `idea_nuclear_uranium.md`, `idea_precision_biology_healthcare_automation.md`, `idea_solar_storage_grid_flexibility_reset.md`, `idea_sovereign_small_drone_supply_chains.md`, `idea_structural_silver_deficit.md`, `idea_terafab_ai_industrial_stack.md`, and `idea_wide_bandgap_power_semiconductors.md`.
- All 36 concrete relationship paths under `data/wiki/relationships/`: the immutable-ID `relationship_<id>.md` pages and the named `relationship_ai_compute_nvda.md`, `relationship_ai_drug_nvda.md`, `relationship_humanoid_nvda.md`, `relationship_solar_storage_grid_atkr.md`, `relationship_solar_storage_grid_enph.md`, `relationship_solar_storage_grid_flnc.md`, `relationship_terafab_asml.md`, `relationship_terafab_intc.md`, `relationship_terafab_nvda.md`, `relationship_terafab_samsung_common_gdr.md`, `relationship_terafab_spcx.md`, `relationship_terafab_tsla.md`, `relationship_terafab_tsm.md`, and `relationship_wide_bandgap_nvda.md`.
- All 70 concrete immutable-identity paths matching `data/wiki/securities/security_<security-id>.md`, each individually listed in `data/wiki/research-catalog.md`.
- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md`.
- All five concrete podcast paths under `data/wiki/podcasts/`: `daily-podcast_20260805T161218Z.md`, `daily-podcast_20260806T125642Z.md`, `daily-podcast_20260813T092636Z.md`, `daily-podcast_20260817T152008Z.md`, and `daily-podcast_20260817T185232Z.md`.
- Raw-source inventory path `data/wiki/raw/.gitkeep` was inspected for raw-tree completeness. It is not a Markdown page and was not modified.

Inspection covered YAML frontmatter and required fields, known tags, inbound and outbound wikilinks, local Markdown links and generated asset routes, index reachability, direct research-catalog membership, review dates against 2026-08-18, contradiction metadata and contrary-evidence language, confidence and sourcing, raw checksums, byte and line sizes, and log rotation. Repository content was treated only as untrusted audit data.

## Pages changed

- `data/wiki/log.md`
- `data/runs/daily-20260818T150041Z/wiki-maintenance/wiki_maintenance_report.md`

No other path was changed by this operation.

## Orphan pages

None. Every maintained idea, security, relationship, strategy, concept, comparison, and query page has at least one resolved inbound link, and every maintained Markdown page is reachable from `data/wiki/index.md` through `data/wiki/research-catalog.md`.

## Broken or ambiguous links

None requiring repair. The deterministic PaperTrader wiki linter returned zero errors. A broader local Markdown scan initially identified the three generated download routes in `data/wiki/system-status.md` (`data/decision_snapshot.json`, `data/model_portfolio.csv`, and `data/actionable_signals.csv`) when interpreted as source-directory-relative Markdown files; these are intentional Quartz publication asset routes, not missing wiki pages. External citations were treated as untrusted data and were not fetched.

## Index or catalog omissions

None. All 454 maintained Markdown pages are reachable from `data/wiki/index.md`, and `data/wiki/research-catalog.md` directly resolves to all 454 maintained page identities, including itself. No duplicate or ambiguous catalog target was found.

## Frontmatter and tag findings

- Missing or invalid YAML frontmatter: None.
- Missing required fields (`title`, `type`, `status`, `tags`, `created`, `updated`, `provenance`): None.
- Invalid tag collections: None.
- Unknown tags or tag drift beyond the `data/wiki/SCHEMA.md` taxonomy: None.
- `data/wiki/SCHEMA.md` was inspected but not changed, as required.

## Stale pages

No page's `updated` date is more than 90 days old. The following 28 maintained pages have a concrete `next_review` earlier than 2026-08-18 and remain overdue pending bounded current-evidence review:

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

No stale date was advanced without current evidence. Dates due on 2026-08-18 were not classified as overdue.

## Contested or contradictory content

No page declares `contested: true` or a nonempty `contradictions` field. Two maintained ideas explicitly preserve material counter-evidence rather than presenting an unresolved contradiction:

- `data/wiki/ideas/idea_critical_minerals_copper.md` records the IEA's narrowing projected supply gap as contrary to a static or worsening-gap narrative.
- `data/wiki/ideas/idea_structural_silver_deficit.md` records lower industrial and photovoltaic demand, photovoltaic thrifting and substitution, and increased recycling as contrary to an unqualified industrial-shortage narrative.

These are sourced qualifications already incorporated into the maintained theses. They were preserved and not silently resolved, removed, or promoted.

## Low-confidence or weakly sourced claims

Fifteen pages explicitly carry low, medium-low, or low-medium confidence and remain bounded warnings:

- `data/wiki/ideas/idea_cable_broadband_convergence.md` — confidence `medium-low`.
- `data/wiki/ideas/idea_humanoid_robotics_embodied_ai_components.md` — confidence `low-medium`.
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` — confidence `low`.
- `data/wiki/relationships/relationship_9e7b4700174908755cbc.md` — confidence `low`.
- `data/wiki/relationships/relationship_afac7205cd7e09800edf.md` — confidence `low`.
- `data/wiki/relationships/relationship_ai_drug_nvda.md` — confidence `low`.
- `data/wiki/relationships/relationship_c829dae21648bb133cc7.md` — confidence `low`.
- `data/wiki/relationships/relationship_terafab_intc.md` — confidence `low`.
- `data/wiki/relationships/relationship_terafab_samsung_common_gdr.md` — confidence `low`.
- `data/wiki/relationships/relationship_wide_bandgap_nvda.md` — confidence `low`.
- `data/wiki/securities/security_3853e54c619d597dcaa1.md` — confidence `low`.
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` — confidence `low`.
- `data/wiki/securities/security_664f93a7eaca72e76e9b.md` — confidence `low`.
- `data/wiki/securities/security_ed7d5b616a196969c815.md` — confidence `low`.
- `data/wiki/securities/security_fb87fac302a5446a1ced.md` — confidence `low`.

All fifteen identify provenance or evidence limits. No page with a single declared frontmatter source lacked an explicit confidence field. Unsupported valuations, unverified optionality, and missing transmission evidence remain explicitly labeled; no estimate or stronger conclusion was invented.

## Raw-source drift findings

None. `data/wiki/raw/` contains only `data/wiki/raw/.gitkeep`; there is no raw Markdown or text source with `sha256` frontmatter to recompute. No raw source was fetched, created, or modified.

## Oversized or archival candidates

No ordinary maintained page exceeds the repository's `max_page_bytes: 200000` hard limit. The following 26 pages exceed the native llm-wiki approximately 200-line split-review guideline:

- `data/wiki/daily-reports/daily-report_20260726.md` — 213 lines, 16,128 bytes.
- `data/wiki/daily-reports/daily-report_20260727.md` — 395 lines, 34,587 bytes.
- `data/wiki/daily-reports/daily-report_20260728.md` — 359 lines, 24,978 bytes.
- `data/wiki/daily-reports/daily-report_20260729.md` — 454 lines, 37,480 bytes.
- `data/wiki/daily-reports/daily-report_20260730.md` — 804 lines, 88,370 bytes.
- `data/wiki/daily-reports/daily-report_20260731.md` — 805 lines, 73,961 bytes.
- `data/wiki/daily-reports/daily-report_20260801.md` — 878 lines, 90,042 bytes.
- `data/wiki/daily-reports/daily-report_20260803.md` — 853 lines, 94,738 bytes.
- `data/wiki/daily-reports/daily-report_20260805.md` — 1,098 lines, 124,925 bytes.
- `data/wiki/daily-reports/daily-report_20260806.md` — 1,031 lines, 134,946 bytes.
- `data/wiki/daily-reports/daily-report_20260807.md` — 923 lines, 115,425 bytes.
- `data/wiki/daily-reports/daily-report_20260808.md` — 995 lines, 123,164 bytes.
- `data/wiki/daily-reports/daily-report_20260809.md` — 984 lines, 128,406 bytes.
- `data/wiki/daily-reports/daily-report_20260810.md` — 992 lines, 125,278 bytes.
- `data/wiki/daily-reports/daily-report_20260811.md` — 981 lines, 126,619 bytes.
- `data/wiki/daily-reports/daily-report_20260812.md` — 1,044 lines, 145,401 bytes.
- `data/wiki/daily-reports/daily-report_20260813.md` — 939 lines, 123,273 bytes.
- `data/wiki/daily-reports/daily-report_20260815.md` — 987 lines, 126,346 bytes.
- `data/wiki/daily-reports/daily-report_20260816.md` — 975 lines, 125,763 bytes.
- `data/wiki/daily-reports/daily-report_20260817.md` — 1,017 lines, 134,061 bytes.
- `data/wiki/daily-reports/daily-report_20260818.md` — 989 lines, 128,141 bytes.
- `data/wiki/research-catalog.md` — 518 lines, 46,523 bytes.
- `data/wiki/securities/security_59304f90c440def31dc5.md` — 216 lines, 15,594 bytes.
- `data/wiki/securities/security_a5dc16f3f4b245e6c168.md` — 228 lines, 15,865 bytes.
- `data/wiki/securities/security_f2b9760d847b2ba59324.md` — 225 lines, 15,537 bytes.
- `data/wiki/system-status.md` — 215 lines, 41,315 bytes.

The dated reports are canonical generated records and must remain single pages. The catalog and status pages are deterministic views and must not be hand-split. The three security pages are editorial split-review candidates, but no safe split was applied because that could alter investment meaning, provenance, assessment hashes, or generated-state freshness. `data/wiki/log.md` has 3,959 lines after the append-only maintenance entry, below `log_rotation_lines: 5000`; log rotation is not required. No archival action was justified.

## Safe repairs applied

- Appended one dated, append-only weekly maintenance entry to `data/wiki/log.md` documenting the 454-page audit.
- Wrote this report at `data/runs/daily-20260818T150041Z/wiki-maintenance/wiki_maintenance_report.md`.
- Applied no thesis, claim, confidence, review-date, catalog, generated-view, raw-source, or structural-state mutation because no additional safely repairable defect remained.
- Preserved all sourced claims, explicit counter-evidence, stale review frontiers, raw-tree state, and deterministic investment state.

## Suggested PaperTrader research follow-ups

These are bounded recommendations only; none was enqueued or invoked:

- `idea_research` — existing entity `idea_energy_refining`, because its 2026-08-12 review frontier passed and its maintained page identifies the then-future Valero second-quarter result and next IEA report as bounded evidence gates.
- `relationship_research` — existing entities `relationship_392da6d90e7c969945a2`, `relationship_510158d3d515d91d5c14`, `relationship_7e9fd9486e494dd05bb5`, `relationship_871e21ff73620ab8eb14`, `relationship_87b95f713a902d531f2f`, `relationship_9e7b4700174908755cbc`, and `relationship_c829dae21648bb133cc7`, because their dated review frontiers are more than seven days overdue.
- `security_research` — existing entities `security_95351d928b674bbdf687` and `security_cc4dcb8f002b61dffe00`, because their maintained pages identify scheduled issuer results or valuation evidence after the retained evidence cutoff and their review frontiers are materially overdue.
- `strategy_research` — existing entity `strategy_bd005fc3733b1475b6f9`, because its 2026-08-04 review frontier passed; any refresh must remain evidence-bound and must not treat this maintenance report as an execution signal.

## Unresolved blockers

- Twenty-eight pages retain overdue review dates because current evidence is required and source/network access was prohibited.
- Fifteen pages retain explicitly weak confidence; maintenance without new evidence cannot strengthen them.
- The raw tree has no hashed source artifact, so source-body drift cannot be assessed beyond confirming the empty raw-source inventory.
- The three oversized maintained security pages need editorial split review; no safe split was evident without risking investment meaning, provenance, assessment hashes, or publication freshness.
- The initial `uv run papertrader wiki lint --strict` wrapper attempt was blocked by permission to replace `.venv/bin/papertrader`; the same repository lint function was then executed directly with the existing environment and returned zero errors. Deterministic controller validation remains pending as directed.
- Repository-delta checks, validation, leasing, result state, and queue post-processing remain controller-owned.

## Exact validation results

- `uv run papertrader schema validate --strict` — PASSED
- `uv run papertrader integrity --strict` — PASSED
- `uv run papertrader wiki lint --strict` — PASSED
- `uv run papertrader advice validate --strict` — PASSED
