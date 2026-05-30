"""Tests for major scale fingering patterns (both hands, 1 and 2 octaves)."""
import json
import os
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_major.json")

IONIAN_RH_SHARP = {
    0: [1,2,3,1,2,3,4,5], 2: [1,2,3,1,2,3,4,5], 4: [1,2,3,1,2,3,4,5],
    5: [1,2,3,4,1,2,3,4], 7: [1,2,3,1,2,3,4,5], 9: [1,2,3,1,2,3,4,5],
    11:[1,2,3,1,2,3,4,5], 1: [2,3,4,1,2,3,4,1], 6: [2,3,4,1,2,3,4,1],
    10:[2,3,4,1,2,3,4,1], 3: [3,1,2,3,1,2,3,4], 8: [3,4,1,2,3,1,2,3],
}
IONIAN_RH_FLAT = {
    0: [1,2,3,1,2,3,4,5], 2: [1,2,3,1,2,3,4,5], 4: [1,2,3,1,2,3,4,5],
    5: [1,2,3,4,1,2,3,4], 7: [1,2,3,1,2,3,4,5], 9: [1,2,3,1,2,3,4,5],
    11:[1,2,3,4,1,2,3,4], 1: [2,3,1,2,3,4,1,2], 6: [2,3,4,1,2,3,1,2],
    10:[2,3,4,1,2,3,4,1], 3: [3,1,2,3,1,2,3,4], 8: [3,4,1,2,3,1,2,3],
}
IONIAN_LH = {
    0: [5,4,3,2,1,3,2,1], 7: [5,4,3,2,1,3,2,1], 2: [5,4,3,2,1,3,2,1],
    9: [5,4,3,2,1,3,2,1], 4: [5,4,3,2,1,3,2,1], 5: [5,4,3,2,1,3,2,1],
    11:[5,4,3,2,1,3,2,1], 6: [4,3,2,1,4,3,2,1],
    10:[3,2,1,4,3,2,1,3], 3: [3,2,1,4,3,2,1,3], 8: [3,2,1,4,3,2,1,3],
    1: [3,2,1,4,3,2,1,3],
}

KEY_TO_PC = {
    "C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11,
    "Bb":10,"Eb":3,"Ab":8,"Db":1,"Gb":6,"F#":6,"C#":1,"Cb":11,
}
# F# uses same RH fingering as Gb; Cb uses same RH fingering as B
FLAT_KEYS = {"Bb","Eb","Ab","Db","Gb","Cb","F#"}


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


def get_pattern(key, hand):
    pc = KEY_TO_PC[key]
    prefer_flat = key in FLAT_KEYS
    if hand == "right":
        return (IONIAN_RH_FLAT if prefer_flat else IONIAN_RH_SHARP)[pc]
    return IONIAN_LH[pc]


def resolve(data, key):
    entry = data[key]
    if "sameAs" in entry:
        return data[entry["sameAs"]]
    return entry


@pytest.fixture(scope="module")
def fixture_data():
    with open(FIXTURE) as f:
        return json.load(f)


KEYS = ["C","G","D","A","E","F","Bb","Eb","Ab","Db","Gb","B","F#","C#","Cb"]


@pytest.mark.parametrize("key", KEYS)
def test_rh_1oct_asc(key, fixture_data):
    entry = resolve(fixture_data, key)
    expected = entry["rightHand"]["1OctAsc"]
    assert extend_pattern(get_pattern(key, "right"), 8) == expected


@pytest.mark.parametrize("key", KEYS)
def test_rh_1oct_desc(key, fixture_data):
    entry = resolve(fixture_data, key)
    asc = extend_pattern(get_pattern(key, "right"), 8)
    assert list(reversed(asc)) == entry["rightHand"]["1OctDesc"]


@pytest.mark.parametrize("key", KEYS)
def test_rh_2oct_app(key, fixture_data):
    entry = resolve(fixture_data, key)
    expected = entry["rightHand"]["2OctAsc_app"]
    assert extend_pattern(get_pattern(key, "right"), len(expected)) == expected


@pytest.mark.parametrize("key", KEYS)
def test_rh_2oct_desc_app(key, fixture_data):
    entry = resolve(fixture_data, key)
    asc = extend_pattern(get_pattern(key, "right"), len(entry["rightHand"]["2OctAsc_app"]))
    assert list(reversed(asc)) == entry["rightHand"]["2OctDesc_app"]


@pytest.mark.parametrize("key", KEYS)
def test_lh_1oct_asc(key, fixture_data):
    entry = resolve(fixture_data, key)
    expected = entry["leftHand"]["1OctAsc"]
    assert extend_pattern(get_pattern(key, "left"), 8) == expected


@pytest.mark.parametrize("key", KEYS)
def test_lh_1oct_desc(key, fixture_data):
    entry = resolve(fixture_data, key)
    asc = extend_pattern(get_pattern(key, "left"), 8)
    assert list(reversed(asc)) == entry["leftHand"]["1OctDesc"]


@pytest.mark.parametrize("key", KEYS)
def test_lh_2oct_app(key, fixture_data):
    entry = resolve(fixture_data, key)
    expected = entry["leftHand"]["2OctAsc_app"]
    assert extend_pattern(get_pattern(key, "left"), len(expected)) == expected


@pytest.mark.parametrize("key", KEYS)
def test_lh_2oct_desc_app(key, fixture_data):
    entry = resolve(fixture_data, key)
    asc = extend_pattern(get_pattern(key, "left"), len(entry["leftHand"]["2OctAsc_app"]))
    assert list(reversed(asc)) == entry["leftHand"]["2OctDesc_app"]
