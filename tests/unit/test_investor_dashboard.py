from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import date
from pathlib import Path

from papertrader.advice import ActionableSignalView, ModelPortfolioRow, load_published_snapshot
from papertrader.investor_pages import (
    SECURITY_TABLE_COLUMNS,
    _buy_initiate_candidates,
    _column_header,
    _currency_amount,
    _data_fx_update,
    _homepage,
    _model_portfolio_page,
    _portfolio_html,
    _rounded_percentage,
    _securities_page,
    _signal_detail,
    _system_status_page,
    _utc_day,
)


def test_market_signal_detail_has_no_empty_limit_suffix() -> None:
    signal = ActionableSignalView(
        signal_id="signal_test",
        strategy_id="strategy_test",
        order_id="order_test",
        security_id="security_test",
        ticker="TEST",
        company_name="Test Security",
        action="buy",
        action_status="pending_order",
        copy_ready=True,
        quantity="7",
        order_type="market",
        limit_price="",
        currency="EUR",
        created_at="2026-07-24T12:00:00Z",
        expires_at="2026-07-25T12:00:00Z",
        market_data_as_of="2026-07-24T11:00:00Z",
        current_weight_pct="0",
        target_weight_pct="5",
        strategy_name="Test strategy",
        entry_rule="Test entry",
        exit_rule="Test exit",
        invalidation="Test invalidation",
        rationale="Test rationale",
        security_research_page="data/wiki/securities/security_test.md",
        strategy_research_page="data/wiki/strategies/strategy_test.md",
        research_page="data/wiki/strategies/strategy_test.md",
        reason_codes=(),
        legs=(),
    )

    lines = _signal_detail(signal)

    assert "- **Order:** market" in lines
    assert all(line == line.rstrip() for line in lines)


def test_securities_table_display_helpers_are_deterministic_and_safe() -> None:
    assert _rounded_percentage("12.6") == "13%"
    assert _rounded_percentage("-12.6") == "-13%"
    assert _rounded_percentage("2.5") == "2%"
    assert _rounded_percentage("3.5") == "4%"
    assert _rounded_percentage("") == "—"
    assert _utc_day("2026-09-01T18:13:42Z") == "2026-09-01"
    assert _utc_day("") == "—"
    assert _data_fx_update("2026-09-01T18:13:42Z", "") == "2026-09-01 / —"
    assert _data_fx_update("", "") == "— / —"
    assert _currency_amount("69.440", "USD", label="fixture") == "69.44 USD"
    assert _currency_amount("", "USD", label="fixture") == "—"

    header = _column_header("safe-key", "<Price>", 'Latest "price" & currency.')
    assert "<Price>" not in header
    assert "&lt;Price&gt;" in header
    assert "&quot;price&quot; &amp; currency." in header
    assert 'aria-describedby="security-column-help-safe-key"' in header
    assert 'role="tooltip"' in header


def test_securities_page_has_readable_columns_and_accessible_header_help(
    repository_root: Path,
) -> None:
    snapshot = load_published_snapshot(repository_root)
    rendered = _securities_page(
        repository_root,
        snapshot,
        date.fromisoformat(snapshot.report_date),
    )
    header = next(line for line in rendered.splitlines() if 'class="column-heading"' in line)
    tooltip_ids = re.findall(r'aria-describedby="([^"]+)"', header)

    assert len(SECURITY_TABLE_COLUMNS) == 10
    assert header.count('class="column-heading"') == 10
    assert header.count('class="column-help"') == 10
    assert len(tooltip_ids) == len(set(tooltip_ids)) == 10
    assert all(f'id="{tooltip_id}"' in header for tooltip_id in tooltip_ids)
    for _key, label, description, _alignment in SECURITY_TABLE_COLUMNS:
        assert label in header
        assert description.replace("'", "&#x27;") in header

    assert "Venue" not in header
    assert "Native mark" not in header
    assert "Base mark" not in header
    assert "Expected return" in header
    assert "Last data/FX update" in header
    assert "—%" not in rendered
    assert re.search(r"\| -?\d+(?:\.\d+)? [A-Z]{3} \| \d{4}-\d{2}-\d{2} /", rendered)
    assert not re.search(r"\| \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z /", rendered)


