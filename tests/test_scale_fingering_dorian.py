"""Tests for Dorian scale fingerings.

LH is identical to Harmonic Minor. RH differs for D (pc=2) and C (pc=0).
"""
import pytest

from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

DORIAN_RH = {
    2: [1,2,3,1,2,3,4,5], 9: [1,2,3,1,2,3,4,5], 4: [1,2,3,1,2,3,4,5],
    11:[1,2,3,1,2,3,4,5], 6: [1,2,3,1,2,3,4,5], 1: [1,2,3,1,2,3,4,5],
    7: [1,2,3,4,1,2,3,4], 0: [1,2,3,4,1,2,3,4],
    5: [2,3,4,1,2,3,4,1], 10:[2,3,4,1,2,3,4,1], 3: [2,3,4,1,2,3,4,1],
    8: [2,3,4,1,2,3,4,1],
}
DORIAN_LH = {  # identical to HARMONIC_MINOR_LH
    2: [5,4,3,2,1,3,2,1], 9: [5,4,3,2,1,3,2,1], 4: [5,4,3,2,1,3,2,1],
    11:[5,4,3,2,1,3,2,1], 6: [5,4,3,2,1,3,2,1], 1: [5,4,3,2,1,3,2,1],
    7: [5,4,3,2,1,3,2,1], 0: [5,4,3,2,1,3,2,1],
    5: [3,2,1,4,3,2,1,3], 10:[3,2,1,4,3,2,1,3], 3: [3,2,1,4,3,2,1,3],
    8: [3,2,1,4,3,2,1,3],
}
KEY_TO_PC = {
    "D":2,"A":9,"E":4,"B":11,"F#":6,"C#":1,
    "G":7,"C":0,"F":5,"Bb":10,"Eb":3,"Ab":8,
}


DORIAN_KEYS = ["D","A","E","B","F#","C#","G","C","F","Bb","Eb","Ab"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_dorian.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", DORIAN_KEYS)
def test_dorian_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=DORIAN_RH,
        left_patterns=DORIAN_LH,
        hand=hand,
        octaves=octaves,
    )
