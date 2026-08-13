from pathlib import Path

from midichords.core.i18n import UI_TEXTS
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


class _PlaybackHarness(IntervalGenerationMixin):
    def __init__(self, instrument_view: str) -> None:
        self._init_interval_generation_state()
        self.instrument_view = instrument_view
        self.sounding_notes = set()
        self.piano_notes = []
        self.guitar_notes = []
        self.stopped_notes = []
        self.callbacks = []
        self.forbidden_notes = []

    def play_note(self, note: int, velocity: int = 80) -> None:
        self.piano_notes.append((note, velocity))

    def pluck_note(
        self,
        note: int,
        velocity: int = 100,
        duration_seconds: float = 1.6,
    ) -> None:
        self.guitar_notes.append((note, velocity, duration_seconds))

    def stop_note(self, note: int) -> None:
        self.stopped_notes.append(note)

    def update_music_views(self) -> None:
        pass

    def after(self, delay: int, callback):
        self.callbacks.append((delay, callback))
        return callback

    def after_cancel(self, _timer) -> None:
        pass

    def _show_forbidden_note_feedback(self, note: int) -> None:
        self.forbidden_notes.append(note)


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


def test_desktop_interval_sequence_uses_selected_instrument_sound() -> None:
    guitar = _PlaybackHarness("guitar")
    guitar._play_interval_gen_sequence([60, 67])

    assert guitar.piano_notes == []
    assert guitar.guitar_notes == [(60, 96, 0.48)]
    guitar.callbacks.pop()[1]()
    assert guitar.guitar_notes[-1] == (67, 96, 0.48)
    assert guitar.stopped_notes == []

    piano = _PlaybackHarness("piano")
    piano._play_interval_gen_sequence([60, 67])

    assert piano.guitar_notes == []
    assert piano.piano_notes == [(60, 80)]
    piano.callbacks.pop()[1]()
    assert piano.piano_notes[-1] == (67, 80)
    assert piano.stopped_notes == [60]


def test_interval_input_accepts_equivalent_notes_in_other_octaves() -> None:
    piano = _PlaybackHarness("piano")
    piano.interval_gen_semitones = 4

    assert piano._handle_interval_gen_input(76)
    assert piano.interval_gen_playing_note == 64
    assert piano.interval_gen_playing_idx == 1
    assert piano.piano_notes == [(76, 100)]
    assert piano.forbidden_notes == []


def test_octave_interval_input_prefers_the_closest_displayed_note() -> None:
    piano = _PlaybackHarness("piano")
    piano.interval_gen_semitones = 12

    assert piano._handle_interval_gen_input(72)
    assert piano.interval_gen_playing_idx == 1

    assert piano._handle_interval_gen_input(48)
    assert piano.interval_gen_playing_idx == 0


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


def test_interval_generation_play_help_explains_persistent_direction() -> None:
    desktop_es = UI_TEXTS["es"]
    desktop_en = UI_TEXTS["en"]
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "ui_texts.js").read_text(
        encoding="utf-8"
    )
    mobile = (
        PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main_help.dart"
    ).read_text(encoding="utf-8")

    assert "reproducciones posteriores" in desktop_es["help_interval_gen_play"]
    assert (
        "reproducciones posteriores"
        in desktop_es["help_interval_gen_play_reverse"]
    )
    assert "subsequent playback" in desktop_en["help_interval_gen_play"]
    assert "subsequent playback" in desktop_en["help_interval_gen_play_reverse"]
    assert web.count("reproducciones posteriores") >= 2
    assert web.count("subsequent playback") >= 2
    assert "interval_generation_play_reverse" in mobile
    assert "interval_generation_play" in mobile
    assert mobile.count("reproducciones posteriores") >= 2
    assert mobile.count("subsequent playback") >= 2


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
    assert "text=self.note_name(note, with_octave=False)" in renderer


