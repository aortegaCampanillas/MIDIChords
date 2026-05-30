"""Tests for Chromatic scale fingerings (same for all keys)."""
import json, os, pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_chromatic.json")
CHR_RH = [1, 3, 1, 2, 1, 1, 3, 1, 2, 1, 2, 3, 1]
CHR_LH = [1, 3, 1, 2, 1, 3, 1, 2, 1, 2, 1, 3, 1]

def ext(p, n):
    if n <= len(p): return p[:n]
    if p[0] == p[-1]:
        period = len(p)-1; out = []
        for i in range(n-1): out.append(p[i % period])
        out.append(p[-1]); return out
    return [p[i % len(p)] for i in range(n)]

@pytest.fixture(scope="module")
def fd():
    with open(FIXTURE) as f: return json.load(f)

def test_chromatic_rh_1oct(fd):
    rh = fd["allKeys"]["rightHand"]
    assert ext(CHR_RH, len(rh["1OctAsc"])) == rh["1OctAsc"]
    assert list(reversed(ext(CHR_RH, len(rh["1OctAsc"])))) == rh["1OctDesc"]

def test_chromatic_lh_1oct(fd):
    lh = fd["allKeys"]["leftHand"]
    assert ext(CHR_LH, len(lh["1OctAsc"])) == lh["1OctAsc"]
    assert list(reversed(ext(CHR_LH, len(lh["1OctAsc"])))) == lh["1OctDesc"]

def test_chromatic_rh_2oct(fd):
    rh = fd["allKeys"]["rightHand"]; n = len(rh["2OctAsc_app"])
    assert ext(CHR_RH, n) == rh["2OctAsc_app"]
    assert list(reversed(ext(CHR_RH, n))) == rh["2OctDesc_app"]

def test_chromatic_lh_2oct(fd):
    lh = fd["allKeys"]["leftHand"]; n = len(lh["2OctAsc_app"])
    assert ext(CHR_LH, n) == lh["2OctAsc_app"]
    assert list(reversed(ext(CHR_LH, n))) == lh["2OctDesc_app"]
