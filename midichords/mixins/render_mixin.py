from __future__ import annotations

import textwrap
import time
from typing import Optional
import midichords.qt.tk_compat as tk
import midichords.qt.tkfont_compat as tkfont
from midichords.core.music_service import _chord_symbol_prefer_flat
from midichords.core.music_theory import WHITE_PCS, ROOT_LETTER_PCS
from midichords.core.tomplay_fingerings import get_fingering_for_scale


class RenderMixin:
    @staticmethod
    def _parallel_beam_endpoint(
        start_x: float,
        start_y: float,
        end_x: float,
        beam_start_x: float,
        beam_start_y: float,
        beam_end_x: float,
        beam_end_y: float,
    ) -> tuple[float, float]:
        """Return an endpoint whose segment follows the primary beam slope."""
        beam_dx = beam_end_x - beam_start_x
        slope = (beam_end_y - beam_start_y) / beam_dx if beam_dx else 0.0
        return end_x, start_y + slope * (end_x - start_x)

    @staticmethod
    def _staff_clef_sizes_px(line_space: int) -> tuple[int, int]:
        """Tamaño de clave de sol / fa alineado con la web (gap≈17 → 𝄞 82px, 𝄢 72px)."""
        ls = float(line_space)
        treble = int(round(ls * (82.0 / 17.0)))
        bass = int(round(ls * (72.0 / 17.0)))
        return (max(52, min(100, treble)), max(46, min(90, bass)))

    @staticmethod
    def _staff_accidental_font_pt(line_space: int, *, prefer_flat: bool) -> int:
        """Tamaño #/♭ en pentagrama; proporción como la web (24px con gap≈17)."""
        ls = float(line_space)
        px = int(round(ls * (24.0 / 17.0)))
        if prefer_flat:
            px = int(round(px * 1.06))
        else:
            px = int(round(px * 0.98))
        return max(17, min(34, px))

    @staticmethod
    def _staff_natural_font_pt(line_space: int) -> int:
        """Tamaño del becuadro (♮), ligeramente menor que #/♭."""
        px = int(round(float(line_space) * (22.0 / 17.0)))
        return max(16, min(32, px))

    @staticmethod
    def _staff_key_sig_step_x(line_space: int, accidental_pt: int) -> int:
        """Separación horizontal entre alteraciones de armadura (evita solape al crecer la fuente)."""
        return max(14, min(22, int(round(line_space * 0.82)), int(accidental_pt * 0.72) + 6))

    @staticmethod
    def _key_signature_index_for_scale_note(
        label: str,
        midi_note: int,
        signature_count: int,
        prefer_flats: bool,
    ) -> int:
        """Índice de la alteración de armadura correspondiente a una nota escrita."""
        if signature_count <= 0:
            return -1
        text = str(label)
        accidental_count = text.count("♭") if prefer_flats else (text.count("#") + text.count("♯"))
        if accidental_count != 1:
            return -1
        pc = int(midi_note) % 12
        natural_pc = (pc + 1) % 12 if prefer_flats else (pc - 1) % 12
        order = [11, 4, 9, 2, 7, 0, 5] if prefer_flats else [5, 0, 7, 2, 9, 4, 11]
        try:
            index = order.index(natural_pc)
        except ValueError:
            return -1
        return index if index < int(signature_count) else -1

    @staticmethod
    def _key_signature_index_for_midi(
        midi_note: int,
        signature_count: int,
        prefer_flats: bool,
    ) -> int:
        """Índice de la alteración de armadura que representa el pitch pulsado."""
        if signature_count <= 0:
            return -1
        pitch_class = int(midi_note) % 12
        order = [10, 3, 8, 1, 6, 11, 4] if prefer_flats else [6, 1, 8, 3, 10, 5, 0]
        try:
            index = order.index(pitch_class)
        except ValueError:
            return -1
        return index if index < int(signature_count) else -1

    @staticmethod
    def _draw_rest_symbol(canvas: object, x: float, center_y: float, dur_code: str,
                          line_space: float, fill: str, treble_top: float) -> None:
        """Draw a rest symbol using canvas primitives (Unicode glyphs are not reliable across fonts)."""
        col = fill
        if dur_code == "w":
            rw, rh = line_space * 1.3, line_space * 0.48
            ry = treble_top + line_space
            canvas.create_rectangle(x - rw / 2, ry, x + rw / 2, ry + rh, fill=col, outline="")
        elif dur_code == "h":
            rw, rh = line_space * 1.3, line_space * 0.48
            ry = treble_top + 2 * line_space
            canvas.create_rectangle(x - rw / 2, ry - rh, x + rw / 2, ry, fill=col, outline="")
        elif dur_code == "q":
            r = line_space * 0.35
            y0 = center_y - line_space * 0.75
            canvas.create_line(x + r, y0,
                                x - r * 0.4, y0 + line_space * 0.5,
                                fill=col, width=1.5)
            canvas.create_line(x - r * 0.4, y0 + line_space * 0.5,
                                x + r * 0.8, y0 + line_space * 0.9,
                                fill=col, width=1.5)
            canvas.create_line(x + r * 0.8, y0 + line_space * 0.9,
                                x, y0 + line_space * 1.25,
                                x - r * 0.5, y0 + line_space * 1.55,
                                fill=col, width=1.5)
        elif dur_code in ("e", "et"):
            # Eighth rest: tall diagonal line (upper-right → lower-left) + large filled circle
            dr = max(4.5, line_space * 0.46)
            span = line_space * 2.6
            x_top = x + line_space * 0.32
            y_top = center_y - span * 0.52
            x_bot = x - line_space * 0.22
            y_bot = center_y + span * 0.48
            canvas.create_line(x_top, y_top, x_bot, y_bot, fill=col, width=2.5)
            # Circle at ~25% from top of line, shifted left so line passes right side
            t = 0.24
            xc = x_top + (x_bot - x_top) * t - dr * 0.65
            yc = y_top + (y_bot - y_top) * t
            canvas.create_oval(xc - dr, yc - dr, xc + dr, yc + dr, fill=col, outline="")
        elif dur_code == "s":
            # Sixteenth rest: taller diagonal + two blobs
            dr = max(3.5, line_space * 0.38)
            span = line_space * 3.2
            x_top = x + line_space * 0.32
            y_top = center_y - span * 0.52
            x_bot = x - line_space * 0.22
            y_bot = center_y + span * 0.48
            canvas.create_line(x_top, y_top, x_bot, y_bot, fill=col, width=2.5)
            # Top blob (~20% from top)
            t0 = 0.18
            xc0 = x_top + (x_bot - x_top) * t0 - dr * 0.65
            yc0 = y_top + (y_bot - y_top) * t0
            canvas.create_oval(xc0 - dr, yc0 - dr, xc0 + dr, yc0 + dr, fill=col, outline="")
            # Second blob (~45% from top)
            t1 = 0.44
            xc1 = x_top + (x_bot - x_top) * t1 - dr * 0.65
            yc1 = y_top + (y_bot - y_top) * t1
            canvas.create_oval(xc1 - dr, yc1 - dr, xc1 + dr, yc1 + dr, fill=col, outline="")

    def _scaled_clef_pixmap(self, pm: object | None, target_h: int, cache_slot: str) -> object | None:
        """Escala PNG de clave al alto del pentagrama; cache por slot para no recalcular cada frame."""
        if pm is None:
            return None
        is_null = getattr(pm, "isNull", None)
        if callable(is_null) and is_null():
            return None
        h0 = int(getattr(pm, "height", lambda: 0)())
        if h0 <= 0:
            return pm
        attr = f"_clef_scaled_cache_{cache_slot}"
        prev = getattr(self, attr, None)
        if prev and prev[0] == target_h and prev[1] is pm:
            return prev[2]
        try:
            from PySide6.QtCore import Qt
        except ImportError:
            return pm
        w0 = int(pm.width())
        new_h = int(target_h)
        new_w = max(1, int(round(w0 * (new_h / float(h0)))))
        scaled = pm.scaled(
            new_w,
            new_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        setattr(self, attr, (target_h, pm, scaled))
        return scaled

    @staticmethod
    def _is_minor_suffix(suffix: str) -> bool:
        return suffix.startswith("m") and not suffix.startswith("maj")

    @staticmethod
    def _scale_prefers_minor_signature(scale_name: str) -> bool:
        if "Minor" in scale_name:
            return True
        return scale_name in {
            "Aeolian",
            "Dorian",
            "Phrygian",
            "Locrian",
            "Super Locrian",
            "Half Diminished",
            "Minor Pentatonic",
            "Minor Blues",
        }

    # Semitonos que hay que SUMAR a la tónica del modo para llegar a su
    # mayor relativo real (el que comparte exactamente las mismas notas
    # naturales/alteradas). Verificado nota a nota: Do Dórico = Sib Mayor
    # (+10), Do Frigio = Lab Mayor (+8), Do Locrio = Reb Mayor (+1), Do
    # Eolio = Mib Mayor (+3, ya era el comportamiento previo/correcto para
    # el modo "menor natural"), Fa Lidio = Do Mayor (+7), Sol Mixolidio =
    # Do Mayor (+5). Ionian/Mayor no necesita entrada (offset 0 = su propia
    # armadura). Sin esto, cada modo "no jónico" heredaba o bien la
    # armadura del menor natural (los de sabor menor) o la de su propia
    # tónica como si fuera Mayor normal (los de sabor mayor: Lidio,
    # Mixolidio), ambas incorrectas salvo casualidad.
    _MODE_RELATIVE_MAJOR_OFFSET = {
        "Dorian": 10,
        "Phrygian": 8,
        "Locrian": 1,
        "Aeolian": 3,
        "Lydian": 7,
        "Mixolydian": 5,
        "Minor": 3,
        "Natural Minor": 3,
        "Minor Pentatonic": 3,
        "Minor Blues": 3,
    }

    @staticmethod
    def _key_signature_count_for_tonic(
        tonic_pc: int,
        is_minor: bool,
        *,
        tie_prefer_flats: bool | None = None,
    ) -> tuple[int, bool]:
        # Returns (count, prefer_flats): menos accidentales gana; en empate (p. ej. Gb/F# mayor),
        # tie_prefer_flats: generación/escalas según #/♭ del usuario; detección usa _chord_symbol_prefer_flat
        # (paridad con el nombre del acorde). None → empate a sostenidos si no se pasa otro criterio.
        tonic_pc = int(tonic_pc) % 12
        if is_minor:
            sharp_map = {4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7}
            flat_map = {2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6}
        else:
            sharp_map = {7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7}
            flat_map = {5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6}
        sharp_count = sharp_map.get(tonic_pc)
        flat_count = flat_map.get(tonic_pc)
        if sharp_count is None and flat_count is None:
            return 0, False
        if sharp_count is None:
            return int(flat_count), True
        if flat_count is None:
            return int(sharp_count), False
        if flat_count < sharp_count:
            return int(flat_count), True
        if sharp_count < flat_count:
            return int(sharp_count), False
        if tie_prefer_flats is True:
            return int(flat_count), True
        return int(sharp_count), False

    @staticmethod
    def _tonic_letter_index(tonic_pc: int, prefer_flats: bool, tonic_letter_pc: Optional[int] = None) -> int:
        tonic_pc = int(tonic_pc) % 12
        if tonic_letter_pc is not None:
            try:
                return ROOT_LETTER_PCS.index(int(tonic_letter_pc) % 12)
            except ValueError:
                pass
        if prefer_flats:
            mapping = {
                0: 0,   # C
                1: 1,   # Db
                2: 1,   # D
                3: 2,   # Eb
                4: 2,   # E
                5: 3,   # F
                6: 4,   # Gb
                7: 4,   # G
                8: 5,   # Ab
                9: 5,   # A
                10: 6,  # Bb
                11: 6,  # B
            }
        else:
            mapping = {
                0: 0,   # C
                1: 0,   # C#
                2: 1,   # D
                3: 1,   # D#
                4: 2,   # E
                5: 3,   # F
                6: 3,   # F#
                7: 4,   # G
                8: 4,   # G#
                9: 5,   # A
                10: 5,  # A#
                11: 6,  # B
            }
        return int(mapping.get(tonic_pc, 0))

    def _staff_signature_context(self, display_notes: set[int]) -> tuple[int, bool]:
        tie_from_ui = str(self.config_data.get("note_accidental", "sharp")) == "flat"
        if self.scale_tab_active:
            pattern = self._resolve_scale_pattern()
            pattern_name = str(pattern.name)
            is_minor = self._scale_prefers_minor_signature(pattern_name)
            offset = self._MODE_RELATIVE_MAJOR_OFFSET.get(pattern_name)
            if offset is not None:
                relative_major_pc = (int(self.scale_tonic_pc) + offset) % 12
                return self._key_signature_count_for_tonic(
                    relative_major_pc, False, tie_prefer_flats=tie_from_ui
                )
            return self._key_signature_count_for_tonic(
                self.scale_tonic_pc, is_minor, tie_prefer_flats=tie_from_ui
            )
        if getattr(self, "circle_fifths_tab_active", False):
            key_tonic = int(self.circle_tonic_pc) % 12
            is_minor_key = str(getattr(self, "circle_key_mode", "major")) == "minor"
            sig = self._key_signature_count_for_tonic(
                key_tonic, is_minor_key, tie_prefer_flats=tie_from_ui
            )
            return sig
        if self.generation_tab_active:
            pattern = self._resolve_generation_pattern()
            is_minor = self._is_minor_suffix(str(pattern.suffix))
            return self._key_signature_count_for_tonic(
                self.generation_root_pc, is_minor, tie_prefer_flats=tie_from_ui
            )
        if getattr(self, "interval_tab_active", False):
            return 0, tie_from_ui
        if self.metronome_tab_active or self.tuner_tab_active or not display_notes:
            return 0, False
        root, pattern, _bass = self._analyze_chord_notes(display_notes)
        if root is None or pattern is None:
            return 0, False
        is_minor = self._is_minor_suffix(str(pattern.suffix))
        tie_pf = bool(_chord_symbol_prefer_flat(int(root), is_minor))
        return self._key_signature_count_for_tonic(
            root, is_minor, tie_prefer_flats=tie_pf
        )

    def _instrument_display_notes(self) -> set[int]:
        if self.tuner_tab_active:
            notes: set[int] = set()
            if self.tuner_detected_note_midi is not None:
                notes.add(int(self.tuner_detected_note_midi))
            if self.tuner_reference_note is not None:
                notes.add(int(self.tuner_reference_note))
            if notes:
                return notes
        if self.generation_tab_active:
            if self.instrument_view == "guitar" and self.guitar_selected_variation_notes:
                return set(self.guitar_selected_variation_notes)
            return set(self.generated_preview_notes)
        if self.scale_tab_active:
            notes = (
                set(self.midi_held_notes)
                | set(self.mouse_held_notes)
                | set(self.sustain_latched_notes)
                | set(self.staff_pressed_scale_notes)
            )
            if self.scale_loop_active and self.scale_current_note is not None:
                notes.add(self.scale_current_note)
            return notes
        if self.metronome_tab_active:
            return set(self.active_notes)
        if getattr(self, "interval_tab_active", False):
            return set(getattr(self, "interval_notes", []))
        return self._current_detection_notes()

    @staticmethod
    def _piano_fingering_for_count(count: int, hand: str) -> list[int]:
        n = max(1, int(count))
        if hand == "right":
            templates = {
                1: [1],
                2: [1, 3],
                3: [1, 3, 5],
                4: [1, 2, 4, 5],
                5: [1, 2, 3, 4, 5],
            }
            if n in templates:
                return templates[n]
            return [min(5, i + 1) for i in range(n)]
        templates = {
            1: [5],
            2: [5, 3],
            3: [5, 3, 1],
            4: [5, 3, 2, 1],
            5: [5, 4, 3, 2, 1],
        }
        if n in templates:
            return templates[n]
        return [max(1, 5 - i) for i in range(n)]

    def _scale_fingering_tomplay(self, scale_type: str, key: int, hand: str, count: int) -> list[int]:
        """Get TomPlay fingering for a scale in a specific key and hand."""
        return get_fingering_for_scale(scale_type, key, hand, count)

    def _scale_note_name_map(self) -> dict[int, str]:
        if not self.scale_preview_notes:
            return {}
        ordered = [int(n) for n in self.scale_preview_notes]
        if not ordered:
            return {}
        labels = self._spelled_scale_note_names(
            root_midi=ordered[0],
            intervals=[int(n - ordered[0]) for n in ordered],
            tonic_pc=self.scale_tonic_pc,
            with_octave=False,
            prefer_flats_override=(self.note_accidental == "flat"),
        )
        name_map: dict[int, str] = {}
        for note, label in zip(ordered, labels):
            pc = int(note) % 12
            if pc not in name_map:
                name_map[pc] = str(label)
        return name_map

    def redraw_guitar_fretboard(self) -> None:
        canvas = self.guitar_canvas
        canvas.delete("all")
        self.scale_guitar_tonic_regions = []
        self.scale_guitar_note_regions = []
        self.guitar_generation_note_regions = []
        # Importante en Qt: si el widget real mide menos, forzar `h`/`w` mayores
        # provoca que el dibujo quede recortado y se pierdan cuerdas/elementos.
        w = max(1, int(canvas.winfo_width()))
        h = max(1, int(canvas.winfo_height()))
        canvas.create_rectangle(0, 0, w, h, fill="#ffffff", outline="")

        frets = 16
        is_left_handed = self.guitar_handedness == "left"
        nut_margin = 58
        board_margin = 12
        if is_left_handed:
            nut_x = w - nut_margin
            board_far_x = board_margin
            direction = -1.0
        else:
            nut_x = nut_margin
            board_far_x = w - board_margin
            direction = 1.0
        step = abs(board_far_x - nut_x) / frets
        open_edge_x = nut_x - direction * (step * 0.5)
        board_x1 = min(nut_x, board_far_x)
        board_x2 = max(nut_x, board_far_x)
        strings_x1 = min(open_edge_x, board_far_x)
        strings_x2 = max(open_edge_x, board_far_x)
        # board_y1=28 keeps fret-number labels (drawn at y=8, ~14px tall) from
        # overlapping the top string's note circles.
        # board_y2 leaves 18px at the bottom so the lowest string's note circle
        # (radius up to 16px) stays fully inside the canvas.
        board_y1 = 28
        board_y2 = max(board_y1 + 10, h - 18)
        canvas.create_rectangle(board_x1, board_y1, board_x2, board_y2, fill="#34363c", outline="#4a4f58", width=1)
        canvas.create_rectangle(min(open_edge_x, nut_x), board_y1, max(open_edge_x, nut_x), board_y2, fill="#ffffff", outline="")
        canvas.create_line(nut_x, board_y1, nut_x, board_y2, fill="#c8b79f", width=3)

        def fret_center_x(fret: int) -> float:
            # Open string marker goes in the half-fret white area before the nut.
            if fret <= 0:
                return (open_edge_x + nut_x) / 2.0
            return nut_x + direction * (fret - 0.5) * step

        for f in range(1, frets + 1):
            x = nut_x + direction * f * step
            canvas.create_line(x, board_y1, x, board_y2, fill="#c8b79f", width=2)
            shadow_x = x + (2 if direction > 0 else -2)
            canvas.create_line(shadow_x, board_y1, shadow_x, board_y2, fill="#8f8576", width=1)

        for n in range(frets):
            label_x = fret_center_x(n)
            canvas.create_text(label_x, 8, text=str(n), fill="#222", font=("Helvetica", 10, "bold"))

        # E B G D A E (de aguda a grave)
        tuning = [64, 59, 55, 50, 45, 40]
        names = ["E", "B", "G", "D", "A", "E"]
        string_gap = (board_y2 - board_y1) / 5.0
        variation = None
        if self.guitar_selected_variation_idx is not None and self.guitar_selected_variation_idx < len(self.guitar_variations):
            variation = self.guitar_variations[self.guitar_selected_variation_idx]
        frets_selected = variation["frets"] if variation is not None else None
        fingers_selected = variation.get("fingers", [0, 0, 0, 0, 0, 0]) if variation is not None else [0, 0, 0, 0, 0, 0]
        root_pc = self.guitar_current_root_pc

        for i, (open_note, name) in enumerate(zip(tuning, names)):
            y = board_y1 + i * string_gap
            canvas.create_line(strings_x1, y, strings_x2, y, fill="#bdbdbd", width=2)
            canvas.create_line(strings_x1, y + 1, strings_x2, y + 1, fill="#8a8a8a", width=1)
            if is_left_handed:
                label_x = min(float(w - 6), float(open_edge_x + 10))
                label_anchor = "w"
            else:
                label_x = max(6.0, float(open_edge_x - 10))
                label_anchor = "e"
            canvas.create_text(
                label_x,
                y,
                text=name,
                fill="#111",
                font=("Helvetica", 10, "bold"),
                anchor=label_anchor,
            )

        if self.scale_tab_active and self.scale_play_mode == "guitar":
            scale_pcs = {n % 12 for n in self.scale_preview_notes}
            if not scale_pcs:
                return
            scale_name_map = self._scale_note_name_map()
            tonic_pc = self.scale_tonic_pc
            current_note = self.scale_current_note if self.scale_loop_active else None
            selected_start = self.scale_guitar_start_note
            note_radius = max(10, min(16, int(string_gap * 0.42)))
            for i, open_note in enumerate(tuning):
                y = board_y1 + i * string_gap
                for fret in range(0, frets):
                    note = open_note + fret
                    if (note % 12) not in scale_pcs:
                        continue
                    cx = fret_center_x(fret)
                    is_tonic = (note % 12) == tonic_pc
                    is_current = current_note is not None and note == current_note
                    is_click_exact = (
                        note in self.scale_guitar_click_highlight_exact_notes
                        or note in self.scale_guitar_drag_exact_notes
                    )
                    is_selected_start = selected_start is not None and note == selected_start and is_tonic
                    if is_current or is_click_exact:
                        fill = "#2fa8ff"
                        outline = "#0f5f99"
                    elif is_selected_start:
                        fill = "#ff9800"
                        outline = "#8a4f10"
                    elif is_tonic:
                        fill = "#f6b60b"
                        outline = "#b38b00"
                    else:
                        fill = "#ffffff"
                        outline = "#2f3137"
                    canvas.create_oval(
                        cx - note_radius,
                        y - note_radius,
                        cx + note_radius,
                        y + note_radius,
                        fill=fill,
                        outline=outline,
                        width=1,
                    )
                    canvas.create_text(
                        cx,
                        y,
                        text=scale_name_map.get(note % 12, self.note_name(note, with_octave=False)),
                        fill="#0f0f0f",
                        font=("Helvetica", 10, "bold"),
                    )
                    self.scale_guitar_note_regions.append(
                        (note, cx - note_radius, y - note_radius, cx + note_radius, y + note_radius)
                    )
                    if is_tonic:
                        self.scale_guitar_tonic_regions.append(
                            (note, cx - note_radius, y - note_radius, cx + note_radius, y + note_radius)
                        )
            now = time.monotonic()
            icon_r = max(7, int(note_radius * 0.65))
            for blocked_note, until in list(self.blocked_note_until.items()):
                if until <= now:
                    continue
                for si, open_note in enumerate(tuning):
                    fret = blocked_note - open_note
                    if 0 <= fret < frets:
                        cx = fret_center_x(fret)
                        sy = board_y1 + si * string_gap
                        self._draw_forbidden_icon(canvas, cx, sy, icon_r)
            return

        if frets_selected is None:
            return

        # Detect barre segments on displayed order (high E -> low E).
        disp_frets = [frets_selected[5 - i] for i in range(6)]
        disp_fingers = [fingers_selected[5 - i] for i in range(6)]
        barre_segments: list[tuple[int, int, int, int, set[int]]] = []  # (fret, finger, start_string, end_string, covered_strings)
        barre_covered: set[int] = set()
        sounded_idxs = [i for i, f in enumerate(disp_frets) if f >= 0]
        min_sounded = min(sounded_idxs) if sounded_idxs else 0
        max_sounded = max(sounded_idxs) if sounded_idxs else 0
        for fret in sorted({f for f in disp_frets if f > 0}):
            idxs = [i for i, f in enumerate(disp_frets) if f == fret and disp_fingers[i] > 0]
            if len(idxs) < 2:
                continue
            # Full barre: same fret on first and last sounding string (e.g., F major at fret 1).
            if idxs[0] == min_sounded and idxs[-1] == max_sounded:
                finger = disp_fingers[idxs[0]]
                covered = set(idxs)
                barre_segments.append((fret, finger, idxs[0], idxs[-1], covered))
                barre_covered.update(covered)
                continue
            run_start = idxs[0]
            run_prev = idxs[0]
            for idx in idxs[1:]:
                if idx == run_prev + 1:
                    run_prev = idx
                else:
                    if run_prev - run_start + 1 >= 2:
                        finger = disp_fingers[run_start]
                        covered = set(range(run_start, run_prev + 1))
                        barre_segments.append((fret, finger, run_start, run_prev, covered))
                        barre_covered.update(covered)
                    run_start = idx
                    run_prev = idx
            if run_prev - run_start + 1 >= 2:
                finger = disp_fingers[run_start]
                covered = set(range(run_start, run_prev + 1))
                barre_segments.append((fret, finger, run_start, run_prev, covered))
                barre_covered.update(covered)

        for fret, finger, start_s, end_s, covered in barre_segments:
            x = fret_center_x(fret)
            y1 = board_y1 + start_s * string_gap
            y2 = board_y1 + end_s * string_gap
            width = max(8, int(string_gap * 0.72))
            canvas.create_line(x, y1, x, y2, fill="#f7b500", width=width, capstyle=tk.ROUND)
            for s in sorted(covered):
                if disp_frets[s] != fret:
                    continue
                y = board_y1 + s * string_gap
                note = tuning[s] + fret
                is_tonic = (root_pc is not None) and ((note % 12) == root_pc)
                is_playing = note in self.generated_playing_notes
                r = max(7, min(12, int(string_gap * 0.30)))
                if is_playing:
                    fill = "#2faeff"
                    text_color = "#ffffff"
                else:
                    fill = "#b35f00" if is_tonic else "#f4a742"
                    text_color = "#ffffff" if is_tonic else "#1f1200"
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="#2e2e2e", width=1)
                canvas.create_text(x, y, text=str(finger), fill=text_color, font=("Helvetica", 9, "bold"))
                self.guitar_generation_note_regions.append((note, x - r, y - r, x + r, y + r))

        # Draw non-barre finger circles.
        for i, open_note in enumerate(tuning):
            y = board_y1 + i * string_gap
            disp_idx = i
            pos_fret = disp_frets[disp_idx]
            if pos_fret is None:
                continue
            if pos_fret < 0:
                canvas.create_text(
                    fret_center_x(0),
                    y,
                    text="X",
                    fill="#9d0d00",
                    font=("Helvetica", 16, "bold"),
                )
                continue
            if disp_idx in barre_covered:
                continue
            finger = disp_fingers[disp_idx]
            note = open_note + pos_fret
            is_tonic = (root_pc is not None) and ((note % 12) == root_pc)
            is_playing = note in self.generated_playing_notes
            cx = fret_center_x(pos_fret)
            r = max(7, min(12, int(string_gap * 0.30)))
            if is_playing:
                fill = "#2faeff"
                text_color = "#ffffff"
            else:
                fill = "#b35f00" if is_tonic else "#f4a742"
                text_color = "#ffffff" if is_tonic else "#1f1200"
            canvas.create_oval(cx - r, y - r, cx + r, y + r, fill=fill, outline="#f1c27d", width=1)
            if pos_fret > 0:
                canvas.create_text(cx, y, text=str(finger if finger > 0 else 1), fill=text_color, font=("Helvetica", 9, "bold"))
            self.guitar_generation_note_regions.append((note, cx - r, y - r, cx + r, y + r))
    def redraw_keyboard(self) -> None:
        if self.scale_tab_active and self.scale_play_mode == "guitar":
            self.redraw_guitar_fretboard()
            return
        if self.generation_tab_active and self.instrument_view == "guitar":
            self.redraw_guitar_fretboard()
            return
        canvas = self.keyboard_canvas
        canvas.delete("all")
        self.white_key_regions = []
        self.black_key_regions = []
        display_active_notes = self._instrument_display_notes()
        if self.generation_tab_active and self.instrument_view == "piano":
            # Keep the generated right-hand chord visible while any key is pressed.
            display_active_notes = set(self.generated_preview_notes) | set(self.generated_playing_notes)
        generated_sorted = sorted(self.generated_preview_notes) if self.generation_tab_active else []
        if self.scale_tab_active:
            name_overlay_notes = set(display_active_notes) | set(self.staff_pressed_scale_notes)
            if self.scale_loop_active and self.scale_current_note is not None:
                name_overlay_notes.add(self.scale_current_note)
        elif self.generation_tab_active:
            name_overlay_notes = set(self.generated_preview_notes)
        elif self.tuner_tab_active:
            name_overlay_notes = set()
            if self.tuner_detected_note_midi is not None:
                name_overlay_notes.add(int(self.tuner_detected_note_midi))
            if self.tuner_reference_note is not None:
                name_overlay_notes.add(int(self.tuner_reference_note))
        else:
            name_overlay_notes = set(self._current_detection_notes())
        scale_note_set = set(self.scale_preview_notes) if self.scale_tab_active else set()
        scale_name_map = self._scale_note_name_map() if self.scale_tab_active else {}
        generation_name_map = self._generation_note_name_map(with_octave=False) if self.generation_tab_active else {}
        detection_name_map = dict(getattr(self, "detection_overlay_note_names", {})) if not (self.generation_tab_active or self.scale_tab_active or self.metronome_tab_active or self.tuner_tab_active) else {}
        scale_tonic_pc = self.scale_tonic_pc
        current_scale_note = self.scale_current_note if (self.scale_tab_active and self.scale_loop_active) else None
        scale_input_raw_note = int(self.scale_input_raw_note) if (self.scale_tab_active and self.scale_input_raw_note is not None) else None
        detection_extra_notes = set(self.detection_extra_notes) if not (self.generation_tab_active or self.scale_tab_active or self.metronome_tab_active or self.tuner_tab_active) else set()
        detection_mode = not (self.generation_tab_active or self.scale_tab_active or self.metronome_tab_active or self.tuner_tab_active)
        now = time.monotonic()
        self.blocked_note_until = {n: t for n, t in self.blocked_note_until.items() if t > now}
        overlay_label_positions: dict[int, tuple[float, str, str]] = {}
        # In generation/scale modes, note names are already conveyed on-key/staff; avoid duplicate labels on top.
        show_top_note_overlays = (not detection_mode) and (not self.generation_tab_active) and (not self.scale_tab_active)

        # Ancho visible del viewport del QScrollArea (no el ancho lógico del canvas tras setFixedWidth).
        viewport_w = max(120, int(canvas.winfo_width()))
        qs = getattr(self, "keyboard_qscroll", None)
        if qs is not None:
            try:
                vp = qs.viewport()
                if vp is not None and int(vp.width()) > 0:
                    viewport_w = max(120, int(vp.width()))
            except Exception:
                pass
        # El alto del canvas lo fija la UI (p. ej. 124 en metrónomo, 156 en otros modos).
        h = max(96, int(canvas.winfo_height()))

        low_note, high_note = 21, 108
        notes = list(range(low_note, high_note + 1))
        scale_rh_display_notes: set[int] = set()
        scale_lh_display_notes: set[int] = set()
        generation_rh_display_notes: set[int] = set()
        generation_lh_display_notes: set[int] = set()
        generation_active_rh_notes: set[int] = set()
        generation_active_lh_notes: set[int] = set()
        if self.scale_tab_active and self.scale_play_mode == "piano":
            scale_rh_display_notes = {int(n) for n in set(self.scale_preview_notes)}
            first_rh = min(scale_rh_display_notes) if scale_rh_display_notes else None
            scale_lh_display_notes = {
                int(n - 12)
                for n in set(self.scale_preview_notes)
                if (low_note <= int(n - 12) <= high_note) and (first_rh is None or int(n - 12) < first_rh)
            }
        scale_display_notes = set(scale_rh_display_notes) | set(scale_lh_display_notes)
        scale_raw_outside_display = (
            self.scale_tab_active
            and self.scale_play_mode == "piano"
            and scale_input_raw_note is not None
            and scale_input_raw_note not in scale_display_notes
        )
        if self.generation_tab_active and self.instrument_view == "piano":
            generation_rh_display_notes = {int(n) for n in set(self.generated_preview_notes)}
            # Mano izquierda del acorde (una octava abajo): siempre desde el acorde, no desde la nota pulsada.
            generation_lh_display_notes = {
                int(n - 12)
                for n in set(self.generated_preview_notes)
                if (low_note <= int(n - 12) <= high_note)
            }
            for note in set(self.generated_playing_notes):
                note_int = int(note)
                if note_int in generation_lh_display_notes and note_int not in generation_rh_display_notes:
                    generation_active_lh_notes.add(note_int)
                elif note_int in generation_rh_display_notes:
                    generation_active_rh_notes.add(note_int)
                elif note_int in generation_lh_display_notes:
                    generation_active_lh_notes.add(note_int)
                else:
                    generation_active_rh_notes.add(note_int)
        white_notes = [n for n in notes if (n % 12) in WHITE_PCS]
        # Misma idea que la web: ~clamp(28px,…) por tecla blanca; si no cabe, scroll horizontal.
        _kb_min_white_px = 28
        content_w = max(float(viewport_w), float(len(white_notes)) * float(_kb_min_white_px))
        white_w = content_w / len(white_notes)
        w = content_w
        # Ajuste de proporción del teclado: menos altura y más presencia.
        scale_fingering_active = (
            self.scale_tab_active
            and getattr(self, "scale_fingering_hand", None) is not None
        )
        strip_h = 22 if scale_fingering_active else 0
        key_top = (strip_h + 4) if scale_fingering_active else 4
        # Fixed key_bottom so the piano is the same height regardless of fingering,
        # but shrink it when the canvas itself is shorter (e.g. metronome compact
        # mode fixes the canvas to 124px instead of 156px) so keys and note labels
        # stay fully inside the visible area instead of being clipped.
        key_bottom = min(148, max(60, h - 8))
        # desc strip at key_bottom+4 .. key_bottom+22; canvas needs key_bottom+28 when active.
        black_h = int((key_bottom - key_top) * 0.58)
        show_key_names = self.config_data.get("show_keyboard_note_labels", True)

        white_index: dict[int, int] = {}
        idx = 0
        for note in notes:
            if (note % 12) in WHITE_PCS:
                white_index[note] = idx
                idx += 1

        scale_key_center_x: dict[int, float] = {}

        # Fondo y marco como `.piano` en web: background #e8ecf2, borde #3a4558.
        panel_bg = getattr(self, "color_surface_alt", "#2f3a4b")
        canvas.create_rectangle(0, 0, content_w, max(h, key_bottom + 74), fill=panel_bg, outline="")
        canvas.create_rectangle(0, key_top, content_w, key_bottom, fill="#e8ecf2", outline="#3a4558", width=1)

        def _draw_bottom_rounded_key(
            x1: float,
            y1: float,
            x2: float,
            y2: float,
            radius: float,
            *,
            fill: str,
            outline: str,
            width: float,
        ) -> None:
            r = max(0.0, min(radius, (x2 - x1) / 2.0, (y2 - y1) / 2.0))
            draw_unified = getattr(canvas, "create_bottom_rounded_rect", None)
            if callable(draw_unified):
                draw_unified(
                    x1,
                    y1,
                    x2,
                    y2,
                    radius=r,
                    fill=fill,
                    outline=outline,
                    width=width,
                )
                return
            if r < 1.0:
                canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)
                return
            # Fallback Tk: varias primitivas (puede dejar artefactos en Qt antiguo).
            canvas.create_rectangle(x1, y1, x2, y2 - r, fill=fill, outline="")
            canvas.create_rectangle(x1 + r, y2 - r, x2 - r, y2, fill=fill, outline="")
            canvas.create_arc(x1, y2 - (2 * r), x1 + (2 * r), y2, start=180, extent=90, style=tk.PIESLICE, fill=fill, outline="")
            canvas.create_arc(x2 - (2 * r), y2 - (2 * r), x2, y2, start=270, extent=90, style=tk.PIESLICE, fill=fill, outline="")
            canvas.create_line(x1, y1, x2, y1, fill=outline, width=width)
            canvas.create_line(x1, y1, x1, y2 - r, fill=outline, width=width)
            canvas.create_line(x2, y1, x2, y2 - r, fill=outline, width=width)
            canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width)
            canvas.create_arc(
                x1,
                y2 - (2 * r),
                x1 + (2 * r),
                y2,
                start=180,
                extent=90,
                style=tk.ARC,
                outline=outline,
                width=width,
            )
            canvas.create_arc(
                x2 - (2 * r),
                y2 - (2 * r),
                x2,
                y2,
                start=270,
                extent=90,
                style=tk.ARC,
                outline=outline,
                width=width,
            )

        # Rendija entre blancas (la web lleva borde 1px por lado; aquí ~1px de fondo visible).
        _white_key_inset = 0.5

        for note in notes:
            if (note % 12) not in WHITE_PCS:
                continue
            i = white_index[note]
            x1 = i * white_w + _white_key_inset
            x2 = (i + 1) * white_w - _white_key_inset

            # Bordes alineados a `style.css` (.key, .rh, .lh, etc.).
            if note in detection_extra_notes:
                fill_color = "#bf2f2f"
                outline_color = "#5c1515"
            elif (
                self.scale_tab_active
                and self.scale_play_mode == "piano"
                and scale_raw_outside_display
                and note == scale_input_raw_note
            ):
                fill_color = "#ffe2a6"
                outline_color = "#7b8798"
            elif (
                self.scale_tab_active
                and self.scale_play_mode == "piano"
                and note in display_active_notes
                and note in scale_lh_display_notes
                and note not in scale_rh_display_notes
            ):
                fill_color = "#ff6a00"
                outline_color = "#c8772f"
            elif self.scale_tab_active and self.scale_play_mode == "piano" and note in display_active_notes:
                fill_color = "#39c5ff"
                outline_color = "#2b6da6"
            elif self.scale_tab_active and note == current_scale_note:
                fill_color = "#65b7ff"
                outline_color = "#2b6da6"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in self.generation_midi_held_notes:
                # MIDI notes held in generation mode: gold/yellow highlight
                fill_color = "#f3bf2f"
                outline_color = "#d4a017"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_active_lh_notes:
                fill_color = "#ff6a00"
                outline_color = "#c8772f"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_active_rh_notes:
                fill_color = "#39c5ff"
                outline_color = "#2b6da6"
            elif note in display_active_notes:
                fill_color = "#4da3ea"
                outline_color = "#2b6da6"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_lh_display_notes:
                fill_color = "#ff8a2b"
                outline_color = "#c8772f"
            else:
                fill_color = "#f7f7f4"
                outline_color = "#7b8798"

            # Web: `.key { border-radius: 0 0 8px 8px; border: 1px solid #7b8798 }`.
            _draw_bottom_rounded_key(
                x1,
                key_top,
                x2,
                key_bottom,
                radius=max(4.0, min(9.0, white_w * 0.29)),
                fill=fill_color,
                outline=outline_color,
                width=1,
            )
            if show_key_names:
                is_generation_active = note in generation_active_lh_notes or note in generation_active_rh_notes
                label_color = "#10243a" if (note in display_active_notes or is_generation_active) else "#5f5f5f"
                label_pt = max(8, min(11, int(white_w * 0.32)))
                canvas.create_text(
                    (x1 + x2) / 2,
                    key_bottom - 16,
                    text=self.note_name(note, with_octave=False),
                    fill=label_color,
                    font=("Helvetica", label_pt, "bold"),
                )
            if self.scale_tab_active and note in scale_note_set:
                circle_fill = "#32d74b" if (note % 12) == scale_tonic_pc else "#f6b60b"
                cx = (x1 + x2) / 2
                scale_key_center_x[note] = cx
                r = max(11, min(17, white_w * 0.28))
                cy = key_bottom - (42 if show_key_names else 28)
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=circle_fill, outline="")
                circle_text = scale_name_map.get(note % 12, self.note_name(note, with_octave=False))
                canvas.create_text(cx, cy, text=circle_text, fill="#101010", font=("Helvetica", 11, "bold"))
            if show_top_note_overlays and note in name_overlay_notes:
                label_fill = "#ff6d6d" if note in detection_extra_notes else "#ffffff"
                if self.scale_tab_active:
                    overlay_text = scale_name_map.get(note % 12, self.note_name(note, with_octave=False))
                elif self.generation_tab_active:
                    overlay_text = generation_name_map.get(note, self.note_name(note, with_octave=False))
                elif detection_name_map:
                    overlay_text = detection_name_map.get(note, self.note_name(note, with_octave=False))
                else:
                    overlay_text = self.note_name(note, with_octave=False)
                overlay_label_positions[note] = ((x1 + x2) / 2, overlay_text, label_fill)
            if note in self.blocked_note_until:
                self._draw_forbidden_icon(canvas, (x1 + x2) / 2, key_bottom - 22, 8)
            self.white_key_regions.append((note, x1, key_top, x2, key_bottom))

        black_w = white_w * 0.64
        for note in notes:
            if (note % 12) in WHITE_PCS:
                continue
            prev_white = note - 1
            while prev_white >= low_note and (prev_white % 12) not in WHITE_PCS:
                prev_white -= 1
            if prev_white < low_note:
                continue
            if prev_white not in white_index:
                continue
            i = white_index[prev_white]
            center_x = (i + 1) * white_w
            x1 = center_x - black_w / 2
            x2 = center_x + black_w / 2
            # Keep black-key geometry on whole pixels to avoid anti-aliased light artifacts.
            x1_i = int(round(x1))
            x2_i = int(round(x2))
            if x2_i <= x1_i:
                x2_i = x1_i + 1

            if note in detection_extra_notes:
                fill_color = "#bf2f2f"
            elif (
                self.scale_tab_active
                and self.scale_play_mode == "piano"
                and scale_raw_outside_display
                and note == scale_input_raw_note
            ):
                fill_color = "#7f5711"
            elif (
                self.scale_tab_active
                and self.scale_play_mode == "piano"
                and note in display_active_notes
                and note in scale_lh_display_notes
                and note not in scale_rh_display_notes
            ):
                fill_color = "#d45a00"
            elif self.scale_tab_active and self.scale_play_mode == "piano" and note in display_active_notes:
                fill_color = "#1089d8"
            elif self.scale_tab_active and note == current_scale_note:
                fill_color = "#388fdb"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_active_lh_notes:
                fill_color = "#d45a00"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_active_rh_notes:
                fill_color = "#1089d8"
            elif note in display_active_notes:
                fill_color = "#0078d7"
            elif self.generation_tab_active and self.instrument_view == "piano" and note in generation_lh_display_notes:
                fill_color = "#ff8a2b"
            else:
                fill_color = "#101822"

            # Misma idea que la web (hereda `border-radius: 0 0 8px 8px`); radio acotado al ancho/alto
            # de la negra para no superar semitecla y suavizar artefactos en bordes muy curvos.
            _draw_bottom_rounded_key(
                x1_i,
                key_top,
                x2_i,
                key_top + black_h,
                radius=max(2.0, min(6.5, min(float(black_w), float(black_h)) * 0.36)),
                fill=fill_color,
                outline="#0a0f16",
                width=1,
            )
            if self.scale_tab_active and note in scale_note_set:
                circle_fill = "#32d74b" if (note % 12) == scale_tonic_pc else "#f6b60b"
                cx = (x1_i + x2_i) / 2
                scale_key_center_x[note] = cx
                cy = key_top + black_h - 22
                r = max(9, min(13, black_w * 0.28))
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=circle_fill, outline="")
                circle_text = scale_name_map.get(note % 12, self.note_name(note, with_octave=False))
                canvas.create_text(cx, cy, text=circle_text, fill="#101010", font=("Helvetica", 8, "bold"))
            elif show_key_names:
                is_generation_active = note in generation_active_lh_notes or note in generation_active_rh_notes
                blabel = "#f0f4fc" if (note in display_active_notes or is_generation_active) else "#9aacbf"
                bl_pt = max(7, min(10, int(black_w * 0.42)))
                canvas.create_text(
                    (x1_i + x2_i) / 2,
                    key_top + black_h - 4,
                    text=self.note_name(note, with_octave=False),
                    fill=blabel,
                    font=("Helvetica", bl_pt, "bold"),
                    anchor="s",
                )
            if show_top_note_overlays and note in name_overlay_notes:
                label_fill = "#ff6d6d" if note in detection_extra_notes else "#ffffff"
                if self.scale_tab_active:
                    overlay_text = scale_name_map.get(note % 12, self.note_name(note, with_octave=False))
                elif self.generation_tab_active:
                    overlay_text = generation_name_map.get(note, self.note_name(note, with_octave=False))
                elif detection_name_map:
                    overlay_text = detection_name_map.get(note, self.note_name(note, with_octave=False))
                else:
                    overlay_text = self.note_name(note, with_octave=False)
                overlay_label_positions[note] = ((x1_i + x2_i) / 2, overlay_text, label_fill)
            if note in self.blocked_note_until:
                self._draw_forbidden_icon(canvas, (x1_i + x2_i) / 2, key_top + black_h * 0.5, 7)
            self.black_key_regions.append((note, x1_i, key_top, x2_i, key_top + black_h))

        if overlay_label_positions:
            if detection_mode:
                label_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
                lower_line_end: list[float] = []
                upper_line_end: list[float] = []
                upper_y = 1
                lower_y = 12
                for note, (cx, text, label_fill) in sorted(overlay_label_positions.items(), key=lambda item: item[1][0]):
                    half_w = (float(label_font.measure(text)) / 2.0) + 3.0
                    x_left = cx - half_w
                    x_right = cx + half_w
                    lower_overlap = any(x_left < end for end in lower_line_end)
                    upper_overlap = any(x_left < end for end in upper_line_end)
                    if not lower_overlap:
                        y = lower_y
                        lower_line_end.append(x_right + 2.0)
                    elif not upper_overlap:
                        y = upper_y
                        upper_line_end.append(x_right + 2.0)
                    else:
                        if (upper_line_end[-1] if upper_line_end else -1.0) <= (lower_line_end[-1] if lower_line_end else -1.0):
                            y = upper_y
                            upper_line_end.append(x_right + 2.0)
                        else:
                            y = lower_y
                            lower_line_end.append(x_right + 2.0)
                    canvas.create_text(
                        cx,
                        y,
                        text=text,
                        fill=label_fill,
                        font=("Helvetica", 10, "bold"),
                        anchor="n",
                    )
            else:
                for _note, (cx, text, label_fill) in overlay_label_positions.items():
                    canvas.create_text(
                        cx,
                        5,
                        text=text,
                        fill=label_fill,
                        font=("Helvetica", 10, "bold"),
                        anchor="n",
                    )

        # Franja inferior para dar profundidad y etiquetas de octava.
        if self.generation_tab_active and self.instrument_view == "piano" and generated_sorted:
            key_centers: dict[int, tuple[float, float, bool]] = {}
            for note, x1, y1, x2, y2 in self.white_key_regions:
                key_centers[int(note)] = ((x1 + x2) * 0.5, y2 - 34.0, False)
            for note, x1, y1, x2, y2 in self.black_key_regions:
                key_centers[int(note)] = ((x1 + x2) * 0.5, y1 + (y2 - y1) * 0.60, True)

            rh_notes = [int(n) for n in generated_sorted if int(n) in key_centers]
            lh_notes = [int(n - 12) for n in generated_sorted if int(n - 12) in key_centers]
            rh_fingers = self._piano_fingering_for_count(len(rh_notes), hand="right")
            lh_fingers = self._piano_fingering_for_count(len(lh_notes), hand="left")

            for note, finger in zip(rh_notes, rh_fingers):
                cx, cy, is_black = key_centers[note]
                r = 10.0 if is_black else 12.0
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#ffd45a", outline="#8c6d00", width=1)
                canvas.create_text(cx, cy, text=str(finger), fill="#101010", font=("Helvetica", 10, "bold"))

            for note, finger in zip(lh_notes, lh_fingers):
                cx, cy, is_black = key_centers[note]
                r = 10.0 if is_black else 12.0
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#ffd45a", outline="#8c6d00", width=1)
                canvas.create_text(cx, cy, text=str(finger), fill="#101010", font=("Helvetica", 10, "bold"))

        # Franjas de digitaciones de escala (ascendente arriba, descendente abajo).
        if scale_fingering_active and scale_key_center_x:
            try:
                scale_fingerings = self._get_scale_fingerings()
                sorted_notes = sorted(scale_key_center_x.keys())
                fingers = [scale_fingerings.get(n) for n in sorted_notes]
                # Crossovers ascending: |f[i] - f[i-1]| > 1
                asc_crossover = [False] * len(sorted_notes)
                for i in range(1, len(sorted_notes) - 1):
                    if fingers[i] is not None and fingers[i - 1] is not None:
                        if abs(fingers[i] - fingers[i - 1]) > 1:
                            asc_crossover[i] = True
                # Crossovers descending: |f[i] - f[i+1]| > 1
                desc_crossover = [False] * len(sorted_notes)
                for i in range(1, len(sorted_notes) - 1):
                    if fingers[i] is not None and fingers[i + 1] is not None:
                        if abs(fingers[i] - fingers[i + 1]) > 1:
                            desc_crossover[i] = True
                bw = max(16, min(20, white_w * 0.52))
                bh = 18
                asc_y = 2
                desc_y = key_bottom + 6
                for idx, note in enumerate(sorted_notes):
                    if fingers[idx] is None:
                        continue
                    cx = scale_key_center_x[note]
                    bx1 = cx - bw / 2
                    bx2 = cx + bw / 2
                    # Ascending strip
                    asc_fill = "#d42010" if asc_crossover[idx] else "#e07818"
                    asc_outline = "#8a1208" if asc_crossover[idx] else "#9a4a08"
                    canvas.create_rectangle(bx1, asc_y, bx2, asc_y + bh, fill=asc_fill, outline=asc_outline, width=1)
                    canvas.create_text(cx, asc_y + bh / 2, text=str(fingers[idx]), fill="#ffffff", font=("Helvetica", 10, "bold"), tags="fingering")
                    # Descending strip
                    desc_fill = "#4a6a8a" if not desc_crossover[idx] else "#3a3a8a"
                    desc_outline = "#2a4a6a" if not desc_crossover[idx] else "#1a1a5a"
                    canvas.create_rectangle(bx1, desc_y, bx2, desc_y + bh, fill=desc_fill, outline=desc_outline, width=1)
                    canvas.create_text(cx, desc_y + bh / 2, text=str(fingers[idx]), fill="#ffffff", font=("Helvetica", 10, "bold"), tags="fingering")
            except Exception:
                pass

        # Narrow dark separator between piano bottom and descending strip (or canvas bottom).
        canvas.create_rectangle(0, key_bottom, w, key_bottom + 4, fill="#101010", outline="")

        try:
            canvas.setFixedWidth(int(round(content_w)))
        except Exception:
            pass

    def redraw_staff(self) -> None:
        canvas = self.staff_canvas
        canvas.delete("all")
        self.staff_scale_note_regions = []
        self.staff_generation_note_regions = []
        self.tuner_string_regions = []
        if self.tuner_tab_active:
            w = max(300, canvas.winfo_width())
            h = max(220, canvas.winfo_height())
            canvas.create_rectangle(0, 0, w, h, fill="#000000", outline="")
            tuning = self._tuner_tuning_def()
            notes = [int(n) for n in tuning["notes"]]
            language = str(self.config_data.get("language", "es"))
            now = time.monotonic()

            top_margin = 16.0
            bottom_margin = 14.0
            section_gap = max(10.0, h * 0.028)
            usable_h = max(140.0, h - top_margin - bottom_margin)

            cards_h = min(122.0, max(72.0, usable_h * 0.36))
            note_h = min(72.0, max(40.0, usable_h * 0.18))
            meter_h = min(62.0, max(42.0, usable_h * 0.20))
            cents_h = min(30.0, max(18.0, usable_h * 0.10))

            # If content overflows, shrink note + cards first.
            total_h = cards_h + note_h + meter_h + cents_h + (section_gap * 3)
            overflow = total_h - usable_h
            if overflow > 0:
                reduce_note = min(overflow * 0.55, max(0.0, note_h - 34.0))
                note_h -= reduce_note
                overflow -= reduce_note
            if overflow > 0:
                reduce_cards = min(overflow, max(0.0, cards_h - 64.0))
                cards_h -= reduce_cards

            total_h = cards_h + note_h + meter_h + cents_h + (section_gap * 3)
            start_y = max(top_margin, (h - total_h) * 0.5)

            pad_x = 20.0
            card_gap = max(6.0, min(12.0, w * 0.012))
            card_w = max(64.0, (w - (pad_x * 2) - (card_gap * 5)) / 6.0)
            cards_y = start_y
            for idx, note in enumerate(notes):
                x1 = pad_x + idx * (card_w + card_gap)
                x2 = x1 + card_w
                y1 = cards_y
                y2 = y1 + cards_h
                active = self.tuner_current_string_idx == idx or self.tuner_button_active_until.get(idx, 0.0) > now
                fill = "#f39c12" if active else "#d2d8df"
                text_color = "#ffffff" if active else "#2b2e34"
                # Rounded capsule card for each string button.
                r = min((y2 - y1) / 2.0, max(10.0, (x2 - x1) * 0.26))
                canvas.create_oval(x1, y1, x1 + 2 * r, y2, fill=fill, outline="")
                canvas.create_oval(x2 - 2 * r, y1, x2, y2, fill=fill, outline="")
                canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="")
                ordinal = self._guitar_string_ordinal(idx, language)
                note_name = self.note_name(note, with_octave=False)
                ord_font = ("Helvetica", max(10, min(13, int(cards_h * 0.14))), "bold")
                note_font = ("Helvetica", max(17, min(26, int(cards_h * 0.29))), "bold")
                canvas.create_text((x1 + x2) / 2, y1 + cards_h * 0.28, text=ordinal, fill=text_color, font=ord_font)
                canvas.create_text((x1 + x2) / 2, y1 + cards_h * 0.64, text=note_name, fill=text_color, font=note_font)
                self.tuner_string_regions.append((idx, x1, y1, x2, y2))

            live_note = "-"
            note_y = cards_y + cards_h + section_gap + (note_h * 0.5)
            live_font = ("Helvetica", max(24, min(44, int(note_h * 0.78))), "bold")
            if self.tuner_detected_note_midi is not None:
                live_note = self.note_name(int(self.tuner_detected_note_midi), with_octave=False)
                if self.tuner_current_freq > 0.0:
                    live_note = f"{live_note} ({self.tuner_current_freq:.1f} Hz)"
                    live_font = ("Helvetica", max(18, min(30, int(note_h * 0.55))), "bold")
            canvas.create_text(w / 2, note_y, text=live_note, fill="#ff9e34", font=live_font)

            meter_x1 = 24.0
            meter_x2 = w - 24.0
            meter_y1 = note_y + (note_h * 0.5) + section_gap
            meter_y2 = meter_y1 + meter_h
            canvas.create_oval(meter_x1, meter_y1, meter_x1 + (meter_y2 - meter_y1), meter_y2, fill="#c8c8ca", outline="")
            canvas.create_oval(meter_x2 - (meter_y2 - meter_y1), meter_y1, meter_x2, meter_y2, fill="#c8c8ca", outline="")
            canvas.create_rectangle(
                meter_x1 + (meter_y2 - meter_y1) / 2,
                meter_y1,
                meter_x2 - (meter_y2 - meter_y1) / 2,
                meter_y2,
                fill="#c8c8ca",
                outline="",
            )
            center_x = (meter_x1 + meter_x2) / 2
            canvas.create_line(center_x, meter_y1 + 2, center_x, meter_y2 - 2, fill="#16a05f", width=5)
            cents = max(-50.0, min(50.0, float(self.tuner_current_cents)))
            knob_x = meter_x1 + ((cents + 50.0) / 100.0) * (meter_x2 - meter_x1)
            r = min(14.0, (meter_y2 - meter_y1) * 0.36)
            canvas.create_oval(knob_x - r, (meter_y1 + meter_y2) / 2 - r, knob_x + r, (meter_y1 + meter_y2) / 2 + r, fill="#ff5a2f", outline="")

            if self.tuner_current_string_idx is not None:
                cents_txt = f"{self.tuner_current_cents:+.1f} cents"
                cents_font = ("Helvetica", max(11, min(15, int(cents_h * 0.60))), "bold")
                cents_y = min(h - bottom_margin, meter_y2 + section_gap + (cents_h * 0.45))
                canvas.create_text(w / 2, cents_y, text=cents_txt, fill="#9fb2c8", font=cents_font)
            return
        if self.metronome_tab_active:
            self._draw_metronome_panel(canvas)
            return
        instrument_override = self.generation_tab_active and self.instrument_view == "guitar" and bool(self.guitar_selected_variation_notes)
        scale_bass_display_notes: set[int] = set()
        if instrument_override:
            display_notes_list = []
            display_notes = set(self.guitar_selected_variation_notes)
        elif self.scale_tab_active:
            display_notes_list = list(getattr(self, "scale_base_notes", self.scale_preview_notes))
            first_treble = int(display_notes_list[0]) if display_notes_list else None
            scale_bass_display_notes = {
                int(n - 12)
                for n in display_notes_list
                if int(n - 12) >= 0 and (first_treble is None or int(n - 12) < first_treble)
            }
            display_notes = set(display_notes_list)
        else:
            display_notes_list = []
            if self.generation_tab_active:
                display_notes = self.generated_preview_notes
            elif getattr(self, "interval_tab_active", False):
                if getattr(self, "interval_melody_mode", False):
                    display_notes = set(n for n in self.get_interval_melody_notes() if n is not None)
                else:
                    display_notes = set(getattr(self, "interval_notes", []))
            else:
                display_notes = self._current_detection_notes()
            if self.generation_tab_active:
                # Show LH voicing in bass clef (same pitch classes, one octave lower) for piano and guitar views.
                lh_notes = {int(n - 12) for n in set(self.generated_preview_notes) if int(n - 12) >= 0}
                display_notes = set(display_notes) | lh_notes
                # Incluir notas actualmente pulsadas en el piano (LH) para que se marquen en el pentagrama.
                display_notes = display_notes | set(self.generated_playing_notes)
        generation_name_map = self._generation_note_name_map(with_octave=False) if self.generation_tab_active else {}

        w = max(300, canvas.winfo_width())
        h = max(260, canvas.winfo_height())

        margin_x = 72
        right_x = w - 20
        line_space = min(22, max(11, h // 24))
        # Con muchas notas en una escala (p.ej. cromática a 2-3 octavas,
        # hasta 37-39 notas), el hueco horizontal por nota puede quedar muy
        # por debajo de lo que necesita una cabeza de nota + símbolo de
        # alteración a tamaño normal, provocando solapes. Se reduce
        # line_space (y por tanto TODO el tamaño: pentagrama, notas,
        # alteraciones) en proporción al hueco horizontal real disponible.
        if self.scale_tab_active and display_notes_list:
            _sig_count_probe, _ = self._staff_signature_context(display_notes)
            # Aproximacion del ancho de la armadura (clave + espacio + una
            # alteracion por cada # o b de la tonalidad) al line_space
            # todavia sin reducir, para no subestimar cuanto hueco le queda
            # realmente a las notas cuando hay muchas alteraciones (p.ej.
            # Do# mayor = 7).
            estimated_left = margin_x + 60.0 + (_sig_count_probe * line_space * 0.95)
            estimated_right = max(estimated_left + 1, right_x - 40)
            estimated_step_x = max(
                6.0,
                (estimated_right - estimated_left) / max(1, len(display_notes_list) - 1),
            )
            # Con una cabeza de nota (~0.72*line_space de radio) mas su
            # simbolo de alteracion (que no debe invadir esa cabeza) mas
            # aire hasta la nota siguiente, hacen falta del orden de 70px
            # de hueco horizontal a line_space=22 para que no se vea
            # apelotonado; si hay menos, se reduce line_space en la misma
            # proporcion.
            comfortable_step_at_max = 70.0
            if estimated_step_x < comfortable_step_at_max:
                scale_factor = max(0.32, estimated_step_x / comfortable_step_at_max)
                line_space = max(7, int(line_space * scale_factor))
        vertical_shift = int(2 * line_space)
        # Si la nota mas aguda a dibujar (p.ej. una escala cromatica de mas
        # de una octava) necesita varias lineas adicionales por encima del
        # pentagrama de clave de sol, el margen superior fijo la dejaba
        # recortada fuera del canvas. Se amplia el desplazamiento vertical
        # segun cuantas lineas adicionales hagan falta.
        treble_bottom_line_diatonic_probe = 4 * 7 + 2  # E4
        treble_top_line_diatonic_probe = treble_bottom_line_diatonic_probe + 8  # F5
        treble_notes_probe = [n for n in display_notes if int(n) >= 60]
        if treble_notes_probe:
            max_diatonic_idx = max(self._diatonic_index(int(n)) for n in treble_notes_probe)
            extra_above = max_diatonic_idx - treble_top_line_diatonic_probe
            if extra_above > 0:
                extra_ledger_lines = (extra_above + 1) // 2
                vertical_shift += int(extra_ledger_lines * line_space)
        treble_top = max(68, int(h * 0.23)) + vertical_shift
        bass_top = treble_top + int(line_space * 7.4)

        for i in range(5):
            y = treble_top + i * line_space
            canvas.create_line(margin_x, y, right_x, y, fill="#f1f1f1", width=1)

        for i in range(5):
            y = bass_top + i * line_space
            canvas.create_line(margin_x, y, right_x, y, fill="#f1f1f1", width=1)

        # Barra inicial del sistema (estilo partitura).
        canvas.create_line(margin_x, treble_top, margin_x, bass_top + 4 * line_space, fill="#f1f1f1", width=2)

        # Llave del gran pentagrama alineada exactamente al sistema.
        top_y = treble_top
        bottom_y = bass_top + 4 * line_space
        brace_target_h = int(bottom_y - top_y + 1)
        brace_img = self._get_brace_image_for_height(brace_target_h)
        if brace_img is not None:
            brace_x = margin_x - brace_img.width() - 8
            brace_y = int((top_y + bottom_y - brace_img.height()) / 2)
            canvas.create_image(brace_x, brace_y, image=brace_img, anchor="nw")
        else:
            mid_y = (top_y + bottom_y) / 2
            brace_inner_x = margin_x - 12
            brace_outer_x = margin_x - 34
            brace_points = [
                brace_inner_x, top_y,
                brace_outer_x - 7, top_y + line_space * 0.55,
                brace_outer_x - 5, top_y + line_space * 1.75,
                brace_outer_x + 4, mid_y - line_space * 1.0,
                brace_outer_x - 6, mid_y - line_space * 0.26,
                brace_outer_x - 6, mid_y + line_space * 0.26,
                brace_outer_x + 4, mid_y + line_space * 1.0,
                brace_outer_x - 5, bottom_y - line_space * 1.75,
                brace_outer_x - 7, bottom_y - line_space * 0.55,
                brace_inner_x, bottom_y,
            ]
            canvas.create_line(
                brace_points,
                fill="#f1f1f1",
                width=4,
                smooth=True,
                splinesteps=48,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
            )

        # Clave de sol y clave de fa: misma escala relativa que la web (𝄞/𝄢 más grandes que antes).
        treble_pt, bass_pt = self._staff_clef_sizes_px(int(line_space))
        treble_x, treble_y = 108, treble_top + line_space * 2.7
        bass_x, bass_y = 108, bass_top + line_space * 2.25
        treble_img = getattr(self, "treble_clef_image", None)
        if treble_img is not None:
            scaled_t = self._scaled_clef_pixmap(treble_img, treble_pt, "treble")
            canvas.create_image(treble_x, treble_y, image=scaled_t or treble_img, anchor="center")
        else:
            clef_font = getattr(self, "_clef_font_family", "serif")
            canvas.create_text(treble_x, treble_y, text="𝄞", font=(clef_font, treble_pt), fill="#ffffff")
        bass_img = getattr(self, "bass_clef_image", None)
        if bass_img is not None:
            scaled_b = self._scaled_clef_pixmap(bass_img, bass_pt, "bass")
            canvas.create_image(bass_x, bass_y, image=scaled_b or bass_img, anchor="center")
        else:
            clef_font = getattr(self, "_clef_font_family", "serif")
            canvas.create_text(bass_x, bass_y, text="𝄢", font=(clef_font, bass_pt), fill="#ffffff")

        signature_count, prefer_flat_signature = self._staff_signature_context(display_notes)
        sharp_order_pcs = [6, 1, 8, 3, 10, 5, 0]  # F# C# G# D# A# E# B#
        sharp_order_naturals = [5, 0, 7, 2, 9, 4, 11]  # F C G D A E B
        flat_order_pcs = [10, 3, 8, 1, 6, 11, 4]   # Bb Eb Ab Db Gb Cb Fb
        flat_order_naturals = [11, 4, 9, 2, 7, 0, 5]  # B E A D G C F
        if signature_count > 0:
            if prefer_flat_signature:
                signature_pcs = flat_order_pcs[:signature_count]
                signature_base_naturals = set(flat_order_naturals[:signature_count])
            else:
                signature_pcs = sharp_order_pcs[:signature_count]
                signature_base_naturals = set(sharp_order_naturals[:signature_count])
        else:
            signature_pcs = []
            signature_base_naturals = set()
        use_key_signature = signature_count > 0
        signature_pc_set = set(signature_pcs)
        active_signature_indices: set[int] = set()
        if self.scale_tab_active and display_notes_list and use_key_signature:
            base_scale_ordered_for_signature = [int(note) for note in display_notes_list]
            root_midi = base_scale_ordered_for_signature[0]
            scale_labels_for_signature = self._spelled_scale_note_names(
                root_midi=root_midi,
                intervals=[int(note - root_midi) for note in base_scale_ordered_for_signature],
                tonic_pc=self.scale_tonic_pc,
                with_octave=False,
            )
            active_scale_notes = (
                set(self.staff_pressed_scale_notes)
                | set(self.scale_guitar_click_highlight_notes)
                | set(self.scale_guitar_drag_staff_notes)
            )
            if self.scale_loop_active and self.scale_current_note is not None:
                active_scale_notes.add(int(self.scale_current_note))
            for active_note in active_scale_notes:
                active_pc = int(active_note) % 12
                for degree, scale_note in enumerate(base_scale_ordered_for_signature):
                    if int(scale_note) % 12 != active_pc or degree >= len(scale_labels_for_signature):
                        continue
                    signature_index = self._key_signature_index_for_scale_note(
                        scale_labels_for_signature[degree],
                        scale_note,
                        signature_count,
                        prefer_flat_signature,
                    )
                    if signature_index >= 0:
                        active_signature_indices.add(signature_index)
                    break
        elif self.generation_tab_active and use_key_signature:
            active_generation_notes = (
                set(self.generated_playing_notes)
                | set(self.generation_midi_held_notes)
            )
            for active_note in active_generation_notes:
                signature_index = self._key_signature_index_for_midi(
                    int(active_note),
                    signature_count,
                    prefer_flat_signature,
                )
                if signature_index >= 0:
                    active_signature_indices.add(signature_index)
        signature_end_x = 132.0
        if use_key_signature:
            accidental_text = "♭" if prefer_flat_signature else "#"
            acc_sig_pt = self._staff_accidental_font_pt(
                int(line_space), prefer_flat=prefer_flat_signature
            )
            accidental_font = ("Helvetica", acc_sig_pt, "bold")
            # Tras la clave (𝄞 centrada en treble_x): mitad aproximada del ancho + margen para no solapar con la armadura.
            _clef_half_w = int(round(treble_pt * 0.52))
            _gap_after_clef = max(10, int(round(float(line_space) * 0.65)))
            sig_x_start = treble_x + _clef_half_w + _gap_after_clef
            sig_step_x = self._staff_key_sig_step_x(int(line_space), acc_sig_pt)
            signature_end_x = sig_x_start + ((max(1, min(7, len(signature_pcs))) - 1) * sig_step_x)
            if prefer_flat_signature:
                treble_offsets = [2.0, 0.5, 2.5, 1.0, 3.0, 1.5, 3.5]
                bass_offsets = [3.0, 1.5, 3.5, 2.0, 4.0, 2.5, 4.5]
            else:
                treble_offsets = [0.0, 1.5, -0.5, 1.0, 2.5, 0.5, 2.0]
                bass_offsets = [1.0, 2.5, 0.5, 2.0, 3.5, 1.5, 3.0]
            for idx in range(min(7, len(signature_pcs))):
                x = sig_x_start + (idx * sig_step_x)
                y_treble = treble_top + (treble_offsets[idx] * line_space)
                y_bass = bass_top + (bass_offsets[idx] * line_space)
                signature_color = "#39c5ff" if idx in active_signature_indices else "#ffffff"
                canvas.create_text(x, y_treble, text=accidental_text, fill=signature_color, font=accidental_font)
                canvas.create_text(x, y_bass, text=accidental_text, fill=signature_color, font=accidental_font)

        if not display_notes:
            canvas.create_text(
                w / 2,
                min(h - 48, bass_top + 5.6 * line_space),
                text=self.tr("staff_no_active_notes"),
                fill="#cfcfcf",
                font=("Helvetica", 13, "italic"),
            )
        else:
            _imel = False
            scale_staff_entries: list[tuple[int, int, bool]] = []  # (midi_note, degree_index, is_bass_clef)
            if self.scale_tab_active:
                treble_ordered = [int(n) for n in display_notes_list]
                first_treble = int(treble_ordered[0]) if treble_ordered else None
                bass_ordered = [
                    int(n - 12)
                    for n in display_notes_list
                    if int(n - 12) >= 0 and (first_treble is None or int(n - 12) < first_treble)
                ]
                pair_count = min(len(treble_ordered), len(bass_ordered))
                for idx in range(pair_count):
                    scale_staff_entries.append((bass_ordered[idx], idx, True))
                    scale_staff_entries.append((treble_ordered[idx], idx, False))
                if len(treble_ordered) > pair_count:
                    for idx in range(pair_count, len(treble_ordered)):
                        scale_staff_entries.append((treble_ordered[idx], idx, False))
                ordered = [int(note) for note, _degree, _is_bass in scale_staff_entries]
                # El simbolo de alteracion de la primera nota se dibuja
                # desplazado a su izquierda; sin hueco extra tras la
                # armadura, ese simbolo queda pegado (o encima) de la
                # ultima alteracion de la armadura, especialmente con
                # tonalidades de muchas alteraciones (p.ej. Do# = 7 #). El
                # hueco reservado es proporcional al tamaño real que
                # tendra ese simbolo (~1.12x el tamaño de fuente).
                _probe_acc_pt = self._staff_accidental_font_pt(
                    int(line_space), prefer_flat=prefer_flat_signature
                )
                first_accidental_gap = max(34.0, _probe_acc_pt * 1.12 + 14.0)
                left_x = max(margin_x + 88, signature_end_x + first_accidental_gap)
                right_limit = max(left_x + 1, right_x - 40)
                step_x = max(18.0, (right_limit - left_x) / max(1, len(display_notes_list) - 1))
                base_scale_ordered = [int(n) for n in display_notes_list]
                scale_label_names = self._spelled_scale_note_names(
                    root_midi=base_scale_ordered[0] if base_scale_ordered else 60,
                    intervals=[int(n - base_scale_ordered[0]) for n in base_scale_ordered] if base_scale_ordered else [0],
                    tonic_pc=self.scale_tonic_pc,
                    with_octave=False,
                ) if base_scale_ordered else []
                language = str(self.config_data.get("language", "es"))
                if language == "es":
                    label_prefixes = [("Do", 0), ("Re", 1), ("Mi", 2), ("Fa", 3), ("Sol", 4), ("La", 5), ("Si", 6)]
                else:
                    label_prefixes = [("C", 0), ("D", 1), ("E", 2), ("F", 3), ("G", 4), ("A", 5), ("B", 6)]
                tonic_letter = self._tonic_letter_index(
                    self.scale_tonic_pc, prefer_flat_signature, getattr(self, "scale_tonic_letter_pc", None)
                )
                scale_letter_indices: list[int] = []
                for idx, label in enumerate(scale_label_names):
                    text = str(label)
                    parsed_idx = None
                    for prefix, letter_idx in label_prefixes:
                        if text.startswith(prefix):
                            parsed_idx = letter_idx
                            break
                    scale_letter_indices.append(parsed_idx if parsed_idx is not None else ((tonic_letter + idx) % 7))
                scale_diatonic_indices: list[int] = []
                if base_scale_ordered:
                    first_letter_idx = scale_letter_indices[0] if scale_letter_indices else tonic_letter
                    scale_diatonic_indices.append((base_scale_ordered[0] // 12 - 1) * 7 + first_letter_idx)
                    for idx in range(1, len(base_scale_ordered)):
                        prev_letter = scale_letter_indices[idx - 1] if idx - 1 < len(scale_letter_indices) else ((tonic_letter + idx - 1) % 7)
                        curr_letter = scale_letter_indices[idx] if idx < len(scale_letter_indices) else ((tonic_letter + idx) % 7)
                        delta = (curr_letter - prev_letter) % 7
                        # delta=0 normalmente significa "misma letra, una
                        # octava mas arriba" (v.g. escalas diatonicas de 7
                        # notas, donde cada letra aparece una sola vez por
                        # octava). En la cromatica, dos notas consecutivas
                        # pueden compartir letra sin ser una octava real
                        # (p.ej. Do4->Do#4, a un semitono): en ese caso se
                        # dibujan en la MISMA linea/espacio del pentagrama
                        # (delta=0 real), diferenciandose solo por el
                        # simbolo de alteracion, no una octava mas arriba.
                        if delta == 0 and base_scale_ordered[idx] > base_scale_ordered[idx - 1]:
                            semitone_gap = base_scale_ordered[idx] - base_scale_ordered[idx - 1]
                            if semitone_gap >= 12:
                                delta = 7
                        scale_diatonic_indices.append(scale_diatonic_indices[-1] + delta)
                note_degree_map: dict[int, set[int]] = {}
                for mapped_note, mapped_degree, _mapped_is_bass in scale_staff_entries:
                    note_degree_map.setdefault(int(mapped_note), set()).add(int(mapped_degree))
                highlighted_scale_degrees: set[int] = set(self.staff_pressed_scale_degrees)
                if self.staff_hover_scale_degree is not None:
                    highlighted_scale_degrees.add(int(self.staff_hover_scale_degree))
                current_scale_degrees: set[int] = set()
                for active_note in set(self.scale_guitar_click_highlight_notes) | set(self.scale_guitar_drag_staff_notes):
                    highlighted_scale_degrees |= note_degree_map.get(int(active_note), set())
                if self.scale_loop_active and self.scale_current_note is not None:
                    current_note = int(self.scale_current_note)
                    current_pc = current_note % 12
                    for idx, scale_note in enumerate(base_scale_ordered):
                        if int(scale_note) == current_note or int(scale_note) % 12 == current_pc:
                            current_scale_degrees.add(int(idx))
                            break
            else:
                _imel = getattr(self, "interval_melody_mode", False) and getattr(self, "interval_tab_active", False)
                if _imel:
                    _mel_obj = self.get_interval_melody()
                    _mel_raw = self.get_interval_melody_notes()  # may contain None
                    _mel_durs = _mel_obj.get("durations", []) if _mel_obj else []
                    # Draw time signature (compás) after clef/key signature
                    _beats = _mel_obj.get("beats_per_bar", 4) if _mel_obj else 4
                    _ts_pt = max(18, int(line_space * 1.9))
                    _ts_half_w = max(12, int(_ts_pt * 0.42))
                    _ts_x = max(margin_x + 60.0, signature_end_x + 10 + _ts_half_w)
                    _ts_font = ("Helvetica", _ts_pt, "bold")
                    canvas.create_text(_ts_x, treble_top + line_space, text=str(_beats), fill="#ffffff", font=_ts_font)
                    canvas.create_text(_ts_x, treble_top + 3 * line_space, text="4", fill="#ffffff", font=_ts_font)
                    canvas.create_text(_ts_x, bass_top + line_space, text=str(_beats), fill="#ffffff", font=_ts_font)
                    canvas.create_text(_ts_x, bass_top + 3 * line_space, text="4", fill="#ffffff", font=_ts_font)
                    _mel_left = max(margin_x + 88, _ts_x + _ts_half_w + 18)
                    _mel_right = max(_mel_left + 1, right_x - 40)
                    _mel_total = len(_mel_raw)
                    _mel_step = max(22.0, (_mel_right - _mel_left) / max(1, _mel_total - 1)) if _mel_total > 1 else 40.0
                    _mel_x_map: list[float] = [_mel_left + i * _mel_step for i in range(_mel_total)]
                    _mel_dur_map: list[str] = [_mel_durs[i] if i < len(_mel_durs) else "q" for i in range(_mel_total)]
                    # Beam groups: consecutive sub-quarter notes within the same beat
                    _Q_t = 1000
                    _dur_t_map = {"w": 4*_Q_t, "h": 2*_Q_t, "q": _Q_t, "e": _Q_t//2, "et": _Q_t//3, "s": _Q_t//4}
                    _note_ticks: list[int] = []
                    for _d in _mel_dur_map:
                        _db2 = _d.rstrip(".")
                        _tv = _dur_t_map.get(_db2, _Q_t)
                        if _d.endswith("."):
                            _tv = _tv * 3 // 2
                        _note_ticks.append(_tv)
                    _beam_group_of: dict[int, int] = {}
                    _beam_groups_mel: list[list[int]] = []
                    _tp = 0
                    _bg_cur: list[int] = []
                    _bg_beat0 = 0
                    for _bni in range(_mel_total):
                        _bdb = _mel_dur_map[_bni].rstrip(".")
                        _is_sq = _bdb in ("e", "et", "s") and _mel_raw[_bni] is not None
                        _beat = _tp // _Q_t
                        if _is_sq:
                            if _bg_cur and _beat != _bg_beat0:
                                if len(_bg_cur) > 1:
                                    _gid = len(_beam_groups_mel)
                                    for _g in _bg_cur:
                                        _beam_group_of[_g] = _gid
                                    _beam_groups_mel.append(list(_bg_cur))
                                _bg_cur = []
                            if not _bg_cur:
                                _bg_beat0 = _beat
                            _bg_cur.append(_bni)
                        else:
                            if len(_bg_cur) > 1:
                                _gid = len(_beam_groups_mel)
                                for _g in _bg_cur:
                                    _beam_group_of[_g] = _gid
                                _beam_groups_mel.append(list(_bg_cur))
                            _bg_cur = []
                        _tp += _note_ticks[_bni]
                    if len(_bg_cur) > 1:
                        _gid = len(_beam_groups_mel)
                        for _g in _bg_cur:
                            _beam_group_of[_g] = _gid
                        _beam_groups_mel.append(list(_bg_cur))
                    _beam_stem_data: dict[int, tuple] = {}
                    # Bar lines: vertical lines at measure boundaries
                    _beats_per_bar_v = _mel_obj.get("beats_per_bar", 4) if _mel_obj else 4
                    _anacrusis_v = float(_mel_obj.get("anacrusis", 0) if _mel_obj else 0)
                    _bar_ticks_v = _beats_per_bar_v * _Q_t
                    _bar_run = int(-_anacrusis_v * _Q_t)
                    _bar_lines_x: list[float] = []
                    for _bni in range(_mel_total):
                        _prev_run = _bar_run
                        _bar_run += _note_ticks[_bni]
                        if _bni > 0 and (_prev_run // _bar_ticks_v) < (_bar_run // _bar_ticks_v):
                            _bar_lines_x.append((_mel_x_map[_bni - 1] + _mel_x_map[_bni]) / 2)
                    _bl_col = "#5a6a7a"
                    for _bx in _bar_lines_x:
                        canvas.create_line(_bx, treble_top, _bx, bass_top + 4 * line_space,
                                           fill=_bl_col, width=1)
                    # Build ordered (no Nones) and map ordered_idx → melody_idx
                    ordered = []
                    _ord_to_mel: dict[int, int] = {}
                    for _mi, _mn in enumerate(_mel_raw):
                        if _mn is not None:
                            _ord_to_mel[len(ordered)] = _mi
                            ordered.append(int(_mn))
                else:
                    ordered = sorted(display_notes)
                    chord_x = margin_x + max(110, min(w - margin_x - 70, (w - margin_x) * 0.45))
            generation_single_note: Optional[int] = None
            if self.generation_tab_active and len(self.generated_playing_notes) == 1:
                generation_single_note = next(iter(self.generated_playing_notes))
            if instrument_override:
                # Con una variante de guitarra seleccionada, el pentagrama
                # muestra directamente sus notas (frets reales, que pueden
                # incluir octavas que no están en generated_preview_notes);
                # el set de "sonando" debe coincidir o esas notas nunca se
                # resaltarían al pulsar Reproducir (p. ej. el Do agudo de
                # ciertas digitaciones de Do mayor).
                generation_rh_staff_notes: set[int] = {int(note) for note in set(self.guitar_selected_variation_notes)}
                generation_lh_staff_notes: set[int] = set()
            else:
                generation_rh_staff_notes = {int(note) for note in set(self.generated_preview_notes)}
                generation_lh_staff_notes = {
                    int(note - 12)
                    for note in set(self.generated_preview_notes)
                    if int(note - 12) >= 0
                }
            generation_staff_playing_rh_notes: set[int] = set()
            generation_staff_playing_lh_notes: set[int] = set()
            if self.generation_tab_active:
                for note in set(self.generated_playing_notes):
                    note_int = int(note)
                    if note_int in generation_lh_staff_notes and note_int not in generation_rh_staff_notes:
                        generation_staff_playing_lh_notes.add(note_int)
                    elif note_int in generation_rh_staff_notes:
                        generation_staff_playing_rh_notes.add(note_int)
                    elif note_int in generation_lh_staff_notes:
                        generation_staff_playing_lh_notes.add(note_int)
                    else:
                        generation_staff_playing_rh_notes.add(note_int)
            if self.generation_tab_active and self.instrument_view == "piano":
                hold_active = bool(self.generation_play_button_pressed or self.generation_play_space_pressed)
                if hold_active:
                    generation_staff_playing_lh_notes |= {
                        int(note - 12)
                        for note in set(generation_staff_playing_rh_notes)
                        if int(note - 12) in generation_lh_staff_notes
                    }
            elif self.generation_tab_active and self.instrument_view == "guitar":
                hold_active = bool(self.generation_play_button_pressed or self.generation_play_space_pressed)
                if hold_active:
                    generation_staff_playing_rh_notes |= set(generation_rh_staff_notes)
                    generation_staff_playing_lh_notes |= set(generation_lh_staff_notes)
            generation_staff_playing_notes: set[int] = (
                set(generation_staff_playing_rh_notes) | set(generation_staff_playing_lh_notes)
            )
            generation_note_label_y = treble_top - 30
            placed_treble_cols: dict[int, list[float]] = {}
            placed_bass_cols: dict[int, list[float]] = {}

            # Todas las notas se dibujan en el mismo tiempo (misma x) y en
            # posiciones diatonicas exactas (linea/espacio real del pentagrama).
            treble_bottom_line_diatonic = 4 * 7 + 2  # E4
            treble_top_line_diatonic = treble_bottom_line_diatonic + 8  # F5
            bass_bottom_line_diatonic = 2 * 7 + 4    # G2
            bass_top_line_diatonic = bass_bottom_line_diatonic + 8      # A3
            staff_step = line_space / 2.0
            for note_idx, note in enumerate(ordered):
                degree_idx = int(note_idx)
                scale_is_bass = False
                if self.scale_tab_active and note_idx < len(scale_staff_entries):
                    degree_idx = int(scale_staff_entries[note_idx][1])
                    scale_is_bass = bool(scale_staff_entries[note_idx][2])
                if note >= 60:
                    placed_cols = placed_treble_cols
                    if self.scale_tab_active and not scale_is_bass and degree_idx < len(scale_diatonic_indices):
                        diatonic_idx = scale_diatonic_indices[degree_idx]
                    else:
                        diatonic_idx = self._diatonic_index(note, prefer_flat_signature)
                    diatonic_steps = diatonic_idx - treble_bottom_line_diatonic
                    y = treble_top + 4 * line_space - diatonic_steps * staff_step
                    label_y_base = treble_top - 28
                    low_bound = treble_bottom_line_diatonic
                    high_bound = treble_top_line_diatonic
                    staff_base_y = treble_top + 4 * line_space
                else:
                    placed_cols = placed_bass_cols
                    diatonic_idx = self._diatonic_index(note, prefer_flat_signature)
                    diatonic_steps = diatonic_idx - bass_bottom_line_diatonic
                    y = bass_top + 4 * line_space - diatonic_steps * staff_step
                    label_y_base = treble_top - 28
                    low_bound = bass_bottom_line_diatonic
                    high_bound = bass_top_line_diatonic
                    staff_base_y = bass_top + 4 * line_space

                note_rx = max(8.0, line_space * 0.72)
                note_ry = line_space / 2.0
                # Apila por columnas: solo desplaza a la derecha si en la columna
                # actual hay solape. Asi una nota posterior puede volver a x base.
                overlap_threshold = max(1.0, (note_ry * 2.0) - 1.0)
                col = 0
                if self.scale_tab_active:
                    x = left_x + (degree_idx * step_x)
                elif _imel:
                    _mi = _ord_to_mel.get(note_idx, note_idx)
                    x = _mel_x_map[_mi]
                else:
                    while any(abs(y - prev_y) < overlap_threshold for prev_y in placed_cols.get(col, [])):
                        col += 1
                    x = chord_x + (col * note_rx * 1.8)
                    placed_cols.setdefault(col, []).append(y)

                # Lineas adicionales para notas fuera del pentagrama.
                ledger_half = int(max(20, note_rx + 11))
                ledger_lines_y: list[float] = []
                if diatonic_idx > high_bound:
                    top_even = diatonic_idx if (diatonic_idx % 2 == 0) else (diatonic_idx - 1)
                    for ledger_idx in range(high_bound + 2, top_even + 1, 2):
                        ledger_y = staff_base_y - (ledger_idx - low_bound) * staff_step
                        ledger_lines_y.append(ledger_y)
                elif diatonic_idx < low_bound:
                    bottom_even = diatonic_idx if (diatonic_idx % 2 == 0) else (diatonic_idx + 1)
                    for ledger_idx in range(low_bound - 2, bottom_even - 1, -2):
                        ledger_y = staff_base_y - (ledger_idx - low_bound) * staff_step
                        ledger_lines_y.append(ledger_y)

                # Color de la nota: calculado antes del simbolo de
                # alteracion para poder resaltar tambien el # / b / natural
                # con el mismo color cuando la nota esta pulsada/sonando.
                _dur_base = ""
                _is_hollow = False
                if self.scale_tab_active:
                    is_hovered = self.staff_hover_note == note
                    is_pressed = (
                        (note in self.staff_pressed_scale_notes)
                        or (note in self.scale_guitar_click_highlight_notes)
                        or (note in self.scale_guitar_drag_staff_notes)
                    )
                    is_current = self.scale_loop_active and self.scale_current_note == note
                    if is_hovered:
                        note_fill = "#49c6ff"
                        note_outline = "#ffffff"
                    elif is_pressed or is_current:
                        if self.scale_play_mode == "piano" and note in scale_bass_display_notes:
                            note_fill = "#ff6a00"
                            note_outline = "#ffd2a7"
                        else:
                            note_fill = "#39c5ff"
                            note_outline = "#ffffff"
                    else:
                        note_fill = ""
                        note_outline = "#d7dde7"
                elif self.generation_tab_active and note in self.generation_midi_held_notes:
                    # MIDI held notes in generation staff: gold/yellow highlight
                    note_fill = "#f3bf2f"
                    note_outline = "#d4a017"
                elif self.generation_tab_active and note in generation_staff_playing_lh_notes:
                    if self.instrument_view == "guitar":
                        note_fill = "#39c5ff"
                        note_outline = "#ffffff"
                    else:
                        note_fill = "#ff6a00"
                        note_outline = "#ffd2a7"
                elif self.generation_tab_active and note in generation_staff_playing_notes:
                    note_fill = "#39c5ff"
                    note_outline = "#ffffff"
                elif _imel:
                    _mi = _ord_to_mel.get(note_idx, note_idx)
                    _dur_base = _mel_dur_map[_mi].rstrip(".")
                    _is_hollow = _dur_base in ("w", "h")
                    _playing_idx = getattr(self, "interval_playing_idx", None)
                    if _playing_idx is not None and _mi == _playing_idx:
                        note_fill = self.color_accent
                        note_outline = self.color_accent
                    else:
                        note_fill = "" if _is_hollow else "#d7dde7"
                        note_outline = "#d7dde7"
                elif note in self.detection_extra_notes:
                    note_fill = "#bf2f2f"
                    note_outline = "#ff9a9a"
                else:
                    note_fill = ""
                    note_outline = "#d7dde7"
                # note_outline suele ser blanco tanto resaltada como no
                # (solo note_fill cambia de verdad, p.ej. azul/naranja al
                # pulsar), asi que hay que usar note_fill como color
                # distintivo del simbolo cuando la nota este resaltada.
                accidental_color = note_fill if note_fill else "#ffffff"

                # Alteraciones: misma altura que la nota natural + simbolo.
                note_pc = note % 12
                natural_pc_by_letter = [0, 2, 4, 5, 7, 9, 11]
                if self.scale_tab_active:
                    letter_idx = scale_letter_indices[degree_idx] if degree_idx < len(scale_letter_indices) else (diatonic_idx % 7)
                else:
                    letter_idx = diatonic_idx % 7
                natural_base_pc = natural_pc_by_letter[letter_idx]
                acc_note_pt = self._staff_accidental_font_pt(
                    int(line_space), prefer_flat=prefer_flat_signature
                )
                nat_pt = self._staff_natural_font_pt(int(line_space))
                if self.scale_tab_active:
                    # En escalas con muchas notas (p.ej. cromática, 13 notas)
                    # el hueco horizontal entre notas (step_x) puede ser mas
                    # pequeño que el desplazamiento normal del simbolo de
                    # alteracion. Se acota el tamaño de fuente al hueco
                    # disponible, pero el desplazamiento (acc_dx) nunca debe
                    # bajar de radio_de_la_nota + margen, o el simbolo cae
                    # encima de la propia cabeza de nota en vez de a su
                    # izquierda.
                    max_dx = max(9, int(step_x * 0.55))
                    acc_note_pt = max(9, min(acc_note_pt, int(max_dx / 1.12)))
                    nat_pt = max(9, min(nat_pt, int(max_dx / 1.12)))
                if self.scale_tab_active:
                    min_dx_over_note = int(note_rx + 4)
                    acc_dx_scale = max(min_dx_over_note, min(40, int(round(acc_note_pt * 1.12))))
                    acc_dx_nat = max(min_dx_over_note, min(38, int(round(nat_pt * 1.12))))
                else:
                    acc_dx_scale = max(22, min(40, int(round(acc_note_pt * 1.12))))
                    acc_dx_nat = max(20, min(38, int(round(nat_pt * 1.12))))
                if use_key_signature and natural_base_pc in signature_base_naturals and note_pc == natural_base_pc:
                    accidental_x = (x - acc_dx_nat) if self.scale_tab_active else (
                        (chord_x - acc_dx_nat - 6) if col > 0 else (x - acc_dx_nat)
                    )
                    canvas.create_text(
                        accidental_x,
                        y,
                        text="♮",
                        fill=accidental_color,
                        font=("Helvetica", nat_pt, "bold"),
                    )
                elif note_pc not in WHITE_PCS and (not use_key_signature or note_pc not in signature_pc_set):
                    accidental_x = (x - acc_dx_scale) if self.scale_tab_active else (
                        (chord_x - acc_dx_scale - 6) if col > 0 else (x - acc_dx_scale)
                    )
                    accidental_text = "♭" if prefer_flat_signature else "#"
                    accidental_font = ("Helvetica", acc_note_pt, "bold")
                    canvas.create_text(
                        accidental_x,
                        y,
                        text=accidental_text,
                        fill=accidental_color,
                        font=accidental_font,
                    )
                # Whole notes are wider; use thicker outline for hollow long notes in melody mode
                _oval_rx = note_rx * 1.2 if (_imel and _dur_base == "w") else note_rx
                _oval_w = 2.5 if (_imel and _is_hollow) else 2
                canvas.create_oval(
                    x - _oval_rx,
                    y - note_ry,
                    x + _oval_rx,
                    y + note_ry,
                    fill=note_fill,
                    outline=note_outline,
                    width=_oval_w,
                )
                if _imel:
                    _dur_full = _mel_dur_map[_mi]
                    _dur_base = _dur_full.rstrip(".")
                    _is_dotted = _dur_full.endswith(".")
                    _flag_count = 1 if _dur_base in ("e", "et") else (2 if _dur_base == "s" else 0)
                    _has_stem = _dur_base != "w"
                    _stem_mid = treble_top + 2 * line_space if note >= 60 else bass_top + 2 * line_space
                    _stem_up = y > _stem_mid
                    _stem_len = 3.5 * line_space
                    _stem_col = note_outline if note_outline else "#d7dde7"
                    if _has_stem:
                        if _stem_up:
                            _sx = x + note_rx - 1
                            _sy_end = y - _stem_len
                            canvas.create_line(_sx, y, _sx, _sy_end, fill=_stem_col, width=2.0)
                            if _flag_count > 0 and _mi in _beam_group_of:
                                _beam_stem_data[_mi] = (_sx, _sy_end, True, _flag_count, _stem_col)
                            else:
                                for _fi in range(_flag_count):
                                    _fy0 = _sy_end + _fi * line_space * 0.55
                                    _fw = line_space * 0.52
                                    _fh = line_space * 1.75
                                    canvas.create_line(
                                        _sx, _fy0,
                                        _sx + _fw * 0.9, _fy0 + _fh * 0.07,
                                        _sx + _fw, _fy0 + _fh * 0.22,
                                        _sx + _fw * 0.65, _fy0 + _fh * 0.62,
                                        _sx + _fw * 0.1, _fy0 + _fh * 1.0,
                                        fill=_stem_col, width=2.0, smooth=True,
                                    )
                        else:
                            _sx = x - note_rx + 1
                            _sy_end = y + _stem_len
                            canvas.create_line(_sx, y, _sx, _sy_end, fill=_stem_col, width=2.0)
                            if _flag_count > 0 and _mi in _beam_group_of:
                                _beam_stem_data[_mi] = (_sx, _sy_end, False, _flag_count, _stem_col)
                            else:
                                for _fi in range(_flag_count):
                                    _fy0 = _sy_end - _fi * line_space * 0.55
                                    _fw = line_space * 0.52
                                    _fh = line_space * 1.75
                                    canvas.create_line(
                                        _sx, _fy0,
                                        _sx + _fw * 0.9, _fy0 - _fh * 0.07,
                                        _sx + _fw, _fy0 - _fh * 0.22,
                                        _sx + _fw * 0.65, _fy0 - _fh * 0.62,
                                        _sx + _fw * 0.1, _fy0 - _fh * 1.0,
                                        fill=_stem_col, width=2.0, smooth=True,
                                    )
                    # Augmentation dot
                    if _is_dotted:
                        _dr = max(2.0, line_space * 0.18)
                        _dx = x + note_rx + _dr * 2.5
                        _dy = y - note_ry * 0.4 if (diatonic_idx % 2 == 0) else y
                        canvas.create_oval(_dx - _dr, _dy - _dr, _dx + _dr, _dy + _dr,
                                           fill=_stem_col, outline=_stem_col)
                if self.generation_tab_active:
                    self.staff_generation_note_regions.append((note, x, y, note_rx, note_ry))
                    if generation_single_note is not None and note == generation_single_note:
                        generation_note_label = generation_name_map.get(note, self.note_name(note, with_octave=False))
                        canvas.create_text(
                            x,
                            generation_note_label_y,
                            text=generation_note_label,
                            fill="#6fe0ff",
                            font=("Helvetica", 15, "bold"),
                        )
                for ledger_y in ledger_lines_y:
                    canvas.create_line(x - ledger_half, ledger_y, x + ledger_half, ledger_y, fill="#bfbfbf", width=1)
                if self.scale_tab_active:
                    label_y = label_y_base
                    label_half_w = 0.0
                    if note >= 60:
                        if degree_idx < len(scale_label_names):
                            label_text = str(scale_label_names[degree_idx])
                        else:
                            label_text = self.note_name(note, with_octave=False)
                        is_label_hl = degree_idx in highlighted_scale_degrees
                        is_current_label = degree_idx in current_scale_degrees
                        if is_current_label:
                            label_fill = "#6fe0ff"
                        elif is_label_hl:
                            label_fill = "#7ed1ff"
                        else:
                            label_fill = "#d4d8df"
                        canvas.create_text(
                            x,
                            label_y,
                            text=label_text,
                            fill=label_fill,
                            font=("Helvetica", 14, "bold" if (is_label_hl or is_current_label) else "normal"),
                        )
                        label_half_w = max(12.0, 4.0 * len(label_text) + 7.0)
                    self.staff_scale_note_regions.append((note, x, y, note_rx, note_ry, label_y, label_half_w, degree_idx))

        # Interval melody: draw beams for grouped sub-quarter notes
        if getattr(self, "interval_tab_active", False) and getattr(self, "interval_melody_mode", False) and "_beam_groups_mel" in locals() and _beam_groups_mel:
            for _bgrp in _beam_groups_mel:
                _bdata = [_beam_stem_data[_bmi] for _bmi in _bgrp if _bmi in _beam_stem_data]
                if len(_bdata) < 2:
                    continue
                _n_prim = min(bd[3] for bd in _bdata)
                _bw_beam = 3.0
                for _bbar in range(_n_prim):
                    _boff = _bbar * line_space * 0.32
                    _bx0, _bsy0 = _bdata[0][0], _bdata[0][1]
                    _bx1, _bsy1 = _bdata[-1][0], _bdata[-1][1]
                    _stem_up_b = _bdata[0][2]
                    if _stem_up_b:
                        _bsy0 += _boff
                        _bsy1 += _boff
                    else:
                        _bsy0 -= _boff
                        _bsy1 -= _boff
                    canvas.create_line(_bx0, _bsy0, _bx1, _bsy1, fill=_bdata[0][4], width=_bw_beam)
                # Draw secondary beam stubs for notes with more flags than the primary count
                _bgrp_last = len(_bgrp) - 1
                for _bsd_idx, _bmi in enumerate(_bgrp):
                    if _bmi not in _beam_stem_data:
                        continue
                    _bsd = _beam_stem_data[_bmi]
                    _extra = _bsd[3] - _n_prim
                    if _extra <= 0:
                        continue
                    _bx_n = _bsd[0]
                    _by_n = _bsd[1]
                    _sup = _bsd[2]
                    _stub_w = max(line_space * 1.2, abs(_bdata[-1][0] - _bdata[0][0]) * 0.45, 14.0)
                    _stub_dir = -1 if _bsd_idx == _bgrp_last else 1
                    for _be in range(_extra):
                        _stub_off = (_n_prim + _be) * line_space * 0.32
                        if _sup:
                            _bsy_s = _by_n + _stub_off
                        else:
                            _bsy_s = _by_n - _stub_off
                        _stub_x, _stub_y = self._parallel_beam_endpoint(
                            _bx_n,
                            _bsy_s,
                            _bx_n + _stub_dir * _stub_w,
                            _bdata[0][0],
                            _bdata[0][1],
                            _bdata[-1][0],
                            _bdata[-1][1],
                        )
                        canvas.create_line(_bx_n, _bsy_s, _stub_x, _stub_y,
                                           fill=_bsd[4], width=_bw_beam)

        # Interval melody: draw rests for None positions
        if getattr(self, "interval_tab_active", False) and getattr(self, "interval_melody_mode", False) and "_mel_raw" in locals():
            for _mi, _mn in enumerate(_mel_raw):
                if _mn is None and _mi < len(_mel_x_map):
                    _rx = _mel_x_map[_mi]
                    _rdur = _mel_dur_map[_mi].rstrip(".")
                    self._draw_rest_symbol(canvas, _rx, treble_top + 2 * line_space,
                                           _rdur, line_space, "#768496", treble_top)

        # Círculo de quintas: ayuda de interacción (como el pie bajo el pentagrama en web), no armadura.
        if getattr(self, "circle_fifths_tab_active", False):
            hint = self.tr("circle_hint")
            _circle_help_pt = 12
            _char_px = 5.5 * (_circle_help_pt / 10.0)
            max_chars = max(24, int(max(1.0, w - 48) / _char_px))
            lines = textwrap.wrap(hint, width=max_chars) or [hint]
            y = float(h) - 8.0
            line_step = 17.0
            for line in reversed(lines):
                canvas.create_text(
                    w / 2,
                    y,
                    text=line,
                    fill="#a8a8a8",
                    font=("Helvetica", _circle_help_pt, "italic"),
                    anchor="s",
                )
                y -= line_step
        elif (
            not self.generation_tab_active
            and not self.scale_tab_active
            and not getattr(self, "interval_tab_active", False)
        ):
            canvas.create_text(
                w / 2,
                h - 14,
                text=self.tr("staff_shift_hint"),
                fill="#a8a8a8",
                font=("Helvetica", 10, "italic"),
            )
        elif self.scale_tab_active and self.scale_play_mode == "guitar":
            canvas.create_text(
                w / 2,
                h - 14,
                text=self.tr("staff_scale_guitar_shift_hint"),
                fill="#a8a8a8",
                font=("Helvetica", 10, "italic"),
            )
