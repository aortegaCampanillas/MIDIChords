"""Tests for Locrian scale fingerings (app output — pure cyclic multi-oct)."""
import json, os, pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_locrian.json")

LOCRIAN_RH = {
  0: [2, 3, 4, 1, 2, 3, 4, 1],
  1: [1, 2, 3, 1, 2, 3, 4, 5],
  2: [2, 3, 4, 1, 2, 3, 4, 1],
  3: [1, 2, 3, 1, 2, 3, 4, 5],
  4: [1, 2, 3, 4, 1, 2, 3, 4],
  5: [2, 3, 4, 1, 2, 3, 4, 1],
  6: [1, 2, 3, 1, 2, 3, 4, 5],
  7: [2, 3, 4, 1, 2, 3, 4, 1],
  8: [1, 2, 3, 1, 2, 3, 4, 5],
  9: [1, 2, 3, 4, 1, 2, 3, 4],
  11: [1, 2, 3, 1, 2, 3, 4, 5],
}
LOCRIAN_LH = {
  0: [3, 2, 1, 4, 3, 2, 1, 3],
  1: [5, 4, 3, 2, 1, 3, 2, 1],
  2: [3, 2, 1, 4, 3, 2, 1, 3],
  3: [5, 4, 3, 2, 1, 3, 2, 1],
  4: [5, 4, 3, 2, 1, 3, 2, 1],
  5: [3, 2, 1, 4, 3, 2, 1, 3],
  6: [5, 4, 3, 2, 1, 3, 2, 1],
  7: [3, 2, 1, 4, 3, 2, 1, 3],
  8: [5, 4, 3, 2, 1, 3, 2, 1],
  9: [5, 4, 3, 2, 1, 3, 2, 1],
  11: [5, 4, 3, 2, 1, 3, 2, 1],
}

def extend(p, n):
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
def fd():
    with open(FIXTURE) as f: return json.load(f)

KEY_TO_PC = {"B":11,"F#":6,"C#":1,"G#":8,"D#":3,"E":4,"A":9,"D":2,"G":7,"C":0,"F":5}
KEYS = ["B", "F#", "C#", "G#", "D#", "E", "A", "D", "G", "C", "F"]

def _get(fd, key):
    for g in ("group1", "group2", "group3"):
        if key in fd[g]["keys"]: return fd[g]["rightHand"], fd[g]["leftHand"]
    raise KeyError(key)

@pytest.mark.parametrize("k", KEYS)
def test_rh_1oct(k, fd):
    rh, _ = _get(fd, k); pc = KEY_TO_PC[k]
    assert extend(LOCRIAN_RH[pc], len(rh["1OctAsc"])) == rh["1OctAsc"]
    assert list(reversed(extend(LOCRIAN_RH[pc], len(rh["1OctAsc"])))) == rh["1OctDesc"]

@pytest.mark.parametrize("k", KEYS)
def test_lh_1oct(k, fd):
    _, lh = _get(fd, k); pc = KEY_TO_PC[k]
    assert extend(LOCRIAN_LH[pc], len(lh["1OctAsc"])) == lh["1OctAsc"]
    assert list(reversed(extend(LOCRIAN_LH[pc], len(lh["1OctAsc"])))) == lh["1OctDesc"]

@pytest.mark.parametrize("k", KEYS)
def test_rh_2oct(k, fd):
    rh, _ = _get(fd, k); pc = KEY_TO_PC[k]; n = len(rh["2OctAsc_app"])
    assert extend(LOCRIAN_RH[pc], n) == rh["2OctAsc_app"]
    assert list(reversed(extend(LOCRIAN_RH[pc], n))) == rh["2OctDesc_app"]

@pytest.mark.parametrize("k", KEYS)
def test_lh_2oct(k, fd):
    _, lh = _get(fd, k); pc = KEY_TO_PC[k]; n = len(lh["2OctAsc_app"])
    assert extend(LOCRIAN_LH[pc], n) == lh["2OctAsc_app"]
    assert list(reversed(extend(LOCRIAN_LH[pc], n))) == lh["2OctDesc_app"]

