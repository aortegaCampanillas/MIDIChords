from __future__ import annotations

from midichords.mixins.interval_mixin import IntervalMixin


class _IntervalPlaybackHarness(IntervalMixin):
    def __init__(self) -> None:
        self._init_interval_state()
        self.interval_notes = [60, 69]
        self.sounding_notes = {60, 69}
        self.events: list[tuple[str, int]] = []
        self.timers: list[tuple[int, object]] = []

    def play_note(self, note: int, velocity: int = 80) -> bool:
        self.events.append(("on", note))
        return True

    def stop_note(self, note: int, fast: bool = False) -> None:
        self.events.append(("off", note))

    def update_music_views(self) -> None:
        pass

    def after(self, delay: int, callback):
        self.timers.append((delay, callback))
        return callback

    def after_cancel(self, timer) -> None:
        pass


def test_first_reverse_play_releases_retained_notes_before_attack() -> None:
    app = _IntervalPlaybackHarness()

    app.play_interval_melody(reversed_=True)

    first_on = app.events.index(("on", 69))
    assert set(app.events[:first_on]) == {("off", 60), ("off", 69)}
    assert app.sounding_notes == set()
    assert app.timers
    assert app.interval_playing_note == 69


def test_first_forward_play_also_retriggers_retained_notes() -> None:
    app = _IntervalPlaybackHarness()

    app.play_interval_melody()

    first_on = app.events.index(("on", 60))
    assert set(app.events[:first_on]) == {("off", 60), ("off", 69)}
    assert app.interval_playing_note == 60


def test_interval_playback_clears_visual_highlight_after_last_note() -> None:
    app = _IntervalPlaybackHarness()

    app.play_interval_melody()
    app.timers[-1][1]()
    assert app.interval_playing_note == 69
    app.timers[-1][1]()

    assert app.interval_playing_note is None
    assert app.interval_playing_idx is None
    assert app.interval_melody_playback_timer is None
