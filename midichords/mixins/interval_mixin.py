"""Interval detection mixin for chord analyzer app."""

from typing import Optional
import midichords.qt.tk_compat as tk
from midichords.core.interval_data import INTERVAL_NAMES, INTERVAL_ALT_NAMES, INTERVAL_MELODIES


class IntervalMixin:
    """Mixin providing interval detection and playback."""

    def _init_interval_state(self):
        """Initialize interval detection state."""
        self.interval_notes: list[int] = []
        # Notes in interval_notes that came from a physical MIDI key, kept
        # even after key release (the pair stays displayed/held until the
        # next note or Clear). Used to keep those notes silent when MIDI out
        # is active, since interval_notes itself doesn't track key-up state.
        self.interval_notes_from_midi: set[int] = set()
        self.interval_playing_note: int | None = None
        self.interval_playing_idx: int | None = None
        self.interval_melody_playing = False
        self.interval_melody_playback_timer: object | None = None
        self.interval_melody_mode: bool = False  # False = play notes, True = play reference song

    def _add_interval_note(self, midi_note: int, *, from_midi: bool = False):
        """Add a note to the interval pair. Keeps only last 2 notes."""
        self.interval_melody_mode = False
        self.interval_notes.append(midi_note)
        if len(self.interval_notes) > 2:
            dropped = self.interval_notes.pop(0)
            self.interval_notes_from_midi.discard(dropped)
        if from_midi:
            self.interval_notes_from_midi.add(midi_note)
        else:
            self.interval_notes_from_midi.discard(midi_note)

    def _clear_interval_notes(self):
        """Clear the interval detection notes."""
        self.interval_notes = []
        self.interval_notes_from_midi = set()
        self.interval_playing_note = None
        self.interval_playing_idx = None
        self.interval_melody_mode = False
        if self.interval_melody_playback_timer:
            self.after_cancel(self.interval_melody_playback_timer)
            self.interval_melody_playback_timer = None
        self._update_interval_display()
        if self.current_mode == "interval_detection":
            self.midi_held_notes = set()
            self.mouse_held_notes = set()
            self.active_notes = set()
            for note in list(self.sounding_notes):
                self.stop_note(note)
            self.sounding_notes.clear()
            self.update_music_views()

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
        lang = getattr(self, "language", None) or self.config_data.get("language", "es")
        lang = lang if lang in INTERVAL_NAMES else "es"
        return INTERVAL_NAMES[lang].get(semitones, "-")

    def get_interval_alt_names(self) -> str:
        """Get other valid enharmonic names for the detected interval."""
        semitones = self.get_interval_semitones()
        if semitones is None:
            return "-"
        lang = getattr(self, "language", None) or self.config_data.get("language", "es")
        lang = lang if lang in INTERVAL_ALT_NAMES else "es"
        names = INTERVAL_ALT_NAMES[lang].get(semitones, [])
        return ", ".join(names) if names else "-"

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
        lang = getattr(self, "language", None) or self.config_data.get("language", "es")
        lang_key = "name_en" if lang == "en" else "name_es"
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

    def _toggle_interval_melody_mode(self):
        """Toggle between playing interval notes and reference song."""
        has_melody = self.get_interval_melody() is not None
        if not has_melody or len(self.interval_notes) < 2:
            return
        self.interval_melody_mode = not self.interval_melody_mode
        if not self.interval_melody_mode:
            self.interval_playing_note = None
            self.interval_playing_idx = None
        self._update_interval_display()
        self.update_music_views()

    def play_interval_melody(self, reversed_: bool = False):
        """Play interval notes or the reference melody depending on current mode."""
        if len(self.interval_notes) < 2:
            return
        if self.interval_melody_mode:
            # Song mode: always play full melody forward
            melody = self.get_interval_melody()
            if not melody:
                return
            notes = self.get_interval_melody_notes()
            self._prepare_interval_playback(notes)
            self.interval_melody_playing = True
            self._play_melody_sequence(notes, melody)
        else:
            # Normal mode: play the two interval notes
            notes_to_play = sorted(self.interval_notes)
            if reversed_:
                notes_to_play = list(reversed(notes_to_play))
            dummy_melody = {"durations": ["q", "q"]}
            self._prepare_interval_playback(notes_to_play)
            self.interval_melody_playing = True
            self._play_melody_sequence(notes_to_play, dummy_melody)

    def _prepare_interval_playback(self, notes: list[int | None]) -> None:
        """Release retained detection voices so transport playback can re-attack."""
        if self.interval_melody_playback_timer:
            self.after_cancel(self.interval_melody_playback_timer)
            self.interval_melody_playback_timer = None
        notes_to_retrigger = {int(note) for note in notes if note is not None}
        for note in notes_to_retrigger & set(self.sounding_notes):
            self.stop_note(note)
        self.sounding_notes -= notes_to_retrigger
        self.interval_playing_note = None
        self.interval_playing_idx = None

    def _play_melody_sequence(self, notes: list[int | None], melody_info: dict, index: int = 0):
        """Play a sequence of notes with timing from melody info."""
        if index >= len(notes):
            self.interval_melody_playing = False
            return

        note = notes[index]
        if note is not None:
            self.interval_playing_note = note
            self.interval_playing_idx = index
            self.play_note(note, velocity=80)
            self.update_music_views()

        # Calculate duration for this note
        durations = melody_info.get("durations", [])
        duration_code = durations[index] if index < len(durations) else "q"
        duration_ms = self._duration_to_ms(duration_code)

        self.interval_melody_playback_timer = self.after(
            duration_ms,
            lambda: self._play_melody_sequence_continue(notes, melody_info, index, note)
        )

    def _play_melody_sequence_continue(self, notes: list[int | None], melody_info: dict, index: int, prev_note: int | None):
        """Continue playing melody sequence."""
        if prev_note is not None:
            self.stop_note(prev_note)

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
        lang = getattr(self, "language", None) or self.config_data.get("language", "es")
        texts = UI_TEXTS.get(lang, UI_TEXTS['es'])
        return texts.get(key, key)

    def _setup_interval_ui(self):
        """Create interval detection UI panel."""
        if hasattr(self, '_interval_panel_created'):
            return

        from midichords.ui.widgets_qt import GrayRoundedButton, PlayTransportButton

        bg = self.color_surface_alt
        self.interval_panel = tk.Frame(self.tab_interval_frame, bg=bg, bd=0, highlightthickness=0)
        self.interval_i18n_labels: list[tuple[object, str]] = []

        # Title — same as chord detection (22 bold)
        self.interval_title_label = tk.Label(
            self.interval_panel,
            text=self._get_ui_text('heading_interval_detection'),
            bg=bg,
            fg=self.color_text,
            font=(self.ui_font_family, 22, "bold"),
        )
        self.interval_title_label.pack(anchor="w", pady=(0, 6))
        self.interval_i18n_labels.append(
            (self.interval_title_label, "heading_interval_detection")
        )

        # Hint subtitle — same as detection_help_label (14)
        self.interval_help_label = tk.Label(
            self.interval_panel,
            text=self._get_ui_text('hint_interval_detection'),
            bg=bg,
            fg=self.color_muted,
            font=(self.ui_font_family, 14),
            justify="left",
            anchor="nw",
            wraplength=800,
        )
        self.interval_help_label.pack(anchor="w", pady=(0, 8))

        # Buttons row: ◄ ► Limpiar — same widget types as detection panel
        controls_row = tk.Frame(self.interval_panel, bg=bg, bd=0, highlightthickness=0)
        controls_row.pack(fill=tk.X, anchor="w", pady=(0, 8))

        self.interval_play_reverse_btn = PlayTransportButton(
            controls_row,
            command=lambda: self.play_interval_melody(reversed_=True),
            width=58,
            height=34,
            reversed_=True,
        )
        self.interval_play_reverse_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.interval_play_btn = PlayTransportButton(
            controls_row,
            command=lambda: self.play_interval_melody(),
            width=58,
            height=34,
        )
        self.interval_play_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.interval_clear_btn = GrayRoundedButton(
            controls_row,
            text=self._get_ui_text('button_clear'),
            command=self._clear_interval_notes,
            font_family=self.ui_font_family,
            width=104,
            height=34,
            radius=14,
            font_size=15,
        )
        self.interval_clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.interval_details_visible = True
        self.interval_details_toggle_btn = GrayRoundedButton(
            controls_row,
            text=self._get_ui_text("button_hide_detection_details"),
            command=self._toggle_interval_details,
            font_family=self.ui_font_family,
            width=112,
            height=34,
            radius=14,
            font_size=15,
            selected_text_color="#17273a",
        )
        self.interval_details_toggle_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Result box — same rounded dark box with dashed border as detection panel
        result_box_bg = "#17273a"
        self.interval_result_canvas = tk.Canvas(
            self.interval_panel,
            bg=bg,
            height=130,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.interval_result_canvas.pack(fill=tk.X, expand=False, pady=(2, 0))

        self.interval_result_inner = tk.Frame(
            self.interval_result_canvas,
            bg=result_box_bg,
            bd=0,
            highlightthickness=0,
        )
        self._interval_result_window_id = self.interval_result_canvas.create_window(
            0, 0, anchor="nw", window=self.interval_result_inner,
        )

        def _redraw_interval_result_block(_event: Optional[tk.Event] = None) -> None:
            w = max(40, int(self.interval_result_canvas.winfo_width()))
            h = max(130, int(self.interval_result_canvas.winfo_height()))
            self.interval_result_canvas.delete("interval_block_bg")
            radius = 15
            self.interval_result_canvas.create_rectangle(
                radius, 1, w - radius, h - 1, fill=result_box_bg, outline="", tags="interval_block_bg",
            )
            self.interval_result_canvas.create_rectangle(
                1, radius, w - 1, h - radius, fill=result_box_bg, outline="", tags="interval_block_bg",
            )
            for sx, sy, start in [(1, 1, 90), (w - radius*2 - 1, 1, 0), (1, h - radius*2 - 1, 180), (w - radius*2 - 1, h - radius*2 - 1, 270)]:
                self.interval_result_canvas.create_arc(
                    sx, sy, sx + radius*2 + 1, sy + radius*2 + 1,
                    fill=result_box_bg, outline="", start=start, extent=90, style=tk.PIESLICE, tags="interval_block_bg",
                )
            dash_color = "#73829a"
            self.interval_result_canvas.create_line(radius+1, 1, w-radius-1, 1, fill=dash_color, width=1, dash=(3,3), tags="interval_block_bg")
            self.interval_result_canvas.create_line(1, radius+1, 1, h-radius-1, fill=dash_color, width=1, dash=(3,3), tags="interval_block_bg")
            self.interval_result_canvas.create_line(radius+1, h-1, w-radius-1, h-1, fill=dash_color, width=1, dash=(3,3), tags="interval_block_bg")
            self.interval_result_canvas.create_line(w-1, radius+1, w-1, h-radius-1, fill=dash_color, width=1, dash=(3,3), tags="interval_block_bg")
            for sx, sy, start in [(1, 1, 90), (w-radius*2-1, 1, 0), (1, h-radius*2-1, 180), (w-radius*2-1, h-radius*2-1, 270)]:
                self.interval_result_canvas.create_arc(
                    sx, sy, sx+radius*2+1, sy+radius*2+1,
                    outline=dash_color, width=1, dash=(3,3), start=start, extent=90, style=tk.ARC, tags="interval_block_bg",
                )
            pad = 8
            self.interval_result_canvas.coords(self._interval_result_window_id, pad, pad)
            self.interval_result_canvas.itemconfigure(
                self._interval_result_window_id,
                width=max(1, w - pad*2),
                height=max(1, h - pad*2),
            )
            self.interval_result_canvas.tag_lower("interval_block_bg")

        self.interval_result_canvas.bind("<Configure>", _redraw_interval_result_block)
        _redraw_interval_result_block()

        # Rows inside result box — same font sizes as detection panel (14)
        def _result_row(label_key, value_fg=None):
            row = tk.Frame(self.interval_result_inner, bg=result_box_bg)
            row.pack(anchor="w", pady=(0, 4), fill=tk.X)
            caption = tk.Label(
                row, text=self._get_ui_text(label_key),
                bg=result_box_bg, fg=self.color_muted,
                font=(self.ui_font_family, 14),
            )
            caption.pack(side=tk.LEFT)
            self.interval_i18n_labels.append((caption, label_key))
            val = tk.Label(
                row, text=" -",
                bg=result_box_bg, fg=value_fg or self.color_text,
                font=(self.ui_mono_font_family, 14),
            )
            val.pack(side=tk.LEFT, padx=(4, 0))
            return row, val

        self.interval_notes_row, self.interval_notes_display = _result_row('label_interval_notes')
        self.interval_name_row, self.interval_name_display = _result_row('label_interval_name', self.color_accent)
        self.interval_alt_row, self.interval_alt_display = _result_row('label_interval_alt')
        self.interval_semitones_row, self.interval_semitones_display = _result_row('label_interval_semitones')

        # Ejemplo row: label + clickable button value
        self.interval_ejemplo_row = tk.Frame(self.interval_result_inner, bg=result_box_bg)
        self.interval_ejemplo_row.pack(anchor="w", pady=(0, 4), fill=tk.X)
        self.interval_example_caption = tk.Label(
            self.interval_ejemplo_row, text=self._get_ui_text('label_interval_example'),
            bg=result_box_bg, fg=self.color_muted,
            font=(self.ui_font_family, 14),
        )
        self.interval_example_caption.pack(side=tk.LEFT)
        self.interval_i18n_labels.append(
            (self.interval_example_caption, "label_interval_example")
        )
        self.interval_melody_btn = GrayRoundedButton(
            self.interval_ejemplo_row,
            text="-",
            command=self._toggle_interval_melody_mode,
            font_family=self.ui_font_family,
            width=120,
            height=28,
            radius=8,
            font_size=13,
            shrink_to_text=True,
            selected_text_color="#dde2e8",
            selected_fill_color="#2b3a50",
            selected_outline_color=self.color_accent,
        )
        self.interval_melody_btn.pack(side=tk.LEFT, padx=(6, 0))
        tk.Frame(self.interval_panel, bg=bg).pack(fill=tk.BOTH, expand=True)

        self.interval_panel.pack(fill=tk.BOTH, expand=True)
        self._interval_panel_created = True
        if hasattr(self, "_refresh_right_panel_wraplengths"):
            self._refresh_right_panel_wraplengths()
        self._refresh_interval_buttons_state()

    def _set_interval_details_visible(self, visible: bool) -> None:
        self.interval_details_visible = bool(visible)
        self.interval_result_canvas.setVisible(self.interval_details_visible)
        key = (
            "button_hide_detection_details"
            if self.interval_details_visible
            else "button_show_detection_details"
        )
        self.interval_details_toggle_btn.set_text(self._get_ui_text(key))
        self.interval_details_toggle_btn.set_selected(not self.interval_details_visible)

    def _toggle_interval_details(self) -> None:
        self._set_interval_details_visible(
            not getattr(self, "interval_details_visible", True)
        )

    def _refresh_interval_ui_language(self) -> None:
        for label, key in getattr(self, "interval_i18n_labels", []):
            label.configure(text=self._get_ui_text(key))
        if hasattr(self, "interval_help_label"):
            self.interval_help_label.configure(
                text=self._get_ui_text("hint_interval_detection")
            )
        if hasattr(self, "interval_clear_btn"):
            self.interval_clear_btn.set_text(self._get_ui_text("button_clear"))
        if hasattr(self, "interval_details_toggle_btn"):
            self._set_interval_details_visible(
                getattr(self, "interval_details_visible", True)
            )

    def _refresh_interval_buttons_state(self):
        """Enable/disable play buttons and update melody button state."""
        if not hasattr(self, '_interval_panel_created'):
            return
        has_two = len(self.interval_notes) >= 2
        has_melody = has_two and self.get_interval_melody() is not None
        self.interval_play_btn.set_enabled(has_two)
        self.interval_play_reverse_btn.set_enabled(has_two and not self.interval_melody_mode)
        self.interval_clear_btn.set_enabled(len(self.interval_notes) > 0)
        self.interval_melody_btn.set_enabled(has_melody)
        self.interval_melody_btn.set_selected(self.interval_melody_mode and has_melody)

    def _update_interval_display(self):
        """Update interval detection UI with current data."""
        if not hasattr(self, 'interval_panel'):
            return

        notes_str = " - ".join([self.note_name(n) for n in self.interval_notes]) if self.interval_notes else "-"
        self.interval_notes_display.configure(text=notes_str)

        if len(self.interval_notes) >= 2:
            name = self.get_interval_name()
            alt_names = self.get_interval_alt_names()
            semitones = self.get_interval_semitones()
            melody_name = self.get_interval_melody_name()
            self.interval_name_display.configure(text=name)
            self.interval_alt_display.configure(text=alt_names)
            self.interval_semitones_display.configure(text=str(semitones) if semitones else "-")
            self.interval_melody_btn.set_text(melody_name)
        else:
            self.interval_name_display.configure(text="-")
            self.interval_alt_display.configure(text="-")
            self.interval_semitones_display.configure(text="-")
            self.interval_melody_btn.set_text("-")

        self._refresh_interval_buttons_state()
