from __future__ import annotations

import midichords.qt.tk_compat as tk
import time
from midichords.core.music_theory import SCALE_PATTERNS, SCALE_BASIC_NAMES, ScalePattern
from midichords.core.tomplay_fingerings import get_fingering_for_scale
from midichords.ui.widgets_qt import GrayRoundedButton


class ScalesMixin:
    def _spelled_scale_note_names(
        self,
        root_midi: int,
        intervals: list[int],
        tonic_pc: int,
        with_octave: bool = True,
        prefer_flats_override: bool | None = None,
    ) -> list[str]:
        language = str(self.config_data.get("language", "es"))
        letter_names = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] if language == "es" else ["C", "D", "E", "F", "G", "A", "B"]
        base_pcs = [0, 2, 4, 5, 7, 9, 11]

        pattern = self._resolve_scale_pattern()
        is_minor = self._scale_prefers_minor_signature(str(pattern.name))
        tie_from_ui = str(self.config_data.get("note_accidental", "sharp")) == "flat"
        _count, prefer_flats = self._key_signature_count_for_tonic(
            tonic_pc, is_minor, tie_prefer_flats=tie_from_ui
        )
        if prefer_flats_override is not None:
            prefer_flats = bool(prefer_flats_override)

        if prefer_flats:
            tonic_letter_map = {
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
            tonic_letter_map = {
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
        tonic_letter = tonic_letter_map.get(int(tonic_pc) % 12, 0)

        names: list[str] = []
        for idx, interval in enumerate(intervals):
            midi_note = int(root_midi + interval)
            target_pc = midi_note % 12
            letter_idx = (tonic_letter + idx) % 7
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
                # Fallback for unusual cases.
                names.append(self.note_name(midi_note, with_octave=with_octave))
                continue

            name = f"{letter_names[letter_idx]}{accidental}"
            if with_octave:
                octave = midi_note // 12 - 1
                name = f"{name}{octave}"
            names.append(name)
        return names

    def _set_scale_play_mode(self, mode: str) -> None:
        previous_metronome_only = self.scale_metronome_only
        if mode == "metronome":
            self.scale_metronome_only = not self.scale_metronome_only
        elif mode in {"piano", "guitar"}:
            self.scale_play_mode = mode
        else:
            self.scale_play_mode = "piano"
        self.config_data["scale_play_mode"] = self.scale_play_mode
        self.config_data["scale_instrument_mode"] = self.scale_play_mode
        self.config_data["scale_metronome_only"] = self.scale_metronome_only
        self.save_config()
        self._refresh_scale_preview()
        self._refresh_scale_transport_styles()
        self._refresh_scale_instrument_view()
        self._refresh_scale_octave_buttons()
        self._refresh_scale_fingering_buttons()
        if (
            self.scale_loop_active
            and (not previous_metronome_only)
            and self.scale_metronome_only
            and self.scale_current_note is not None
        ):
            # Cambio en caliente: mantener el loop, pero apagar la nota sostenida actual.
            self.stop_note(self.scale_current_note)
            self.scale_playing_notes.discard(self.scale_current_note)

    def _set_scale_octaves(self, octaves: int) -> None:
        """Cambia el número de octavas a reproducir en escalas (piano)."""
        octaves = max(1, min(3, int(octaves)))
        self.scale_octaves = octaves
        self._refresh_scale_preview()
        self._refresh_scale_octave_buttons()
        if self.scale_loop_active:
            # Detener el loop actual y reiniciar con las nuevas notas
            self._stop_scale_playback()
            self._play_scale()
        if self.scale_tab_active:
            self.update_music_views()
        # Guardar la preferencia
        self.config_data["scale_octaves"] = self.scale_octaves
        self.save_config()

    def _refresh_scale_octave_buttons(self) -> None:
        """Actualiza el estado visual de los botones de octavas."""
        if not hasattr(self, "scale_octave_buttons"):
            return
        is_piano = self.scale_play_mode == "piano"
        muted = "#666e7a"
        for idx, btn in enumerate(self.scale_octave_buttons):
            btn.set_selected(idx + 1 == self.scale_octaves)
            btn.set_enabled(is_piano)
        if hasattr(self, "scale_octave_selector_label"):
            self.scale_octave_selector_label.configure(fg=self.color_text if is_piano else muted)

    def _set_scale_fingering(self, hand: str) -> None:
        """Cambia la mano de digitación (none, right, left)."""
        was_active = self.scale_fingering_hand is not None
        self.scale_fingering_hand = hand if hand != "none" else None
        now_active = self.scale_fingering_hand is not None
        self.config_data["scale_fingering_hand"] = hand
        self.save_config()
        self._refresh_scale_fingering_buttons()
        # Only resize the canvas when toggling fingering on/off, not when switching hands.
        if was_active != now_active:
            # Same pack → redraw → fit sequence as the guitar→piano switch; the
            # canvas must be visible when _fit_instrument_panel_height runs.
            try:
                self.keyboard_qscroll.pack_forget()
            except Exception:
                pass
            self._refresh_scale_instrument_view()
            return
        self.redraw_keyboard()

    def _refresh_scale_fingering_buttons(self) -> None:
        """Actualiza el estado de los radio buttons de digitación."""
        if not hasattr(self, "scale_fingering_radios"):
            return
        is_piano = self.scale_play_mode == "piano"
        muted = "#666e7a"
        state = "normal" if is_piano else "disabled"
        current = "none" if self.scale_fingering_hand is None else self.scale_fingering_hand
        self.scale_fingering_var.set(current)
        for rb in self.scale_fingering_radios:
            rb.configure(state=state)
        if hasattr(self, "scale_fingering_label"):
            self.scale_fingering_label.configure(fg=self.color_text if is_piano else muted)

    def _get_scale_fingerings(self) -> dict[int, int]:
        """Obtiene digitaciones para las notas actuales de escala.

        Returns: {midi_note: finger_number} mapping
        """
        if self.scale_fingering_hand is None:
            return {}

        pattern = self._resolve_scale_pattern()
        sorted_notes = sorted(set(self.scale_preview_notes))
        _name_map = {
            "ionian": "ionian_mode",
            "dorian": "dorian_mode",
            "phrygian": "phrygian_mode",
            "lydian": "lydian_mode",
            "mixolydian": "mixolydian_mode",
            "aeolian": "aeolian_mode",
            "locrian": "locrian_mode",
            "harmonic minor": "harmonic_minor",
            "melodic minor": "melodic_minor",
            "natural minor": "natural_minor",
        }
        scale_type = _name_map.get(pattern.name.lower(), pattern.name.lower().replace(" ", "_"))
        fingerings = get_fingering_for_scale(
            scale_type,
            self.scale_tonic_pc,
            self.scale_fingering_hand,
            count=len(sorted_notes)
        )

        result = {}
        for idx, midi_note in enumerate(sorted_notes):
            if idx < len(fingerings):
                result[midi_note] = fingerings[idx]

        return result

    def _refresh_scale_transport_styles(self) -> None:
        self._refresh_scale_metronome_volume_visibility()
        if self.scale_transport_buttons_are_images:
            panel_bg = self.cget("background")
            selected_hl = "#f3bf2f"
            normal_hl = panel_bg
            def style_button(widget: tk.Widget, selected: bool) -> None:
                if selected:
                    widget.configure(
                        bg="#343a44",
                        relief=tk.SUNKEN,
                        bd=3,
                        padx=7,
                        pady=5,
                        highlightbackground=selected_hl,
                        highlightcolor=selected_hl,
                        highlightthickness=1,
                    )
                else:
                    widget.configure(
                        bg=panel_bg,
                        relief=tk.FLAT,
                        bd=2,
                        highlightbackground=normal_hl,
                        highlightcolor=normal_hl,
                        highlightthickness=0,
                        padx=6,
                        pady=4,
                    )

            style_button(self.scale_mode_piano_btn, self.scale_play_mode == "piano")
            style_button(self.scale_mode_guitar_btn, self.scale_play_mode == "guitar")
            style_button(self.scale_mode_metronome_btn, self.scale_metronome_only)
            return
        self.scale_mode_piano_btn.set_selected(self.scale_play_mode == "piano")
        self.scale_mode_guitar_btn.set_selected(self.scale_play_mode == "guitar")
        self.scale_mode_metronome_btn.set_selected(self.scale_metronome_only)
    def _refresh_scale_metronome_volume_visibility(self) -> None:
        if not hasattr(self, "scale_metronome_volume_frame"):
            return
        if self.scale_metronome_only:
            self.scale_metronome_volume_frame.grid(row=0, column=4, sticky="ew", padx=(8, 0))
        else:
            self.scale_metronome_volume_frame.grid_remove()
    def _set_scale_transport_icon_pressed(self, mode: str, pressed: bool) -> None:
        if not self.scale_transport_buttons_are_images:
            return
        if mode == "piano":
            widget = self.scale_mode_piano_btn
        elif mode == "guitar":
            widget = self.scale_mode_guitar_btn
        else:
            widget = self.scale_mode_metronome_btn
        if pressed:
            widget.configure(
                bg="#3b424d",
                relief=tk.SUNKEN,
                bd=4,
                padx=7,
                pady=5,
                highlightbackground="#f3bf2f",
                highlightcolor="#f3bf2f",
                highlightthickness=1,
            )
        else:
            widget.configure(padx=6, pady=4)
            self._refresh_scale_transport_styles()
    def _refresh_scale_instrument_view(self) -> None:
        if not self.scale_tab_active:
            return
        self.guitar_variations_frame.pack_forget()
        self.guitar_handedness_combo.pack_forget()
        if self.scale_play_mode == "guitar":
            self.keyboard_qscroll.pack_forget()
            try:
                self.guitar_canvas.setFixedHeight(196)
                self.guitar_canvas.setMinimumHeight(196)
            except Exception:
                pass
            self.guitar_canvas.pack(fill=tk.X, expand=False)
            self._fit_instrument_panel_height()
            self.redraw_guitar_fretboard()
        else:
            self.guitar_canvas.pack_forget()
            self.keyboard_qscroll.pack(fill=tk.X, expand=False)
            self._fit_instrument_panel_height()
            self.redraw_keyboard()
    def _on_scale_transport_icon_press(self, _event: tk.Event, mode: str) -> None:
        self.scale_transport_pressed_mode = mode
        self._set_scale_transport_icon_pressed(mode, True)
    def _on_scale_transport_icon_release(self, _event: tk.Event, mode: str) -> None:
        self._set_scale_transport_icon_pressed(mode, False)
        self.scale_transport_pressed_mode = None
        self._set_scale_play_mode(mode)
    def _scale_guitar_note_at_position(self, x: float, y: float) -> Optional[int]:
        for note, x1, y1, x2, y2 in self.scale_guitar_note_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return int(note)
        return None
    def _activate_scale_guitar_drag_note(self, note: int) -> None:
        self.scale_guitar_drag_exact_notes = {int(note)}
        self.audio_engine.pluck_guitar_note(int(note), velocity=106, duration_seconds=1.1)
        staff_note = self._scale_staff_note_for_pitch(int(note))
        self.scale_guitar_drag_staff_notes.clear()
        if staff_note is not None:
            self.scale_guitar_drag_staff_notes = {staff_note}
        self.redraw_guitar_fretboard()
        self.redraw_staff()
        self.redraw_keyboard()
    def _resolve_scale_pattern(self) -> ScalePattern:
        for pattern in SCALE_PATTERNS:
            if pattern.name == self.scale_pattern_name:
                return pattern
        return SCALE_PATTERNS[0]

    def _get_scale_notes_for_octaves(self, notes_midi: list[int], octaves: int) -> list[int]:
        """Expande una lista de notas de una octava a múltiples octavas.

        Si octaves=1, retorna las notas sin cambios.
        Si octaves=2, añade la octava baja a la izquierda (notas - 12).
        Si octaves=3, añade octavas baja y alta (notas - 12 y notas + 12).
        """
        if not notes_midi or octaves <= 1:
            return notes_midi

        result = set(notes_midi)

        if octaves >= 2:
            for note in notes_midi:
                if note - 12 >= 0:
                    result.add(note - 12)

        if octaves >= 3:
            for note in notes_midi:
                result.add(note + 12)

        return sorted(result)
    def _refresh_scale_preview(self) -> None:
        # Inicializar scale_octaves si no existe
        if not hasattr(self, "scale_octaves"):
            self.scale_octaves = 1

        pattern = self._resolve_scale_pattern()
        tonic_name = self.note_name(self.scale_tonic_pc, with_octave=False)
        localized_scale_name = self.scale_name(pattern.name)
        if hasattr(self, "scale_tonic_combo"):
            self._update_scale_tonic_combo()
        if hasattr(self, "scale_type_combo"):
            self._update_scale_type_combo()
        if hasattr(self, "scale_name_var"):
            self.scale_name_var.set(f"{tonic_name} {localized_scale_name}")

        default_root_midi = 60 + self.scale_tonic_pc
        if self.scale_guitar_start_note is None or (self.scale_guitar_start_note % 12) != self.scale_tonic_pc:
            self.scale_guitar_start_note = default_root_midi
        root_midi = self.scale_guitar_start_note if self.scale_play_mode == "guitar" else default_root_midi
        base_notes = [root_midi + interval for interval in pattern.intervals]

        # scale_base_notes: always single-octave (used for staff display)
        self.scale_base_notes: list[int] = base_notes
        # Expandir notas según el selector de octavas (solo en modo piano)
        if self.scale_play_mode == "piano":
            self.scale_preview_notes = self._get_scale_notes_for_octaves(base_notes, self.scale_octaves)
        else:
            self.scale_preview_notes = base_notes

        if self.scale_preview_notes:
            spelled = self._spelled_scale_note_names(
                root_midi=root_midi,
                intervals=list(pattern.intervals),
                tonic_pc=self.scale_tonic_pc,
                with_octave=True,
                prefer_flats_override=(self.note_accidental == "flat"),
            )
            self.scale_notes_var.set(" - ".join(spelled))
            self.scale_intervals_var.set(self.format_intervals(set(self.scale_preview_notes)))
        else:
            self.scale_notes_var.set("-")
            self.scale_intervals_var.set("-")

    def _update_scale_tonic_combo(self) -> None:
        if not hasattr(self, "scale_tonic_combo"):
            return
        options = [self.note_name(pc, with_octave=False) for pc in range(12)]
        self._scale_tonic_label_to_pc = {self.note_name(pc, with_octave=False): pc for pc in range(12)}
        self.scale_tonic_combo.configure(values=options)
        self.scale_tonic_var.set(self.note_name(self.scale_tonic_pc, with_octave=False))

    def _scale_type_aliases(self) -> dict[str, str]:
        language = str(self.config_data.get("language", "es"))
        if language == "es":
            return {"Ionian": "Mayor", "Aeolian": "Menor Natural", "Super Locrian": "Alterada"}
        return {"Ionian": "Major", "Aeolian": "Natural Minor", "Super Locrian": "Altered"}

    def _scale_type_display_label(self, pattern_name: str) -> str:
        alias = self._scale_type_aliases().get(pattern_name)
        localized = self.scale_name(pattern_name)
        return f"{alias} ({localized})" if alias else localized

    def _update_scale_type_combo(self) -> None:
        if not hasattr(self, "scale_type_combo"):
            return
        if not hasattr(self, "scale_filter_mode"):
            self.scale_filter_mode = "basic"
        patterns = SCALE_PATTERNS
        if self.scale_filter_mode == "basic":
            patterns = [p for p in patterns if p.name in SCALE_BASIC_NAMES]
        options = [self._scale_type_display_label(p.name) for p in patterns]
        self._scale_type_label_to_name = {self._scale_type_display_label(p.name): p.name for p in patterns}
        self.scale_type_combo.configure(values=options)
        current_label = self._scale_type_display_label(self.scale_pattern_name)
        if current_label in options:
            self.scale_type_var.set(current_label)
        elif options:
            self.scale_type_var.set(options[0])
            self.scale_pattern_name = self._scale_type_label_to_name[options[0]]

    def _on_scale_tonic_combo_changed(self, _event: object) -> None:
        label = str(self.scale_tonic_var.get()).strip()
        pc = getattr(self, "_scale_tonic_label_to_pc", {}).get(label, None)
        if pc is None:
            for i in range(12):
                if self.note_name(i, with_octave=False) == label:
                    pc = i
                    break
        if pc is not None:
            self.scale_tonic_pc = int(pc)
            self._refresh_scale_preview()
            if self.scale_loop_active:
                self._play_scale()
            if self.scale_tab_active:
                self.update_music_views()

    def _on_scale_type_combo_changed(self, _event: object) -> None:
        label = str(self.scale_type_var.get()).strip()
        name = getattr(self, "_scale_type_label_to_name", {}).get(label, None)
        if name is None:
            for p in SCALE_PATTERNS:
                if self._scale_type_display_label(p.name) == label or self.scale_name(p.name) == label:
                    name = p.name
                    break
        if name is not None:
            self.scale_pattern_name = name
            self._refresh_scale_preview()
            if self.scale_loop_active:
                self._play_scale()
            if self.scale_tab_active:
                self.update_music_views()

    def open_scale_tonic_dialog(self) -> None:
        if self.scale_tonic_overlay is not None:
            self._close_scale_tonic_overlay()
            return

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.scale_tonic_overlay = overlay

        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_scale_tonic"),
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)

        buttons_frame = self._build_scrollable_area(overlay, bg="#2a2f36", padx=8, pady=(2, 10))
        for col in range(3):
            buttons_frame.columnconfigure(col, weight=1)
        for pc in range(12):
            btn = GrayRoundedButton(
                buttons_frame,
                text=self.note_name(pc, with_octave=False),
                command=lambda p=pc: self._select_scale_tonic_from_overlay(p),
                font_family=self.ui_font_family,
                width=122,
                height=74,
                radius=28,
                text_color="#f2f2f2",
                selected_text_color="#000000",
            )
            btn.grid(row=pc // 3, column=pc % 3, sticky="ew", padx=6, pady=6)
            btn.set_selected(pc == self.scale_tonic_pc)
    def _close_scale_tonic_overlay(self) -> None:
        if self.scale_tonic_overlay is not None:
            self.scale_tonic_overlay.destroy()
            self.scale_tonic_overlay = None
    def _select_scale_tonic_from_overlay(self, pc: int) -> None:
        self.scale_tonic_pc = pc
        self._refresh_scale_preview()
        if self.scale_loop_active:
            self._play_scale()
        if self.scale_tab_active:
            self.update_music_views()
        self._close_scale_tonic_overlay()
    def open_scale_type_dialog(self) -> None:
        if self.scale_type_overlay is not None:
            self._close_scale_type_overlay()
            return

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.scale_type_overlay = overlay

        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))

        # Título + botón toggle Básicas/Todas
        header_left = tk.Frame(header, bg="#2a2f36")
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            header_left,
            text=self.tr("label_scale_type"),
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)

        # Toggle Básicas/Todas
        if not hasattr(self, "scale_filter_mode"):
            self.scale_filter_mode = "basic"

        filter_btn = GrayRoundedButton(
            header_left,
            text=self.tr("basic") if self.scale_filter_mode == "basic" else self.tr("all"),
            command=self._toggle_scale_filter_mode,
            font_family=self.ui_font_family,
            width=90,
            height=40,
            radius=12,
            font_size=12,
            text_color="#f2f2f2",
            selected_text_color="#000000",
        )
        filter_btn.pack(side=tk.RIGHT, padx=10)
        self.scale_filter_btn = filter_btn

        body = tk.Frame(overlay, bg="#2a2f36")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))
        search_var, entry = self._build_rounded_search_entry(body, self.tr("label_search_scale"))
        self._scale_search_var = search_var  # Guardar para acceso desde _toggle_scale_filter_mode

        buttons_frame = self._build_scrollable_area(body, bg="#2a2f36", padx=0, pady=(0, 0))
        for col in range(2):
            buttons_frame.columnconfigure(col, weight=1)

        def render_buttons() -> None:
            for w in buttons_frame.winfo_children():
                w.destroy()

            term = search_var.get().strip().lower()
            patterns = SCALE_PATTERNS
            # Aplicar filtro de básicas si está activo
            if self.scale_filter_mode == "basic":
                patterns = [p for p in patterns if p.name in SCALE_BASIC_NAMES]
            # Aplicar búsqueda
            filtered = [p for p in patterns if term in self.scale_name(p.name).lower()]
            for idx, pattern in enumerate(filtered):
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=self.scale_name(pattern.name),
                    command=lambda n=pattern.name: self._select_scale_type_from_overlay(n),
                    font_family=self.ui_font_family,
                    width=208,
                    height=64,
                    radius=24,
                    font_size=16,
                    text_color="#f2f2f2",
                    selected_text_color="#000000",
                )
                btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=6, pady=6)
                btn.set_selected(pattern.name == self.scale_pattern_name)

        def on_search(*_args) -> None:
            render_buttons()

        search_var.trace_add("write", on_search)
        render_buttons()
        entry.focus_set()
    def _toggle_scale_filter_mode(self) -> None:
        self.scale_filter_mode = "all" if self.scale_filter_mode == "basic" else "basic"
        btn_text = self.tr("basic") if self.scale_filter_mode == "basic" else self.tr("all")
        if hasattr(self, "scale_filter_btn"):
            self.scale_filter_btn.set_text(btn_text)
        if hasattr(self, "scale_inline_filter_btn"):
            self.scale_inline_filter_btn.set_text(btn_text)
            self.scale_inline_filter_btn.set_selected(self.scale_filter_mode == "basic")
        if hasattr(self, "_scale_search_var"):
            self._scale_search_var.set(self._scale_search_var.get())
        if hasattr(self, "scale_type_combo"):
            self._update_scale_type_combo()
    def _close_scale_type_overlay(self) -> None:
        if self.scale_type_overlay is not None:
            self.scale_type_overlay.destroy()
            self.scale_type_overlay = None
    def _select_scale_type_from_overlay(self, pattern_name: str) -> None:
        self.scale_pattern_name = pattern_name
        self._refresh_scale_preview()
        if self.scale_loop_active:
            self._play_scale()
        if self.scale_tab_active:
            self.update_music_views()
        self._close_scale_type_overlay()
    def _finalize_scale_space_release(self) -> None:
        self.scale_space_release_after_id = None
        self.scale_space_pressed = False
    def _stop_scale_playback(self) -> None:
        self.scale_loop_active = False
        if self.scale_loop_after_id is not None:
            try:
                self.after_cancel(self.scale_loop_after_id)
            except Exception:
                pass
            self.scale_loop_after_id = None
        if self.scale_current_note is not None:
            self.stop_note(self.scale_current_note)
            self.scale_current_note = None
        self.scale_input_raw_note = None
        for note in list(self.scale_playing_notes):
            self.stop_note(note)
        self.scale_playing_notes.clear()
        self.scale_play_btn.set_playing(False)
        if self.scale_tab_active:
            self.redraw_keyboard()
            self.redraw_staff()
    def _stop_staff_scale_note_playback(self) -> None:
        if (
            not self.staff_pressed_scale_notes
            and not self.staff_pressed_scale_degrees
            and not self.scale_guitar_click_highlight_notes
            and not self.scale_guitar_drag_exact_notes
            and self.staff_hover_note is None
            and self.staff_hover_scale_degree is None
        ):
            return
        self.scale_staff_drag_active = False
        for note in list(self.staff_pressed_scale_notes):
            self.stop_note(note)
        self.staff_pressed_scale_notes.clear()
        self.staff_pressed_scale_degrees.clear()
        self.scale_guitar_click_highlight_notes.clear()
        self.scale_guitar_drag_exact_notes.clear()
        self.scale_guitar_drag_staff_notes.clear()
        self.staff_hover_note = None
        self.staff_hover_scale_degree = None
        self.scale_input_raw_note = None
        self.staff_scale_note_regions.clear()
        self.redraw_guitar_fretboard()
        self.redraw_keyboard()
        self.redraw_staff()
    def _scale_staff_note_for_pitch(self, note: int) -> Optional[int]:
        if not self.scale_preview_notes:
            return None
        target = int(note)
        if target in self.scale_preview_notes:
            return target
        first_rh = int(self.scale_preview_notes[0]) if self.scale_preview_notes else None
        lh_notes = [
            int(n - 12)
            for n in self.scale_preview_notes
            if int(n - 12) >= 0 and (first_rh is None or int(n - 12) < first_rh)
        ]
        if target in lh_notes:
            return target
        pc = int(note) % 12
        candidates = [n for n in self.scale_preview_notes if (n % 12) == pc]
        candidates.extend([n for n in lh_notes if (n % 12) == pc])
        if candidates:
            return min(candidates, key=lambda n: abs(int(n) - target))
        return None

    def _sync_scale_piano_staff_from_active_keys(self, active_notes: set[int]) -> None:
        """En Escalas (piano), el pentagrama usa `staff_pressed_scale_notes`; MIDI solo
        actualizaba `active_notes` en el teclado. Sincroniza cabezas del pentagrama con
        las notas mantenidas por MIDI/ratón/sostenido (sin pisar un arrastre en el pentagrama)."""
        if not self.scale_tab_active or self.scale_play_mode != "piano":
            return
        if getattr(self, "scale_staff_drag_active", False):
            return
        scale_pcs = {int(n) % 12 for n in self.scale_preview_notes}
        new_staff: set[int] = set()
        for n in active_notes:
            ni = int(n)
            if (ni % 12) not in scale_pcs:
                continue
            sn = self._scale_staff_note_for_pitch(ni)
            if sn is not None:
                new_staff.add(int(sn))
        self.staff_pressed_scale_notes = new_staff
        # Misma idea que el clic en teclado: una sola nota “cruda” para el resaltado fuera de rango.
        if len(active_notes) == 1:
            self.scale_input_raw_note = int(next(iter(active_notes)))
        else:
            self.scale_input_raw_note = None

    def _clear_scale_guitar_click_highlight(self, note: int) -> None:
        if note in self.scale_guitar_click_highlight_notes:
            self.scale_guitar_click_highlight_notes.discard(note)
            if self.scale_tab_active:
                self.redraw_staff()
    def _clear_scale_guitar_exact_highlight(self, note: int) -> None:
        if note in self.scale_guitar_click_highlight_exact_notes:
            self.scale_guitar_click_highlight_exact_notes.discard(note)
            if self.scale_tab_active and self.scale_play_mode == "guitar":
                self.redraw_guitar_fretboard()
    def _clear_scale_guitar_pc_highlight(self, pc: int) -> None:
        if pc in self.scale_guitar_click_highlight_pcs:
            self.scale_guitar_click_highlight_pcs.discard(pc)
            if self.scale_tab_active and self.scale_play_mode == "guitar":
                self.redraw_guitar_fretboard()
    def _staff_scale_hit_at_position(self, x: float, y: float) -> Optional[tuple[int, int]]:
        if not self.scale_tab_active:
            return None
        best_note: Optional[int] = None
        best_degree: Optional[int] = None
        best_dist = 10_000.0
        for note, cx, cy, rx, ry, label_y, label_half_w, degree_idx in self.staff_scale_note_regions:
            nx = (x - cx) / max(1.0, rx + 4.0)
            ny = (y - cy) / max(1.0, ry + 3.0)
            in_head = (nx * nx + ny * ny) <= 1.0
            in_label = (abs(x - cx) <= label_half_w) and (abs(y - label_y) <= 10.0)
            if not in_head and not in_label:
                continue
            dist = abs(x - cx) + abs(y - cy)
            if dist < best_dist:
                best_dist = dist
                best_note = note
                best_degree = int(degree_idx)
        if best_note is None or best_degree is None:
            return None
        return int(best_note), int(best_degree)

    def _staff_scale_note_at_position(self, x: float, y: float) -> Optional[int]:
        hit = self._staff_scale_hit_at_position(x, y)
        return int(hit[0]) if hit is not None else None
    def _play_scale(self) -> None:
        self._stop_scale_playback()
        if not self.scale_preview_notes:
            return
        self.scale_loop_active = True
        self.scale_loop_index = 0
        self.scale_loop_direction = 1
        self.scale_play_btn.set_playing(True)
        self._play_next_scale_step()
    def _scale_step_ms(self) -> int:
        bpm = int(self.config_data.get("metronome_bpm", 120))
        bpm = max(1, min(300, bpm))
        return int(60000 / bpm)
    def _play_next_scale_step(self) -> None:
        if not self.scale_loop_active or not self.scale_preview_notes:
            return

        notes = self.scale_preview_notes
        idx = max(0, min(self.scale_loop_index, len(notes) - 1))
        note = notes[idx]
        play_piano = self.scale_play_mode == "piano" and not self.scale_metronome_only
        play_guitar = self.scale_play_mode == "guitar" and not self.scale_metronome_only

        if self.scale_current_note is not None:
            if self.scale_current_note not in self.staff_pressed_scale_notes:
                self.stop_note(self.scale_current_note)
            self.scale_playing_notes.discard(self.scale_current_note)
        self.scale_current_note = note
        self.scale_input_raw_note = None
        if play_piano:
            self.play_note(note, 104)
            self.scale_playing_notes.add(note)
        elif play_guitar:
            self.audio_engine.pluck_guitar_note(note, velocity=104, duration_seconds=1.2)
        self._play_metronome_click(accent=(idx == 0 and self.scale_loop_direction > 0))
        if self.scale_tab_active:
            self.redraw_keyboard()
            self.redraw_staff()

        step_ms = self._scale_step_ms()
        if len(notes) > 1:
            if self.scale_loop_direction > 0:
                if idx >= len(notes) - 1:
                    self.scale_loop_direction = -1
                    self.scale_loop_index = idx
                else:
                    self.scale_loop_index = idx + 1
            else:
                if idx <= 0:
                    self.scale_loop_direction = 1
                    self.scale_loop_index = idx
                else:
                    self.scale_loop_index = idx - 1
        self.scale_loop_after_id = self.after(step_ms, self._play_next_scale_step)
    def _toggle_scale_play(self) -> None:
        if not self.scale_tab_active:
            return
        if self.scale_loop_active:
            self._stop_scale_playback()
        else:
            self._play_scale()
