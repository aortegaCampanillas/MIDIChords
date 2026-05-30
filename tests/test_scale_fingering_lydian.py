"""Tests for Lydian scale fingerings.

LH identical to Harmonic Minor. RH differs for G#(8), D#(3), A(9), G(7).
"""
import json
import os
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_lydian.json")

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


def extend_pattern(pattern8, n):
    if n <= 8:
        return pattern8[:n]
    ob = 1 if pattern8[0] == 1 else pattern8[7]
    period = pattern8[:7]
    fingers = []
    for i in range(n - 1):
        fingers.append(ob if (i > 0 and i % 7 == 0) else period[i % 7])
    fingers.append(pattern8[7])
    return fingers


@pytest.fixture(scope="module")
def fixture_data():
    with open(FIXTURE) as f:
        return json.load(f)


LYDIAN_KEYS = ["E","B","F#","C#","G#","D#","A","D","G","C","F","Bb"]


def _get(fixture_data, key):
    for g in ("group1", "group2", "group3"):
        if key in fixture_data[g]["keys"]:
            return fixture_data[g]["rightHand"], fixture_data[g]["leftHand"]
    raise KeyError(key)


@pytest.mark.parametrize("key", LYDIAN_KEYS)
def test_lydian_rh_1oct(key, fixture_data):
    rh, _ = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(LYDIAN_RH[pc], 8) == rh["1OctAsc"]
    assert list(reversed(extend_pattern(LYDIAN_RH[pc], 8))) == rh["1OctDesc"]


@pytest.mark.parametrize("key", LYDIAN_KEYS)
def test_lydian_lh_1oct(key, fixture_data):
    _, lh = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(LYDIAN_LH[pc], 8) == lh["1OctAsc"]
    assert list(reversed(extend_pattern(LYDIAN_LH[pc], 8))) == lh["1OctDesc"]


@pytest.mark.parametrize("key", LYDIAN_KEYS)
def test_lydian_rh_2oct(key, fixture_data):
    rh, _ = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    n = len(rh["2OctAsc_app"])
    assert extend_pattern(LYDIAN_RH[pc], n) == rh["2OctAsc_app"]
    assert list(reversed(extend_pattern(LYDIAN_RH[pc], n))) == rh["2OctDesc_app"]


@pytest.mark.parametrize("key", LYDIAN_KEYS)
def test_lydian_lh_2oct(key, fixture_data):
    _, lh = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    n = len(lh["2OctAsc_app"])
    assert extend_pattern(LYDIAN_LH[pc], n) == lh["2OctAsc_app"]
    assert list(reversed(extend_pattern(LYDIAN_LH[pc], n))) == lh["2OctDesc_app"]
