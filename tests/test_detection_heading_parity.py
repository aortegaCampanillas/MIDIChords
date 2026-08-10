from pathlib import Path

from midichords.core.i18n import UI_TEXTS


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_detection_headings_are_explicit_and_aligned_across_platforms() -> None:
    web_texts = (PROJECT_ROOT / "apps/web/static/ui_texts.js").read_text(
        encoding="utf-8"
    )
    mobile_pages = (
        PROJECT_ROOT / "apps/mobile_flutter/lib/main_pages.dart"
    ).read_text(encoding="utf-8")

    expected = {
        "es": ("Detección de Acordes", "Detección de Intervalos"),
        "en": ("Chord Detection", "Interval Detection"),
    }
    for language, (chords, intervals) in expected.items():
        assert UI_TEXTS[language]["detection_title"] == chords
        assert UI_TEXTS[language]["heading_interval_detection"] == intervals
        assert chords in web_texts
        assert intervals in web_texts
        assert chords in mobile_pages
        assert intervals in mobile_pages
