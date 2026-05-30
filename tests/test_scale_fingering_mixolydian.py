"""Tests for Mixolydian scale fingerings."""
import json, os, pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "scale_fingering_mixolydian.json")

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

def extend_pattern(p8, n):
    if n<=8: return p8[:n]
    ob = 1 if p8[0]==1 else p8[7]; period=p8[:7]; out=[]
    for i in range(n-1): out.append(ob if (i>0 and i%7==0) else period[i%7])
    out.append(p8[7]); return out

@pytest.fixture(scope="module")
def fd():
    with open(FIXTURE) as f: return json.load(f)

KEYS = ["G","D","A","E","B","F#","C","F","Bb","Eb","Ab","Db"]

def _get(fd, k):
    for g in("group1","group2","group3"):
        if k in fd[g]["keys"]: return fd[g]["rightHand"],fd[g]["leftHand"]
    raise KeyError(k)

@pytest.mark.parametrize("k",KEYS)
def test_rh_1oct(k,fd):
    rh,_=_get(fd,k); pc=KEY_TO_PC[k]
    assert extend_pattern(MIXOLYDIAN_RH[pc],8)==rh["1OctAsc"]
    assert list(reversed(extend_pattern(MIXOLYDIAN_RH[pc],8)))==rh["1OctDesc"]

@pytest.mark.parametrize("k",KEYS)
def test_lh_1oct(k,fd):
    _,lh=_get(fd,k); pc=KEY_TO_PC[k]
    assert extend_pattern(MIXOLYDIAN_LH[pc],8)==lh["1OctAsc"]
    assert list(reversed(extend_pattern(MIXOLYDIAN_LH[pc],8)))==lh["1OctDesc"]

@pytest.mark.parametrize("k",KEYS)
def test_rh_2oct(k,fd):
    rh,_=_get(fd,k); pc=KEY_TO_PC[k]; n=len(rh["2OctAsc_app"])
    assert extend_pattern(MIXOLYDIAN_RH[pc],n)==rh["2OctAsc_app"]
    assert list(reversed(extend_pattern(MIXOLYDIAN_RH[pc],n)))==rh["2OctDesc_app"]

@pytest.mark.parametrize("k",KEYS)
def test_lh_2oct(k,fd):
    _,lh=_get(fd,k); pc=KEY_TO_PC[k]; n=len(lh["2OctAsc_app"])
    assert extend_pattern(MIXOLYDIAN_LH[pc],n)==lh["2OctAsc_app"]
    assert list(reversed(extend_pattern(MIXOLYDIAN_LH[pc],n)))==lh["2OctDesc_app"]
