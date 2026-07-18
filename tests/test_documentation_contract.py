from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIVE_DOCS = (
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "PROJECT_SPEC.md",
    ROOT / "docs" / "ROADMAP.md",
    ROOT / "docs" / "archive" / "README.md",
    ROOT / "apps" / "mobile_flutter" / "README.md",
)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+\.md(?:#[^)]+)?)\)")


def test_live_documentation_uses_existing_relative_markdown_links() -> None:
    for document in LIVE_DOCS:
        text = document.read_text(encoding="utf-8")
        assert "/Users/" not in text, document
        for target in MARKDOWN_LINK.findall(text):
            relative = target.split("#", 1)[0]
            assert not relative.startswith("/"), (document, target)
            assert (document.parent / relative).resolve().is_file(), (
                document,
                target,
            )


def test_historical_plans_and_retired_modules_do_not_return_to_active_roots() -> None:
    obsolete_roots = (
        "COMPLETION_SUMMARY.md",
        "INTEGRATION_ROADMAP.md",
        "TODO_DESKTOP.md",
        "TODO_MOBILE.md",
        "PENDING_CHANGES.md",
    )
    for relative in obsolete_roots:
        assert not (ROOT / relative).exists(), relative

    retired_modules = (
        "midichords/ui/widgets.py",
        "midichords/core/circle_of_fifths.py",
        "apps/mobile_flutter/lib/changelog_utils.dart",
    )
    for relative in retired_modules:
        assert not (ROOT / relative).exists(), relative

    assert (ROOT / "docs" / "ROADMAP.md").is_file()
    assert (ROOT / "docs" / "archive" / "README.md").is_file()
