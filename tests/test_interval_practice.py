from pathlib import Path

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


def test_new_question_playback_cancels_pending_single_note_clear():
    app = _PracticeHarness()
    app.interval_practice_playback_mode = "melodic"
    app.interval_practice_single_timer = "old-clear"
    app.interval_gen_input_clear_timer = "previous-mode-clear"
    app.cancelled = []
    app.played = []
    app.after_cancel = app.cancelled.append
    app._play_interval_gen_sequence = app.played.append

    app._play_interval_practice_notes([60, 64], hide_second=True)

    assert app.cancelled == ["old-clear", "previous-mode-clear"]
    assert app.interval_practice_single_timer is None
    assert app.interval_gen_input_clear_timer is None
    assert app.played == [[60, 64]]


def test_filter_keyboards_show_pitch_names_without_octaves_on_every_platform():
    desktop = Path("midichords/mixins/interval_practice_mixin.py").read_text()
    web = Path("apps/web/static/app.js").read_text()
    mobile = Path("apps/mobile_flutter/lib/main_pages.dart").read_text()

    assert "self.note_name(60 + semitones, with_octave=False)" in desktop
    assert "key.textContent = noteNameFromPc(semitones);" in web
    assert "_pcLabel(semitones % 12)" in mobile


def test_answered_table_cell_replays_selected_descending_interval():
    app = _PracticeHarness()
    app.interval_practice_running = False
    app.interval_practice_root = 60
    app.interval_practice_direction = -1
    app.interval_practice_semitones = 7
    app.interval_practice_answer = {
        "note": 57,
        "semitones": 3,
        "correct": False,
    }
    app.played = []
    app._play_interval_practice_notes = app.played.append

    assert app._answer_interval_practice(semitones=7)
    assert app._answer_interval_practice(semitones=3)
    assert not app._answer_interval_practice(semitones=5)
    assert app.played == [[60, 53], [60, 57]]


def test_table_feedback_marks_the_correct_and_wrong_semitone_columns():
    app = _PracticeHarness()
    app.interval_practice_column_key = "augmented"
    app.interval_practice_semitones = 1
    app.interval_practice_answer = {
        "note": 62,
        "semitones": 2,
        "column_key": "major",
        "correct": False,
    }

    assert app._interval_practice_cell_feedback("augmented", 1) == "correct"
    assert app._interval_practice_cell_feedback("major", 2) == "wrong"
    assert app._interval_practice_cell_feedback("diminished", 2) == "wrong"
    assert app._interval_practice_cell_feedback("minor", 1) == "correct"


def test_piano_answer_marks_every_matching_spelling_when_row_is_unknown():
    app = _PracticeHarness()
    app.interval_practice_column_key = "perfect"
    app.interval_practice_semitones = 7
    app.interval_practice_answer = {
        "note": 68,
        "semitones": 8,
        "column_key": None,
        "correct": False,
    }

    assert app._interval_practice_cell_feedback("minor", 8) == "wrong"
    assert app._interval_practice_cell_feedback("augmented", 8) == "wrong"
    assert app._interval_practice_cell_feedback("perfect", 7) == "correct"


def test_piano_answer_normalizes_compound_distance_to_the_table_column():
    app = _PracticeHarness()
    app.interval_practice_started = True
    app.interval_practice_running = True
    app.interval_practice_root = 57
    app.interval_practice_direction = 1
    app.interval_practice_semitones = 1
    app.interval_practice_column_key = "minor"
    app.interval_practice_total = 0
    app.interval_practice_correct = 0
    app.interval_practice_repetitions = 3
    app.interval_practice_answer = None
    app.interval_practice_history = []
    app._play_interval_practice_notes = lambda _notes: None
    app._refresh_interval_practice_ui = lambda: None

    assert app._answer_interval_practice(note=71)
    assert app.interval_practice_answer["semitones"] == 14
    assert app.interval_practice_answer["table_semitones"] == 2
    assert app._interval_practice_cell_feedback("major", 2) == "wrong"
