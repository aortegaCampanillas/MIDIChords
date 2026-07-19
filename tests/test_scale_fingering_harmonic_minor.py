"""Tests for harmonic-minor scale fingerings."""

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

HARMONIC_MINOR_KEYS = ["A", "E", "B", "F#", "C#", "D", "G", "C", "F", "Bb", "Eb", "Ab"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_harmonic_minor.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", HARMONIC_MINOR_KEYS)
def test_harmonic_minor_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=HARMONIC_MINOR_RH,
        left_patterns=HARMONIC_MINOR_LH,
        hand=hand,
        octaves=octaves,
    )
