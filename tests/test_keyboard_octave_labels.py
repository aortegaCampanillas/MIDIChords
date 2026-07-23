from midichords.mixins.render_mixin import RenderMixin


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
