from __future__ import annotations

import time
import midichords.qt.tk_compat as tk
import midichords.qt.tkfont_compat as tkfont
import midichords.qt.ttk_compat as ttk
from typing import Any, Optional

from midichords.ui.widgets_qt import GrayRoundedButton, GreenRoundedButton, PlayTransportButton, RoundedChoiceButton, RoundedPanel


class UiMixin:
    def _available_mode_keys(self) -> list[str]:
        modes = ["detection", "generation", "circle_fifths", "scales", "metronome"]
        if bool(getattr(self, "tuner_enabled", True)):
            modes.append("tuner")
        return modes

    def _draw_vertical_gradient(self, canvas: tk.Canvas, color_top: str, color_bottom: str) -> None:
        def hex_to_rgb(color: str) -> tuple[int, int, int]:
            color = color.lstrip("#")
            return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

        r1, g1, b1 = hex_to_rgb(color_top)
        r2, g2, b2 = hex_to_rgb(color_bottom)
        width = max(1, int(canvas.winfo_width()))
        height = max(1, int(canvas.winfo_height()))
        steps = max(1, height - 1)

        canvas.delete("bg_gradient")
        for i in range(height):
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="bg_gradient")
        canvas.lower("bg_gradient")

    def _set_generation_toolbar_layout(self, show_instrument_buttons: bool) -> None:
        self.generation_accidental_switch.pack_forget()
        self.generation_accidental_switch.pack(side=tk.LEFT, padx=(0, 10))
        if show_instrument_buttons:
            self.instrument_view_switch_side.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        else:
            self.instrument_view_switch_side.pack_forget()

    def _show_generation_instrument_buttons(self) -> None:
        if not hasattr(self, "instrument_view_switch_side"):
            return
        self.scale_mode_piano_btn.pack_forget()
        self.scale_mode_guitar_btn.pack_forget()
        self.piano_view_btn.pack_forget()
        self.guitar_view_btn.pack_forget()
        self.piano_view_btn.pack(side=tk.TOP, pady=(0, 8))
        self.guitar_view_btn.pack(side=tk.TOP)

    def _show_scale_mode_buttons(self) -> None:
        if not hasattr(self, "instrument_view_switch_side"):
            return
        self.piano_view_btn.pack_forget()
        self.guitar_view_btn.pack_forget()
        self.guitar_handedness_combo.pack_forget()
        self.scale_mode_piano_btn.pack_forget()
        self.scale_mode_guitar_btn.pack_forget()
        self.scale_mode_piano_btn.pack(side=tk.TOP, pady=(0, 8))
        self.scale_mode_guitar_btn.pack(side=tk.TOP)

    def _pick_font_family(self, preferred: list[str], fallback: str) -> str:
        try:
            available = {name.lower(): name for name in tkfont.families(self)}
        except Exception:
            return fallback
        for name in preferred:
            match = available.get(name.lower())
            if match:
                return match
        return fallback

    def _setup_typography(self) -> None:
        self.color_bg = "#202834"
        self.color_bg_gradient_top = "#2a3442"
        self.color_bg_gradient_bottom = "#202834"
        self.color_topbar = "#161e2a"
        self.color_surface = "#182535"
        self.color_surface_alt = "#2f3a4b"
        self.color_card = "#3a4452"
        self.color_card_hover = "#465465"
        self.color_border = "#56627a"
        self.color_border_hover = "#6a7a98"
        self.color_text = "#e9edf2"
        self.color_muted = "#a8b6c8"
        self.color_accent = "#f3bf2f"
        self.color_accent_soft = "#ffd45e"

        self.ui_font_family = self._pick_font_family(
            ["Avenir Next", "SF Pro Text", "Segoe UI", "Helvetica Neue"],
            "Helvetica",
        )
        self.ui_mono_font_family = self.ui_font_family

        try:
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family=self.ui_font_family, size=13)
            text_font = tkfont.nametofont("TkTextFont")
            text_font.configure(family=self.ui_font_family, size=13)
            heading_font = tkfont.nametofont("TkHeadingFont")
            heading_font.configure(family=self.ui_font_family, size=14, weight="bold")
        except Exception:
            pass

        style = ttk.Style()
        style.configure("TFrame", background=self.color_surface_alt)
        style.configure("TLabel", background=self.color_surface_alt, foreground=self.color_text, font=(self.ui_font_family, 13))
        style.configure("TLabelframe", background=self.color_surface_alt, borderwidth=0, relief=tk.FLAT)
        style.configure("TLabelframe.Label", background=self.color_surface_alt, foreground=self.color_text, font=(self.ui_font_family, 13, "bold"))
        style.configure("TButton", font=(self.ui_font_family, 13, "bold"))
        style.configure("TCheckbutton", background=self.color_surface_alt, foreground=self.color_text, font=(self.ui_font_family, 13, "bold"))
        style.configure("TCombobox", font=(self.ui_font_family, 13))
        style.configure(
            "Panel.TCombobox",
            font=(self.ui_font_family, 13),
            foreground=self.color_text,
            fieldbackground=self.color_surface,
            background=self.color_surface,
            bordercolor=self.color_border,
            lightcolor=self.color_border,
            darkcolor=self.color_border,
            arrowcolor=self.color_text,
            padding=6,
        )
        style.map(
            "Panel.TCombobox",
            foreground=[("readonly", self.color_text)],
            fieldbackground=[("readonly", self.color_surface)],
            background=[("readonly", self.color_surface)],
            bordercolor=[("readonly", self.color_border), ("focus", self.color_border_hover)],
            arrowcolor=[("readonly", self.color_text), ("active", self.color_text)],
        )

    def _qt_apply_dark_combobox_style(self, w: Any) -> None:
        """Qt (p. ej. Windows): QComboBox en panel oscuro con texto claro, como en Ajustes."""
        if not hasattr(w, "setStyleSheet"):
            return
        fg = getattr(self, "color_text", "#e9edf2")
        card = getattr(self, "color_card", "#3a4452")
        border = getattr(self, "color_border", "#56627a")
        hover_border = getattr(self, "color_border_hover", "#6a7a98")
        btn_bg = getattr(self, "color_card_hover", "#465465")
        w.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {card};
                color: {fg};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 1.2em;
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
                outline: 0;
            }}
            """
        )

    def _qt_apply_guitar_handedness_combo_style(self, w: Any) -> None:
        """Mismo criterio visual que la web: `style.css` → `#guitarHandedness` (select)."""
        if not hasattr(w, "setStyleSheet"):
            return
        # Flecha: `HandednessComboBox` la pinta en `paintEvent` (QSS `image:` en ::down-arrow no es fiable en macOS).
        # Ocultamos el subcontrol nativo para no duplicar ni mostrar rectángulos vacíos.
        # apps/web/static/style.css — .instrument-dock #guitarHandedness
        web_bg = "#17273a"
        web_border = "#4a6180"
        web_fg = "#e8effa"
        web_border_hover = "#5a7194"
        web_popup_bg = "#17273a"
        web_popup_sel = "#243a52"
        combo_h = 38
        w.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {web_bg};
                color: {web_fg};
                border: 1px solid {web_border};
                border-radius: 10px;
                padding: 0 28px 0 8px;
                min-height: 22px;
                max-height: {combo_h}px;
                font-weight: bold;
            }}
            QComboBox:hover {{
                border: 1px solid {web_border_hover};
            }}
            QComboBox:focus {{
                border: 1px solid {web_border_hover};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 26px;
                border: none;
                border-left: 1px solid {web_border};
                border-top-right-radius: 9px;
                border-bottom-right-radius: 9px;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {web_popup_bg};
                color: {web_fg};
                selection-background-color: {web_popup_sel};
                selection-color: {web_fg};
                border: 1px solid {web_border};
                outline: 0;
                border-radius: 8px;
                padding: 2px;
            }}
            """
        )
        try:
            from PySide6.QtGui import QFont

            f = w.font()
            f.setBold(True)
            w.setFont(f)
        except Exception:
            pass
        self._apply_guitar_handedness_combo_geometry(w)

    def _apply_guitar_handedness_combo_geometry(self, w: Any | None = None) -> None:
        """Tras `pack(fill=X)` el QComboBox recupera política vertical; altura como el `<select>` web (38px)."""
        combo = w if w is not None else getattr(self, "guitar_handedness_combo", None)
        if combo is None or not hasattr(combo, "setFixedHeight"):
            return
        try:
            # Web: min-width 86px; en escritorio alineamos al ancho de Piano/Guitarra (124).
            combo.setMinimumWidth(124)
        except Exception:
            pass
        try:
            combo.setFixedHeight(38)
        except Exception:
            pass
        try:
            from PySide6.QtWidgets import QSizePolicy

            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        except Exception:
            pass

    def _build_ui(self) -> None:
        self._setup_typography()
        self.configure(bg=self.color_bg)
        container = tk.Frame(self, bg=self.color_bg, bd=0, highlightthickness=0)
        container.pack(fill=tk.BOTH, expand=True)
        container.configure(padx=12, pady=12)
        unified_green_width = 200
        unified_green_height = 46
        unified_green_radius = 22

        topbar_bg = self.cget("background")
        mode_bar = tk.Frame(container, bg=topbar_bg, bd=0, highlightthickness=0)
        mode_bar.pack(fill=tk.X, pady=(0, 6))
        mode_bar.columnconfigure(0, weight=1)
        mode_bar.columnconfigure(1, weight=1)
        mode_bar.columnconfigure(2, weight=1)

        self.top_title_label = tk.Label(
            mode_bar,
            text="",
            bg=topbar_bg,
            fg=self.color_text,
            font=(self.ui_font_family, 20, "bold"),
        )
        self.top_title_label.grid(row=0, column=0, sticky="w")

        mode_center = tk.Frame(mode_bar, bg=topbar_bg, bd=0, highlightthickness=0)
        mode_center.grid(row=0, column=1)

        self.mode_trigger_var = tk.StringVar(value="")
        self._mode_picker_hover = False
        self.mode_picker_trigger = tk.Canvas(
            mode_center,
            width=320,
            height=40,
            bg=topbar_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.mode_picker_trigger.pack(side=tk.LEFT)
        self._mode_picker_text_id = self.mode_picker_trigger.create_text(
            18,
            20,
            anchor="w",
            text="",
            fill=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        self._mode_picker_arrow_id = self.mode_picker_trigger.create_text(
            0,
            20,
            anchor="e",
            text="▼",
            fill=self.color_muted,
            font=(self.ui_font_family, 15, "bold"),
        )

        def _mode_picker_points(x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
            return [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]

        def _redraw_mode_picker(_event: Optional[tk.Event] = None) -> None:
            w = max(120, int(self.mode_picker_trigger.winfo_width()))
            h = max(34, int(self.mode_picker_trigger.winfo_height()))
            self.mode_picker_trigger.delete("mode_picker_bg")
            self.mode_picker_trigger.create_polygon(
                _mode_picker_points(1, 1, w - 1, h - 1, 11),
                smooth=True,
                splinesteps=18,
                fill=self.color_surface,
                outline=(self.color_border_hover if self._mode_picker_hover else self.color_border),
                width=1.4,
                tags="mode_picker_bg",
            )
            self.mode_picker_trigger.coords(self._mode_picker_text_id, 18, h / 2)
            self.mode_picker_trigger.coords(self._mode_picker_arrow_id, w - 16, h / 2)
            self.mode_picker_trigger.tag_lower("mode_picker_bg")

        def _refresh_mode_picker_text(*_args: object) -> None:
            self.mode_picker_trigger.itemconfigure(self._mode_picker_text_id, text=self.mode_trigger_var.get())

        self.mode_picker_trigger.bind("<Configure>", _redraw_mode_picker)
        self.mode_picker_trigger.bind("<Button-1>", self._toggle_mode_selector)
        self.mode_picker_trigger.bind("<Enter>", lambda _e: (setattr(self, "_mode_picker_hover", True), _redraw_mode_picker()))
        self.mode_picker_trigger.bind("<Leave>", lambda _e: (setattr(self, "_mode_picker_hover", False), _redraw_mode_picker()))
        self.mode_trigger_var.trace_add("write", _refresh_mode_picker_text)
        _refresh_mode_picker_text()
        _redraw_mode_picker()

        self.top_right_controls = tk.Frame(mode_bar, bg=topbar_bg, bd=0, highlightthickness=0)
        self.top_right_controls.grid(row=0, column=2, sticky="e")

        self.top_right_mode_controls = tk.Frame(self.top_right_controls, bg=topbar_bg, bd=0, highlightthickness=0)
        self.top_right_mode_controls.pack(side=tk.LEFT, padx=(0, 8))

        self.config_icon_btn = tk.Label(
            self.top_right_controls,
            text="⚙",
            fg=self.color_accent,
            bg=topbar_bg,
            font=(self.ui_font_family, 18, "bold"),
            cursor="hand2",
        )
        self.config_icon_btn.pack(side=tk.LEFT)
        self.config_icon_btn.bind("<Button-1>", lambda _e: self.open_settings_dialog())
        self.config_icon_btn.bind("<Enter>", lambda _e: self.config_icon_btn.configure(fg=self.color_accent_soft))
        self.config_icon_btn.bind("<Leave>", lambda _e: self.config_icon_btn.configure(fg=self.color_accent))

        top_area = tk.Canvas(container, bg=self.color_bg, bd=0, highlightthickness=0)
        top_area.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        # Layout superior similar a web: panel izquierdo dominante y derecho secundario.
        self.left_panel = RoundedPanel(
            top_area,
            radius=12,
            bg_color=self.color_surface_alt,
            border_color=self.color_border,
            border_width=1.2,
            padding=(12, 12, 12, 12),
        )
        self.right_panel = RoundedPanel(
            top_area,
            radius=12,
            bg_color=self.color_surface_alt,
            border_color=self.color_border,
            border_width=1.2,
            # Un poco menos de aire vertical que el panel izquierdo (panel de acordes más compacto).
            padding=(10, 8, 10, 8),
        )
        def _layout_top_panels(_event: Optional[tk.Event] = None) -> None:
            self._draw_vertical_gradient(
                top_area,
                self.color_bg_gradient_top,
                self.color_bg_gradient_bottom,
            )
            w = max(1, int(top_area.winfo_width()))
            h = max(1, int(top_area.winfo_height()))
            gap = 12
            usable_w = max(1, w - gap)
            left_w = max(1, int(usable_w * 0.58))
            # Ancho mínimo panel derecho para que no se corten Notas ni Intervalos en Escalas.
            right_w = max(580, usable_w - left_w)
            left_w = max(1, usable_w - gap - right_w)
            self.left_panel.place(x=0, y=0, width=left_w, height=h)
            self.right_panel.place(x=left_w + gap, y=0, width=right_w, height=h)

        top_area.bind("<Configure>", _layout_top_panels)
        _layout_top_panels()

        self.staff_canvas = tk.Canvas(
            self.left_panel.content,
            bg="#0f1621",
            highlightthickness=1,
            highlightbackground="#3a4558",
        )
        self.left_panel_title_label = tk.Label(
            self.left_panel.content,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            font=(self.ui_font_family, 15, "bold"),
            anchor="w",
        )
        self.left_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 5))
        self.staff_canvas.pack(fill=tk.BOTH, expand=True)
        self.detection_help_label = tk.Label(
            self.left_panel.content,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            justify="left",
            anchor="w",
            wraplength=520,
            font=(self.ui_font_family, 16),
        )

        self.right_panel_title_label = tk.Label(
            self.right_panel.content,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            font=(self.ui_font_family, 15, "bold"),
            anchor="w",
        )
        self.right_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 5))
        self.right_side_panel = tk.Frame(self.right_panel.content, bg=self.color_surface_alt, bd=0, highlightthickness=0, padx=0)
        self.right_side_panel.pack(fill=tk.BOTH, expand=True)
        self.right_side_panel.columnconfigure(0, weight=1)
        self.right_side_panel.rowconfigure(0, weight=1)

        self.chord_panel = tk.Frame(
            self.right_side_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
        )
        self.chord_panel.grid(row=0, column=0, sticky="nsew")

        self.tab_detection_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=4,
            pady=3,
        )
        self.tab_generation_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        self.tab_circle_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        self.tab_scale_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        self.tab_metronome_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=6,
        )
        self.tab_tuner_frame = tk.Frame(
            self.chord_panel,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
            padx=6,
            pady=6,
        )
        self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)
        # Qt: los frames hijos no empaquetados siguen visibles por defecto y taparían la pestaña activa.
        for _hidden_tab in (
            self.tab_generation_frame,
            self.tab_circle_frame,
            self.tab_scale_frame,
            self.tab_metronome_frame,
            self.tab_tuner_frame,
        ):
            _hidden_tab.setVisible(False)

        self.chord_title_label = tk.Label(
            self.tab_detection_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 22, "bold"),
        )
        self.chord_title_label.pack(anchor="w", pady=(0, 2))
        self.detection_controls_row = tk.Frame(self.tab_detection_frame, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        # El botón MIDI solo ocupa el ancho del texto (no expande a todo el panel).
        # Margen inferior para separar los botones del bloque de resultados.
        self.detection_controls_row.pack(fill=tk.X, anchor="w", pady=(0, 2))
        # Igual que generación: el audio va en ButtonPress + bind_all release; no llamar command al soltar (doble note_on en Qt).
        self.detection_play_btn = PlayTransportButton(
            self.detection_controls_row,
            command=lambda: None,
            width=58,
            height=34,
        )
        self.detection_play_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.detection_play_btn.bind("<ButtonPress-1>", self._on_detection_play_press)
        self.detection_clear_btn = GrayRoundedButton(
            self.detection_controls_row,
            text="",
            command=self._clear_detection_panel,
            font_family=self.ui_font_family,
            width=104,
            height=34,
            radius=14,
            font_size=15,
        )
        self.detection_clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.detection_midi_sound_toggle_btn = GrayRoundedButton(
            self.detection_controls_row,
            text="",
            command=self._toggle_midi_input_sound,
            font_family=self.ui_font_family,
            width=120,
            height=34,
            radius=14,
            font_size=14,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
            shrink_to_text=True,
        )
        self.detection_midi_sound_toggle_btn.pack(side=tk.LEFT)

        self.chord_var = tk.StringVar(value="-")
        self.detection_result_canvas = tk.Canvas(
            self.tab_detection_frame,
            bg=self.color_surface_alt,
            height=250,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        # Margen superior para evitar que el subpanel toque visualmente la fila de botones.
        self.detection_result_canvas.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        self.detection_result_inner = tk.Frame(
            self.detection_result_canvas,
            bg="#17273a",
            bd=0,
            highlightthickness=0,
        )
        self._detection_result_window_id = self.detection_result_canvas.create_window(
            0,
            0,
            anchor="nw",
            window=self.detection_result_inner,
        )

        def redraw_detection_result_block(_event: Optional[tk.Event] = None) -> None:
            w = max(40, int(self.detection_result_canvas.winfo_width()))
            h = max(180, int(self.detection_result_canvas.winfo_height()))
            self.detection_result_canvas.delete("result_block_bg")
            self.detection_result_canvas.create_rectangle(
                1,
                1,
                w - 1,
                h - 1,
                fill="#17273a",
                outline="#73829a",
                width=1,
                dash=(3, 3),
                tags="result_block_bg",
            )
            pad = 8
            self.detection_result_canvas.coords(self._detection_result_window_id, pad, pad)
            self.detection_result_canvas.itemconfigure(
                self._detection_result_window_id,
                width=max(1, w - (pad * 2)),
                height=max(1, h - (pad * 2)),
            )
            self.detection_result_canvas.tag_lower("result_block_bg")

        self.detection_result_canvas.bind("<Configure>", redraw_detection_result_block)
        redraw_detection_result_block()

        self.chord_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.chord_var,
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 42, "bold"),
        )
        self.chord_label.pack(anchor="w", pady=(0, 2))

        self.notes_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 16, "bold"),
        )
        self.notes_caption_label.pack(anchor="w")
        self.notes_var = tk.StringVar(value="-")
        self.notes_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 16),
        )
        self.notes_label.pack(anchor="w", pady=(1, 1))
        self.intervals_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 16, "bold"),
        )
        self.intervals_caption_label.pack(anchor="w")
        self.intervals_var = tk.StringVar(value="-")
        self.intervals_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 16),
        )
        self.intervals_label.pack(anchor="w", pady=(1, 1))
        self.extra_notes_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 16, "bold"),
        )
        self.extra_notes_caption_label.pack(anchor="w", pady=(0, 0))
        self.extra_notes_var = tk.StringVar(value="")
        self.extra_notes_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.extra_notes_var,
            bg="#17273a",
            fg="#ff5a5f",
            wraplength=420,
            font=(self.ui_mono_font_family, 16, "bold"),
        )
        self.extra_notes_label.pack(anchor="w", pady=(0, 1))

        self.generated_title_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 20, "bold"),
        )
        self.generated_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 6))

        self.generation_root_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_root_label.grid(row=1, column=0, sticky="w", pady=(0, 5), padx=(0, 8))
        self.generation_root_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_root_dialog,
            font_family=self.ui_font_family,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_root_btn.grid(row=1, column=1, sticky="ew", pady=(0, 5))

        self.generation_variant_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_variant_label.grid(row=2, column=0, sticky="w", pady=(0, 5), padx=(0, 8))
        self.generation_variant_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_variant_dialog,
            font_family=self.ui_font_family,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_variant_btn.grid(row=2, column=1, sticky="ew", pady=(0, 5))

        self.generation_inversion_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_inversion_label.grid(row=3, column=0, sticky="w", pady=(0, 4), padx=(0, 8))
        self.generation_inversion_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_inversion_dialog,
            font_family=self.ui_font_family,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_inversion_btn.grid(row=3, column=1, sticky="ew", pady=(0, 4))

        self.generated_chord_var = tk.StringVar(value="-")
        # Un solo recuadro (como web): etiqueta + nombre. Borde vía QSS con padding en `Widget._apply_tk_frame_surface`.
        self.staff_generated_chord_frame = tk.Frame(
            self.left_panel.content,
            bg="#1a2330",
            bd=0,
            highlightthickness=0,
        )
        self.staff_generated_chord_caption = tk.Label(
            self.staff_generated_chord_frame,
            text="",
            bg="transparent",
            fg=self.color_muted,
            font=(self.ui_font_family, 15),
            highlightthickness=0,
        )
        self.staff_generated_chord_caption.pack(side=tk.LEFT, padx=(2, 4), pady=2)
        self.staff_generated_chord_value = tk.Label(
            self.staff_generated_chord_frame,
            textvariable=self.generated_chord_var,
            bg="transparent",
            fg=self.color_accent,
            font=(self.ui_font_family, 20, "bold"),
            anchor="w",
            highlightthickness=0,
        )
        self.staff_generated_chord_value.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=2, padx=(0, 2))
        # Borde en el frame; el hueco interior lo marca el layout (Qt a veces no respeta padding QSS para hijos).
        try:
            _sf = self.staff_generated_chord_frame
            if hasattr(_sf, "setStyleSheet"):
                _sf.setStyleSheet(
                    "background-color: #1a2330; border: 1px solid #4a5668;"
                )
            from PySide6.QtWidgets import QHBoxLayout

            _lay = _sf.layout()
            if isinstance(_lay, QHBoxLayout):
                _lay.setContentsMargins(8, 4, 8, 4)
        except Exception:
            pass

        self.generated_chord_row = tk.Frame(
            self.tab_generation_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.generated_chord_row.grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 3))

        self.generation_play_btn = PlayTransportButton(
            self.generated_chord_row,
            command=lambda: None,
            width=58,
            height=34,
        )
        self.generation_play_btn.pack(side=tk.LEFT)
        self.generation_play_btn.bind("<ButtonPress-1>", self._on_generation_play_press)
        self.bind_all("<ButtonRelease-1>", self._on_global_mouse_release)

        self.generation_result_canvas = tk.Canvas(
            self.tab_generation_frame,
            bg=self.color_surface_alt,
            width=520,
            height=160,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        # En Qt, si la altura de la ventana cambia, el QGridLayout puede repartir el "stretch"
        # entre filas y acabar variando los huecos entre los botones superiores.
        # Forzamos que la fila del canvas (row=5) sea la que absorbe el cambio de tamaño.
        self.generation_result_canvas.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(2, 2))
        self.generation_result_inner = tk.Frame(
            self.generation_result_canvas,
            bg="#17273a",
            bd=0,
            highlightthickness=0,
        )
        self._generation_result_window_id = self.generation_result_canvas.create_window(
            0,
            0,
            anchor="nw",
            window=self.generation_result_inner,
        )

        def redraw_generation_result_block(_event: Optional[tk.Event] = None) -> None:
            w = max(40, int(self.generation_result_canvas.winfo_width()))
            h = max(120, int(self.generation_result_canvas.winfo_height()))
            self.generation_result_canvas.delete("result_block_bg")
            self.generation_result_canvas.create_rectangle(
                1,
                1,
                w - 1,
                h - 1,
                fill="#17273a",
                outline="#73829a",
                width=1,
                dash=(3, 3),
                tags="result_block_bg",
            )
            pad = 10
            self.generation_result_canvas.coords(self._generation_result_window_id, pad, pad)
            self.generation_result_canvas.itemconfigure(
                self._generation_result_window_id,
                width=max(1, w - (pad * 2)),
                height=max(1, h - (pad * 2)),
            )
            self.generation_result_canvas.tag_lower("result_block_bg")

        self.generation_result_canvas.bind("<Configure>", redraw_generation_result_block)
        redraw_generation_result_block()

        self.generated_notes_caption_label = tk.Label(
            self.generation_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        self.generated_notes_caption_label.pack(anchor="w")
        self.generated_notes_var = tk.StringVar(value="-")
        self.generated_notes_label = tk.Label(
            self.generation_result_inner,
            textvariable=self.generated_notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 15),
        )
        self.generated_notes_label.pack(anchor="w", pady=(3, 4))
        self.generated_intervals_caption_label = tk.Label(
            self.generation_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        self.generated_intervals_caption_label.pack(anchor="w")
        self.generated_intervals_var = tk.StringVar(value="-")
        self.generated_intervals_label = tk.Label(
            self.generation_result_inner,
            textvariable=self.generated_intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 15),
        )
        self.generated_intervals_label.pack(anchor="w", pady=(3, 0))

        self.tab_generation_frame.columnconfigure(0, weight=0)
        self.tab_generation_frame.columnconfigure(1, weight=1)
        # Row stretching: que solo el subpanel de resultados (row=5) crezca con la altura.
        self.tab_generation_frame.rowconfigure(0, weight=0)
        self.tab_generation_frame.rowconfigure(1, weight=0)
        self.tab_generation_frame.rowconfigure(2, weight=0)
        self.tab_generation_frame.rowconfigure(3, weight=0)
        self.tab_generation_frame.rowconfigure(4, weight=0)
        self.tab_generation_frame.rowconfigure(5, weight=1)

        self.circle_title_label = tk.Label(
            self.tab_circle_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 20, "bold"),
        )
        self.circle_title_label.pack(anchor="w", pady=(0, 4))
        self.circle_canvas_shell = tk.Frame(self.tab_circle_frame, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.circle_canvas_shell.pack(fill=tk.BOTH, expand=True)
        self.circle_canvas = tk.Canvas(
            self.circle_canvas_shell,
            bg="#1a2330",
            width=480,
            height=480,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.circle_canvas.pack(fill=tk.BOTH, expand=True)
        self.circle_play_btn = PlayTransportButton(
            self.circle_canvas_shell,
            command=lambda: None,
            width=58,
            height=34,
        )
        # Mismo criterio que la web: margen desde la esquina superior izquierda del área del círculo.
        self.circle_play_btn.place(x=10, y=10, anchor="nw", width=58, height=34)
        if hasattr(self.circle_play_btn, "raise_"):
            self.circle_play_btn.raise_()
        elif hasattr(self.circle_play_btn, "lift"):
            self.circle_play_btn.lift()
        self.circle_play_btn.bind("<ButtonPress-1>", self._on_generation_play_press)
        self.circle_canvas.bind("<Configure>", self._on_circle_canvas_configure)
        self.circle_canvas.bind("<Button-1>", self._on_circle_canvas_click)

        self.scale_panel_title_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 20, "bold"),
        )
        self.scale_panel_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 6))

        self.scale_controls_row = tk.Frame(
            self.tab_scale_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.scale_controls_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 8))
        self.scale_controls_row.columnconfigure(2, weight=1)
        self.scale_play_btn = PlayTransportButton(
            self.scale_controls_row,
            command=self._toggle_scale_play,
            width=58,
            height=34,
        )
        self.scale_play_btn.grid(row=0, column=0, sticky="w")
        self.scale_play_btn.bind("<space>", lambda _e: "break")
        self.scale_mode_metronome_btn = GrayRoundedButton(
            self.scale_controls_row,
            text="⏱",
            command=lambda: self._set_scale_play_mode("metronome"),
            font_family=self.ui_font_family,
            width=48,
            height=34,
            radius=14,
            font_size=16,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
        )
        self.scale_mode_metronome_btn.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.scale_metronome_volume_frame = tk.Frame(
            self.scale_controls_row,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.scale_metronome_volume_frame.columnconfigure(1, weight=1)
        self.scale_metronome_volume_label = tk.Label(
            self.scale_metronome_volume_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            font=(self.ui_font_family, 13),
            anchor="w",
            width=8,
        )
        self.scale_metronome_volume_label.grid(row=0, column=0, sticky="w")
        self.scale_metronome_volume_slider = tk.Canvas(
            self.scale_metronome_volume_frame,
            width=220,
            height=34,
            bg=self.color_surface_alt,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.scale_metronome_volume_slider.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.scale_metronome_volume_slider.bind("<Configure>", lambda _e: self._draw_scale_metronome_volume_slider())
        self.scale_metronome_volume_slider.bind("<Button-1>", self._on_scale_metronome_volume_slider_interact)
        self.scale_metronome_volume_slider.bind("<B1-Motion>", self._on_scale_metronome_volume_slider_interact)
        self.scale_metronome_volume_var = tk.StringVar(value="100%")
        self.scale_metronome_volume_value_label = tk.Label(
            self.scale_metronome_volume_frame,
            textvariable=self.scale_metronome_volume_var,
            bg=self.color_surface_alt,
            fg="#f3bf2f",
            font=(self.ui_font_family, 12, "bold"),
            width=7,
            anchor="e",
        )
        self.scale_metronome_volume_value_label.grid(row=0, column=2, sticky="e")

        self.scale_bpm_row = tk.Frame(
            self.tab_scale_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.scale_bpm_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.scale_bpm_row.columnconfigure(1, weight=1)
        panel_bg = self.color_surface_alt
        self.scale_bpm_minus_btn = tk.Canvas(
            self.scale_bpm_row,
            width=34,
            height=34,
            bg=panel_bg,
            highlightthickness=0,
            bd=0,
        )
        self.scale_bpm_minus_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._draw_scale_bpm_step_button(self.scale_bpm_minus_btn, "−")
        self.scale_bpm_minus_btn.bind("<Configure>", lambda _e: self._draw_scale_bpm_step_button(self.scale_bpm_minus_btn, "−"))
        self.scale_bpm_minus_btn.bind("<Button-1>", self._on_scale_bpm_minus)

        self.scale_bpm_slider = tk.Canvas(
            self.scale_bpm_row,
            # Qt: si el Canvas no tiene ancho mínimo solicitado, el layout puede
            # colapsarlo (y entonces no se ve el "slice"/slider del BPM).
            width=1,
            height=34,
            bg=panel_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.scale_bpm_slider.grid(row=0, column=1, sticky="ew")
        self.scale_bpm_slider.bind("<Configure>", lambda _e: self._draw_scale_bpm_slider())
        self.scale_bpm_slider.bind("<Button-1>", self._on_scale_bpm_slider_interact)
        self.scale_bpm_slider.bind("<B1-Motion>", self._on_scale_bpm_slider_interact)

        self.scale_bpm_plus_btn = tk.Canvas(
            self.scale_bpm_row,
            width=34,
            height=34,
            bg=panel_bg,
            highlightthickness=0,
            bd=0,
        )
        self.scale_bpm_plus_btn.grid(row=0, column=2, sticky="e", padx=(8, 8))
        self._draw_scale_bpm_step_button(self.scale_bpm_plus_btn, "+")
        self.scale_bpm_plus_btn.bind("<Configure>", lambda _e: self._draw_scale_bpm_step_button(self.scale_bpm_plus_btn, "+"))
        self.scale_bpm_plus_btn.bind("<Button-1>", self._on_scale_bpm_plus)

        self.scale_bpm_value_label = tk.Label(
            self.scale_bpm_row,
            text="120 BPM",
            bg=panel_bg,
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="e",
        )
        self.scale_bpm_value_label.grid(row=0, column=3, sticky="e")
        self._set_scale_bpm(self.scale_bpm_value, save=False)

        self.scale_tonic_selector_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.scale_tonic_selector_label.grid(row=1, column=0, sticky="w", pady=(0, 5), padx=(0, 8))
        self.scale_tonic_btn = GrayRoundedButton(
            self.tab_scale_frame,
            text="C",
            command=self.open_scale_tonic_dialog,
            font_family=self.ui_font_family,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.scale_tonic_btn.grid(row=1, column=1, sticky="ew", pady=(0, 5))

        self.scale_type_selector_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.scale_type_selector_label.grid(row=2, column=0, sticky="w", pady=(0, 5), padx=(0, 8))
        self.scale_type_btn = GrayRoundedButton(
            self.tab_scale_frame,
            text=self.scale_pattern_name,
            command=self.open_scale_type_dialog,
            font_family=self.ui_font_family,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.scale_type_btn.grid(row=2, column=1, sticky="ew", pady=(0, 5))

        # Selector de octavas (piano only)
        self.scale_octave_selector_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.scale_octave_selector_label.grid(row=3, column=0, sticky="w", pady=(0, 5), padx=(0, 8))

        octave_buttons_frame = tk.Frame(
            self.tab_scale_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        octave_buttons_frame.grid(row=3, column=1, sticky="ew", pady=(0, 5))
        octave_buttons_frame.columnconfigure(0, weight=1)
        octave_buttons_frame.columnconfigure(1, weight=1)
        octave_buttons_frame.columnconfigure(2, weight=1)

        self.scale_octave_buttons = []
        for oct in [1, 2, 3]:
            btn = GrayRoundedButton(
                octave_buttons_frame,
                text=f"{oct}",
                command=lambda o=oct: self._set_scale_octaves(o),
                font_family=self.ui_font_family,
                width=100,
                height=40,
                radius=16,
                font_size=15,
                text_color="#e6edf7",
                selected_text_color="#1a222d",
            )
            btn.grid(row=0, column=oct - 1, sticky="ew", padx=2)
            btn.set_selected(oct == 1)  # Default: 1 octava
            self.scale_octave_buttons.append(btn)

        self.scale_result_row = tk.Frame(
            self.tab_scale_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.scale_result_row.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(2, 2))
        self.scale_result_row.columnconfigure(0, weight=1)
        self.scale_result_row.rowconfigure(0, weight=1)
        self.scale_result_canvas = tk.Canvas(
            self.scale_result_row,
            bg=self.color_surface_alt,
            height=220,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.scale_result_canvas.grid(row=0, column=0, sticky="nsew")
        self.scale_result_inner = tk.Frame(
            self.scale_result_canvas,
            bg="#17273a",
            bd=0,
            highlightthickness=0,
        )
        self._scale_result_window_id = self.scale_result_canvas.create_window(
            0,
            0,
            anchor="nw",
            window=self.scale_result_inner,
        )
        self.scale_result_inner.bind(
            "<Configure>",
            lambda _e: self.scale_result_canvas.configure(scrollregion=self.scale_result_canvas.bbox("all")),
        )

        def redraw_scale_result_block(_event: Optional[tk.Event] = None) -> None:
            w = max(40, int(self.scale_result_canvas.winfo_width()))
            h = max(120, int(self.scale_result_canvas.winfo_height()))
            self.scale_result_canvas.delete("result_block_bg")
            self.scale_result_canvas.create_rectangle(
                1,
                1,
                w - 1,
                h - 1,
                fill="#17273a",
                outline="#73829a",
                width=1,
                dash=(3, 3),
                tags="result_block_bg",
            )
            pad = 10
            self.scale_result_canvas.coords(self._scale_result_window_id, pad, pad)
            self.scale_result_canvas.itemconfigure(
                self._scale_result_window_id,
                width=max(1, w - (pad * 2)),
                height=max(1, h - (pad * 2)),
            )
            self.scale_result_canvas.tag_lower("result_block_bg")

        self.scale_result_canvas.bind("<Configure>", redraw_scale_result_block)
        redraw_scale_result_block()

        self.scale_name_var = tk.StringVar(value="-")
        self.scale_name_label = tk.Label(
            self.scale_result_inner,
            textvariable=self.scale_name_var,
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 28, "bold"),
        )
        self.scale_name_label.pack(anchor="w", pady=(0, 5))

        self.scale_notes_caption_label = tk.Label(
            self.scale_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        self.scale_notes_caption_label.pack(anchor="w")
        self.scale_notes_var = tk.StringVar(value="-")
        self.scale_notes_label = tk.Label(
            self.scale_result_inner,
            textvariable=self.scale_notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 15),
        )
        self.scale_notes_label.pack(anchor="w", pady=(3, 4))

        self.scale_intervals_caption_label = tk.Label(
            self.scale_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        self.scale_intervals_caption_label.pack(anchor="w")
        self.scale_intervals_var = tk.StringVar(value="-")
        self.scale_intervals_label = tk.Label(
            self.scale_result_inner,
            textvariable=self.scale_intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 15),
        )
        self.scale_intervals_label.pack(anchor="w", pady=(3, 0))

        self.tab_scale_frame.columnconfigure(0, weight=0)
        self.tab_scale_frame.columnconfigure(1, weight=1)
        self.tab_scale_frame.rowconfigure(5, weight=1)

        self._metronome_scroll_outer = tk.Frame(
            self.tab_metronome_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self._metronome_scroll_outer.pack(fill=tk.BOTH, expand=True)
        self._metronome_form_root = self._build_scrollable_area(
            self._metronome_scroll_outer,
            bg=self.color_surface_alt,
            padx=0,
            pady=(0, 8),
        )
        # Qt/Windows: ttk.Label → QLabel sin fg; QCheckBox/QSpinBox nativos en negro sobre gris.
        self._qt_append_dark_native_controls_stylesheet(self._metronome_form_root)
        self._qt_style_scroll_area_viewport(self._metronome_form_root)

        self.metronome_title_row = ttk.Frame(self._metronome_form_root)
        self.metronome_title_row.grid(row=0, column=0, sticky="ew", pady=(4, 10))
        # Play + MIDI a la izquierda; columna 2 absorbe el hueco (el MIDI no se estira).
        self.metronome_title_row.columnconfigure(2, weight=1)
        self.metronome_play_btn = PlayTransportButton(
            self.metronome_title_row,
            command=self._toggle_metronome,
            width=58,
            height=34,
        )
        self.metronome_play_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.metronome_play_btn.bind("<space>", lambda _e: "break")
        self.metronome_midi_sound_toggle_btn = GrayRoundedButton(
            self.metronome_title_row,
            text="",
            command=self._toggle_midi_input_sound,
            font_family=self.ui_font_family,
            width=120,
            height=34,
            radius=14,
            font_size=12,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
            shrink_to_text=True,
        )
        self.metronome_midi_sound_toggle_btn.grid(row=0, column=1, sticky="w")

        self.metronome_volume_row = ttk.Frame(self._metronome_form_root)
        self.metronome_volume_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.metronome_volume_row.columnconfigure(2, weight=1)
        self.metronome_volume_label = ttk.Label(
            self.metronome_volume_row,
            text="",
            font=(self.ui_font_family, 15, "bold"),
            anchor="e",
            fg=self.color_text,
        )
        self.metronome_volume_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=(0, 0))
        self.metronome_volume_minus_btn = tk.Canvas(self.metronome_volume_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_volume_minus_btn.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.metronome_volume_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_volume_minus_btn, "−"))
        self.metronome_volume_minus_btn.bind("<Button-1>", self._on_metronome_volume_minus)
        # En Qt: si el Canvas no tiene ancho solicitado, el layout puede colapsarlo a 0 px
        # (y el slider se dibuja pero no se ve). Añadimos un width mínimo.
        self.metronome_volume_slider_canvas = tk.Canvas(
            self.metronome_volume_row,
            # Qt: dejamos un mínimo muy bajo para que el widget pueda crecer con
            # el ancho del panel (la columna 1 tiene weight=1).
            width=120,
            height=34,
            bg=self.color_surface_alt,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.metronome_volume_slider_canvas.grid(row=0, column=2, sticky="ew")
        self.metronome_volume_slider_canvas.bind("<Configure>", lambda _e: self._draw_metronome_volume_slider())
        self.metronome_volume_slider_canvas.bind("<Button-1>", self._on_metronome_volume_slider_interact)
        self.metronome_volume_slider_canvas.bind("<B1-Motion>", self._on_metronome_volume_slider_interact)
        self.metronome_volume_plus_btn = tk.Canvas(self.metronome_volume_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_volume_plus_btn.grid(row=0, column=3, sticky="e", padx=(8, 0))
        self.metronome_volume_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_volume_plus_btn, "+"))
        self.metronome_volume_plus_btn.bind("<Button-1>", self._on_metronome_volume_plus)
        self.metronome_volume_var = tk.StringVar(value="")
        self.metronome_volume_value_label = tk.Label(
            self.metronome_volume_row,
            textvariable=self.metronome_volume_var,
            bg=self.color_surface_alt,
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="center",
        )
        self.metronome_volume_value_label.grid(row=1, column=2, sticky="", pady=(4, 0))

        self.metronome_slider_row = ttk.Frame(self._metronome_form_root)
        self.metronome_slider_row.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        self.metronome_slider_row.columnconfigure(2, weight=1)
        self.metronome_tempo_label = ttk.Label(
            self.metronome_slider_row,
            text="",
            font=(self.ui_font_family, 15, "bold"),
            anchor="e",
            fg=self.color_text,
        )
        self.metronome_tempo_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=(0, 0))
        self.metronome_minus_btn = tk.Canvas(self.metronome_slider_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_minus_btn.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.metronome_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_minus_btn, "−"))
        self.metronome_minus_btn.bind("<Button-1>", self._on_metronome_bpm_minus)
        self.metronome_slider_canvas = tk.Canvas(
            self.metronome_slider_row,
            width=120,
            height=34,
            bg=self.color_surface_alt,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.metronome_slider_canvas.grid(row=0, column=2, sticky="ew")
        self.metronome_slider_canvas.bind("<Configure>", lambda _e: self._draw_metronome_bpm_slider())
        self.metronome_slider_canvas.bind("<Button-1>", self._on_metronome_slider_interact)
        self.metronome_slider_canvas.bind("<B1-Motion>", self._on_metronome_slider_interact)
        self.metronome_plus_btn = tk.Canvas(self.metronome_slider_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_plus_btn.grid(row=0, column=3, sticky="e", padx=(8, 0))
        self.metronome_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_plus_btn, "+"))
        self.metronome_plus_btn.bind("<Button-1>", self._on_metronome_bpm_plus)
        self.metronome_bpm_var = tk.StringVar(value="")
        self.metronome_bpm_label = tk.Label(
            self.metronome_slider_row,
            textvariable=self.metronome_bpm_var,
            bg=self.color_surface_alt,
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            anchor="center",
        )
        self.metronome_bpm_label.grid(row=1, column=2, sticky="", pady=(4, 0))

        self.metronome_meter_row = ttk.Frame(self._metronome_form_root)
        self.metronome_meter_row.grid(row=3, column=0, sticky="ew", pady=(4, 8))
        self.metronome_meter_row.columnconfigure(2, weight=1)
        self.metronome_meter_label = ttk.Label(
            self.metronome_meter_row,
            text="",
            font=(self.ui_font_family, 15, "bold"),
            anchor="e",
            fg=self.color_text,
        )
        self.metronome_meter_label.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=(0, 0))
        self.metronome_meter_minus_btn = tk.Canvas(self.metronome_meter_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_meter_minus_btn.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.metronome_meter_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_meter_minus_btn, "−"))
        self.metronome_meter_minus_btn.bind("<Button-1>", self._on_metronome_meter_minus)
        self.metronome_meter_canvas = tk.Canvas(
            self.metronome_meter_row,
            width=120,
            height=34,
            bg=self.color_surface_alt,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.metronome_meter_canvas.grid(row=0, column=2, sticky="ew")
        self.metronome_meter_canvas.bind("<Configure>", lambda _e: self._draw_metronome_meter_slider())
        self.metronome_meter_canvas.bind("<Button-1>", self._on_metronome_meter_slider_interact)
        self.metronome_meter_canvas.bind("<B1-Motion>", self._on_metronome_meter_slider_interact)
        self.metronome_meter_plus_btn = tk.Canvas(self.metronome_meter_row, width=34, height=34, bg=self.color_surface_alt, highlightthickness=0, bd=0)
        self.metronome_meter_plus_btn.grid(row=0, column=3, sticky="e", padx=(8, 0))
        self.metronome_meter_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_meter_plus_btn, "+"))
        self.metronome_meter_plus_btn.bind("<Button-1>", self._on_metronome_meter_plus)
        self.metronome_meter_var = tk.StringVar(value="")
        self.metronome_meter_value_label = tk.Label(
            self.metronome_meter_row,
            textvariable=self.metronome_meter_var,
            bg=self.color_surface_alt,
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="center",
        )
        self.metronome_meter_value_label.grid(row=1, column=2, sticky="", pady=(4, 0))

        self.metronome_clicks_label = ttk.Label(
            self._metronome_form_root,
            text="",
            font=(self.ui_font_family, 15, "bold"),
            anchor="w",
            fg=self.color_text,
        )
        # Antes no tenía grid: en Qt quedaba suelta y solapaba play/MIDI o la fila de figuras.
        self.metronome_clicks_label.grid(row=4, column=0, sticky="ew", padx=(2, 0), pady=(4, 2))
        self.metronome_clicks_row = ttk.Frame(self._metronome_form_root)
        self.metronome_clicks_row.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        n_fig = len(self.metronome_click_figure_defs)
        for col in range(n_fig):
            self.metronome_clicks_row.columnconfigure(col, weight=1)
        for col, figure in enumerate(self.metronome_click_figure_defs):
            # Ancho mínimo bajo: en paneles estrechos 5×88px se solapaban; reparten espacio con weight.
            btn = tk.Canvas(
                self.metronome_clicks_row,
                width=1,
                height=68,
                bg=self.color_surface_alt,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
            )
            # ew: reparten ancho; sin n/s el alto sigue el mínimo del canvas (~68), no crece con la ventana.
            btn.grid(row=0, column=col, sticky="ew", padx=3, pady=(4, 2))
            key = str(figure["key"])
            btn.bind("<Button-1>", lambda _e, k=key: self._select_metronome_click_figure(k))
            btn.bind("<Configure>", lambda _e, k=key: self._draw_metronome_figure_button(k))
            self.metronome_figure_buttons[key] = btn

        self.metronome_timer_row = ttk.Frame(self._metronome_form_root)
        self.metronome_timer_row.grid(row=6, column=0, sticky="ew", pady=(8, 4))
        self.metronome_timer_row.columnconfigure(1, weight=1)
        self.metronome_timer_enabled_var = tk.BooleanVar(value=self.metronome_timer_enabled)
        self.metronome_timer_check = ttk.Checkbutton(
            self.metronome_timer_row,
            text="",
            variable=self.metronome_timer_enabled_var,
            command=self._on_metronome_timer_toggle,
        )
        self.metronome_timer_check.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 0))
        self.metronome_timer_label = ttk.Label(
            self.metronome_timer_row,
            text="",
            font=(self.ui_font_family, 15, "bold"),
            fg=self.color_text,
        )
        self.metronome_timer_label.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(0, 6))

        self.metronome_timer_fields = ttk.Frame(self.metronome_timer_row)
        self.metronome_timer_fields.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 4))

        self.metronome_timer_minutes_label = ttk.Label(
            self.metronome_timer_fields,
            text="",
            font=(self.ui_font_family, 14, "bold"),
            fg=self.color_text,
        )
        self.metronome_timer_minutes_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.metronome_timer_minutes_var = tk.StringVar(value=str(self.metronome_timer_minutes))
        self.metronome_timer_minutes_spin = ttk.Spinbox(
            self.metronome_timer_fields,
            from_=0,
            to=99,
            increment=1,
            textvariable=self.metronome_timer_minutes_var,
            width=5,
            command=self._on_metronome_timer_fields_changed,
            font=(self.ui_font_family, 14),
        )
        self.metronome_timer_minutes_spin.grid(row=0, column=1, sticky="w", padx=(0, 28))
        self.metronome_timer_minutes_spin.bind("<FocusOut>", self._on_metronome_timer_fields_changed)
        self.metronome_timer_minutes_spin.bind("<Return>", self._on_metronome_timer_fields_changed)

        self.metronome_timer_seconds_label = ttk.Label(
            self.metronome_timer_fields,
            text="",
            font=(self.ui_font_family, 14, "bold"),
            fg=self.color_text,
        )
        self.metronome_timer_seconds_label.grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.metronome_timer_seconds_var = tk.StringVar(value=str(self.metronome_timer_seconds))
        self.metronome_timer_seconds_spin = ttk.Spinbox(
            self.metronome_timer_fields,
            from_=0,
            to=59,
            increment=1,
            textvariable=self.metronome_timer_seconds_var,
            width=5,
            command=self._on_metronome_timer_fields_changed,
            font=(self.ui_font_family, 14),
        )
        self.metronome_timer_seconds_spin.grid(row=0, column=3, sticky="w", padx=(0, 8))
        self.metronome_timer_seconds_spin.bind("<FocusOut>", self._on_metronome_timer_fields_changed)
        self.metronome_timer_seconds_spin.bind("<Return>", self._on_metronome_timer_fields_changed)

        self.metronome_bar_accent_var = tk.BooleanVar(value=self.metronome_bar_accent_enabled)
        self.metronome_bar_accent_row = ttk.Frame(self._metronome_form_root)
        self.metronome_bar_accent_row.grid(row=7, column=0, sticky="ew", pady=(10, 14))
        self.metronome_bar_accent_row.columnconfigure(1, weight=1)
        self.metronome_bar_accent_check = ttk.Checkbutton(
            self.metronome_bar_accent_row,
            text="",
            variable=self.metronome_bar_accent_var,
            command=self._on_metronome_bar_accent_toggle,
            font=(self.ui_font_family, 14, "bold"),
        )
        self.metronome_bar_accent_check.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 0))
        self.metronome_bar_accent_label = ttk.Label(
            self.metronome_bar_accent_row,
            text="",
            font=(self.ui_font_family, 14, "bold"),
            anchor="w",
            justify="left",
            wraplength=280,
            fg=self.color_text,
        )
        self.metronome_bar_accent_label.grid(row=0, column=1, sticky="ew", pady=(0, 4))
        try:
            self.metronome_bar_accent_check.configure(style="Metronome.TCheckbutton")
            style = ttk.Style()
            style.configure("Metronome.TCheckbutton", font=(self.ui_font_family, 14, "bold"))
        except Exception:
            pass

        self._metronome_form_root.columnconfigure(0, weight=1)

        self.tuner_gain_label = ttk.Label(self.tab_tuner_frame, text="", font=(self.ui_font_family, 15, "bold"), anchor="center", justify="center")
        self.tuner_gain_label.grid(row=4, column=0, sticky="ew", pady=(2, 2))
        self.tuner_gain_row = ttk.Frame(self.tab_tuner_frame)
        self.tuner_gain_row.grid(row=5, column=0, sticky="", pady=(0, 8))
        self.tuner_gain_row.columnconfigure(1, weight=1)
        self.tuner_gain_minus_btn = tk.Canvas(self.tuner_gain_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.tuner_gain_minus_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.tuner_gain_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_gain_minus_btn, "−"))
        self.tuner_gain_minus_btn.bind("<Button-1>", self._on_tuner_gain_minus)
        self.tuner_gain_slider_canvas = tk.Canvas(self.tuner_gain_row, height=34, bg=self.cget("background"), highlightthickness=0, bd=0, cursor="hand2")
        self.tuner_gain_slider_canvas.grid(row=0, column=1, sticky="ew")
        self.tuner_gain_slider_canvas.bind("<Configure>", lambda _e: self._draw_tuner_gain_slider())
        self.tuner_gain_slider_canvas.bind("<Button-1>", self._on_tuner_gain_slider_interact)
        self.tuner_gain_slider_canvas.bind("<B1-Motion>", self._on_tuner_gain_slider_interact)
        self.tuner_gain_plus_btn = tk.Canvas(self.tuner_gain_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.tuner_gain_plus_btn.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.tuner_gain_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_gain_plus_btn, "+"))
        self.tuner_gain_plus_btn.bind("<Button-1>", self._on_tuner_gain_plus)
        self.tuner_gain_var = tk.StringVar(value="")
        self.tuner_gain_value_label = tk.Label(
            self.tuner_gain_row,
            textvariable=self.tuner_gain_var,
            bg=self.cget("background"),
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="center",
        )
        self.tuner_gain_value_label.grid(row=1, column=1, sticky="", pady=(4, 0))

        self.tuner_spectrum_range_label = ttk.Label(self.tab_tuner_frame, text="", font=(self.ui_font_family, 15, "bold"), anchor="center")
        self.tuner_spectrum_range_label.grid(row=6, column=0, sticky="ew", pady=(2, 2))
        self.tuner_spectrum_range_row = ttk.Frame(self.tab_tuner_frame)
        self.tuner_spectrum_range_row.grid(row=7, column=0, sticky="", pady=(0, 6))
        self.tuner_spectrum_range_row.columnconfigure(2, weight=1)

        self.tuner_spectrum_min_minus_btn = tk.Canvas(
            self.tuner_spectrum_range_row,
            width=28,
            height=28,
            bg=self.cget("background"),
            highlightthickness=0,
            bd=0,
        )
        self.tuner_spectrum_min_minus_btn.grid(row=0, column=0, padx=(0, 4))
        self.tuner_spectrum_min_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_spectrum_min_minus_btn, "−"))
        self.tuner_spectrum_min_minus_btn.bind("<Button-1>", self._on_tuner_spectrum_min_minus)

        self.tuner_spectrum_max_minus_btn = tk.Canvas(
            self.tuner_spectrum_range_row,
            width=28,
            height=28,
            bg=self.cget("background"),
            highlightthickness=0,
            bd=0,
        )
        self.tuner_spectrum_max_minus_btn.grid(row=0, column=1, padx=(0, 8))
        self.tuner_spectrum_max_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_spectrum_max_minus_btn, "−"))
        self.tuner_spectrum_max_minus_btn.bind("<Button-1>", self._on_tuner_spectrum_max_minus)

        self.tuner_spectrum_range_canvas = tk.Canvas(
            self.tuner_spectrum_range_row,
            width=440,
            height=34,
            bg=self.cget("background"),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.tuner_spectrum_range_canvas.grid(row=0, column=2, sticky="ew")
        self.tuner_spectrum_range_canvas.bind("<Configure>", lambda _e: self._draw_tuner_spectrum_range_slider())
        self.tuner_spectrum_range_canvas.bind("<Button-1>", self._on_tuner_spectrum_range_press)
        self.tuner_spectrum_range_canvas.bind("<B1-Motion>", self._on_tuner_spectrum_range_drag)
        self.tuner_spectrum_range_canvas.bind("<ButtonRelease-1>", self._on_tuner_spectrum_range_release)

        self.tuner_spectrum_min_plus_btn = tk.Canvas(
            self.tuner_spectrum_range_row,
            width=28,
            height=28,
            bg=self.cget("background"),
            highlightthickness=0,
            bd=0,
        )
        self.tuner_spectrum_min_plus_btn.grid(row=0, column=3, padx=(8, 4))
        self.tuner_spectrum_min_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_spectrum_min_plus_btn, "+"))
        self.tuner_spectrum_min_plus_btn.bind("<Button-1>", self._on_tuner_spectrum_min_plus)

        self.tuner_spectrum_max_plus_btn = tk.Canvas(
            self.tuner_spectrum_range_row,
            width=28,
            height=28,
            bg=self.cget("background"),
            highlightthickness=0,
            bd=0,
        )
        self.tuner_spectrum_max_plus_btn.grid(row=0, column=4, padx=(0, 0))
        self.tuner_spectrum_max_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.tuner_spectrum_max_plus_btn, "+"))
        self.tuner_spectrum_max_plus_btn.bind("<Button-1>", self._on_tuner_spectrum_max_plus)
        self.tuner_spectrum_range_var = tk.StringVar(value="")
        self.tuner_spectrum_range_value_label = tk.Label(
            self.tab_tuner_frame,
            textvariable=self.tuner_spectrum_range_var,
            bg=self.cget("background"),
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            anchor="center",
        )
        self.tuner_spectrum_range_value_label.grid(row=8, column=0, sticky="ew", pady=(0, 2))

        self.tuner_status_var = tk.StringVar(value="-")

        self.tuner_tuning_label = ttk.Label(self.tab_tuner_frame, text="", anchor="center", justify="center")
        self.tuner_tuning_label.grid(row=0, column=0, sticky="ew", pady=(2, 2))
        self.tuner_tuning_btn = GreenRoundedButton(
            self.tab_tuner_frame,
            text="-",
            command=self.open_tuner_tuning_dialog,
            font_family=self.ui_font_family,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.tuner_tuning_btn.grid(row=1, column=0, sticky="", pady=(0, 6))

        self.tuner_input_label = ttk.Label(self.tab_tuner_frame, text="", anchor="center", justify="center")
        self.tuner_input_label.grid(row=2, column=0, sticky="ew", pady=(2, 2))
        self.tuner_input_var = tk.StringVar(value=self.tuner_input_name)
        self.tuner_input_combo = ttk.Combobox(
            self.tab_tuner_frame,
            textvariable=self.tuner_input_var,
            state="readonly",
            values=[""],
            width=42,
            font=(self.ui_font_family, 13),
        )
        self.tuner_input_combo.grid(row=3, column=0, sticky="", pady=(0, 8))
        self.tuner_input_combo.bind("<<ComboboxSelected>>", self._on_tuner_input_changed)
        self.tuner_input_combo.configure(postcommand=self.refresh_devices)

        self.tab_tuner_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="")

        self.instrument_toolbar_height = 56

        self.instrument_switch_frame = tk.Frame(container, bg=self.cget("background"))
        self.instrument_switch_frame.configure(height=self.instrument_toolbar_height)
        self.instrument_switch_frame.pack_propagate(False)
        self.instrument_switch_frame.rowconfigure(0, weight=1)
        self.instrument_switch_frame.columnconfigure(0, weight=1)
        self.instrument_switch_frame.columnconfigure(1, weight=0)
        self.instrument_switch_frame.columnconfigure(2, weight=1)
        self.instrument_switch_inner = tk.Frame(self.top_right_mode_controls, bg=topbar_bg)
        self.instrument_switch_inner.pack(side=tk.LEFT)
        self.generation_accidental_switch = tk.Frame(self.instrument_switch_inner, bg=topbar_bg)
        self.generation_accidental_switch.pack(side=tk.LEFT, padx=(0, 10))
        self.generation_accidental_sharp_btn = RoundedChoiceButton(
            self.generation_accidental_switch,
            text="#",
            command=lambda: self._set_note_accidental("sharp"),
            font_family=self.ui_font_family,
            font_size=12,
            width=48,
            height=40,
            radius=12,
        )
        self.generation_accidental_sharp_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.generation_accidental_flat_btn = RoundedChoiceButton(
            self.generation_accidental_switch,
            text="♭",
            command=lambda: self._set_note_accidental("flat"),
            font_family=self.ui_font_family,
            font_size=12,
            width=48,
            height=40,
            radius=12,
        )
        self.generation_accidental_flat_btn.pack(side=tk.LEFT)

        self.instrument_panel = RoundedPanel(
            container,
            radius=12,
            bg_color=self.color_surface_alt,
            border_color=self.color_border,
            border_width=1.2,
            # Aire vertical moderado; el panel inferior no debe “hincharse” más de lo necesario.
            padding=(12, 8, 12, 4),
        )
        self.instrument_panel.pack(fill=tk.X, expand=False)
        self.instrument_body_row = tk.Frame(self.instrument_panel.content, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.instrument_body_row.pack(fill=tk.X, expand=False)
        self.instrument_canvas_holder = tk.Frame(self.instrument_body_row, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.instrument_canvas_holder.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.instrument_view_switch_side = tk.Frame(self.instrument_body_row, bg=self.color_surface_alt, bd=0, highlightthickness=0)

        self.keyboard_qscroll = tk.KeyboardStripScroll(self.instrument_canvas_holder)
        self.keyboard_canvas = tk.Canvas(
            self.keyboard_qscroll,
            bg="#f5f4ef",
            height=156,
            highlightthickness=1,
            highlightbackground="#c5cad3",
        )
        self.keyboard_qscroll.setWidget(self.keyboard_canvas)
        # Scroll horizontal si el teclado supera el ancho (misma idea que la web con overflow-x).
        self.keyboard_qscroll.pack(fill=tk.X, expand=False)
        self.tuner_spectrum_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#081425",
            height=190,
            highlightthickness=1,
            highlightbackground=self.color_border,
        )
        self.tuner_spectrum_canvas.bind("<Configure>", lambda _e: self._draw_tuner_spectrum())

        self.guitar_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#2f3137",
            height=196,
            highlightthickness=1,
            highlightbackground=self.color_border,
        )
        self.guitar_variations_frame = tk.Frame(self.instrument_canvas_holder, bg=self.color_surface_alt)
        self.guitar_variations_inner = tk.Frame(self.guitar_variations_frame, bg=self.color_surface_alt)
        self.guitar_variations_inner.pack(anchor="center")
        # Qt: hermanos sin pack siguen visibles y tapaban el teclado (solo fondo gris).
        self.tuner_spectrum_canvas.setVisible(False)
        self.guitar_canvas.setVisible(False)
        self.guitar_variations_frame.setVisible(False)

        self.instrument_buttons_are_images = False
        self.piano_view_btn = GrayRoundedButton(
            self.instrument_view_switch_side,
            text="Piano",
            command=lambda: self._set_instrument_view("piano"),
            font_family=self.ui_font_family,
            width=124,
            height=42,
            radius=20,
            font_size=13,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
        )
        self.piano_view_btn.pack(side=tk.TOP, pady=(0, 8))

        self.guitar_view_btn = GrayRoundedButton(
            self.instrument_view_switch_side,
            text="Guitarra",
            command=lambda: self._set_instrument_view("guitar"),
            font_family=self.ui_font_family,
            width=124,
            height=42,
            radius=20,
            font_size=13,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.guitar_view_btn.pack(side=tk.TOP)

        self.handedness_buttons_are_images = False
        self.guitar_handedness_var = tk.StringVar(value="")
        self.guitar_handedness_combo = ttk.HandednessComboBox(
            self.instrument_view_switch_side,
            textvariable=self.guitar_handedness_var,
            state="readonly",
            width=10,
            font=(self.ui_font_family, 13),
        )
        self.guitar_handedness_combo.bind("<<ComboboxSelected>>", self._on_guitar_handedness_combo_changed)
        self._qt_apply_guitar_handedness_combo_style(self.guitar_handedness_combo)

        self.scale_transport_frame = tk.Frame(container, bg=self.cget("background"))
        self.scale_transport_frame.configure(height=self.instrument_toolbar_height)
        self.scale_transport_frame.pack_propagate(False)
        self.scale_transport_icons = tk.Frame(self.scale_transport_frame, bg=self.cget("background"))
        self.scale_transport_icons.place(relx=0.5, rely=0.5, anchor="center")
        self.scale_accidental_sharp_btn = RoundedChoiceButton(
            self.scale_transport_icons,
            text="#",
            command=lambda: self._set_note_accidental("sharp"),
            font_family=self.ui_font_family,
            width=48,
            height=34,
            radius=12,
        )
        self.scale_accidental_sharp_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.scale_accidental_flat_btn = RoundedChoiceButton(
            self.scale_transport_icons,
            text="♭",
            command=lambda: self._set_note_accidental("flat"),
            font_family=self.ui_font_family,
            width=48,
            height=34,
            radius=12,
        )
        self.scale_accidental_flat_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.scale_transport_bpm_frame = tk.Frame(self.scale_transport_frame, bg=self.cget("background"))
        self.scale_transport_bpm_frame.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        self.scale_transport_buttons_are_images = False
        self.scale_mode_piano_btn = GrayRoundedButton(
            self.instrument_view_switch_side,
            text="Piano",
            command=lambda: self._set_scale_play_mode("piano"),
            font_family=self.ui_font_family,
            width=124,
            height=42,
            radius=20,
            font_size=13,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
        )
        self.scale_mode_guitar_btn = GrayRoundedButton(
            self.instrument_view_switch_side,
            text="Guitarra",
            command=lambda: self._set_scale_play_mode("guitar"),
            font_family=self.ui_font_family,
            width=124,
            height=42,
            radius=20,
            font_size=13,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
        )
        if not hasattr(self, "scale_bpm_slider"):
            panel_bg = self.cget("background")
            self.scale_bpm_minus_btn = tk.Canvas(
                self.scale_transport_bpm_frame,
                width=34,
                height=34,
                bg=panel_bg,
                highlightthickness=0,
                bd=0,
            )
            self.scale_bpm_minus_btn.pack(side=tk.LEFT, padx=(0, 8))
            self._draw_scale_bpm_step_button(self.scale_bpm_minus_btn, "−")
            self.scale_bpm_minus_btn.bind("<Configure>", lambda _e: self._draw_scale_bpm_step_button(self.scale_bpm_minus_btn, "−"))
            self.scale_bpm_minus_btn.bind("<Button-1>", self._on_scale_bpm_minus)

            self.scale_bpm_slider = tk.Canvas(
                self.scale_transport_bpm_frame,
                width=240,
                height=34,
                bg=panel_bg,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
            )
            self.scale_bpm_slider.pack(side=tk.LEFT, padx=(0, 8))
            self.scale_bpm_slider.bind("<Configure>", lambda _e: self._draw_scale_bpm_slider())
            self.scale_bpm_slider.bind("<Button-1>", self._on_scale_bpm_slider_interact)
            self.scale_bpm_slider.bind("<B1-Motion>", self._on_scale_bpm_slider_interact)

            self.scale_bpm_plus_btn = tk.Canvas(
                self.scale_transport_bpm_frame,
                width=34,
                height=34,
                bg=panel_bg,
                highlightthickness=0,
                bd=0,
            )
            self.scale_bpm_plus_btn.pack(side=tk.LEFT, padx=(0, 8))
            self._draw_scale_bpm_step_button(self.scale_bpm_plus_btn, "+")
            self.scale_bpm_plus_btn.bind("<Configure>", lambda _e: self._draw_scale_bpm_step_button(self.scale_bpm_plus_btn, "+"))
            self.scale_bpm_plus_btn.bind("<Button-1>", self._on_scale_bpm_plus)

            self.scale_bpm_value_label = tk.Label(
                self.scale_transport_bpm_frame,
                text="120 BPM",
                bg=panel_bg,
                fg="#f3bf2f",
                font=(self.ui_font_family, 13, "bold"),
                width=7,
                anchor="e",
            )
            self.scale_bpm_value_label.pack(side=tk.LEFT)
            self._set_scale_bpm(self.scale_bpm_value, save=False)

        # Marcos de transporte solo visibles en algunos modos; si no, en Qt quedarían encima del contenido.
        self.instrument_switch_frame.setVisible(False)
        self.scale_transport_frame.setVisible(False)

        self.staff_canvas.bind("<Configure>", lambda _event: self.redraw_staff())
        self.staff_canvas.bind("<Motion>", self._on_staff_motion)
        self.staff_canvas.bind("<Leave>", self._on_staff_leave)
        self.staff_canvas.bind("<ButtonPress-1>", self._on_staff_press)
        self.staff_canvas.bind("<ButtonRelease-1>", self._on_staff_release)
        self.keyboard_canvas.bind("<Configure>", lambda _event: self.redraw_keyboard())
        self.keyboard_canvas.bind("<ButtonPress-1>", self._on_keyboard_press)
        self.keyboard_canvas.bind("<B1-Motion>", self._on_keyboard_drag)
        self.keyboard_canvas.bind("<ButtonRelease-1>", self._on_keyboard_release)
        self.guitar_canvas.bind("<Configure>", lambda _event: self.redraw_guitar_fretboard())
        self.guitar_canvas.bind("<ButtonPress-1>", self._on_guitar_canvas_press)
        self.guitar_canvas.bind("<B1-Motion>", self._on_guitar_canvas_drag)
        self.guitar_canvas.bind("<ButtonRelease-1>", self._on_guitar_canvas_release)
        self.bind_all("<KeyPress-Shift_L>", self._on_shift_press)
        self.bind_all("<KeyPress-Shift_R>", self._on_shift_press)
        self.bind_all("<KeyRelease-Shift_L>", self._on_shift_release)
        self.bind_all("<KeyRelease-Shift_R>", self._on_shift_release)
        self.bind_all("<Escape>", self._on_escape_pressed, add="+")
        self.bind_all("<Return>", self._on_return_pressed, add="+")
        self.bind_all("<space>", self._on_space_pressed, add="+")
        self.bind_all("<KeyRelease-space>", self._on_space_released, add="+")
        self.bind_all("<ButtonPress-1>", self._on_global_click_press, add="+")
        self.bind_all("<MouseWheel>", self._on_any_mousewheel, add="+")
        self.bind_all("<Shift-MouseWheel>", self._on_any_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_any_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_any_mousewheel, add="+")
        self.chord_panel.bind("<Configure>", self._refresh_right_panel_wraplengths, add="+")
        self.staff_canvas.bind("<Configure>", self._refresh_right_panel_wraplengths, add="+")
        self._refresh_right_panel_wraplengths()
        self._set_instrument_view(self.instrument_view)
        self._refresh_top_panel_titles()

    def _set_panel_title(self, widget: tk.Label, text: str) -> None:
        value = str(text or "").strip()
        if value:
            widget.configure(text=value)
            # Evita re-pack si el label ya está visible (en Qt shim, `winfo_manager()`
            # no siempre refleja el estado real y puede provocar reordenamientos).
            try:
                if widget.isVisible():  # type: ignore[attr-defined]
                    return
            except Exception:
                pass

            if widget is self.left_panel_title_label:
                widget.pack(fill=tk.X, anchor="w", pady=(0, 8), before=self.staff_canvas)
            else:
                widget.pack(fill=tk.X, anchor="w", pady=(0, 8), before=self.right_side_panel)
        elif widget.winfo_manager() != "":
            # En Qt shim, `winfo_manager()` puede no reflejar correctamente
            # el estado real. Aun así, para evitar espacio desperdiciado,
            # aseguramos que el label se desmonte cuando el texto está vacío.
            try:
                widget.pack_forget()
            except Exception:
                try:
                    widget.pack_forget()
                except Exception:
                    pass
        else:
            # Si no hay manager reportado, igualmente intentamos desmontar
            # para garantizar que no ocupe espacio.
            try:
                widget.pack_forget()
            except Exception:
                try:
                    widget.setVisible(False)  # type: ignore[attr-defined]
                except Exception:
                    pass

    def _refresh_top_panel_titles(self) -> None:
        if self.metronome_tab_active:
            # En metronomo no hace falta el titulo en el panel izquierdo.
            left_title = ""
            # El texto "Configuración de Metrónomo" no es necesario en el panel derecho.
            # Además, en Qt puede acabar desplazando/rompiendo el layout.
            right_title = ""
        elif self.tuner_tab_active:
            left_title = self.tr("panel_tuner")
            right_title = self.tr("panel_tuner_settings")
        else:
            # En modos de "staff" (deteccion/generacion/escalas) no mostramos
            # el titulo para que el `staff_canvas` aproveche todo el alto.
            left_title = ""
            right_title = ""
        self._set_panel_title(self.left_panel_title_label, left_title)
        self._set_panel_title(self.right_panel_title_label, right_title)

    def _refresh_detection_help_visibility(self) -> None:
        """Ayuda de detección: bajo el pentagrama (panel izquierdo), solo en modo detección."""
        if not hasattr(self, "detection_help_label"):
            return
        visible = self.current_mode == "detection"
        try:
            if hasattr(self.detection_help_label, "setVisible"):
                self.detection_help_label.setVisible(bool(visible))  # type: ignore[attr-defined]
        except Exception:
            pass
        if visible:
            try:
                self.detection_help_label.pack(
                    fill=tk.X,
                    anchor="w",
                    pady=(6, 0),
                    after=self.staff_canvas,
                )
            except Exception:
                try:
                    self.detection_help_label.pack(fill=tk.X, anchor="w", pady=(6, 0))
                except Exception:
                    pass
        else:
            try:
                self.detection_help_label.pack_forget()
            except Exception:
                pass

    def _refresh_staff_generated_chord_overlay(self) -> None:
        """Muestra el nombre del acorde generado sobre el pentagrama (generación y círculo de quintas)."""
        if not hasattr(self, "staff_generated_chord_frame"):
            return
        show = bool(self.generation_tab_active or self.circle_fifths_tab_active)
        try:
            if hasattr(self.staff_generated_chord_frame, "setVisible"):
                self.staff_generated_chord_frame.setVisible(bool(show))  # type: ignore[attr-defined]
        except Exception:
            pass
        if show:
            try:
                self.staff_generated_chord_frame.pack(
                    fill=tk.X,
                    anchor="w",
                    pady=(0, 8),
                    before=self.staff_canvas,
                )
            except Exception:
                try:
                    self.staff_generated_chord_frame.pack(
                        fill=tk.X,
                        anchor="w",
                        pady=(0, 8),
                        before=self.staff_canvas,
                    )
                except Exception:
                    pass
        else:
            try:
                self.staff_generated_chord_frame.pack_forget()
            except Exception:
                pass

    def apply_ui_language(self) -> None:
        self.title(self.tr("app_title"))
        self.top_title_label.configure(text=self.tr("app_title"))
        self.chord_title_label.configure(text=self.tr("detection_title"))
        self.detection_help_label.configure(text=self.tr("detection_help"))
        self.detection_clear_btn.set_text(self.tr("button_clear"))
        self._refresh_midi_input_sound_toggle_button()
        self._refresh_detection_controls_state()
        self.notes_caption_label.configure(text=self.tr("label_active_notes"))
        self.extra_notes_caption_label.configure(text=self.tr("label_extra_notes"))
        self.intervals_caption_label.configure(text=self.tr("label_intervals"))
        self.generated_title_label.configure(text=self.tr("mode_generation"))
        if hasattr(self, "circle_title_label"):
            self.circle_title_label.configure(text=self.tr("mode_circle_fifths"))
        if hasattr(self, "staff_generated_chord_caption"):
            self.staff_generated_chord_caption.configure(text=self.tr("label_chord"))
        self.generation_root_label.configure(text=self.tr("label_root_note"))
        self.generation_variant_label.configure(text=self.tr("label_variant"))
        self.generation_inversion_label.configure(text=self.tr("label_inversion"))
        self.generated_notes_caption_label.configure(text=self.tr("label_active_notes"))
        self.generated_intervals_caption_label.configure(text=self.tr("label_intervals"))
        self.scale_panel_title_label.configure(text=self.tr("mode_scales"))
        self.scale_tonic_selector_label.configure(text=self.tr("label_scale_tonic"))
        self.scale_type_selector_label.configure(text=self.tr("label_scale_type"))
        if hasattr(self, "scale_octave_selector_label"):
            self.scale_octave_selector_label.configure(text=self.tr("label_scale_octaves"))
        self.scale_notes_caption_label.configure(text=self.tr("label_scale_notes"))
        self.scale_intervals_caption_label.configure(text=self.tr("label_scale_intervals"))
        self.scale_metronome_volume_label.configure(text=self.tr("label_metronome_volume"))
        self.metronome_volume_label.configure(text=self.tr("label_metronome_volume"))
        self.metronome_tempo_label.configure(text=self.tr("label_metronome_tempo"))
        self.metronome_meter_label.configure(text=self.tr("label_metronome_meter"))
        self.metronome_clicks_label.configure(text=self.tr("label_metronome_clicks"))
        self.metronome_timer_label.configure(text=self.tr("label_metronome_timer"))
        self.metronome_timer_minutes_label.configure(text=self.tr("label_metronome_minutes"))
        self.metronome_timer_seconds_label.configure(text=self.tr("label_metronome_seconds"))
        self.metronome_bar_accent_check.configure(text="")
        if hasattr(self, "metronome_bar_accent_label"):
            self.metronome_bar_accent_label.configure(text=self.tr("label_metronome_bar_accent"))
        self.tuner_tuning_label.configure(text=self.tr("label_tuner_tuning"))
        self.tuner_input_label.configure(text=self.tr("label_tuner_input"))
        self.tuner_gain_label.configure(text=self.tr("label_tuner_input_gain"))
        self.tuner_spectrum_range_label.configure(text=self.tr("label_tuner_spectrum_range"))
        self.config_icon_btn.configure(text="⚙")
        if not self.instrument_buttons_are_images:
            self.piano_view_btn.set_text(self.tr("instrument_piano"))
            self.guitar_view_btn.set_text(self.tr("instrument_guitar"))
        if hasattr(self, "guitar_handedness_combo"):
            self._refresh_handedness_toggle_styles()
        if not self.scale_transport_buttons_are_images:
            self.scale_mode_piano_btn.set_text(self.tr("instrument_piano"))
            self.scale_mode_guitar_btn.set_text(self.tr("instrument_guitar"))
            self.scale_mode_metronome_btn.set_text("⏱")
        self.scale_bpm_value_label.configure(text=f"{int(self.config_data.get('metronome_bpm', 120))} {self.tr('scale_bpm_short')}")
        self.mode_var.set(self._mode_label(self.current_mode))
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._refresh_top_panel_titles()
        self._refresh_note_accidental_toggle_styles()
        self._refresh_scale_transport_styles()
        self._refresh_generation_controls()
        self._refresh_scale_preview()
        self._refresh_metronome_ui()
        self._refresh_tuner_ui()
        if not self.active_notes:
            self.status_var.set(self.tr("status_no_notes"))
    def _refresh_note_accidental_toggle_styles(self) -> None:
        is_flat = self.note_accidental == "flat"
        self.generation_accidental_sharp_btn.set_selected(not is_flat)
        self.generation_accidental_flat_btn.set_selected(is_flat)
        self.scale_accidental_sharp_btn.set_selected(not is_flat)
        self.scale_accidental_flat_btn.set_selected(is_flat)
    def _set_note_accidental(self, accidental: str) -> None:
        normalized = "flat" if accidental == "flat" else "sharp"
        if self.note_accidental == normalized:
            return
        self.note_accidental = normalized
        self.config_data["note_accidental"] = self.note_accidental
        self.save_config()
        self._refresh_note_accidental_toggle_styles()
        self.update_music_views()
        if getattr(self, "circle_fifths_tab_active", False):
            self._circle_run_generate()
        if self.generation_tab_active:
            self._refresh_generation_controls()
        if self.scale_tab_active:
            self._refresh_scale_preview()
    def _refresh_midi_input_sound_toggle_button(self) -> None:
        if self.midi_input_sound_enabled:
            label = self.tr("button_midi_sound_on")
        else:
            label = self.tr("button_midi_sound_off")
        for widget_name in ("detection_midi_sound_toggle_btn", "metronome_midi_sound_toggle_btn"):
            btn = getattr(self, widget_name, None)
            if btn is None:
                continue
            btn.set_text(label)
            btn.set_selected(self.midi_input_sound_enabled)
    def _toggle_midi_input_sound(self) -> None:
        self.midi_input_sound_enabled = not self.midi_input_sound_enabled
        self.config_data["midi_input_sound_enabled"] = self.midi_input_sound_enabled
        self.save_config()
        self._refresh_midi_input_sound_toggle_button()
        self._refresh_sounding_notes()
    def _fit_instrument_panel_height(self) -> None:
        if not hasattr(self, "instrument_panel") or not hasattr(self, "instrument_body_row"):
            return
        try:
            is_guitar = getattr(self, "instrument_view", None) == "guitar"
            if not is_guitar:
                for target_name in ("instrument_canvas_holder", "instrument_body_row"):
                    target = getattr(self, target_name, None)
                    if target is not None:
                        try:
                            target.setMinimumHeight(0)
                        except Exception:
                            pass

            metro_compact = bool(
                getattr(self, "metronome_tab_active", False)
                and getattr(self, "instrument_view", None) == "piano"
                and hasattr(self, "keyboard_canvas")
            )
            if hasattr(self, "keyboard_canvas"):
                try:
                    kb_vis = bool(self.keyboard_canvas.isVisible())
                except Exception:
                    kb_vis = True
                if kb_vis and getattr(self, "instrument_view", None) == "piano":
                    kh = 124 if metro_compact else 156
                    try:
                        self.keyboard_canvas.setFixedHeight(kh)
                        self.keyboard_canvas.setMinimumHeight(kh)
                        qs = getattr(self, "keyboard_qscroll", None)
                        if qs is not None:
                            qs.setMinimumHeight(kh + 2)
                            qs.setMaximumHeight(kh + 2)
                    except Exception:
                        pass

            # En Qt el shim no implementa siempre `update_idletasks()` ni
            # `winfo_reqheight()`. Usamos alternativas robustas.
            try:
                self.update_idletasks()  # type: ignore[attr-defined]
            except Exception:
                pass

            try:
                body_height = int(self.instrument_body_row.winfo_reqheight())  # type: ignore[attr-defined]
            except Exception:
                # `sizeHint()` suele ser el equivalente más cercano a reqheight.
                body_height = int(self.instrument_body_row.sizeHint().height())
            slack = 10 if getattr(self, "metronome_tab_active", False) else 14
            panel_height = max(80, body_height + slack)
            # En Qt no existe `winfo_height()` (es un método Tk).
            try:
                window_height = max(1, int(self.winfo_height()))  # type: ignore[attr-defined]
            except Exception:
                # QMainWindow: altura real del widget.
                window_height = max(1, int(self.height()))
            # Prevent the bottom instrument panel from consuming too much vertical space
            # and clipping the upper content when guitar controls are visible.
            max_panel_height = max(170, int(window_height * 0.42))

            # En Qt a veces el layout calcula un reqheight demasiado pequeño
            # para el modo guitarra (y recorta el `guitar_canvas`), haciendo
            # que falten las 2 cuerdas inferiores. Aseguramos un mínimo realista
            # según el alto del canvas de guitarra y el subpanel de variaciones.
            if is_guitar and hasattr(self, "guitar_canvas"):
                try:
                    guitar_h = int(self.guitar_canvas.winfo_height())
                except Exception:
                    guitar_h = 0
                try:
                    variations_h = int(self.guitar_variations_frame.winfo_height())
                except Exception:
                    variations_h = 0

                # Fallbacks: en Qt a veces el reqheight/winfo_height aún no está
                # resuelto al ejecutar este método.
                if guitar_h <= 0:
                    try:
                        guitar_h = int(self.guitar_canvas.sizeHint().height())
                    except Exception:
                        guitar_h = 196
                if variations_h <= 0 and hasattr(self, "guitar_variations_frame"):
                    try:
                        variations_h = int(self.guitar_variations_frame.sizeHint().height())
                    except Exception:
                        variations_h = 28

                # Aunque Qt informe una altura parcial/recortada en este punto,
                # el canvas de guitarra tiene un alto "base" de 196px y el subpanel
                # de variaciones (botones) ~28px. Forzamos mínimos para no recortar.
                guitar_h = max(guitar_h, 196)
                variations_h = max(variations_h, 28)

                # Margen extra para separación visual entre canvas y botones.
                min_required = max(0, guitar_h) + max(0, variations_h) + 12

                # Forzamos reserva de altura para evitar recortes del `guitar_canvas`.
                for target_name in ("instrument_canvas_holder", "instrument_body_row"):
                    target = getattr(self, target_name, None)
                    if target is not None:
                        try:
                            target.setMinimumHeight(min_required)
                        except Exception:
                            pass

                panel_height = max(panel_height, min_required)
                max_panel_height = max(max_panel_height, min_required)

            panel_height = min(panel_height, max_panel_height)
            # En Qt, `configure(height=...)` en el shim no siempre fuerza
            # el layout; fijar altura asegura que el panel no recorte el canvas.
            try:
                self.instrument_panel.setFixedHeight(panel_height)
            except Exception:
                try:
                    self.instrument_panel.configure(height=panel_height)
                except Exception:
                    pass
        except Exception:
            pass
    def _refresh_right_panel_wraplengths(self, _event: Optional[tk.Event] = None) -> None:
        try:
            panel_width = int(self.chord_panel.winfo_width())
        except Exception:
            panel_width = 0
        try:
            left_w = int(self.staff_canvas.winfo_width())
        except Exception:
            left_w = 0

        help_wrap = max(220, left_w - 56) if left_w > 1 else max(220, panel_width - 56)
        try:
            self.detection_help_label.configure(wraplength=help_wrap)
        except Exception:
            pass
        if left_w > 1 and hasattr(self, "staff_generated_chord_value"):
            try:
                self.staff_generated_chord_value.configure(wraplength=max(120, left_w - 100))
            except Exception:
                pass

        if panel_width <= 1:
            return

        result_wrap = max(480, panel_width - 84)

        for widget_name in (
            "notes_label",
            "extra_notes_label",
            "intervals_label",
            "generated_notes_label",
            "generated_intervals_label",
            "scale_notes_label",
            "scale_intervals_label",
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                try:
                    widget.configure(wraplength=result_wrap)
                except Exception:
                    pass

        accent_wrap = max(200, panel_width - 72)
        try:
            if hasattr(self, "metronome_bar_accent_label"):
                self.metronome_bar_accent_label.configure(wraplength=accent_wrap)
        except Exception:
            pass
    def _clear_detection_panel(self) -> None:
        self._stop_detection_preview()
        self._clear_live_input_state()
        self.update_music_views()
    def _play_detection_panel(self) -> None:
        self._start_detection_hold()
    def _start_detection_hold(self) -> None:
        live = set(self._current_detection_notes())
        if live:
            detection_notes = sorted(live)
        else:
            fallback = getattr(self, "detection_last_playable_notes", set())
            detection_notes = sorted(fallback) if fallback else []
        if not detection_notes:
            self.detection_play_button_pressed = False
            return
        self.detection_play_button_pressed = True
        self._stop_detection_preview()
        # Solo note_off al soltar de notas donde note_on creó voz (si ya sonaba, note_on se ignora y no hacemos off).
        owned: set[int] = set()
        for note in detection_notes:
            if self.audio_engine.note_on(int(note), 108):
                owned.add(int(note))
        if not owned and detection_notes:
            # Todas las notas ya estaban en el motor (duplicado): cortar y volver a disparar para que el transport se oiga.
            for note in detection_notes:
                self.audio_engine.note_off(int(note))
            try:
                self.sounding_notes -= set(int(n) for n in detection_notes)
            except Exception:
                pass
            for note in detection_notes:
                if self.audio_engine.note_on(int(note), 108):
                    owned.add(int(note))
        self._detection_preview_owned_notes = owned
        self.detection_play_btn.set_playing(True)
    def _stop_detection_hold(self) -> None:
        self.detection_play_button_pressed = False
        owned_snapshot = set(getattr(self, "_detection_preview_owned_notes", set()))
        self._stop_detection_preview()
        # Alinear solo el estado lógico; no llamar a _refresh_sounding_notes aquí (volvería a note_on y se oiría un segundo ataque al soltar).
        if owned_snapshot and str(getattr(self, "current_mode", "")) == "detection":
            try:
                self.sounding_notes -= owned_snapshot
            except Exception:
                pass
    def _on_detection_play_press(self, _event: tk.Event) -> str:
        self._start_detection_hold()
        return "break"
    def _refresh_detection_controls_state(self) -> None:
        live = bool(self._current_detection_notes())
        has_fallback = bool(getattr(self, "detection_last_playable_notes", set()))
        has_notes = live or has_fallback
        if hasattr(self, "detection_play_btn"):
            try:
                self.detection_play_btn.set_enabled(has_notes)
            except Exception:
                pass
        if hasattr(self, "detection_clear_btn"):
            try:
                self.detection_clear_btn.set_enabled(has_notes)
            except Exception:
                pass
    def _stop_detection_preview(self) -> None:
        after_id = getattr(self, "_detection_preview_after_id", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
            self._detection_preview_after_id = None
        owned = set(getattr(self, "_detection_preview_owned_notes", set()))
        if owned:
            for note in owned:
                self.audio_engine.note_off(int(note))
        self._detection_preview_owned_notes = set()
        if hasattr(self, "detection_play_btn"):
            self.detection_play_btn.set_playing(False)
    def _pointer_inside_widget(self, widget: tk.Widget) -> bool:
        try:
            pointer_x, pointer_y = widget.winfo_pointerxy()
            x0 = widget.winfo_rootx()
            y0 = widget.winfo_rooty()
            x1 = x0 + widget.winfo_width()
            y1 = y0 + widget.winfo_height()
            return x0 <= pointer_x <= x1 and y0 <= pointer_y <= y1
        except tk.TclError:
            return False
    def _register_scroll_target(self, wrapper: tk.Widget, canvas: tk.Canvas) -> None:
        self._scroll_targets = [(w, c) for (w, c) in self._scroll_targets if w != wrapper]
        self._scroll_targets.append((wrapper, canvas))
    def _unregister_scroll_target(self, wrapper: tk.Widget) -> None:
        self._scroll_targets = [(w, c) for (w, c) in self._scroll_targets if w != wrapper]
    def _scroll_canvas_from_event(self, canvas: tk.Canvas, event: tk.Event) -> str:
        delta = float(getattr(event, "delta", 0))
        if delta:
            # macOS trackpad sends small deltas, Windows typically uses +/-120.
            if abs(delta) >= 120:
                units = int(-delta / 120)
            else:
                units = int(-delta)
                if units == 0:
                    units = -1 if delta > 0 else 1
            canvas.yview_scroll(units, "units")
        elif getattr(event, "num", 0) == 4:
            canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", 0) == 5:
            canvas.yview_scroll(1, "units")
        return "break"
    def _on_any_mousewheel(self, event: tk.Event) -> Optional[str]:
        for wrapper, canvas in reversed(self._scroll_targets):
            if not wrapper.winfo_exists() or not canvas.winfo_exists():
                continue
            if self._pointer_inside_widget(wrapper):
                return self._scroll_canvas_from_event(canvas, event)
        return None
    def _build_scrollable_area(
        self,
        parent: tk.Widget,
        bg: Optional[str] = None,
        padx: int = 8,
        pady: tuple[int, int] = (2, 10),
    ) -> tk.Frame:
        # Nuestro `tk_compat.Canvas` no implementa `yview`/`yview_scroll`
        # (scrolling Tk). Para no crashear (y mantener scroll real),
        # usamos `QScrollArea` directamente.
        from PySide6.QtWidgets import QScrollArea, QVBoxLayout

        bg = bg or self.color_surface_alt
        wrapper = tk.Frame(parent, bg=bg)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)

        # Layout interno del wrapper para alojar el scroll area.
        layout = wrapper.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            wrapper.setLayout(layout)

        scroll_area = QScrollArea(wrapper)
        scroll_area.setWidgetResizable(True)
        try:
            scroll_area.setFrameShape(QScrollArea.NoFrame)  # type: ignore[attr-defined]
        except Exception:
            pass

        content = tk.Frame(scroll_area, bg=bg)
        scroll_area.setWidget(content)

        layout.addWidget(scroll_area)
        return content
    def _build_rounded_search_entry(self, parent: tk.Widget, placeholder: str) -> tuple[tk.StringVar, tk.Entry]:
        wrapper = tk.Frame(parent, bg=self.color_surface_alt)
        wrapper.pack(fill=tk.X, pady=(0, 8))

        canvas = tk.Canvas(
            wrapper,
            bg=self.color_surface_alt,
            height=42,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        canvas.pack(fill=tk.X)

        search_var = tk.StringVar(value="")
        entry = tk.Entry(
            canvas,
            textvariable=search_var,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            highlightbackground=self.color_surface,
            highlightcolor=self.color_surface,
            bg=self.color_surface,
            fg=self.color_text,
            insertbackground=self.color_text,
            font=(self.ui_font_family, 15, "bold"),
        )
        entry_window = canvas.create_window(46, 21, anchor="w", window=entry, height=24)
        placeholder_id = canvas.create_text(50, 21, anchor="w", text=placeholder, fill=self.color_muted, font=(self.ui_font_family, 15, "bold"))
        clear_button_bg_id = canvas.create_oval(0, 0, 0, 0, fill=self.color_muted, outline="")
        clear_button_x_id = canvas.create_text(0, 0, text="✕", fill=self.color_surface, font=(self.ui_font_family, 10, "bold"))
        search_lens_id = canvas.create_oval(0, 0, 0, 0, outline=self.color_text, width=2)
        search_handle_id = canvas.create_line(0, 0, 0, 0, fill=self.color_text, width=2, capstyle=tk.ROUND)

        def rounded_points(x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
            return [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]

        def redraw(_event: Optional[tk.Event] = None) -> None:
            w = max(40, int(canvas.winfo_width()))
            h = max(30, int(canvas.winfo_height()))
            r = max(10, min(h // 2, 20))
            canvas.delete("search_bg")
            canvas.create_polygon(
                rounded_points(1, 1, w - 1, h - 1, r),
                smooth=True,
                splinesteps=18,
                fill=self.color_surface,
                outline=self.color_border,
                width=2.0,
                tags="search_bg",
            )
            cx = 28
            cy = h / 2
            lens_r = 8
            canvas.coords(search_lens_id, cx - lens_r, cy - lens_r, cx + lens_r, cy + lens_r)
            canvas.coords(search_handle_id, cx + 6, cy + 6, cx + 12, cy + 12)

            clear_r = 10
            clear_cx = w - 24
            clear_cy = h / 2
            canvas.coords(clear_button_bg_id, clear_cx - clear_r, clear_cy - clear_r, clear_cx + clear_r, clear_cy + clear_r)
            canvas.coords(clear_button_x_id, clear_cx, clear_cy)

            canvas.coords(entry_window, 46, h / 2)
            canvas.itemconfigure(entry_window, width=max(16, w - 82))
            canvas.coords(placeholder_id, 50, h / 2)
            canvas.tag_lower("search_bg")

        def update_placeholder(*_args) -> None:
            is_empty = not search_var.get().strip()
            has_focus = self.focus_get() == entry
            canvas.itemconfigure(placeholder_id, state=("normal" if (is_empty and not has_focus) else "hidden"))
            canvas.itemconfigure(
                clear_button_bg_id,
                state=("hidden" if is_empty else "normal"),
            )
            canvas.itemconfigure(
                clear_button_x_id,
                state=("hidden" if is_empty else "normal"),
            )

        def clear_search(_event: Optional[tk.Event] = None) -> None:
            search_var.set("")
            entry.focus_set()

        canvas.bind("<Configure>", redraw)
        canvas.bind("<Button-1>", lambda _e: entry.focus_set())
        canvas.tag_bind(placeholder_id, "<Button-1>", lambda _e: entry.focus_set())
        canvas.tag_bind(clear_button_bg_id, "<Button-1>", clear_search)
        canvas.tag_bind(clear_button_x_id, "<Button-1>", clear_search)
        entry.bind("<FocusIn>", lambda _e: update_placeholder())
        entry.bind("<FocusOut>", lambda _e: update_placeholder())
        search_var.trace_add("write", update_placeholder)
        redraw()
        update_placeholder()
        return search_var, entry
    def _mode_label(self, mode_key: str) -> str:
        if mode_key == "generation":
            return self.tr("mode_generation")
        if mode_key == "circle_fifths":
            return self.tr("mode_circle_fifths")
        if mode_key == "scales":
            return self.tr("mode_scales")
        if mode_key == "metronome":
            return self.tr("mode_metronome")
        if mode_key == "tuner":
            return self.tr("mode_tuner")
        return self.tr("mode_detection")
    def _toggle_mode_selector(self, _event: Optional[tk.Event] = None) -> str:
        if self.mode_selector_overlay is not None:
            self._close_mode_selector_overlay()
        else:
            self._open_mode_selector_overlay()
        return "break"
    def _open_mode_selector_overlay(self) -> None:
        if self.mode_selector_overlay is not None:
            self._close_mode_selector_overlay()

        from PySide6.QtCore import QRect, QRectF, Qt
        from PySide6.QtGui import QColor, QFont, QPainter, QPen

        _CIRCLE_FIFTHS_ICON_MARKER = "__CIRCLE_FIFTHS_ICON__"

        class ModeCard(tk.Frame):  # type: ignore[misc]
            def __init__(
                self,
                master: tk.Widget,
                *,
                selected: bool,
                bg_color: str,
                hover_bg_color: str,
                border_color_selected: str,
                border_color_normal: str,
                border_width_selected: int = 2,
                border_width_normal: int = 1,
                padding: tuple[int, int, int, int] = (12, 12, 12, 12),
                icon_txt: str,
                icon_color: str,
                text_txt: str,
                text_color: str,
                font_family: str,
                icon_font_size: int = 56,
                text_font_size: int = 30,
            ) -> None:
                # Sin highlight/border CSS: lo pintamos nosotros.
                super().__init__(master, bg=bg_color, bd=0, highlightthickness=0, padding=padding)
                self._selected = bool(selected)
                self._bg_color = str(bg_color)
                self._hover_bg_color = str(hover_bg_color)
                self._border_color_selected = str(border_color_selected)
                self._border_color_normal = str(border_color_normal)
                self._border_width_selected = int(border_width_selected)
                self._border_width_normal = int(border_width_normal)
                self._hover = False
                self._icon_txt = str(icon_txt)
                self._icon_color = str(icon_color)
                self._text_txt = str(text_txt)
                self._text_color = str(text_color)
                self._font_family = str(font_family)
                self._icon_font_size = int(icon_font_size)
                self._text_font_size = int(text_font_size)
                self.setCursor(tk.Qt.CursorShape.PointingHandCursor if hasattr(tk, "Qt") else None)  # type: ignore[attr-defined]

            def _draw_circle_fifths_icon(self, painter: QPainter, icon_rect: QRect) -> None:
                """Icono vectorial (rueda 12 sectores); evita Unicode poco soportado (p. ej. U+2B58 → ?)."""
                rect = QRectF(icon_rect)
                cw = float(rect.center().x())
                ch = float(rect.center().y())
                side = min(rect.width(), rect.height())
                r = side * 0.38
                outer = QRectF(cw - r, ch - r, 2.0 * r, 2.0 * r)
                bg = QColor(self._hover_bg_color if self._hover else self._bg_color)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                for i in range(12):
                    c = QColor("#c9b8f0") if i % 2 == 0 else QColor("#6f58b8")
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(c)
                    painter.drawPie(outer, int((75 + i * 30) * 16), 30 * 16)
                hole = r * 0.36
                painter.setBrush(bg)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRectF(cw - hole, ch - hole, 2.0 * hole, 2.0 * hole))
                pen = QPen(QColor(self._icon_color), max(1.8, r * 0.07))
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(outer)

            def set_hover(self, hovering: bool) -> None:
                self._hover = bool(hovering)
                self.update()

            def paintEvent(self, _event) -> None:  # type: ignore[override]
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

                bg = self._hover_bg_color if self._hover else self._bg_color
                painter.fillRect(self.rect(), QColor(bg))

                # Solo dibujamos borde cuando está seleccionada.
                # Así evitamos el "recuadro fino" en tarjetas no seleccionadas.
                if self._selected:
                    bw = self._border_width_selected
                    bcolor = self._border_color_selected
                    pen = QPen(QColor(bcolor), float(bw))
                    painter.setPen(pen)

                    # Trazo pegado al borde exterior.
                    r = self.rect().adjusted(0, 0, -1, -1)
                    painter.drawRect(QRect(r.left(), r.top(), r.width(), r.height()))

                # Pintamos icono + texto directamente para evitar artefactos
                # de bordes en widgets hijos (`tk_compat.Label`).
                w = int(self.width())
                h = int(self.height())
                icon_rect = QRect(0, int(h * 0.10), w, int(h * 0.42))
                text_rect = QRect(0, int(h * 0.44), w, int(h * 0.56))

                # Icono (texto o dibujo vectorial para modos sin glifo fiable en la fuente)
                if self._icon_txt == _CIRCLE_FIFTHS_ICON_MARKER:
                    self._draw_circle_fifths_icon(painter, icon_rect)
                else:
                    icon_font = QFont(self._font_family, self._icon_font_size)
                    icon_font.setBold(True)
                    painter.setFont(icon_font)
                    painter.setPen(QColor(self._icon_color))
                    painter.drawText(icon_rect, int(Qt.AlignmentFlag.AlignCenter), self._icon_txt)

                # Texto
                text_font_size = self._text_font_size
                text_font = QFont(self._font_family, text_font_size)
                text_font.setBold(True)
                painter.setFont(text_font)
                painter.setPen(QColor(self._text_color))

                # Ajuste para que el texto vaya en una sola línea.
                # Si no cabe, reducimos tamaño en proporción.
                metrics = painter.fontMetrics()
                max_w = max(1, int(text_rect.width()) - 10)
                text_w = float(metrics.horizontalAdvance(self._text_txt))
                if text_w > max_w:
                    scale = max_w / max(1e-6, text_w)
                    text_font_size = max(14, int(round(text_font_size * scale)))
                    text_font = QFont(self._font_family, text_font_size)
                    text_font.setBold(True)
                    painter.setFont(text_font)

                painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignCenter), self._text_txt)
                painter.end()

        overlay = tk.Frame(
            self,
            bg=self.color_surface_alt,
            highlightthickness=1,
            highlightbackground=self.color_border,
            bd=0,
        )
        # Más alto para que el icono/texto grandes no se desborden y
        # no se solape con bordes de tarjetas vecinas.
        overlay.place(relx=0.5, rely=0.12, anchor="n", relwidth=0.52, relheight=0.68)
        self.mode_selector_overlay = overlay
        self._mode_selector_opened_ts = time.monotonic()

        cards_frame = tk.Frame(overlay, bg=self.color_surface_alt)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)

        mode_cards = {
            "detection": ("◎", "#ffa320"),
            "generation": ("♬", "#39c8ff"),
            "circle_fifths": (_CIRCLE_FIFTHS_ICON_MARKER, "#9b7bff"),
            "scales": ("♪", "#e4eb3f"),
            "metronome": ("⏱", "#ff8f40"),
            "tuner": ("🎸", "#8eea6b"),
        }
        options = []
        for mode_key in self._available_mode_keys():
            icon_txt, icon_color = mode_cards[mode_key]
            options.append((mode_key, self._mode_label(mode_key), icon_txt, icon_color))

        # Solo filas con tarjetas (evita fila vacía con stretch que deja un bloque oscuro abajo en Qt).
        n_mode_rows = (len(options) + 1) // 2
        for row_idx in range(n_mode_rows):
            cards_frame.rowconfigure(row_idx, weight=1)

        for idx, (mode_key, mode_text, icon_txt, icon_color) in enumerate(options):
            selected = self.current_mode == mode_key
            card = ModeCard(
                cards_frame,
                selected=selected,
                bg_color=self.color_card,
                hover_bg_color=self.color_card_hover,
                border_color_selected=self.color_accent,
                # Borde normal del mismo color que el fondo => no se aprecia.
                border_color_normal=self.color_card,
                border_width_selected=2,
                border_width_normal=1,
                padding=(14, 14, 14, 14),
                icon_txt=icon_txt,
                icon_color=icon_color,
                text_txt=mode_text,
                text_color=self.color_text,
                font_family=self.ui_font_family,
            )
            card.setCursor(tk.Qt.CursorShape.PointingHandCursor)  # type: ignore[attr-defined]
            card.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=6, pady=6)

            def on_enter(_e: tk.Event, c=card) -> None:
                c.set_hover(True)

            def on_leave(_e: tk.Event, c=card) -> None:
                c.set_hover(False)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            card.bind("<Button-1>", lambda _e, mk=mode_key: self._apply_mode(mk))
    def _close_mode_selector_overlay(self) -> None:
        if self.mode_selector_overlay is not None:
            self.mode_selector_overlay.destroy()
            self.mode_selector_overlay = None
    def _apply_mode(self, mode_key: str) -> None:
        if mode_key not in self._available_mode_keys():
            mode_key = "detection"
        self.mode_var.set(self._mode_label(mode_key))
        self._close_mode_selector_overlay()
        self._on_mode_combo_changed(None)
    def _on_mode_combo_changed(self, _event: tk.Event) -> None:
        self._close_mode_selector_overlay()
        self._close_scale_tonic_overlay()
        self._close_scale_type_overlay()
        self._close_generation_selection_overlay()
        self._close_tuner_tuning_overlay()
        self._close_settings_overlay()
        self._stop_staff_scale_note_playback()
        selected = self.mode_var.get()
        if selected == self._mode_label("generation"):
            self.current_mode = "generation"
        elif selected == self._mode_label("circle_fifths"):
            self.current_mode = "circle_fifths"
        elif selected == self._mode_label("scales"):
            self.current_mode = "scales"
        elif selected == self._mode_label("metronome"):
            self.current_mode = "metronome"
        elif bool(getattr(self, "tuner_enabled", True)) and selected == self._mode_label("tuner"):
            self.current_mode = "tuner"
        else:
            self.current_mode = "detection"
        if self.current_mode != "detection":
            try:
                from midichords.core.midi_idle_inhibit import cancel_midi_idle_inhibit

                cancel_midi_idle_inhibit()
            except Exception:
                pass
        self.config_data["mode"] = self.current_mode
        self.save_config()
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._set_generation_toolbar_layout(
            show_instrument_buttons=self.current_mode in ("generation", "circle_fifths"),
        )

        self.generation_tab_active = self.current_mode in ("generation", "circle_fifths")
        self.circle_fifths_tab_active = self.current_mode == "circle_fifths"
        self.scale_tab_active = self.current_mode == "scales"
        self.metronome_tab_active = self.current_mode == "metronome"
        self.tuner_tab_active = self.current_mode == "tuner"
        self._set_tuner_spectrum_visible(self.tuner_tab_active)
        if self.generation_space_release_after_id is not None:
            try:
                self.after_cancel(self.generation_space_release_after_id)
            except Exception:
                pass
            self.generation_space_release_after_id = None
        if self.scale_space_release_after_id is not None:
            try:
                self.after_cancel(self.scale_space_release_after_id)
            except Exception:
                pass
            self.scale_space_release_after_id = None
        if self.metronome_space_release_after_id is not None:
            try:
                self.after_cancel(self.metronome_space_release_after_id)
            except Exception:
                pass
            self.metronome_space_release_after_id = None
        if self.tuner_space_release_after_id is not None:
            try:
                self.after_cancel(self.tuner_space_release_after_id)
            except Exception:
                pass
            self.tuner_space_release_after_id = None
        self._stop_generated_playback()
        self._stop_scale_playback()
        self._stop_metronome()
        self._stop_tuner_stream()
        self._stop_detection_preview()
        self.scale_space_pressed = False
        self.metronome_space_pressed = False
        self.tuner_space_pressed = False

        if self.current_mode == "circle_fifths":
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.scale_transport_frame.pack_forget()
            self._show_generation_instrument_buttons()
            self._set_instrument_view(self.instrument_view)
            self._clear_live_input_state()
            self.tab_detection_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_circle_frame.pack(fill=tk.BOTH, expand=True)
            self._circle_run_generate()
        elif self.generation_tab_active:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.scale_transport_frame.pack_forget()
            self._show_generation_instrument_buttons()
            self._set_instrument_view(self.instrument_view)
            detected_notes = self._current_detection_notes()
            self._clear_live_input_state()
            if detected_notes:
                self._load_generation_from_detected_notes(detected_notes)
            self.tab_detection_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_circle_frame.pack_forget()
            self.tab_generation_frame.pack(fill=tk.BOTH, expand=True)
        elif self.scale_tab_active:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.instrument_view_switch_side.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            self._show_scale_mode_buttons()
            self._refresh_scale_transport_styles()
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self._refresh_scale_instrument_view()
            self._clear_live_input_state()
            self.tab_detection_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_circle_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_scale_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_scale_preview()
        elif self.metronome_tab_active:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.instrument_view_switch_side.pack_forget()
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_qscroll.pack(fill=tk.X, expand=False)
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_circle_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_metronome_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_metronome_ui()
        elif self.tuner_tab_active:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_qscroll.pack_forget()
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_circle_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_tuner_frame.pack(fill=tk.BOTH, expand=True)
            self._start_tuner_stream()
            self._refresh_tuner_ui()
        else:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.scale_transport_frame.pack_forget()
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_qscroll.pack(fill=tk.X, expand=False)
            self.tab_generation_frame.pack_forget()
            self.tab_circle_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)
        self._refresh_top_panel_titles()
        self._refresh_detection_help_visibility()
        self._refresh_staff_generated_chord_overlay()
        self._fit_instrument_panel_height()
        self.update_music_views()
