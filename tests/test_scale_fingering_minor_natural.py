"""Natural minor uses the fingering of its relative major."""

import pytest

from tests.support.ionian_fingering import ionian_pattern, resolve_major_entry
from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    extend_fingering_pattern,
    load_fingering_fixture,
)

MINOR_KEYS = ["A", "E", "B", "F#", "C#", "G#", "D#", "A#", "D", "G", "C", "F", "Bb", "Eb", "Ab"]
MINOR_DATA = load_fingering_fixture("scale_fingering_minor_natural.json")
MAJOR_DATA = load_fingering_fixture("scale_fingering_major.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("minor_key", MINOR_KEYS)
def test_natural_minor_matches_relative_major(minor_key, hand, octaves):
    relation = MINOR_DATA[minor_key]
    major_key = relation["sameAsMajor"]
    major_reference = MAJOR_DATA[major_key].get("sameAs", major_key)
    major_hand = resolve_major_entry(MAJOR_DATA, major_key)[hand]
    asc_field = "1OctAsc" if octaves == "1Oct" else "2OctAsc_app"
    expected = major_hand[asc_field]
    actual = extend_fingering_pattern(
        ionian_pattern(
            major_key,
            hand,
            prefer_flat=(
                relation["preferFlat"]
                or "b" in major_reference
            ),
        ),
        len(expected),
    )
    assert actual == expected, (
        f"{minor_key} minor {hand} {octaves} should equal {major_key} major"
    )
