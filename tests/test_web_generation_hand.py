from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "apps/web/app.html").read_text(encoding="utf-8")
APP_JS = (ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")


def test_generation_hand_control_defaults_to_both():
    assert 'name="generationHand" value="left"' in HTML
    assert 'name="generationHand" value="right"' in HTML
    assert 'name="generationHand" value="both" checked' in HTML
    assert 'generationHand: "both"' in APP_JS


def test_generation_hand_filters_piano_and_staff_and_is_disabled_for_guitar():
    assert "document.querySelectorAll(\"input[name='generationHand']\")" in APP_JS
    assert 'input.disabled = disabled' in APP_JS
    assert 'generationHandShows("right")' in APP_JS
    assert 'generationHandShows("left")' in APP_JS
    assert 'generationPlaybackPianoNotes.has(midi)' in APP_JS
    assert 'generationPlaybackPianoNotes.add(midi)' in APP_JS
    assert 'function getGenerationPlaybackNotes()' in APP_JS
    assert 'const notes = getGenerationPlaybackNotes();' in APP_JS
    assert 'if (state.mode !== "generation" || state.instrument !== "piano") return true;' in APP_JS


def test_entering_generation_does_not_autoplay_the_chord():
    assert 'async function runGenerateChord({ play = false } = {})' in APP_JS
    assert 'if (play && notes.length)' in APP_JS
    assert 'runGenerateChord({ play: true });' in APP_JS
