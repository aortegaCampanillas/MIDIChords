from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from midichords.ui.widgets import GrayRoundedButton


class OverlaysMixin:
    def _close_tuner_tuning_overlay(self) -> None:
        if self.tuner_tuning_overlay is not None:
            self.tuner_tuning_overlay.destroy()
            self.tuner_tuning_overlay = None
    def open_tuner_tuning_dialog(self) -> None:
        if self.tuner_tuning_overlay is not None:
            self._close_tuner_tuning_overlay()
            return
        overlay = tk.Frame(
            self.chord_panel,
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.tuner_tuning_overlay = overlay
        header = tk.Frame(overlay, bg="#2b2d38")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_tuner_tuning"),
            bg="#2b2d38",
            fg="#f0f0f0",
            font=("Helvetica", 13, "bold"),
        ).pack(side=tk.LEFT)
        buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
        for col in range(2):
            buttons_frame.columnconfigure(col, weight=1)
        for idx, tuning in enumerate(self.tuner_tuning_defs):
            text = str(tuning["es"] if self.config_data.get("language", "es") == "es" else tuning["en"])
            key = str(tuning["key"])
            btn = GrayRoundedButton(
                buttons_frame,
                text=text,
                command=lambda k=key: self._select_tuner_tuning_from_overlay(k),
                width=210,
                height=64,
                radius=24,
                font_size=16,
            )
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=6, pady=6)
            btn.set_selected(key == self.tuner_tuning_key)
    def _select_tuner_tuning_from_overlay(self, key: str) -> None:
        if key not in {str(t["key"]) for t in self.tuner_tuning_defs}:
            return
        self.tuner_tuning_key = key
        self.config_data["tuner_tuning"] = key
        self.save_config()
        self._refresh_tuner_ui()
        self._close_tuner_tuning_overlay()
    def _is_widget_inside(self, parent: tk.Widget, child: object) -> bool:
        current: Optional[tk.Widget]
        if isinstance(child, tk.Widget):
            current = child
        elif isinstance(child, str):
            try:
                resolved = parent.nametowidget(child)
            except Exception:
                return False
            if not isinstance(resolved, tk.Widget):
                return False
            current = resolved
        else:
            return False
        while current is not None:
            if current == parent:
                return True
            next_widget = getattr(current, "master", None)
            if not isinstance(next_widget, tk.Widget):
                return False
            current = next_widget
        return False
    def _is_combobox_popdown_widget(self, widget: object) -> bool:
        widget_name = str(widget).lower()
        if "combobox" in widget_name and "popdown" in widget_name:
            return True
        if isinstance(widget, tk.Widget):
            try:
                widget_class = widget.winfo_class().lower()
            except Exception:
                return False
            if widget_class == "listbox" and "popdown" in widget_name:
                return True
        return False
    def _on_escape_pressed(self, _event: tk.Event) -> None:
        self._close_mode_selector_overlay()
        self._close_scale_tonic_overlay()
        self._close_scale_type_overlay()
        self._close_generation_selection_overlay()
        self._close_tuner_tuning_overlay()
        self._close_settings_overlay()
    def _on_return_pressed(self, _event: tk.Event) -> Optional[str]:
        if self.settings_overlay is not None and callable(self._settings_save_callback):
            self._settings_save_callback()
            return "break"
        return None
    def _on_space_pressed(self, _event: tk.Event) -> Optional[str]:
        if self.metronome_tab_active:
            if self.metronome_space_release_after_id is not None:
                try:
                    self.after_cancel(self.metronome_space_release_after_id)
                except Exception:
                    pass
                self.metronome_space_release_after_id = None
            if self.metronome_space_pressed:
                return "break"
            self.metronome_space_pressed = True
            self._toggle_metronome()
            return "break"
        if self.scale_tab_active:
            if self.scale_space_release_after_id is not None:
                try:
                    self.after_cancel(self.scale_space_release_after_id)
                except Exception:
                    pass
                self.scale_space_release_after_id = None
            if self.scale_space_pressed:
                return "break"
            self.scale_space_pressed = True
            self._toggle_scale_play()
            return "break"
        if self.generation_tab_active:
            if self.generation_space_release_after_id is not None:
                try:
                    self.after_cancel(self.generation_space_release_after_id)
                except Exception:
                    pass
                self.generation_space_release_after_id = None
            if not self.generation_play_space_pressed:
                self._start_generated_hold(source="space")
            return "break"
        return None
    def _on_space_released(self, _event: tk.Event) -> Optional[str]:
        if self.metronome_tab_active:
            if self.metronome_space_release_after_id is not None:
                try:
                    self.after_cancel(self.metronome_space_release_after_id)
                except Exception:
                    pass
                self.metronome_space_release_after_id = None
            self.metronome_space_release_after_id = self.after(35, self._finalize_metronome_space_release)
            return "break"
        if self.scale_tab_active:
            if self.scale_space_release_after_id is not None:
                try:
                    self.after_cancel(self.scale_space_release_after_id)
                except Exception:
                    pass
                self.scale_space_release_after_id = None
            self.scale_space_release_after_id = self.after(35, self._finalize_scale_space_release)
            return "break"
        if self.generation_tab_active and self.generation_play_space_pressed:
            if self.generation_space_release_after_id is not None:
                try:
                    self.after_cancel(self.generation_space_release_after_id)
                except Exception:
                    pass
                self.generation_space_release_after_id = None
            self.generation_space_release_after_id = self.after(35, self._finalize_generation_space_release)
            return "break"
        return None
    def _finalize_tuner_space_release(self) -> None:
        self.tuner_space_release_after_id = None
        self.tuner_space_pressed = False
    def _on_global_click_press(self, event: tk.Event) -> None:
        widget = event.widget
        if self.scale_tonic_overlay is not None and not self._is_widget_inside(self.scale_tonic_overlay, widget):
            if widget != self.scale_tonic_btn:
                self._close_scale_tonic_overlay()
        if self.scale_type_overlay is not None and not self._is_widget_inside(self.scale_type_overlay, widget):
            if widget != self.scale_type_btn:
                self._close_scale_type_overlay()
        if self.generation_selection_overlay is not None and not self._is_widget_inside(self.generation_selection_overlay, widget):
            if widget not in {
                self.generation_root_btn,
                self.generation_variant_btn,
                self.generation_inversion_btn,
            }:
                self._close_generation_selection_overlay()
        if self.tuner_tuning_overlay is not None and not self._is_widget_inside(self.tuner_tuning_overlay, widget):
            if widget != self.tuner_tuning_btn:
                self._close_tuner_tuning_overlay()
        if self.settings_overlay is not None and not self._is_widget_inside(self.settings_overlay, widget):
            if self._is_combobox_popdown_widget(widget):
                return
            if widget != self.config_icon_btn:
                self._close_settings_overlay()
        if self.mode_selector_overlay is not None and not self._is_widget_inside(self.mode_selector_overlay, widget):
            if not self._is_widget_inside(self.mode_picker_trigger, widget):
                self._close_mode_selector_overlay()
    def _preview_piano_sound(self, preset: str) -> None:
        previous = str(self.audio_engine.preset)
        self.audio_engine.set_preset(preset)
        preview_note = 60
        self.audio_engine.note_on(preview_note, 106)

        def stop_preview() -> None:
            self.audio_engine.note_off(preview_note)
            self.audio_engine.set_preset(previous)

        self.after(520, stop_preview)
    def _preview_guitar_sound(self, preset: str) -> None:
        previous = str(self.audio_engine.guitar_preset)
        self.audio_engine.set_guitar_preset(preset)
        for note in (52, 59, 64):
            self.audio_engine.pluck_guitar_note(note, velocity=104, duration_seconds=1.3)

        def restore_preview() -> None:
            self.audio_engine.set_guitar_preset(previous)

        self.after(220, restore_preview)
    def open_settings_dialog(self) -> None:
        if self.settings_overlay is not None:
            self._close_settings_overlay()
            return

        self.refresh_devices()
        self._close_scale_tonic_overlay()
        self._close_scale_type_overlay()
        self._close_generation_selection_overlay()

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.settings_overlay = overlay

        frame = ttk.Frame(overlay, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=self.tr("settings_language")).grid(row=0, column=0, sticky="w", pady=4)
        language_options = [("es", "Español"), ("en", "English")]
        lang_id_to_label = {lang_id: label for lang_id, label in language_options}
        lang_label_to_id = {label: lang_id for lang_id, label in language_options}
        current_lang = str(self.config_data.get("language", "es"))
        if current_lang not in lang_id_to_label:
            current_lang = "es"
        lang_var = tk.StringVar(value=lang_id_to_label[current_lang])
        lang_combo = ttk.Combobox(
            frame,
            textvariable=lang_var,
            state="readonly",
            values=[label for _, label in language_options],
            width=18,
        )
        lang_combo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text=self.tr("settings_midi_input")).grid(row=1, column=0, sticky="w", pady=4)
        in_values = [""] + self.input_names
        in_var = tk.StringVar(value=self.config_data.get("midi_input", ""))
        in_combo = ttk.Combobox(frame, textvariable=in_var, state="readonly", values=in_values, width=48)
        in_combo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text=self.tr("settings_audio_output")).grid(row=2, column=0, sticky="w", pady=4)
        out_values = [""] + self.audio_output_names
        out_var = tk.StringVar(value=self.config_data.get("audio_output", ""))
        out_combo = ttk.Combobox(frame, textvariable=out_var, state="readonly", values=out_values, width=48)
        out_combo.grid(row=2, column=1, sticky="ew", pady=4)

        piano_sound_options = [
            ("acoustic", self.tr("sound_acoustic")),
            ("warm", self.tr("sound_warm")),
            ("bright", self.tr("sound_bright")),
            ("soft", self.tr("sound_soft")),
        ]
        piano_sound_id_to_label = {sid: label for sid, label in piano_sound_options}
        piano_sound_label_to_id = {label: sid for sid, label in piano_sound_options}
        current_piano_sound = str(self.config_data.get("sound_preset", "acoustic"))
        if current_piano_sound not in piano_sound_id_to_label:
            current_piano_sound = "acoustic"

        guitar_sound_options = [
            ("steel_clean", self.tr("guitar_sound_steel_clean")),
            ("steel_bright", self.tr("guitar_sound_steel_bright")),
            ("nylon_warm", self.tr("guitar_sound_nylon_warm")),
            ("muted_short", self.tr("guitar_sound_muted_short")),
        ]
        guitar_sound_id_to_label = {sid: label for sid, label in guitar_sound_options}
        guitar_sound_label_to_id = {label: sid for sid, label in guitar_sound_options}
        current_guitar_sound = str(self.config_data.get("guitar_sound_preset", "steel_clean"))
        if current_guitar_sound not in guitar_sound_id_to_label:
            current_guitar_sound = "steel_clean"

        ttk.Label(frame, text=self.tr("settings_piano_sound")).grid(row=3, column=0, sticky="w", pady=4)
        piano_sound_row = ttk.Frame(frame)
        piano_sound_row.grid(row=3, column=1, sticky="ew", pady=4)
        piano_sound_row.columnconfigure(0, weight=1)
        piano_sound_var = tk.StringVar(value=piano_sound_id_to_label[current_piano_sound])
        piano_sound_combo = ttk.Combobox(
            piano_sound_row,
            textvariable=piano_sound_var,
            state="readonly",
            values=[label for _, label in piano_sound_options],
            width=44,
        )
        piano_sound_combo.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            piano_sound_row,
            text="🔊",
            width=3,
            command=lambda: self._preview_piano_sound(piano_sound_label_to_id.get(piano_sound_var.get(), "acoustic")),
        ).grid(row=0, column=1, padx=(6, 0))

        ttk.Label(frame, text=self.tr("settings_guitar_sound")).grid(row=4, column=0, sticky="w", pady=4)
        guitar_sound_row = ttk.Frame(frame)
        guitar_sound_row.grid(row=4, column=1, sticky="ew", pady=4)
        guitar_sound_row.columnconfigure(0, weight=1)
        guitar_sound_var = tk.StringVar(value=guitar_sound_id_to_label[current_guitar_sound])
        guitar_sound_combo = ttk.Combobox(
            guitar_sound_row,
            textvariable=guitar_sound_var,
            state="readonly",
            values=[label for _, label in guitar_sound_options],
            width=44,
        )
        guitar_sound_combo.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            guitar_sound_row,
            text="🔊",
            width=3,
            command=lambda: self._preview_guitar_sound(guitar_sound_label_to_id.get(guitar_sound_var.get(), "steel_clean")),
        ).grid(row=0, column=1, padx=(6, 0))

        def refresh_device_lists() -> None:
            prev_in = in_var.get()
            prev_out = out_var.get()
            self.refresh_devices()
            in_combo["values"] = [""] + self.input_names
            out_combo["values"] = [""] + self.audio_output_names
            if prev_in in in_combo["values"]:
                in_var.set(prev_in)
            if prev_out in out_combo["values"]:
                out_var.set(prev_out)

        # Refresca dispositivos justo antes de abrir cada lista desplegable.
        in_combo.configure(postcommand=refresh_device_lists)
        out_combo.configure(postcommand=refresh_device_lists)

        show_labels_var = tk.BooleanVar(value=bool(self.config_data.get("show_keyboard_note_labels", False)))
        show_labels_chk = ttk.Checkbutton(
            frame,
            text=self.tr("settings_show_key_labels"),
            variable=show_labels_var,
        )
        show_labels_chk.grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 4))

        ttk.Label(frame, text=self.tr("settings_guitar_handedness")).grid(row=6, column=0, sticky="w", pady=4)
        handed_options = [("right", self.tr("handed_right")), ("left", self.tr("handed_left"))]
        handed_id_to_label = {hid: label for hid, label in handed_options}
        handed_label_to_id = {label: hid for hid, label in handed_options}
        current_handed = str(self.config_data.get("guitar_handedness", "right"))
        if current_handed not in handed_id_to_label:
            current_handed = "right"
        handed_var = tk.StringVar(value=handed_id_to_label[current_handed])
        handed_combo = ttk.Combobox(
            frame,
            textvariable=handed_var,
            state="readonly",
            values=[label for _, label in handed_options],
            width=18,
        )
        handed_combo.grid(row=6, column=1, sticky="w", pady=4)

        def do_save(_event: Optional[tk.Event] = None) -> str:
            self.config_data["language"] = lang_label_to_id.get(lang_var.get(), "es")
            self.config_data["midi_input"] = in_var.get().strip()
            self.config_data["audio_output"] = out_var.get().strip()
            self.config_data["sound_preset"] = piano_sound_label_to_id.get(piano_sound_var.get(), "acoustic")
            self.config_data["guitar_sound_preset"] = guitar_sound_label_to_id.get(guitar_sound_var.get(), "steel_clean")
            self.config_data["show_keyboard_note_labels"] = bool(show_labels_var.get())
            self.config_data["guitar_handedness"] = handed_label_to_id.get(handed_var.get(), "right")
            self.guitar_handedness = "left" if self.config_data["guitar_handedness"] == "left" else "right"
            self.audio_engine.set_preset(str(self.config_data["sound_preset"]))
            self.audio_engine.set_guitar_preset(str(self.config_data["guitar_sound_preset"]))
            self.apply_ui_language()
            self.save_config()
            self.connect_ports()
            self._refresh_handedness_toggle_styles()
            self.redraw_guitar_fretboard()
            self.update_music_views()
            self._close_settings_overlay()
            return "break"

        def close_dialog(_event: Optional[tk.Event] = None) -> str:
            self._close_settings_overlay()
            return "break"

        buttons = ttk.Frame(frame)
        buttons.grid(row=7, column=0, columnspan=2, sticky="e")

        ttk.Button(buttons, text=self.tr("button_cancel"), command=self._close_settings_overlay).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text=self.tr("button_save"), command=do_save).pack(side=tk.LEFT)

        frame.columnconfigure(1, weight=1)
        overlay.bind("<Escape>", close_dialog)
        overlay.bind("<Return>", do_save)
        frame.bind("<Escape>", close_dialog)
        frame.bind("<Return>", do_save)
        self._settings_save_callback = do_save
        overlay.focus_set()
    def _close_settings_overlay(self) -> None:
        if self.settings_overlay is not None:
            self.settings_overlay.destroy()
            self.settings_overlay = None
        self._settings_save_callback = None
