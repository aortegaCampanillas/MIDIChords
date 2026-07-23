from midichords.core.interval_data import INTERVAL_GRID_COLUMNS
from midichords.mixins.interval_generation_mixin import IntervalGenerationMixin


class _IntervalGenerationHarness(IntervalGenerationMixin):
    def __init__(self, language: str):
        self.config_data = {"language": language}


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
