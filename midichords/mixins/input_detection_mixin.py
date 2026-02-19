from __future__ import annotations

import queue
import time
import tkinter as tk
from typing import Optional

from midichords.core.i18n import NOTE_NAMES
from midichords.core.music_theory import PC_TO_DIATONIC_LETTER, ChordPattern, analyze_chord_notes, format_intervals


class InputDetectionMixin:
    def _clear_live_input_state(self) -> None:
        for note in list(self.active_notes):
            self.audio_engine.note_off(note)
        self.active_notes.clear()
        self.midi_held_notes.clear()
        self.mouse_held_notes.clear()
        self.sustain_latched_notes.clear()
        self.note_velocity.clear()
        self.mouse_current_note = None
    def _clear_detection_hold(self) -> None:
        self.detect_hold_active = False
        self.detect_hold_notes.clear()
    def _current_detection_notes(self) -> set[int]:
        if self.active_notes:
            return set(self.active_notes)
        if self.detect_hold_active:
            return set(self.detect_hold_notes)
        return set()
    def _show_forbidden_note_feedback(self, note: int) -> None:
        self.blocked_note_until[note] = time.monotonic() + 0.35
        self.redraw_keyboard()
        self.after(380, self.redraw_keyboard)
    def _draw_forbidden_icon(self, canvas: tk.Canvas, cx: float, cy: float, radius: float) -> None:
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#d32f2f", width=2)
        canvas.create_line(cx - radius * 0.65, cy + radius * 0.65, cx + radius * 0.65, cy - radius * 0.65, fill="#d32f2f", width=2)
    def _refresh_sounding_notes(self) -> None:
        next_active = self.midi_held_notes | self.mouse_held_notes | self.sustain_latched_notes
        to_start = next_active - self.active_notes
        to_stop = self.active_notes - next_active

        for note in to_start:
            self.audio_engine.note_on(note, int(self.note_velocity.get(note, 100)))
        for note in to_stop:
            self.audio_engine.note_off(note)

        if next_active != self.active_notes:
            self.active_notes = next_active
            self.update_music_views()
    def _note_on_from_source(self, note: int, velocity: int, source: str) -> None:
        if self.current_mode == "detection" and self.detect_hold_active:
            self._clear_detection_hold()
        velocity = int(max(1, min(127, velocity)))
        self.note_velocity[note] = velocity
        self.sustain_latched_notes.discard(note)
        if source == "midi":
            self.midi_held_notes.add(note)
        else:
            self.mouse_held_notes.add(note)
    def _note_off_from_source(self, note: int, source: str) -> None:
        if source == "midi":
            self.midi_held_notes.discard(note)
        else:
            self.mouse_held_notes.discard(note)

        if self.pedal_active:
            if note not in self.midi_held_notes and note not in self.mouse_held_notes:
                self.sustain_latched_notes.add(note)
        else:
            self.sustain_latched_notes.discard(note)
    def _note_at_position(self, x: float, y: float) -> Optional[int]:
        for note, x1, y1, x2, y2 in self.black_key_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return note
        for note, x1, y1, x2, y2 in self.white_key_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return note
        return None
    def _on_keyboard_press(self, event: tk.Event) -> None:
        note = self._note_at_position(float(event.x), float(event.y))
        if note is None:
            return
        if self.generation_tab_active:
            if self.instrument_view == "piano":
                if note in self.generated_preview_notes:
                    self._trigger_generated_single_note(note)
                else:
                    self._show_forbidden_note_feedback(note)
                return
            self._show_forbidden_note_feedback(note)
            return
        if self.scale_tab_active and self.scale_play_mode == "piano":
            scale_pcs = {n % 12 for n in self.scale_preview_notes}
            if (note % 12) not in scale_pcs:
                self._show_forbidden_note_feedback(note)
                return
            if self.mouse_current_note == note:
                return
            if self.mouse_current_note is not None:
                self._note_off_from_source(self.mouse_current_note, source="mouse")
            self.mouse_current_note = note
            self._note_on_from_source(note, velocity=100, source="mouse")
            self.staff_pressed_scale_notes.clear()
            staff_note = self._scale_staff_note_for_pitch(note)
            if staff_note is not None:
                self.staff_pressed_scale_notes.add(staff_note)
            self._refresh_sounding_notes()
            self.redraw_staff()
            return
        if self.pedal_active and note in self.active_notes:
            # Toggle con pedal: clic en nota activa la deselecciona.
            self.mouse_held_notes.discard(note)
            self.sustain_latched_notes.discard(note)
            if self.mouse_current_note == note:
                self.mouse_current_note = None
            self._refresh_sounding_notes()
            return
        if self.mouse_current_note == note:
            return
        if self.mouse_current_note is not None:
            self._note_off_from_source(self.mouse_current_note, source="mouse")
        self.mouse_current_note = note
        self._note_on_from_source(note, velocity=100, source="mouse")
        self._refresh_sounding_notes()
    def _on_keyboard_drag(self, event: tk.Event) -> None:
        note = self._note_at_position(float(event.x), float(event.y))
        if self.generation_tab_active:
            if self.instrument_view == "piano":
                if note is not None and note in self.generated_preview_notes:
                    if (
                        len(self.generated_playing_notes) == 1
                        and note in self.generated_playing_notes
                        and note in self.generated_note_highlight_after
                    ):
                        return
                    self._trigger_generated_single_note(note)
                elif note is not None:
                    self._show_forbidden_note_feedback(note)
            elif note is not None:
                self._show_forbidden_note_feedback(note)
            return
        if self.scale_tab_active and self.scale_play_mode == "piano":
            scale_pcs = {n % 12 for n in self.scale_preview_notes}
            if note is not None and (note % 12) not in scale_pcs:
                note = None
            if note == self.mouse_current_note:
                return
            if self.mouse_current_note is not None:
                self._note_off_from_source(self.mouse_current_note, source="mouse")
                self.mouse_current_note = None
            self.staff_pressed_scale_notes.clear()
            if note is not None:
                self.mouse_current_note = note
                self._note_on_from_source(note, velocity=100, source="mouse")
                staff_note = self._scale_staff_note_for_pitch(note)
                if staff_note is not None:
                    self.staff_pressed_scale_notes.add(staff_note)
            self._refresh_sounding_notes()
            self.redraw_staff()
            return
        if note == self.mouse_current_note:
            return
        if self.mouse_current_note is not None:
            self._note_off_from_source(self.mouse_current_note, source="mouse")
            self.mouse_current_note = None
        if note is not None:
            self.mouse_current_note = note
            self._note_on_from_source(note, velocity=100, source="mouse")
        self._refresh_sounding_notes()
    def _on_keyboard_release(self, _event: tk.Event) -> None:
        if self.mouse_current_note is not None:
            self._note_off_from_source(self.mouse_current_note, source="mouse")
            self.mouse_current_note = None
            if self.scale_tab_active and self.scale_play_mode == "piano":
                self.staff_pressed_scale_notes.clear()
                self.redraw_staff()
            self._refresh_sounding_notes()
    def _on_shift_press(self, _event: tk.Event) -> None:
        if self.current_mode == "detection" and self.detect_hold_active:
            self._clear_detection_hold()
            self.update_music_views()
        self.pedal_active = True
    def _on_shift_release(self, _event: tk.Event) -> None:
        prev_active = set(self.active_notes)
        self.pedal_active = False
        self.sustain_latched_notes.clear()
        self._refresh_sounding_notes()
        if self.current_mode == "detection" and prev_active and not self.active_notes:
            self.detect_hold_notes = prev_active
            self.detect_hold_active = True
            self.update_music_views()
    def _process_midi_queue(self) -> None:
        changed = False
        while True:
            try:
                message = self.message_queue.get_nowait()
            except queue.Empty:
                break

            if self.generation_tab_active:
                if message.type == "note_on" and message.velocity > 0:
                    self._show_forbidden_note_feedback(message.note)
                continue

            if message.type == "note_on" and message.velocity > 0:
                self._note_on_from_source(message.note, velocity=int(message.velocity), source="midi")
                changed = True
            elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                self._note_off_from_source(message.note, source="midi")
                changed = True

        if changed:
            self._refresh_sounding_notes()
        if self.tuner_running:
            self._process_tuner_audio()

        self.after(20, self._process_midi_queue)
    def note_name(self, midi_note: int, with_octave: bool = True) -> str:
        language = self.config_data.get("language", "es")
        base_names = NOTE_NAMES.get(language, NOTE_NAMES["en"])
        name = base_names[midi_note % 12]
        if not with_octave:
            return name
        octave = midi_note // 12 - 1
        return f"{name}{octave}"
    def format_intervals(self, notes: set[int]) -> str:
        return format_intervals(notes)
    def _diatonic_index(self, midi_note: int) -> int:
        octave = midi_note // 12 - 1
        letter_index = PC_TO_DIATONIC_LETTER[midi_note % 12]
        return octave * 7 + letter_index
    def _analyze_chord_notes(self, notes: set[int]) -> tuple[Optional[int], Optional[ChordPattern], Optional[int]]:
        return analyze_chord_notes(notes)
    def detect_chord(self, notes: Optional[set[int]] = None) -> str:
        chord_notes = set(notes if notes is not None else self._current_detection_notes())
        if not chord_notes:
            return "-"

        pcs = {note % 12 for note in chord_notes}
        if len(pcs) == 1:
            note = next(iter(pcs))
            return self.note_name(note, with_octave=False)

        best_root, best_pattern, bass_pc = self._analyze_chord_notes(chord_notes)

        if best_root is None or best_pattern is None:
            ordered = sorted(chord_notes)
            return " + ".join(self.note_name(n, with_octave=False) for n in ordered)

        root = best_root
        pattern = best_pattern
        chord = f"{self.note_name(root, with_octave=False)}{pattern.suffix}"

        if bass_pc is not None and bass_pc != root:
            chord = f"{chord}/{self.note_name(bass_pc, with_octave=False)}"

        return chord
    def update_music_views(self) -> None:
        self._refresh_scale_preview()
        self._refresh_guitar_variations()
        active_set = self._current_detection_notes()
        generated_set = set(self.generated_preview_notes)

        if active_set:
            active_ordered = sorted(active_set)
            self.notes_var.set(" - ".join(self.note_name(note) for note in active_ordered))
        else:
            self.notes_var.set("-")
        self.intervals_var.set(self.format_intervals(active_set))

        if generated_set:
            generated_ordered = sorted(generated_set)
            self.generated_notes_var.set(" - ".join(self.note_name(note) for note in generated_ordered))
        else:
            self.generated_notes_var.set("-")
        self.generated_intervals_var.set(self.format_intervals(generated_set))

        if self.generation_tab_active:
            self.chord_var.set(self.generated_chord_var.get())
        elif self.scale_tab_active:
            self.chord_var.set(self.scale_title_var.get())
        elif self.metronome_tab_active:
            self.chord_var.set("-")
        elif self.tuner_tab_active:
            self.chord_var.set(self.tuner_status_var.get())
        else:
            self.chord_var.set(self.detect_chord(active_set))
        if self.tuner_tab_active:
            self._refresh_tuner_ui()
        self.redraw_keyboard()
        self.redraw_staff()
