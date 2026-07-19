"""Contract tests for scales that use a synthetic fingering family."""

import pytest

from tests.support.scale_fingering import (
    assert_hand_fingering_data,
    load_fingering_fixture,
)

FAMILY_RH = {
    "pentatonic_5": [1, 2, 3, 1, 2, 3],
    "hexatonic_6": [1, 2, 3, 1, 2, 3, 1],
    "heptatonic_7": [1, 2, 3, 1, 2, 3, 4, 5],
    "octatonic_8": [1, 2, 3, 1, 2, 3, 1, 2, 3],
}
FAMILIES = load_fingering_fixture("scale_fingering_families.json")
SCALE_CASES = [
    (entry["id"], entry["scaleName"], entry["fingeringFamily"])
    for entry in load_fingering_fixture("scale_fingering_nonbasic_meta.json")
    if not entry.get("id", "").startswith("_")
]


@pytest.mark.parametrize("octaves", ("1Oct", "2Oct"))
@pytest.mark.parametrize("scale_id,scale_name,family", SCALE_CASES)
def test_nonbasic_right_hand_fingering(scale_id, scale_name, family, octaves):
    assert_hand_fingering_data(
        pattern=FAMILY_RH[family],
        hand_data=FAMILIES[family]["rightHand"],
        octaves=octaves,
    )
