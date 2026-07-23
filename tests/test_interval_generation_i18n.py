from pathlib import Path

from midichords.core.interval_data import INTERVAL_GRID_COLUMNS
from midichords.mixins.interval_generation_mixin import IntervalGenerationMixin


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class _IntervalGenerationHarness(IntervalGenerationMixin):
    def __init__(self, language: str):
        self.config_data = {"language": language}


class _FakeCell:
    def __init__(self):
        self.minimum_width = None
        self.text = None

    def setMinimumWidth(self, width):
        self.minimum_width = width

    def configure(self, *, text):
        self.text = text


def test_interval_grid_titles_follow_configured_english_language():
    harness = _IntervalGenerationHarness("en")

    assert [
        harness._interval_gen_grid_title(column)
        for column in INTERVAL_GRID_COLUMNS
    ] == ["Diminished", "Minor", "Major", "Perfect", "Augmented"]


def test_interval_grid_titles_remain_available_in_spanish():
    harness = _IntervalGenerationHarness("es")

    assert [
        harness._interval_gen_grid_title(column)
        for column in INTERVAL_GRID_COLUMNS
    ] == ["Disminuidas", "Menores", "Mayores", "Justas", "Aumentadas"]


def test_existing_first_column_refreshes_after_language_changes():
    harness = _IntervalGenerationHarness("en")
    rows = [
        (column, _FakeCell(), _FakeCell()) for column in INTERVAL_GRID_COLUMNS
    ]
    harness.interval_gen_title_labels = rows
    harness.ui_font_family = "Arial"

    harness._apply_interval_gen_table_titles(180)
    assert [label.text for _column, _cell, label in rows] == [
        "Diminished",
        "Minor",
        "Major",
        "Perfect",
        "Augmented",
    ]

    harness.config_data["language"] = "es"
    harness._apply_interval_gen_table_titles(210)

    assert [label.text for _column, _cell, label in rows] == [
        "Disminuidas",
        "Menores",
        "Mayores",
        "Justas",
        "Aumentadas",
    ]
    assert {cell.minimum_width for _column, cell, _label in rows} == {210}


def test_applying_desktop_language_refreshes_existing_interval_table():
    source = (
        PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py"
    ).read_text(encoding="utf-8")
    apply_language = source.split("def apply_ui_language(self) -> None:", 1)[1].split(
        "def _refresh_note_accidental_toggle_styles", 1
    )[0]

    assert "self._refresh_interval_gen_ui_language()" in apply_language


def test_interval_modes_register_all_static_labels_for_live_translation():
    detection = (
        PROJECT_ROOT / "midichords" / "mixins" / "interval_mixin.py"
    ).read_text(encoding="utf-8")
    generation = (
        PROJECT_ROOT / "midichords" / "mixins" / "interval_generation_mixin.py"
    ).read_text(encoding="utf-8")

    assert "self.interval_i18n_labels.append((caption, label_key))" in detection
    assert '"heading_interval_detection"' in detection
    assert '"label_interval_example"' in detection
    assert "def _refresh_interval_ui_language" in detection
    assert "self.interval_gen_i18n_labels.append((caption, label_key))" in generation
    assert '"heading_interval_generation"' in generation
    assert '"label_root_note"' in generation
    assert "def _refresh_interval_gen_ui_language" in generation


def test_scale_fingering_labels_refresh_with_desktop_language():
    ui = (
        PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py"
    ).read_text(encoding="utf-8")

    assert 'self.scale_fingering_label.configure(text=self.tr("label_fingering_hand"))' in ui
    assert '"none": self.tr("label_fingering_none")' in ui
    assert '"left": self.tr("label_fingering_left")' in ui
    assert '"right": self.tr("label_fingering_right")' in ui
