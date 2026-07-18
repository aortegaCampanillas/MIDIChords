from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURES_DIR = Path(__file__).with_name("fixtures")
HAND_OCTAVE_CASES = (
    ("rightHand", "1Oct"),
    ("leftHand", "1Oct"),
    ("rightHand", "2Oct"),
    ("leftHand", "2Oct"),
)


def load_fingering_fixture(filename: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / filename).read_text(encoding="utf-8"))


def extend_fingering_pattern(pattern: list[int], count: int) -> list[int]:
    """Extend one documented octave using the application's cyclic contract."""
    if len(pattern) == 8:
        if count <= 8:
            return pattern[:count]
        octave_boundary = 1 if pattern[0] == 1 else pattern[7]
        period = pattern[:7]
        result = []
        for index in range(count - 1):
            result.append(
                octave_boundary
                if index > 0 and index % 7 == 0
                else period[index % 7]
            )
        result.append(pattern[7])
        return result

    if count <= len(pattern):
        return pattern[:count]
    if pattern[0] == pattern[-1]:
        period = len(pattern) - 1
        return [pattern[index % period] for index in range(count - 1)] + [
            pattern[-1]
        ]
    return [pattern[index % len(pattern)] for index in range(count)]


def grouped_hand_data(
    fixture: dict[str, Any], key: str
) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    for group_name, group in fixture.items():
        if not group_name.startswith("group") or not isinstance(group, dict):
            continue
        if key in group.get("keys", []):
            return group["rightHand"], group["leftHand"]
    raise KeyError(key)


def assert_grouped_fingering_case(
    *,
    fixture: dict[str, Any],
    key: str,
    pitch_class_by_key: dict[str, int],
    right_patterns: dict[int, list[int]],
    left_patterns: dict[int, list[int]],
    hand: str,
    octaves: str,
) -> None:
    right_data, left_data = grouped_hand_data(fixture, key)
    hand_data = right_data if hand == "rightHand" else left_data
    patterns = right_patterns if hand == "rightHand" else left_patterns
    pitch_class = pitch_class_by_key[key]
    assert_hand_fingering_data(
        pattern=patterns[pitch_class], hand_data=hand_data, octaves=octaves
    )


def assert_hand_fingering_data(
    *, pattern: list[int], hand_data: dict[str, list[int]], octaves: str
) -> None:
    asc_field = "1OctAsc" if octaves == "1Oct" else "2OctAsc_app"
    desc_field = "1OctDesc" if octaves == "1Oct" else "2OctDesc_app"
    expected_ascending = hand_data[asc_field]
    actual_ascending = extend_fingering_pattern(pattern, len(expected_ascending))
    assert actual_ascending == expected_ascending
    assert list(reversed(actual_ascending)) == hand_data[desc_field]
