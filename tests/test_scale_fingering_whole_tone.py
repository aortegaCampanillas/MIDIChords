"""Tests for Whole Tone scale fingerings (app output — pure cyclic multi-oct)."""

import pytest

from tests.scale_fingering_test_support import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

WHOLE_TONE_RH = {
  0: [1, 2, 3, 1, 2, 3, 1],
  1: [2, 3, 1, 2, 3, 1, 2],
  2: [1, 2, 3, 1, 2, 3, 1],
  3: [2, 3, 1, 2, 3, 1, 2],
  4: [1, 2, 3, 1, 2, 3, 1],
  5: [2, 3, 1, 2, 3, 1, 2],
  6: [1, 2, 3, 1, 2, 3, 1],
  7: [2, 3, 1, 2, 3, 1, 2],
  8: [1, 2, 3, 1, 2, 3, 1],
  9: [2, 3, 1, 2, 3, 1, 2],
  10: [1, 2, 3, 1, 2, 3, 1],
  11: [2, 3, 1, 2, 3, 1, 2],
}
WHOLE_TONE_LH = {
  0: [3, 2, 1, 3, 2, 1, 3],
  1: [3, 2, 1, 2, 1, 2, 3],
  2: [3, 2, 1, 3, 2, 1, 3],
  3: [3, 2, 1, 2, 1, 2, 3],
  4: [3, 2, 1, 3, 2, 1, 3],
  5: [3, 2, 1, 2, 1, 2, 3],
  6: [3, 2, 1, 3, 2, 1, 3],
  7: [3, 2, 1, 2, 1, 2, 3],
  8: [3, 2, 1, 3, 2, 1, 3],
  9: [3, 2, 1, 2, 1, 2, 3],
  10: [3, 2, 1, 3, 2, 1, 3],
  11: [3, 2, 1, 2, 1, 2, 3],
}
KEY_TO_PC = {"C":0,"D":2,"E":4,"F#":6,"G#":8,"A#":10,"C#":1,"D#":3,"F":5,"G":7,"A":9,"B":11}
KEYS = ["C", "D", "E", "F#", "G#", "A#", "C#", "D#", "F", "G", "A", "B"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_whole_tone.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_whole_tone_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=WHOLE_TONE_RH,
        left_patterns=WHOLE_TONE_LH,
        hand=hand,
        octaves=octaves,
    )
