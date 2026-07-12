from __future__ import annotations

import time
import threading
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea

import midichords.qt.tk_compat as tk
import midichords.qt.ttk_compat as ttk

from midichords.core.app_constants import desktop_build_display_name
from midichords.ui.widgets_qt import GrayRoundedButton


class OverlaysMixin:
    def _build_radio_row(self, parent: Any, options: list[tuple[str, str]], variable: Any) -> Any:
        """Fila de opciones tipo radio button, dibujadas a mano (ver
        `_draw_radio_indicator` en metronome_mixin.py). Con ttk.Radiobutton
        nativo, el punto de la opción marcada no se pinta (visto en Idioma y
        Salida de sonido del diálogo de Configuración, con el estilo
        "windows11" y también con Fusion)."""
        row = ttk.Frame(parent)
        canvases: dict[str, tk.Canvas] = {}

        def _redraw_all(*_args: Any) -> None:
            current = str(variable.get())
            for value, canvas in canvases.items():
                self._draw_radio_indicator(canvas, value == current)

        for value, label in options:
            item = ttk.Frame(row)
            item.pack(side=tk.LEFT, padx=(0, 16))
            indicator = tk.Canvas(
                item, width=16, height=16, bg=self.color_surface_alt, highlightthickness=0, bd=0, cursor="hand2"
            )
            indicator.pack(side=tk.LEFT, padx=(0, 6))
            text_label = tk.Label(
                item,
                text=label,
                bg=self.color_surface_alt,
                fg=self.color_text,
                font=(self.ui_font_family, 13),
                cursor="hand2",
            )
            text_label.pack(side=tk.LEFT)
            canvases[value] = indicator

            def _select(_e: Optional[Any] = None, v: str = value) -> str:
                variable.set(v)
                return "break"

            indicator.bind("<Button-1>", _select)
            text_label.bind("<Button-1>", _select)
            indicator.bind("<Configure>", lambda _e, c=indicator, v=value: self._draw_radio_indicator(c, v == str(variable.get())))

        variable.trace_add("write", _redraw_all)
        return row

    def _build_checkbox_row(self, parent: Any, text: str, variable: Any) -> Any:
        """Fila con un checkbox dibujado a mano (ver `_draw_metronome_checkbox`
        en metronome_mixin.py) — con ttk.Checkbutton nativo, la caja alrededor
        del check no se pinta cuando está marcado."""
        row = ttk.Frame(parent)
        indicator = tk.Canvas(
            row, width=18, height=18, bg=self.color_surface_alt, highlightthickness=0, bd=0, cursor="hand2"
        )
        indicator.pack(side=tk.LEFT, padx=(0, 8))
        text_label = tk.Label(
            row, text=text, bg=self.color_surface_alt, fg=self.color_text, font=(self.ui_font_family, 13), cursor="hand2"
        )
        text_label.pack(side=tk.LEFT)

        def _toggle(_e: Optional[Any] = None) -> str:
            variable.set(not bool(variable.get()))
            return "break"

        def _redraw(*_args: Any) -> None:
            self._draw_metronome_checkbox(indicator, bool(variable.get()))

        indicator.bind("<Button-1>", _toggle)
        text_label.bind("<Button-1>", _toggle)
        indicator.bind("<Configure>", _redraw)
        variable.trace_add("write", _redraw)
        return row

    def _qt_append_dark_native_controls_stylesheet(self, root: Any) -> None:
        """QLabel/QCheckBox/QSpinBox sin fg explícito heredan gris/negro del estilo nativo (p. ej. Windows)."""
        if not hasattr(root, "setStyleSheet"):
            return
        fg = getattr(self, "color_text", "#e9edf2")
        card = getattr(self, "color_card", "#3a4452")
        border = getattr(self, "color_border", "#56627a")
        extra = f"""
            QLabel {{
                color: {fg};
                background-color: transparent;
            }}
            QCheckBox {{
                color: {fg};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QSpinBox {{
                background-color: {card};
                color: {fg};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 1.2em;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: {card};
                border: none;
                width: 16px;
            }}
        """
        prev = (root.styleSheet() or "").strip()
        root.setStyleSheet((prev + "\n" + extra).strip() if prev else extra.strip())

    def _qt_style_scroll_area_viewport(self, content_root: Any) -> None:
        """Viewport y QScrollArea: fondo alineado al panel (evita franjas claras)."""
        bg = getattr(self, "color_surface_alt", "#2f3a4b")
        pw = content_root.parentWidget() if hasattr(content_root, "parentWidget") else None
        if pw is None:
            return
        try:
            pw.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        except Exception:
            pass
        pw.setStyleSheet(f"background-color: {bg};")
        sa = pw.parentWidget()
        if isinstance(sa, QScrollArea):
            sa.setStyleSheet(
                f"QScrollArea {{ border: none; background-color: {bg}; }}"
                f" QScrollBar:vertical {{ background: {bg}; width: 12px; }}"
                f" QScrollBar::handle:vertical {{ background: {getattr(self, 'color_border', '#56627a')}; min-height: 24px; border-radius: 4px; }}"
            )

    def _qt_settings_combo_stylesheet(self) -> str:
        fg = getattr(self, "color_text", "#e9edf2")
        card = getattr(self, "color_card", "#3a4452")
        border = getattr(self, "color_border", "#56627a")
        hover_border = getattr(self, "color_border_hover", "#6a7a98")
        btn_bg = getattr(self, "color_card_hover", "#465465")
        return f"""
            QComboBox {{
                background-color: {card};
                color: {fg};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 2px 8px;
                height: 28px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border: 1px solid {hover_border};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
                background: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {card};
                color: {fg};
                selection-background-color: {btn_bg};
                selection-color: {fg};
                border: 1px solid {border};
                border-radius: 8px;
                outline: 0;
                padding: 2px;
            }}
        """

    def _qt_style_settings_combo(self, combo: Any) -> None:
        if not hasattr(combo, "setStyleSheet"):
            return
        combo.setStyleSheet(self._qt_settings_combo_stylesheet())
        if hasattr(combo, "_popup_bg"):
            combo._popup_bg = getattr(self, "color_card", "#3a4452")

    def _qt_style_settings_form(self, form: Any) -> None:
        """Tema oscuro coherente con la app (Qt/Windows: evita texto negro sobre gris del estilo nativo)."""
        if not hasattr(form, "setStyleSheet"):
            return
        bg = getattr(self, "color_surface_alt", "#2f3a4b")
        fg = getattr(self, "color_text", "#e9edf2")
        border = getattr(self, "color_border", "#56627a")
        hover_border = getattr(self, "color_border_hover", "#6a7a98")
        btn_bg = getattr(self, "color_card_hover", "#465465")
        form.setStyleSheet(
            f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
            }}
            QLabel {{
                color: {fg};
                background-color: transparent;
            }}
            {self._qt_settings_combo_stylesheet()}
            QCheckBox {{
                color: {fg};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 72px;
            }}
            QPushButton:hover {{
                background-color: {hover_border};
                border: 1px solid {hover_border};
            }}
            QPushButton:pressed {{
                background-color: {getattr(self, "color_card", "#3a4452")};
            }}
            """
        )

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
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.tuner_tuning_overlay = overlay
        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_tuner_tuning"),
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)
        buttons_frame = self._build_scrollable_area(overlay, bg="#2a2f36", padx=8, pady=(2, 10))
        for col in range(2):
            buttons_frame.columnconfigure(col, weight=1)
        for idx, tuning in enumerate(self.tuner_tuning_defs):
            text = str(tuning["es"] if self.config_data.get("language", "es") == "es" else tuning["en"])
            key = str(tuning["key"])
            btn = GrayRoundedButton(
                buttons_frame,
                text=text,
                command=lambda k=key: self._select_tuner_tuning_from_overlay(k),
                font_family=self.ui_font_family,
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
        if child is parent:
            return True
        current: Any = child
        if isinstance(child, str):
            try:
                resolved = parent.nametowidget(child)
            except Exception:
                return False
            if not isinstance(resolved, tk.Widget):
                return False
            current = resolved
        elif not isinstance(child, tk.Widget) and hasattr(child, "parentWidget"):
            # Clic en QLabel interno, QComboBox, etc.: subir por la jerarquía Qt.
            try:
                current = child.parentWidget()
            except Exception:
                return False
        elif not isinstance(child, tk.Widget):
            return False
        while current is not None:
            if current == parent:
                return True
            if isinstance(current, tk.Widget):
                next_widget = current.master
            else:
                next_widget = current.parentWidget() if hasattr(current, "parentWidget") else None
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
            tonic_trigger = getattr(self, "scale_tonic_combo", getattr(self, "scale_tonic_btn", None))
            if widget != tonic_trigger:
                self._close_scale_tonic_overlay()
        if self.scale_type_overlay is not None and not self._is_widget_inside(self.scale_type_overlay, widget):
            type_trigger = getattr(self, "scale_type_combo", getattr(self, "scale_type_btn", None))
            if widget != type_trigger:
                self._close_scale_type_overlay()
        if self.generation_selection_overlay is not None and not self._is_widget_inside(self.generation_selection_overlay, widget):
            keep_open_triggers = {
                getattr(self, "generation_root_btn", None),
                getattr(self, "generation_variant_btn", None),
                getattr(self, "generation_inversion_btn", None),
                getattr(self, "generation_root_combo", None),
                getattr(self, "generation_variant_combo", None),
                getattr(self, "generation_inversion_combo", None),
            }
            if widget not in keep_open_triggers:
                self._close_generation_selection_overlay()
        if self.tuner_tuning_overlay is not None and not self._is_widget_inside(self.tuner_tuning_overlay, widget):
            if widget != self.tuner_tuning_btn:
                self._close_tuner_tuning_overlay()
        if self.settings_overlay is not None and not self._is_widget_inside(self.settings_overlay, widget):
            if self._is_combobox_popdown_widget(widget):
                return
            # Qt: el eventFilter de la app dispara bind_all por cada ancestro del clic; al abrir
            # desde ⚙ el siguiente "receptor" es el Frame padre y cerraba el overlay al instante.
            opened_ts = float(getattr(self, "_settings_overlay_opened_ts", 0.0) or 0.0)
            if opened_ts > 0.0 and (time.monotonic() - opened_ts) < 0.28:
                return
            if widget != self.config_icon_btn:
                self._close_settings_overlay()
        if self.mode_selector_overlay is not None and not self._is_widget_inside(self.mode_selector_overlay, widget):
            opened_ts = float(getattr(self, "_mode_selector_opened_ts", 0.0) or 0.0)
            if opened_ts > 0.0 and (time.monotonic() - opened_ts) < 0.18:
                return
            if not self._is_widget_inside(self.mode_picker_trigger, widget):
                self._close_mode_selector_overlay()
    def _preview_piano_sound(self, preset: str) -> None:
        previous = str(self.audio_engine.preset)
        self.audio_engine.set_preset(preset)
        preview_note = 60
        self.play_note(preview_note, 106)

        def stop_preview() -> None:
            self.stop_note(preview_note)
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

        self._close_scale_tonic_overlay()
        self._close_scale_type_overlay()
        self._close_generation_selection_overlay()

        dialog = tk.Toplevel(self)
        dialog.title(self.tr("settings_title"))
        dialog.resizable(False, False)
        dialog_bg = getattr(self, "color_surface_alt", "#2f3a4b")
        dialog.setStyleSheet(f"QDialog {{ background-color: {dialog_bg}; }}")

        dialog.columnconfigure(0, weight=1)

        self.settings_overlay = dialog
        self._settings_overlay_opened_ts = time.monotonic()

        def fit_settings_dialog_to_content() -> None:
            if self.settings_overlay is not dialog:
                return
            try:
                dialog.setMinimumSize(0, 0)
                dialog.setMaximumSize(16777215, 16777215)
                layout = dialog.layout()
                if layout is not None:
                    layout.activate()
                dialog.adjustSize()
                size = dialog.sizeHint()
                dialog.resize(size)
                dialog.setFixedSize(size.width(), size.height())
            except Exception:
                pass

        frame = ttk.Frame(dialog, padding=14)
        frame.grid(row=0, column=0, sticky="w", padx=0, pady=0)

        ttk.Label(frame, text=self.tr("settings_language")).grid(row=0, column=0, sticky="w", pady=0)

        language_options = [("es", "Español"), ("en", "English")]
        lang_id_to_label = {lang_id: label for lang_id, label in language_options}
        lang_label_to_id = {label: lang_id for lang_id, label in language_options}
        current_lang = str(self.config_data.get("language", "es"))
        if current_lang not in lang_id_to_label:
            current_lang = "es"
        lang_var = tk.StringVar(value=current_lang)

        lang_frame = self._build_radio_row(frame, language_options, lang_var)
        lang_frame.grid(row=0, column=1, sticky="w", pady=4)

        not_selected_label = self.tr("settings_not_selected")

        def set_combo_text(combo: Any, var: Any, value: str) -> None:
            if hasattr(combo, "setCurrentText"):
                combo.setCurrentText(value)
                # En Qt, `setCurrentText` no emite `currentTextChanged` si el
                # combo ya mostraba ese texto (p. ej. el índice 0 tras
                # `addItems`), así que el StringVar puede quedarse sin
                # sincronizar. Forzamos el valor explícitamente.
                var.set(value)
            else:
                var.set(value)

        ttk.Label(frame, text=self.tr("settings_midi_input")).grid(row=1, column=0, sticky="w", pady=0)
        in_values = [not_selected_label] + self.input_names
        in_var = tk.StringVar()
        in_combo = ttk.Combobox(frame, textvariable=in_var, state="readonly", values=in_values)
        self._qt_style_settings_combo(in_combo)
        in_combo.grid(row=1, column=1, sticky="ew", pady=0)
        midi_current = self.config_data.get("midi_input", "")
        if midi_current in in_values:
            set_combo_text(in_combo, in_var, str(midi_current))
        else:
            set_combo_text(in_combo, in_var, not_selected_label)

        ttk.Label(frame, text=self.tr("settings_audio_output")).grid(row=2, column=0, sticky="w", pady=0)
        out_values = [not_selected_label] + self.audio_output_names
        out_var = tk.StringVar()
        out_combo = ttk.Combobox(frame, textvariable=out_var, state="readonly", values=out_values)
        self._qt_style_settings_combo(out_combo)
        out_combo.grid(row=2, column=1, sticky="ew", pady=0)
        audio_current = self.config_data.get("audio_output", "")
        if audio_current in out_values:
            set_combo_text(out_combo, out_var, str(audio_current))
        else:
            set_combo_text(out_combo, out_var, not_selected_label)

        piano_sound_options = [
            ("acoustic", self.tr("sound_acoustic")),
            ("warm", self.tr("sound_warm")),
            ("bright", self.tr("sound_bright")),
            ("soft", self.tr("sound_soft")),
            ("grand_sample", self.tr("sound_grand_sample")),
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
            ("nylon_sample", self.tr("guitar_sound_nylon_sample")),
        ]
        guitar_sound_id_to_label = {sid: label for sid, label in guitar_sound_options}
        guitar_sound_label_to_id = {label: sid for sid, label in guitar_sound_options}
        current_guitar_sound = str(self.config_data.get("guitar_sound_preset", "steel_clean"))
        if current_guitar_sound not in guitar_sound_id_to_label:
            current_guitar_sound = "steel_clean"

        ttk.Label(frame, text=self.tr("settings_piano_sound")).grid(row=3, column=0, sticky="w", pady=0)
        piano_sound_row = ttk.Frame(frame)
        piano_sound_row.grid(row=3, column=1, sticky="ew", pady=0)
        piano_sound_row.columnconfigure(0, weight=1)
        piano_sound_var = tk.StringVar(value=piano_sound_id_to_label[current_piano_sound])
        piano_sound_combo = ttk.Combobox(
            piano_sound_row,
            textvariable=piano_sound_var,
            state="readonly",
            values=[label for _, label in piano_sound_options],
        )
        self._qt_style_settings_combo(piano_sound_combo)
        piano_sound_combo.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            piano_sound_row,
            text="🔊",
            width=3,
            command=lambda: self._preview_piano_sound(piano_sound_label_to_id.get(piano_sound_var.get(), "acoustic")),
        ).grid(row=0, column=1, padx=(6, 0))

        ttk.Label(frame, text=self.tr("settings_guitar_sound")).grid(row=4, column=0, sticky="w", pady=0)
        guitar_sound_row = ttk.Frame(frame)
        guitar_sound_row.grid(row=4, column=1, sticky="ew", pady=0)
        guitar_sound_row.columnconfigure(0, weight=1)
        guitar_sound_var = tk.StringVar(value=guitar_sound_id_to_label[current_guitar_sound])
        guitar_sound_combo = ttk.Combobox(
            guitar_sound_row,
            textvariable=guitar_sound_var,
            state="readonly",
            values=[label for _, label in guitar_sound_options],
        )
        self._qt_style_settings_combo(guitar_sound_combo)
        guitar_sound_combo.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            guitar_sound_row,
            text="🔊",
            width=3,
            command=lambda: self._preview_guitar_sound(guitar_sound_label_to_id.get(guitar_sound_var.get(), "steel_clean")),
        ).grid(row=0, column=1, padx=(6, 0))

        # Sound output: Audio vs MIDI
        ttk.Label(frame, text=self.tr("settings_sound_output")).grid(row=5, column=0, sticky="w", pady=4)
        sound_output_var = tk.StringVar(value=str(self.config_data.get("sound_output", "audio")))
        sound_output_options = [("audio", self.tr("sound_output_audio")), ("midi", self.tr("sound_output_midi"))]
        sound_output_frame = self._build_radio_row(frame, sound_output_options, sound_output_var)
        sound_output_frame.grid(row=5, column=1, sticky="w", pady=4)
        # `_build_radio_row` ya redibuja sus indicadores en cada escritura del
        # StringVar (incluidas las programáticas, p. ej. al detectar/perder
        # una entrada MIDI más abajo), así que no hace falta sincronizar nada
        # a mano aquí.

        # Si el usuario selecciona una entrada MIDI (antes vacía/"no seleccionado"),
        # activa automáticamente la salida por MIDI: es el flujo esperado al
        # conectar un piano MIDI por primera vez. Si se queda sin entrada MIDI
        # (se quita o se desconecta), vuelve a Audio (síntesis) por defecto.
        _prev_midi_input_choice = {"value": in_var.get()}

        def _on_midi_input_choice_changed(*_args: Any) -> None:
            prev = _prev_midi_input_choice["value"]
            current = in_var.get()
            _prev_midi_input_choice["value"] = current
            had_device = bool(prev) and prev != not_selected_label
            has_device = bool(current) and current != not_selected_label
            if has_device and not had_device:
                sound_output_var.set("midi")
            elif had_device and not has_device:
                sound_output_var.set("audio")

        in_var.trace_add("write", _on_midi_input_choice_changed)

        ttk.Label(frame, text=self.tr("settings_midi_output")).grid(row=6, column=0, sticky="w", pady=4)
        midi_out_values = [not_selected_label] + self.get_midi_output_names()
        midi_out_var = tk.StringVar()
        midi_out_combo = ttk.Combobox(
            frame, textvariable=midi_out_var, state="readonly", values=midi_out_values
        )
        self._qt_style_settings_combo(midi_out_combo)
        midi_out_combo.grid(row=6, column=1, sticky="ew", pady=4)
        midi_out_current = self.config_data.get("midi_output", "")
        if midi_out_current in midi_out_values:
            set_combo_text(midi_out_combo, midi_out_var, str(midi_out_current))
        else:
            set_combo_text(midi_out_combo, midi_out_var, not_selected_label)

        midi_out_error_label = ttk.Label(
            frame,
            text="",
            foreground="#d32f2f",
        )
        midi_out_error_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 2))

        def _clear_midi_output_error(*_args: Any) -> None:
            midi_out_error_label.configure(text="")

        sound_output_var.trace_add("write", _clear_midi_output_error)
        midi_out_var.trace_add("write", _clear_midi_output_error)

        def refresh_device_lists() -> None:
            # En Qt no existe (o no se propaga) `postcommand` igual que en Tk.
            # Para que el usuario vea dispositivos conectados "después de arrancar",
            # actualizamos en segundo plano y luego aplicamos los valores en el hilo UI.
            if getattr(self, "_settings_device_refreshing", False):
                return
            setattr(self, "_settings_device_refreshing", True)

            # Respaldo con config por si el combo y la var visual se desincronizan.
            prev_in = in_var.get() or str(self.config_data.get("midi_input", ""))
            prev_out = out_var.get() or str(self.config_data.get("audio_output", ""))
            prev_midi_out = midi_out_var.get() or str(self.config_data.get("midi_output", ""))

            def worker() -> None:
                self.refresh_devices()
                new_inputs = list(self.input_names)
                new_outputs = list(self.audio_output_names)
                new_midi_outputs = self.get_midi_output_names()

                def apply() -> None:
                    try:
                        updated_in_values = [not_selected_label] + new_inputs
                        updated_out_values = [not_selected_label] + new_outputs
                        updated_midi_out_values = [not_selected_label] + new_midi_outputs
                        in_combo["values"] = updated_in_values
                        out_combo["values"] = updated_out_values
                        midi_out_combo["values"] = updated_midi_out_values
                        set_combo_text(
                            in_combo,
                            in_var,
                            prev_in if prev_in in updated_in_values else not_selected_label,
                        )
                        set_combo_text(
                            out_combo,
                            out_var,
                            prev_out if prev_out in updated_out_values else not_selected_label,
                        )
                        set_combo_text(
                            midi_out_combo,
                            midi_out_var,
                            prev_midi_out if prev_midi_out in updated_midi_out_values else not_selected_label,
                        )
                        fit_settings_dialog_to_content()
                    finally:
                        setattr(self, "_settings_device_refreshing", False)

                # No usar `self.after` desde el worker: en Qt crea QTimer en un hilo
                # que no es el GUI y aparece "Timers can only be used with QThread".
                try:
                    from midichords.qt.qt_primitives import run_on_main_thread

                    run_on_main_thread(apply)
                except Exception:
                    apply()

            threading.Thread(target=worker, daemon=True).start()

        # Refresca dispositivos justo antes de abrir cada lista desplegable.
        in_combo.configure(postcommand=refresh_device_lists)
        out_combo.configure(postcommand=refresh_device_lists)
        midi_out_combo.configure(postcommand=refresh_device_lists)
        # Refresco inicial al abrir el diálogo (útil en Qt, donde `postcommand`
        # puede no dispararse). El refresco periódico que había aquí (cada
        # 1.5s, varias veces) llamaba a sd.query_devices() repetidamente
        # mientras el diálogo estaba abierto, lo cual podía introducir un
        # glitch/click audible en el stream de audio activo. Cada combo sigue
        # refrescando al desplegarse (ver postcommand arriba), así que basta
        # con abrir el desplegable para ver dispositivos recién conectados.
        self._settings_overlay_device_refresh_after_id = None
        refresh_device_lists()

        show_labels_var = tk.BooleanVar(value=bool(self.config_data.get("show_keyboard_note_labels", True)))
        show_labels_chk = self._build_checkbox_row(frame, self.tr("settings_show_key_labels"), show_labels_var)
        show_labels_chk.grid(row=8, column=0, columnspan=2, sticky="w", pady=(6, 4))

        def _open_whats_new() -> None:
            self._close_settings_overlay()
            self.after(50, self.show_startup_changelog_window)

        ttk.Button(
            frame,
            text=self.tr("settings_whats_new") if hasattr(self, "tr") else "Mostrar Novedades",
            command=_open_whats_new,
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(2, 6))

        def do_save(_event: Optional[tk.Event] = None) -> str:
            midi_out_val = midi_out_var.get().strip()
            if sound_output_var.get() == "midi" and midi_out_val in ("", not_selected_label):
                midi_out_error_label.configure(text=self.tr("settings_midi_output_required"))
                return "break"
            midi_out_error_label.configure(text="")

            self.config_data["language"] = lang_var.get()
            midi_val = in_var.get().strip()
            self.config_data["midi_input"] = "" if midi_val == not_selected_label else midi_val
            audio_val = out_var.get().strip()
            self.config_data["audio_output"] = "" if audio_val == not_selected_label else audio_val
            self.config_data["midi_output"] = "" if midi_out_val == not_selected_label else midi_out_val
            self.config_data["sound_preset"] = piano_sound_label_to_id.get(piano_sound_var.get(), "acoustic")
            self.config_data["guitar_sound_preset"] = guitar_sound_label_to_id.get(guitar_sound_var.get(), "steel_clean")
            self.config_data["show_keyboard_note_labels"] = bool(show_labels_var.get())
            self.config_data["sound_output"] = sound_output_var.get()
            self.sound_output = sound_output_var.get()
            self.audio_engine.set_preset(str(self.config_data["sound_preset"]))
            self.audio_engine.set_guitar_preset(str(self.config_data["guitar_sound_preset"]))
            self.apply_ui_language()
            self.save_config()
            self.connect_ports()
            self.redraw_guitar_fretboard()
            self.update_music_views()
            self._close_settings_overlay()
            return "break"

        def close_dialog(_event: Optional[tk.Event] = None) -> str:
            self._close_settings_overlay()
            return "break"

        frame.columnconfigure(1, weight=1)

        action_bg = getattr(self, "color_surface_alt", "#2f3a4b")
        button_bg = getattr(self, "color_card", "#3a4452")
        action_border = getattr(self, "color_border", "#56627a")
        action_btn_bg = getattr(self, "color_card_hover", "#465465")
        action_btn_hover = getattr(self, "color_border_hover", "#6a7a98")
        action_fg = getattr(self, "color_text", "#e9edf2")
        accent = getattr(self, "color_accent", "#f3bf2f")
        buttons_bg = tk.Frame(dialog, bg=action_bg, highlightthickness=0)
        buttons_bg.setObjectName("settingsActionsPanel")
        buttons_bg.setStyleSheet(
            f"#settingsActionsPanel {{ background-color: {action_bg}; border: none; }}"
        )
        buttons_bg.grid(row=1, column=0, sticky="ew")

        cancel_btn = ttk.Button(buttons_bg, text=self.tr("button_cancel"), command=self._close_settings_overlay)
        cancel_btn.setObjectName("settingsCancelButton")
        save_btn = ttk.Button(buttons_bg, text=self.tr("button_save"), command=do_save)
        save_btn.setObjectName("settingsSaveButton")

        _btn_row = QHBoxLayout(buttons_bg)
        _btn_row.setContentsMargins(14, 6, 14, 14)
        _btn_row.setSpacing(10)
        _btn_row.addWidget(cancel_btn)
        _btn_row.addWidget(save_btn)
        _btn_row.addStretch(1)
        build_muted = getattr(self, "color_muted", "#a8b6c8")
        ff = getattr(self, "ui_font_family", "Helvetica")
        build_line = ttk.Label(
            buttons_bg,
            text=self.tr("settings_build_line").format(name=desktop_build_display_name()),
            font=(ff, 11),
            foreground=build_muted,
        )
        _btn_row.addWidget(build_line)

        _btn_base = (
            f"background-color: {button_bg}; color: {action_fg}; border-radius: 10px; "
            f"padding: 6px 14px; min-width: 80px; min-height: 28px; font-weight: 600;"
        )
        _btn_hover = f"background-color: {action_btn_hover};"
        _btn_pressed = f"background-color: {action_bg};"
        cancel_btn.setStyleSheet(
            f"QPushButton {{ {_btn_base} border: 1px solid {action_border}; }}"
            f" QPushButton:hover {{ {_btn_hover} border: 1px solid {action_btn_hover}; }}"
            f" QPushButton:pressed {{ {_btn_pressed} }}"
        )
        save_btn.setStyleSheet(
            f"QPushButton {{ {_btn_base} border: 1px solid {accent}; }}"
            f" QPushButton:hover {{ {_btn_hover} border: 1px solid {accent}; }}"
            f" QPushButton:pressed {{ {_btn_pressed} }}"
        )

        dialog.bind("<Escape>", close_dialog)
        dialog.bind("<Return>", do_save)
        frame.bind("<Escape>", close_dialog)
        frame.bind("<Return>", do_save)
        self._settings_save_callback = do_save
        self._qt_style_settings_form(frame)
        dialog.focus_set()
        dialog.transient(self)
        dialog.grab_set()
        fit_settings_dialog_to_content()
        dialog.show()
    def _close_settings_overlay(self) -> None:
        if self.settings_overlay is not None:
            self.settings_overlay.destroy()
            self.settings_overlay = None
        aid = getattr(self, "_settings_overlay_device_refresh_after_id", None)
        if aid is not None:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
            self._settings_overlay_device_refresh_after_id = None
        self._settings_overlay_opened_ts = 0.0
        self._settings_save_callback = None
