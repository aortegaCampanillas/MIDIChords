from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_interval_generation_reserves_a_real_column_for_instrument_controls():
    css = (ROOT / "apps/web/static/style.css").read_text(encoding="utf-8")

    selector = (
        ".mode-screen.mode-interval_generation "
        ".instrument-panel.with-inst-dock"
    )
    block = css.split(selector, 1)[1].split("}", 1)[0]

    assert "display: grid" in block
    assert "grid-template-columns: minmax(0, 1fr) 96px" in block
    assert "padding-right: 12px" in block
    assert "> :not(.instrument-dock)" in css
    assert "min-width: 0" in css


def test_interval_generation_stacks_the_dock_on_narrow_screens():
    css = (ROOT / "apps/web/static/style.css").read_text(encoding="utf-8")
    media = css.split("@media (max-width: 1200px)", 1)[1]

    assert (
        ".mode-screen.mode-interval_generation .instrument-panel.with-inst-dock"
        in media
    )
    assert "grid-template-columns: minmax(0, 1fr)" in media
    assert "justify-self: end" in media


def test_interval_generation_staff_registers_clickable_note_regions():
    source = (ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    assert (
        'const intervalMelodyStaff = state.mode === "interval_detection" '
        "&& !!state.intervalMelodyActive;"
    ) in source
    region_registration = source.split(
        "state.staff.scaleRegions.push({", 1
    )[0].rsplit("if (", 1)[1]
    assert "intervalDetectionStaff && !intervalMelodyStaff" in region_registration
    interactive_branch = source.split(
        "} else if (scaleStaff || detectionStaff || generationStaff || intervalDetectionStaff) {",
        1,
    )[1].split("function renderChangelog", 1)[0]
    assert "state.staff.scaleRegions.forEach" in interactive_branch
    assert "handleInstrumentNote(Number(hit.note))" in interactive_branch


def test_interval_detection_playback_maps_sound_order_to_staff_order():
    source = (ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    sequence = source.split("function playIntervalNoteSequence(", 1)[1].split(
        "function refreshIntervalButtonsState", 1
    )[0]
    assert "displayIndices = null" in sequence
    assert "const displayIdx = displayIndices?.[idx] ?? idx" in sequence
    assert "state.intervalPlayingIdx = displayIdx" in sequence

    assert "function intervalDisplayIndicesForPlayback(notes)" in source
    assert source.count("intervalDisplayIndicesForPlayback(notes)") == 3


def test_interval_detection_piano_only_activates_the_sounding_note():
    source = (ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    active_midi = source.split("function getActiveMidiForMode()", 1)[1].split(
        "const {", 1
    )[0]
    interval_branch = active_midi.split(
        'if (state.mode === "interval_detection") {', 1
    )[1].split("}", 1)[0]

    assert "state.intervalPlayingNote" in interval_branch
    assert "return new Set();" in interval_branch
    assert "state.intervalNotes.map" not in interval_branch


def test_chord_staff_uses_the_spelling_returned_for_each_chord_note():
    source = (ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    spelling = source.split("function chordStaffAccidentalForMidi", 1)[1].split(
        "function getNoteAccidental", 1
    )[0]
    accidental = source.split("function getNoteAccidental", 1)[1].split(
        "function renderStaff", 1
    )[0]
    assert "chord?.notes_midi" in spelling
    assert "chord?.notes" in spelling
    assert 'label.includes("♭")' in spelling
    assert "chordStaffAccidentalForMidi(midi)" in accidental
