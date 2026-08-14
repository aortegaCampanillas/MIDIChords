from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_correction_playback_overrides_the_active_filter_on_every_platform():
    desktop = (ROOT / "midichords/mixins/interval_practice_mixin.py").read_text(
        encoding="utf-8"
    )
    web = (ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")
    mobile = (ROOT / "apps/mobile_flutter/lib/main_pages.dart").read_text(
        encoding="utf-8"
    )

    assert "((not answered and allowed) or playable_answer)" in desktop
    assert "state.intervalPracticeAnswer ? !correctionPlayable : !allowed" in web
    assert "? allowed && _intervalPracticeRunning" in mobile
    assert ": semitones == _intervalPracticeSemitones" in mobile
