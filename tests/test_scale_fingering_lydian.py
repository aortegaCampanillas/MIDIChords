"""Tests for Lydian scale fingerings.

LH identical to Harmonic Minor. RH differs for G#(8), D#(3), A(9), G(7)."""

import pytest

from tests.scale_fingering_test_support import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

LYDIAN_RH = {
    4: [1,2,3,1,2,3,4,5], 11:[1,2,3,1,2,3,4,5], 6: [1,2,3,1,2,3,4,5],
    1: [1,2,3,1,2,3,4,5], 8: [1,2,3,1,2,3,4,5], 3: [1,2,3,1,2,3,4,5],
    9: [1,2,3,4,1,2,3,4], 2: [1,2,3,4,1,2,3,4],
    7: [2,3,4,1,2,3,4,1], 0: [2,3,4,1,2,3,4,1], 5: [2,3,4,1,2,3,4,1],
    10:[2,3,4,1,2,3,4,1],
}
LYDIAN_LH = {  # identical to HARMONIC_MINOR_LH
    4: [5,4,3,2,1,3,2,1], 11:[5,4,3,2,1,3,2,1], 6: [5,4,3,2,1,3,2,1],
    1: [5,4,3,2,1,3,2,1], 8: [5,4,3,2,1,3,2,1], 3: [5,4,3,2,1,3,2,1],
    9: [5,4,3,2,1,3,2,1], 2: [5,4,3,2,1,3,2,1],
    7: [3,2,1,4,3,2,1,3], 0: [3,2,1,4,3,2,1,3], 5: [3,2,1,4,3,2,1,3],
    10:[3,2,1,4,3,2,1,3],
}
KEY_TO_PC = {
    "E":4,"B":11,"F#":6,"C#":1,"G#":8,"D#":3,
    "A":9,"D":2,"G":7,"C":0,"F":5,"Bb":10,
}
LYDIAN_KEYS = ["E","B","F#","C#","G#","D#","A","D","G","C","F","Bb"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_lydian.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", LYDIAN_KEYS)
def test_lydian_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=LYDIAN_RH,
        left_patterns=LYDIAN_LH,
        hand=hand,
        octaves=octaves,
    )
