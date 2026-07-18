"""Key signature (armadura) for the 7 diatonic modes across all 12 tonics.

Each mode's key signature must match its true relative major (the major
key sharing exactly the same notes), not a one-size-fits-all "minor"
formula. Expected values below were verified note-by-note against
standard music theory and cross-checked against an independently
generated reference table.
"""
import pytest

from midichords.mixins.input_detection_mixin import InputDetectionMixin
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


@pytest.mark.parametrize(
    "label,midi,count,prefer_flats,expected",
    [
        ("Fa#", 66, 1, False, 0),
        ("Do#", 61, 2, False, 1),
        ("Mi#", 65, 6, False, 5),
        ("Si#", 60, 7, False, 6),
        ("Si♭", 70, 1, True, 0),
        ("Do♭", 59, 6, True, 5),
        ("Fa♭", 64, 7, True, 6),
        ("Do#", 61, 1, False, -1),
        ("Fa##", 67, 7, False, -1),
        ("Fa", 65, 7, False, -1),
    ],
)
def test_active_scale_note_maps_to_key_signature_position(label, midi, count, prefer_flats, expected):
    assert RenderMixin._key_signature_index_for_scale_note(
        label, midi, count, prefer_flats
    ) == expected


def test_scale_keyboard_visual_state_ignores_audio_latch_after_release():
    render = RenderMixin()
    render.tuner_tab_active = False
    render.generation_tab_active = False
    render.scale_tab_active = True
    render.scale_play_mode = "piano"
    render.active_notes = {60}  # nota retenida solo para audio
    render.midi_held_notes = set()
    render.mouse_held_notes = set()
    render.sustain_latched_notes = set()
    render.staff_pressed_scale_notes = set()
    render.scale_loop_active = False
    render.scale_current_note = None

    assert render._instrument_display_notes() == set()

    render.mouse_held_notes = {64}
    assert render._instrument_display_notes() == {64}


@pytest.mark.parametrize(
    "source,held_attribute",
    [("mouse", "mouse_held_notes"), ("midi", "midi_held_notes")],
)
def test_scale_repeated_latched_note_is_retriggered(source, held_attribute):
    input_state = InputDetectionMixin()
    input_state.current_mode = "scales"
    input_state.note_velocity = {}
    input_state.sustain_latched_notes = set()
    input_state.midi_latched_notes = set()
    input_state.midi_held_notes = set()
    input_state.mouse_held_notes = set()
    input_state.held_release_notes = {60}
    input_state.sounding_notes = {60}
    stopped = []
    started = []
    input_state.stop_note = stopped.append
    input_state.play_note = lambda note, velocity: started.append((note, velocity))
    input_state._should_play_midi_input_locally = lambda: True

    input_state._note_on_from_source(60, velocity=100, source=source)
    _, next_sounding = input_state._compute_next_sounding_state()
    input_state._apply_sounding_note_diff(next_sounding)

    assert stopped == [60]
    assert started == [(60, 100)]
    assert input_state.sounding_notes == {60}
    assert getattr(input_state, held_attribute) == {60}
    assert input_state.held_release_notes == {60}


def test_scale_duplicate_note_on_while_key_is_held_is_not_retriggered():
    input_state = InputDetectionMixin()
    input_state.current_mode = "scales"
    input_state.note_velocity = {}
    input_state.sustain_latched_notes = set()
    input_state.midi_latched_notes = set()
    input_state.midi_held_notes = set()
    input_state.mouse_held_notes = {60}
    input_state.held_release_notes = {60}
    input_state.sounding_notes = {60}
    stopped = []
    input_state.stop_note = stopped.append

    input_state._note_on_from_source(60, velocity=100, source="mouse")

    assert stopped == []
    assert input_state.sounding_notes == {60}


def test_scale_repeated_note_repaints_when_audio_active_set_is_unchanged():
    input_state = InputDetectionMixin()
    input_state.current_mode = "scales"
    input_state.active_notes = {60}
    input_state._last_scale_visual_notes = set()
    input_state.midi_held_notes = set()
    input_state.mouse_held_notes = {60}
    input_state.sustain_latched_notes = set()
    input_state.staff_pressed_scale_notes = {60}
    input_state._sync_scale_piano_staff_from_active_keys = lambda _notes: None
    redraws = []
    input_state.update_music_views = lambda: redraws.append(True)

    input_state._sync_sounding_ui({60})

    assert input_state._last_scale_visual_notes == {60}
    assert redraws == [True]
