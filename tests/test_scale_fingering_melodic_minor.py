"""Tests for melodic minor scale fingerings.

Melodic Minor uses identical fingering patterns to Harmonic Minor.
"""
import json
import os
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_melodic_minor.json")
HM_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_harmonic_minor.json")


@pytest.fixture(scope="module")
def melodic_data():
    with open(FIXTURE) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def harmonic_data():
    with open(HM_FIXTURE) as f:
        return json.load(f)


def test_melodic_minor_fingerings_match_harmonic_minor(melodic_data, harmonic_data):
    """Melodic minor uses the exact same fingering patterns as harmonic minor."""
    for group in ("group1", "group2", "group3"):
        mm = melodic_data[group]
        hm = harmonic_data[group]
        assert mm["keys"] == hm["keys"], f"{group}: key lists differ"
        for hand in ("rightHand", "leftHand"):
            for variant in ("1OctAsc", "1OctDesc", "2OctAsc_app", "2OctDesc_app"):
                assert mm[hand][variant] == hm[hand][variant], (
                    f"{group} {hand} {variant}: melodic ≠ harmonic"
                )


# --- Parametrised tests (same logic as harmonic minor) ---

from test_scale_fingering_harmonic_minor import (  # noqa: E402
    HARMONIC_MINOR_RH,
    HARMONIC_MINOR_LH,
    KEY_TO_PC,
    extend_pattern,
)

MELODIC_KEYS = ["A","E","B","F#","C#","D","G","C","F","Bb","Eb","Ab"]


def _get_expected(melodic_data, key):
    for g in ("group1", "group2", "group3"):
        if key in melodic_data[g]["keys"]:
            return melodic_data[g]["rightHand"], melodic_data[g]["leftHand"]
    raise KeyError(key)


@pytest.mark.parametrize("key", MELODIC_KEYS)
def test_melodic_minor_rh_1oct(key, melodic_data):
    rh_data, _ = _get_expected(melodic_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(HARMONIC_MINOR_RH[pc], 8) == rh_data["1OctAsc"]
    assert list(reversed(extend_pattern(HARMONIC_MINOR_RH[pc], 8))) == rh_data["1OctDesc"]


@pytest.mark.parametrize("key", MELODIC_KEYS)
def test_melodic_minor_lh_1oct(key, melodic_data):
    _, lh_data = _get_expected(melodic_data, key)
    pc = KEY_TO_PC[key]
    assert extend_pattern(HARMONIC_MINOR_LH[pc], 8) == lh_data["1OctAsc"]
    assert list(reversed(extend_pattern(HARMONIC_MINOR_LH[pc], 8))) == lh_data["1OctDesc"]


@pytest.mark.parametrize("key", MELODIC_KEYS)
def test_melodic_minor_rh_2oct(key, melodic_data):
    rh_data, _ = _get_expected(melodic_data, key)
    pc = KEY_TO_PC[key]
    n = len(rh_data["2OctAsc_app"])
    assert extend_pattern(HARMONIC_MINOR_RH[pc], n) == rh_data["2OctAsc_app"]
    assert list(reversed(extend_pattern(HARMONIC_MINOR_RH[pc], n))) == rh_data["2OctDesc_app"]


@pytest.mark.parametrize("key", MELODIC_KEYS)
def test_melodic_minor_lh_2oct(key, melodic_data):
    _, lh_data = _get_expected(melodic_data, key)
    pc = KEY_TO_PC[key]
    n = len(lh_data["2OctAsc_app"])
    assert extend_pattern(HARMONIC_MINOR_LH[pc], n) == lh_data["2OctAsc_app"]
    assert list(reversed(extend_pattern(HARMONIC_MINOR_LH[pc], n))) == lh_data["2OctDesc_app"]
