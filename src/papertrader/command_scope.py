"""Operation-scoped PaperTrader CLI command policy shared by dispatch and validation."""

from __future__ import annotations

from collections.abc import Sequence

READ_ONLY_COMMAND_PREFIXES = frozenset(
    {
        ("portfolio", "reconcile"),
        ("queue", "validate"),
        ("schema", "validate"),
        ("wiki", "lint"),
        ("allocation", "readiness"),
        ("integrity",),
        ("runtime-whitelist", "validate"),
        ("research", "security-context"),
        ("research", "assessment-get"),
    }
)


def normalized_command(arguments: Sequence[str]) -> tuple[str, ...]:
    """Return command tokens without the optional repository selector."""

    command = tuple(arguments)
    if len(command) >= 2 and command[0] == "--repository":
        return command[2:]
    return command


def _matches(command: tuple[str, ...], prefix: tuple[str, ...]) -> bool:
    return command[: len(prefix)] == prefix


def command_allowed(
    operation_type: str,
    arguments: Sequence[str],
    *,
    youtube_video: bool = False,
    seekingalpha_lead: bool = False,
    pre_dispatch: bool = False,
    profile: str = "",
) -> bool:
    """Return whether one canonical CLI argument vector is allowed for an operation.

    The pre-dispatch check deliberately uses a superset for ``wiki_ingest`` because its
    fine-grained source kind is validated from the immutable payload after the run. The
    post-run validator remains the authoritative boundary for that conditional command.
    """

    command = normalized_command(arguments)
    if not command:
        return False
    if profile:
        from papertrader.profiles import profile_command_allowed

        if not profile_command_allowed(profile, command):
            return False
    if any(_matches(command, prefix) for prefix in READ_ONLY_COMMAND_PREFIXES):
        return True
    if _matches(command, ("issue", "record")):
        return True
    if _matches(command, ("wiki", "sync-technical-charts")):
        return operation_type in {"security_research", "quick_check_research"}
    if _matches(command, ("podcast", "validate-script")) or _matches(
        command, ("podcast", "render-draft")
    ):
        return operation_type == "daily_podcast"
    if _matches(command, ("queue", "enqueue")):
        return operation_type != "source_discovery"
    if _matches(command, ("seekingalpha", "enqueue-leads")):
        return operation_type == "source_discovery"
    if _matches(command, ("watchlist", "import")):
        return operation_type == "idea_research" or (
            operation_type == "wiki_ingest" and (pre_dispatch or youtube_video or seekingalpha_lead)
        )
    if _matches(command, ("research", "source", "record")):
        return operation_type in {"wiki_ingest", "security_research", "quick_check_research"}
    if _matches(command, ("research", "security", "upsert")):
        return operation_type in {"security_research", "quick_check_research"}
    if _matches(command, ("research", "assessment", "upsert")):
        return operation_type in {"security_research", "quick_check_research"}
    if _matches(command, ("research", "relationship", "upsert")):
        return operation_type == "relationship_research"
    if _matches(command, ("research", "strategy", "upsert")):
        return operation_type == "strategy_research"
    if _matches(command, ("signal", "create")):
        return operation_type == "strategy_research"
    if _matches(command, ("order", "create")) or _matches(command, ("order", "create-baseline")):
        return operation_type == "execute_strategy"
    if _matches(command, ("order", "cancel")):
        return operation_type == "execute_strategy"
    return False
