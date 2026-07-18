"""Tests for Locrian scale fingerings (app output — pure cyclic multi-oct)."""

import pytest

from tests.scale_fingering_test_support import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

LOCRIAN_RH = {
  0: [2, 3, 4, 1, 2, 3, 4, 1],
  1: [1, 2, 3, 1, 2, 3, 4, 5],
  2: [2, 3, 4, 1, 2, 3, 4, 1],
  3: [1, 2, 3, 1, 2, 3, 4, 5],
  4: [1, 2, 3, 4, 1, 2, 3, 4],
  5: [2, 3, 4, 1, 2, 3, 4, 1],
  6: [1, 2, 3, 1, 2, 3, 4, 5],
  7: [2, 3, 4, 1, 2, 3, 4, 1],
  8: [1, 2, 3, 1, 2, 3, 4, 5],
  9: [1, 2, 3, 4, 1, 2, 3, 4],
  11: [1, 2, 3, 1, 2, 3, 4, 5],
}
LOCRIAN_LH = {
  0: [3, 2, 1, 4, 3, 2, 1, 3],
  1: [5, 4, 3, 2, 1, 3, 2, 1],
  2: [3, 2, 1, 4, 3, 2, 1, 3],
  3: [5, 4, 3, 2, 1, 3, 2, 1],
  4: [5, 4, 3, 2, 1, 3, 2, 1],
  5: [3, 2, 1, 4, 3, 2, 1, 3],
  6: [5, 4, 3, 2, 1, 3, 2, 1],
  7: [3, 2, 1, 4, 3, 2, 1, 3],
  8: [5, 4, 3, 2, 1, 3, 2, 1],
  9: [5, 4, 3, 2, 1, 3, 2, 1],
  11: [5, 4, 3, 2, 1, 3, 2, 1],
}
KEY_TO_PC = {"B":11,"F#":6,"C#":1,"G#":8,"D#":3,"E":4,"A":9,"D":2,"G":7,"C":0,"F":5}
KEYS = ["B", "F#", "C#", "G#", "D#", "E", "A", "D", "G", "C", "F"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_locrian.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_locrian_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=LOCRIAN_RH,
        left_patterns=LOCRIAN_LH,
        hand=hand,
        octaves=octaves,
    )
