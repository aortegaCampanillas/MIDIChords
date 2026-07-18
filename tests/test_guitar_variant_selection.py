from midichords.main_app import MidiChordAnalyzerApp


class _GuitarVariantHarness:
    def __init__(self) -> None:
        self.guitar_variations = [
            {"notes": [48, 52, 55]},
            {"notes": [52, 55, 60]},
        ]
        self.guitar_selected_variation_idx = 0
        self.guitar_selected_variation_notes = {48, 52, 55}
        self.calls: list[str] = []

    def _refresh_guitar_variations(self) -> None:
        self.calls.append("refresh")

    def redraw_keyboard(self) -> None:
        self.calls.append("keyboard")

    def redraw_staff(self) -> None:
        self.calls.append("staff")

    def _preview_generated_chord_short(self) -> None:
        self.calls.append("play")


def test_selecting_a_new_guitar_variant_updates_and_plays_it() -> None:
    app = _GuitarVariantHarness()

    MidiChordAnalyzerApp._select_guitar_variation(app, 1)

    assert app.guitar_selected_variation_idx == 1
    assert app.guitar_selected_variation_notes == {52, 55, 60}
    assert app.calls == ["refresh", "keyboard", "staff", "play"]


def test_selecting_the_current_or_invalid_variant_is_a_noop() -> None:
    app = _GuitarVariantHarness()

    MidiChordAnalyzerApp._select_guitar_variation(app, 0)
    MidiChordAnalyzerApp._select_guitar_variation(app, -1)
    MidiChordAnalyzerApp._select_guitar_variation(app, 2)

    assert app.calls == []