def test_portfolio_cards_escape_untrusted_labels_and_expose_scaler_references() -> None:
    row = ModelPortfolioRow(
        snapshot_id="decision_0123456789abcdefabcd",
        as_of="2026-07-24T12:00:00Z",
        holding_type="security",
        security_id="sec_escape",
        ticker='X" onmouseover="bad',
        company_name="<script>alert('bad')</script> & Co",
        instrument_type="equity",
        sleeve="conviction",
        current_weight_pct="0",
        target_weight_pct="10",
        current_value_base="0",
        target_value_base="1000",
        delta_value_base="1000",
        current_quantity="0",
        target_quantity="10",
        mark="100",
        mark_currency="EUR",
        mark_base="100",
        fx_rate_to_base="1",
        fx_as_of="2026-07-24T12:00:00Z",
        market_data_as_of="2026-07-24T12:00:00Z",
        action="buy",
        action_status="pending_order",
        strategy_id="strategy_escape",
        signal_id="signal_escape",
        order_id="order_escape",
        confidence="high",
        effective_score="80",
        downside_pct="-20",
        base_upside_pct="25",
        bear_fair_value="80",
        bear_return_pct="-20",
        bear_probability_pct="25",
        base_fair_value="125",
        base_return_pct="25",
        base_probability_pct="50",
        bull_fair_value="160",
        bull_return_pct="60",
        bull_probability_pct="25",
        expected_return_pct="22.5",
        confidence_adjusted_expected_return_pct="22.5",
        buy_below_price="100",
        canonical_rating="strong_buy",
        portfolio_action="initiate",
        evidence_state="eligible",
        rating_change_conditions="Reassess when the valuation evidence changes.",
        valuation_horizon_months="12",
        thesis_summary="Fixture",
        entry_rule="Fixture entry",
        exit_rule="Fixture exit",
        invalidation="Fixture invalidation",
        review_at="2026-08-24T12:00:00Z",
        security_research_page="data/wiki/securities/sec_escape.md",
        strategy_research_page="data/wiki/strategies/strategy_escape.md",
        research_page="data/wiki/securities/sec_escape.md",
        reason_codes=(),
    )

    rendered = _portfolio_html((row,), "EUR")

    assert "<script>" not in rendered
    assert "&lt;script&gt;alert(&#x27;bad&#x27;)&lt;/script&gt; &amp; Co" in rendered
    assert 'data-scalable="true"' in rendered
    assert 'data-mark-currency="EUR"' in rendered
    assert 'data-market-data-as-of="2026-07-24T12:00:00Z"' in rendered
    assert "onmouseover=&quot;bad" in rendered

    excluded = _portfolio_html(
        (
            replace(
                row,
                target_value_base="-1000",
                target_weight_pct="-10",
            ),
        ),
        "EUR",
    )
    assert 'data-scalable="false"' in excluded


def test_dashboard_progressive_enhancement_is_local_and_long_equity_only(
    repository_root: Path,
) -> None:
    script = (
        repository_root / "site" / "papertrader" / "scripts" / "dashboard.inline.ts"
    ).read_text(encoding="utf-8")
    styles = (repository_root / "site" / "papertrader" / "styles.scss").read_text(encoding="utf-8")

    assert "navigator.clipboard.writeText" in script
    assert "row.scalable" in script
    assert "Math.floor" in script
    assert "Residual cash (target cash plus whole-share rounding)" in script
    assert "marketDataAsOf" in script
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "fetch(" not in script
    assert "XMLHttpRequest" not in script
    assert "WebSocket" not in script
    assert "@media (max-width: 800px)" in styles
    assert ".model-portfolio-grid" in styles
    assert 'body[data-slug="index"] .page-footer' in styles
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in styles
    assert ":focus-visible" in styles
    assert ".column-help-tooltip" in styles
    assert "&:focus .column-help-tooltip" in styles
    assert 'body[data-slug="security-catalog"]' in styles
    assert "min-width: 82rem" in styles


def test_dashboard_candidate_section_uses_only_buy_initiate_assessments(
    repository_root: Path,
) -> None:
    snapshot = load_published_snapshot(repository_root)
    fixture = snapshot.candidate_pipeline[0]
    included = replace(
        fixture,
        security_id="security_included",
        canonical_rating="buy",
        portfolio_action="initiate",
        expected_return_pct="20.7817678274164750316066337",
        reason_labels=("The comparable assessment is stale or expired.",),
    )
    wrong_rating = replace(
        fixture,
        security_id="security_wrong_rating",
        canonical_rating="hold",
        portfolio_action="initiate",
    )
    wrong_action = replace(
        fixture,
        security_id="security_wrong_action",
        canonical_rating="strong_buy",
        portfolio_action="watch",
    )
    synthetic = replace(
        snapshot,
        candidate_pipeline=(wrong_rating, *([included] * 6), wrong_action),
    )

    candidates = _buy_initiate_candidates(synthetic)
    homepage = _homepage(
        synthetic,
        date.fromisoformat(synthetic.report_date),
        "daily-reports/daily-report_20260903",
    )

    assert candidates == (included,) * 6
    assert all(candidate.canonical_rating in {"buy", "strong_buy"} for candidate in candidates)
    assert all(candidate.portfolio_action == "initiate" for candidate in candidates)
    assert "expected return 21% · The comparable assessment is stale or expired." in homepage
    assert "expected 20.7817678274164750316066337%" not in homepage


