from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_open_guitar_strings_render_finger_zero_on_every_platform() -> None:
    desktop = (ROOT / "midichords/mixins/render_mixin.py").read_text(encoding="utf-8")
    web = (ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")
    mobile = (ROOT / "apps/mobile_flutter/lib/main.dart").read_text(encoding="utf-8")

    assert "shown_finger = 0 if pos_fret == 0" in desktop
    assert "fret === 0 ? 0 : (finger > 0 ? finger : 1)" in web
    assert "f == 0 ? 0 : (selectedFinger > 0 ? selectedFinger : 1)" in mobile


def test_muted_guitar_strings_render_x_at_the_open_string_position() -> None:
    desktop = (ROOT / "midichords/mixins/render_mixin.py").read_text(encoding="utf-8")
    web = (ROOT / "apps/web/static/app.js").read_text(encoding="utf-8")
    mobile = (ROOT / "apps/mobile_flutter/lib/main.dart").read_text(encoding="utf-8")

    assert 'text="X"' in desktop
    assert 'ctx.fillStyle = "#ff5a5a"' in web
    assert 'ctx.fillText("X", cx, y)' in web
    assert "child: Text(\n                            'X'" in mobile
    assert "color: Color(0xFFFF5A5A)" in mobile
