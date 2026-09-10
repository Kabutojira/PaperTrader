# PaperTrader wiki maintenance report

## Maintenance identity and execution date

- maintenance identity: wiki-maintenance:2026-W37
- execution date: 2026-09-10

## Native llm-wiki identity

- native llm-wiki version: 2.1.0
- native llm-wiki sha256: a37ae04745b04b8e9bbd8de37cdcbc2b2187ccafb68418e436a46ebb1e491ee5

## Pages inspected

The complete 837-page Markdown inventory under `data/wiki/` was inspected. The following explicit path sets are compressed only to keep the report usable; every matching pathname was individually included in the audit:

- `data/wiki/SCHEMA.md`
- `data/wiki/index.md`
- `data/wiki/log.md`
- `data/wiki/model-portfolio.md`
- `data/wiki/performance.md`
- `data/wiki/research-catalog.md`
- `data/wiki/security-catalog.md`
- `data/wiki/signals.md`
- `data/wiki/system-status.md`
- `data/wiki/_archive/log-2026.md` — one archived page.
- `data/wiki/daily-reports/*.md` — all 45 matching pages.
- `data/wiki/ideas/*.md` — all 29 matching pages.
- `data/wiki/inbox/*.md` — all 589 matching pages.
- `data/wiki/podcasts/*.md` — all 29 matching pages.
- `data/wiki/relationships/*.md` — all 47 matching pages.
- `data/wiki/securities/*.md` — all 83 matching pages.
- `data/wiki/strategies/*.md` — all five matching pages.
- `data/wiki/raw/` — inspected for source material and hash-bearing Markdown; it contains no Markdown source file and only `data/wiki/raw/.gitkeep`.

The audit covered required frontmatter, schema tags, reachability from `index.md` through `research-catalog.md`, wikilinks, catalog Markdown links, review dates, confidence markers, contradiction language, source-hash drift eligibility, page-size bounds, and log-rotation bounds.

## Pages changed

- `data/wiki/research-catalog.md`
- `data/wiki/log.md`
- `data/runs/daily-20260910T193402Z/wiki-maintenance/wiki_maintenance_report.md`

No raw source, schema, archive, structured state, market data, publication, accounting, portfolio, performance, skill, or source-code file was changed.

## Orphan pages

Before repair, `data/wiki/podcasts/daily-podcast_20260910T181020Z.md` was not reachable from the investor index through the complete research catalog. It was added to `data/wiki/research-catalog.md`.

No orphan maintained Markdown page remains in the audited reachability graph. `data/wiki/_archive/log-2026.md` is intentionally excluded from current-index reachability by the repository schema.

## Broken or ambiguous links

None found among maintained-page wikilinks or the index/catalog Markdown links covered by the PaperTrader wiki contract.

The generated download links in `data/wiki/system-status.md` target publication assets rather than Markdown wiki pages and were not misclassified as missing wiki pages. No external target was fetched or opened.

## Index or catalog omissions

One omission was found and repaired:

- Added `data/wiki/podcasts/daily-podcast_20260910T181020Z.md` to the Podcast section of `data/wiki/research-catalog.md`.

`data/wiki/index.md` remains a results-first homepage and links to the complete catalog; duplicating every maintained page into the homepage would violate its intended role. No remaining catalog omission was found.

## Frontmatter and tag findings

No invalid required frontmatter or unknown schema tag was found in the 836 current maintained pages plus the archived log. All current pages carry the required PaperTrader fields: `title`, `type`, `status`, `tags`, `created`, `updated`, and `provenance`.

`data/wiki/securities/security_ce9b78a4d0773c950765.md` does not carry an optional frontmatter `confidence` field, but its body explicitly states medium confidence. This is not a required-frontmatter failure. It was not edited because changing a security research page outside a bounded research operation could invalidate its hash-linked structured assessment.

No tag drift was found.

## Stale pages

