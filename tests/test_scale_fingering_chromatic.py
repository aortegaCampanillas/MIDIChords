"""Tests for the chromatic fingering shared by every tonic."""

import pytest

from tests.support.scale_fingering import (
    HAND_OCTAVE_CASES,
    assert_hand_fingering_data,
    load_fingering_fixture,
)

CHROMATIC_PATTERNS = {
    "rightHand": [1, 3, 1, 2, 1, 1, 3, 1, 2, 1, 2, 3, 1],
    "leftHand": [1, 3, 1, 2, 1, 3, 1, 2, 1, 2, 1, 3, 1],
}
FIXTURE_DATA = load_fingering_fixture("scale_fingering_chromatic.json")["allKeys"]


@pytest.mark.parametrize("hand,octaves", HAND_OCTAVE_CASES)
def test_chromatic_fingering(hand, octaves):
    assert_hand_fingering_data(
        pattern=CHROMATIC_PATTERNS[hand],
        hand_data=FIXTURE_DATA[hand],
        octaves=octaves,
    )