def test_model_portfolio_omits_comparison_benchmark_and_status_uses_snapshot_backlog(
    repository_root: Path,
) -> None:
    snapshot = load_published_snapshot(repository_root)
    day = date.fromisoformat(snapshot.report_date)

    model_portfolio = _model_portfolio_page(snapshot, day)
    status = _system_status_page(repository_root, snapshot, day)

    assert "Comparison-only research benchmark" not in model_portfolio
    assert "Research comparison benchmark" not in model_portfolio
    assert "## Sequential research backlog" in status
    assert "Active research work" not in status
    assert str(snapshot.coverage.research_backlog_count) in status


def test_quartz_uses_external_dashboard_source_and_validated_publication_copy(
    repository_root: Path,
) -> None:
    site = repository_root / "site"
    layout = (site / "quartz.layout.ts").read_text(encoding="utf-8")
    navigation = (site / "papertrader" / "components" / "DecisionNavigation.tsx").read_text(
        encoding="utf-8"
    )
    build = (site / "build-quartz.mjs").read_text(encoding="utf-8")
    tsconfig = (site / "tsconfig.json").read_text(encoding="utf-8")
    package = (site / "package.json").read_text(encoding="utf-8")

    assert (site / "papertrader" / "components" / "DecisionNavigation.tsx").is_file()
    assert "./papertrader/components/DecisionNavigation" in layout
    assert "condition: (page) => !isDashboardPage(page)" in layout
    assert "condition: isHomepage" in layout
    assert "Component.Explorer" in layout
    assert "Component.Graph" in layout
    assert 'folderDefaultState: "collapsed"' in layout
    assert '!["tags", "inbox", "raw", "_meta", "_archive"].includes(' in layout
    assert "node.slugSegment" in layout
    assert '"security-catalog",' in layout
    assert '{ label: "Securities", slug: "security-catalog" }' in navigation
    assert '{ label: "Securities", slug: "securities" }' not in navigation
    assert '{ label: "Ideas", slug: "ideas", collectionPrefix: "ideas/" }' in navigation
    assert '{ label: "Podcasts", slug: "podcasts", collectionPrefix: "podcasts/" }' in navigation
    assert '"collectionPrefix" in link' in navigation
    assert "`${slug}/index`" in navigation
    assert "href={resolveRelative(current, destination)}" in navigation
    assert 'title: "Recently explored ideas"' in layout
    assert 'title: "Latest podcast transcripts"' in layout
    assert layout.count("limit: 3") == 2
    assert 'linkToMore: "ideas/" as SimpleSlug' in layout
    assert 'linkToMore: "podcasts/" as SimpleSlug' in layout
    assert '"papertrader/**/*.ts"' in tsconfig
    assert '"papertrader/**/*.tsx"' in tsconfig
    assert "prettier quartz.config.ts quartz.layout.ts papertrader" in package
    for name in (
        "decision_snapshot.json",
        "model_portfolio.csv",
        "actionable_signals.csv",
        "research_benchmark.csv",
    ):
        assert name in build
    assert "isSymbolicLink()" in build
    assert "CSV header does not match" in build
    assert "differs from decision_snapshot.json" in build
    assert "publication artifact hash changed during copy" in build
    assert "copyFileSync" in build


def test_quartz_research_charts_use_pinned_local_echarts_with_fallback(
    repository_root: Path,
) -> None:
    site = repository_root / "site"
    package = json.loads((site / "package.json").read_text(encoding="utf-8"))
    renderer = (site / "papertrader" / "scripts" / "research-charts.inline.ts").read_text(
        encoding="utf-8"
    )
    prepare = (site / "prepare-quartz.mjs").read_text(encoding="utf-8")
    layout = (site / "quartz.layout.ts").read_text(encoding="utf-8")

    assert package["dependencies"]["echarts"] == "6.0.0"
    assert "static/vendor/echarts/echarts.min.js" in renderer
    assert "cdn." not in renderer
    assert "fetch(" not in renderer
    assert "View chart data table" in renderer
    assert "View validated chart JSON" in renderer
    assert 'case "technical"' in renderer
    assert "Adjusted OHLC" in renderer
    assert "MACD histogram" in renderer
    assert "Download the canonical technical CSV" in renderer
    assert 'renderer: "svg"' in renderer
    assert "hydratedWikiCopy" in (site / "build-quartz.mjs").read_text(encoding="utf-8")
    assert "publishTechnicalSeries" in (site / "build-quartz.mjs").read_text(encoding="utf-8")
    assert '["LICENSE", "LICENSE"]' in prepare
    assert "ResearchCharts()" in layout