No page is more than 90 days older than the 2026-09-10 execution date. The following 59 maintained pages nevertheless have an explicit `next_review` or `next_review_at` date before 2026-09-10 and therefore remain overdue under their own bounded review schedule:

- `data/wiki/ideas/idea_energy_refining.md` — 2026-08-12
- `data/wiki/ideas/idea_macro_hedge_gold.md` — 2026-08-28
- `data/wiki/ideas/idea_nuclear_uranium.md` — 2026-08-31
- `data/wiki/ideas/idea_solar_storage_grid_flexibility_reset.md` — 2026-08-24
- `data/wiki/relationships/relationship_1655ac715c33506ec7da.md` — 2026-08-27
- `data/wiki/relationships/relationship_250194f6a9e3a1817632.md` — 2026-08-14
- `data/wiki/relationships/relationship_297f9e36fb4e93a808e8.md` — 2026-08-14
- `data/wiki/relationships/relationship_392da6d90e7c969945a2.md` — 2026-07-30
- `data/wiki/relationships/relationship_510158d3d515d91d5c14.md` — 2026-08-07
- `data/wiki/relationships/relationship_670ed88c8e4616316a19.md` — 2026-08-15
- `data/wiki/relationships/relationship_7e9fd9486e494dd05bb5.md` — 2026-08-01
- `data/wiki/relationships/relationship_871e21ff73620ab8eb14.md` — 2026-08-06
- `data/wiki/relationships/relationship_87b95f713a902d531f2f.md` — 2026-08-04
- `data/wiki/relationships/relationship_9773364a04293a4febaf.md` — 2026-08-31
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
- `data/wiki/securities/security_0cf8075039299094d614.md` — 2026-08-19
- `data/wiki/securities/security_18a3ab0ee6086ee85d0f.md` — 2026-09-02
- `data/wiki/securities/security_1c055eb9b2bb1f5a8ff2.md` — 2026-08-19
- `data/wiki/securities/security_2010347f1a0a5ea60f47.md` — 2026-08-20
- `data/wiki/securities/security_22c2b9d782a62d7a9b86.md` — 2026-08-15
- `data/wiki/securities/security_37ddcbdaad296ad831f2.md` — 2026-09-04
- `data/wiki/securities/security_3853e54c619d597dcaa1.md` — 2026-08-31
- `data/wiki/securities/security_3a75fc1ccca2ee7c937a.md` — 2026-08-31
- `data/wiki/securities/security_4627aea1bf7d8943d3d8.md` — 2026-08-15
- `data/wiki/securities/security_488a9d7f7a8573597724.md` — 2026-09-02
- `data/wiki/securities/security_567d0d575bbd30aaa91d.md` — 2026-09-02
- `data/wiki/securities/security_59304f90c440def31dc5.md` — 2026-09-04
- `data/wiki/securities/security_61567714298b9563d1a9.md` — 2026-08-20
- `data/wiki/securities/security_664f93a7eaca72e76e9b.md` — 2026-08-19
- `data/wiki/securities/security_6ad1af8d10d6276a0221.md` — 2026-09-04
- `data/wiki/securities/security_6f9a1450edceb9307c9a.md` — 2026-08-23
- `data/wiki/securities/security_7bf8f4c9cc12ae410e40.md` — 2026-08-24
- `data/wiki/securities/security_7ca095d63423c55a90e3.md` — 2026-08-23
- `data/wiki/securities/security_89969b7dac39b7db5661.md` — 2026-08-31
- `data/wiki/securities/security_95351d928b674bbdf687.md` — 2026-09-02
- `data/wiki/securities/security_96ba305ee7cd586bc348.md` — 2026-09-03
- `data/wiki/securities/security_9d4049ed6669a52815d6.md` — 2026-09-05
- `data/wiki/securities/security_a9eb9838940ef5ceaa0c.md` — 2026-08-20
- `data/wiki/securities/security_ad5917642acbba28c1f2.md` — 2026-09-04
- `data/wiki/securities/security_b1f2c48e1a744f5ecf67.md` — 2026-09-04
- `data/wiki/securities/security_bdc2f87dadf134760c3a.md` — 2026-08-25
- `data/wiki/securities/security_c86bb4e75658c07142cf.md` — 2026-08-31
- `data/wiki/securities/security_c9a37d277445869a8809.md` — 2026-09-01
- `data/wiki/securities/security_cb88f9154cfeaa15e878.md` — 2026-09-07
- `data/wiki/securities/security_f2b9760d847b2ba59324.md` — 2026-08-29
- `data/wiki/securities/security_fb87fac302a5446a1ced.md` — 2026-08-15
- `data/wiki/strategies/strategy_bd005fc3733b1475b6f9.md` — 2026-08-04

