"""Canonical Ionian fingering patterns shared by scale contract tests."""

IONIAN_RH_SHARP = {
    0: [1, 2, 3, 1, 2, 3, 4, 5], 2: [1, 2, 3, 1, 2, 3, 4, 5],
    4: [1, 2, 3, 1, 2, 3, 4, 5], 5: [1, 2, 3, 4, 1, 2, 3, 4],
    7: [1, 2, 3, 1, 2, 3, 4, 5], 9: [1, 2, 3, 1, 2, 3, 4, 5],
    11: [1, 2, 3, 1, 2, 3, 4, 5], 1: [2, 3, 4, 1, 2, 3, 4, 1],
    6: [2, 3, 4, 1, 2, 3, 4, 1], 10: [2, 3, 4, 1, 2, 3, 4, 1],
    3: [3, 1, 2, 3, 1, 2, 3, 4], 8: [3, 4, 1, 2, 3, 1, 2, 3],
}
IONIAN_RH_FLAT = {
    0: [1, 2, 3, 1, 2, 3, 4, 5], 2: [1, 2, 3, 1, 2, 3, 4, 5],
    4: [1, 2, 3, 1, 2, 3, 4, 5], 5: [1, 2, 3, 4, 1, 2, 3, 4],
    7: [1, 2, 3, 1, 2, 3, 4, 5], 9: [1, 2, 3, 1, 2, 3, 4, 5],
    11: [1, 2, 3, 4, 1, 2, 3, 4], 1: [2, 3, 1, 2, 3, 4, 1, 2],
    6: [2, 3, 4, 1, 2, 3, 1, 2], 10: [2, 3, 4, 1, 2, 3, 4, 1],
    3: [3, 1, 2, 3, 1, 2, 3, 4], 8: [3, 4, 1, 2, 3, 1, 2, 3],
}
IONIAN_LH = {
    0: [5, 4, 3, 2, 1, 3, 2, 1], 7: [5, 4, 3, 2, 1, 3, 2, 1],
    2: [5, 4, 3, 2, 1, 3, 2, 1], 9: [5, 4, 3, 2, 1, 3, 2, 1],
    4: [5, 4, 3, 2, 1, 3, 2, 1], 5: [5, 4, 3, 2, 1, 3, 2, 1],
    11: [5, 4, 3, 2, 1, 3, 2, 1], 6: [4, 3, 2, 1, 4, 3, 2, 1],
    10: [3, 2, 1, 4, 3, 2, 1, 3], 3: [3, 2, 1, 4, 3, 2, 1, 3],
    8: [3, 2, 1, 4, 3, 2, 1, 3], 1: [3, 2, 1, 4, 3, 2, 1, 3],
}

KEY_TO_PC = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
    "Bb": 10, "Eb": 3, "Ab": 8, "Db": 1, "Gb": 6, "F#": 6,
    "C#": 1, "Cb": 11, "G#": 8, "D#": 3, "A#": 10,
}


def ionian_pattern(key: str, hand: str, *, prefer_flat: bool | None = None) -> list[int]:
    """Return the pattern while preserving enharmonic spelling for the RH."""
    pitch_class = KEY_TO_PC[key]
    if hand == "leftHand":
        return IONIAN_LH[pitch_class]
    if prefer_flat is None:
        prefer_flat = key in {"Bb", "Eb", "Ab", "Db", "Gb", "Cb", "F#"}
    patterns = IONIAN_RH_FLAT if prefer_flat else IONIAN_RH_SHARP
    return patterns[pitch_class]


def resolve_major_entry(fixture: dict, key: str) -> dict:
    entry = fixture[key]
    return fixture[entry["sameAs"]] if "sameAs" in entry else entry
