from __future__ import annotations

from papertrader.public_markdown import visible_machine_ids, visible_markdown


def test_public_markdown_ignores_frontmatter_and_link_destinations() -> None:
    markdown = (
        "---\n"
        "snapshot_id: decision_1234567890abcdef1234\n"
        "run_id: daily-20260805T220920Z\n"
        "---\n\n"
        "[[securities/security_1234567890abcdef1234|EXM]] and "
        "[report](daily-reports/daily-20260805T220920Z.md)\n"
    )

    assert visible_machine_ids(markdown) == ()
    assert "EXM" in visible_markdown(markdown)


def test_public_markdown_rejects_visible_machine_identity_and_hash() -> None:
    markdown = (
        "Security security_1234567890abcdef1234 used source "
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef."
    )

    assert visible_machine_ids(markdown) == (
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "security_1234567890abcdef1234",
    )


def test_unaliased_wikilink_identity_is_visible() -> None:
    assert visible_machine_ids("[[securities/security_1234567890abcdef1234]]") == (
        "security_1234567890abcdef1234",
    )
