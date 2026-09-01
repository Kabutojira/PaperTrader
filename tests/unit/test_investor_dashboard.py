from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from papertrader.advice import ActionableSignalView, ModelPortfolioRow
from papertrader.investor_pages import _portfolio_html, _signal_detail


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
    assert '{ label: "Securities", slug: "security-catalog" }' in navigation
    assert '{ label: "Securities", slug: "securities" }' not in navigation
    assert '{ label: "Ideas", slug: "ideas", collectionPrefix: "ideas/" }' in navigation
    assert '{ label: "Podcasts", slug: "podcasts", collectionPrefix: "podcasts/" }' in navigation
    assert 'title: "Recently explored ideas"' in layout
    assert 'title: "Latest podcast transcripts"' in layout
    assert layout.count("limit: 3") == 2
    assert 'linkToMore: "ideas" as SimpleSlug' in layout
    assert 'linkToMore: "podcasts" as SimpleSlug' in layout
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
    assert 'renderer: "svg"' in renderer
    assert '["LICENSE", "LICENSE"]' in prepare
    assert "ResearchCharts()" in layout
