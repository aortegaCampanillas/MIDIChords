from __future__ import annotations

import time
import tkinter as tk
from midichords.core.music_theory import WHITE_PCS


class RenderMixin:
    def _instrument_display_notes(self) -> set[int]:
        if self.tuner_tab_active:
            notes: set[int] = set()
            if self.tuner_detected_note_midi is not None:
                notes.add(int(self.tuner_detected_note_midi))
            if self.tuner_reference_note is not None:
                notes.add(int(self.tuner_reference_note))
            if notes:
                return notes
        if self.instrument_view == "guitar" and self.guitar_selected_variation_notes:
            return set(self.guitar_selected_variation_notes)
        if self.generation_tab_active:
            return set(self.generated_preview_notes)
        if self.scale_tab_active:
            notes = set(self.active_notes) | set(self.staff_pressed_scale_notes)
            if self.scale_loop_active and self.scale_current_note is not None:
                notes.add(self.scale_current_note)
            return notes
        return self._current_detection_notes()
    def redraw_guitar_fretboard(self) -> None:
        canvas = self.guitar_canvas
        canvas.delete("all")
        self.scale_guitar_tonic_regions = []
        self.scale_guitar_note_regions = []
        self.guitar_generation_note_regions = []
        w = max(720, canvas.winfo_width())
        h = max(180, canvas.winfo_height())
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
        board_y1 = 24
        board_y2 = h - 14
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
            canvas.create_text(strings_x1 - 22, y, text=name, fill="#111", font=("Helvetica", 10, "bold"))

        if self.scale_tab_active and self.scale_play_mode == "guitar":
            scale_pcs = {n % 12 for n in self.scale_preview_notes}
            if not scale_pcs:
                return
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
                        text=self.note_name(note, with_octave=False),
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
        if self.generation_tab_active and self.instrument_view == "piano" and self.generated_playing_notes:
            display_active_notes = set(self.generated_playing_notes)
        if self.scale_tab_active:
            name_overlay_notes = set(self.active_notes) | set(self.staff_pressed_scale_notes)
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
        scale_pc_set = {note % 12 for note in self.scale_preview_notes} if self.scale_tab_active else set()
        scale_tonic_pc = self.scale_tonic_pc
        current_scale_note = self.scale_current_note if (self.scale_tab_active and self.scale_loop_active) else None
        now = time.monotonic()
        self.blocked_note_until = {n: t for n, t in self.blocked_note_until.items() if t > now}

        w = max(100, canvas.winfo_width())
        h = max(156, canvas.winfo_height())

        low_note, high_note = 21, 108
        notes = list(range(low_note, high_note + 1))
        white_notes = [n for n in notes if (n % 12) in WHITE_PCS]
        white_w = w / len(white_notes)
        key_top = 28
        key_bottom = h - 6
        black_h = int((key_bottom - key_top) * 0.58)

        white_index: dict[int, int] = {}
        idx = 0
        for note in notes:
            if (note % 12) in WHITE_PCS:
                white_index[note] = idx
                idx += 1

        # Fondo y marco base del teclado.
        canvas.create_rectangle(0, 0, w, h, fill="#1f1f1f", outline="")
        canvas.create_rectangle(0, key_top, w, key_bottom, fill="#d8d8d8", outline="#b7b7b7", width=1)

        for note in notes:
            if (note % 12) not in WHITE_PCS:
                continue
            i = white_index[note]
            x1 = i * white_w
            x2 = (i + 1) * white_w

            if self.scale_tab_active and note == current_scale_note:
                top_fill = "#65b7ff"
                base_fill = "#65b7ff"
            elif note in display_active_notes:
                top_fill = "#4da3ea"
                base_fill = "#4da3ea"
            else:
                top_fill = "#f9f9f5"
                base_fill = "#ecebe7"

            canvas.create_rectangle(x1, key_top, x2, key_bottom, fill=base_fill, outline="#9a9a9a", width=1)
            canvas.create_rectangle(x1 + 1, key_top + 1, x2 - 1, key_top + (key_bottom - key_top) * 0.42, fill=top_fill, outline="")
            canvas.create_line(x1 + 1, key_bottom - 2, x2 - 1, key_bottom - 2, fill="#c8c8c8")
            show_label = self.config_data.get("show_keyboard_note_labels", False) and not self.scale_tab_active
            if show_label:
                label_color = "#0b2540" if note in display_active_notes else "#5f5f5f"
                canvas.create_text(
                    (x1 + x2) / 2,
                    key_bottom - 16,
                    text=self.note_name(note, with_octave=False),
                    fill=label_color,
                    font=("Helvetica", 8, "bold"),
                )
            if self.scale_tab_active and (note % 12) in scale_pc_set:
                circle_fill = "#32d74b" if (note % 12) == scale_tonic_pc else "#f6b60b"
                circle_text = self.note_name(note, with_octave=False)
                cx = (x1 + x2) / 2
                cy = key_bottom - 28
                r = max(11, min(17, white_w * 0.28))
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=circle_fill, outline="")
                canvas.create_text(cx, cy, text=circle_text, fill="#101010", font=("Helvetica", 11, "bold"))
            if note in name_overlay_notes:
                canvas.create_text(
                    (x1 + x2) / 2,
                    5,
                    text=self.note_name(note, with_octave=False),
                    fill="#ffffff",
                    font=("Helvetica", 11, "bold"),
                    anchor="n",
                )
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

            if self.scale_tab_active and note == current_scale_note:
                top = "#72c1ff"
                mid = "#388fdb"
                low = "#1c5f99"
            elif note in display_active_notes:
                top = "#0078d7"
                mid = "#0078d7"
                low = "#0078d7"
            else:
                top = "#3a3a3a"
                mid = "#161616"
                low = "#050505"

            canvas.create_rectangle(x1, key_top, x2, key_top + black_h, fill=mid, outline="#000000", width=1)
            canvas.create_rectangle(x1 + 1, key_top + 1, x2 - 1, key_top + black_h * 0.45, fill=top, outline="")
            canvas.create_rectangle(x1 + 1, key_top + black_h * 0.75, x2 - 1, key_top + black_h - 1, fill=low, outline="")
            canvas.create_line(x1 + 1, key_top + black_h - 3, x2 - 1, key_top + black_h - 3, fill="#2a2a2a")
            if self.scale_tab_active and (note % 12) in scale_pc_set:
                circle_fill = "#32d74b" if (note % 12) == scale_tonic_pc else "#f6b60b"
                circle_text = self.note_name(note, with_octave=False)
                cx = (x1 + x2) / 2
                cy = key_top + black_h - 22
                r = max(9, min(13, black_w * 0.28))
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=circle_fill, outline="")
                canvas.create_text(cx, cy, text=circle_text, fill="#101010", font=("Helvetica", 8, "bold"))
            if note in name_overlay_notes:
                canvas.create_text(
                    (x1 + x2) / 2,
                    5,
                    text=self.note_name(note, with_octave=False),
                    fill="#ffffff",
                    font=("Helvetica", 10, "bold"),
                    anchor="n",
                )
            if note in self.blocked_note_until:
                self._draw_forbidden_icon(canvas, (x1 + x2) / 2, key_top + black_h * 0.5, 7)
            self.black_key_regions.append((note, x1, key_top, x2, key_top + black_h))

        # Franja inferior para dar profundidad y etiquetas de octava.
        canvas.create_rectangle(0, key_bottom, w, h, fill="#101010", outline="")
        if not self.config_data.get("show_keyboard_note_labels", False) and not self.scale_tab_active:
            for note in white_notes:
                if note % 12 != 0:  # marcar C de cada octava
                    continue
                i = white_index[note]
                x = i * white_w + white_w * 0.5
                octave = note // 12 - 1
                canvas.create_text(x, h - 5, text=f"C{octave}", anchor="s", fill="#8f8f8f", font=("Helvetica", 9))
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
        if instrument_override:
            display_notes_list = []
            display_notes = set(self.guitar_selected_variation_notes)
        elif self.scale_tab_active:
            display_notes_list = list(self.scale_preview_notes)
            display_notes = set(display_notes_list)
        else:
            display_notes_list = []
            display_notes = self.generated_preview_notes if self.generation_tab_active else self._current_detection_notes()

        w = max(300, canvas.winfo_width())
        h = max(260, canvas.winfo_height())

        margin_x = 72
        right_x = w - 20
        line_space = min(22, max(11, h // 24))
        vertical_shift = int(2 * line_space)
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

        canvas.create_text(108, treble_top + line_space * 1.65, text="𝄞", font=("Times New Roman", 64), fill="#ffffff")
        canvas.create_text(108, bass_top + line_space * 1.65, text="𝄢", font=("Times New Roman", 58), fill="#ffffff")

        if not display_notes:
            canvas.create_text(
                w / 2,
                min(h - 48, bass_top + 5.6 * line_space),
                text=self.tr("staff_no_active_notes"),
                fill="#cfcfcf",
                font=("Helvetica", 13, "italic"),
            )
        else:
            if self.scale_tab_active:
                ordered = display_notes_list
                left_x = margin_x + 88
                right_limit = max(left_x + 1, right_x - 40)
                step_x = max(18.0, (right_limit - left_x) / max(1, len(ordered) - 1))
            else:
                ordered = sorted(display_notes)
                chord_x = margin_x + max(110, min(w - margin_x - 70, (w - margin_x) * 0.45))
            generation_single_note: Optional[int] = None
            if self.generation_tab_active and len(self.generated_playing_notes) == 1:
                generation_single_note = next(iter(self.generated_playing_notes))
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
                if note >= 60:
                    placed_cols = placed_treble_cols
                    diatonic_idx = self._diatonic_index(note)
                    diatonic_steps = diatonic_idx - treble_bottom_line_diatonic
                    y = treble_top + 4 * line_space - diatonic_steps * staff_step
                    label_y_base = treble_top - 28
                    low_bound = treble_bottom_line_diatonic
                    high_bound = treble_top_line_diatonic
                    staff_base_y = treble_top + 4 * line_space
                else:
                    placed_cols = placed_bass_cols
                    diatonic_idx = self._diatonic_index(note)
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
                    x = left_x + (note_idx * step_x)
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

                # Sostenidos: misma altura que la nota natural + simbolo #.
                if (note % 12) not in WHITE_PCS:
                    sharp_x = (x - 24) if self.scale_tab_active else ((chord_x - 34) if col > 0 else (x - 34))
                    canvas.create_text(
                        sharp_x,
                        y,
                        text="#",
                        fill="#ffffff",
                        font=("Helvetica", 18, "bold"),
                    )
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
                    elif is_pressed:
                        note_fill = "#2faeff"
                        note_outline = "#ffffff"
                    elif is_current:
                        note_fill = "#2fb8ff"
                        note_outline = "#ffffff"
                    else:
                        note_fill = "#000000"
                        note_outline = "#ffffff"
                elif self.generation_tab_active and note in self.generated_playing_notes:
                    note_fill = "#2faeff"
                    note_outline = "#ffffff"
                else:
                    note_fill = "#000000"
                    note_outline = "#ffffff"
                canvas.create_oval(
                    x - note_rx,
                    y - note_ry,
                    x + note_rx,
                    y + note_ry,
                    fill=note_fill,
                    outline=note_outline,
                    width=2,
                )
                if self.generation_tab_active:
                    self.staff_generation_note_regions.append((note, x, y, note_rx, note_ry))
                    if generation_single_note is not None and note == generation_single_note:
                        canvas.create_text(
                            x,
                            generation_note_label_y,
                            text=self.note_name(note, with_octave=False),
                            fill="#6fe0ff",
                            font=("Helvetica", 15, "bold"),
                        )
                for ledger_y in ledger_lines_y:
                    canvas.create_line(x - ledger_half, ledger_y, x + ledger_half, ledger_y, fill="#bfbfbf", width=1)
                if self.scale_tab_active:
                    label_text = self.note_name(note, with_octave=False)
                    label_y = label_y_base
                    is_label_hl = (
                        (self.staff_hover_note == note)
                        or (note in self.staff_pressed_scale_notes)
                        or (note in self.scale_guitar_click_highlight_notes)
                        or (note in self.scale_guitar_drag_staff_notes)
                    )
                    is_current_label = self.scale_loop_active and self.scale_current_note == note
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
                    self.staff_scale_note_regions.append((note, x, y, note_rx, note_ry, label_y, label_half_w))

        if not self.generation_tab_active and not self.scale_tab_active:
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