No review date was advanced without current evidence.

## Contested or contradictory content

No `contested: true` or `contradictions:` frontmatter marker is present. The audit did find bounded contrary-evidence disclosures that are already preserved rather than silently reconciled:

- `data/wiki/securities/security_3e597863f00753e8c65c.md` keeps the issuer response to scandium-supply allegations separate from independent resolution.
- `data/wiki/securities/security_b19e8f0343b7da1f3c03.md` records operating evidence that contradicts a near-term operating-leverage thesis.
- `data/wiki/ideas/idea_structural_silver_deficit.md` records evidence against an unqualified industrial-shortage narrative.
- `data/wiki/ideas/idea_critical_minerals_copper.md` records a reduced projected supply gap against a static or worsening-gap narrative.
- `data/wiki/ideas/idea_terafab_ai_industrial_stack.md` preserves tension between near-term supplier demand and long-run vertical-integration ambitions.
- `data/wiki/ideas/idea_humanoid_robotics_embodied_ai_components.md` preserves the tension between broad ecosystem evidence and promotional evidence without unit economics.

Other contradiction-language matches explicitly say that measurement variation or refreshed evidence did not contradict the maintained conclusion. No material contradiction was silently removed or resolved.

## Low-confidence or weakly sourced claims

Fifteen pages retain an explicit low-like confidence marker and should not be hardened into high-confidence conclusions without evidence:

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

PaperTrader uses dated body citations and `provenance` rather than requiring a frontmatter `sources` list, so a mechanical one-source count would be unreliable. The low-like markers above and the explicit evidence gaps on the maintained pages remain the conservative quality signals. No unsupported claim was promoted and no source was fetched.

## Raw-source drift findings

None. `data/wiki/raw/` contains no Markdown source file and therefore no `sha256:` frontmatter to recompute; only `data/wiki/raw/.gitkeep` exists. This means there is no raw-source hash baseline to drift, not that external sources were revalidated. External source drift was not tested because network access was prohibited.

## Oversized or archival candidates

No current maintained page exceeds the repository's `max_page_bytes: 200000` limit. `data/wiki/log.md` is exempt from that byte limit and contains 3,758 lines after this maintenance entry, below the repository's `log_rotation_lines: 5000` threshold. Rotation is not required.

No page was archived or consolidated. Historical daily reports, inbox packets, and the existing archived log were retained because removing or coalescing them could alter audit provenance or investment meaning. No safe, meaning-preserving archival candidate was identified within this operation.

## Safe repairs applied

- Added the missing catalog link for `data/wiki/podcasts/daily-podcast_20260910T181020Z.md` to `data/wiki/research-catalog.md`.
- Appended this dated maintenance event to `data/wiki/log.md`.
- Wrote this report to `data/runs/daily-20260910T193402Z/wiki-maintenance/wiki_maintenance_report.md`.

No other repair was both evidence-independent and safe under the repository ownership boundaries.

## Suggested PaperTrader research follow-ups

The following are recommendations only; no operation was enqueued and no PaperTrader state-changing command was invoked:

