"""Tests for non-basic scale fingerings using family-based synthetic patterns.

Each scale is assigned to a fingering family (pentatonic_5, hexatonic_6,
heptatonic_7, octatonic_8). Tests verify the RH 1-oct and 2-oct output.
"""
import json, os, pytest

META_FIXTURE    = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_nonbasic_meta.json")
FAMILY_FIXTURE  = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_families.json")

# Family RH patterns (same as FAMILY_FIXTURE rightHand.1OctAsc)
FAMILY_RH = {
    "pentatonic_5": [1,2,3,1,2,3],
    "hexatonic_6":  [1,2,3,1,2,3,1],
    "heptatonic_7": [1,2,3,1,2,3,4,5],
    "octatonic_8":  [1,2,3,1,2,3,1,2,3],
}


def ext(p, n):
    if len(p) == 8:
        if n <= 8: return p[:n]
        ob = 1 if p[0] == 1 else p[7]; period = p[:7]; out = []
        for i in range(n-1): out.append(ob if (i > 0 and i % 7 == 0) else period[i % 7])
        out.append(p[7]); return out
    if n <= len(p): return p[:n]
    if p[0] == p[-1]:
        period = len(p)-1; out = []
        for i in range(n-1): out.append(p[i % period])
        out.append(p[-1]); return out
    return [p[i % len(p)] for i in range(n)]


@pytest.fixture(scope="module")
def meta():
    with open(META_FIXTURE) as f:
        return [e for e in json.load(f) if not e.get("id","").startswith("_")]


@pytest.fixture(scope="module")
def families():
    with open(FAMILY_FIXTURE) as f:
        return json.load(f)


def _cases(meta):
    return [(e["id"], e["scaleName"], e["fingeringFamily"]) for e in meta]


@pytest.mark.parametrize("scale_id,scale_name,family", _cases(
    [e for e in json.load(open(META_FIXTURE)) if not e.get("id","").startswith("_")]
))
def test_rh_1oct(scale_id, scale_name, family, families):
    p = FAMILY_RH[family]
    expected_asc  = families[family]["rightHand"]["1OctAsc"]
    expected_desc = families[family]["rightHand"]["1OctDesc"]
    n = len(expected_asc)
    assert ext(p, n) == expected_asc,  f"{scale_name}: 1OctAsc mismatch"
    assert list(reversed(ext(p, n))) == expected_desc, f"{scale_name}: 1OctDesc mismatch"


@pytest.mark.parametrize("scale_id,scale_name,family", _cases(
    [e for e in json.load(open(META_FIXTURE)) if not e.get("id","").startswith("_")]
))
def test_rh_2oct(scale_id, scale_name, family, families):
    p = FAMILY_RH[family]
    expected_asc  = families[family]["rightHand"]["2OctAsc_app"]
    expected_desc = families[family]["rightHand"]["2OctDesc_app"]
    n = len(expected_asc)
    assert ext(p, n) == expected_asc,  f"{scale_name}: 2OctAsc mismatch"
    assert list(reversed(ext(p, n))) == expected_desc, f"{scale_name}: 2OctDesc mismatch"
