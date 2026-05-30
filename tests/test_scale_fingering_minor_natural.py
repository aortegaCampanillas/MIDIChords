"""Tests for natural minor (Aeolian) scale fingerings.

Natural minor uses the same fingering pattern as its relative major
(minor tonic + 3 semitones = relative major tonic).
"""
import json
import os
import pytest

MINOR_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_minor_natural.json")
MAJOR_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_major.json")

IONIAN_RH_SHARP = {
    0: [1,2,3,1,2,3,4,5], 2: [1,2,3,1,2,3,4,5], 4: [1,2,3,1,2,3,4,5],
    5: [1,2,3,4,1,2,3,4], 7: [1,2,3,1,2,3,4,5], 9: [1,2,3,1,2,3,4,5],
    11:[1,2,3,1,2,3,4,5], 1: [2,3,4,1,2,3,4,1], 6: [2,3,4,1,2,3,1,2],
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
    "C":0, "D":2, "E":4, "F":5, "G":7, "A":9, "B":11,
    "Bb":10,"Eb":3,"Ab":8,"Db":1,"Gb":6,"F#":6,"C#":1,"Cb":11,
    "G#":8,"D#":3,"A#":10,
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


def get_aeolian_pattern(minor_key, hand, minor_fixture):
    """Compute Aeolian fingering via relative major lookup."""
    entry = minor_fixture[minor_key]
    major_key = entry["sameAsMajor"]
    prefer_flat = entry["preferFlat"]
    major_pc = KEY_TO_PC[major_key]
    if hand == "right":
        return (IONIAN_RH_FLAT if prefer_flat else IONIAN_RH_SHARP)[major_pc]
    return IONIAN_LH[major_pc]


def resolve_major(major_key, major_fixture):
    entry = major_fixture[major_key]
    if "sameAs" in entry:
        return major_fixture[entry["sameAs"]]
    return entry


@pytest.fixture(scope="module")
def minor_data():
    with open(MINOR_FIXTURE) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def major_data():
    with open(MAJOR_FIXTURE) as f:
        return json.load(f)


MINOR_KEYS = ["A","E","B","F#","C#","G#","D#","A#","D","G","C","F","Bb","Eb","Ab"]


@pytest.mark.parametrize("minor_key", MINOR_KEYS)
def test_aeolian_rh_same_as_relative_major_1oct(minor_key, minor_data, major_data):
    major_key = minor_data[minor_key]["sameAsMajor"]
    major_entry = resolve_major(major_key, major_data)
    expected = major_entry["rightHand"]["1OctAsc"]
    got = extend_pattern(get_aeolian_pattern(minor_key, "right", minor_data), 8)
    assert got == expected, f"{minor_key} minor RH 1-oct should equal {major_key} major"


@pytest.mark.parametrize("minor_key", MINOR_KEYS)
def test_aeolian_lh_same_as_relative_major_1oct(minor_key, minor_data, major_data):
    major_key = minor_data[minor_key]["sameAsMajor"]
    major_entry = resolve_major(major_key, major_data)
    expected = major_entry["leftHand"]["1OctAsc"]
    got = extend_pattern(get_aeolian_pattern(minor_key, "left", minor_data), 8)
    assert got == expected, f"{minor_key} minor LH 1-oct should equal {major_key} major"


@pytest.mark.parametrize("minor_key", MINOR_KEYS)
def test_aeolian_rh_same_as_relative_major_2oct(minor_key, minor_data, major_data):
    major_key = minor_data[minor_key]["sameAsMajor"]
    major_entry = resolve_major(major_key, major_data)
    expected_15 = major_entry["rightHand"]["2OctAsc_app"]
    got = extend_pattern(get_aeolian_pattern(minor_key, "right", minor_data), len(expected_15))
    assert got == expected_15, f"{minor_key} minor RH 2-oct should equal {major_key} major"


@pytest.mark.parametrize("minor_key", MINOR_KEYS)
def test_aeolian_lh_same_as_relative_major_2oct(minor_key, minor_data, major_data):
    major_key = minor_data[minor_key]["sameAsMajor"]
    major_entry = resolve_major(major_key, major_data)
    expected_15 = major_entry["leftHand"]["2OctAsc_app"]
    got = extend_pattern(get_aeolian_pattern(minor_key, "left", minor_data), len(expected_15))
    assert got == expected_15, f"{minor_key} minor LH 2-oct should equal {major_key} major"
