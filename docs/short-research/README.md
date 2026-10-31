# Bearish-universe intake and execution evidence

This extension starts from `c1a4f3a1b9013af38ec249adfae6739d55ca3190`
on `feature/short-research`. The eight files in `imports/` are actual manual CLI
requests, each containing two companies. They are intake records, not research
assessments or sources of valuation authority.

## Actual intake and market checks — 2026-10-31 UTC

All eight batches ran sequentially through
`uv run papertrader import-candidates --request ... --apply` and passed canonical
validation after each batch. All 16 instruments were new: there were no matching
existing instruments or issuer identities to merge. Each has a distinct immutable
security/issuer ID, a source-registered page and its requested research role.
The 94 existing securities preserve every pre-existing field; only `research_role`
was added with `long`. All 94 existing assessment rows, including their dates,
values and evidence, remain unchanged. Existing company/idea prose is unchanged.

The first identity check exposed a compatibility bug: installed yfinance returns
a lazy `Mapping`, while the importer required `dict`. The narrow repair accepts
mapping metadata and reads only six identity keys, avoiding unrelated lazy network
requests. It preserves every exact issuer/symbol/exchange/currency/equity gate and
the eight-request identity budget. Regression tests cover non-dict lazy mappings
and incomplete responses. After repair, actual provider checks succeeded for all
16 symbols; the CLI independently repeated verification during each import.
Initial plain HTTP diagnostics returned Yahoo 429; this was not used as grounds
to infer delisting. Some IR subdomains returned 403; accessible issuer corporate
sites and direct issuer releases were verified through the existing broker instead.
Corporate homepages establish intake provenance, not financial evidence.

Actual `papertrader market --apply` succeeded: two provider batches, 33 HTTP
requests, no failed tickers. All 16 new instruments have native USD prices dated
2026-10-30, the latest completed US exchange session at execution. Market refresh
made no model calls and changed no fair values or assessment dates.

## Identity and corporate-action review

Primary issuer/exchange disclosures were reviewed alongside current independent
yfinance listing metadata. XNAS = Nasdaq; XNYS = NYSE. These are current listed
equity instruments, not their former SPAC symbols, warrants or ordinary shares
underlying an ADS. Historical events below prevent mixing pre-action share units
with current quotes; they are not valuations or an assertion that no other
financing/corporate events exist. Complete current capitalization and funding
analysis remains part of the blocked fundamental review.

