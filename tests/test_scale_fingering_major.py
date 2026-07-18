"""Tests for major scale fingering patterns and enharmonic spellings."""

import pytest

from tests.support.ionian_fingering import ionian_pattern, resolve_major_entry
from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_hand_fingering_data,
    load_fingering_fixture,
)

MAJOR_KEYS = ["C", "G", "D", "A", "E", "F", "Bb", "Eb", "Ab", "Db", "Gb", "B", "F#", "C#", "Cb"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_major.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", MAJOR_KEYS)
def test_major_fingering(key, hand, octaves):
    entry = resolve_major_entry(FIXTURE_DATA, key)
    assert_hand_fingering_data(
        pattern=ionian_pattern(key, hand),
        hand_data=entry[hand],
        octaves=octaves,
    )
