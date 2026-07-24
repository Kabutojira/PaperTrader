"""Pure Telegram MarkdownV2 escaping and bounded message splitting."""

from __future__ import annotations

TELEGRAM_MARKDOWN_V2_SPECIAL = "_*[]()~`>#+-=|{}.!\\"


def escape_markdown_v2(value: str) -> str:
    """Escape every Telegram MarkdownV2 metacharacter exactly once."""

    return "".join(
        f"\\{character}" if character in TELEGRAM_MARKDOWN_V2_SPECIAL else character
        for character in value
    )


def split_message(value: str, *, limit: int = 4096) -> tuple[str, ...]:
    """Split at line/space boundaries while preserving all content and hard limits."""

    if limit <= 0:
        raise ValueError("message limit must be positive")
    if not value:
        return ("",)
    chunks: list[str] = []
    remaining = value
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        else:
            split_at += 1
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]
    chunks.append(remaining)
    return tuple(chunks)
