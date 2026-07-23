from midichords.core.interval_data import INTERVAL_GRID_COLUMNS
from midichords.mixins.interval_generation_mixin import IntervalGenerationMixin


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
