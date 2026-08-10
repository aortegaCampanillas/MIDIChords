from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_note_detection_is_the_first_web_mode_with_its_complete_panel() -> None:
    html = (PROJECT_ROOT / "apps/web/app.html").read_text(encoding="utf-8")
    options = html.split('<select id="modeSelect">', 1)[1].split("</select>", 1)[0]

    assert options.index('value="note_detection"') < options.index(
        'value="detection"'
    )
    for element_id in (
        "panelNoteDetection",
        "noteDetectPlay",
        "noteDetectClear",
        "noteDetectDetailsToggle",
        "noteDetectResultBlock",
        "noteDetectFieldNote",
        "noteDetectName",
    ):
        assert f'id="{element_id}"' in html


def test_note_detection_keeps_one_note_and_hides_only_its_piano_labels() -> None:
    app = (PROJECT_ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")

    assert 'noteDetectionNote: null' in app
    assert 'noteDetectionDetailsVisible: true' in app
    assert 'state.noteDetectionNote != null && Number.isFinite(note)' in app
    assert 'state.noteDetectionNote = midi' in app
    assert 'return new Set([Number(state.noteDetectionNote)])' in app
    assert 'return state.noteDetectionNote == null ? [] : [Number(state.noteDetectionNote)]' in app
    assert 'state.mode === "note_detection"\n      && !state.noteDetectionDetailsVisible' in app
    assert 'key.innerHTML = hideNoteDetectionLabels ? "" : pianoKeyLabelHtml(midi)' in app
    assert 'const tonic = !noteDetectionStaff' in app
    assert '!noteDetectionStaff && !detectionStaff && !intervalDetectionStaff' in app
    note_play_binding = app.split(
        'bindImmediatePress(el("noteDetectPlay")', 1
    )[1].split('listen(el("noteDetectClear")', 1)[0]
    assert "noteDetectionPlayHeldNote = Number(state.noteDetectionNote)" in note_play_binding
    assert "startHeldInputNote(noteDetectionPlayHeldNote" in note_play_binding
    assert "stopHeldInputNote(noteDetectionPlayHeldNote)" in note_play_binding
    assert "highlightWhilePressed: true" in note_play_binding


def test_note_detection_has_bilingual_contextual_help() -> None:
    help_callouts = (
        PROJECT_ROOT / "apps/web/static/help_callouts.js"
    ).read_text(encoding="utf-8")
    texts = (PROJECT_ROOT / "apps/web/static/ui_texts.js").read_text(
        encoding="utf-8"
    )

    assert 'mode === "note_detection"' in help_callouts
    for selector in (
        "#staffCanvas",
        "#panelNoteDetection",
        "#noteDetectPlay",
        "#noteDetectClear",
        "#noteDetectDetailsToggle",
        "#noteDetectFieldNote",
        "#sharedPiano",
    ):
        assert f'selector: "{selector}"' in help_callouts
    assert "Con fines didácticos" in texts
    assert "For learning purposes" in texts
