from midichords.mixins.render_mixin import RenderMixin
from midichords.mixins.input_detection_mixin import InputDetectionMixin


class _Harness(RenderMixin):
    language = "es"

    def note_name(self, midi_note: int, *, with_octave: bool = True) -> str:
        names = ("Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si")
        label = names[int(midi_note) % 12]
        return f"{label}{int(midi_note) // 12 - 1}" if with_octave else label


def test_desktop_c_key_labels_include_the_octave() -> None:
    app = _Harness()

    assert app._keyboard_note_label(48) == "Do3"
    assert app._keyboard_note_label(60) == "Do4"
    assert app._keyboard_note_label(72) == "Do5"
    assert app._keyboard_note_label(62) == "Re"


class _NamingHarness:
    def __init__(self, accidental: str, mode: str) -> None:
        self.config_data = {"language": "en", "note_accidental": accidental}
        self.current_mode = mode


def test_desktop_keyboard_uses_global_flat_names_in_every_mode() -> None:
    app = _NamingHarness("flat", "interval_practice")

    assert InputDetectionMixin.note_name(app, 61, with_octave=False) == "D♭"
    assert InputDetectionMixin.note_name(app, 70, with_octave=False) == "B♭"
