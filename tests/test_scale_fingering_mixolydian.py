"""Tests for Mixolydian scale fingerings."""

import pytest

from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_grouped_fingering_case,
    load_fingering_fixture,
)

MIXOLYDIAN_RH = {
    7:[1,2,3,1,2,3,4,5],2:[1,2,3,1,2,3,4,5],9:[1,2,3,1,2,3,4,5],
    4:[1,2,3,1,2,3,4,5],11:[1,2,3,1,2,3,4,5],6:[1,2,3,1,2,3,4,5],
    0:[1,2,3,4,1,2,3,4],5:[1,2,3,4,1,2,3,4],
    10:[2,3,4,1,2,3,4,1],3:[2,3,4,1,2,3,4,1],8:[2,3,4,1,2,3,4,1],1:[2,3,4,1,2,3,4,1],
}
MIXOLYDIAN_LH = {
    7:[5,4,3,2,1,3,2,1],2:[5,4,3,2,1,3,2,1],9:[5,4,3,2,1,3,2,1],
    4:[5,4,3,2,1,3,2,1],11:[5,4,3,2,1,3,2,1],6:[5,4,3,2,1,3,2,1],
    0:[5,4,3,2,1,3,2,1],5:[5,4,3,2,1,3,2,1],
    10:[3,2,1,4,3,2,1,3],3:[3,2,1,4,3,2,1,3],8:[3,2,1,4,3,2,1,3],1:[3,2,1,4,3,2,1,3],
}
KEY_TO_PC = {"G":7,"D":2,"A":9,"E":4,"B":11,"F#":6,"C":0,"F":5,"Bb":10,"Eb":3,"Ab":8,"Db":1}
KEYS = ["G","D","A","E","B","F#","C","F","Bb","Eb","Ab","Db"]
FIXTURE_DATA = load_fingering_fixture("scale_fingering_mixolydian.json")


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
@pytest.mark.parametrize("key", KEYS)
def test_mixolydian_fingering(key, hand, octaves):
    assert_grouped_fingering_case(
        fixture=FIXTURE_DATA,
        key=key,
        pitch_class_by_key=KEY_TO_PC,
        right_patterns=MIXOLYDIAN_RH,
        left_patterns=MIXOLYDIAN_LH,
        hand=hand,
        octaves=octaves,
    )
