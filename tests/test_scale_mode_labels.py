from midichords.mixins.scales_mixin import MODAL_SCALE_DEGREES, ScalesMixin


class _ScaleLabels(ScalesMixin):
    config_data = {"language": "es"}

    @staticmethod
    def scale_name(pattern_name: str) -> str:
        return {
            "Ionian": "Jónica",
            "Dorian": "Dórica",
            "Phrygian": "Frigia",
            "Lydian": "Lidia",
            "Mixolydian": "Mixolidia",
            "Aeolian": "Eólica",
            "Locrian": "Locria",
        }.get(pattern_name, pattern_name)


def test_modal_scale_labels_include_their_roman_degree() -> None:
    labels = _ScaleLabels()

    assert list(MODAL_SCALE_DEGREES.values()) == ["I", "II", "III", "IV", "V", "VI", "VII"]
    assert labels._scale_type_display_label("Ionian") == "Mayor (Jónica) (I)"
    assert labels._scale_type_display_label("Dorian") == "Dórica (II)"
    assert labels._scale_type_display_label("Locrian") == "Locria (VII)"
    assert labels._scale_type_display_label("Chromatic") == "Chromatic"
