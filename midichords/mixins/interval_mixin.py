"""Interval detection mixin for chord analyzer app."""

from midichords.core.interval_data import INTERVAL_NAMES, INTERVAL_MELODIES


class IntervalMixin:
    """Mixin providing interval detection and playback."""

    def _init_interval_state(self):
        """Initialize interval detection state."""
        self.interval_notes: list[int] = []
        self.interval_playing_note: int | None = None
        self.interval_playing_idx: int | None = None
        self.interval_melody_playing = False
        self.interval_melody_playback_timer: object | None = None

    def _add_interval_note(self, midi_note: int):
        """Add a note to the interval pair. Keeps only last 2 notes."""
        self.interval_notes.append(midi_note)
        if len(self.interval_notes) > 2:
            self.interval_notes.pop(0)

    def _clear_interval_notes(self):
        """Clear the interval detection notes."""
        self.interval_notes = []
        self.interval_playing_note = None
        self.interval_playing_idx = None
        if self.interval_melody_playback_timer:
            self.master.after_cancel(self.interval_melody_playback_timer)
            self.interval_melody_playback_timer = None

    def get_interval_semitones(self) -> int | None:
        """Calculate semitones between the two interval notes."""
        if len(self.interval_notes) < 2:
            return None
        raw = abs(self.interval_notes[1] - self.interval_notes[0])
        mod = raw % 12
        return 12 if (mod == 0 and raw > 0) else mod

    def get_interval_name(self) -> str:
        """Get the name of the detected interval."""
        semitones = self.get_interval_semitones()
        if semitones is None:
            return "-"
        lang = self.language if self.language in INTERVAL_NAMES else "es"
        return INTERVAL_NAMES[lang].get(semitones, "-")

    def get_interval_melody(self) -> dict | None:
        """Get the reference melody for the detected interval."""
        semitones = self.get_interval_semitones()
        if semitones is None:
            return None
        return INTERVAL_MELODIES.get(semitones)

    def get_interval_melody_name(self) -> str:
        """Get the name of the reference melody."""
        melody = self.get_interval_melody()
        if not melody:
            return "-"
        lang_key = "name_en" if self.language == "en" else "name_es"
        return melody.get(lang_key, "-")

    def get_interval_melody_notes(self) -> list[int | None]:
        """Get the note sequence for the reference melody."""
        if len(self.interval_notes) < 2:
            return sorted(self.interval_notes)

        melody = self.get_interval_melody()
        if not melody:
            return sorted(self.interval_notes)

        base = min(self.interval_notes)
        notes = []
        for offset in melody.get("offsets", []):
            if offset is None:
                notes.append(None)
            else:
                note = base + offset
                notes.append(note if 0 <= note <= 127 else None)
        return notes

    def play_interval_melody(self, reversed_: bool = False):
        """Play the reference melody for the detected interval."""
        melody = self.get_interval_melody()
        if not melody:
            return

        notes = self.get_interval_melody_notes()
        if reversed_:
            notes = list(reversed(notes))

        self.interval_melody_playing = True
        self._play_melody_sequence(notes, melody)

    def _play_melody_sequence(self, notes: list[int | None], melody_info: dict, index: int = 0):
        """Play a sequence of notes with timing from melody info."""
        if index >= len(notes):
            self.interval_melody_playing = False
            return

        note = notes[index]
        if note is not None:
            self.interval_playing_note = note
            self.interval_playing_idx = index
            self.audio_engine.note_on(note, velocity=80)
            self.render()

        # Calculate duration for this note
        durations = melody_info.get("durations", [])
        duration_code = durations[index] if index < len(durations) else "q"
        duration_ms = self._duration_to_ms(duration_code)

        self.interval_melody_playback_timer = self.master.after(
            duration_ms,
            lambda: self._play_melody_sequence_continue(notes, melody_info, index, note)
        )

    def _play_melody_sequence_continue(self, notes: list[int | None], melody_info: dict, index: int, prev_note: int | None):
        """Continue playing melody sequence."""
        if prev_note is not None:
            self.audio_engine.note_off(prev_note)

        self._play_melody_sequence(notes, melody_info, index + 1)

    def _duration_to_ms(self, duration_code: str) -> int:
        """Convert duration code to milliseconds. Assumes quarter note = 500ms (120 BPM)."""
        base_ms = 500

        dotted = duration_code.endswith(".")
        code = duration_code.rstrip(".")

        durations = {
            "w": base_ms * 4,
            "h": base_ms * 2,
            "q": base_ms,
            "e": base_ms / 2,
            "s": base_ms / 4,
            "t": base_ms / 3,  # triplet
            "et": base_ms / 3,  # eighth triplet
        }

        ms = durations.get(code, base_ms)
        if dotted:
            ms = ms * 1.5

        return int(ms)
