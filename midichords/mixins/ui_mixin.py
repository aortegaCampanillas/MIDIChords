from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from midichords.ui.widgets import GrayRoundedButton, GreenRoundedButton, RoundedChoiceButton


class UiMixin:
    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        unified_green_width = 200
        unified_green_height = 46
        unified_green_radius = 22

        mode_bar = ttk.Frame(container)
        mode_bar.pack(fill=tk.X, pady=(0, 8))
        mode_bar.columnconfigure(0, weight=1)
        mode_bar.columnconfigure(1, weight=1)
        mode_bar.columnconfigure(2, weight=1)

        mode_center = ttk.Frame(mode_bar)
        mode_center.grid(row=0, column=1)

        self.mode_trigger_var = tk.StringVar(value="")
        self.mode_picker_trigger = tk.Frame(
            mode_center,
            bg="#25272f",
            highlightthickness=1,
            highlightbackground="#3a3d47",
            bd=0,
            cursor="hand2",
        )
        self.mode_picker_trigger.pack(side=tk.LEFT)
        self.mode_picker_label = tk.Label(
            self.mode_picker_trigger,
            textvariable=self.mode_trigger_var,
            bg="#25272f",
            fg="#d6d9df",
            font=("Helvetica", 16),
            padx=16,
            pady=10,
            cursor="hand2",
        )
        self.mode_picker_label.pack(side=tk.LEFT)
        self.mode_picker_arrow = tk.Label(
            self.mode_picker_trigger,
            text="⌄",
            bg="#25272f",
            fg="#8d93a3",
            font=("Helvetica", 18, "bold"),
            padx=10,
            pady=7,
            cursor="hand2",
        )
        self.mode_picker_arrow.pack(side=tk.LEFT)
        self.mode_picker_trigger.bind("<Button-1>", self._toggle_mode_selector)
        self.mode_picker_label.bind("<Button-1>", self._toggle_mode_selector)
        self.mode_picker_arrow.bind("<Button-1>", self._toggle_mode_selector)
        self.mode_picker_trigger.bind("<Enter>", lambda _e: self.mode_picker_trigger.configure(highlightbackground="#4a4f5f"))
        self.mode_picker_trigger.bind("<Leave>", lambda _e: self.mode_picker_trigger.configure(highlightbackground="#3a3d47"))

        self.config_icon_btn = tk.Label(
            mode_bar,
            text="⚙",
            fg="#f39c12",
            bg=self.cget("background"),
            font=("Helvetica", 20, "bold"),
            cursor="hand2",
        )
        self.config_icon_btn.grid(row=0, column=2, sticky="e")
        self.config_icon_btn.bind("<Button-1>", lambda _e: self.open_settings_dialog())
        self.config_icon_btn.bind("<Enter>", lambda _e: self.config_icon_btn.configure(fg="#ffad2a"))
        self.config_icon_btn.bind("<Leave>", lambda _e: self.config_icon_btn.configure(fg="#f39c12"))

        top_area = ttk.Frame(container)
        top_area.pack(fill=tk.BOTH, expand=True)

        # Layout superior fijo 50/50 para evitar que textos largos deformen el pentagrama.
        left_panel = ttk.Frame(top_area)
        right_panel = ttk.Frame(top_area)
        left_panel.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)
        right_panel.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

        self.staff_canvas = tk.Canvas(left_panel, bg="#000000", highlightthickness=1, highlightbackground="#3a3a3a")
        self.staff_canvas.pack(fill=tk.BOTH, expand=True, padx=(0, 8))

        side_panel = ttk.Frame(right_panel, padding=(6, 0, 0, 0))
        side_panel.pack(fill=tk.BOTH, expand=True)
        side_panel.columnconfigure(0, weight=1)
        side_panel.rowconfigure(0, weight=1)

        self.chord_panel = ttk.LabelFrame(side_panel, text="", padding=(12, 10))
        self.chord_panel.grid(row=0, column=0, sticky="nsew")

        self.tab_detection_frame = ttk.Frame(self.chord_panel, padding=(6, 6))
        self.tab_generation_frame = ttk.Frame(self.chord_panel, padding=(6, 4))
        self.tab_scale_frame = ttk.Frame(self.chord_panel, padding=(6, 4))
        self.tab_metronome_frame = ttk.Frame(self.chord_panel, padding=(6, 6))
        self.tab_tuner_frame = ttk.Frame(self.chord_panel, padding=(6, 6))
        self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)

        self.chord_title_label = ttk.Label(self.tab_detection_frame, text="", font=("Helvetica", 18, "bold"))
        self.chord_title_label.pack(anchor="w", pady=(4, 8))

        self.chord_var = tk.StringVar(value="-")
        self.chord_label = ttk.Label(self.tab_detection_frame, textvariable=self.chord_var, font=("Helvetica", 36, "bold"))
        self.chord_label.pack(anchor="w", pady=(0, 18))

        self.notes_caption_label = ttk.Label(self.tab_detection_frame, text="", font=("Helvetica", 12, "bold"))
        self.notes_caption_label.pack(anchor="w")

        self.notes_var = tk.StringVar(value="-")
        self.notes_label = ttk.Label(self.tab_detection_frame, textvariable=self.notes_var, wraplength=420, font=("Menlo", 12))
        self.notes_label.pack(anchor="w", pady=(6, 12))
        self.intervals_caption_label = ttk.Label(self.tab_detection_frame, text="", font=("Helvetica", 12, "bold"))
        self.intervals_caption_label.pack(anchor="w")
        self.intervals_var = tk.StringVar(value="-")
        self.intervals_label = ttk.Label(self.tab_detection_frame, textvariable=self.intervals_var, wraplength=420, font=("Menlo", 12))
        self.intervals_label.pack(anchor="w", pady=(6, 10))

        self.generated_title_label = ttk.Label(self.tab_generation_frame, text="", font=("Helvetica", 16, "bold"))
        self.generated_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(2, 10))

        self.generation_root_label = ttk.Label(self.tab_generation_frame, text="")
        self.generation_root_label.grid(row=1, column=0, sticky="w", pady=(0, 2))
        self.generation_root_btn = GreenRoundedButton(
            self.tab_generation_frame,
            text="C",
            command=self.open_generation_root_dialog,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.generation_root_btn.grid(row=2, column=0, sticky="w", pady=(0, 4), padx=(0, 6))

        self.generation_variant_label = ttk.Label(self.tab_generation_frame, text="")
        self.generation_variant_label.grid(row=1, column=1, sticky="w", pady=(0, 2), padx=(6, 0))
        self.generation_variant_btn = GreenRoundedButton(
            self.tab_generation_frame,
            text="maj",
            command=self.open_generation_variant_dialog,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.generation_variant_btn.grid(row=2, column=1, sticky="w", pady=(0, 4), padx=(6, 0))

        self.generation_inversion_label = ttk.Label(self.tab_generation_frame, text="")
        self.generation_inversion_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.generation_inversion_btn = GreenRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_inversion_dialog,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.generation_inversion_btn.grid(row=4, column=0, sticky="w", pady=(0, 4))

        self.generated_chord_var = tk.StringVar(value="-")
        self.generated_chord_row = ttk.Frame(self.tab_generation_frame)
        self.generated_chord_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 4))

        self.generation_play_btn = ttk.Button(
            self.generated_chord_row,
            text="▶",
            width=3,
        )
        self.generation_play_btn.pack(side=tk.LEFT)
        self.generation_play_btn.bind("<ButtonPress-1>", self._on_generation_play_press)
        self.bind_all("<ButtonRelease-1>", self._on_global_mouse_release)

        self.generated_chord_label = ttk.Label(
            self.generated_chord_row,
            textvariable=self.generated_chord_var,
            font=("Helvetica", 30, "bold"),
        )
        self.generated_chord_label.pack(side=tk.LEFT, padx=(8, 0))

        self.generated_notes_caption_label = ttk.Label(self.tab_generation_frame, text="", font=("Helvetica", 12, "bold"))
        self.generated_notes_caption_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 2))
        self.generated_notes_var = tk.StringVar(value="-")
        self.generated_notes_label = ttk.Label(
            self.tab_generation_frame,
            textvariable=self.generated_notes_var,
            wraplength=420,
            font=("Menlo", 12),
        )
        self.generated_notes_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.generated_intervals_caption_label = ttk.Label(self.tab_generation_frame, text="", font=("Helvetica", 12, "bold"))
        self.generated_intervals_caption_label.grid(row=8, column=0, columnspan=2, sticky="w", pady=(2, 2))
        self.generated_intervals_var = tk.StringVar(value="-")
        self.generated_intervals_label = ttk.Label(
            self.tab_generation_frame,
            textvariable=self.generated_intervals_var,
            wraplength=420,
            font=("Menlo", 12),
        )
        self.generated_intervals_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 2))

        self.tab_generation_frame.columnconfigure(0, weight=1)
        self.tab_generation_frame.columnconfigure(1, weight=1)

        self.scale_title_row = ttk.Frame(self.tab_scale_frame)
        self.scale_title_row.grid(row=0, column=0, sticky="w", pady=(4, 8))
        self.scale_play_btn = ttk.Button(self.scale_title_row, text="▶", width=3, command=self._toggle_scale_play, takefocus=False)
        self.scale_play_btn.pack(side=tk.LEFT)
        self.scale_play_btn.bind("<space>", lambda _e: "break")
        self.scale_title_var = tk.StringVar(value="-")
        self.scale_title_label = ttk.Label(self.scale_title_row, textvariable=self.scale_title_var, font=("Helvetica", 28, "bold"))
        self.scale_title_label.pack(side=tk.LEFT, padx=(8, 0))

        self.scale_buttons_row = ttk.Frame(self.tab_scale_frame)
        self.scale_buttons_row.grid(row=1, column=0, sticky="w", pady=(4, 8))
        self.scale_tonic_btn = GreenRoundedButton(
            self.scale_buttons_row,
            text="C",
            command=self.open_scale_tonic_dialog,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.scale_tonic_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.scale_type_btn = GreenRoundedButton(
            self.scale_buttons_row,
            text=self.scale_pattern_name,
            command=self.open_scale_type_dialog,
            width=unified_green_width,
            height=unified_green_height,
            radius=unified_green_radius,
        )
        self.scale_type_btn.pack(side=tk.LEFT)

        self.scale_notes_caption_label = ttk.Label(self.tab_scale_frame, text="", font=("Helvetica", 12, "bold"))
        self.scale_notes_caption_label.grid(row=2, column=0, sticky="w", pady=(2, 2))
        self.scale_notes_var = tk.StringVar(value="-")
        self.scale_notes_label = ttk.Label(self.tab_scale_frame, textvariable=self.scale_notes_var, wraplength=420, font=("Menlo", 12))
        self.scale_notes_label.grid(row=3, column=0, sticky="w", pady=(0, 4))

        self.scale_intervals_caption_label = ttk.Label(self.tab_scale_frame, text="", font=("Helvetica", 12, "bold"))
        self.scale_intervals_caption_label.grid(row=4, column=0, sticky="w", pady=(2, 2))
        self.scale_intervals_var = tk.StringVar(value="-")
        self.scale_intervals_label = ttk.Label(self.tab_scale_frame, textvariable=self.scale_intervals_var, wraplength=420, font=("Menlo", 12))
        self.scale_intervals_label.grid(row=5, column=0, sticky="w", pady=(0, 4))

        self.tab_scale_frame.columnconfigure(0, weight=1)

        self.metronome_title_row = ttk.Frame(self.tab_metronome_frame)
        self.metronome_title_row.grid(row=0, column=0, sticky="w", pady=(4, 10))
        self.metronome_play_btn = ttk.Button(self.metronome_title_row, text="▶", width=3, command=self._toggle_metronome, takefocus=False)
        self.metronome_play_btn.pack(side=tk.LEFT)
        self.metronome_play_btn.bind("<space>", lambda _e: "break")

        self.metronome_tempo_label = ttk.Label(self.tab_metronome_frame, text="", font=("Helvetica", 13, "bold"), anchor="center")
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
            fg="#ff533d",
            font=("Helvetica", 11, "bold"),
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
            font=("Helvetica", 12, "bold"),
            anchor="center",
            justify="center",
        )
        self.metronome_preset_label.grid(row=0, column=0, sticky="ew")

        self.metronome_meter_label = ttk.Label(self.tab_metronome_frame, text="", font=("Helvetica", 13, "bold"), anchor="center")
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
            fg="#ff533d",
            font=("Helvetica", 11, "bold"),
            width=7,
            anchor="center",
        )
        self.metronome_meter_value_label.grid(row=1, column=1, sticky="", pady=(4, 0))

        self.metronome_clicks_label = ttk.Label(self.tab_metronome_frame, text="", font=("Helvetica", 13, "bold"), anchor="center")
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
        self.metronome_timer_label = ttk.Label(self.metronome_timer_row, text="", font=("Helvetica", 13, "bold"))
        self.metronome_timer_label.grid(row=0, column=1, sticky="w", padx=(4, 10))

        self.metronome_timer_minutes_label = ttk.Label(self.metronome_timer_row, text="", font=("Helvetica", 12, "bold"))
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

        self.metronome_timer_seconds_label = ttk.Label(self.metronome_timer_row, text="", font=("Helvetica", 12, "bold"))
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
            style.configure("Metronome.TCheckbutton", font=("Helvetica", 13, "bold"))
        except Exception:
            pass

        self.tab_metronome_frame.columnconfigure(0, weight=1)

        self.tuner_gain_label = ttk.Label(self.tab_tuner_frame, text="", font=("Helvetica", 13, "bold"), anchor="center", justify="center")
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
            fg="#ff533d",
            font=("Helvetica", 11, "bold"),
            width=7,
            anchor="center",
        )
        self.tuner_gain_value_label.grid(row=1, column=1, sticky="", pady=(4, 0))

        self.tuner_spectrum_range_label = ttk.Label(self.tab_tuner_frame, text="", font=("Helvetica", 13, "bold"), anchor="center")
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
            fg="#ff533d",
            font=("Helvetica", 11, "bold"),
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

        self.bottom_separator = ttk.Separator(container, orient=tk.HORIZONTAL)
        self.bottom_separator.pack(fill=tk.X, pady=(10, 10))

        self.instrument_toolbar_height = 56

        self.instrument_switch_frame = tk.Frame(container, bg=self.cget("background"))
        self.instrument_switch_frame.configure(height=self.instrument_toolbar_height)
        self.instrument_switch_frame.pack_propagate(False)
        self.instrument_switch_frame.pack(fill=tk.X, pady=(0, 6))
        self.instrument_switch_frame.rowconfigure(0, weight=1)
        self.instrument_switch_frame.columnconfigure(0, weight=1)
        self.instrument_switch_frame.columnconfigure(1, weight=0)
        self.instrument_switch_frame.columnconfigure(2, weight=1)
        self.instrument_switch_inner = tk.Frame(self.instrument_switch_frame, bg=self.cget("background"))
        self.instrument_switch_inner.grid(row=0, column=1, sticky="")

        if self.piano_image is not None and self.guitar_image is not None:
            self.instrument_buttons_are_images = True
            self.piano_view_btn = tk.Label(
                self.instrument_switch_inner,
                image=self.piano_image,
                bg=self.cget("background"),
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=4,
            )
            self.piano_view_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.piano_view_btn.bind("<Button-1>", lambda _e: self._set_instrument_view("piano"))

            self.guitar_view_btn = tk.Label(
                self.instrument_switch_inner,
                image=self.guitar_image,
                bg=self.cget("background"),
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=4,
            )
            self.guitar_view_btn.pack(side=tk.LEFT)
            self.guitar_view_btn.bind("<Button-1>", lambda _e: self._set_instrument_view("guitar"))
        else:
            self.instrument_buttons_are_images = False
            self.piano_view_btn = GreenRoundedButton(
                self.instrument_switch_inner,
                text="Piano",
                command=lambda: self._set_instrument_view("piano"),
                width=140,
                height=42,
                radius=20,
            )
            self.piano_view_btn.pack(side=tk.LEFT, padx=(0, 8))

            self.guitar_view_btn = GreenRoundedButton(
                self.instrument_switch_inner,
                text="Guitarra",
                command=lambda: self._set_instrument_view("guitar"),
                width=140,
                height=42,
                radius=20,
            )
            self.guitar_view_btn.pack(side=tk.LEFT)

        if self.right_hand_icon_image is not None and self.left_hand_icon_image is not None:
            self.handedness_buttons_are_images = True
            panel_bg = self.cget("background")
            self.guitar_right_btn = tk.Label(
                self.instrument_switch_frame,
                image=self.right_hand_icon_image,
                bg=panel_bg,
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=8,
                pady=6,
            )
            self.guitar_right_btn.bind("<Button-1>", lambda _e: self._set_guitar_handedness("right"))
            self.guitar_right_btn.grid(row=0, column=0, sticky="w", padx=(6, 0))
            self.guitar_left_btn = tk.Label(
                self.instrument_switch_frame,
                image=self.left_hand_icon_image,
                bg=panel_bg,
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=8,
                pady=6,
            )
            self.guitar_left_btn.bind("<Button-1>", lambda _e: self._set_guitar_handedness("left"))
            self.guitar_left_btn.grid(row=0, column=2, sticky="e", padx=(0, 6))
        else:
            self.handedness_buttons_are_images = False
            self.guitar_right_btn = GreenRoundedButton(
                self.instrument_switch_frame,
                text="Diestro",
                command=lambda: self._set_guitar_handedness("right"),
                width=130,
                height=38,
                radius=18,
            )
            self.guitar_right_btn.grid(row=0, column=0, sticky="w", padx=(6, 0))
            self.guitar_left_btn = GreenRoundedButton(
                self.instrument_switch_frame,
                text="Zurdo",
                command=lambda: self._set_guitar_handedness("left"),
                width=130,
                height=38,
                radius=18,
            )
            self.guitar_left_btn.grid(row=0, column=2, sticky="e", padx=(0, 6))

        self.scale_transport_frame = tk.Frame(container, bg=self.cget("background"))
        self.scale_transport_frame.configure(height=self.instrument_toolbar_height)
        self.scale_transport_frame.pack_propagate(False)
        self.scale_transport_frame.pack(fill=tk.X, pady=(0, 6))
        self.scale_transport_icons = tk.Frame(self.scale_transport_frame, bg=self.cget("background"))
        self.scale_transport_icons.place(relx=0.5, rely=0.5, anchor="center")
        self.scale_transport_bpm_frame = tk.Frame(self.scale_transport_frame, bg=self.cget("background"))
        self.scale_transport_bpm_frame.place(relx=1.0, rely=0.5, anchor="e", x=-6)

        if self.piano_image is not None and self.metronome_image is not None:
            self.scale_transport_buttons_are_images = True
            panel_bg = self.cget("background")
            self.scale_mode_piano_btn = tk.Label(
                self.scale_transport_icons,
                image=self.piano_image,
                bg=panel_bg,
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=4,
            )
            self.scale_mode_piano_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.scale_mode_piano_btn.bind("<ButtonPress-1>", lambda e: self._on_scale_transport_icon_press(e, "piano"))
            self.scale_mode_piano_btn.bind("<ButtonRelease-1>", lambda e: self._on_scale_transport_icon_release(e, "piano"))

            self.scale_mode_guitar_btn = tk.Label(
                self.scale_transport_icons,
                image=self.guitar_image if self.guitar_image is not None else self.piano_image,
                bg=panel_bg,
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=4,
            )
            self.scale_mode_guitar_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.scale_mode_guitar_btn.bind("<ButtonPress-1>", lambda e: self._on_scale_transport_icon_press(e, "guitar"))
            self.scale_mode_guitar_btn.bind("<ButtonRelease-1>", lambda e: self._on_scale_transport_icon_release(e, "guitar"))

            self.scale_mode_metronome_btn = tk.Label(
                self.scale_transport_icons,
                image=self.metronome_image,
                bg=panel_bg,
                bd=2,
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=4,
            )
            self.scale_mode_metronome_btn.pack(side=tk.LEFT, padx=(0, 6))
            self.scale_mode_metronome_btn.bind("<ButtonPress-1>", lambda e: self._on_scale_transport_icon_press(e, "metronome"))
            self.scale_mode_metronome_btn.bind("<ButtonRelease-1>", lambda e: self._on_scale_transport_icon_release(e, "metronome"))
        else:
            self.scale_transport_buttons_are_images = False
            self.scale_mode_piano_btn = GreenRoundedButton(
                self.scale_transport_icons,
                text="Piano",
                command=lambda: self._set_scale_play_mode("piano"),
                width=130,
                height=40,
                radius=19,
            )
            self.scale_mode_piano_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.scale_mode_guitar_btn = GreenRoundedButton(
                self.scale_transport_icons,
                text="Guitarra",
                command=lambda: self._set_scale_play_mode("guitar"),
                width=130,
                height=40,
                radius=19,
            )
            self.scale_mode_guitar_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.scale_mode_metronome_btn = GreenRoundedButton(
                self.scale_transport_icons,
                text="Metrónomo",
                command=lambda: self._set_scale_play_mode("metronome"),
                width=160,
                height=40,
                radius=19,
            )
            self.scale_mode_metronome_btn.pack(side=tk.LEFT, padx=(0, 6))
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
            fg="#ff533d",
            font=("Helvetica", 11, "bold"),
            width=7,
            anchor="e",
        )
        self.scale_bpm_value_label.pack(side=tk.LEFT)
        self._set_scale_bpm(self.scale_bpm_value, save=False)

        self.instrument_canvas_holder = tk.Frame(container, bg=self.cget("background"))
        self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)

        self.keyboard_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#f5f4ef",
            height=156,
            highlightthickness=1,
            highlightbackground="#cfc9bc",
        )
        self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)

        self.tuner_spectrum_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#0b0c10",
            height=190,
            highlightthickness=1,
            highlightbackground="#3a3a3a",
        )
        self.tuner_spectrum_canvas.bind("<Configure>", lambda _e: self._draw_tuner_spectrum())

        self.guitar_canvas = tk.Canvas(
            self.instrument_canvas_holder,
            bg="#2f3137",
            height=196,
            highlightthickness=1,
            highlightbackground="#5c6068",
        )
        self.guitar_variations_frame = tk.Frame(self.instrument_canvas_holder, bg="#1f2024")
        self.guitar_variations_inner = tk.Frame(self.guitar_variations_frame, bg="#1f2024")
        self.guitar_variations_inner.pack(anchor="center")

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
        self._set_instrument_view(self.instrument_view)
    def apply_ui_language(self) -> None:
        self.title(self.tr("app_title"))
        self.chord_panel.configure(text="")
        self.chord_title_label.configure(text="")
        self.notes_caption_label.configure(text=self.tr("label_active_notes"))
        self.intervals_caption_label.configure(text=self.tr("label_intervals"))
        self.generated_title_label.configure(text="")
        self.generation_root_label.configure(text=self.tr("label_root_note"))
        self.generation_variant_label.configure(text=self.tr("label_variant"))
        self.generation_inversion_label.configure(text=self.tr("label_inversion"))
        self.generated_notes_caption_label.configure(text=self.tr("label_active_notes"))
        self.generated_intervals_caption_label.configure(text=self.tr("label_intervals"))
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
        if not self.handedness_buttons_are_images:
            self.guitar_right_btn.set_text(self.tr("handed_right"))
            self.guitar_left_btn.set_text(self.tr("handed_left"))
        if not self.scale_transport_buttons_are_images:
            self.scale_mode_piano_btn.set_text(self.tr("instrument_piano"))
            self.scale_mode_guitar_btn.set_text(self.tr("instrument_guitar"))
            self.scale_mode_metronome_btn.set_text(self.tr("scale_play_metronome"))
        self.scale_bpm_value_label.configure(text=f"{int(self.config_data.get('metronome_bpm', 120))} {self.tr('scale_bpm_short')}")
        self.mode_var.set(self._mode_label(self.current_mode))
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._refresh_scale_transport_styles()
        self._refresh_generation_controls()
        self._refresh_scale_preview()
        self._refresh_metronome_ui()
        self._refresh_tuner_ui()
        if not self.active_notes:
            self.status_var.set(self.tr("status_no_notes"))
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
        bg: str = "#2b2d38",
        padx: int = 8,
        pady: tuple[int, int] = (2, 10),
    ) -> tk.Frame:
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
        wrapper = tk.Frame(parent, bg="#2b2d38")
        wrapper.pack(fill=tk.X, pady=(0, 8))

        canvas = tk.Canvas(
            wrapper,
            bg="#2b2d38",
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
            bg="#1f2128",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
            font=("Helvetica", 15, "bold"),
        )
        entry_window = canvas.create_window(46, 21, anchor="w", window=entry, height=24)
        placeholder_id = canvas.create_text(50, 21, anchor="w", text=placeholder, fill="#a4a9b6", font=("Helvetica", 15, "bold"))
        clear_button_bg_id = canvas.create_oval(0, 0, 0, 0, fill="#81858f", outline="")
        clear_button_x_id = canvas.create_text(0, 0, text="✕", fill="#242730", font=("Helvetica", 10, "bold"))
        search_lens_id = canvas.create_oval(0, 0, 0, 0, outline="#eceff5", width=2)
        search_handle_id = canvas.create_line(0, 0, 0, 0, fill="#eceff5", width=2, capstyle=tk.ROUND)

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
                fill="#1f2128",
                outline="#666a74",
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
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.5, rely=0.12, anchor="n", relwidth=0.52, relheight=0.54)
        self.mode_selector_overlay = overlay

        cards_frame = tk.Frame(overlay, bg="#2b2d38")
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
                bg="#3b3f49",
                highlightthickness=2 if self.current_mode == mode_key else 1,
                highlightbackground="#f39c12" if self.current_mode == mode_key else "#3b3f49",
                bd=0,
                cursor="hand2",
            )
            card.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=10, pady=10)
            icon = tk.Label(card, text=icon_txt, bg="#3b3f49", fg=icon_color, font=("Helvetica", 34, "bold"), cursor="hand2")
            icon.pack(pady=(16, 4))
            label = tk.Label(card, text=mode_text, bg="#3b3f49", fg="#e2e4ea", font=("Helvetica", 18), cursor="hand2")
            label.pack(pady=(0, 14))

            def on_enter(_e: tk.Event, c=card) -> None:
                c.configure(bg="#434854")
                for child in c.winfo_children():
                    child.configure(bg="#434854")

            def on_leave(_e: tk.Event, c=card, is_current=(self.current_mode == mode_key)) -> None:
                base = "#3b3f49"
                c.configure(bg=base)
                for child in c.winfo_children():
                    child.configure(bg=base)
                c.configure(highlightbackground="#f39c12" if is_current else "#3b3f49")

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
        self.scale_space_pressed = False
        self.metronome_space_pressed = False
        self.tuner_space_pressed = False

        if self.generation_tab_active:
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack(fill=tk.X, pady=(0, 6), before=self.instrument_canvas_holder)
            self.scale_transport_frame.pack_forget()
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
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack(fill=tk.X, pady=(0, 6), before=self.instrument_canvas_holder)
            self._refresh_scale_transport_styles()
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
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
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_metronome_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_metronome_ui()
        elif self.tuner_tab_active:
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
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
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack_forget()
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)
            self.tab_generation_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_tuner_frame.pack_forget()
            self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)
        self.update_music_views()
