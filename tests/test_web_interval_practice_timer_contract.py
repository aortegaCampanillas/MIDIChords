from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"


def test_practice_playback_cancels_stale_manual_note_cleanup() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    playback = source.split("function playIntervalPracticeNotes(", 1)[1].split(
        "function intervalPracticeRepetitionLimit", 1
    )[0]

    assert "cancelIntervalPracticeInputClearTimer();" in playback
    assert playback.index("cancelIntervalPracticeInputClearTimer();") < playback.index(
        "playIntervalGenNoteSequence("
    )
