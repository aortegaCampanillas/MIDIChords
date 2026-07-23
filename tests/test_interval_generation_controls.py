from pathlib import Path

from midichords.mixins.interval_generation_mixin import IntervalGenerationMixin


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class _Button:
    def __init__(self) -> None:
        self.enabled = False
        self.selected = False

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def set_selected(self, selected: bool) -> None:
        self.selected = selected


class _Harness(IntervalGenerationMixin):
    def __init__(self) -> None:
        self._init_interval_generation_state()
        self._interval_generation_panel_created = True
        self.interval_gen_semitones = 7
        self.interval_gen_play_btn = _Button()
        self.interval_gen_play_reverse_btn = _Button()
        self.played = 0

    def _play_interval_gen_current(self) -> None:
        self.played += 1


def test_desktop_highlights_only_the_last_pressed_direction() -> None:
    app = _Harness()

    app._refresh_interval_gen_buttons_state()
    assert not app.interval_gen_play_btn.selected
    assert not app.interval_gen_play_reverse_btn.selected

    app._play_interval_gen_reverse()
    assert app.interval_gen_play_reverse_btn.selected
    assert not app.interval_gen_play_btn.selected

    app._play_interval_gen_forward()
    assert app.interval_gen_play_btn.selected
    assert not app.interval_gen_play_reverse_btn.selected
    assert app.played == 2


def test_web_persists_only_valid_modes_and_has_no_initial_play_selection() -> None:
    source = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    assert 'const MODE_STORAGE_KEY = "lastMode"' in source
    assert "return AVAILABLE_MODES.has(saved) ? saved : \"detection\";" in source
    assert "saveModePref(mode);" in source
    assert "setMode(savedMode);" in source
    assert "intervalGenLastPlayReverse: null" in source
    assert "state.intervalGenLastPlayReverse === false" in source
    assert "state.intervalGenLastPlayReverse === true" in source
    interval_bindings = source.split(
        'bindImmediatePress(el("intervalGenPlayReverse")'
    )[1].split("bindKeyboardUiEvents", 1)[0]
    assert "highlightWhilePressed" not in interval_bindings


def test_desktop_selected_transport_keeps_the_triangle_icon() -> None:
    source = (
        PROJECT_ROOT / "midichords" / "ui" / "widgets_qt.py"
    ).read_text(encoding="utf-8")

    assert "elif self._playing or self._selected:" in source
    assert "if self._playing:" in source
    assert "def set_selected(self, selected: bool)" in source


def test_desktop_interval_generation_exposes_and_renders_guitar() -> None:
    ui = (
        PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py"
    ).read_text(encoding="utf-8")
    renderer = (
        PROJECT_ROOT / "midichords" / "mixins" / "render_mixin.py"
    ).read_text(encoding="utf-8")

    interval_mode = ui.split("elif self.interval_gen_tab_active:", 1)[1].split(
        "else:", 1
    )[0]
    assert "self._show_generation_instrument_buttons()" in interval_mode
    assert "self._set_instrument_view(self.instrument_view)" in interval_mode
    assert 'getattr(self, "interval_gen_tab_active", False)' in renderer
    assert 'text="1" if is_root else "2"' in renderer
