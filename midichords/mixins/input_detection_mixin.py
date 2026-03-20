from __future__ import annotations

import queue
import time
import midichords.qt.tk_compat as tk
from typing import Optional

from midichords.core.i18n import NOTE_NAMES
from midichords.core.music_theory import PC_TO_DIATONIC_LETTER, ChordPattern, analyze_chord_notes, format_intervals


class InputDetectionMixin:
    @staticmethod
    def _detection_interval_degree(interval: int, suffix: str) -> int:
        value = int(interval)
        suffix_text = str(suffix)
        if value in {0, 12}:
            return 0
        if value in {1, 2, 13, 14}:
            return 1
        if value in {3, 4, 15}:
            return 2
        if value in {5, 17}:
            return 3
        if value in {6, 18}:
            if ("b5" in suffix_text) or ("dim" in suffix_text):
                return 4
            return 3
        if value == 7:
            return 4
        if value == 8:
            if ("#5" in suffix_text) or ("aug" in suffix_text):
                return 4
            return 5
        if value in {9, 21}:
            return 5
        if value in {10, 11}:
            return 6
        return max(0, min(6, value % 7))

    def _spell_detection_note_name(
        self,
        root_pc: int,
        target_pc: int,
        degree: int,
        prefer_flats: bool,
        midi_note: Optional[int] = None,
        with_octave: bool = False,
    ) -> str:
        language = str(self.config_data.get("language", "es"))
        letter_names = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] if language == "es" else ["C", "D", "E", "F", "G", "A", "B"]
        base_pcs = [0, 2, 4, 5, 7, 9, 11]
        tonic_letter = self._tonic_letter_index(root_pc, prefer_flats)
        letter_idx = (tonic_letter + int(degree)) % 7
        base_pc = base_pcs[letter_idx]
        diff = (int(target_pc) - base_pc) % 12
        if diff > 6:
            diff -= 12
        if diff == 0:
            accidental = ""
        elif diff == 1:
            accidental = "#"
        elif diff == -1:
            accidental = "♭"
        elif diff == 2:
            accidental = "##"
        elif diff == -2:
            accidental = "♭♭"
        else:
            fallback_note = int(midi_note if midi_note is not None else target_pc)
            return self.note_name(fallback_note, with_octave=with_octave)
        name = f"{letter_names[letter_idx]}{accidental}"
        if with_octave:
            if midi_note is None:
                return name
            octave = int(midi_note) // 12 - 1
            return f"{name}{octave}"
        return name

    def _detect_harmonic_spelling(
        self,
        notes: set[int],
    ) -> tuple[str, set[int], dict[int, str], dict[int, str]]:
        chord_notes = set(notes)
        if not chord_notes:
            return "-", set(), {}, {}

        pcs = {note % 12 for note in chord_notes}
        if len(pcs) == 1:
            single_pc = next(iter(pcs))
            chord = self.note_name(single_pc, with_octave=False)
            map_oct = {int(n): self.note_name(int(n), with_octave=True) for n in chord_notes}
            map_no_oct = {int(n): self.note_name(int(n), with_octave=False) for n in chord_notes}
            return chord, set(), map_oct, map_no_oct

        root, pattern, bass_pc = self._analyze_chord_notes(chord_notes)
        if root is None or pattern is None:
            ordered = sorted(chord_notes)
            chord = " + ".join(self.note_name(n, with_octave=False) for n in ordered)
            map_oct = {int(n): self.note_name(int(n), with_octave=True) for n in chord_notes}
            map_no_oct = {int(n): self.note_name(int(n), with_octave=False) for n in chord_notes}
            return chord, set(), map_oct, map_no_oct

        prefer_flats = str(self.config_data.get("note_accidental", "sharp")) == "flat"
        degree_by_pc: dict[int, int] = {}
        for interval in pattern.intervals:
            pc = (int(root) + int(interval)) % 12
            if pc not in degree_by_pc:
                degree_by_pc[pc] = self._detection_interval_degree(int(interval), str(pattern.suffix))

        root_name = self._spell_detection_note_name(
            root_pc=int(root),
            target_pc=int(root),
            degree=0,
            prefer_flats=prefer_flats,
            midi_note=int(root),
            with_octave=False,
        )
        chord = f"{root_name}{pattern.suffix}"
        if bass_pc is not None and bass_pc != root:
            bass_degree = degree_by_pc.get(int(bass_pc))
            if bass_degree is not None:
                bass_name = self._spell_detection_note_name(
                    root_pc=int(root),
                    target_pc=int(bass_pc),
                    degree=int(bass_degree),
                    prefer_flats=prefer_flats,
                    midi_note=int(bass_pc),
                    with_octave=False,
                )
            else:
                bass_name = self.note_name(int(bass_pc), with_octave=False)
            chord = f"{chord}/{bass_name}"

        expected_pcs = {(int(root) + int(interval)) % 12 for interval in pattern.intervals}
        # Treat as extra only notes outside the detected chord pitch classes.
        # Duplicates across octaves are valid (e.g., left-hand reinforcement).
        extras: set[int] = {int(note) for note in chord_notes if (int(note) % 12) not in expected_pcs}

        map_oct: dict[int, str] = {}
        map_no_oct: dict[int, str] = {}
        for note in chord_notes:
            note_int = int(note)
            pc = note_int % 12
            degree = degree_by_pc.get(pc)
            if degree is None:
                map_oct[note_int] = self.note_name(note_int, with_octave=True)
                map_no_oct[note_int] = self.note_name(note_int, with_octave=False)
                continue
            map_oct[note_int] = self._spell_detection_note_name(
                root_pc=int(root),
                target_pc=pc,
                degree=int(degree),
                prefer_flats=prefer_flats,
                midi_note=note_int,
                with_octave=True,
            )
            map_no_oct[note_int] = self._spell_detection_note_name(
                root_pc=int(root),
                target_pc=pc,
                degree=int(degree),
                prefer_flats=prefer_flats,
                midi_note=note_int,
                with_octave=False,
            )
        return chord, extras, map_oct, map_no_oct

    def _clear_live_input_state(self) -> None:
        for note in list(self.sounding_notes):
            self.audio_engine.note_off(note)
        self.sounding_notes.clear()
        self.active_notes.clear()
        self.midi_held_notes.clear()
        self.mouse_held_notes.clear()
        self.sustain_latched_notes.clear()
        self.midi_latched_notes.clear()
        self.note_velocity.clear()
        self.mouse_current_note = None
        self.detection_mouse_chord_notes.clear()
        self.detection_midi_held_notes.clear()
        self.detection_shift_pressed = False
        self._clear_detection_hold()
    def _clear_detection_hold(self) -> None:
        self.detect_hold_active = False
        self.detect_hold_notes.clear()
    def _current_detection_notes(self) -> set[int]:
        if self.detection_midi_held_notes:
            return set(self.detection_midi_held_notes)
        return set(self.detection_mouse_chord_notes)
    def _show_forbidden_note_feedback(self, note: int) -> None:
        self.blocked_note_until[note] = time.monotonic() + 0.35
        self.redraw_keyboard()
        self.after(380, self.redraw_keyboard)
    def _draw_forbidden_icon(self, canvas: tk.Canvas, cx: float, cy: float, radius: float) -> None:
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#d32f2f", width=2)
        canvas.create_line(cx - radius * 0.65, cy + radius * 0.65, cx + radius * 0.65, cy - radius * 0.65, fill="#d32f2f", width=2)
    def _refresh_sounding_notes(self) -> None:
        if self.current_mode == "detection":
            next_active = set(self._current_detection_notes())
            if self.midi_input_sound_enabled:
                next_sounding = set(next_active)
            else:
                next_sounding = {
                    int(note)
                    for note in next_active
                    if note not in set(self.detection_midi_held_notes)
                }
        else:
            next_active = self.midi_held_notes | self.mouse_held_notes | self.sustain_latched_notes
            if self.midi_input_sound_enabled:
                next_sounding = set(next_active)
            else:
                blocked_midi_notes = set(self.midi_held_notes) | set(self.midi_latched_notes)
                # Keep mouse-triggered notes audible even if MIDI sound is muted.
                next_sounding = {
                    int(note)
                    for note in next_active
                    if (note not in blocked_midi_notes) or (note in self.mouse_held_notes)
                }
        to_start = next_sounding - self.sounding_notes
        to_stop = self.sounding_notes - next_sounding

        for note in to_start:
            self.audio_engine.note_on(note, int(self.note_velocity.get(note, 100)))
        for note in to_stop:
            self.audio_engine.note_off(note)
        self.sounding_notes = next_sounding

        if next_active != self.active_notes:
            self.active_notes = next_active
            self.update_music_views()
    def _note_on_from_source(self, note: int, velocity: int, source: str) -> None:
        velocity = int(max(1, min(127, velocity)))
        self.note_velocity[note] = velocity
        self.sustain_latched_notes.discard(note)
        if source == "midi":
            self.midi_held_notes.add(note)
            self.midi_latched_notes.discard(note)
        else:
            self.mouse_held_notes.add(note)
            self.midi_latched_notes.discard(note)
    def _note_off_from_source(self, note: int, source: str) -> None:
        if source == "midi":
            self.midi_held_notes.discard(note)
        else:
            self.mouse_held_notes.discard(note)

        if self.pedal_active:
            if note not in self.midi_held_notes and note not in self.mouse_held_notes:
                self.sustain_latched_notes.add(note)
                if source == "midi":
                    self.midi_latched_notes.add(note)
        else:
            self.sustain_latched_notes.discard(note)
            self.midi_latched_notes.discard(note)
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
        if self.current_mode == "detection":
            self.detection_midi_held_notes.clear()
            if self.detection_shift_pressed:
                if note in self.detection_mouse_chord_notes:
                    self.detection_mouse_chord_notes.discard(note)
                else:
                    self.detection_mouse_chord_notes.add(note)
            else:
                self.detection_mouse_chord_notes = {int(note)}
            self.mouse_current_note = note
            self._refresh_sounding_notes()
            return
        if self.generation_tab_active:
            if self.instrument_view == "piano":
                # Permitir teclas mano derecha (preview) y mano izquierda (una octava abajo, clave de fa).
                allowed_piano = set(self.generated_preview_notes)
                allowed_piano |= {int(n - 12) for n in self.generated_preview_notes if int(n - 12) >= 0}
                if note in allowed_piano:
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
            self.scale_input_raw_note = int(note)
            self.staff_pressed_scale_notes.clear()
            staff_note = self._scale_staff_note_for_pitch(note)
            if staff_note is not None:
                self.staff_pressed_scale_notes.add(staff_note)
            self._refresh_sounding_notes()
            self.redraw_staff()
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
        if self.current_mode == "detection":
            if note is None:
                return
            if note == self.mouse_current_note:
                return
            self.detection_midi_held_notes.clear()
            if self.detection_shift_pressed:
                if note in self.detection_mouse_chord_notes:
                    self.detection_mouse_chord_notes.discard(note)
                else:
                    self.detection_mouse_chord_notes.add(note)
            else:
                self.detection_mouse_chord_notes = {int(note)}
            self.mouse_current_note = note
            self._refresh_sounding_notes()
            return
        if self.generation_tab_active:
            if self.instrument_view == "piano":
                allowed_piano = set(self.generated_preview_notes)
                allowed_piano |= {int(n - 12) for n in self.generated_preview_notes if int(n - 12) >= 0}
                if note is not None and note in allowed_piano:
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
            self.scale_input_raw_note = None
            if note is not None:
                self.mouse_current_note = note
                self._note_on_from_source(note, velocity=100, source="mouse")
                self.scale_input_raw_note = int(note)
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
        if self.current_mode == "detection":
            self.mouse_current_note = None
            return
        if self.mouse_current_note is not None:
            self._note_off_from_source(self.mouse_current_note, source="mouse")
            self.mouse_current_note = None
            if self.scale_tab_active and self.scale_play_mode == "piano":
                self.staff_pressed_scale_notes.clear()
                self.scale_input_raw_note = None
                self.redraw_staff()
            self._refresh_sounding_notes()
    def _on_shift_press(self, _event: tk.Event) -> None:
        self.detection_shift_pressed = True
        self.pedal_active = True
    def _on_shift_release(self, _event: tk.Event) -> None:
        self.detection_shift_pressed = False
        self.pedal_active = False
        if self.current_mode != "detection":
            self.sustain_latched_notes.clear()
            self.midi_latched_notes.clear()
            self._refresh_sounding_notes()
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

            if self.current_mode == "detection":
                if message.type == "note_on" and message.velocity > 0:
                    if not self.detection_midi_held_notes and self.detection_mouse_chord_notes:
                        self.detection_mouse_chord_notes.clear()
                    self.detection_midi_held_notes.add(int(message.note))
                    changed = True
                elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                    self.detection_midi_held_notes.discard(int(message.note))
                    changed = True
            elif message.type == "note_on" and message.velocity > 0:
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
    def note_name(
        self,
        midi_note: int,
        with_octave: bool = True,
        include_flat_alias: bool = False,
        prefer_flat: Optional[bool] = None,
    ) -> str:
        language = self.config_data.get("language", "es")
        base_names = NOTE_NAMES.get(language, NOTE_NAMES["en"])
        pc = midi_note % 12
        sharp_name = base_names[pc]
        if language == "es":
            flat_aliases = {
                1: "Re♭",
                3: "Mi♭",
                6: "Sol♭",
                8: "La♭",
                10: "Si♭",
            }
        else:
            flat_aliases = {
                1: "D♭",
                3: "E♭",
                6: "G♭",
                8: "A♭",
                10: "B♭",
            }
        if prefer_flat is None:
            in_note_modes = self.current_mode in {"detection", "generation", "scales"}
            prefer_flat = in_note_modes and str(self.config_data.get("note_accidental", "sharp")) == "flat"
        flat_name = flat_aliases.get(pc)
        name = flat_name if (prefer_flat and flat_name is not None) else sharp_name
        if include_flat_alias and not with_octave:
            if flat_name is not None:
                if prefer_flat:
                    return f"{flat_name} / {sharp_name}"
                return f"{sharp_name} / {flat_name}"
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
    def _detect_chord_with_extras(self, notes: set[int]) -> tuple[str, set[int]]:
        chord, extras, _map_oct, _map_no_oct = self._detect_harmonic_spelling(set(notes))
        return chord, extras
    def detect_chord(self, notes: Optional[set[int]] = None) -> str:
        chord_notes = set(notes if notes is not None else self._current_detection_notes())
        chord, _extras = self._detect_chord_with_extras(chord_notes)
        return chord
    def update_music_views(self) -> None:
        self._refresh_scale_preview()
        self._refresh_guitar_variations()
        if hasattr(self, "_refresh_detection_controls_state"):
            self._refresh_detection_controls_state()
        active_set = self._current_detection_notes()
        generated_set = set(self.generated_preview_notes)
        detected_chord_name, detected_extras, detected_map_oct, detected_map_no_oct = self._detect_harmonic_spelling(active_set)
        self.detection_overlay_note_names = dict(detected_map_no_oct)
        self.detection_extra_notes = set(detected_extras)

        if active_set:
            active_ordered = sorted(active_set)
            self.notes_var.set(" - ".join(detected_map_oct.get(int(note), self.note_name(note)) for note in active_ordered))
        else:
            self.detection_overlay_note_names = {}
            self.notes_var.set("-")
        if self.detection_extra_notes:
            extra_ordered = sorted(self.detection_extra_notes)
            self.extra_notes_var.set(" - ".join(detected_map_oct.get(int(note), self.note_name(note)) for note in extra_ordered))
        else:
            self.extra_notes_var.set("")
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
            scale_name = getattr(self, "scale_name_var", None)
            if scale_name is not None:
                self.chord_var.set(scale_name.get())
            else:
                self.chord_var.set("-")
        elif self.metronome_tab_active:
            self.chord_var.set("-")
        elif self.tuner_tab_active:
            self.chord_var.set(self.tuner_status_var.get())
        else:
            self.chord_var.set(detected_chord_name)
        if self.tuner_tab_active:
            self._refresh_tuner_ui()
        self.redraw_keyboard()
        self.redraw_staff()
