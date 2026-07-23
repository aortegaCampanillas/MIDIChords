from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_interval_notes_use_scale_style_circles_on_every_platform():
    desktop = (ROOT / "midichords/mixins/render_mixin.py").read_text(
        encoding="utf-8"
    )
    web = (ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")
    mobile = (ROOT / "apps/mobile_flutter/lib/main.dart").read_text(
        encoding="utf-8"
    )

    assert "interval_marker_set" in desktop
    assert 'circle_fill = "#32d74b" if note == interval_root_note else "#f6b60b"' in desktop
    assert "scale-badge interval-badge" in web
    assert "intervalNoteSet.has(midi)" in web
    assert "_intervalPianoMarker(" in mobile
    assert "intervalNoteSet.contains(midi)" in mobile


def test_desktop_interval_names_are_not_drawn_above_the_keyboard():
    desktop = (ROOT / "midichords/mixins/render_mixin.py").read_text(
        encoding="utf-8"
    )

    assert "and not interval_marker_set" in desktop
