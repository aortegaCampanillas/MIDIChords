from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _app() -> str:
    return (PROJECT_ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")


def test_key_changes_are_coalesced_before_calling_the_api() -> None:
    app = _app()
    refresh = app.split("function refreshDetectionActiveNotes() {", 1)[1].split("\n}\n", 1)[0]
    assert "scheduleDetection();" in refresh
    assert "runDetection();" not in refresh
    assert "const DETECTION_DEBOUNCE_MS = " in app


def test_releasing_every_key_clears_the_panel_without_a_request() -> None:
    run = _app().split("async function runDetection(", 1)[1].split("\nfunction applyDetectionResult(", 1)[0]
    empty_branch = run.split("if (!notes.length) {", 1)[1].split("return;", 1)[0]
    assert "applyDetectionResult({ ...EMPTY_DETECTION_RESULT });" in empty_branch
    assert run.index("if (!notes.length)") < run.index('fetchJson("/api/detect"')


def test_stale_or_rejected_responses_do_not_overwrite_the_panel() -> None:
    run = _app().split("async function runDetection(", 1)[1].split("\nfunction applyDetectionResult(", 1)[0]
    assert "const seq = ++detectionRequestSeq;" in run
    after_fetch = run.split('fetchJson("/api/detect"', 1)[1]
    assert "catch (err)" in after_fetch
    assert after_fetch.index("if (seq !== detectionRequestSeq) return;") < after_fetch.index("applyDetectionResult(out);")
    assert "DETECTION_MAX_RETRIES" in after_fetch
