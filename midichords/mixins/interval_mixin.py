"""Interval detection mixin for chord analyzer app."""

import midichords.qt.tk_compat as tk
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

    def _get_ui_text(self, key: str) -> str:
        """Helper to get translated UI text."""
        from midichords.core.i18n import UI_TEXTS
        lang = self.language if hasattr(self, 'language') else 'es'
        texts = UI_TEXTS.get(lang, UI_TEXTS['es'])
        return texts.get(key, key)

    def _setup_interval_ui(self):
        """Create interval detection UI panel."""
        if hasattr(self, '_interval_panel_created'):
            return

        # Create panel frame
        self.interval_panel = tk.Frame(self.tab_interval_frame, bg=self.color_surface)

        # Title
        title = tk.Label(
            self.interval_panel,
            text=self._get_ui_text('heading_interval_detection'),
            bg=self.color_surface,
            fg=self.color_text,
            font=("Arial", 14, "bold"),
        )
        title.pack(pady=(10, 15))

        # Info frame
        info_frame = tk.Frame(self.interval_panel, bg=self.color_surface)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        # Notes
        notes_label = tk.Label(info_frame, text=self._get_ui_text('label_interval_notes'), bg=self.color_surface, fg=self.color_muted)
        notes_label.pack(anchor=tk.W)
        self.interval_notes_display = tk.Label(info_frame, text="-", bg=self.color_surface, fg=self.color_accent, font=("Courier", 11))
        self.interval_notes_display.pack(anchor=tk.W)

        # Interval name
        name_label = tk.Label(info_frame, text=self._get_ui_text('label_interval_name'), bg=self.color_surface, fg=self.color_muted)
        name_label.pack(anchor=tk.W, pady=(10, 0))
        self.interval_name_display = tk.Label(info_frame, text="-", bg=self.color_surface, fg=self.color_accent, font=("Arial", 12))
        self.interval_name_display.pack(anchor=tk.W)

        # Semitones
        semi_label = tk.Label(info_frame, text=self._get_ui_text('label_interval_semitones'), bg=self.color_surface, fg=self.color_muted)
        semi_label.pack(anchor=tk.W, pady=(10, 0))
        self.interval_semitones_display = tk.Label(info_frame, text="-", bg=self.color_surface, fg=self.color_accent, font=("Arial", 11))
        self.interval_semitones_display.pack(anchor=tk.W)

        # Melody name
        melody_label = tk.Label(info_frame, text=self._get_ui_text('label_interval_example'), bg=self.color_surface, fg=self.color_muted)
        melody_label.pack(anchor=tk.W, pady=(10, 0))
        self.interval_melody_display = tk.Label(info_frame, text="-", bg=self.color_surface, fg=self.color_accent, font=("Arial", 11))
        self.interval_melody_display.pack(anchor=tk.W)

        # Buttons frame
        button_frame = tk.Frame(self.interval_panel, bg=self.color_surface)
        button_frame.pack(fill=tk.X, padx=10, pady=15)

        play_btn = tk.Button(
            button_frame,
            text=self._get_ui_text('button_play_interval'),
            command=self.play_interval_melody,
            bg=self.color_accent,
            fg="#000000",
            relief=tk.FLAT,
            padx=15,
            pady=8,
        )
        play_btn.pack(side=tk.LEFT, padx=(0, 10))

        play_reverse_btn = tk.Button(
            button_frame,
            text=self._get_ui_text('button_play_interval_reverse'),
            command=lambda: self.play_interval_melody(reversed_=True),
            bg=self.color_accent_soft,
            fg="#000000",
            relief=tk.FLAT,
            padx=15,
            pady=8,
        )
        play_reverse_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = tk.Button(
            button_frame,
            text=self._get_ui_text('button_clear'),
            command=self._clear_interval_notes,
            bg=self.color_card,
            fg=self.color_text,
            relief=tk.FLAT,
            padx=15,
            pady=8,
        )
        clear_btn.pack(side=tk.LEFT)

        self.interval_panel.pack(fill=tk.BOTH, expand=True)
        self._interval_panel_created = True

    def _update_interval_display(self):
        """Update interval detection UI with current data."""
        if not hasattr(self, 'interval_panel'):
            return

        # Notes display
        notes_str = " - ".join([self.note_name(n) for n in self.interval_notes]) if self.interval_notes else "-"
        self.interval_notes_display.config(text=notes_str)

        # Interval info
        if len(self.interval_notes) >= 2:
            name = self.get_interval_name()
            semitones = self.get_interval_semitones()
            melody_name = self.get_interval_melody_name()

            self.interval_name_display.config(text=name)
            self.interval_semitones_display.config(text=str(semitones) if semitones else "-")
            self.interval_melody_display.config(text=melody_name)
        else:
            self.interval_name_display.config(text="-")
            self.interval_semitones_display.config(text="-")
            self.interval_melody_display.config(text="-")
