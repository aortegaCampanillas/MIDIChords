from __future__ import annotations

import re
from pathlib import Path

from midichords.mixins.scales_mixin import MODAL_SCALE_DEGREES, SCALE_FAMILY_GROUPS


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _quoted(source: str, quote: str) -> list[str]:
    return re.findall(rf"{re.escape(quote)}([^{re.escape(quote)}]+){re.escape(quote)}", source)


def _web_groups() -> list[tuple[str, tuple[str, ...]]]:
    source = (PROJECT_ROOT / "apps/web/static/scale_theory.js").read_text(encoding="utf-8")
    block = source.split("const SCALE_FAMILY_GROUPS = Object.freeze([", 1)[1].split("\n  ]);", 1)[0]
    groups: list[tuple[str, tuple[str, ...]]] = []
    entry_pattern = re.compile(
        r'\["scale_group_([^"]+)",\s*(MODAL_SCALE_NAMES|\[(.*?)\])\],?', re.DOTALL
    )
    for key, value, explicit_names in entry_pattern.findall(block):
        names = tuple(MODAL_SCALE_DEGREES) if value == "MODAL_SCALE_NAMES" else tuple(_quoted(explicit_names, '"'))
        groups.append((key, names))
    return groups


def _mobile_groups() -> list[tuple[str, tuple[str, ...]]]:
    source = (PROJECT_ROOT / "apps/mobile_flutter/lib/music_catalog.dart").read_text(encoding="utf-8")
    block = source.split("const List<Map<String, Object>> scaleFamilyGroups", 1)[1].split("\n];", 1)[0]
    entries = re.findall(
        r"'key': '([^']+)',\s*'names': <String>\[(.*?)\],\s*}", block, re.DOTALL
    )
    return [(key, tuple(_quoted(names, "'"))) for key, names in entries]


def test_scale_family_contract_is_identical_on_every_platform() -> None:
    expected = [(key, tuple(names)) for key, names in SCALE_FAMILY_GROUPS]

    assert _web_groups() == expected
    assert _mobile_groups() == expected
