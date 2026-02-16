from __future__ import annotations

import json
from pathlib import Path
import queue
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional

import mido
import sounddevice as sd

from audio_engine import PianoAudioEngine
from i18n import NOTE_NAMES, SCALE_NAME_TEXTS, UI_TEXTS
from music_theory import CHORD_PATTERNS, SCALE_PATTERNS, PC_TO_DIATONIC_LETTER, WHITE_PCS, ChordPattern, ScalePattern, analyze_chord_notes, format_intervals
from widgets import GrayRoundedButton, GreenRoundedButton, RoundedChoiceButton


CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
BRACE_IMAGE_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "brace_left.png",
    Path(__file__).resolve().parent / "assets" / "brace_left.jpg",
    Path(__file__).resolve().parent / "assets" / "brace_left.jpeg",
    Path(__file__).resolve().parent / "assets" / "brace_left.gif",
    Path(__file__).resolve().parent / "assets" / "brace_left.ppm",
]
APP_LOGO_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "app_logo.png",
    Path(__file__).resolve().parent / "assets" / "app_logo.gif",
    Path(__file__).resolve().parent / "assets" / "app_logo.ppm",
]
class MidiChordAnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry("1300x800")
        self.minsize(980, 620)

        self.config_data = {
            "language": "es",
            "midi_input": "",
            "audio_output": "",
            "sound_preset": "acoustic",
            "show_keyboard_note_labels": False,
            "metronome_enabled": False,
            "metronome_bpm": 120,
            "mode": "detection",
        }
        self.load_config()
        self.brace_base_image: Optional[tk.PhotoImage] = None
        self.brace_image_cache: dict[tuple[int, int], tk.PhotoImage] = {}
        self.app_logo_image: Optional[tk.PhotoImage] = None
        self._load_brace_image()
        self._load_app_logo()

        self.active_notes: set[int] = set()
        self.generated_preview_notes: set[int] = set()
        self.midi_held_notes: set[int] = set()
        self.mouse_held_notes: set[int] = set()
        self.sustain_latched_notes: set[int] = set()
        self.note_velocity: dict[int, int] = {}
        self.pedal_active = False
        self.mouse_current_note: Optional[int] = None
        self.generated_playing_notes: set[int] = set()
        self.generated_play_after_id: Optional[str] = None
        self.generation_play_button_pressed = False
        self.white_key_regions: list[tuple[int, float, float, float, float]] = []
        self.black_key_regions: list[tuple[int, float, float, float, float]] = []
        self.message_queue: queue.Queue = queue.Queue()
        self.blocked_note_until: dict[int, float] = {}

        self.input_port: Optional[mido.ports.BaseInput] = None

        self.input_names: list[str] = []
        self.audio_output_names: list[str] = []
        self.audio_output_map: dict[str, int] = {}
        self.audio_engine = PianoAudioEngine()
        self.audio_engine.set_preset(str(self.config_data.get("sound_preset", "acoustic")))
        self.current_mode = str(self.config_data.get("mode", "detection"))
        if self.current_mode not in {"detection", "generation", "scales"}:
            self.current_mode = "detection"
        self.generation_tab_active = False
        self.scale_tab_active = False
        self.mode_var = tk.StringVar()
        self.generation_root_pc = 0
        self.generation_pattern_suffix = ""
        self.generation_inversion = 0
        self.scale_tonic_pc = 0
        self.scale_pattern_name = SCALE_PATTERNS[0].name
        self.scale_preview_notes: list[int] = []
        self.scale_playing_notes: set[int] = set()
        self.scale_loop_active = False
        self.scale_loop_after_id: Optional[str] = None
        self.scale_loop_index = 0
        self.scale_loop_direction = 1
        self.scale_current_note: Optional[int] = None
        self.staff_hover_note: Optional[int] = None
        self.staff_pressed_scale_notes: set[int] = set()
        self.staff_scale_note_regions: list[tuple[int, float, float, float, float, float, float]] = []
        self.scale_tonic_overlay: Optional[tk.Frame] = None
        self.scale_type_overlay: Optional[tk.Frame] = None
        self.generation_selection_overlay: Optional[tk.Frame] = None
        self.settings_overlay: Optional[tk.Frame] = None
        self.mode_selector_overlay: Optional[tk.Frame] = None
        self._settings_save_callback = None
        self.detect_hold_notes: set[int] = set()
        self.detect_hold_active = False
        self._scroll_targets: list[tuple[tk.Widget, tk.Canvas]] = []

        self._build_ui()
        self.apply_ui_language()
        self._on_mode_combo_changed(None)
        self.refresh_devices()
        self.connect_ports()
        self.after(20, self._process_midi_queue)

    def tr(self, key: str) -> str:
        language = self.config_data.get("language", "es")
        return UI_TEXTS.get(language, UI_TEXTS["en"]).get(key, key)

    def scale_name(self, canonical_name: str) -> str:
        language = self.config_data.get("language", "es")
        return SCALE_NAME_TEXTS.get(language, SCALE_NAME_TEXTS["en"]).get(canonical_name, canonical_name)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

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
            width=220,
            height=52,
            radius=26,
        )
        self.generation_root_btn.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.generation_variant_label = ttk.Label(self.tab_generation_frame, text="")
        self.generation_variant_label.grid(row=3, column=0, sticky="w", pady=(0, 2))
        self.generation_variant_btn = GreenRoundedButton(
            self.tab_generation_frame,
            text="maj",
            command=self.open_generation_variant_dialog,
            width=260,
            height=52,
            radius=26,
        )
        self.generation_variant_btn.grid(row=4, column=0, sticky="w", pady=(0, 4))

        self.generation_inversion_label = ttk.Label(self.tab_generation_frame, text="")
        self.generation_inversion_label.grid(row=5, column=0, sticky="w", pady=(0, 2))
        self.generation_inversion_btn = GreenRoundedButton(
            self.tab_generation_frame,
            text="-",
            command=self.open_generation_inversion_dialog,
            width=240,
            height=52,
            radius=26,
        )
        self.generation_inversion_btn.grid(row=6, column=0, sticky="w", pady=(0, 4))

        self.generated_chord_var = tk.StringVar(value="-")
        self.generated_chord_row = ttk.Frame(self.tab_generation_frame)
        self.generated_chord_row.grid(row=7, column=0, sticky="w", pady=(6, 4))

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
        self.generated_notes_caption_label.grid(row=8, column=0, sticky="w", pady=(4, 2))
        self.generated_notes_var = tk.StringVar(value="-")
        self.generated_notes_label = ttk.Label(
            self.tab_generation_frame,
            textvariable=self.generated_notes_var,
            wraplength=420,
            font=("Menlo", 12),
        )
        self.generated_notes_label.grid(row=9, column=0, sticky="w", pady=(0, 4))
        self.generated_intervals_caption_label = ttk.Label(self.tab_generation_frame, text="", font=("Helvetica", 12, "bold"))
        self.generated_intervals_caption_label.grid(row=10, column=0, sticky="w", pady=(2, 2))
        self.generated_intervals_var = tk.StringVar(value="-")
        self.generated_intervals_label = ttk.Label(
            self.tab_generation_frame,
            textvariable=self.generated_intervals_var,
            wraplength=420,
            font=("Menlo", 12),
        )
        self.generated_intervals_label.grid(row=11, column=0, sticky="w", pady=(0, 2))

        self.tab_generation_frame.columnconfigure(0, weight=1)

        self.scale_title_row = ttk.Frame(self.tab_scale_frame)
        self.scale_title_row.grid(row=0, column=0, sticky="w", pady=(4, 8))
        self.scale_play_btn = ttk.Button(self.scale_title_row, text="▶", width=3, command=self._toggle_scale_play)
        self.scale_play_btn.pack(side=tk.LEFT)
        self.scale_title_var = tk.StringVar(value="-")
        self.scale_title_label = ttk.Label(self.scale_title_row, textvariable=self.scale_title_var, font=("Helvetica", 28, "bold"))
        self.scale_title_label.pack(side=tk.LEFT, padx=(8, 0))

        self.scale_buttons_row = ttk.Frame(self.tab_scale_frame)
        self.scale_buttons_row.grid(row=1, column=0, sticky="w", pady=(4, 8))
        self.scale_tonic_btn = GreenRoundedButton(
            self.scale_buttons_row,
            text="C",
            command=self.open_scale_tonic_dialog,
            width=126,
            height=56,
            radius=28,
        )
        self.scale_tonic_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.scale_type_btn = GreenRoundedButton(
            self.scale_buttons_row,
            text=self.scale_pattern_name,
            command=self.open_scale_type_dialog,
            width=340,
            height=56,
            radius=28,
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

        self.status_var = tk.StringVar(value="")

        separator = ttk.Separator(container, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(10, 10))

        self.keyboard_canvas = tk.Canvas(
            container,
            bg="#f5f4ef",
            height=156,
            highlightthickness=1,
            highlightbackground="#cfc9bc",
        )
        self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)

        self.staff_canvas.bind("<Configure>", lambda _event: self.redraw_staff())
        self.staff_canvas.bind("<Motion>", self._on_staff_motion)
        self.staff_canvas.bind("<Leave>", self._on_staff_leave)
        self.staff_canvas.bind("<ButtonPress-1>", self._on_staff_press)
        self.staff_canvas.bind("<ButtonRelease-1>", self._on_staff_release)
        self.keyboard_canvas.bind("<Configure>", lambda _event: self.redraw_keyboard())
        self.keyboard_canvas.bind("<ButtonPress-1>", self._on_keyboard_press)
        self.keyboard_canvas.bind("<B1-Motion>", self._on_keyboard_drag)
        self.keyboard_canvas.bind("<ButtonRelease-1>", self._on_keyboard_release)
        self.bind_all("<KeyPress-Shift_L>", self._on_shift_press)
        self.bind_all("<KeyPress-Shift_R>", self._on_shift_press)
        self.bind_all("<KeyRelease-Shift_L>", self._on_shift_release)
        self.bind_all("<KeyRelease-Shift_R>", self._on_shift_release)
        self.bind_all("<Escape>", self._on_escape_pressed, add="+")
        self.bind_all("<Return>", self._on_return_pressed, add="+")
        self.bind_all("<space>", self._on_space_pressed, add="+")
        self.bind_all("<ButtonPress-1>", self._on_global_click_press, add="+")
        self.bind_all("<MouseWheel>", self._on_any_mousewheel, add="+")
        self.bind_all("<Shift-MouseWheel>", self._on_any_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_any_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_any_mousewheel, add="+")

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
        self.config_icon_btn.configure(text="⚙")
        self.mode_var.set(self._mode_label(self.current_mode))
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._refresh_generation_controls()
        self._refresh_scale_preview()
        if not self.active_notes:
            self.status_var.set(self.tr("status_no_notes"))

    def _refresh_generation_controls(self) -> None:
        if self.generation_pattern_suffix not in {p.suffix for p in CHORD_PATTERNS}:
            self.generation_pattern_suffix = ""
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()

    def _refresh_generation_selection_buttons(self) -> None:
        self.generation_root_btn.set_text(self.note_name(self.generation_root_pc, with_octave=False))
        variant_label = self.generation_pattern_suffix if self.generation_pattern_suffix else "maj"
        self.generation_variant_btn.set_text(variant_label)
        self.generation_inversion_btn.set_text(self._inversion_label(self.generation_inversion))

    @staticmethod
    def _pointer_inside_widget(widget: tk.Widget) -> bool:
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

    @staticmethod
    def _scroll_canvas_from_event(canvas: tk.Canvas, event: tk.Event) -> str:
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

    def _max_generation_inversion(self) -> int:
        pattern = self._resolve_generation_pattern()
        return max(0, len(pattern.intervals) - 1)

    def _clamp_generation_inversion(self) -> None:
        max_inv = self._max_generation_inversion()
        self.generation_inversion = max(0, min(self.generation_inversion, max_inv))

    def _on_generation_root_clicked(self, pc: int) -> None:
        self.generation_root_pc = pc
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()

    def _on_generation_variant_clicked(self, suffix: str) -> None:
        self.generation_pattern_suffix = suffix
        self._clamp_generation_inversion()
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()

    def _inversion_label(self, inversion: int) -> str:
        if inversion == 0:
            return self.tr("inversion_root")
        language = self.config_data.get("language", "es")
        if language == "es":
            return f"{inversion}ª inversión"
        ord_map = {1: "1st", 2: "2nd", 3: "3rd"}
        ord_txt = ord_map.get(inversion, f"{inversion}th")
        return f"{ord_txt} inversion"

    def _on_generation_inversion_clicked(self, inversion: int) -> None:
        self.generation_inversion = inversion
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()

    def _close_generation_selection_overlay(self) -> None:
        if self.generation_selection_overlay is not None:
            self.generation_selection_overlay.destroy()
            self.generation_selection_overlay = None

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

    def _open_generation_selection_overlay(self, kind: str) -> None:
        if self.generation_selection_overlay is not None:
            self._close_generation_selection_overlay()

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.generation_selection_overlay = overlay

        header = tk.Frame(overlay, bg="#2b2d38")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        if kind == "root":
            title = self.tr("label_root_note")
        elif kind == "variant":
            title = self.tr("label_variant")
        else:
            title = self.tr("label_inversion")
        tk.Label(header, text=title, bg="#2b2d38", fg="#f0f0f0", font=("Helvetica", 13, "bold")).pack(side=tk.LEFT)

        buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))

        if kind == "root":
            columns = 3
            options: list[tuple[str, int, bool]] = []
            for pc in range(12):
                options.append((self.note_name(pc, with_octave=False), pc, pc == self.generation_root_pc))
        elif kind == "variant":
            columns = 3
            options = []
            for pattern in CHORD_PATTERNS:
                label = pattern.suffix if pattern.suffix else "maj"
                options.append((label, pattern.suffix, pattern.suffix == self.generation_pattern_suffix))
        else:
            columns = 3
            options = []
            for inv in range(self._max_generation_inversion() + 1):
                options.append((self._inversion_label(inv), inv, inv == self.generation_inversion))

        for col in range(columns):
            buttons_frame.columnconfigure(col, weight=1)

        for idx, (label, value, selected) in enumerate(options):
            btn = GrayRoundedButton(
                buttons_frame,
                text=str(label),
                command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                width=160 if kind != "root" else 122,
                height=74 if kind == "root" else 64,
                radius=28 if kind == "root" else 24,
                font_size=16 if kind == "inversion" else 22,
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
        self._open_generation_selection_overlay("inversion")

    def _resolve_scale_pattern(self) -> ScalePattern:
        for pattern in SCALE_PATTERNS:
            if pattern.name == self.scale_pattern_name:
                return pattern
        return SCALE_PATTERNS[0]

    def _refresh_scale_preview(self) -> None:
        pattern = self._resolve_scale_pattern()
        tonic_name = self.note_name(self.scale_tonic_pc, with_octave=False)
        localized_scale_name = self.scale_name(pattern.name)
        self.scale_tonic_btn.set_text(tonic_name)
        self.scale_type_btn.set_text(localized_scale_name)
        self.scale_title_var.set(f"{tonic_name} {localized_scale_name}")

        root_midi = 60 + self.scale_tonic_pc
        self.scale_preview_notes = [root_midi + interval for interval in pattern.intervals]
        if self.scale_preview_notes:
            self.scale_notes_var.set(" - ".join(self.note_name(note) for note in self.scale_preview_notes))
            self.scale_intervals_var.set(self.format_intervals(set(self.scale_preview_notes)))
        else:
            self.scale_notes_var.set("-")
            self.scale_intervals_var.set("-")

    def open_scale_tonic_dialog(self) -> None:
        if self.scale_tonic_overlay is not None:
            self._close_scale_tonic_overlay()
            return

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.scale_tonic_overlay = overlay

        header = tk.Frame(overlay, bg="#2b2d38")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_scale_tonic"),
            bg="#2b2d38",
            fg="#f0f0f0",
            font=("Helvetica", 13, "bold"),
        ).pack(side=tk.LEFT)

        buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
        for col in range(3):
            buttons_frame.columnconfigure(col, weight=1)
        for pc in range(12):
            btn = GrayRoundedButton(
                buttons_frame,
                text=self.note_name(pc, with_octave=False),
                command=lambda p=pc: self._select_scale_tonic_from_overlay(p),
                width=122,
                height=74,
                radius=28,
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
            bg="#2b2d38",
            highlightthickness=1,
            highlightbackground="#4a4f5f",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self.scale_type_overlay = overlay

        header = tk.Frame(overlay, bg="#2b2d38")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_scale_type"),
            bg="#2b2d38",
            fg="#f0f0f0",
            font=("Helvetica", 13, "bold"),
        ).pack(side=tk.LEFT)

        body = tk.Frame(overlay, bg="#2b2d38")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))
        tk.Label(
            body,
            text=self.tr("label_search_scale"),
            bg="#2b2d38",
            fg="#dfe2e8",
            font=("Helvetica", 11),
        ).pack(anchor="w")
        search_var = tk.StringVar(value="")
        entry = ttk.Entry(body, textvariable=search_var, width=34)
        entry.pack(fill=tk.X, pady=(4, 8))

        buttons_frame = self._build_scrollable_area(body, bg="#2b2d38", padx=0, pady=(0, 0))
        for col in range(2):
            buttons_frame.columnconfigure(col, weight=1)

        def render_buttons() -> None:
            for w in buttons_frame.winfo_children():
                w.destroy()

            term = search_var.get().strip().lower()
            filtered = [p for p in SCALE_PATTERNS if term in self.scale_name(p.name).lower()]
            primary_modes = {"Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"}
            for idx, pattern in enumerate(filtered):
                is_primary = pattern.name in primary_modes
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=self.scale_name(pattern.name),
                    command=lambda n=pattern.name: self._select_scale_type_from_overlay(n),
                    width=208,
                    height=64,
                    radius=24,
                    font_size=16,
                    text_color="#19d27f" if is_primary else "#f2f2f2",
                    selected_text_color="#19d27f" if is_primary else "#ffffff",
                )
                btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=6, pady=6)
                btn.set_selected(pattern.name == self.scale_pattern_name)

        def on_search(*_args) -> None:
            render_buttons()

        search_var.trace_add("write", on_search)
        render_buttons()
        entry.focus_set()

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

    @staticmethod
    def _is_widget_inside(parent: tk.Widget, child: tk.Widget) -> bool:
        current: Optional[tk.Widget] = child
        while current is not None:
            if current == parent:
                return True
            current = current.master
        return False

    def _on_escape_pressed(self, _event: tk.Event) -> None:
        self._close_mode_selector_overlay()
        self._close_scale_tonic_overlay()
        self._close_scale_type_overlay()
        self._close_generation_selection_overlay()
        self._close_settings_overlay()

    def _on_return_pressed(self, _event: tk.Event) -> Optional[str]:
        if self.settings_overlay is not None and callable(self._settings_save_callback):
            self._settings_save_callback()
            return "break"
        return None

    def _on_space_pressed(self, _event: tk.Event) -> Optional[str]:
        if self.scale_tab_active:
            self._toggle_scale_play()
            return "break"
        return None

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
        if self.settings_overlay is not None and not self._is_widget_inside(self.settings_overlay, widget):
            if widget != self.config_icon_btn:
                self._close_settings_overlay()
        if self.mode_selector_overlay is not None and not self._is_widget_inside(self.mode_selector_overlay, widget):
            if not self._is_widget_inside(self.mode_picker_trigger, widget):
                self._close_mode_selector_overlay()

    def _mode_label(self, mode_key: str) -> str:
        if mode_key == "generation":
            return self.tr("mode_generation")
        if mode_key == "scales":
            return self.tr("mode_scales")
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
        overlay.place(relx=0.5, rely=0.12, anchor="n", relwidth=0.52, relheight=0.38)
        self.mode_selector_overlay = overlay

        cards_frame = tk.Frame(overlay, bg="#2b2d38")
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        cards_frame.rowconfigure(1, weight=1)

        options = [
            ("detection", self._mode_label("detection"), "◎", "#ffa320"),
            ("generation", self._mode_label("generation"), "♬", "#39c8ff"),
            ("scales", self._mode_label("scales"), "♪", "#e4eb3f"),
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
        self._close_settings_overlay()
        self._stop_staff_scale_note_playback()
        selected = self.mode_var.get()
        if selected == self._mode_label("generation"):
            self.current_mode = "generation"
        elif selected == self._mode_label("scales"):
            self.current_mode = "scales"
        else:
            self.current_mode = "detection"
        self.config_data["mode"] = self.current_mode
        self.save_config()
        self.mode_trigger_var.set(self._mode_label(self.current_mode))

        self.generation_tab_active = self.current_mode == "generation"
        self.scale_tab_active = self.current_mode == "scales"
        self._stop_generated_playback()
        self._stop_scale_playback()

        if self.generation_tab_active:
            detected_notes = self._current_detection_notes()
            self._clear_live_input_state()
            if detected_notes:
                self._load_generation_from_detected_notes(detected_notes)
            self.tab_detection_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_generation_frame.pack(fill=tk.BOTH, expand=True)
        elif self.scale_tab_active:
            self._clear_live_input_state()
            self.tab_detection_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
            self.tab_scale_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_scale_preview()
        else:
            self.tab_generation_frame.pack_forget()
            self.tab_scale_frame.pack_forget()
            self.tab_detection_frame.pack(fill=tk.BOTH, expand=True)
        self.update_music_views()

    def _resolve_generation_pattern(self) -> ChordPattern:
        for pattern in CHORD_PATTERNS:
            if pattern.suffix == self.generation_pattern_suffix:
                return pattern
        return CHORD_PATTERNS[0]

    def _update_generation_preview(self) -> None:
        was_playing = self.generation_play_button_pressed or bool(self.generated_playing_notes)
        if was_playing:
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

        voiced_intervals = [(interval + (12 if idx < inversion else 0)) for idx, interval in enumerate(intervals)]
        voiced_intervals.sort()
        voiced_notes = [root_midi + interval for interval in voiced_intervals]
        self.generated_preview_notes = set(voiced_notes)

        shown_suffix = pattern.suffix if pattern.suffix else ""
        chord_name = f"{self.note_name(self.generation_root_pc, with_octave=False)}{shown_suffix}"
        if inversion > 0 and voiced_notes:
            bass_pc = voiced_notes[0] % 12
            chord_name = f"{chord_name}/{self.note_name(bass_pc, with_octave=False)}"
        self.generated_chord_var.set(chord_name)
        if self.generated_preview_notes:
            ordered = sorted(self.generated_preview_notes)
            self.generated_notes_var.set(" - ".join(self.note_name(note) for note in ordered))
        else:
            self.generated_notes_var.set("-")

        if was_playing and self.generation_play_button_pressed:
            self._play_generated_chord()

        if self.generation_tab_active:
            self.update_music_views()

    def _clear_live_input_state(self) -> None:
        for note in list(self.active_notes):
            self.audio_engine.note_off(note)
        self.active_notes.clear()
        self.midi_held_notes.clear()
        self.mouse_held_notes.clear()
        self.sustain_latched_notes.clear()
        self.note_velocity.clear()
        self.mouse_current_note = None

    def _clear_detection_hold(self) -> None:
        self.detect_hold_active = False
        self.detect_hold_notes.clear()

    def _current_detection_notes(self) -> set[int]:
        if self.active_notes:
            return set(self.active_notes)
        if self.detect_hold_active:
            return set(self.detect_hold_notes)
        return set()

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

    def _stop_generated_playback(self) -> None:
        if self.generated_play_after_id is not None:
            try:
                self.after_cancel(self.generated_play_after_id)
            except Exception:
                pass
            self.generated_play_after_id = None
        for note in list(self.generated_playing_notes):
            self.audio_engine.note_off(note)
        self.generated_playing_notes.clear()

    def _stop_scale_playback(self) -> None:
        self.scale_loop_active = False
        if self.scale_loop_after_id is not None:
            try:
                self.after_cancel(self.scale_loop_after_id)
            except Exception:
                pass
            self.scale_loop_after_id = None
        if self.scale_current_note is not None:
            self.audio_engine.note_off(self.scale_current_note)
            self.scale_current_note = None
        for note in list(self.scale_playing_notes):
            self.audio_engine.note_off(note)
        self.scale_playing_notes.clear()
        self.scale_play_btn.configure(text="▶")
        if self.scale_tab_active:
            self.redraw_keyboard()
            self.redraw_staff()

    def _stop_staff_scale_note_playback(self) -> None:
        if not self.staff_pressed_scale_notes and self.staff_hover_note is None:
            return
        for note in list(self.staff_pressed_scale_notes):
            self.audio_engine.note_off(note)
        self.staff_pressed_scale_notes.clear()
        self.staff_hover_note = None
        self.staff_scale_note_regions.clear()
        self.redraw_keyboard()
        self.redraw_staff()

    def _staff_scale_note_at_position(self, x: float, y: float) -> Optional[int]:
        if not self.scale_tab_active:
            return None
        best_note: Optional[int] = None
        best_dist = 10_000.0
        for note, cx, cy, rx, ry, label_y, label_half_w in self.staff_scale_note_regions:
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
        return best_note

    def _on_staff_motion(self, event: tk.Event) -> None:
        if not self.scale_tab_active:
            return
        note = self._staff_scale_note_at_position(float(event.x), float(event.y))
        if note != self.staff_hover_note:
            self.staff_hover_note = note
            self.redraw_staff()
        self.staff_canvas.configure(cursor="hand2" if note is not None else "")

    def _on_staff_leave(self, _event: tk.Event) -> None:
        if not self.scale_tab_active:
            return
        if self.staff_hover_note is not None:
            self.staff_hover_note = None
            self.redraw_staff()
        self.staff_canvas.configure(cursor="")

    def _on_staff_press(self, event: tk.Event) -> None:
        if not self.scale_tab_active:
            return
        note = self._staff_scale_note_at_position(float(event.x), float(event.y))
        if note is None:
            return
        self.staff_hover_note = note
        if note not in self.staff_pressed_scale_notes:
            self.staff_pressed_scale_notes.add(note)
            self.audio_engine.note_on(note, 106)
        self.redraw_staff()
        self.redraw_keyboard()

    def _on_staff_release(self, event: tk.Event) -> None:
        if not self.scale_tab_active:
            return
        if self.staff_pressed_scale_notes:
            for note in list(self.staff_pressed_scale_notes):
                self.audio_engine.note_off(note)
            self.staff_pressed_scale_notes.clear()
        self.staff_hover_note = self._staff_scale_note_at_position(float(event.x), float(event.y))
        self.redraw_staff()
        self.redraw_keyboard()

    def _play_generated_chord(self) -> None:
        if not self.generated_preview_notes:
            return
        self._stop_generated_playback()
        for note in sorted(self.generated_preview_notes):
            self.audio_engine.note_on(note, 108)
            self.generated_playing_notes.add(note)

    def _play_scale(self) -> None:
        self._stop_scale_playback()
        if not self.scale_preview_notes:
            return
        self.scale_loop_active = True
        self.scale_loop_index = 0
        self.scale_loop_direction = 1
        self.scale_play_btn.configure(text="■")
        self._play_next_scale_step()

    def _scale_step_ms(self) -> int:
        bpm = int(self.config_data.get("metronome_bpm", 120))
        bpm = max(30, min(240, bpm))
        return int(60000 / bpm)

    def _play_metronome_click(self, accent: bool) -> None:
        if not bool(self.config_data.get("metronome_enabled", False)):
            return
        self.audio_engine.metronome_click(accent=accent)

    def _play_next_scale_step(self) -> None:
        if not self.scale_loop_active or not self.scale_preview_notes:
            return

        notes = self.scale_preview_notes
        idx = max(0, min(self.scale_loop_index, len(notes) - 1))
        note = notes[idx]

        if self.scale_current_note is not None:
            if self.scale_current_note not in self.staff_pressed_scale_notes:
                self.audio_engine.note_off(self.scale_current_note)
            self.scale_playing_notes.discard(self.scale_current_note)
        self.audio_engine.note_on(note, 104)
        self.scale_playing_notes.add(note)
        self.scale_current_note = note
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

    def _on_generation_play_press(self, _event: tk.Event) -> str:
        self.generation_play_button_pressed = True
        self.generation_play_btn.state(["pressed"])
        self._play_generated_chord()
        return "break"

    def _toggle_scale_play(self) -> None:
        if self.scale_loop_active:
            self._stop_scale_playback()
        else:
            self._play_scale()

    def _on_global_mouse_release(self, _event: tk.Event) -> None:
        if self.generation_play_button_pressed:
            self.generation_play_button_pressed = False
            self.generation_play_btn.state(["!pressed"])
            self._stop_generated_playback()

    def _show_forbidden_note_feedback(self, note: int) -> None:
        self.blocked_note_until[note] = time.monotonic() + 0.35
        self.redraw_keyboard()
        self.after(380, self.redraw_keyboard)

    @staticmethod
    def _draw_forbidden_icon(canvas: tk.Canvas, cx: float, cy: float, radius: float) -> None:
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#d32f2f", width=2)
        canvas.create_line(cx - radius * 0.65, cy + radius * 0.65, cx + radius * 0.65, cy - radius * 0.65, fill="#d32f2f", width=2)

    def load_config(self) -> None:
        if not CONFIG_PATH.exists():
            return
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(loaded, dict):
            return
        for key in self.config_data:
            if key in loaded:
                self.config_data[key] = loaded[key]

    def _load_brace_image(self) -> None:
        self.brace_base_image = None
        self.brace_image_cache.clear()
        for path in BRACE_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                self.brace_base_image = tk.PhotoImage(file=str(path))
                return
            except tk.TclError:
                continue

    def _load_app_logo(self) -> None:
        self.app_logo_image = None
        for path in APP_LOGO_CANDIDATES:
            if not path.exists():
                continue
            try:
                self.app_logo_image = tk.PhotoImage(file=str(path))
                self.iconphoto(True, self.app_logo_image)
                return
            except tk.TclError:
                continue

    def _get_brace_image_for_height(self, target_height: int) -> Optional[tk.PhotoImage]:
        if self.brace_base_image is None or target_height <= 0:
            return None

        base_h = self.brace_base_image.height()
        if base_h <= 0:
            return None

        best_zoom, best_sub = 1, 1
        best_diff = abs(base_h - target_height)
        for zoom in range(1, 6):
            for sub in range(1, 10):
                h = max(1, (base_h * zoom) // sub)
                diff = abs(h - target_height)
                if diff < best_diff:
                    best_zoom, best_sub = zoom, sub
                    best_diff = diff

        if best_zoom == 1 and best_sub == 1:
            return self.brace_base_image

        key = (best_zoom, best_sub)
        cached = self.brace_image_cache.get(key)
        if cached is not None:
            return cached

        img = self.brace_base_image.zoom(best_zoom, best_zoom)
        if best_sub > 1:
            img = img.subsample(best_sub, best_sub)
        self.brace_image_cache[key] = img
        return img

    def save_config(self) -> None:
        CONFIG_PATH.write_text(json.dumps(self.config_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def refresh_devices(self) -> None:
        try:
            self.input_names = mido.get_input_names()
        except Exception as exc:
            self.status_var.set(f"{self.tr('error_list_inputs')}: {exc}")
            self.input_names = []

        self.audio_output_map = {}
        self.audio_output_names = []
        try:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if int(device.get("max_output_channels", 0)) <= 0:
                    continue
                name = f"{idx}: {device.get('name', 'Output')}"
                self.audio_output_map[name] = idx
                self.audio_output_names.append(name)
        except Exception as exc:
            self.status_var.set(f"{self.tr('error_list_outputs')}: {exc}")
            self.audio_output_names = []
            self.audio_output_map = {}

    def connect_ports(self) -> None:
        self.disconnect_ports()
        self.audio_engine.set_preset(str(self.config_data.get("sound_preset", "acoustic")))

        input_name = self.config_data.get("midi_input", "")
        audio_name = self.config_data.get("audio_output", "")
        audio_error: Optional[str] = None

        if input_name:
            try:
                self.input_port = mido.open_input(input_name, callback=self._on_midi_message)
            except Exception as exc:
                self.status_var.set(f"{self.tr('error_open_input')}: {exc}")
                self.input_port = None

        audio_device_index = self.audio_output_map.get(audio_name)
        try:
            self.audio_engine.start(audio_device_index)
        except Exception as exc:
            audio_error = str(exc)

        in_state = input_name if self.input_port else self.tr("status_no_input")
        if self.audio_engine.stream is None:
            out_state = self.tr("status_unavailable")
        elif audio_name and audio_name in self.audio_output_map:
            out_state = audio_name
        else:
            out_state = self.tr("status_default_output")

        status = f"{self.tr('status_input')}: {in_state}\n{self.tr('status_output')}: {out_state}"
        if audio_error:
            status += f"\n{self.tr('status_audio_error')}: {audio_error}"
        self.status_var.set(status)

    def disconnect_ports(self) -> None:
        if self.input_port is not None:
            try:
                self.input_port.close()
            except Exception:
                pass
            self.input_port = None

        self.audio_engine.stop()

    def _on_midi_message(self, message: mido.Message) -> None:
        self.message_queue.put(message)

    def _refresh_sounding_notes(self) -> None:
        next_active = self.midi_held_notes | self.mouse_held_notes | self.sustain_latched_notes
        to_start = next_active - self.active_notes
        to_stop = self.active_notes - next_active

        for note in to_start:
            self.audio_engine.note_on(note, int(self.note_velocity.get(note, 100)))
        for note in to_stop:
            self.audio_engine.note_off(note)

        if next_active != self.active_notes:
            self.active_notes = next_active
            self.update_music_views()

    def _note_on_from_source(self, note: int, velocity: int, source: str) -> None:
        if self.current_mode == "detection" and self.detect_hold_active:
            self._clear_detection_hold()
        velocity = int(max(1, min(127, velocity)))
        self.note_velocity[note] = velocity
        self.sustain_latched_notes.discard(note)
        if source == "midi":
            self.midi_held_notes.add(note)
        else:
            self.mouse_held_notes.add(note)

    def _note_off_from_source(self, note: int, source: str) -> None:
        if source == "midi":
            self.midi_held_notes.discard(note)
        else:
            self.mouse_held_notes.discard(note)

        if self.pedal_active:
            if note not in self.midi_held_notes and note not in self.mouse_held_notes:
                self.sustain_latched_notes.add(note)
        else:
            self.sustain_latched_notes.discard(note)

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
        if self.generation_tab_active:
            self._show_forbidden_note_feedback(note)
            return
        if self.pedal_active and note in self.active_notes:
            # Toggle con pedal: clic en nota activa la deselecciona.
            self.mouse_held_notes.discard(note)
            self.sustain_latched_notes.discard(note)
            if self.mouse_current_note == note:
                self.mouse_current_note = None
            self._refresh_sounding_notes()
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
        if self.generation_tab_active:
            if note is not None:
                self._show_forbidden_note_feedback(note)
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
        if self.mouse_current_note is not None:
            self._note_off_from_source(self.mouse_current_note, source="mouse")
            self.mouse_current_note = None
            self._refresh_sounding_notes()

    def _on_shift_press(self, _event: tk.Event) -> None:
        if self.current_mode == "detection" and self.detect_hold_active:
            self._clear_detection_hold()
            self.update_music_views()
        self.pedal_active = True

    def _on_shift_release(self, _event: tk.Event) -> None:
        prev_active = set(self.active_notes)
        self.pedal_active = False
        self.sustain_latched_notes.clear()
        self._refresh_sounding_notes()
        if self.current_mode == "detection" and prev_active and not self.active_notes:
            self.detect_hold_notes = prev_active
            self.detect_hold_active = True
            self.update_music_views()

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

            if message.type == "note_on" and message.velocity > 0:
                self._note_on_from_source(message.note, velocity=int(message.velocity), source="midi")
                changed = True
            elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                self._note_off_from_source(message.note, source="midi")
                changed = True

        if changed:
            self._refresh_sounding_notes()

        self.after(20, self._process_midi_queue)

    def note_name(self, midi_note: int, with_octave: bool = True) -> str:
        language = self.config_data.get("language", "es")
        base_names = NOTE_NAMES.get(language, NOTE_NAMES["en"])
        name = base_names[midi_note % 12]
        if not with_octave:
            return name
        octave = midi_note // 12 - 1
        return f"{name}{octave}"

    @staticmethod
    def format_intervals(notes: set[int]) -> str:
        return format_intervals(notes)

    @staticmethod
    def _diatonic_index(midi_note: int) -> int:
        octave = midi_note // 12 - 1
        letter_index = PC_TO_DIATONIC_LETTER[midi_note % 12]
        return octave * 7 + letter_index

    def _analyze_chord_notes(self, notes: set[int]) -> tuple[Optional[int], Optional[ChordPattern], Optional[int]]:
        return analyze_chord_notes(notes)

    def detect_chord(self, notes: Optional[set[int]] = None) -> str:
        chord_notes = set(notes if notes is not None else self._current_detection_notes())
        if not chord_notes:
            return "-"

        pcs = {note % 12 for note in chord_notes}
        if len(pcs) == 1:
            note = next(iter(pcs))
            return self.note_name(note, with_octave=False)

        best_root, best_pattern, bass_pc = self._analyze_chord_notes(chord_notes)

        if best_root is None or best_pattern is None:
            ordered = sorted(chord_notes)
            return " + ".join(self.note_name(n, with_octave=False) for n in ordered)

        root = best_root
        pattern = best_pattern
        chord = f"{self.note_name(root, with_octave=False)}{pattern.suffix}"

        if bass_pc is not None and bass_pc != root:
            chord = f"{chord}/{self.note_name(bass_pc, with_octave=False)}"

        return chord

    def update_music_views(self) -> None:
        self._refresh_scale_preview()
        active_set = self._current_detection_notes()
        generated_set = set(self.generated_preview_notes)

        if active_set:
            active_ordered = sorted(active_set)
            self.notes_var.set(" - ".join(self.note_name(note) for note in active_ordered))
        else:
            self.notes_var.set("-")
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
            self.chord_var.set(self.scale_title_var.get())
        else:
            self.chord_var.set(self.detect_chord(active_set))
        self.redraw_keyboard()
        self.redraw_staff()

    def redraw_keyboard(self) -> None:
        canvas = self.keyboard_canvas
        canvas.delete("all")
        self.white_key_regions = []
        self.black_key_regions = []
        if self.generation_tab_active:
            display_active_notes = set(self.generated_preview_notes)
        elif self.scale_tab_active:
            display_active_notes = set(self.active_notes) | set(self.staff_pressed_scale_notes)
            if self.scale_loop_active and self.scale_current_note is not None:
                display_active_notes.add(self.scale_current_note)
        else:
            display_active_notes = self._current_detection_notes()
        if self.scale_tab_active:
            name_overlay_notes = set(self.active_notes) | set(self.staff_pressed_scale_notes)
            if self.scale_loop_active and self.scale_current_note is not None:
                name_overlay_notes.add(self.scale_current_note)
        elif self.generation_tab_active:
            name_overlay_notes = set(self.generated_preview_notes)
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
        if self.scale_tab_active:
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
                    label_y_base = treble_top - 16
                    low_bound = treble_bottom_line_diatonic
                    high_bound = treble_top_line_diatonic
                    staff_base_y = treble_top + 4 * line_space
                else:
                    placed_cols = placed_bass_cols
                    diatonic_idx = self._diatonic_index(note)
                    diatonic_steps = diatonic_idx - bass_bottom_line_diatonic
                    y = bass_top + 4 * line_space - diatonic_steps * staff_step
                    label_y_base = bass_top - 14
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
                    is_pressed = note in self.staff_pressed_scale_notes
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
                for ledger_y in ledger_lines_y:
                    canvas.create_line(x - ledger_half, ledger_y, x + ledger_half, ledger_y, fill="#bfbfbf", width=1)
                if self.scale_tab_active:
                    label_text = self.note_name(note, with_octave=False)
                    label_y = label_y_base
                    is_label_hl = (self.staff_hover_note == note) or (note in self.staff_pressed_scale_notes)
                    label_fill = "#7ed1ff" if is_label_hl else "#d4d8df"
                    canvas.create_text(
                        x,
                        label_y,
                        text=label_text,
                        fill=label_fill,
                        font=("Helvetica", 11, "bold" if is_label_hl else "normal"),
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

        sound_options = [
            ("acoustic", self.tr("sound_acoustic")),
            ("warm", self.tr("sound_warm")),
            ("bright", self.tr("sound_bright")),
            ("soft", self.tr("sound_soft")),
        ]
        sound_id_to_label = {sid: label for sid, label in sound_options}
        sound_label_to_id = {label: sid for sid, label in sound_options}
        current_sound = str(self.config_data.get("sound_preset", "acoustic"))
        if current_sound not in sound_id_to_label:
            current_sound = "acoustic"

        ttk.Label(frame, text=self.tr("settings_sound")).grid(row=3, column=0, sticky="w", pady=4)
        sound_var = tk.StringVar(value=sound_id_to_label[current_sound])
        sound_combo = ttk.Combobox(
            frame,
            textvariable=sound_var,
            state="readonly",
            values=[label for _, label in sound_options],
            width=48,
        )
        sound_combo.grid(row=3, column=1, sticky="ew", pady=4)

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
        show_labels_chk.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 4))

        metronome_enabled_var = tk.BooleanVar(value=bool(self.config_data.get("metronome_enabled", False)))
        metronome_chk = ttk.Checkbutton(
            frame,
            text=self.tr("settings_metronome"),
            variable=metronome_enabled_var,
        )
        metronome_chk.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 4))

        ttk.Label(frame, text=self.tr("settings_metronome_bpm")).grid(row=6, column=0, sticky="w", pady=4)
        bpm_var = tk.StringVar(value=str(int(self.config_data.get("metronome_bpm", 120))))
        bpm_spin = ttk.Spinbox(frame, from_=30, to=240, increment=1, textvariable=bpm_var, width=8)
        bpm_spin.grid(row=6, column=1, sticky="w", pady=4)

        def do_save(_event: Optional[tk.Event] = None) -> str:
            self.config_data["language"] = lang_label_to_id.get(lang_var.get(), "es")
            self.config_data["midi_input"] = in_var.get().strip()
            self.config_data["audio_output"] = out_var.get().strip()
            self.config_data["sound_preset"] = sound_label_to_id.get(sound_var.get(), "acoustic")
            self.config_data["show_keyboard_note_labels"] = bool(show_labels_var.get())
            self.config_data["metronome_enabled"] = bool(metronome_enabled_var.get())
            try:
                bpm_value = int(float(bpm_var.get()))
            except (TypeError, ValueError):
                bpm_value = 120
            self.config_data["metronome_bpm"] = max(30, min(240, bpm_value))
            self.apply_ui_language()
            self.save_config()
            self.connect_ports()
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

    def on_close(self) -> None:
        self._stop_generated_playback()
        self._stop_scale_playback()
        self._stop_staff_scale_note_playback()
        self.disconnect_ports()
        self.destroy()


def main() -> None:
    app = MidiChordAnalyzerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.update_music_views()
    app.mainloop()


if __name__ == "__main__":
    main()
