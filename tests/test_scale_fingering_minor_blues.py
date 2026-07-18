"""Tests for Minor Blues scale fingerings (app output — pure cyclic multi-oct)."""

import pytest

from tests.scale_fingering_test_support import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

MINOR_BLUES_RH = {
  0: [2, 3, 1, 2, 3, 1, 2],
  1: [1, 2, 3, 1, 2, 3, 4],
  2: [2, 3, 1, 2, 3, 1, 2],
  4: [1, 2, 3, 1, 2, 3, 4],
  5: [2, 3, 1, 2, 3, 1, 2],
  6: [1, 2, 3, 1, 2, 3, 4],
  7: [2, 3, 1, 2, 3, 1, 2],
  9: [1, 2, 3, 1, 2, 3, 4],
  10: [2, 3, 1, 2, 3, 1, 2],
  11: [1, 2, 3, 1, 2, 3, 4],
}
MINOR_BLUES_LH = {
  0: [3, 2, 1, 2, 1, 2, 3],
  1: [4, 3, 2, 1, 2, 1, 2],
  2: [3, 2, 1, 2, 1, 2, 3],
  4: [4, 3, 2, 1, 2, 1, 2],
  5: [3, 2, 1, 2, 1, 2, 3],
  6: [4, 3, 2, 1, 2, 1, 2],
  7: [3, 2, 1, 2, 1, 2, 3],
  9: [4, 3, 2, 1, 2, 1, 2],
  10: [3, 2, 1, 2, 1, 2, 3],
  11: [4, 3, 2, 1, 2, 1, 2],
}
KEY_TO_PC = {"A":9,"E":4,"B":11,"F#":6,"C#":1,"D":2,"G":7,"C":0,"F":5,"Bb":10}
KEYS = ["A", "E", "B", "F#", "C#", "D", "G", "C", "F", "Bb"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_minor_blues.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_minor_blues_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=MINOR_BLUES_RH,
        left_patterns=MINOR_BLUES_LH,
        hand=hand,
        octaves=octaves,
    )
