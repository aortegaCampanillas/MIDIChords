"""Tests for Minor Pentatonic scale fingerings (app output — pure cyclic multi-oct)."""

import pytest

from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

MINOR_PENT_RH = {
  0: [2, 3, 1, 2, 3, 1],
  1: [1, 2, 3, 1, 2, 3],
  2: [2, 3, 1, 2, 3, 1],
  4: [1, 2, 3, 1, 2, 3],
  5: [2, 3, 1, 2, 3, 1],
  6: [1, 2, 3, 1, 2, 3],
  7: [2, 3, 1, 2, 3, 1],
  9: [1, 2, 3, 1, 2, 3],
  10: [2, 3, 1, 2, 3, 1],
  11: [1, 2, 3, 1, 2, 3],
}
MINOR_PENT_LH = {
  0: [3, 2, 1, 2, 1, 3],
  1: [4, 3, 2, 1, 2, 1],
  2: [3, 2, 1, 2, 1, 3],
  4: [4, 3, 2, 1, 2, 1],
  5: [3, 2, 1, 2, 1, 3],
  6: [4, 3, 2, 1, 2, 1],
  7: [3, 2, 1, 2, 1, 3],
  9: [4, 3, 2, 1, 2, 1],
  10: [3, 2, 1, 2, 1, 3],
  11: [4, 3, 2, 1, 2, 1],
}
KEY_TO_PC = {"A":9,"E":4,"B":11,"F#":6,"C#":1,"D":2,"G":7,"C":0,"F":5,"Bb":10}
KEYS = ["A", "E", "B", "F#", "C#", "D", "G", "C", "F", "Bb"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_minor_pentatonic.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_minor_pentatonic_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=MINOR_PENT_RH,
        left_patterns=MINOR_PENT_LH,
        hand=hand,
        octaves=octaves,
    )
