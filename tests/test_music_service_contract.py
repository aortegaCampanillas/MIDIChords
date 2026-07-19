from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from midichords.core.music_service import detect_chord, generate_chord, generate_scale


CONTRACT_PATH = Path(__file__).with_name("fixtures") / "music_service_contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def evaluate(operation: str, values: dict[str, Any]) -> dict[str, Any]:
    if operation == "generate_chord":
        return generate_chord(**values)
    if operation == "generate_scale":
        return generate_scale(**values)
    if operation == "detect_chord":
        return detect_chord(**values)
    raise AssertionError(f"Unknown contract operation: {operation}")


@pytest.mark.parametrize("case", CONTRACT["cases"], ids=lambda case: case["id"])
def test_python_music_service_matches_shared_contract(case):
    result = evaluate(case["operation"], case["input"])
    actual = {field: result[field] for field in case["expected"]}
    assert actual == case["expected"]
