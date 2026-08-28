# PaperTrader wiki maintenance report

## Maintenance identity and execution date

- maintenance identity: wiki-maintenance:2026-W35
- execution date: 2026-08-28

## Native llm-wiki identity

- native llm-wiki version: 2.1.0
- native llm-wiki sha256: a37ae04745b04b8e9bbd8de37cdcbc2b2187ccafb68418e436a46ebb1e491ee5

## Pages inspected

All 618 Markdown paths present below `data/wiki/` were inspected. The explicit inventory scope was:

- `data/wiki/SCHEMA.md`
- `data/wiki/index.md`
- `data/wiki/log.md`
- `data/wiki/model-portfolio.md`
- `data/wiki/performance.md`
- `data/wiki/research-catalog.md`
- `data/wiki/security-catalog.md`
- `data/wiki/signals.md`
- `data/wiki/system-status.md`
- `data/wiki/_archive/log-2026.md` (one archived Markdown path)
- every `data/wiki/daily-reports/*.md` path (32 paths)
- every `data/wiki/ideas/*.md` path (28 paths)
- every `data/wiki/inbox/*.md` path (405 paths)
- every `data/wiki/podcasts/*.md` path (18 paths)
- every `data/wiki/relationships/*.md` path (46 paths)
- every `data/wiki/securities/*.md` path (78 paths)
- every `data/wiki/strategies/*.md` path (one path)
- `data/wiki/raw/` (no Markdown source path; only the non-Markdown placeholder `data/wiki/raw/.gitkeep` exists)

The orientation pass read `data/wiki/SCHEMA.md`, `data/wiki/index.md`, `data/wiki/research-catalog.md`, and the recent portion of `data/wiki/log.md` before the audit.

## Pages changed

- `data/wiki/log.md` — appended the required maintenance-lint record; no sourced conclusion was changed.
- `data/runs/daily-20260828T210155Z/wiki-maintenance/wiki_maintenance_report.md` — created this report at the sole allowed report path.

No other path was changed by this operation.

## Orphan pages

None. The maintained-page link graph and the project catalog/index conventions produced no unreferenced maintained research page.

## Broken or ambiguous links

None. No missing or multiply resolved wikilink target was found. The three ordinary Markdown links in `data/wiki/system-status.md` to `data/decision_snapshot.json`, `data/model_portfolio.csv`, and `data/actionable_signals.csv` are Quartz publication-asset paths rather than wikilinks; the official strict linter accepts them. No link target was opened or fetched.

## Index or catalog omissions

None. Every maintained catalog-eligible page was represented according to the specialized PaperTrader index and research-catalog rules. Generated inbox packets, canonical daily reports, and generated or delivery views were assessed under their schema-specific navigation rules rather than forced into the research catalog.

## Frontmatter and tag findings

- Invalid or missing required frontmatter: none.
- Malformed frontmatter dates or identity fields: none found.
- Unknown tags or tag drift outside the `data/wiki/SCHEMA.md` taxonomy: none.
- Exact `contested:` or `contradictions:` frontmatter markers: none present. The content-level tensions listed below remain explicit in prose and were not silently resolved.

## Stale pages

The following 54 maintained pages have a `next_review` or `next_review_at` date before 2026-08-28. Dates were not advanced without a substantive evidence review.

Ideas:

- `data/wiki/ideas/idea_ai_infrastructure_power.md` — 2026-08-26
- `data/wiki/ideas/idea_energy_refining.md` — 2026-08-12
- `data/wiki/ideas/idea_solar_storage_grid_flexibility_reset.md` — 2026-08-24

Relationships:

