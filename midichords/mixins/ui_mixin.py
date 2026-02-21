from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Optional

from midichords.ui.widgets import GrayRoundedButton, GreenRoundedButton, PlayTransportButton, RoundedChoiceButton, RoundedPanel


class UiMixin:
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
            font=(self.ui_font_family, 13, "bold"),
        )
        self._mode_picker_arrow_id = self.mode_picker_trigger.create_text(
            0,
            20,
            anchor="e",
            text="▾",
            fill=self.color_muted,
            font=(self.ui_font_family, 13, "bold"),
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
            padding=(12, 12, 12, 12),
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
            font=(self.ui_font_family, 14, "bold"),
            anchor="w",
        )
        self.left_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 8))
        self.staff_canvas.pack(fill=tk.BOTH, expand=True)

        self.right_panel_title_label = tk.Label(
            self.right_panel.content,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            font=(self.ui_font_family, 14, "bold"),
            anchor="w",
        )
        self.right_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 8))
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
            padx=5,
            pady=5,
        )
        self.tab_generation_frame = tk.Frame(
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

        self.chord_title_label = tk.Label(
            self.tab_detection_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 18, "bold"),
        )
        self.chord_title_label.pack(anchor="w", pady=(4, 8))
        self.detection_help_label = tk.Label(
            self.tab_detection_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_muted,
            justify="left",
            anchor="w",
            wraplength=520,
            font=(self.ui_font_family, 13),
        )
        self.detection_help_label.pack(fill=tk.X, anchor="w", pady=(0, 8))
        self.detection_controls_row = tk.Frame(self.tab_detection_frame, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.detection_controls_row.pack(anchor="w", pady=(0, 8))
        self.detection_play_btn = PlayTransportButton(
            self.detection_controls_row,
            command=self._play_detection_panel,
            width=58,
            height=34,
        )
        self.detection_play_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.detection_play_btn.bind("<ButtonPress-1>", self._on_detection_play_press)
        self.detection_clear_btn = GrayRoundedButton(
            self.detection_controls_row,
            text="",
            command=self._clear_detection_panel,
            width=104,
            height=34,
            radius=14,
            font_size=14,
        )
        self.detection_clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.detection_midi_sound_toggle_btn = GrayRoundedButton(
            self.detection_controls_row,
            text="",
            command=self._toggle_midi_input_sound,
            width=220,
            height=34,
            radius=14,
            font_size=12,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
            selected_fill_color="#f3bf2f",
            selected_outline_color="#c9961f",
            selected_border_width=2.0,
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
        self.detection_result_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
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
            pad = 12
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
            font=(self.ui_font_family, 34, "bold"),
        )
        self.chord_label.pack(anchor="w", pady=(0, 12))

        self.notes_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 13, "bold"),
        )
        self.notes_caption_label.pack(anchor="w")
        self.notes_var = tk.StringVar(value="-")
        self.notes_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 13),
        )
        self.notes_label.pack(anchor="w", pady=(6, 6))
        self.intervals_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 13, "bold"),
        )
        self.intervals_caption_label.pack(anchor="w")
        self.intervals_var = tk.StringVar(value="-")
        self.intervals_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 13),
        )
        self.intervals_label.pack(anchor="w", pady=(6, 10))
        self.extra_notes_caption_label = tk.Label(
            self.detection_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 13, "bold"),
        )
        self.extra_notes_caption_label.pack(anchor="w", pady=(0, 1))
        self.extra_notes_var = tk.StringVar(value="")
        self.extra_notes_label = tk.Label(
            self.detection_result_inner,
            textvariable=self.extra_notes_var,
            bg="#17273a",
            fg="#ff5a5f",
            wraplength=420,
            font=(self.ui_mono_font_family, 13, "bold"),
        )
        self.extra_notes_label.pack(anchor="w", pady=(0, 8))

        self.generated_title_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 18, "bold"),
        )
        self.generated_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 10))

        self.generation_root_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_root_label.grid(row=1, column=0, sticky="w", pady=(0, 8), padx=(0, 8))
        self.generation_root_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_root_dialog,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_root_btn.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        self.generation_variant_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_variant_label.grid(row=2, column=0, sticky="w", pady=(0, 8), padx=(0, 8))
        self.generation_variant_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_variant_dialog,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_variant_btn.grid(row=2, column=1, sticky="ew", pady=(0, 8))

        self.generation_inversion_label = tk.Label(
            self.tab_generation_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.generation_inversion_label.grid(row=3, column=0, sticky="w", pady=(0, 6), padx=(0, 8))
        self.generation_inversion_btn = GrayRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_inversion_dialog,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.generation_inversion_btn.grid(row=3, column=1, sticky="ew", pady=(0, 6))

        self.generated_chord_var = tk.StringVar(value="-")
        self.generated_chord_row = tk.Frame(
            self.tab_generation_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.generated_chord_row.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 4))

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
            height=160,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.generation_result_canvas.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 2))
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
            font=(self.ui_font_family, 14, "bold"),
        )
        self.generated_chord_inner_label = tk.Label(
            self.generation_result_inner,
            textvariable=self.generated_chord_var,
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 34, "bold"),
        )
        self.generated_chord_inner_label.pack(anchor="w", pady=(0, 8))
        self.generated_notes_caption_label.pack(anchor="w")
        self.generated_notes_var = tk.StringVar(value="-")
        self.generated_notes_label = tk.Label(
            self.generation_result_inner,
            textvariable=self.generated_notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 14),
        )
        self.generated_notes_label.pack(anchor="w", pady=(6, 6))
        self.generated_intervals_caption_label = tk.Label(
            self.generation_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 14, "bold"),
        )
        self.generated_intervals_caption_label.pack(anchor="w")
        self.generated_intervals_var = tk.StringVar(value="-")
        self.generated_intervals_label = tk.Label(
            self.generation_result_inner,
            textvariable=self.generated_intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 14),
        )
        self.generated_intervals_label.pack(anchor="w", pady=(6, 0))

        self.tab_generation_frame.columnconfigure(0, weight=0)
        self.tab_generation_frame.columnconfigure(1, weight=1)

        self.scale_panel_title_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 18, "bold"),
        )
        self.scale_panel_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 10))

        self.scale_controls_row = tk.Frame(
            self.tab_scale_frame,
            bg=self.color_surface_alt,
            bd=0,
            highlightthickness=0,
        )
        self.scale_controls_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 8))
        self.scale_play_btn = PlayTransportButton(
            self.scale_controls_row,
            command=self._toggle_scale_play,
            width=58,
            height=34,
        )
        self.scale_play_btn.pack(side=tk.LEFT)
        self.scale_play_btn.bind("<space>", lambda _e: "break")
        self.scale_mode_metronome_btn = GrayRoundedButton(
            self.scale_controls_row,
            text="⏱",
            command=lambda: self._set_scale_play_mode("metronome"),
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
        self.scale_mode_metronome_btn.pack(side=tk.LEFT, padx=(8, 0))

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
        self.scale_tonic_selector_label.grid(row=1, column=0, sticky="w", pady=(0, 8), padx=(0, 8))
        self.scale_tonic_btn = GrayRoundedButton(
            self.tab_scale_frame,
            text="C",
            command=self.open_scale_tonic_dialog,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.scale_tonic_btn.grid(row=1, column=1, sticky="ew", pady=(0, 8))

        self.scale_type_selector_label = tk.Label(
            self.tab_scale_frame,
            text="",
            bg=self.color_surface_alt,
            fg=self.color_text,
            font=(self.ui_font_family, 13),
        )
        self.scale_type_selector_label.grid(row=2, column=0, sticky="w", pady=(0, 8), padx=(0, 8))
        self.scale_type_btn = GrayRoundedButton(
            self.tab_scale_frame,
            text=self.scale_pattern_name,
            command=self.open_scale_type_dialog,
            width=320,
            height=40,
            radius=16,
            font_size=15,
            text_color="#e6edf7",
            selected_text_color="#1a222d",
        )
        self.scale_type_btn.grid(row=2, column=1, sticky="ew", pady=(0, 8))

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
            font=(self.ui_font_family, 24, "bold"),
        )
        self.scale_name_label.pack(anchor="w", pady=(0, 8))

        self.scale_notes_caption_label = tk.Label(
            self.scale_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 14, "bold"),
        )
        self.scale_notes_caption_label.pack(anchor="w")
        self.scale_notes_var = tk.StringVar(value="-")
        self.scale_notes_label = tk.Label(
            self.scale_result_inner,
            textvariable=self.scale_notes_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 14),
        )
        self.scale_notes_label.pack(anchor="w", pady=(6, 6))

        self.scale_intervals_caption_label = tk.Label(
            self.scale_result_inner,
            text="",
            bg="#17273a",
            fg=self.color_text,
            font=(self.ui_font_family, 14, "bold"),
        )
        self.scale_intervals_caption_label.pack(anchor="w")
        self.scale_intervals_var = tk.StringVar(value="-")
        self.scale_intervals_label = tk.Label(
            self.scale_result_inner,
            textvariable=self.scale_intervals_var,
            bg="#17273a",
            fg=self.color_text,
            wraplength=420,
            font=(self.ui_mono_font_family, 14),
        )
        self.scale_intervals_label.pack(anchor="w", pady=(6, 0))

        self.tab_scale_frame.columnconfigure(0, weight=0)
        self.tab_scale_frame.columnconfigure(1, weight=1)
        self.tab_scale_frame.rowconfigure(5, weight=1)

        self.metronome_title_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_title_row.grid(row=0, column=0, sticky="w", pady=(4, 10))
        self.metronome_play_btn = PlayTransportButton(
            self.metronome_title_row,
            command=self._toggle_metronome,
            width=58,
            height=34,
        )
        self.metronome_play_btn.pack(side=tk.LEFT)
        self.metronome_play_btn.bind("<space>", lambda _e: "break")

        self.metronome_tempo_label = ttk.Label(self.tab_metronome_frame, text="", font=(self.ui_font_family, 15, "bold"), anchor="center")
        self.metronome_tempo_label.grid(row=1, column=0, sticky="ew", pady=(0, 2))

        self.metronome_slider_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_slider_row.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        self.metronome_slider_row.columnconfigure(1, weight=1)
        self.metronome_minus_btn = tk.Canvas(self.metronome_slider_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.metronome_minus_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.metronome_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_minus_btn, "−"))
        self.metronome_minus_btn.bind("<Button-1>", self._on_metronome_bpm_minus)
        self.metronome_slider_canvas = tk.Canvas(self.metronome_slider_row, height=34, bg=self.cget("background"), highlightthickness=0, bd=0, cursor="hand2")
        self.metronome_slider_canvas.grid(row=0, column=1, sticky="ew")
        self.metronome_slider_canvas.bind("<Configure>", lambda _e: self._draw_metronome_bpm_slider())
        self.metronome_slider_canvas.bind("<Button-1>", self._on_metronome_slider_interact)
        self.metronome_slider_canvas.bind("<B1-Motion>", self._on_metronome_slider_interact)
        self.metronome_plus_btn = tk.Canvas(self.metronome_slider_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.metronome_plus_btn.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.metronome_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_plus_btn, "+"))
        self.metronome_plus_btn.bind("<Button-1>", self._on_metronome_bpm_plus)
        self.metronome_bpm_var = tk.StringVar(value="")
        self.metronome_bpm_label = tk.Label(
            self.metronome_slider_row,
            textvariable=self.metronome_bpm_var,
            bg=self.cget("background"),
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="center",
        )
        self.metronome_bpm_label.grid(row=1, column=1, sticky="", pady=(4, 0))

        self.metronome_info_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_info_row.grid(row=3, column=0, sticky="ew", pady=(2, 10))
        self.metronome_info_row.columnconfigure(0, weight=1)
        self.metronome_preset_var = tk.StringVar(value="")
        self.metronome_preset_label = ttk.Label(
            self.metronome_info_row,
            textvariable=self.metronome_preset_var,
            font=(self.ui_font_family, 14, "bold"),
            anchor="center",
            justify="center",
        )
        self.metronome_preset_label.grid(row=0, column=0, sticky="ew")

        self.metronome_meter_label = ttk.Label(self.tab_metronome_frame, text="", font=(self.ui_font_family, 15, "bold"), anchor="center")
        self.metronome_meter_label.grid(row=4, column=0, sticky="ew", pady=(2, 2))
        self.metronome_meter_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_meter_row.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        self.metronome_meter_row.columnconfigure(1, weight=1)
        self.metronome_meter_minus_btn = tk.Canvas(self.metronome_meter_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.metronome_meter_minus_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.metronome_meter_minus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_meter_minus_btn, "−"))
        self.metronome_meter_minus_btn.bind("<Button-1>", self._on_metronome_meter_minus)
        self.metronome_meter_canvas = tk.Canvas(self.metronome_meter_row, height=34, bg=self.cget("background"), highlightthickness=0, bd=0, cursor="hand2")
        self.metronome_meter_canvas.grid(row=0, column=1, sticky="ew")
        self.metronome_meter_canvas.bind("<Configure>", lambda _e: self._draw_metronome_meter_slider())
        self.metronome_meter_canvas.bind("<Button-1>", self._on_metronome_meter_slider_interact)
        self.metronome_meter_canvas.bind("<B1-Motion>", self._on_metronome_meter_slider_interact)
        self.metronome_meter_plus_btn = tk.Canvas(self.metronome_meter_row, width=34, height=34, bg=self.cget("background"), highlightthickness=0, bd=0)
        self.metronome_meter_plus_btn.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.metronome_meter_plus_btn.bind("<Configure>", lambda _e: self._draw_circle_step_button(self.metronome_meter_plus_btn, "+"))
        self.metronome_meter_plus_btn.bind("<Button-1>", self._on_metronome_meter_plus)
        self.metronome_meter_var = tk.StringVar(value="")
        self.metronome_meter_value_label = tk.Label(
            self.metronome_meter_row,
            textvariable=self.metronome_meter_var,
            bg=self.cget("background"),
            fg="#f3bf2f",
            font=(self.ui_font_family, 13, "bold"),
            width=7,
            anchor="center",
        )
        self.metronome_meter_value_label.grid(row=1, column=1, sticky="", pady=(4, 0))

        self.metronome_clicks_label = ttk.Label(self.tab_metronome_frame, text="", font=(self.ui_font_family, 15, "bold"), anchor="center")
        self.metronome_clicks_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_clicks_row.grid(row=6, column=0, sticky="ew", pady=(0, 2))
        for col, figure in enumerate(self.metronome_click_figure_defs):
            btn = tk.Canvas(
                self.metronome_clicks_row,
                width=88,
                height=64,
                bg=self.cget("background"),
                highlightthickness=0,
                bd=0,
                cursor="hand2",
            )
            btn.grid(row=0, column=col, padx=6, pady=2)
            key = str(figure["key"])
            btn.bind("<Button-1>", lambda _e, k=key: self._select_metronome_click_figure(k))
            btn.bind("<Configure>", lambda _e, k=key: self._draw_metronome_figure_button(k))
            self.metronome_figure_buttons[key] = btn

        self.metronome_timer_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_timer_row.grid(row=7, column=0, sticky="w", pady=(8, 2))
        self.metronome_timer_enabled_var = tk.BooleanVar(value=self.metronome_timer_enabled)
        self.metronome_timer_check = ttk.Checkbutton(
            self.metronome_timer_row,
            text="",
            variable=self.metronome_timer_enabled_var,
            command=self._on_metronome_timer_toggle,
        )
        self.metronome_timer_check.grid(row=0, column=0, sticky="w")
        self.metronome_timer_label = ttk.Label(self.metronome_timer_row, text="", font=(self.ui_font_family, 15, "bold"))
        self.metronome_timer_label.grid(row=0, column=1, sticky="w", padx=(4, 10))

        self.metronome_timer_minutes_label = ttk.Label(self.metronome_timer_row, text="", font=(self.ui_font_family, 14, "bold"))
        self.metronome_timer_minutes_label.grid(row=0, column=2, sticky="w")
        self.metronome_timer_minutes_var = tk.StringVar(value=str(self.metronome_timer_minutes))
        self.metronome_timer_minutes_spin = ttk.Spinbox(
            self.metronome_timer_row,
            from_=0,
            to=99,
            increment=1,
            textvariable=self.metronome_timer_minutes_var,
            width=4,
            command=self._on_metronome_timer_fields_changed,
        )
        self.metronome_timer_minutes_spin.grid(row=0, column=3, sticky="w", padx=(4, 10))
        self.metronome_timer_minutes_spin.bind("<FocusOut>", self._on_metronome_timer_fields_changed)
        self.metronome_timer_minutes_spin.bind("<Return>", self._on_metronome_timer_fields_changed)

        self.metronome_timer_seconds_label = ttk.Label(self.metronome_timer_row, text="", font=(self.ui_font_family, 14, "bold"))
        self.metronome_timer_seconds_label.grid(row=0, column=4, sticky="w")
        self.metronome_timer_seconds_var = tk.StringVar(value=str(self.metronome_timer_seconds))
        self.metronome_timer_seconds_spin = ttk.Spinbox(
            self.metronome_timer_row,
            from_=0,
            to=59,
            increment=1,
            textvariable=self.metronome_timer_seconds_var,
            width=4,
            command=self._on_metronome_timer_fields_changed,
        )
        self.metronome_timer_seconds_spin.grid(row=0, column=5, sticky="w", padx=(4, 0))
        self.metronome_timer_seconds_spin.bind("<FocusOut>", self._on_metronome_timer_fields_changed)
        self.metronome_timer_seconds_spin.bind("<Return>", self._on_metronome_timer_fields_changed)

        self.metronome_bar_accent_var = tk.BooleanVar(value=self.metronome_bar_accent_enabled)
        self.metronome_bar_accent_check = ttk.Checkbutton(
            self.tab_metronome_frame,
            text="",
            variable=self.metronome_bar_accent_var,
            command=self._on_metronome_bar_accent_toggle,
        )
        self.metronome_bar_accent_check.grid(row=8, column=0, sticky="w", pady=(6, 0))
        try:
            self.metronome_bar_accent_check.configure(style="Metronome.TCheckbutton")
            style = ttk.Style()
            style.configure("Metronome.TCheckbutton", font=(self.ui_font_family, 14, "bold"))
        except Exception:
            pass

        self.tab_metronome_frame.columnconfigure(0, weight=1)

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
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.tuner_tuning_btn.grid(row=1, column=0, sticky="", pady=(0, 6))

        self.tuner_input_label = ttk.Label(self.tab_tuner_frame, text="", anchor="center", justify="center")
        self.tuner_input_label.grid(row=2, column=0, sticky="ew", pady=(2, 2))
        self.tuner_input_var = tk.StringVar(value=self.tuner_input_name)
        self.tuner_input_combo = ttk.Combobox(self.tab_tuner_frame, textvariable=self.tuner_input_var, state="readonly", values=[""], width=42)
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
            width=48,
            height=34,
            radius=12,
        )
        self.generation_accidental_sharp_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.generation_accidental_flat_btn = RoundedChoiceButton(
            self.generation_accidental_switch,
            text="♭",
            command=lambda: self._set_note_accidental("flat"),
            width=48,
            height=34,
            radius=12,
        )
        self.generation_accidental_flat_btn.pack(side=tk.LEFT)

        self.instrument_panel = RoundedPanel(
            container,
            radius=12,
            bg_color=self.color_surface_alt,
            border_color=self.color_border,
            border_width=1.2,
            padding=(12, 12, 12, 6),
        )
        self.instrument_panel.pack(fill=tk.X, expand=False)
        self.instrument_body_row = tk.Frame(self.instrument_panel.content, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.instrument_body_row.pack(fill=tk.X, expand=False)
        self.instrument_canvas_holder = tk.Frame(self.instrument_body_row, bg=self.color_surface_alt, bd=0, highlightthickness=0)
        self.instrument_canvas_holder.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.instrument_view_switch_side = tk.Frame(self.instrument_body_row, bg=self.color_surface_alt, bd=0, highlightthickness=0)

        self.keyboard_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#f5f4ef",
            height=156,
            highlightthickness=1,
            highlightbackground="#c5cad3",
        )
        self.keyboard_canvas.pack(fill=tk.X, expand=False)

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

        self.instrument_buttons_are_images = False
        self.piano_view_btn = GrayRoundedButton(
            self.instrument_view_switch_side,
            text="Piano",
            command=lambda: self._set_instrument_view("piano"),
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
        self.guitar_handedness_combo = ttk.Combobox(
            self.instrument_view_switch_side,
            textvariable=self.guitar_handedness_var,
            state="readonly",
            width=10,
        )
        self.guitar_handedness_combo.bind("<<ComboboxSelected>>", self._on_guitar_handedness_combo_changed)

        self.scale_transport_frame = tk.Frame(container, bg=self.cget("background"))
        self.scale_transport_frame.configure(height=self.instrument_toolbar_height)
        self.scale_transport_frame.pack_propagate(False)
        self.scale_transport_icons = tk.Frame(self.scale_transport_frame, bg=self.cget("background"))
        self.scale_transport_icons.place(relx=0.5, rely=0.5, anchor="center")
        self.scale_accidental_sharp_btn = RoundedChoiceButton(
            self.scale_transport_icons,
            text="#",
            command=lambda: self._set_note_accidental("sharp"),
            width=48,
            height=34,
            radius=12,
        )
        self.scale_accidental_sharp_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.scale_accidental_flat_btn = RoundedChoiceButton(
            self.scale_transport_icons,
            text="♭",
            command=lambda: self._set_note_accidental("flat"),
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
        self._refresh_right_panel_wraplengths()
        self._set_instrument_view(self.instrument_view)
        self._refresh_top_panel_titles()

    def _set_panel_title(self, widget: tk.Label, text: str) -> None:
        value = str(text or "").strip()
        if value:
            widget.configure(text=value)
            if widget.winfo_manager() == "":
                if widget is self.left_panel_title_label:
                    widget.pack(fill=tk.X, anchor="w", pady=(0, 8), before=self.staff_canvas)
                else:
                    widget.pack(fill=tk.X, anchor="w", pady=(0, 8), before=self.right_side_panel)
        elif widget.winfo_manager() != "":
            widget.pack_forget()

    def _refresh_top_panel_titles(self) -> None:
        if self.metronome_tab_active:
            left_title = self.tr("panel_metronome")
            right_title = self.tr("panel_metronome_settings")
        elif self.tuner_tab_active:
            left_title = self.tr("panel_tuner")
            right_title = self.tr("panel_tuner_settings")
        else:
            left_title = self.tr("panel_staff")
            right_title = ""
        self._set_panel_title(self.left_panel_title_label, left_title)
        self._set_panel_title(self.right_panel_title_label, right_title)

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
        self.generation_root_label.configure(text=self.tr("label_root_note"))
        self.generation_variant_label.configure(text=self.tr("label_variant"))
        self.generation_inversion_label.configure(text=self.tr("label_inversion"))
        self.generated_notes_caption_label.configure(text=self.tr("label_active_notes"))
        self.generated_intervals_caption_label.configure(text=self.tr("label_intervals"))
        self.scale_panel_title_label.configure(text=self.tr("mode_scales"))
        self.scale_tonic_selector_label.configure(text=self.tr("label_scale_tonic"))
        self.scale_type_selector_label.configure(text=self.tr("label_scale_type"))
        self.scale_notes_caption_label.configure(text=self.tr("label_scale_notes"))
        self.scale_intervals_caption_label.configure(text=self.tr("label_scale_intervals"))
        self.metronome_tempo_label.configure(text=self.tr("label_metronome_tempo"))
        self.metronome_meter_label.configure(text=self.tr("label_metronome_meter"))
        self.metronome_clicks_label.configure(text=self.tr("label_metronome_clicks"))
        self.metronome_timer_label.configure(text=self.tr("label_metronome_timer"))
        self.metronome_timer_minutes_label.configure(text=self.tr("label_metronome_minutes"))
        self.metronome_timer_seconds_label.configure(text=self.tr("label_metronome_seconds"))
        self.metronome_bar_accent_check.configure(text=self.tr("label_metronome_bar_accent"))
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
        if self.generation_tab_active:
            self._refresh_generation_controls()
        if self.scale_tab_active:
            self._refresh_scale_preview()
    def _refresh_midi_input_sound_toggle_button(self) -> None:
        if not hasattr(self, "detection_midi_sound_toggle_btn"):
            return
        if self.midi_input_sound_enabled:
            label = self.tr("button_midi_sound_on")
        else:
            label = self.tr("button_midi_sound_off")
        self.detection_midi_sound_toggle_btn.set_text(label)
        self.detection_midi_sound_toggle_btn.set_selected(self.midi_input_sound_enabled)
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
            self.update_idletasks()
            body_height = int(self.instrument_body_row.winfo_reqheight())
            panel_height = max(80, body_height + 18)
            window_height = max(1, int(self.winfo_height()))
            # Prevent the bottom instrument panel from consuming too much vertical space
            # and clipping the upper content when guitar controls are visible.
            max_panel_height = max(170, int(window_height * 0.42))
            panel_height = min(panel_height, max_panel_height)
            self.instrument_panel.configure(height=panel_height)
        except Exception:
            pass
    def _refresh_right_panel_wraplengths(self, _event: Optional[tk.Event] = None) -> None:
        try:
            panel_width = int(self.chord_panel.winfo_width())
        except Exception:
            return
        if panel_width <= 1:
            return

        help_wrap = max(220, panel_width - 56)
        result_wrap = max(480, panel_width - 84)

        try:
            self.detection_help_label.configure(wraplength=help_wrap)
        except Exception:
            pass

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
    def _clear_detection_panel(self) -> None:
        self._stop_detection_preview()
        self._clear_live_input_state()
        self.update_music_views()
    def _play_detection_panel(self) -> None:
        self._start_detection_hold()
    def _start_detection_hold(self) -> None:
        detection_notes = sorted(self._current_detection_notes())
        if not detection_notes:
            self.detection_play_button_pressed = False
            return
        self.detection_play_button_pressed = True
        self._stop_detection_preview()
        self._detection_preview_notes = set(detection_notes)
        for note in detection_notes:
            self.audio_engine.note_on(int(note), 108)
        self.detection_play_btn.set_playing(True)
    def _stop_detection_hold(self) -> None:
        self.detection_play_button_pressed = False
        self._stop_detection_preview()
    def _on_detection_play_press(self, _event: tk.Event) -> str:
        self._start_detection_hold()
        return "break"
    def _refresh_detection_controls_state(self) -> None:
        has_notes = bool(self._current_detection_notes())
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
        preview_notes = set(getattr(self, "_detection_preview_notes", set()))
        if preview_notes:
            for note in preview_notes:
                self.audio_engine.note_off(int(note))
        self._detection_preview_notes = set()
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
        bg = bg or self.color_surface_alt
        wrapper = tk.Frame(parent, bg=bg)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)

        canvas = tk.Canvas(
            wrapper,
            bg=bg,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        scrollbar = ttk.Scrollbar(wrapper, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        content = tk.Frame(canvas, bg=bg)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_content_configure(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event: tk.Event) -> str:
            return self._scroll_canvas_from_event(canvas, event)

        self._register_scroll_target(wrapper, canvas)
        wrapper.bind("<Destroy>", lambda e: self._unregister_scroll_target(wrapper), add="+")

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        for widget in (wrapper, canvas, content):
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", on_mousewheel)
            widget.bind("<Button-5>", on_mousewheel)

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

        overlay = tk.Frame(
            self,
            bg=self.color_surface_alt,
            highlightthickness=1,
            highlightbackground=self.color_border,
            bd=0,
        )
        overlay.place(relx=0.5, rely=0.12, anchor="n", relwidth=0.52, relheight=0.62)
        self.mode_selector_overlay = overlay

        cards_frame = tk.Frame(overlay, bg=self.color_surface_alt)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        cards_frame.rowconfigure(1, weight=1)
        cards_frame.rowconfigure(2, weight=1)

        options = [
            ("detection", self._mode_label("detection"), "◎", "#ffa320"),
            ("generation", self._mode_label("generation"), "♬", "#39c8ff"),
            ("scales", self._mode_label("scales"), "♪", "#e4eb3f"),
            ("metronome", self._mode_label("metronome"), "⏱", "#ff8f40"),
            ("tuner", self._mode_label("tuner"), "🎸", "#8eea6b"),
        ]

        for idx, (mode_key, mode_text, icon_txt, icon_color) in enumerate(options):
            card = tk.Frame(
                cards_frame,
                bg=self.color_card,
                highlightthickness=2 if self.current_mode == mode_key else 1,
                highlightbackground=self.color_accent if self.current_mode == mode_key else self.color_card,
                bd=0,
                cursor="hand2",
            )
            card.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=8, pady=8)
            icon = tk.Label(card, text=icon_txt, bg=self.color_card, fg=icon_color, font=(self.ui_font_family, 30, "bold"), cursor="hand2")
            icon.pack(pady=(10, 2))
            label = tk.Label(
                card,
                text=mode_text,
                bg=self.color_card,
                fg=self.color_text,
                font=(self.ui_font_family, 16, "bold"),
                justify="center",
                cursor="hand2",
            )
            label.pack(pady=(0, 10), padx=8)

            def on_enter(_e: tk.Event, c=card) -> None:
                c.configure(bg=self.color_card_hover)
                for child in c.winfo_children():
                    child.configure(bg=self.color_card_hover)

            def on_leave(_e: tk.Event, c=card, is_current=(self.current_mode == mode_key)) -> None:
                base = self.color_card
                c.configure(bg=base)
                for child in c.winfo_children():
                    child.configure(bg=base)
                c.configure(highlightbackground=self.color_accent if is_current else self.color_card)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            card.bind("<Button-1>", lambda _e, mk=mode_key: self._apply_mode(mk))
            icon.bind("<Button-1>", lambda _e, mk=mode_key: self._apply_mode(mk))
            label.bind("<Button-1>", lambda _e, mk=mode_key: self._apply_mode(mk))
    def _close_mode_selector_overlay(self) -> None:
        if self.mode_selector_overlay is not None:
            self.mode_selector_overlay.destroy()
            self.mode_selector_overlay = None
    def _apply_mode(self, mode_key: str) -> None:
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
        elif selected == self._mode_label("scales"):
            self.current_mode = "scales"
        elif selected == self._mode_label("metronome"):
            self.current_mode = "metronome"
        elif selected == self._mode_label("tuner"):
            self.current_mode = "tuner"
        else:
            self.current_mode = "detection"
        self.config_data["mode"] = self.current_mode
        self.save_config()
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._set_generation_toolbar_layout(show_instrument_buttons=self.current_mode == "generation")

        self.generation_tab_active = self.current_mode == "generation"
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

        if self.generation_tab_active:
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
            self.tab_tuner_frame.pack_forget()
            self.tab_scale_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_scale_preview()
        elif self.metronome_tab_active:
            self.instrument_panel.pack(fill=tk.X, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_canvas.pack(fill=tk.X, expand=False)
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
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
            self.keyboard_canvas.pack_forget()
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
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
            self.keyboard_canvas.pack(fill=tk.X, expand=False)
            self.tab_generation_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)
        self._refresh_top_panel_titles()
        self._fit_instrument_panel_height()
        self.update_music_views()
