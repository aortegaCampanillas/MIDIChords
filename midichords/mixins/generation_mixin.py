from __future__ import annotations

from typing import Optional

import midichords.qt.tk_compat as tk
from midichords.core.music_theory import CHORD_PATTERNS, ChordPattern, chord_patterns_for_ui
from midichords.ui.widgets_qt import GrayRoundedButton


class GenerationMixin:
    @staticmethod
    def _voiced_intervals_for_inversion(intervals: list[int], inversion: int) -> list[int]:
        if not intervals:
            return []
        total = len(intervals)
        inversion_idx = max(0, min(int(inversion), total - 1))
        rotated = [int(intervals[(inversion_idx + i) % total]) for i in range(total)]
        voiced: list[int] = []
        for raw in rotated:
            value = int(raw)
            if voiced:
                while value <= voiced[-1]:
                    value += 12
            voiced.append(value)
        return voiced

    @staticmethod
    def _generation_interval_degree(interval: int, suffix: str) -> int:
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

    def _spelled_generation_note_names(
        self,
        root_midi: int,
        voiced_intervals: list[int],
        suffix: str,
        with_octave: bool = True,
    ) -> list[str]:
        language = str(self.config_data.get("language", "es"))
        letter_names = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] if language == "es" else ["C", "D", "E", "F", "G", "A", "B"]
        base_pcs = [0, 2, 4, 5, 7, 9, 11]
        prefer_flats = self.note_accidental == "flat"
        tonic_letter = self._tonic_letter_index(self.generation_root_pc, prefer_flats)

        names: list[str] = []
        for interval in voiced_intervals:
            midi_note = int(root_midi + int(interval))
            target_pc = midi_note % 12
            degree = self._generation_interval_degree(int(interval), str(suffix))
            letter_idx = (tonic_letter + degree) % 7
            base_pc = base_pcs[letter_idx]
            diff = (target_pc - base_pc) % 12
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
                names.append(self.note_name(midi_note, with_octave=with_octave))
                continue
            name = f"{letter_names[letter_idx]}{accidental}"
            if with_octave:
                octave = midi_note // 12 - 1
                name = f"{name}{octave}"
            names.append(name)
        return names

    def _generation_note_name_map(self, with_octave: bool = False) -> dict[int, str]:
        pattern = self._resolve_generation_pattern()
        intervals = list(pattern.intervals)
        if not intervals:
            return {}
        max_inversion = len(intervals) - 1
        inversion = min(max(0, self.generation_inversion), max_inversion)
        voiced_intervals = self._voiced_intervals_for_inversion(intervals, inversion)
        root_midi = 60 + self.generation_root_pc
        voiced_notes = [root_midi + interval for interval in voiced_intervals]
        labels = self._spelled_generation_note_names(
            root_midi=root_midi,
            voiced_intervals=voiced_intervals,
            suffix=str(pattern.suffix),
            with_octave=with_octave,
        )
        return {int(note): str(label) for note, label in zip(voiced_notes, labels)}

    def _refresh_generation_controls(self) -> None:
        if self.generation_pattern_suffix not in {p.suffix for p in CHORD_PATTERNS}:
            self.generation_pattern_suffix = ""
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
    def _refresh_generation_selection_buttons(self) -> None:
        # Legacy button-based UI (kept for backward compatibility).
        if hasattr(self, "generation_root_btn"):
            self.generation_root_btn.set_text(self.note_name(self.generation_root_pc, with_octave=False))
        variant_label = self.generation_pattern_suffix if self.generation_pattern_suffix else "maj"
        if hasattr(self, "generation_variant_btn"):
            self.generation_variant_btn.set_text(variant_label)
        if hasattr(self, "generation_inversion_btn"):
            self.generation_inversion_btn.set_text(self._inversion_label(self.generation_inversion))

        # Combo-based UI.
        if hasattr(self, "generation_root_combo") and hasattr(self, "generation_root_var"):
            root_options = [(self.note_name(pc, with_octave=False), int(pc)) for pc in range(12)]
            self._generation_root_label_to_pc = {label: pc for label, pc in root_options}
            self.generation_root_combo.configure(values=[label for label, _ in root_options])
            self.generation_root_var.set(self.note_name(self.generation_root_pc, with_octave=False))

        if hasattr(self, "generation_variant_combo") and hasattr(self, "generation_variant_var"):
            variant_options: list[tuple[str, str]] = []
            seen: set[str] = set()
            for pattern in chord_patterns_for_ui():
                label = pattern.suffix if pattern.suffix else "maj"
                if label in seen:
                    continue
                seen.add(label)
                variant_options.append((label, str(pattern.suffix)))
            self._generation_variant_label_to_suffix = {label: suffix for label, suffix in variant_options}
            self.generation_variant_combo.configure(values=[label for label, _ in variant_options])
            self.generation_variant_var.set(variant_label)

        if hasattr(self, "generation_inversion_combo") and hasattr(self, "generation_inversion_var"):
            inversion_options = [(self._inversion_label(inv), inv) for inv in range(self._max_generation_inversion() + 1)]
            self._generation_inversion_label_to_value = {label: inv for label, inv in inversion_options}
            self.generation_inversion_combo.configure(values=[label for label, _ in inversion_options])
            self.generation_inversion_var.set(self._inversion_label(self.generation_inversion))
        self._refresh_generation_inversion_control_state()
    def _refresh_generation_inversion_control_state(self) -> None:
        inversion_enabled = self.instrument_view != "guitar"
        if hasattr(self, "generation_inversion_btn"):
            self.generation_inversion_btn.set_enabled(inversion_enabled)
        if hasattr(self, "generation_inversion_combo"):
            self.generation_inversion_combo.configure(state=("readonly" if inversion_enabled else "disabled"))
        if hasattr(self, "generation_inversion_label"):
            muted = getattr(self, "color_muted", "#5a6370")
            text_color = getattr(self, "color_text", "#e9edf2")
            self.generation_inversion_label.configure(fg=(text_color if inversion_enabled else muted))

    def _on_generation_root_combo_changed(self, _event: tk.Event) -> None:
        label = str(self.generation_root_var.get()).strip()
        pc = getattr(self, "_generation_root_label_to_pc", {}).get(label)
        if pc is None:
            return
        self._on_generation_root_clicked(int(pc))

    def _on_generation_variant_combo_changed(self, _event: tk.Event) -> None:
        label = str(self.generation_variant_var.get()).strip()
        suffix = getattr(self, "_generation_variant_label_to_suffix", {}).get(label)
        if suffix is None:
            return
        self._on_generation_variant_clicked(str(suffix))

    def _on_generation_inversion_combo_changed(self, _event: tk.Event) -> None:
        label = str(self.generation_inversion_var.get()).strip()
        inversion = getattr(self, "_generation_inversion_label_to_value", {}).get(label)
        if inversion is None:
            return
        self._on_generation_inversion_clicked(int(inversion))
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
        if int(pc) == int(self.generation_root_pc):
            return
        self.generation_root_pc = int(pc)
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
        self._preview_generated_chord_short()
    def _on_generation_variant_clicked(self, suffix: str) -> None:
        if str(suffix) == str(self.generation_pattern_suffix):
            return
        self.generation_pattern_suffix = str(suffix)
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
        self._preview_generated_chord_short()
    def _on_generation_inversion_clicked(self, inversion: int) -> None:
        if int(inversion) == int(self.generation_inversion):
            return
        self.generation_inversion = int(inversion)
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
        self._preview_generated_chord_short()
    def _close_generation_selection_overlay(self) -> None:
        if self.generation_selection_overlay is not None:
            self.generation_selection_overlay.destroy()
            self.generation_selection_overlay = None
    def _open_generation_selection_overlay(self, kind: str) -> None:
        if self.generation_selection_overlay is not None:
            self._close_generation_selection_overlay()

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.generation_selection_overlay = overlay

        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        if kind == "root":
            title = self.tr("label_root_note")
        elif kind == "variant":
            title = self.tr("label_variant")
        else:
            title = self.tr("label_inversion")
        tk.Label(
            header,
            text=title,
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)

        if kind == "root":
            buttons_frame = self._build_scrollable_area(overlay, bg="#2a2f36", padx=8, pady=(2, 10))
            columns = 3
            options: list[tuple[str, int, bool]] = []
            for pc in range(12):
                options.append(
                    (
                        self.note_name(pc, with_octave=False),
                        pc,
                        pc == self.generation_root_pc,
                    )
                )
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            for idx, (label, value, selected) in enumerate(options):
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=str(label),
                    command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                    font_family=self.ui_font_family,
                    width=122,
                    height=74,
                    radius=28,
                    font_size=22,
                    selected_text_color="#000000",
                )
                btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                btn.set_selected(bool(selected))
            return

        if kind == "variant":
            body = tk.Frame(overlay, bg="#2a2f36")
            body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))
            search_var, entry = self._build_rounded_search_entry(body, self.tr("label_search_variant"))

            buttons_frame = self._build_scrollable_area(body, bg="#2a2f36", padx=0, pady=(0, 0))
            columns = 3
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            def render_buttons() -> None:
                for w in buttons_frame.winfo_children():
                    w.destroy()
                term = search_var.get().strip().lower()
                options: list[tuple[str, str, bool]] = []
                for pattern in chord_patterns_for_ui():
                    label = pattern.suffix if pattern.suffix else "maj"
                    if term and term not in label.lower():
                        continue
                    options.append((label, pattern.suffix, pattern.suffix == self.generation_pattern_suffix))
                for idx, (label, value, selected) in enumerate(options):
                    btn = GrayRoundedButton(
                        buttons_frame,
                        text=str(label),
                        command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                        font_family=self.ui_font_family,
                        width=160,
                        height=64,
                        radius=24,
                        font_size=16,
                        selected_text_color="#000000",
                    )
                    btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                    btn.set_selected(bool(selected))

            search_var.trace_add("write", lambda *_args: render_buttons())
            render_buttons()
            entry.focus_set()
            return

        # inversion
        buttons_frame = self._build_scrollable_area(overlay, bg="#2a2f36", padx=8, pady=(2, 10))
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
                    font_family=self.ui_font_family,
                    width=160,
                    height=64,
                    radius=24,
                    font_size=16,
                    selected_text_color="#000000",
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
        if self.instrument_view == "guitar":
            return
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

    def _generation_piano_staff_midi_notes(self) -> set[int]:
        """Notas MIDI que el pentagrama muestra en piano: clave de sol + fa (una octava abajo).

        Debe coincidir con `display_notes` en `redraw_staff` (generación y círculo de quintas).
        En guitarra solo la vista previa del acorde (sin duplicar octava).
        """
        rh = set(self.generated_preview_notes)
        if self.instrument_view != "piano":
            return rh
        return rh | {int(n - 12) for n in rh if int(n - 12) >= 0}
    def _update_generation_preview(self) -> None:
        # No usar `generated_playing_notes` aquí: incluye notas sueltas (MIDI/clic) y al
        # recalcular la vista previa no deben borrarse (p. ej. Qt puede refrescar combos
        # y disparar esta función mientras el usuario mantiene teclas MIDI).
        was_holding_generated_chord = self.generation_play_button_pressed or self.generation_play_space_pressed
        if was_holding_generated_chord:
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

        voiced_intervals = self._voiced_intervals_for_inversion(intervals, inversion)
        voiced_notes = [root_midi + interval for interval in voiced_intervals]
        self.generated_preview_notes = set(voiced_notes)
        spelled_map = self._generation_note_name_map(with_octave=False)
        spelled_map_oct = self._generation_note_name_map(with_octave=True)

        shown_suffix = pattern.suffix if pattern.suffix else ""
        chord_name = f"{self.note_name(self.generation_root_pc, with_octave=False)}{shown_suffix}"
        if inversion > 0 and voiced_notes:
            bass_name = spelled_map.get(int(voiced_notes[0]), self.note_name(voiced_notes[0], with_octave=False))
            chord_name = f"{chord_name}/{bass_name}"
        self.generated_chord_var.set(chord_name)
        if self.generated_preview_notes:
            ordered = sorted(self.generated_preview_notes)
            self.generated_notes_var.set(" - ".join(spelled_map_oct.get(int(note), self.note_name(note)) for note in ordered))
        else:
            self.generated_notes_var.set("-")

        if was_holding_generated_chord and (
            self.generation_play_button_pressed or self.generation_play_space_pressed
        ):
            self._play_generated_chord()

        if self.generation_tab_active:
            self.update_music_views()
        if getattr(self, "circle_fifths_tab_active", False):
            self._circle_schedule_redraw()
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
    def _preview_generated_chord_short(self) -> None:
        """Reproduce brevemente el acorde actual al cambiar tónica/variante (generación o círculo)."""
        if not (self.generation_tab_active or getattr(self, "circle_fifths_tab_active", False)):
            return
        if not self.generated_preview_notes:
            return
        pid = getattr(self, "_preview_chord_after_id", None)
        if pid is not None:
            try:
                self.after_cancel(pid)
            except Exception:
                pass
            setattr(self, "_preview_chord_after_id", None)
        self._stop_generated_playback()
        notes = sorted(self._generation_piano_staff_midi_notes())
        if self.instrument_view == "guitar":
            for note in notes:
                self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.3)
            if self.generation_tab_active or getattr(self, "circle_fifths_tab_active", False):
                self.redraw_guitar_fretboard()
                self.redraw_staff()
            return
        # Identifica esta ronda de forma explícita en vez de confiar solo en
        # after_cancel: si dos acordes se disparan muy seguidos (p. ej. clics
        # rápidos en el círculo de quintas), un after_cancel que no surta
        # efecto a tiempo podía dejar el timer viejo ejecutándose sobre notas
        # ya reemplazadas, y las notas del acorde anterior se quedaban
        # sonando indefinidamente (acumulación de voces activas sin apagar).
        preview_token = getattr(self, "_preview_chord_token", 0) + 1
        self._preview_chord_token = preview_token
        for note in notes:
            self.play_note(note, 108)
            self.generated_playing_notes.add(note)
        if self.generation_tab_active or getattr(self, "circle_fifths_tab_active", False):
            self.redraw_keyboard()
            self.redraw_staff()

        is_circle = getattr(self, "circle_fifths_tab_active", False)

        def _release_preview() -> None:
            setattr(self, "_preview_chord_after_id", None)
            if getattr(self, "_preview_chord_token", None) != preview_token:
                return
            for note in list(notes):
                if note in self.generated_playing_notes:
                    # En el círculo de quintas el preview es un sonido corto,
                    # no una nota sostenida real: un release rápido evita que
                    # cambiar de acorde repetidamente acumule voces con la
                    # cola larga normal del piano (se oía como ruido/crackle).
                    self.stop_note(note, fast=is_circle)
                    self.generated_playing_notes.discard(note)
            if self.generation_tab_active or getattr(self, "circle_fifths_tab_active", False):
                self.redraw_keyboard()
                self.redraw_staff()

        setattr(self, "_preview_chord_after_id", self.after(1500, _release_preview))

    def _stop_generated_playback(self) -> None:
        self.generation_guitar_drag_active = False
        self.generation_staff_drag_active = False
        self.generation_piano_staff_drag_active = False
        self.generation_drag_notes.clear()
        self.generation_drag_moved = False
        pid = getattr(self, "_preview_chord_after_id", None)
        if pid is not None:
            try:
                self.after_cancel(pid)
            except Exception:
                pass
            setattr(self, "_preview_chord_after_id", None)
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
        is_circle = getattr(self, "circle_fifths_tab_active", False)
        for note in list(self.generated_playing_notes):
            self.stop_note(note, fast=is_circle)
        self.generated_playing_notes.clear()
        if self.generation_tab_active or getattr(self, "circle_fifths_tab_active", False):
            self.redraw_keyboard()
            self.redraw_guitar_fretboard()
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
            self.stop_note(note)
        if self.generation_tab_active:
            self.redraw_keyboard()
            self.redraw_guitar_fretboard()
            self.redraw_staff()
    def _trigger_generated_single_note(
        self,
        note: int,
        *,
        auto_clear_ms: Optional[int] = 520,
        additive: bool = False,
        source: str = "mouse",
    ) -> None:
        """Dispara una nota suelta en modo generación.

        `auto_clear_ms`: si es un entero > 0, quita resaltado y corta audio de piano tras ese tiempo
        (clic ratón / pentagrama). Si es `None`, el resaltado y el sostenido siguen hasta `note_off`
        (p. ej. tecla MIDI mantenida).

        `additive`: si es True, no vacía las demás notas en resaltado/audio (varias teclas MIDI a la vez).
        Los clics de ratón/pentagrama usan False para sustituir la nota previa.

        `source`: "mouse" o "midi". Con salida MIDI activa, las notas que llegan de un
        teclado MIDI físico no deben sonar localmente (el propio teclado ya las reproduce).
        """
        if self.generation_tab_active and self.instrument_view == "guitar" and self.guitar_selected_variation_notes:
            allowed_notes = set(self.guitar_selected_variation_notes)
        else:
            allowed_notes = set(self.generated_preview_notes)
            if self.generation_tab_active:
                # Permitir notas mano izquierda (clave de fa): una octava abajo.
                allowed_notes |= {int(n - 12) for n in set(self.generated_preview_notes) if int(n - 12) >= 0}
        if note not in allowed_notes:
            return
        if additive:
            if note in self.generated_playing_notes:
                return
        else:
            for after_id in list(self.generated_note_highlight_after.values()):
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
            self.generated_note_highlight_after.clear()
            for n in list(self.generated_playing_notes):
                if self.instrument_view != "guitar":
                    self.stop_note(n)
            self.generated_playing_notes.clear()
        self.generated_playing_notes.add(note)
        play_locally = source != "midi" or self._should_play_midi_input_locally()
        if self.instrument_view == "guitar":
            if play_locally:
                self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.1)
            stop_audio = False
        else:
            if play_locally:
                self.play_note(note, 108)
            stop_audio = True
        if auto_clear_ms is not None and int(auto_clear_ms) > 0:
            self.generated_note_highlight_after[note] = self.after(
                int(auto_clear_ms),
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
        notes = sorted(self._generation_piano_staff_midi_notes())
        if self.instrument_view == "guitar":
            for note in notes:
                self.audio_engine.pluck_guitar_note(note, velocity=108, duration_seconds=1.3)
        else:
            for note in notes:
                self.play_note(note, 108)
                self.generated_playing_notes.add(note)
        if self.generation_tab_active:
            self.redraw_keyboard()
            self.redraw_staff()
    def _start_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = True
        else:
            self.generation_play_space_pressed = True
        self.generation_play_btn.set_playing(True)
        cp = getattr(self, "circle_play_btn", None)
        if cp is not None:
            cp.set_playing(True)
        self._play_generated_chord()
    def _stop_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = False
        else:
            self.generation_play_space_pressed = False
        if self.generation_play_button_pressed or self.generation_play_space_pressed:
            return
        self.generation_play_btn.set_playing(False)
        cp = getattr(self, "circle_play_btn", None)
        if cp is not None:
            cp.set_playing(False)
        self._stop_generated_playback()
    def _on_generation_play_press(self, _event: tk.Event) -> str:
        self._start_generated_hold(source="button")
        return "break"
