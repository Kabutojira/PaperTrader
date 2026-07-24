"""Paper execution boundary; deterministic fill behavior is implemented in Step 2."""

from papertrader.config import Settings


def assert_paper_execution_enabled(settings: Settings) -> None:
    """Fail closed at the execution boundary if paper mode was not asserted."""

    if not settings.paper_trading_only:
        raise RuntimeError("execution requires PAPER_TRADING_ONLY=true")
