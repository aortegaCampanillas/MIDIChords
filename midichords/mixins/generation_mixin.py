from __future__ import annotations

import tkinter as tk
from midichords.core.music_theory import CHORD_PATTERNS, ChordPattern
from midichords.ui.widgets import GrayRoundedButton


class GenerationMixin:
    def _refresh_generation_controls(self) -> None:
        if self.generation_pattern_suffix not in {p.suffix for p in CHORD_PATTERNS}:
            self.generation_pattern_suffix = ""
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _refresh_generation_selection_buttons(self) -> None:
        self.generation_root_btn.set_text(self.note_name(self.generation_root_pc, with_octave=False))
        variant_label = self.generation_pattern_suffix if self.generation_pattern_suffix else "maj"
        self.generation_variant_btn.set_text(variant_label)
        self.generation_inversion_btn.set_text(self._inversion_label(self.generation_inversion))
    def _clear_generated_single_note(self, note: int) -> None:
        if note in self.generated_playing_notes:
            self.generated_playing_notes.discard(note)
            if self.generation_tab_active:
                self.redraw_guitar_fretboard()
                self.redraw_staff()
    def _activate_generation_drag_note(self, note: int) -> None:
        if not (self.generation_tab_active and self.instrument_view == "guitar"):
            return
        if self.guitar_selected_variation_notes and note not in self.guitar_selected_variation_notes:
            return
        if note in self.generation_drag_notes and len(self.generation_drag_notes) == 1:
            return
        self.generation_drag_notes = {note}
        self.generated_playing_notes = {note}
        self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.1)
        self.redraw_guitar_fretboard()
        self.redraw_staff()
    def _clear_generation_drag_state(self) -> None:
        if not (self.generation_guitar_drag_active or self.generation_staff_drag_active or self.generation_drag_notes):
            return
        self.generation_guitar_drag_active = False
        self.generation_staff_drag_active = False
        self.generation_drag_notes.clear()
        self.generation_drag_moved = False
        self.generated_playing_notes.clear()
        if self.generation_tab_active:
            self.redraw_guitar_fretboard()
            self.redraw_staff()
    def _max_generation_inversion(self) -> int:
        pattern = self._resolve_generation_pattern()
        return max(0, len(pattern.intervals) - 1)
    def _clamp_generation_inversion(self) -> None:
        max_inv = self._max_generation_inversion()
        self.generation_inversion = max(0, min(self.generation_inversion, max_inv))
    def _on_generation_root_clicked(self, pc: int) -> None:
        self.generation_root_pc = pc
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _on_generation_variant_clicked(self, suffix: str) -> None:
        self.generation_pattern_suffix = suffix
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _on_generation_inversion_clicked(self, inversion: int) -> None:
        self.generation_inversion = inversion
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _close_generation_selection_overlay(self) -> None:
        if self.generation_selection_overlay is not None:
            self.generation_selection_overlay.destroy()
            self.generation_selection_overlay = None
    def _open_generation_selection_overlay(self, kind: str) -> None:
        if self.generation_selection_overlay is not None:
            self._close_generation_selection_overlay()

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.generation_selection_overlay = overlay

        header = tk.Frame(overlay, bg="#2b2d38")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        if kind == "root":
            title = self.tr("label_root_note")
        elif kind == "variant":
            title = self.tr("label_variant")
        else:
            title = self.tr("label_inversion")
        tk.Label(header, text=title, bg="#2b2d38", fg="#f0f0f0", font=("Helvetica", 13, "bold")).pack(side=tk.LEFT)

        if kind == "root":
            buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
            columns = 3
            options: list[tuple[str, int, bool]] = []
            for pc in range(12):
                options.append((self.note_name(pc, with_octave=False), pc, pc == self.generation_root_pc))
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            for idx, (label, value, selected) in enumerate(options):
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=str(label),
                    command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                    width=122,
                    height=74,
                    radius=28,
                    font_size=22,
                )
                btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                btn.set_selected(bool(selected))
            return

        if kind == "variant":
            body = tk.Frame(overlay, bg="#2b2d38")
            body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))
            search_var, entry = self._build_rounded_search_entry(body, self.tr("label_search_variant"))

            buttons_frame = self._build_scrollable_area(body, bg="#2b2d38", padx=0, pady=(0, 0))
            columns = 3
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            def render_buttons() -> None:
                for w in buttons_frame.winfo_children():
                    w.destroy()
                term = search_var.get().strip().lower()
                options: list[tuple[str, str, bool]] = []
                for pattern in CHORD_PATTERNS:
                    label = pattern.suffix if pattern.suffix else "maj"
                    if term and term not in label.lower():
                        continue
                    options.append((label, pattern.suffix, pattern.suffix == self.generation_pattern_suffix))
                for idx, (label, value, selected) in enumerate(options):
                    btn = GrayRoundedButton(
                        buttons_frame,
                        text=str(label),
                        command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                        width=160,
                        height=64,
                        radius=24,
                        font_size=16,
                    )
                    btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                    btn.set_selected(bool(selected))

            search_var.trace_add("write", lambda *_args: render_buttons())
            render_buttons()
            entry.focus_set()
            return

        # inversion
        buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
        if kind == "inversion":
            columns = 3
            options: list[tuple[str, int, bool]] = []
            for inv in range(self._max_generation_inversion() + 1):
                options.append((self._inversion_label(inv), inv, inv == self.generation_inversion))
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)
            for idx, (label, value, selected) in enumerate(options):
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=str(label),
                    command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                    width=160,
                    height=64,
                    radius=24,
                    font_size=16,
                )
                btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                btn.set_selected(bool(selected))
    def _select_generation_overlay_value(self, kind: str, value) -> None:
        if kind == "root":
            self._on_generation_root_clicked(int(value))
        elif kind == "variant":
            self._on_generation_variant_clicked(str(value))
        else:
            self._on_generation_inversion_clicked(int(value))
        self._close_generation_selection_overlay()
    def open_generation_root_dialog(self) -> None:
        self._open_generation_selection_overlay("root")
    def open_generation_variant_dialog(self) -> None:
        self._open_generation_selection_overlay("variant")
    def open_generation_inversion_dialog(self) -> None:
        self._open_generation_selection_overlay("inversion")
    def _finalize_generation_space_release(self) -> None:
        self.generation_space_release_after_id = None
        if self.generation_tab_active and self.generation_play_space_pressed:
            self._stop_generated_hold(source="space")
    def _resolve_generation_pattern(self) -> ChordPattern:
        for pattern in CHORD_PATTERNS:
            if pattern.suffix == self.generation_pattern_suffix:
                return pattern
        return CHORD_PATTERNS[0]
    def _update_generation_preview(self) -> None:
        was_playing = self.generation_play_button_pressed or bool(self.generated_playing_notes)
        if was_playing:
            self._stop_generated_playback()

        pattern = self._resolve_generation_pattern()
        self.generation_pattern_suffix = pattern.suffix

        root_midi = 60 + self.generation_root_pc
        intervals = list(pattern.intervals)
        if not intervals:
            self.generated_preview_notes = set()
            self.generated_chord_var.set("-")
            self.generated_notes_var.set("-")
            if self.generation_tab_active:
                self.update_music_views()
            return

        max_inversion = len(intervals) - 1
        inversion = min(max(0, self.generation_inversion), max_inversion)
        if inversion != self.generation_inversion:
            self.generation_inversion = inversion
            self._refresh_generation_selection_buttons()

        voiced_intervals = [(interval + (12 if idx < inversion else 0)) for idx, interval in enumerate(intervals)]
        voiced_intervals.sort()
        voiced_notes = [root_midi + interval for interval in voiced_intervals]
        self.generated_preview_notes = set(voiced_notes)

        shown_suffix = pattern.suffix if pattern.suffix else ""
        chord_name = f"{self.note_name(self.generation_root_pc, with_octave=False)}{shown_suffix}"
        if inversion > 0 and voiced_notes:
            bass_pc = voiced_notes[0] % 12
            chord_name = f"{chord_name}/{self.note_name(bass_pc, with_octave=False)}"
        self.generated_chord_var.set(chord_name)
        if self.generated_preview_notes:
            ordered = sorted(self.generated_preview_notes)
            self.generated_notes_var.set(" - ".join(self.note_name(note) for note in ordered))
        else:
            self.generated_notes_var.set("-")

        if was_playing and self.generation_play_button_pressed:
            self._play_generated_chord()

        if self.generation_tab_active:
            self.update_music_views()
    def _load_generation_from_detected_notes(self, notes: set[int]) -> None:
        if not notes:
            return
        root, pattern, bass_pc = self._analyze_chord_notes(notes)
        if root is None:
            root = min(notes) % 12
        if pattern is None:
            pattern = CHORD_PATTERNS[0]
        self.generation_root_pc = root
        self.generation_pattern_suffix = pattern.suffix
        inversion = 0
        if bass_pc is not None:
            for idx, interval in enumerate(pattern.intervals):
                if (root + interval) % 12 == bass_pc:
                    inversion = idx
                    break
        self.generation_inversion = inversion
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _stop_generated_playback(self) -> None:
        self.generation_guitar_drag_active = False
        self.generation_staff_drag_active = False
        self.generation_piano_staff_drag_active = False
        self.generation_drag_notes.clear()
        self.generation_drag_moved = False
        if self.generated_play_after_id is not None:
            try:
                self.after_cancel(self.generated_play_after_id)
            except Exception:
                pass
            self.generated_play_after_id = None
        for after_id in list(self.generated_note_highlight_after.values()):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self.generated_note_highlight_after.clear()
        for note in list(self.generated_playing_notes):
            self.audio_engine.note_off(note)
        self.generated_playing_notes.clear()
        if self.generation_tab_active:
            self.redraw_staff()
    def _generation_staff_note_at_position(self, x: float, y: float) -> Optional[int]:
        if not self.generation_tab_active:
            return None
        best_note: Optional[int] = None
        best_dist = 10_000.0
        for note, cx, cy, rx, ry in self.staff_generation_note_regions:
            nx = (x - cx) / max(1.0, rx + 4.0)
            ny = (y - cy) / max(1.0, ry + 3.0)
            if (nx * nx + ny * ny) > 1.0:
                continue
            dist = abs(x - cx) + abs(y - cy)
            if dist < best_dist:
                best_dist = dist
                best_note = note
        return best_note
    def _clear_generated_note_highlight(self, note: int, stop_audio: bool = True) -> None:
        self.generated_note_highlight_after.pop(note, None)
        if note in self.generated_playing_notes:
            self.generated_playing_notes.discard(note)
        if stop_audio:
            self.audio_engine.note_off(note)
        if self.generation_tab_active:
            self.redraw_keyboard()
            self.redraw_guitar_fretboard()
            self.redraw_staff()
    def _trigger_generated_single_note(self, note: int) -> None:
        if self.generation_tab_active and self.instrument_view == "guitar" and self.guitar_selected_variation_notes:
            allowed_notes = set(self.guitar_selected_variation_notes)
        else:
            allowed_notes = set(self.generated_preview_notes)
        if note not in allowed_notes:
            return
        for after_id in list(self.generated_note_highlight_after.values()):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self.generated_note_highlight_after.clear()
        self.generated_playing_notes.clear()
        if note in self.generated_note_highlight_after:
            try:
                self.after_cancel(self.generated_note_highlight_after[note])
            except Exception:
                pass
            self.generated_note_highlight_after.pop(note, None)
        self.generated_playing_notes.add(note)
        if self.instrument_view == "guitar":
            self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.1)
            stop_audio = False
        else:
            self.audio_engine.note_on(note, 108)
            stop_audio = True
        self.generated_note_highlight_after[note] = self.after(
            520,
            lambda n=note, s=stop_audio: self._clear_generated_note_highlight(n, stop_audio=s),
        )
        if self.generation_tab_active:
            self.redraw_keyboard()
            self.redraw_guitar_fretboard()
            self.redraw_staff()
    def _play_generated_chord(self) -> None:
        if not self.generated_preview_notes:
            return
        self._stop_generated_playback()
        if self.instrument_view == "guitar":
            for note in sorted(self.generated_preview_notes):
                self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.3)
        else:
            for note in sorted(self.generated_preview_notes):
                self.audio_engine.note_on(note, 108)
                self.generated_playing_notes.add(note)
        if self.generation_tab_active:
            self.redraw_staff()
    def _start_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = True
        else:
            self.generation_play_space_pressed = True
        self.generation_play_btn.state(["pressed"])
        self._play_generated_chord()
    def _stop_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = False
        else:
            self.generation_play_space_pressed = False
        if self.generation_play_button_pressed or self.generation_play_space_pressed:
            return
        self.generation_play_btn.state(["!pressed"])
        self._stop_generated_playback()
    def _on_generation_play_press(self, _event: tk.Event) -> str:
        self._start_generated_hold(source="button")
        return "break"
