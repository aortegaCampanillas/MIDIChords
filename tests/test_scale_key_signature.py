"""Key signature (armadura) for the 7 diatonic modes across all 12 tonics.

Each mode's key signature must match its true relative major (the major
key sharing exactly the same notes), not a one-size-fits-all "minor"
formula. Expected values below were verified note-by-note against
standard music theory and cross-checked against an independently
generated reference table.
"""
import pytest

from midichords.mixins.render_mixin import RenderMixin

# pc -> canonical name preferring sharps / preferring flats
SHARP_NAMES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
FLAT_NAMES = ["Do", "Reb", "Re", "Mib", "Mi", "Fa", "Solb", "Sol", "Lab", "La", "Sib", "Si"]

MODES = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]

NAME_TO_PC = {name: pc for pc, name in enumerate(SHARP_NAMES)}
NAME_TO_PC.update({name: pc for pc, name in enumerate(FLAT_NAMES)})


def _sig_for_mode(tonic_pc: int, mode: str) -> tuple[int, bool]:
    offset = RenderMixin._MODE_RELATIVE_MAJOR_OFFSET.get(mode)
    if offset is None:
        return RenderMixin._key_signature_count_for_tonic(tonic_pc, False, tie_prefer_flats=False)
    relative_major_pc = (tonic_pc + offset) % 12
    return RenderMixin._key_signature_count_for_tonic(relative_major_pc, False, tie_prefer_flats=False)


# (count, prefer_flats): list of "Tonic Mode" entries, verified against
# standard music theory (see conversation/PR description for full derivation).
EXPECTED_BUCKETS: dict[tuple[int, bool], list[str]] = {
    (0, False): ["Do Ionian", "Re Dorian", "Mi Phrygian", "Fa Lydian", "Sol Mixolydian", "La Aeolian", "Si Locrian"],
    (1, False): ["Sol Ionian", "La Dorian", "Si Phrygian", "Do Lydian", "Re Mixolydian", "Mi Aeolian", "Fa# Locrian"],
    (1, True): ["Fa Ionian", "Sol Dorian", "La Phrygian", "Sib Lydian", "Do Mixolydian", "Re Aeolian", "Mi Locrian"],
    (2, False): ["Re Ionian", "Mi Dorian", "Fa# Phrygian", "Sol Lydian", "La Mixolydian", "Si Aeolian", "Do# Locrian"],
    (2, True): ["Sib Ionian", "Do Dorian", "Re Phrygian", "Mib Lydian", "Fa Mixolydian", "Sol Aeolian", "La Locrian"],
    (3, False): ["La Ionian", "Si Dorian", "Do# Phrygian", "Re Lydian", "Mi Mixolydian", "Fa# Aeolian", "Sol# Locrian"],
    (3, True): ["Mib Ionian", "Fa Dorian", "Sol Phrygian", "Lab Lydian", "Sib Mixolydian", "Do Aeolian", "Re Locrian"],
    (4, False): ["Mi Ionian", "Fa# Dorian", "Sol# Phrygian", "La Lydian", "Si Mixolydian", "Do# Aeolian", "Re# Locrian"],
    (4, True): ["Lab Ionian", "Sib Dorian", "Do Phrygian", "Reb Lydian", "Mib Mixolydian", "Fa Aeolian", "Sol Locrian"],
    (5, False): ["Si Ionian", "Do# Dorian", "Re# Phrygian", "Mi Lydian", "Fa# Mixolydian", "Sol# Aeolian", "La# Locrian"],
    (5, True): ["Reb Ionian", "Mib Dorian", "Fa Phrygian", "Solb Lydian", "Lab Mixolydian", "Sib Aeolian", "Do Locrian"],
    (6, False): ["Fa# Ionian", "Sol# Dorian", "La# Phrygian", "Si Lydian", "Do# Mixolydian", "Re# Aeolian", "Fa Locrian"],
}


def _flatten_expected():
    cases = []
    for (count, prefer_flats), entries in EXPECTED_BUCKETS.items():
        for entry in entries:
            tonic_name, mode = entry.rsplit(" ", 1)
            cases.append((tonic_name, mode, count, prefer_flats))
    return cases


@pytest.mark.parametrize("tonic_name,mode,expected_count,expected_prefer_flats", _flatten_expected())
def test_mode_key_signature(tonic_name, mode, expected_count, expected_prefer_flats):
    tonic_pc = NAME_TO_PC[tonic_name]
    count, prefer_flats = _sig_for_mode(tonic_pc, mode)
    assert (count, prefer_flats) == (expected_count, expected_prefer_flats), (
        f"{tonic_name} {mode}: expected {expected_count} "
        f"{'flats' if expected_prefer_flats else 'sharps'}, got {count} "
        f"{'flats' if prefer_flats else 'sharps'}"
    )


def test_all_84_combinations_covered():
    """Sanity check: every tonic x mode combination (12 x 7) is exercised exactly once."""
    seen = set()
    for (_count, _prefer_flats), entries in EXPECTED_BUCKETS.items():
        for entry in entries:
            tonic_name, mode = entry.rsplit(" ", 1)
            key = (NAME_TO_PC[tonic_name], mode)
            assert key not in seen, f"duplicate case: {entry}"
            seen.add(key)
    assert len(seen) == 12 * 7  # 12 tonics x 7 modes


@pytest.mark.parametrize(
    "tonic_pc,mode,expected_count,expected_prefer_flats",
    [
        # Regression cases explicitly reported during development.
        (0, "Dorian", 2, True),      # C Dorian -> Bb major (2 flats), not 3 like natural minor
        (2, "Dorian", 0, False),     # D Dorian -> C major (no accidentals)
        (5, "Lydian", 0, False),     # F Lydian -> C major (no accidentals), not 1 flat like F major
        (7, "Mixolydian", 0, False),  # G Mixolydian -> C major (no accidentals), not 1 sharp like G major
        (0, "Aeolian", 3, True),     # C Aeolian (natural minor) unchanged: Eb major, 3 flats
    ],
)
def test_regression_cases(tonic_pc, mode, expected_count, expected_prefer_flats):
    count, prefer_flats = _sig_for_mode(tonic_pc, mode)
    assert (count, prefer_flats) == (expected_count, expected_prefer_flats)
