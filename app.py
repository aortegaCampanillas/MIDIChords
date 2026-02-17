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
from guitar_chord_cache import get_cached_variations, load_guitar_chord_cache
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
PIANO_IMAGE_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "piano.png",
    Path(__file__).resolve().parent / "assets" / "piano.gif",
    Path(__file__).resolve().parent / "assets" / "piano.ppm",
]
METRONOME_IMAGE_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "metronome.png",
    Path(__file__).resolve().parent / "assets" / "metronome.gif",
    Path(__file__).resolve().parent / "assets" / "metronome.ppm",
]
GUITAR_IMAGE_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "guitar.png",
    Path(__file__).resolve().parent / "assets" / "guitar.gif",
    Path(__file__).resolve().parent / "assets" / "guitar.ppm",
]
RIGHT_HAND_ICON_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "right_hand.png",
    Path(__file__).resolve().parent / "assets" / "right_hand.gif",
    Path(__file__).resolve().parent / "assets" / "right_hand.ppm",
]
LEFT_HAND_ICON_CANDIDATES = [
    Path(__file__).resolve().parent / "assets" / "left_hand.png",
    Path(__file__).resolve().parent / "assets" / "left_hand.gif",
    Path(__file__).resolve().parent / "assets" / "left_hand.ppm",
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
            "metronome_bpm": 120,
            "metronome_beats_per_bar": 4,
            "metronome_clicks_per_beat": 1,
            "metronome_timer_enabled": False,
            "metronome_timer_minutes": 2,
            "metronome_timer_seconds": 0,
            "metronome_bar_accent_enabled": True,
            "scale_play_mode": "piano",
            "mode": "detection",
            "instrument_view": "piano",
            "guitar_handedness": "right",
        }
        self.load_config()
        self.brace_base_image: Optional[tk.PhotoImage] = None
        self.brace_image_cache: dict[tuple[int, int], tk.PhotoImage] = {}
        self.app_logo_image: Optional[tk.PhotoImage] = None
        self.piano_image: Optional[tk.PhotoImage] = None
        self.metronome_image: Optional[tk.PhotoImage] = None
        self.guitar_image: Optional[tk.PhotoImage] = None
        self.right_hand_icon_image: Optional[tk.PhotoImage] = None
        self.left_hand_icon_image: Optional[tk.PhotoImage] = None
        self.instrument_buttons_are_images = False
        self.scale_transport_buttons_are_images = False
        self.handedness_buttons_are_images = False
        self._load_brace_image()
        self._load_app_logo()
        self._load_instrument_icons()

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
        self.generation_play_space_pressed = False
        self.generation_space_release_after_id: Optional[str] = None
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
        if self.current_mode not in {"detection", "generation", "scales", "metronome"}:
            self.current_mode = "detection"
        self.generation_tab_active = False
        self.scale_tab_active = False
        self.metronome_tab_active = False
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
        self.scale_space_pressed = False
        self.scale_space_release_after_id: Optional[str] = None
        self.metronome_space_pressed = False
        self.metronome_space_release_after_id: Optional[str] = None
        self.staff_hover_note: Optional[int] = None
        self.staff_pressed_scale_notes: set[int] = set()
        self.staff_scale_note_regions: list[tuple[int, float, float, float, float, float, float]] = []
        self.scale_tonic_overlay: Optional[tk.Frame] = None
        self.scale_type_overlay: Optional[tk.Frame] = None
        self.generation_selection_overlay: Optional[tk.Frame] = None
        self.settings_overlay: Optional[tk.Frame] = None
        self.mode_selector_overlay: Optional[tk.Frame] = None
        self.instrument_view = "piano"
        self.scale_play_mode = "piano"
        self.scale_bpm_min = 1
        self.scale_bpm_max = 300
        self.scale_bpm_value = int(self.config_data.get("metronome_bpm", 120))
        self.scale_transport_pressed_mode: Optional[str] = None
        self.guitar_handedness = "right"
        self.guitar_variations: list[dict] = []
        self.guitar_selected_variation_idx: Optional[int] = None
        self.guitar_selected_variation_notes: set[int] = set()
        self.guitar_variation_buttons: list[tk.Button] = []
        self._last_guitar_chord_key: Optional[tuple[int, str]] = None
        self.guitar_current_root_pc: Optional[int] = None
        self._settings_save_callback = None
        self.detect_hold_notes: set[int] = set()
        self.detect_hold_active = False
        self._scroll_targets: list[tuple[tk.Widget, tk.Canvas]] = []
        self.guitar_chord_cache = load_guitar_chord_cache()
        self.metronome_bpm = max(1, min(300, int(self.config_data.get("metronome_bpm", 120))))
        self.metronome_beats_per_bar = max(1, min(16, int(self.config_data.get("metronome_beats_per_bar", 4))))
        self.metronome_clicks_per_beat = max(1, min(16, int(self.config_data.get("metronome_clicks_per_beat", 1))))
        self.metronome_timer_enabled = bool(self.config_data.get("metronome_timer_enabled", False))
        self.metronome_timer_minutes = max(0, min(99, int(self.config_data.get("metronome_timer_minutes", 2))))
        self.metronome_timer_seconds = max(0, min(59, int(self.config_data.get("metronome_timer_seconds", 0))))
        self.metronome_bar_accent_enabled = bool(self.config_data.get("metronome_bar_accent_enabled", True))
        self.metronome_click_figure_defs = [
            {"key": "q", "clicks": 1, "glyph": "♩", "triplet": False},
            {"key": "e", "clicks": 2, "glyph": "♪♪", "triplet": False},
            {"key": "s", "clicks": 4, "glyph": "♬", "triplet": False},
            {"key": "t3", "clicks": 3, "glyph": "♪♪♪", "triplet": True},
            {"key": "t6", "clicks": 6, "glyph": "♬♬", "triplet": True},
        ]
        self.metronome_click_figure_key = next(
            (str(f["key"]) for f in self.metronome_click_figure_defs if int(f["clicks"]) == self.metronome_clicks_per_beat),
            "q",
        )
        self.metronome_figure_buttons: dict[str, tk.Canvas] = {}
        self.metronome_running = False
        self.metronome_after_id: Optional[str] = None
        self.metronome_anim_after_id: Optional[str] = None
        self.metronome_current_beat = 0
        self.metronome_current_subclick = 0
        self.metronome_tick_count = 0
        self.metronome_direction = 1
        self.metronome_motion_start_ts = time.monotonic()
        self.metronome_timer_remaining = 0.0
        self.metronome_timer_last_ts = time.monotonic()

        self._build_ui()
        loaded_instrument_view = str(self.config_data.get("instrument_view", "piano"))
        loaded_handedness = str(self.config_data.get("guitar_handedness", "right"))
        self.guitar_handedness = "left" if loaded_handedness == "left" else "right"
        loaded_scale_play_mode = str(self.config_data.get("scale_play_mode", "piano"))
        self.scale_play_mode = "metronome" if loaded_scale_play_mode == "metronome" else "piano"
        self.instrument_view = "guitar" if loaded_instrument_view == "guitar" else "piano"
        self._set_instrument_view(self.instrument_view)
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
        self.config_icon_btn.configure(text="⚙")
        if not self.instrument_buttons_are_images:
            self.piano_view_btn.set_text(self.tr("instrument_piano"))
            self.guitar_view_btn.set_text(self.tr("instrument_guitar"))
        if not self.handedness_buttons_are_images:
            self.guitar_right_btn.set_text(self.tr("handed_right"))
            self.guitar_left_btn.set_text(self.tr("handed_left"))
        if not self.scale_transport_buttons_are_images:
            self.scale_mode_piano_btn.set_text(self.tr("instrument_piano"))
            self.scale_mode_metronome_btn.set_text(self.tr("scale_play_metronome"))
        self.scale_bpm_value_label.configure(text=f"{int(self.config_data.get('metronome_bpm', 120))} {self.tr('scale_bpm_short')}")
        self.mode_var.set(self._mode_label(self.current_mode))
        self.mode_trigger_var.set(self._mode_label(self.current_mode))
        self._refresh_scale_transport_styles()
        self._refresh_generation_controls()
        self._refresh_scale_preview()
        self._refresh_metronome_ui()
        if not self.active_notes:
            self.status_var.set(self.tr("status_no_notes"))

    def _instrument_display_notes(self) -> set[int]:
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

    def _set_instrument_view(self, view: str) -> None:
        self.instrument_view = "guitar" if view == "guitar" else "piano"
        self.config_data["instrument_view"] = self.instrument_view
        self.save_config()
        if self.instrument_view == "guitar":
            self.guitar_right_btn.grid()
            self.guitar_left_btn.grid()
            self.keyboard_canvas.pack_forget()
            self.guitar_canvas.pack(fill=tk.BOTH, expand=False)
            self.guitar_variations_frame.pack(fill=tk.X, pady=(6, 0))
        else:
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)
        self._refresh_instrument_toggle_styles()
        self._refresh_handedness_toggle_styles()
        self._refresh_guitar_variations()
        self.redraw_keyboard()
        self.redraw_guitar_fretboard()

    def _set_scale_play_mode(self, mode: str) -> None:
        self.scale_play_mode = "metronome" if mode == "metronome" else "piano"
        self.config_data["scale_play_mode"] = self.scale_play_mode
        self.save_config()
        self._refresh_scale_transport_styles()
        if self.scale_loop_active and self.scale_play_mode == "metronome" and self.scale_current_note is not None:
            # Cambio en caliente: mantener el loop, pero apagar la nota sostenida actual.
            self.audio_engine.note_off(self.scale_current_note)
            self.scale_playing_notes.discard(self.scale_current_note)

    def _draw_scale_bpm_step_button(self, canvas: tk.Canvas, symbol: str) -> None:
        canvas.delete("all")
        w = max(2, int(canvas.winfo_width()))
        h = max(2, int(canvas.winfo_height()))
        cx = w / 2
        cy = h / 2
        r = min(w, h) * 0.46
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#555d67", width=1.5, fill="#1f2127")
        canvas.create_text(cx, cy, text=symbol, fill="#dfe3e9", font=("Helvetica", 16, "bold"))

    def _draw_scale_bpm_slider(self) -> None:
        canvas = self.scale_bpm_slider
        canvas.delete("all")
        w = max(120, int(canvas.winfo_width()))
        h = max(24, int(canvas.winfo_height()))
        y = h / 2
        x1 = 12
        x2 = w - 12
        canvas.create_line(x1, y, x2, y, fill="#9aa6b2", width=4)
        ratio = (self.scale_bpm_value - self.scale_bpm_min) / max(1, (self.scale_bpm_max - self.scale_bpm_min))
        knob_x = x1 + ratio * (x2 - x1)
        r = 10
        canvas.create_oval(knob_x - r, y - r, knob_x + r, y + r, fill="#ff533d", outline="")

    def _set_scale_bpm(self, bpm: int, save: bool = True) -> None:
        self.scale_bpm_value = max(self.scale_bpm_min, min(self.scale_bpm_max, int(bpm)))
        self.config_data["metronome_bpm"] = self.scale_bpm_value
        self.metronome_bpm = self.scale_bpm_value
        self.scale_bpm_value_label.configure(text=f"{self.scale_bpm_value} {self.tr('scale_bpm_short')}")
        self._draw_scale_bpm_slider()
        if hasattr(self, "metronome_bpm_var"):
            self.metronome_bpm_var.set(f"{self.metronome_bpm} {self.tr('scale_bpm_short')}")
        if hasattr(self, "metronome_slider_canvas"):
            self._draw_metronome_bpm_slider()
        if save:
            self.save_config()

    def _on_scale_bpm_minus(self, _event: tk.Event) -> str:
        self._set_scale_bpm(self.scale_bpm_value - 1)
        return "break"

    def _on_scale_bpm_plus(self, _event: tk.Event) -> str:
        self._set_scale_bpm(self.scale_bpm_value + 1)
        return "break"

    def _on_scale_bpm_slider_interact(self, event: tk.Event) -> str:
        w = max(120, int(self.scale_bpm_slider.winfo_width()))
        x1 = 12
        x2 = w - 12
        x = min(max(float(event.x), x1), x2)
        ratio = (x - x1) / max(1.0, (x2 - x1))
        bpm = int(round(self.scale_bpm_min + ratio * (self.scale_bpm_max - self.scale_bpm_min)))
        self._set_scale_bpm(bpm)
        return "break"

    @staticmethod
    def _metronome_preset_text(bpm: int, language: str) -> str:
        # Rangos de tempo con nombres musicales tradicionales.
        labels_es = [
            (24, "Larguísimo"),
            (45, "Grave"),
            (60, "Largo"),
            (76, "Lento"),
            (108, "Andante"),
            (120, "Moderato"),
            (156, "Allegro"),
            (176, "Vivace"),
            (200, "Presto"),
            (999, "Prestísimo"),
        ]
        labels_en = [
            (24, "Larghissimo"),
            (45, "Grave"),
            (60, "Largo"),
            (76, "Lento"),
            (108, "Andante"),
            (120, "Moderato"),
            (156, "Allegro"),
            (176, "Vivace"),
            (200, "Presto"),
            (999, "Prestissimo"),
        ]
        table = labels_es if language == "es" else labels_en
        for limit, text in table:
            if bpm <= limit:
                return text
        return table[-1][1]

    def _refresh_metronome_ui(self) -> None:
        bpm = max(1, min(300, int(self.metronome_bpm)))
        self.metronome_bpm = bpm
        self.metronome_bpm_var.set(f"{bpm} {self.tr('scale_bpm_short')}")
        self.metronome_preset_var.set(self._metronome_preset_text(bpm, str(self.config_data.get("language", "es"))))
        self.metronome_meter_var.set(str(self.metronome_beats_per_bar))
        self.metronome_timer_enabled_var.set(self.metronome_timer_enabled)
        self.metronome_timer_minutes_var.set(str(self.metronome_timer_minutes))
        self.metronome_timer_seconds_var.set(str(self.metronome_timer_seconds))
        self.metronome_bar_accent_var.set(self.metronome_bar_accent_enabled)
        self.metronome_play_btn.configure(text="■" if self.metronome_running else "▶")
        self._draw_metronome_bpm_slider()
        self._draw_metronome_meter_slider()
        self._refresh_metronome_figure_buttons()
        timer_state = tk.NORMAL if self.metronome_timer_enabled else tk.DISABLED
        self.metronome_timer_minutes_spin.configure(state=timer_state)
        self.metronome_timer_seconds_spin.configure(state=timer_state)
        self.redraw_staff()

    def _on_metronome_timer_toggle(self) -> None:
        self.metronome_timer_enabled = bool(self.metronome_timer_enabled_var.get())
        self.config_data["metronome_timer_enabled"] = self.metronome_timer_enabled
        self.save_config()
        self._refresh_metronome_ui()

    def _on_metronome_timer_fields_changed(self, _event: Optional[tk.Event] = None) -> None:
        try:
            minutes = int(float(self.metronome_timer_minutes_var.get()))
        except (TypeError, ValueError):
            minutes = self.metronome_timer_minutes
        try:
            seconds = int(float(self.metronome_timer_seconds_var.get()))
        except (TypeError, ValueError):
            seconds = self.metronome_timer_seconds
        self.metronome_timer_minutes = max(0, min(99, minutes))
        self.metronome_timer_seconds = max(0, min(59, seconds))
        self.config_data["metronome_timer_minutes"] = self.metronome_timer_minutes
        self.config_data["metronome_timer_seconds"] = self.metronome_timer_seconds
        self.save_config()
        self._refresh_metronome_ui()

    def _on_metronome_bar_accent_toggle(self) -> None:
        self.metronome_bar_accent_enabled = bool(self.metronome_bar_accent_var.get())
        self.config_data["metronome_bar_accent_enabled"] = self.metronome_bar_accent_enabled
        self.save_config()
        self._refresh_metronome_ui()

    @staticmethod
    def _format_timer_mmss(total_seconds: float) -> str:
        total = max(0, int(total_seconds))
        mm = total // 60
        ss = total % 60
        return f"{mm:02d}:{ss:02d}"

    def _draw_circle_step_button(self, canvas: tk.Canvas, symbol: str) -> None:
        canvas.delete("all")
        w = max(2, int(canvas.winfo_width()))
        h = max(2, int(canvas.winfo_height()))
        cx = w / 2
        cy = h / 2
        r = min(w, h) * 0.46
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#555d67", width=1.5, fill="#1f2127")
        canvas.create_text(cx, cy, text=symbol, fill="#dfe3e9", font=("Helvetica", 16, "bold"))

    def _draw_metronome_bpm_slider(self) -> None:
        canvas = self.metronome_slider_canvas
        canvas.delete("all")
        w = max(120, int(canvas.winfo_width()))
        h = max(24, int(canvas.winfo_height()))
        y = h / 2
        x1 = 12
        x2 = w - 12
        canvas.create_line(x1, y, x2, y, fill="#9aa6b2", width=4)
        ratio = (self.metronome_bpm - self.scale_bpm_min) / max(1, (self.scale_bpm_max - self.scale_bpm_min))
        knob_x = x1 + ratio * (x2 - x1)
        r = 10
        canvas.create_oval(knob_x - r, y - r, knob_x + r, y + r, fill="#ff533d", outline="")

    def _draw_metronome_meter_slider(self) -> None:
        canvas = self.metronome_meter_canvas
        canvas.delete("all")
        w = max(120, int(canvas.winfo_width()))
        h = max(24, int(canvas.winfo_height()))
        y = h / 2
        x1 = 12
        x2 = w - 12
        canvas.create_line(x1, y, x2, y, fill="#9aa6b2", width=4)
        ratio = (self.metronome_beats_per_bar - 1) / 15.0
        knob_x = x1 + ratio * (x2 - x1)
        r = 10
        canvas.create_oval(knob_x - r, y - r, knob_x + r, y + r, fill="#ff533d", outline="")

    def _closest_metronome_figure_key(self, clicks: int) -> str:
        best = self.metronome_click_figure_defs[0]
        best_diff = abs(int(best["clicks"]) - clicks)
        for figure in self.metronome_click_figure_defs[1:]:
            diff = abs(int(figure["clicks"]) - clicks)
            if diff < best_diff:
                best = figure
                best_diff = diff
        return str(best["key"])

    def _draw_metronome_figure_button(self, key: str) -> None:
        btn = self.metronome_figure_buttons.get(key)
        if btn is None:
            return
        figure = next((f for f in self.metronome_click_figure_defs if str(f["key"]) == key), None)
        if figure is None:
            return
        btn.delete("all")
        w = max(30, int(btn.winfo_width()))
        h = max(24, int(btn.winfo_height()))
        selected = (self.metronome_click_figure_key == key)
        fill = "#ff533d" if selected else "#8896a3"
        outline = "#ff7b69" if selected else "#99a8b5"
        text_color = "#ffffff"
        btn.create_rectangle(4, 4, w - 4, h - 4, fill=fill, outline=outline, width=1.5)
        if bool(figure.get("triplet", False)):
            btn.create_text(w / 2, 16, text="3", fill=text_color, font=("Helvetica", 11, "bold"))
            btn.create_text(w / 2, h / 2 + 8, text=str(figure["glyph"]), fill=text_color, font=("Helvetica", 16, "bold"))
        else:
            btn.create_text(w / 2, h / 2 + 2, text=str(figure["glyph"]), fill=text_color, font=("Helvetica", 18, "bold"))

    def _refresh_metronome_figure_buttons(self) -> None:
        for figure in self.metronome_click_figure_defs:
            self._draw_metronome_figure_button(str(figure["key"]))

    def _select_metronome_click_figure(self, key: str) -> None:
        figure = next((f for f in self.metronome_click_figure_defs if str(f["key"]) == key), None)
        if figure is None:
            return
        self.metronome_click_figure_key = key
        self._set_metronome_clicks(int(figure["clicks"]))

    def _set_metronome_bpm(self, bpm: int) -> None:
        self.metronome_bpm = max(1, min(300, int(bpm)))
        self.config_data["metronome_bpm"] = self.metronome_bpm
        self.scale_bpm_value = self.metronome_bpm
        self.save_config()
        if hasattr(self, "scale_bpm_value_label"):
            self.scale_bpm_value_label.configure(text=f"{self.scale_bpm_value} {self.tr('scale_bpm_short')}")
        if hasattr(self, "scale_bpm_slider"):
            self._draw_scale_bpm_slider()
        self._refresh_metronome_ui()

    def _on_metronome_bpm_minus(self, _event: tk.Event) -> str:
        self._set_metronome_bpm(self.metronome_bpm - 1)
        return "break"

    def _on_metronome_bpm_plus(self, _event: tk.Event) -> str:
        self._set_metronome_bpm(self.metronome_bpm + 1)
        return "break"

    def _on_metronome_slider_interact(self, event: tk.Event) -> str:
        w = max(120, int(self.metronome_slider_canvas.winfo_width()))
        x1 = 12
        x2 = w - 12
        x = min(max(float(event.x), x1), x2)
        ratio = (x - x1) / max(1.0, (x2 - x1))
        bpm = int(round(self.scale_bpm_min + ratio * (self.scale_bpm_max - self.scale_bpm_min)))
        self._set_metronome_bpm(bpm)
        return "break"

    def _set_metronome_meter(self, value: int) -> None:
        self.metronome_beats_per_bar = max(1, min(16, int(value)))
        self.config_data["metronome_beats_per_bar"] = self.metronome_beats_per_bar
        self.save_config()
        if self.metronome_current_beat >= self.metronome_beats_per_bar:
            self.metronome_current_beat = 0
        self._refresh_metronome_ui()

    def _on_metronome_meter_minus(self, _event: tk.Event) -> str:
        self._set_metronome_meter(self.metronome_beats_per_bar - 1)
        return "break"

    def _on_metronome_meter_plus(self, _event: tk.Event) -> str:
        self._set_metronome_meter(self.metronome_beats_per_bar + 1)
        return "break"

    def _on_metronome_meter_slider_interact(self, event: tk.Event) -> str:
        w = max(120, int(self.metronome_meter_canvas.winfo_width()))
        x1 = 12
        x2 = w - 12
        x = min(max(float(event.x), x1), x2)
        ratio = (x - x1) / max(1.0, (x2 - x1))
        value = 1 + int(round(ratio * 15.0))
        self._set_metronome_meter(value)
        return "break"

    def _set_metronome_clicks(self, value: int) -> None:
        self.metronome_clicks_per_beat = max(1, min(16, int(value)))
        self.metronome_click_figure_key = self._closest_metronome_figure_key(self.metronome_clicks_per_beat)
        self.config_data["metronome_clicks_per_beat"] = self.metronome_clicks_per_beat
        self.save_config()
        self._refresh_metronome_ui()

    def _toggle_metronome(self) -> None:
        if not self.metronome_tab_active:
            return
        if self.metronome_running:
            self._stop_metronome()
        else:
            self._start_metronome()

    def _start_metronome(self) -> None:
        self._stop_metronome()
        self.metronome_running = True
        self.metronome_current_beat = 0
        self.metronome_current_subclick = 0
        self.metronome_tick_count = 0
        self.metronome_direction = 1
        now = time.monotonic()
        self.metronome_motion_start_ts = now
        self.metronome_timer_last_ts = now
        if self.metronome_timer_enabled:
            self.metronome_timer_remaining = max(0.0, float(self.metronome_timer_minutes * 60 + self.metronome_timer_seconds))
        else:
            self.metronome_timer_remaining = 0.0
        self._metronome_tick()
        self._metronome_anim_loop()
        self._refresh_metronome_ui()

    def _stop_metronome(self) -> None:
        self.metronome_running = False
        if self.metronome_after_id is not None:
            try:
                self.after_cancel(self.metronome_after_id)
            except Exception:
                pass
            self.metronome_after_id = None
        if self.metronome_anim_after_id is not None:
            try:
                self.after_cancel(self.metronome_anim_after_id)
            except Exception:
                pass
            self.metronome_anim_after_id = None
        self.metronome_current_subclick = 0
        self.metronome_tick_count = 0
        self.metronome_timer_last_ts = time.monotonic()
        if self.metronome_timer_enabled:
            self.metronome_timer_remaining = max(0.0, float(self.metronome_timer_minutes * 60 + self.metronome_timer_seconds))
        self._refresh_metronome_ui()

    def _metronome_step_ms(self) -> int:
        pulse_ms = 60000.0 / max(1, self.metronome_bpm)
        return max(10, int(round(pulse_ms / max(1, self.metronome_clicks_per_beat))))

    def _metronome_tick(self) -> None:
        if not self.metronome_running:
            return
        now = time.monotonic()
        if self.metronome_current_subclick == 0:
            if self.metronome_tick_count > 0:
                self.metronome_current_beat = (self.metronome_current_beat + 1) % max(1, self.metronome_beats_per_bar)
                self.metronome_direction *= -1
            self.metronome_motion_start_ts = now

        accent = self.metronome_current_subclick == 0
        bar_accent = accent and (self.metronome_current_beat == 0) and self.metronome_bar_accent_enabled
        self.audio_engine.metronome_click(accent=accent, bar=bar_accent)
        self.redraw_staff()

        self.metronome_current_subclick = (self.metronome_current_subclick + 1) % max(1, self.metronome_clicks_per_beat)
        self.metronome_tick_count += 1
        self.metronome_after_id = self.after(self._metronome_step_ms(), self._metronome_tick)

    def _metronome_anim_loop(self) -> None:
        if not self.metronome_running:
            return
        now = time.monotonic()
        if self.metronome_timer_enabled:
            elapsed = max(0.0, now - self.metronome_timer_last_ts)
            self.metronome_timer_remaining = max(0.0, self.metronome_timer_remaining - elapsed)
            if self.metronome_timer_remaining <= 0.0:
                self.metronome_timer_last_ts = now
                self._stop_metronome()
                return
        self.metronome_timer_last_ts = now
        if self.metronome_tab_active:
            self.redraw_staff()
        self.metronome_anim_after_id = self.after(16, self._metronome_anim_loop)

    def _set_guitar_handedness(self, handedness: str) -> None:
        self.guitar_handedness = "left" if handedness == "left" else "right"
        self.config_data["guitar_handedness"] = self.guitar_handedness
        self.save_config()
        self._refresh_handedness_toggle_styles()
        self.redraw_guitar_fretboard()

    def _refresh_instrument_toggle_styles(self) -> None:
        if self.instrument_buttons_are_images:
            panel_bg = self.cget("background")
            selected_hl = "#f39c12"
            normal_hl = panel_bg
            if self.instrument_view == "piano":
                self.piano_view_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=7,
                    pady=5,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
                self.guitar_view_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    padx=6,
                    pady=4,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                )
            else:
                self.piano_view_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    padx=6,
                    pady=4,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                )
                self.guitar_view_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=7,
                    pady=5,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
            return
        self.piano_view_btn.set_selected(self.instrument_view == "piano")
        self.guitar_view_btn.set_selected(self.instrument_view == "guitar")

    def _refresh_handedness_toggle_styles(self) -> None:
        if self.handedness_buttons_are_images:
            panel_bg = self.cget("background")
            selected_hl = "#f39c12"
            normal_hl = panel_bg
            if self.guitar_handedness == "right":
                self.guitar_right_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=9,
                    pady=7,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
                self.guitar_left_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    padx=8,
                    pady=6,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                )
            else:
                self.guitar_right_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    padx=8,
                    pady=6,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                )
                self.guitar_left_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=9,
                    pady=7,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
            return
        self.guitar_right_btn.set_selected(self.guitar_handedness == "right")
        self.guitar_left_btn.set_selected(self.guitar_handedness == "left")

    def _refresh_scale_transport_styles(self) -> None:
        if self.scale_transport_buttons_are_images:
            panel_bg = self.cget("background")
            selected_hl = "#f39c12"
            normal_hl = panel_bg
            if self.scale_play_mode == "piano":
                self.scale_mode_piano_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=7,
                    pady=5,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
                self.scale_mode_metronome_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                    padx=6,
                    pady=4,
                )
            else:
                self.scale_mode_piano_btn.configure(
                    bg=panel_bg,
                    relief=tk.FLAT,
                    bd=2,
                    highlightbackground=normal_hl,
                    highlightcolor=normal_hl,
                    highlightthickness=0,
                    padx=6,
                    pady=4,
                )
                self.scale_mode_metronome_btn.configure(
                    bg="#8a4f10",
                    relief=tk.SUNKEN,
                    bd=3,
                    padx=7,
                    pady=5,
                    highlightbackground=selected_hl,
                    highlightcolor=selected_hl,
                    highlightthickness=1,
                )
            return
        self.scale_mode_piano_btn.set_selected(self.scale_play_mode == "piano")
        self.scale_mode_metronome_btn.set_selected(self.scale_play_mode == "metronome")

    def _set_scale_transport_icon_pressed(self, mode: str, pressed: bool) -> None:
        if not self.scale_transport_buttons_are_images:
            return
        widget = self.scale_mode_piano_btn if mode == "piano" else self.scale_mode_metronome_btn
        if pressed:
            widget.configure(
                bg="#b86b14",
                relief=tk.SUNKEN,
                bd=4,
                padx=7,
                pady=5,
                highlightbackground="#f39c12",
                highlightcolor="#f39c12",
                highlightthickness=1,
            )
        else:
            widget.configure(padx=6, pady=4)
            self._refresh_scale_transport_styles()

    def _on_scale_transport_icon_press(self, _event: tk.Event, mode: str) -> None:
        self.scale_transport_pressed_mode = mode
        self._set_scale_transport_icon_pressed(mode, True)

    def _on_scale_transport_icon_release(self, _event: tk.Event, mode: str) -> None:
        self._set_scale_transport_icon_pressed(mode, False)
        self.scale_transport_pressed_mode = None
        self._set_scale_play_mode(mode)

    def _compute_guitar_variations(self, root_pc: int, pattern: ChordPattern) -> list[dict]:
        cached = get_cached_variations(self.guitar_chord_cache, root_pc, pattern.suffix)
        if cached:
            return cached

        tuning = [40, 45, 50, 55, 59, 64]  # E2 A2 D3 G3 B3 E4 (6->1)
        pcs = {(root_pc + interval) % 12 for interval in pattern.intervals}
        candidate_shapes: list[tuple[tuple[int, int, int, int, int, int, int], dict]] = []
        seen: set[tuple[int, ...]] = set()

        for start in range(0, 11):
            end = start + 4
            per_string_options: list[list[int]] = []
            for string_idx, open_note in enumerate(tuning):
                options = {-1}
                for fret in range(0, 16):
                    if (open_note + fret) % 12 not in pcs:
                        continue
                    if fret == 0:
                        if start == 0:
                            options.add(0)
                        continue
                    if start <= fret <= end:
                        options.add(fret)
                # Prefer not muting treble strings by default to keep complete voicings.
                ordered = sorted(options, key=lambda f: (0 if (f >= 0 and string_idx >= 2) else 1, f))
                per_string_options.append(ordered)

            stack: list[tuple[int, list[int]]] = [(0, [])]
            while stack:
                idx, current = stack.pop()
                if idx == 6:
                    frets = current
                    sounding = [(i, f) for i, f in enumerate(frets) if f >= 0]
                    if len(sounding) < 3:
                        continue
                    notes = [tuning[i] + f for i, f in sounding]
                    note_pcs = {n % 12 for n in notes}
                    if root_pc not in note_pcs:
                        continue
                    if len(note_pcs) < min(3, len(pcs)):
                        continue

                    fretted = [f for f in frets if f > 0]
                    open_count = sum(1 for f in frets if f == 0)
                    if fretted and (max(fretted) - min(fretted) > 4):
                        continue
                    # Closed-position shapes (e.g. barre chords) should not keep open strings.
                    if fretted and min(fretted) > 0 and open_count > 0:
                        continue

                    key = tuple(frets)
                    if key in seen:
                        continue
                    seen.add(key)

                    bass_pc = notes[0] % 12
                    mute_count = sum(1 for f in frets if f < 0)
                    span = (max(fretted) - min(fretted)) if fretted else 0
                    position = min(fretted) if fretted else 0
                    complexity = len({f for f in fretted})
                    # Logical order: open/low positions first, then compact and easy fingerings.
                    sort_key = (
                        0 if position == 0 else 1,
                        position,
                        0 if bass_pc == root_pc else 1,
                        mute_count,
                        open_count,
                        span,
                        complexity,
                        -len(note_pcs),
                    )
                    fingers = self._assign_guitar_fingers(frets)
                    string_notes = [(tuning[i] + frets[i]) if frets[i] >= 0 else None for i in range(6)]
                    candidate_shapes.append(
                        (
                            sort_key,
                            {
                                "frets": frets,
                                "notes": notes,
                                "fingers": fingers,
                                "string_notes": string_notes,
                            },
                        )
                    )
                    continue

                # Limit branching: keep at most first 6 options per string after ordering.
                for fret in reversed(per_string_options[idx][:6]):
                    stack.append((idx + 1, current + [fret]))

        candidate_shapes.sort(key=lambda item: item[0])

        by_position: set[int] = set()
        variations: list[dict] = []

        # First pass: prioritize one strong shape per position.
        for _key, entry in candidate_shapes:
            fretted = [f for f in entry["frets"] if f > 0]
            pos = min(fretted) if fretted else 0
            if pos in by_position:
                continue
            by_position.add(pos)
            variations.append(entry)

        # Second pass: append remaining shapes preserving the sorted order.
        chosen = {tuple(v["frets"]) for v in variations}
        for _key, entry in candidate_shapes:
            shape_key = tuple(entry["frets"])
            if shape_key in chosen:
                continue
            variations.append(entry)
            chosen.add(shape_key)

        if not variations:
            notes = [60 + root_pc + iv for iv in pattern.intervals]
            variations.append(
                {
                    "frets": [-1, -1, -1, -1, -1, -1],
                    "notes": notes,
                    "fingers": [0, 0, 0, 0, 0, 0],
                    "string_notes": [None, None, None, None, None, None],
                }
            )
        return variations

    @staticmethod
    def _assign_guitar_fingers(frets: list[int]) -> list[int]:
        pressed = sorted({f for f in frets if f > 0})
        if not pressed:
            return [0 for _ in frets]
        finger_map = {fret: min(4, idx + 1) for idx, fret in enumerate(pressed)}
        return [finger_map.get(fret, 0) if fret > 0 else 0 for fret in frets]

    def _resolve_guitar_chord_context(self) -> tuple[Optional[int], Optional[ChordPattern]]:
        if self.generation_tab_active:
            root = self.generation_root_pc
            pattern = self._resolve_generation_pattern()
            return root, pattern
        notes = self._current_detection_notes()
        if not notes:
            return None, None
        root, pattern, _bass = self._analyze_chord_notes(notes)
        return root, pattern

    def _refresh_guitar_variations(self) -> None:
        for btn in self.guitar_variation_buttons:
            btn.destroy()
        self.guitar_variation_buttons.clear()

        root, pattern = self._resolve_guitar_chord_context()
        if root is None or pattern is None:
            self.guitar_variations = []
            self.guitar_selected_variation_idx = None
            self.guitar_selected_variation_notes = set()
            self._last_guitar_chord_key = None
            return

        chord_key = (root, pattern.suffix)
        self.guitar_current_root_pc = root
        if chord_key != self._last_guitar_chord_key:
            self.guitar_variations = self._compute_guitar_variations(root, pattern)
            self.guitar_selected_variation_idx = 0 if self.guitar_variations else None
            self._last_guitar_chord_key = chord_key

        if self.guitar_selected_variation_idx is None:
            self.guitar_selected_variation_notes = set()
            return

        self.guitar_selected_variation_idx = max(0, min(self.guitar_selected_variation_idx, len(self.guitar_variations) - 1))
        self.guitar_selected_variation_notes = set(self.guitar_variations[self.guitar_selected_variation_idx]["notes"])

        for idx in range(len(self.guitar_variations)):
            selected = idx == self.guitar_selected_variation_idx
            btn = tk.Button(
                self.guitar_variations_inner,
                text=str(idx + 1),
                command=lambda i=idx: self._select_guitar_variation(i),
                width=3,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                bg="#ff9f1a" if selected else "#6a7283",
                fg="#000000",
                activebackground="#ffb347" if selected else "#7d879b",
                activeforeground="#000000",
                font=("Helvetica", 10, "bold"),
            )
            btn.pack(side=tk.LEFT, padx=(0 if idx == 0 else 4, 0), pady=4)
            self.guitar_variation_buttons.append(btn)

    def _select_guitar_variation(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.guitar_variations):
            return
        self.guitar_selected_variation_idx = idx
        self.guitar_selected_variation_notes = set(self.guitar_variations[idx]["notes"])
        self._refresh_guitar_variations()
        self.redraw_keyboard()
        self.redraw_staff()

    def redraw_guitar_fretboard(self) -> None:
        canvas = self.guitar_canvas
        canvas.delete("all")
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
                r = max(7, min(12, int(string_gap * 0.30)))
                fill = "#b35f00" if is_tonic else "#f4a742"
                text_color = "#ffffff" if is_tonic else "#1f1200"
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="#2e2e2e", width=1)
                canvas.create_text(x, y, text=str(finger), fill=text_color, font=("Helvetica", 9, "bold"))

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
            cx = fret_center_x(pos_fret)
            r = max(7, min(12, int(string_gap * 0.30)))
            fill = "#b35f00" if is_tonic else "#f4a742"
            text_color = "#ffffff" if is_tonic else "#1f1200"
            canvas.create_oval(cx - r, y - r, cx + r, y + r, fill=fill, outline="#f1c27d", width=1)
            if pos_fret > 0:
                canvas.create_text(cx, y, text=str(finger if finger > 0 else 1), fill=text_color, font=("Helvetica", 9, "bold"))

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

        if kind == "root":
            buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
            columns = 3
            options: list[tuple[str, int, bool]] = []
            for pc in range(12):
                options.append((self.note_name(pc, with_octave=False), pc, pc == self.generation_root_pc))
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            for idx, (label, value, selected) in enumerate(options):
                btn = GrayRoundedButton(
                    buttons_frame,
                    text=str(label),
                    command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                    width=122,
                    height=74,
                    radius=28,
                    font_size=22,
                )
                btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                btn.set_selected(bool(selected))
            return

        if kind == "variant":
            body = tk.Frame(overlay, bg="#2b2d38")
            body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))
            search_var, entry = self._build_rounded_search_entry(body, self.tr("label_search_variant"))

            buttons_frame = self._build_scrollable_area(body, bg="#2b2d38", padx=0, pady=(0, 0))
            columns = 3
            for col in range(columns):
                buttons_frame.columnconfigure(col, weight=1)

            def render_buttons() -> None:
                for w in buttons_frame.winfo_children():
                    w.destroy()
                term = search_var.get().strip().lower()
                options: list[tuple[str, str, bool]] = []
                for pattern in CHORD_PATTERNS:
                    label = pattern.suffix if pattern.suffix else "maj"
                    if term and term not in label.lower():
                        continue
                    options.append((label, pattern.suffix, pattern.suffix == self.generation_pattern_suffix))
                for idx, (label, value, selected) in enumerate(options):
                    btn = GrayRoundedButton(
                        buttons_frame,
                        text=str(label),
                        command=lambda v=value, k=kind: self._select_generation_overlay_value(k, v),
                        width=160,
                        height=64,
                        radius=24,
                        font_size=16,
                    )
                    btn.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=6, pady=6)
                    btn.set_selected(bool(selected))

            search_var.trace_add("write", lambda *_args: render_buttons())
            render_buttons()
            entry.focus_set()
            return

        # inversion
        buttons_frame = self._build_scrollable_area(overlay, bg="#2b2d38", padx=8, pady=(2, 10))
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
                    width=160,
                    height=64,
                    radius=24,
                    font_size=16,
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
        search_var, entry = self._build_rounded_search_entry(body, self.tr("label_search_scale"))

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

    def _finalize_generation_space_release(self) -> None:
        self.generation_space_release_after_id = None
        if self.generation_tab_active and self.generation_play_space_pressed:
            self._stop_generated_hold(source="space")

    def _finalize_scale_space_release(self) -> None:
        self.scale_space_release_after_id = None
        self.scale_space_pressed = False

    def _finalize_metronome_space_release(self) -> None:
        self.metronome_space_release_after_id = None
        self.metronome_space_pressed = False

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
        if mode_key == "metronome":
            return self.tr("mode_metronome")
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
            ("metronome", self._mode_label("metronome"), "⏱", "#ff8f40"),
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
        elif selected == self._mode_label("metronome"):
            self.current_mode = "metronome"
        else:
            self.current_mode = "detection"
        self.config_data["mode"] = self.current_mode
        self.save_config()
        self.mode_trigger_var.set(self._mode_label(self.current_mode))

        self.generation_tab_active = self.current_mode == "generation"
        self.scale_tab_active = self.current_mode == "scales"
        self.metronome_tab_active = self.current_mode == "metronome"
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
        self._stop_generated_playback()
        self._stop_scale_playback()
        self._stop_metronome()
        self.scale_space_pressed = False
        self.metronome_space_pressed = False

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
            self.tab_generation_frame.pack(fill=tk.BOTH, expand=True)
        elif self.scale_tab_active:
            self.instrument_canvas_holder.pack(fill=tk.BOTH, expand=False)
            self.instrument_switch_frame.pack_forget()
            self.scale_transport_frame.pack(fill=tk.X, pady=(0, 6), before=self.instrument_canvas_holder)
            self._refresh_scale_transport_styles()
            self.guitar_right_btn.grid_remove()
            self.guitar_left_btn.grid_remove()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)
            self._clear_live_input_state()
            self.tab_detection_frame.pack_forget()
            self.tab_metronome_frame.pack_forget()
            self.tab_generation_frame.pack_forget()
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
            self.tab_metronome_frame.pack(fill=tk.BOTH, expand=True)
            self._refresh_metronome_ui()
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
        if self.generation_tab_active:
            self.redraw_staff()

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
        if self.generation_tab_active:
            self.redraw_staff()

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
        bpm = max(1, min(300, bpm))
        return int(60000 / bpm)

    def _play_metronome_click(self, accent: bool) -> None:
        if self.scale_play_mode != "metronome":
            return
        self.audio_engine.metronome_click(accent=accent, bar=False)

    def _play_next_scale_step(self) -> None:
        if not self.scale_loop_active or not self.scale_preview_notes:
            return

        notes = self.scale_preview_notes
        idx = max(0, min(self.scale_loop_index, len(notes) - 1))
        note = notes[idx]
        play_piano = self.scale_play_mode == "piano"

        if self.scale_current_note is not None:
            if self.scale_current_note not in self.staff_pressed_scale_notes:
                self.audio_engine.note_off(self.scale_current_note)
            self.scale_playing_notes.discard(self.scale_current_note)
        self.scale_current_note = note
        if play_piano:
            self.audio_engine.note_on(note, 104)
            self.scale_playing_notes.add(note)
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

    def _start_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = True
        else:
            self.generation_play_space_pressed = True
        self.generation_play_btn.state(["pressed"])
        self._play_generated_chord()

    def _stop_generated_hold(self, source: str) -> None:
        if source == "button":
            self.generation_play_button_pressed = False
        else:
            self.generation_play_space_pressed = False
        if self.generation_play_button_pressed or self.generation_play_space_pressed:
            return
        self.generation_play_btn.state(["!pressed"])
        self._stop_generated_playback()

    def _on_generation_play_press(self, _event: tk.Event) -> str:
        self._start_generated_hold(source="button")
        return "break"

    def _toggle_scale_play(self) -> None:
        if not self.scale_tab_active:
            return
        if self.scale_loop_active:
            self._stop_scale_playback()
        else:
            self._play_scale()

    def _on_global_mouse_release(self, _event: tk.Event) -> None:
        if self.scale_transport_buttons_are_images and self.scale_transport_pressed_mode is not None:
            self._set_scale_transport_icon_pressed(self.scale_transport_pressed_mode, False)
            self.scale_transport_pressed_mode = None
        if self.generation_play_button_pressed:
            self._stop_generated_hold(source="button")

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

    def _load_instrument_icons(self) -> None:
        self.piano_image = None
        self.metronome_image = None
        self.guitar_image = None
        self.right_hand_icon_image = None
        self.left_hand_icon_image = None

        for path in PIANO_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = tk.PhotoImage(file=str(path))
                self.piano_image = self._fit_photo_image(img, max_w=86, max_h=34)
                break
            except Exception:
                continue

        for path in METRONOME_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = tk.PhotoImage(file=str(path))
                fitted = self._fit_photo_image(img, max_w=86, max_h=34)
                self._prepare_icon_for_dark_ui(fitted, bg=(43, 47, 55), fg=(246, 246, 246))
                self.metronome_image = fitted
                break
            except Exception:
                continue

        for path in GUITAR_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = tk.PhotoImage(file=str(path))
                fitted = self._fit_photo_image(img, max_w=86, max_h=34)
                self._recolor_dark_pixels(fitted, threshold=56, target=(255, 255, 255))
                self.guitar_image = fitted
                break
            except Exception:
                continue

        for path in RIGHT_HAND_ICON_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = tk.PhotoImage(file=str(path))
                fitted = self._fit_photo_image(img, max_w=44, max_h=22)
                self.right_hand_icon_image = self._pad_photo_image(fitted, pad_x=6, pad_y=4)
                break
            except Exception:
                continue

        for path in LEFT_HAND_ICON_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = tk.PhotoImage(file=str(path))
                fitted = self._fit_photo_image(img, max_w=44, max_h=22)
                self.left_hand_icon_image = self._pad_photo_image(fitted, pad_x=6, pad_y=4)
                break
            except Exception:
                continue

    @staticmethod
    def _fit_photo_image(image: tk.PhotoImage, max_w: int, max_h: int) -> tk.PhotoImage:
        w = image.width()
        h = image.height()
        if w <= 0 or h <= 0:
            return image
        if w <= max_w and h <= max_h:
            return image

        best_zoom = 1
        best_sub = 1
        best_diff = float("inf")

        for zoom in range(1, 5):
            for sub in range(1, 20):
                nw = max(1, (w * zoom) // sub)
                nh = max(1, (h * zoom) // sub)
                if nw > max_w or nh > max_h:
                    continue
                diff = (max_w - nw) + (max_h - nh)
                if diff < best_diff:
                    best_diff = diff
                    best_zoom = zoom
                    best_sub = sub

        if best_zoom == 1 and best_sub == 1:
            return image.subsample(max(1, (w + max_w - 1) // max_w), max(1, (h + max_h - 1) // max_h))

        fitted = image.zoom(best_zoom, best_zoom)
        if best_sub > 1:
            fitted = fitted.subsample(best_sub, best_sub)
        return fitted

    @staticmethod
    def _pad_photo_image(image: tk.PhotoImage, pad_x: int = 4, pad_y: int = 4) -> tk.PhotoImage:
        w = image.width()
        h = image.height()
        out = tk.PhotoImage(width=w + pad_x * 2, height=h + pad_y * 2)
        out.tk.call(str(out), "copy", str(image), "-to", pad_x, pad_y)
        return out

    @staticmethod
    def _recolor_dark_pixels(image: tk.PhotoImage, threshold: int = 56, target: tuple[int, int, int] = (255, 255, 255)) -> None:
        target_hex = f"#{target[0]:02x}{target[1]:02x}{target[2]:02x}"
        w = image.width()
        h = image.height()
        dark_map = [[False for _ in range(w)] for _ in range(h)]
        rgb_map: list[list[tuple[int, int, int] | None]] = [[None for _ in range(w)] for _ in range(h)]

        for y in range(h):
            for x in range(w):
                rgb = image.get(x, y)
                if isinstance(rgb, tuple) and len(rgb) >= 3:
                    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                elif isinstance(rgb, str) and rgb.startswith("#") and len(rgb) == 7:
                    r = int(rgb[1:3], 16)
                    g = int(rgb[3:5], 16)
                    b = int(rgb[5:7], 16)
                else:
                    continue
                rgb_map[y][x] = (r, g, b)
                dark_map[y][x] = r <= threshold and g <= threshold and b <= threshold

        for y in range(h):
            for x in range(w):
                if not dark_map[y][x]:
                    continue
                # Recolor only edge dark pixels (likely strokes), not full dark backgrounds.
                has_light_neighbor = False
                for ny in range(max(0, y - 1), min(h, y + 2)):
                    for nx in range(max(0, x - 1), min(w, x + 2)):
                        if nx == x and ny == y:
                            continue
                        if not dark_map[ny][nx]:
                            has_light_neighbor = True
                            break
                    if has_light_neighbor:
                        break
                if has_light_neighbor:
                    image.put(target_hex, (x, y))

    @staticmethod
    def _prepare_icon_for_dark_ui(
        image: tk.PhotoImage,
        bg: tuple[int, int, int] = (43, 47, 55),
        fg: tuple[int, int, int] = (246, 246, 246),
        light_threshold: int = 232,
    ) -> None:
        bg_hex = f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
        fg_hex = f"#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"
        w = image.width()
        h = image.height()
        for y in range(h):
            for x in range(w):
                rgb = image.get(x, y)
                if isinstance(rgb, tuple) and len(rgb) >= 3:
                    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                elif isinstance(rgb, str) and rgb.startswith("#") and len(rgb) == 7:
                    r = int(rgb[1:3], 16)
                    g = int(rgb[3:5], 16)
                    b = int(rgb[5:7], 16)
                else:
                    continue
                if r >= light_threshold and g >= light_threshold and b >= light_threshold:
                    image.put(bg_hex, (x, y))
                else:
                    image.put(fg_hex, (x, y))

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
        self._refresh_guitar_variations()
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
        elif self.metronome_tab_active:
            self.chord_var.set("-")
        else:
            self.chord_var.set(self.detect_chord(active_set))
        self.redraw_keyboard()
        self.redraw_staff()

    def redraw_keyboard(self) -> None:
        if self.instrument_view == "guitar":
            self.redraw_guitar_fretboard()
            return
        canvas = self.keyboard_canvas
        canvas.delete("all")
        self.white_key_regions = []
        self.black_key_regions = []
        display_active_notes = self._instrument_display_notes()
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
            elif self.scale_tab_active and (note % 12) in scale_pc_set:
                top_fill = "#eefaff"
                base_fill = "#d8f1ff"
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
            elif self.scale_tab_active and (note % 12) in scale_pc_set:
                top = "#6d97ab"
                mid = "#4b6977"
                low = "#304851"
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

    def _draw_metronome_panel(self, canvas: tk.Canvas) -> None:
        w = max(300, canvas.winfo_width())
        h = max(220, canvas.winfo_height())
        canvas.create_rectangle(0, 0, w, h, fill="#000000", outline="")
        beats = max(1, self.metronome_beats_per_bar)
        left = 80.0
        right = w - 80.0
        if right <= left:
            right = left + 1.0
        y_top = max(54.0, h * 0.33)
        y_bot = min(h - 56.0, y_top + 84.0)
        if beats == 1:
            xs = [(left + right) * 0.5]
            spacing = (right - left)
        else:
            step = (right - left) / (beats - 1)
            xs = [left + i * step for i in range(beats)]
            spacing = step

        # Eje de desplazamiento del punto rojo con divisiones por click.
        axis_y = y_bot + 18.0
        canvas.create_line(left, axis_y, right, axis_y, fill="#8f98a3", width=3)
        clicks = max(1, self.metronome_clicks_per_beat)
        # Divisiones del eje solo por clicks por pulso (independiente de pulsos por compas).
        for k in range(clicks + 1):
            x_tick = left + (right - left) * (k / clicks)
            is_end = k in {0, clicks}
            tick_h = 18 if is_end else 13
            tick_w = 2.8 if is_end else 2.0
            tick_color = "#9aa6b2" if is_end else "#747f8d"
            canvas.create_line(x_tick, axis_y - tick_h / 2, x_tick, axis_y + tick_h / 2, fill=tick_color, width=tick_w)

        current = self.metronome_current_beat % beats
        # Radio adaptativo: mayor con pocos pulsos, menor con muchos (sin solape).
        base_r = max(7.0, min(24.0, 30.0 - (beats * 0.75)))
        max_r_by_spacing = max(6.0, (spacing * 0.42) - 2.0)
        normal_r = min(base_r, max_r_by_spacing)
        active_r = min(normal_r + 2.0, max_r_by_spacing + 1.5)
        for idx, x in enumerate(xs):
            active = self.metronome_running and idx == current
            fill = "#ffd24a" if active else "#c8a832"
            outline = "#f3da7a" if active else "#9f8427"
            r = active_r if active else normal_r
            canvas.create_oval(x - r, y_top - r, x + r, y_top + r, fill=fill, outline=outline, width=2)
            canvas.create_text(
                x,
                y_top,
                text=str(idx + 1),
                fill="#1a1a1a",
                font=("Helvetica", max(8, min(12, int(normal_r * 0.82))), "bold"),
            )

        red_x = xs[0]
        if self.metronome_running:
            pulse_seconds = 60.0 / max(1, self.metronome_bpm)
            elapsed = max(0.0, time.monotonic() - self.metronome_motion_start_ts)
            t = min(1.0, elapsed / max(0.001, pulse_seconds))
            if self.metronome_direction > 0:
                red_x = left + (right - left) * t
            else:
                red_x = right - (right - left) * t
        red_r = 12
        red_y = axis_y
        canvas.create_oval(
            red_x - red_r,
            red_y - red_r,
            red_x + red_r,
            red_y + red_r,
            fill="#ff4333",
            outline="#ff8d81",
            width=2,
        )
        if self.metronome_timer_enabled:
            timer_text = self._format_timer_mmss(self.metronome_timer_remaining)
            timer_y = axis_y + ((h - axis_y) * 0.5)
            canvas.create_text(
                w / 2,
                timer_y,
                text=timer_text,
                fill="#ffb17a",
                font=("Helvetica", 56, "bold"),
            )

    def redraw_staff(self) -> None:
        canvas = self.staff_canvas
        canvas.delete("all")
        self.staff_scale_note_regions = []
        if self.metronome_tab_active:
            self._draw_metronome_panel(canvas)
            return
        instrument_override = self.instrument_view == "guitar" and bool(self.guitar_selected_variation_notes)
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
                for ledger_y in ledger_lines_y:
                    canvas.create_line(x - ledger_half, ledger_y, x + ledger_half, ledger_y, fill="#bfbfbf", width=1)
                if self.scale_tab_active:
                    label_text = self.note_name(note, with_octave=False)
                    label_y = label_y_base
                    is_label_hl = (self.staff_hover_note == note) or (note in self.staff_pressed_scale_notes)
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
                        font=("Helvetica", 11, "bold" if (is_label_hl or is_current_label) else "normal"),
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

        ttk.Label(frame, text=self.tr("settings_guitar_handedness")).grid(row=5, column=0, sticky="w", pady=4)
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
        handed_combo.grid(row=5, column=1, sticky="w", pady=4)

        def do_save(_event: Optional[tk.Event] = None) -> str:
            self.config_data["language"] = lang_label_to_id.get(lang_var.get(), "es")
            self.config_data["midi_input"] = in_var.get().strip()
            self.config_data["audio_output"] = out_var.get().strip()
            self.config_data["sound_preset"] = sound_label_to_id.get(sound_var.get(), "acoustic")
            self.config_data["show_keyboard_note_labels"] = bool(show_labels_var.get())
            self.config_data["guitar_handedness"] = handed_label_to_id.get(handed_var.get(), "right")
            self.guitar_handedness = "left" if self.config_data["guitar_handedness"] == "left" else "right"
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
        buttons.grid(row=6, column=0, columnspan=2, sticky="e")

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
        self._stop_generated_playback()
        self._stop_scale_playback()
        self._stop_metronome()
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
