from midichords.main_app import MidiChordAnalyzerApp
from midichords.core.music_theory import ChordPattern
from midichords.mixins.generation_mixin import GenerationMixin
from midichords.mixins.render_mixin import RenderMixin


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


class _CachedGuitarVariationHarness:
    _assign_guitar_fingers = staticmethod(MidiChordAnalyzerApp._assign_guitar_fingers)


def test_cached_open_major_voicings_keep_their_standard_fingerings() -> None:
    app = _CachedGuitarVariationHarness()
    pattern = ChordPattern("", (0, 4, 7))

    cases = (
        (2, [-1, -1, 0, 2, 3, 2], [0, 0, 0, 1, 3, 2]),
        (9, [-1, 0, 2, 2, 2, 0], [0, 0, 2, 3, 4, 0]),
    )
    for root_pc, frets, fingers in cases:
        cached = [{"frets": frets, "fingers": fingers}]

        variations = MidiChordAnalyzerApp._postprocess_cached_guitar_variations(
            app, cached, root_pc, pattern
        )

        assert variations[0]["frets"] == frets
        assert variations[0]["fingers"] == fingers


def test_cached_voicing_recalculates_invalid_fingers() -> None:
    app = _CachedGuitarVariationHarness()
    cached = [{"frets": [-1, 0, 2, 2, 2, 0], "fingers": [0, 9]}]

    variations = MidiChordAnalyzerApp._postprocess_cached_guitar_variations(
        app, cached, 9, ChordPattern("", (0, 4, 7))
    )

    assert variations[0]["fingers"] == [0, 0, 1, 1, 1, 0]


def test_shifted_barre_voicing_does_not_keep_open_strings_behind_it() -> None:
    app = _CachedGuitarVariationHarness()
    cached = [{"frets": [0, 5, 7, 7, 5, 5], "fingers": [0, 1, 3, 4, 1, 1]}]

    variations = MidiChordAnalyzerApp._postprocess_cached_guitar_variations(
        app, cached, 9, ChordPattern("", (0, 4, 7))
    )

    assert variations == []


def test_open_g_major_is_not_drawn_as_a_barre() -> None:
    # Display order is high E -> low E. The B string remains open in the
    # standard 320003 voicing.
    frets = [3, 0, 0, 0, 2, 3]
    fingers = [3, 0, 0, 0, 1, 2]

    segments, covered = RenderMixin._guitar_barre_segments(frets, fingers)

    assert segments == []
    assert covered == set()


def test_matching_finger_still_draws_a_real_barre() -> None:
    frets = [1, 1, 2, 3, 3, 1]
    fingers = [1, 1, 2, 4, 3, 1]

    segments, covered = RenderMixin._guitar_barre_segments(frets, fingers)

    assert segments == [(1, 1, 0, 5, {0, 1, 5})]
    assert covered == {0, 1, 5}


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
