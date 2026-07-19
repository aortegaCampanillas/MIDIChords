from midichords.main_app import MidiChordAnalyzerApp
from midichords.mixins.generation_mixin import GenerationMixin


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


class _ChordVariantHarness:
    generation_pattern_suffix = ""
    guitar_selected_variation_idx = 3

    def __init__(self) -> None:
        self.index_seen_during_update: int | None = None

    def _clamp_generation_inversion(self) -> None:
        pass

    def _refresh_generation_selection_buttons(self) -> None:
        pass

    def _update_generation_preview(self) -> None:
        self.index_seen_during_update = self.guitar_selected_variation_idx

    def _preview_generated_chord_short(self) -> None:
        pass


def test_changing_chord_type_resets_guitar_voicing_before_refresh() -> None:
    app = _ChordVariantHarness()

    GenerationMixin._on_generation_variant_clicked(app, "m7")

    assert app.generation_pattern_suffix == "m7"
    assert app.guitar_selected_variation_idx == 0
    assert app.index_seen_during_update == 0
