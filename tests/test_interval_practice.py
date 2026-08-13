from midichords.mixins.interval_practice_mixin import IntervalPracticeMixin


class _PracticeHarness(IntervalPracticeMixin):
    interval_practice_random_tonic = False
    interval_practice_ascending_only = True
    interval_practice_allowed_semitones = set(range(13))
    interval_practice_deck = []
    interval_practice_last_semitones = None


def test_choices_respect_second_note_filter_and_direction():
    app = _PracticeHarness()
    app.interval_practice_allowed_semitones = {0, 6, 12}
    choices = app._interval_practice_choices()
    assert {choice["semitones"] for choice in choices} == {0, 6, 12}
    assert {choice["direction"] for choice in choices} == {1}

    app.interval_practice_ascending_only = False
    choices = app._interval_practice_choices()
    assert {choice["direction"] for choice in choices if choice["semitones"] == 6} == {-1, 1}


def test_balanced_deck_covers_every_allowed_distance_before_repeating():
    app = _PracticeHarness()
    app.interval_practice_allowed_semitones = {1, 4, 7}
    drawn = [app._draw_interval_practice_choice()["semitones"] for _ in range(3)]
    assert set(drawn) == {1, 4, 7}


def test_filter_keeps_unison_and_octave_independent():
    app = _PracticeHarness()
    app.interval_practice_allowed_semitones = {12}
    choices = app._interval_practice_choices()
    assert {choice["semitones"] for choice in choices} == {12}