- `data/wiki/relationships/relationship_1655ac715c33506ec7da.md` — 2026-08-27
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` — 2026-08-14
- `data/wiki/relationships/relationship_297f9e36fb4e93a808e8.md` — 2026-08-14
- `data/wiki/relationships/relationship_392da6d90e7c969945a2.md` — 2026-07-30
- `data/wiki/relationships/relationship_510158d3d515d91d5c14.md` — 2026-08-07
- `data/wiki/relationships/relationship_670ed88c8e4616316a19.md` — 2026-08-15
- `data/wiki/relationships/relationship_7e9fd9486e494dd05bb5.md` — 2026-08-01
- `data/wiki/relationships/relationship_871e21ff73620ab8eb14.md` — 2026-08-06
- `data/wiki/relationships/relationship_87b95f713a902d531f2f.md` — 2026-08-04
- `data/wiki/relationships/relationship_9befaccc50d8cd94372b.md` — 2026-08-15
- `data/wiki/relationships/relationship_9e7b4700174908755cbc.md` — 2026-08-10
- `data/wiki/relationships/relationship_ad2f37b49980dbc73a08.md` — 2026-08-15
- `data/wiki/relationships/relationship_afac7205cd7e09800edf.md` — 2026-08-27
- `data/wiki/relationships/relationship_c829dae21648bb133cc7.md` — 2026-08-10
- `data/wiki/relationships/relationship_cbdd07edda84994325d6.md` — 2026-08-26
- `data/wiki/relationships/relationship_d9c8f578040386a487be.md` — 2026-08-14
- `data/wiki/relationships/relationship_def43e5b4e13577e2b99.md` — 2026-08-26
- `data/wiki/relationships/relationship_e5f55616b9beaf661080.md` — 2026-08-14
- `data/wiki/relationships/relationship_f2efab6050df0edcb762.md` — 2026-08-14
- `data/wiki/relationships/relationship_solar_storage_grid_atkr.md` — 2026-08-15
- `data/wiki/relationships/relationship_solar_storage_grid_enph.md` — 2026-08-15
- `data/wiki/relationships/relationship_solar_storage_grid_flnc.md` — 2026-08-15

Securities:

- `data/wiki/securities/security_0a56aa634d077fe5796f.md` — 2026-08-26
- `data/wiki/securities/security_0cf8075039299094d614.md` — 2026-08-19
- `data/wiki/securities/security_1c055eb9b2bb1f5a8ff2.md` — 2026-08-19
- `data/wiki/securities/security_2010347f1a0a5ea60f47.md` — 2026-08-20
- `data/wiki/securities/security_204be2a44063993de1a8.md` — 2026-08-20
- `data/wiki/securities/security_22c2b9d782a62d7a9b86.md` — 2026-08-15
- `data/wiki/securities/security_2c779e81c27b78c556bb.md` — 2026-08-20
- `data/wiki/securities/security_33d9c44facc75c726c7d.md` — 2026-08-19
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` — 2026-08-15
- `data/wiki/securities/security_47a0b06f6c6c478d7c1e.md` — 2026-08-25
- `data/wiki/securities/security_55c9ce2fdcd32dad6b8c.md` — 2026-08-22
- `data/wiki/securities/security_61567714298b9563d1a9.md` — 2026-08-20
- `data/wiki/securities/security_664f93a7eaca72e76e9b.md` — 2026-08-19
- `data/wiki/securities/security_66cdcf90aac0d83e76f3.md` — 2026-08-20
- `data/wiki/securities/security_6f9a1450edceb9307c9a.md` — 2026-08-23
- `data/wiki/securities/security_7bf8f4c9cc12ae410e40.md` — 2026-08-24
- `data/wiki/securities/security_7ca095d63423c55a90e3.md` — 2026-08-23
- `data/wiki/securities/security_97f38b2cb2d5ef127f5a.md` — 2026-08-23
- `data/wiki/securities/security_98470cfc01bbcde78fc2.md` — 2026-08-19
- `data/wiki/securities/security_a9eb9838940ef5ceaa0c.md` — 2026-08-20
- `data/wiki/securities/security_bdc2f87dadf134760c3a.md` — 2026-08-25
- `data/wiki/securities/security_c120e9f26ebb6159adf9.md` — 2026-08-24
- `data/wiki/securities/security_ce9b78a4d0773c950765.md` — 2026-08-20
- `data/wiki/securities/security_d08d763780400dfbffce.md` — 2026-08-20
- `data/wiki/securities/security_dfa34d4b9050964b465e.md` — 2026-08-20
- `data/wiki/securities/security_eca976f0076a425ea1bb.md` — 2026-08-20
- `data/wiki/securities/security_ed7d5b616a196969c815.md` — 2026-08-15
- `data/wiki/securities/security_fb87fac302a5446a1ced.md` — 2026-08-15

Strategy:

- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md` — 2026-08-04

## Contested or contradictory content

No pair of maintained pages was found to make an unmarked, directly incompatible canonical claim. Three material tensions are already surfaced and dated in maintained prose and were preserved:

- `data/wiki/ideas/idea_critical_minerals_copper.md` records that the IEA's projected 2035 copper gap narrowed as projects advanced, contrary to a static or continually worsening scarcity narrative.
- `data/wiki/ideas/idea_structural_silver_deficit.md` records industrial-demand weakness, photovoltaic thrifting/substitution, and recycling against an unqualified industrial-shortage narrative.
- `data/wiki/securities/security_3e597863f00753e8c65c.md` preserves the issuer's July response to accounting and scandium-supply allegations as a company response, not independent resolution.

These are evidence-bearing uncertainties, not safe mechanical repair targets. No claim was deleted and no contradiction was adjudicated.

## Low-confidence or weakly sourced claims

Fifteen maintained pages explicitly carry low-like confidence and remain correctly visible rather than being promoted without evidence:

- `data/wiki/ideas/idea_cable_broadband_convergence.md` — medium-low
- `data/wiki/ideas/idea_humanoid_robotics_embodied_ai_components.md` — low-medium
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` — low
- `data/wiki/relationships/relationship_9e7b4700174908755cbc.md` — low
- `data/wiki/relationships/relationship_afac7205cd7e09800edf.md` — low
- `data/wiki/relationships/relationship_ai_drug_nvda.md` — low
- `data/wiki/relationships/relationship_c829dae21648bb133cc7.md` — low
- `data/wiki/relationships/relationship_terafab_intc.md` — low
- `data/wiki/relationships/relationship_terafab_samsung_common_gdr.md` — low
- `data/wiki/relationships/relationship_wide_bandgap_nvda.md` — low
- `data/wiki/securities/security_3853e54c619d597dcaa1.md` — low
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` — low
- `data/wiki/securities/security_664f93a7eaca72e76e9b.md` — low
- `data/wiki/securities/security_ed7d5b616a196969c815.md` — low
- `data/wiki/securities/security_fb87fac302a5446a1ced.md` — low

Provenance frontmatter is present on maintained research pages. Broad keyword matches for unsupported or unverified evidence were retained as explicit research limitations; they were not treated as established fact or silently rewritten.

## Raw-source drift findings

None measurable. `data/wiki/raw/` contains no raw Markdown source or hash-bearing raw artifact, only `data/wiki/raw/.gitkeep`. Therefore there was no stored raw body whose declared SHA-256 could drift. The placeholder was not modified.

## Oversized or archival candidates

No page violates the PaperTrader project limit of 200,000 bytes. The native llm-wiki's general 200-line review heuristic identified these 38 maintained pages:

- Canonical daily reports: `data/wiki/daily-reports/daily-report_20260726.md` (213 lines), `daily-report_20260727.md` (395), `daily-report_20260728.md` (359), `daily-report_20260729.md` (454), `daily-report_20260730.md` (804), `daily-report_20260731.md` (805), `daily-report_20260801.md` (878), `daily-report_20260803.md` (853), `daily-report_20260805.md` (1,098), `daily-report_20260806.md` (1,031), `daily-report_20260807.md` (923), `daily-report_20260808.md` (995), `daily-report_20260809.md` (984), `daily-report_20260810.md` (992), `daily-report_20260811.md` (981), `daily-report_20260812.md` (1,044), `daily-report_20260813.md` (939), `daily-report_20260815.md` (987), `daily-report_20260816.md` (975), `daily-report_20260817.md` (1,017), `daily-report_20260818.md` (1,028), `daily-report_20260819.md` (1,134), `daily-report_20260820.md` (1,143), `daily-report_20260821.md` (1,227), `daily-report_20260822.md` (1,186), `daily-report_20260823.md` (1,176), `daily-report_20260824.md` (1,179), `daily-report_20260825.md` (1,167), `daily-report_20260826.md` (1,183), and `daily-report_20260828.md` (1,208). These are canonical generated records and are not archival or manual split candidates.
- Generated catalogs/status: `data/wiki/research-catalog.md` (681 lines) and `data/wiki/system-status.md` (235). These are generated or deterministic views and were not hand-edited.
- Security-page split candidates: `data/wiki/securities/security_099561384c0f5e697727.md` (213 lines), `security_59304f90c440def31dc5.md` (232), `security_96ba305ee7cd586bc348.md` (235), `security_a5dc16f3f4b245e6c168.md` (228), `security_dc7a111e297be528d96b.md` (205), and `security_f2b9760d847b2ba59324.md` (225). Splitting could alter stable research-page identity or investment context, so no automatic split was safe.

`data/wiki/log.md` contains 159 `##` entries after this maintenance entry, below the native 500-entry rotation threshold. No log rotation is required. No additional archival candidate was identified.

## Safe repairs applied

