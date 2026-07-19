"""Tests for melodic-minor fingerings and their harmonic-minor parity."""

import pytest

from tests.support.harmonic_minor_fingering import (
    HARMONIC_MINOR_LH,
    HARMONIC_MINOR_RH,
    KEY_TO_PC,
)
from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

MELODIC_KEYS = ["A", "E", "B", "F#", "C#", "D", "G", "C", "F", "Bb", "Eb", "Ab"]
MELODIC_DATA = load_fingering_fixture("scale_fingering_melodic_minor.json")
HARMONIC_DATA = load_fingering_fixture("scale_fingering_harmonic_minor.json")


def test_melodic_minor_fingerings_match_harmonic_minor():
    """The application deliberately shares both complete fingering contracts."""
    for group in ("group1", "group2", "group3"):
        assert MELODIC_DATA[group] == HARMONIC_DATA[group]


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", MELODIC_KEYS)
def test_melodic_minor_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=MELODIC_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=HARMONIC_MINOR_RH,
        left_patterns=HARMONIC_MINOR_LH,
        hand=hand,
        octaves=octaves,
    )