| Ticker | Current issuer / instrument | MIC / currency | Material history or identity evidence reviewed |
| --- | --- | --- | --- |
| FCEL | FuelCell Energy, Inc.; common stock | XNAS / USD | [2024 1-for-30 reverse split](https://investor.fce.com/press-releases/press-release-details/2024/FuelCell-Energy-Announces-1-For-30-Reverse-Stock-Split/) |
| AI | C3.ai, Inc.; Class A common stock | XNYS / USD | [Issuer stock history](https://ir.c3.ai/stock-information/historic-price-lookup); retain Class A instrument identity |
| SPCE | Virgin Galactic Holdings, Inc.; common stock | XNYS / USD | [2024 1-for-20 reverse split](https://investors.virgingalactic.com/news/news-details/2024/Virgin-Galactic-to-Effect-a-Reverse-Stock-Split/default.aspx) |
| CIFR | Cipher Digital Inc.; common stock | XNAS / USD | [2026-02-20 rename from Cipher Mining; CIFR and CUSIP retained](https://www.sec.gov/Archives/edgar/data/1819989/000181998926000007/cifr-20260220.htm) |
| WULF | TeraWulf Inc.; common stock | XNAS / USD | [IKONICS business-combination history](https://investors.terawulf.com/sec-filings/quarterly-reports/content/0001083301-24-000147/0001083301-24-000147.pdf) |
| BBAI | BigBear.ai Holdings, Inc.; common stock | XNYS / USD | [GigCapital4 combination](https://ir.bigbear.ai/news-events/press-releases/detail/26/bigbear-ai-announces-completion-of-business-combination); [current legal registrant](https://ir.bigbear.ai/sec-filings/all-sec-filings/content/0001836981-26-000092/bbai-20260930.htm) |
| APLD | Applied Digital Corporation; common stock | XNAS / USD | [2022 rename from Applied Blockchain](https://ir.applieddigital.com/news-events/press-releases/detail/44/applied-blockchain-announces-official-name-change-to) |
| ONDS | Ondas Inc.; common stock | XNAS / USD | [January 2026 name-change announcement](https://ir.ondas.com/all-sec-filings/content/0001213900-26-000083/ea027135201ex99-1_ondas.htm); current provider and issuer agree on Ondas Inc. |
| AEVA | Aeva Technologies, Inc.; common stock | XNAS / USD | [2024 1-for-5 split](https://investors.aeva.com/static-files/6225d633-c31b-45e7-ba31-2473f74549f3); [issuer FAQ: Nasdaq and InterPrivate history](https://investors.aeva.com/ir-resources/investor-faqs) |
| PDYN | Palladyne AI Corp.; common stock | XNAS / USD | [Former Sarcos/STRC; PDYN effective April 2024](https://investor.palladyneai.com/ir-resources/faqs); [2023 1-for-6 split disclosed in current filing](https://investor.palladyneai.com/node/10726/ixbrl-viewer) |
| KSCP | Knightscope, Inc.; Class A common stock | XNAS / USD | [2024 1-for-50 split and CUSIP change](https://nasdaqtrader.com/TraderNews.aspx?id=ECA2024-426) |
| MVIS | MicroVision, Inc.; common stock | XNAS / USD | [2026 1-for-15 reverse split](https://ir.microvision.com/news/press-releases/detail/461/microvision-announces-reverse-split-of-common-stock-to) |
| PSNY | Polestar Automotive Holding UK PLC; Class A ADS | XNAS / USD | [2025-12-09 ADS ratio changed to 1 ADS : 30 ordinary shares](https://www.sec.gov/Archives/edgar/data/1884082/000188408226000006/R20.htm); canonical instrument description explicitly retains the ratio |
| PLUG | Plug Power Inc.; common stock | XNAS / USD | [2011 1-for-10 reverse split](https://www.ir.plugpower.com/press-releases/news-details/2011/PLUG-POWER-ANNOUNCES-1-FOR-10-REVERSE-STOCK-SPLIT-2011-5-19/) |
| ARQQ | Arqit Quantum Inc.; ordinary shares | XNAS / USD | [2024 1-for-25 reverse split](https://ir.arqit.uk/sec-filings/all-sec-filings/content/0001104659-24-101182/0001104659-24-101182.pdf); Cayman issuer, US-listed USD instrument |
| SPIR | Spire Global, Inc.; Class A common stock | XNYS / USD | [2023 1-for-8 reverse split](https://ir.spire.com/news-events/press-releases/detail/189/spire-global-effects-1-for-8-reverse-stock-split); [2026 NYSE-listed Class A instrument](https://ir.spire.com/sec-filings/all-sec-filings/content/0001193125-26-153094/0001193125-26-153094.pdf) |

## Fundamental research blockage

The user explicitly chose to keep Actions workflows unchanged and document blocked
research. The existing research workflow always checks out/commits `main`; it was
not dispatched against these unmerged feature-branch identities. The local pinned
Hermes executable `/opt/hermes/.venv/bin/python` is absent. No alternate model,
credential workaround, source-validation exception or fabricated result was used.

Each new security was submitted to the existing explicit single-security research
CLI in the requested order (the ten active candidates first). The per-operation
result, canonical validation and page existence were checked before continuing.
These attempts fail at the isolated-worker preflight before inference or research
web calls. An operation attempt is not a measured model API call or completed
assessment. Failed tasks retain the normal retry/backoff and two-attempt ceiling;
no attempt was reset, and production defaults remain three sequential operations,
30 pending tasks and 30-day maximum assessment freshness.

All 16 pages therefore remain **unresearched intake pages**, prominently Unrated.
No new fair values, financial scores, confidence, research dates, fundamental
conclusions or options statistics are asserted. Genuine sections A–F, current
primary financial review and defensible scenarios still require the isolated worker.
The valid imported pages and sources are retained for normal queue processing or
an explicit manual continuation after review/merge with the existing runtime.

The current Pages pipeline requires the published exact SHA to belong to `main`.
This branch is delivered for review; it has not replaced the public site. A draft
PR and passing feature-branch checks cannot establish public deployment or full
research completion. Do not mark the user's public acceptance criterion complete
until research and the independent Pages deployment have actually succeeded.

## Per-company completion status

All entries share blocker H: isolated Hermes executable unavailable; zero research
web requests and zero inference calls. Every operation consumed one bounded attempt,
kept its intake page valid, and left a normal retry scheduled (attempts 1 of 2).
Optionability, put liquidity, spreads, implied volatility and catalysts are unknown
until a genuine review verifies them.

| Ticker | Research completion | Current opinion | Weighted fair value | Confidence | Blocker |
| --- | --- | --- | --- | --- | --- |
| [FCEL](../../data/wiki/securities/security_bb61343adcd613fd84e9.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [AI](../../data/wiki/securities/security_f9b4eb9ee3c847797e3b.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [SPCE](../../data/wiki/securities/security_c843b10b0d128d0fada8.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [CIFR](../../data/wiki/securities/security_abadc86a2ed7b5a86e32.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [WULF](../../data/wiki/securities/security_93ae4d1c015392716cd1.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [BBAI](../../data/wiki/securities/security_b493b89a6ed6fee5905e.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [APLD](../../data/wiki/securities/security_52702758461db03286f7.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [ONDS](../../data/wiki/securities/security_df72f58f926ed39b0675.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [AEVA](../../data/wiki/securities/security_2e9d3d6cb899976cc127.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [PDYN](../../data/wiki/securities/security_5d8b1483732cb8151b3e.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [KSCP](../../data/wiki/securities/security_5693568146922e796a14.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [MVIS](../../data/wiki/securities/security_d051c308c3e15b025fb1.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [PSNY](../../data/wiki/securities/security_f1238da5e465e051a47e.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [PLUG](../../data/wiki/securities/security_1d114694d447e35497b0.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [ARQQ](../../data/wiki/securities/security_c9b32b251703b0990793.md) | Imported; research preflight failed | Unrated | — | Unknown | H |
| [SPIR](../../data/wiki/securities/security_93d73f1a39279ecf6407.md) | Imported; research preflight failed | Unrated | — | Unknown | H |

## Validation and render review

Final local checks passed:276 Python tests (two existing exchange-calendar
warnings), Ruff lint/formatting, MyPy19 source files, strict `papertrader validate`,
locked `npm ci --prefix site --ignore-scripts`, and the localhost Quartz check/build.
The actual build parsed162 Markdown pages and emitted225 files; internal-link
validation passed. Local Node was25.8.1; exact-SHA CI verifies pinned24.4.1.

Headless browser review inspected the actual Shorts catalog on desktop/mobile,
the FCEL Unrated page and an existing ROBOTIS Strong Sell page. A synthetic
unit-test fixture separately verified the SHORT heading, reason, fair values,
confidence and scenario details; it is not a real company recommendation and was
never applied to canonical data. A small responsive fix lets the mobile grid and
search toolbar shrink. At390px the summary spans x16–374 with zero horizontal
scroll range; table columns remain horizontally scrollable. Site check/build/link
checks passed again after that CSS repair. The94-row preservation audit still passes.

Feature-branch CI and PR links are recorded in the delivery report. Public
publication and16 genuine fundamental assessments remain outstanding as described
above; local/render/mock checks do not establish either outcome.
