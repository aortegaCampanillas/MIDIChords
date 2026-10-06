import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB = PROJECT_ROOT / "apps/web"
PAGES_FILE_LIMIT = 25 * 1024 * 1024


def test_note_reading_mode_has_option_panel_and_scripts() -> None:
    html = (WEB / "app.html").read_text(encoding="utf-8")
    options = html.split('<select id="modeSelect">', 1)[1].split("</select>", 1)[0]
    assert 'value="note_reading"' in options
    for element_id in (
        "panelNoteReading",
        "noteReadingClef",
        "noteReadingRange",
        "noteReadingListen",
        "noteReadingNew",
        "noteReadingStatus",
        "noteReadingResultBlock",
        "noteReadingProgress",
        "noteReadingAccuracy",
        "noteReadingWrong",
    ):
        assert f'id="{element_id}"' in html
    scripts = re.findall(r'<script src="/static/([^"]+)"', html)
    assert scripts.index("note_reading.js") < scripts.index("app.js")
    assert scripts.index("note_speech.js") < scripts.index("app.js")


def test_note_reading_is_registered_in_the_app() -> None:
    app = (WEB / "static/app.js").read_text(encoding="utf-8")
    assert '"note_reading",' in app.split("const AVAILABLE_MODES", 1)[1].split("]);", 1)[0]
    assert 'note_reading: "panelNoteReading"' in app
    assert '|| state.mode === "note_reading"' in app
    assert 'if (state.mode === "note_reading") {\n    drawNoteReadingCanvas(ctx, width, height);' in app
    assert 'if (state.mode === "note_reading" && mode !== "note_reading") stopNoteReadingListening();' in app


def test_speech_model_parts_fit_pages_and_match_the_loader() -> None:
    speech = (WEB / "static/note_speech.js").read_text(encoding="utf-8")
    parts = re.findall(r'url: "/(vendor/vosk/[^"]+)", bytes: (\d+)', speech)
    # Two parts per language: Spanish and English.
    assert len(parts) == 4
    assert {path.split("/")[-1].split(".tar")[0] for path, _ in parts} == {
        "vosk-model-small-es-0.42",
        "vosk-model-small-en-us-0.15",
    }
    for path, size in parts:
        file = WEB / path
        assert file.is_file(), path
        assert file.stat().st_size == int(size)
        assert file.stat().st_size < PAGES_FILE_LIMIT
    library = re.search(r'VOSK_LIBRARY_URL = "/(vendor/vosk/[^"]+)"', speech).group(1)
    assert (WEB / library).stat().st_size < PAGES_FILE_LIMIT
    assert (WEB / "vendor/vosk/NOTICE.md").is_file()


def test_vendor_files_are_cached_and_bundled() -> None:
    headers = (WEB / "_headers").read_text(encoding="utf-8")
    vendor_rule = headers.split("/vendor/*", 1)[1].strip().splitlines()[0]
    assert "immutable" in vendor_rule
    launch = (PROJECT_ROOT / "launch.py").read_text(encoding="utf-8")
    assert 'shutil.copytree(web_dir / "vendor", pages_dist / "vendor"' in launch


def test_note_reading_has_bilingual_contextual_help() -> None:
    help_callouts = (WEB / "static/help_callouts.js").read_text(encoding="utf-8")
    texts = (WEB / "static/ui_texts.js").read_text(encoding="utf-8")
    assert 'if (mode === "note_reading") return HELP_CALLOUTS_NOTE_READING;' in help_callouts
    block = help_callouts.split("const HELP_CALLOUTS_NOTE_READING = [", 1)[1].split("];", 1)[0]
    for key in re.findall(r'textKey: "([a-z_]+)"', block):
        assert texts.count(f"    {key}:") == 2, key
