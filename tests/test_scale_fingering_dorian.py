"""Tests for Dorian scale fingerings.

LH is identical to Harmonic Minor. RH differs for D (pc=2) and C (pc=0).
"""
import json
import os
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_dorian.json")

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


DORIAN_KEYS = ["D","A","E","B","F#","C#","G","C","F","Bb","Eb","Ab"]


def _get(fixture_data, key):
    for g in ("group1", "group2", "group3"):
        if key in fixture_data[g]["keys"]:
            return fixture_data[g]["rightHand"], fixture_data[g]["leftHand"]
    raise KeyError(key)


@pytest.mark.parametrize("key", DORIAN_KEYS)
def test_dorian_rh_1oct(key, fixture_data):
    rh, _ = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(DORIAN_RH[pc], 8) == rh["1OctAsc"]
    assert list(reversed(extend_pattern(DORIAN_RH[pc], 8))) == rh["1OctDesc"]


@pytest.mark.parametrize("key", DORIAN_KEYS)
def test_dorian_lh_1oct(key, fixture_data):
    _, lh = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(DORIAN_LH[pc], 8) == lh["1OctAsc"]
    assert list(reversed(extend_pattern(DORIAN_LH[pc], 8))) == lh["1OctDesc"]


@pytest.mark.parametrize("key", DORIAN_KEYS)
def test_dorian_rh_2oct(key, fixture_data):
    rh, _ = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    n = len(rh["2OctAsc_app"])
    assert extend_pattern(DORIAN_RH[pc], n) == rh["2OctAsc_app"]
    assert list(reversed(extend_pattern(DORIAN_RH[pc], n))) == rh["2OctDesc_app"]


@pytest.mark.parametrize("key", DORIAN_KEYS)
def test_dorian_lh_2oct(key, fixture_data):
    _, lh = _get(fixture_data, key)
    pc = KEY_TO_PC[key]
    n = len(lh["2OctAsc_app"])
    assert extend_pattern(DORIAN_LH[pc], n) == lh["2OctAsc_app"]
    assert list(reversed(extend_pattern(DORIAN_LH[pc], n))) == lh["2OctDesc_app"]
