"""Tests for Major Pentatonic scale fingerings (app output — pure cyclic multi-oct)."""

import pytest

from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

MAJOR_PENT_RH = {
  0: [1, 2, 3, 1, 2, 3],
  1: [2, 3, 1, 2, 3, 1],
  2: [1, 2, 3, 1, 2, 3],
  3: [2, 3, 1, 2, 3, 1],
  4: [1, 2, 3, 1, 2, 3],
  5: [2, 3, 1, 2, 3, 1],
  7: [1, 2, 3, 1, 2, 3],
  8: [2, 3, 1, 2, 3, 1],
  9: [1, 2, 3, 1, 2, 3],
  10: [2, 3, 1, 2, 3, 1],
}
MAJOR_PENT_LH = {
  0: [4, 3, 2, 1, 2, 1],
  1: [3, 2, 1, 2, 1, 3],
  2: [4, 3, 2, 1, 2, 1],
  3: [3, 2, 1, 2, 1, 3],
  4: [4, 3, 2, 1, 2, 1],
  5: [3, 2, 1, 2, 1, 3],
  7: [4, 3, 2, 1, 2, 1],
  8: [3, 2, 1, 2, 1, 3],
  9: [4, 3, 2, 1, 2, 1],
  10: [3, 2, 1, 2, 1, 3],
}
KEY_TO_PC = {"C":0,"G":7,"D":2,"A":9,"E":4,"F":5,"Bb":10,"Eb":3,"Ab":8,"Db":1}
KEYS = ["C", "G", "D", "A", "E", "F", "Bb", "Eb", "Ab", "Db"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_major_pentatonic.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_major_pentatonic_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=MAJOR_PENT_RH,
        left_patterns=MAJOR_PENT_LH,
        hand=hand,
        octaves=octaves,
    )