- `idea_research` — bounded existing entities `idea_energy_refining`, `idea_macro_hedge_gold`, `idea_nuclear_uranium`, and `idea_solar_storage_grid_flexibility_reset`, each in a separate sequential operation, because their explicit review dates are overdue.
- `relationship_research` — bounded existing entities `relationship_1655ac715c33506ec7da`, `relationship_250194f6a9e3a1817632`, `relationship_297f9e36fb4e93a808e8`, `relationship_392da6d90e7c969945a2`, `relationship_510158d3d515d91d5c14`, `relationship_670ed88c8e4616316a19`, `relationship_7e9fd9486e494dd05bb5`, `relationship_871e21ff73620ab8eb14`, `relationship_87b95f713a902d531f2f`, `relationship_9773364a04293a4febaf`, `relationship_9befaccc50d8cd94372b`, `relationship_9e7b4700174908755cbc`, `relationship_ad2f37b49980dbc73a08`, `relationship_afac7205cd7e09800edf`, `relationship_c829dae21648bb133cc7`, `relationship_cbdd07edda84994325d6`, `relationship_d9c8f578040386a487be`, `relationship_def43e5b4e13577e2b99`, `relationship_e5f55616b9beaf661080`, `relationship_f2efab6050df0edcb762`, `relationship_solar_storage_grid_atkr`, `relationship_solar_storage_grid_enph`, and `relationship_solar_storage_grid_flnc`, each separately, because their explicit review dates are overdue. Low-confidence non-overdue relationships should be reviewed only when a new bounded cause exists.
- `security_research` — bounded existing entities `security_0cf8075039299094d614`, `security_18a3ab0ee6086ee85d0f`, `security_1c055eb9b2bb1f5a8ff2`, `security_2010347f1a0a5ea60f47`, `security_22c2b9d782a62d7a9b86`, `security_37ddcbdaad296ad831f2`, `security_3853e54c619d597dcaa1`, `security_3a75fc1ccca2ee7c937a`, `security_4627aea1bf7d8943d3d8`, `security_488a9d7f7a8573597724`, `security_567d0d575bbd30aaa91d`, `security_59304f90c440def31dc5`, `security_61567714298b9563d1a9`, `security_664f93a7eaca72e76e9b`, `security_6ad1af8d10d6276a0221`, `security_6f9a1450edceb9307c9a`, `security_7bf8f4c9cc12ae410e40`, `security_7ca095d63423c55a90e3`, `security_89969b7dac39b7db5661`, `security_95351d928b674bbdf687`, `security_96ba305ee7cd586bc348`, `security_9d4049ed6669a52815d6`, `security_a9eb9838940ef5ceaa0c`, `security_ad5917642acbba28c1f2`, `security_b1f2c48e1a744f5ecf67`, `security_bdc2f87dadf134760c3a`, `security_c86bb4e75658c07142cf`, `security_c9a37d277445869a8809`, `security_cb88f9154cfeaa15e878`, `security_f2b9760d847b2ba59324`, and `security_fb87fac302a5446a1ced`, each separately, because their explicit review dates are overdue.
- `strategy_research` — bounded existing entity `strategy_bd005fc3733b1475b6f9` because its explicit review date is overdue.

No `wiki_ingest` follow-up is justified: there is no registered raw Markdown source in `data/wiki/raw/` to ingest or refresh.

## Unresolved blockers

- The 59 overdue review markers and 15 low-like confidence markers require current evidence and operation-specific judgment; this maintenance operation could not safely resolve them.
- External source freshness and source drift were not checked because network access and source fetching were prohibited.
- Optional confidence metadata on `data/wiki/securities/security_ce9b78a4d0773c950765.md` was not changed because the page is hash-linked to structured assessment state owned outside wiki maintenance.
- Deterministic controller validation, repository-delta enforcement, lease/result state, and later queue processing remain controller-owned.

## Exact validation results

- `uv run papertrader schema validate --strict` — PASSED
- `uv run papertrader integrity --strict` — PASSED
- `uv run papertrader wiki lint --strict` — PASSED
- `uv run papertrader advice validate --strict` — PASSED
