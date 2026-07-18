from midichords.core.music_theory import SCALE_PATTERNS
from midichords.mixins.scales_mixin import MODAL_SCALE_DEGREES, SCALE_FAMILY_GROUPS, ScalesMixin


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


class _Value:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


class _GroupedCombo:
    def __init__(self) -> None:
        self.groups: list[tuple[str, list[str]]] = []

    def set_grouped_values(self, groups: list[tuple[str, list[str]]]) -> None:
        self.groups = groups


def test_modal_scale_labels_include_their_roman_degree() -> None:
    labels = _ScaleLabels()

    assert list(MODAL_SCALE_DEGREES.values()) == ["I", "II", "III", "IV", "V", "VI", "VII"]
    assert labels._scale_type_display_label("Ionian") == "Mayor (Jónica) (I)"
    assert labels._scale_type_display_label("Dorian") == "Dórica (II)"
    assert labels._scale_type_display_label("Locrian") == "Locria (VII)"
    assert labels._scale_type_display_label("Chromatic") == "Chromatic"


def test_scale_families_cover_the_catalog_once_and_keep_modes_ordered() -> None:
    grouped_names = [name for _key, names in SCALE_FAMILY_GROUPS for name in names]

    assert grouped_names[:7] == list(MODAL_SCALE_DEGREES)
    assert len(grouped_names) == len(set(grouped_names)) == len(SCALE_PATTERNS)
    assert set(grouped_names) == {pattern.name for pattern in SCALE_PATTERNS}


def test_desktop_scale_combo_uses_non_selectable_family_groups() -> None:
    labels = _ScaleLabels()
    labels.scale_type_combo = _GroupedCombo()
    labels.scale_type_var = _Value()
    labels.scale_filter_mode = "all"
    labels.scale_pattern_name = "Ionian"

    labels._update_scale_type_combo()

    assert [label for label, _values in labels.scale_type_combo.groups] == [
        "Modos griegos",
        "Escalas menores",
        "Modos alterados",
        "Pentatónicas y blues",
        "Bebop",
        "Simétricas y sintéticas",
        "Tradicionales del mundo",
    ]
    assert labels.scale_type_combo.groups[0][1][:2] == ["Mayor (Jónica) (I)", "Dórica (II)"]