def test_interval_guitar_uses_note_names_and_distinct_colors_on_every_platform():
    desktop = (
        PROJECT_ROOT / "midichords" / "mixins" / "render_mixin.py"
    ).read_text(encoding="utf-8")
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    mobile = (
        PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main.dart"
    ).read_text(encoding="utf-8")

    assert 'else ("#22c55e" if is_root else "#f6b60b")' in desktop
    assert "text=self.note_name(note, with_octave=False)" in desktop
    assert 'ctx.fillStyle = isExtra ? "#f48f8f" : isRoot ? "#52d16f" : "#ffd46a"' in web
    assert "const label = noteNameFromPc(pc)" in web
    assert "final isIntervalRoot" in mobile
    assert "const Color(0xFF22C55E)" in mobile
    assert "const Color(0xFFF3BF2F)" in mobile
    assert "_pcLabel(note % 12)" in mobile


def test_web_interval_guitar_keeps_both_notes_during_playback() -> None:
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    active_pcs = web.split("function getActivePcsForMode()", 1)[1].split(
        "function getActiveMidiForMode()", 1
    )[0]
    interval_generation = active_pcs.split(
        'if (state.mode === "interval_generation") {', 1
    )[1].split("}", 1)[0]

    assert "return new Set(intervalGenNotes()" in interval_generation
    assert "intervalGenPlayingNote != null) return new Set" not in interval_generation
    assert "state.intervalGenInputCurrentNote != null" in web
    assert "state.intervalGenPlayingNote != null" in web


def test_web_interval_input_accepts_equivalent_notes_in_other_octaves() -> None:
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    handler = web.split("function handleInstrumentNote(note, options = {})", 1)[
        1
    ].split("function ", 1)[0]

    assert ".filter((n) => (n % 12) === (inputNote % 12))" in handler
    assert "Number(b === inputNote) - Number(a === inputNote)" in handler
    assert "Math.abs(a - inputNote) - Math.abs(b - inputNote)" in handler


def test_web_c_keys_include_their_octave_in_keyboard_labels() -> None:
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )

    assert "function pianoKeyLabelHtml(midi)" in web
    assert "if (pc === 0)" in web
    assert "Math.floor(Number(midi) / 12) - 1" in web
    assert "pianoKeyLabelHtml(midi)" in web


def test_playing_interval_highlights_the_key_not_its_note_badge() -> None:
    desktop = (
        PROJECT_ROOT / "midichords" / "mixins" / "render_mixin.py"
    ).read_text(encoding="utf-8")
    web = (PROJECT_ROOT / "apps" / "web" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    mobile = (
        PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main.dart"
    ).read_text(encoding="utf-8")

    assert "display_active_notes = (" in desktop
    assert "{int(current_interval_note)}" in desktop
    assert 'getattr(self, "interval_playing_note", None)' in desktop
    assert 'note == getattr(self, "interval_playing_note", None)' in desktop
    assert 'circle_fill = "#32d74b" if note == interval_root_note else "#f6b60b"' in desktop
    assert 'midi === intervalCurrentMidi ? "current" : ""' not in web
    assert 'key.classList.add("active")' in web
    assert "final isIntervalCurrent" in mobile
    assert "color: isIntervalCurrent" in mobile
    assert "_tabIndex == 5 || _tabIndex == 7" in mobile
    assert "active: midi == intervalCurrentMidi" not in mobile


def test_desktop_staff_uses_each_chord_notes_diatonic_spelling() -> None:
    desktop = (
        PROJECT_ROOT / "midichords" / "mixins" / "render_mixin.py"
    ).read_text(encoding="utf-8")

    assert "staff_chord_name_map = generation_name_map or detection_name_map" in desktop
    assert "def _note_prefers_flat_spelling(note: int)" in desktop
    assert 'if "♭" in str(label)' in desktop
    assert "self._diatonic_index(note, note_prefers_flat)" in desktop


def test_desktop_interval_staff_initializes_its_shared_horizontal_origin() -> None:
    desktop = (
        PROJECT_ROOT / "midichords" / "mixins" / "render_mixin.py"
    ).read_text(encoding="utf-8")

    origin = desktop.index("chord_x = margin_x + max(")
    interval_layout = desktop.index('elif getattr(self, "interval_tab_active", False):', origin)
    interval_x = desktop.index("x = chord_x + (note_idx * note_rx * 4.6)", interval_layout)

    assert origin < interval_layout < interval_x
