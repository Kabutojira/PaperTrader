from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from papertrader.advice import ModelPortfolioRow
from papertrader.investor_pages import _portfolio_html


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
        approved_target_weight_pct="10",
        current_value_base="0",
        approved_target_value_base="1000",
        delta_value_base="1000",
        current_quantity="0",
        approved_target_quantity="10",
        mark="100",
        mark_currency="EUR",
        fx_rate_to_base="1",
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
        valuation_horizon_months="12",
        thesis_summary="Fixture",
        entry_rule="Fixture entry",
        exit_rule="Fixture exit",
        invalidation="Fixture invalidation",
        review_at="2026-08-24T12:00:00Z",
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
                approved_target_value_base="-1000",
                approved_target_weight_pct="-10",
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
    assert ":focus-visible" in styles


def test_quartz_uses_external_dashboard_source_and_validated_publication_copy(
    repository_root: Path,
) -> None:
    site = repository_root / "site"
    layout = (site / "quartz.layout.ts").read_text(encoding="utf-8")
    build = (site / "build-quartz.mjs").read_text(encoding="utf-8")
    tsconfig = (site / "tsconfig.json").read_text(encoding="utf-8")
    package = (site / "package.json").read_text(encoding="utf-8")

    assert (site / "papertrader" / "components" / "DecisionNavigation.tsx").is_file()
    assert "./papertrader/components/DecisionNavigation" in layout
    assert "condition: (page) => !isDashboardPage(page)" in layout
    assert '"papertrader/**/*.ts"' in tsconfig
    assert '"papertrader/**/*.tsx"' in tsconfig
    assert "prettier quartz.config.ts quartz.layout.ts papertrader" in package
    for name in (
        "decision_snapshot.json",
        "model_portfolio.csv",
        "actionable_signals.csv",
    ):
        assert name in build
    assert "isSymbolicLink()" in build
    assert "CSV header does not match" in build
    assert "differs from decision_snapshot.json" in build
    assert "publication artifact hash changed during copy" in build
    assert "copyFileSync" in build