- Appended one dated lint entry to `data/wiki/log.md` recording scope and findings.
- Created this maintenance report.
- Preserved every sourced claim, review date, low-confidence marker, contradiction, canonical page identity, and generated view.
- No other safe repair was necessary because strict link, graph, catalog, frontmatter, tag, and size checks passed.

## Suggested PaperTrader research follow-ups

Recommendations only; no operation was enqueued.

- `idea_research`: bounded existing entities `idea_ai_infrastructure_power`, `idea_energy_refining`, and `idea_solar_storage_grid_flexibility_reset` for overdue reviews; `idea_cable_broadband_convergence` and `idea_humanoid_robotics_embodied_ai_components` for explicit low-like confidence.
- `security_research`: bounded existing entities `security_0a56aa634d077fe5796f`, `security_0cf8075039299094d614`, `security_1c055eb9b2bb1f5a8ff2`, `security_2010347f1a0a5ea60f47`, `security_204be2a44063993de1a8`, `security_22c2b9d782a62d7a9b86`, `security_2c779e81c27b78c556bb`, `security_33d9c44facc75c726c7d`, `security_4627aea1bf7d8943d3d8`, `security_47a0b06f6c6c478d7c1e`, `security_55c9ce2fdcd32dad6b8c`, `security_61567714298b9563d1a9`, `security_664f93a7eaca72e76e9b`, `security_66cdcf90aac0d83e76f3`, `security_6f9a1450edceb9307c9a`, `security_7bf8f4c9cc12ae410e40`, `security_7ca095d63423c55a90e3`, `security_97f38b2cb2d5ef127f5a`, `security_98470cfc01bbcde78fc2`, `security_a9eb9838940ef5ceaa0c`, `security_bdc2f87dadf134760c3a`, `security_c120e9f26ebb6159adf9`, `security_ce9b78a4d0773c950765`, `security_d08d763780400dfbffce`, `security_dfa34d4b9050964b465e`, `security_eca976f0076a425ea1bb`, `security_ed7d5b616a196969c815`, and `security_fb87fac302a5446a1ced` for overdue reviews; additionally `security_3853e54c619d597dcaa1` for explicit low confidence.
- `relationship_research`: bounded existing entities `relationship_1655ac715c33506ec7da`, `relationship_250194f6a9e3a1817632`, `relationship_297f9e36fb4e93a808e8`, `relationship_392da6d90e7c969945a2`, `relationship_510158d3d515d91d5c14`, `relationship_670ed88c8e4616316a19`, `relationship_7e9fd9486e494dd05bb5`, `relationship_871e21ff73620ab8eb14`, `relationship_87b95f713a902d531f2f`, `relationship_9befaccc50d8cd94372b`, `relationship_9e7b4700174908755cbc`, `relationship_ad2f37b49980dbc73a08`, `relationship_afac7205cd7e09800edf`, `relationship_c829dae21648bb133cc7`, `relationship_cbdd07edda84994325d6`, `relationship_d9c8f578040386a487be`, `relationship_def43e5b4e13577e2b99`, `relationship_e5f55616b9beaf661080`, `relationship_f2efab6050df0edcb762`, `relationship_solar_storage_grid_atkr`, `relationship_solar_storage_grid_enph`, and `relationship_solar_storage_grid_flnc` for overdue reviews; additionally `relationship_ai_drug_nvda`, `relationship_terafab_intc`, `relationship_terafab_samsung_common_gdr`, and `relationship_wide_bandgap_nvda` for explicit low confidence.
- `strategy_research`: bounded existing entity `strategy_bd005fc3733b1475b6f9` for its overdue 2026-08-04 review marker.
- `wiki_ingest`: None.

## Unresolved blockers

- Fifty-four review markers require current evidence and an operation-specific substantive review; changing dates mechanically would conceal staleness.
- Fifteen pages intentionally expose low-like confidence; raising confidence requires corroborating evidence.
- The three preserved content tensions require evidence-bearing research before any conclusion changes.
- Six security pages exceed the native general line-count heuristic, but automatic splitting could change stable identity or context and is not a safe maintenance-only edit.
- Raw-source drift cannot be tested without a hash-bearing raw artifact; no source was fetched because network and source access were prohibited.

## Exact validation results

- `uv run papertrader schema validate --strict` — PASSED
- `uv run papertrader integrity --strict` — PASSED
- `uv run papertrader wiki lint --strict` — PASSED
- `uv run papertrader advice validate --strict` — PASSED
