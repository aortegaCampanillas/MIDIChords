from __future__ import annotations

import json
import math
import os
import queue
import subprocess
import sys
import threading
import time
from typing import Optional

import mido
import numpy as np
import sounddevice as sd

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from midichords.qt import QtSchedulerMixin, QtStringVar
import midichords.qt.tk_compat as tk

from midichords.core.audio_engine import PianoAudioEngine
from midichords.core.app_config import load_config_file, save_config_file
from midichords.core.app_constants import (
    APP_LOGO_CANDIDATES,
    BASS_CLEF_IMAGE_CANDIDATES,
    BRACE_IMAGE_CANDIDATES,
    CLEF_FONT_FAMILIES,
    CONFIG_PATH,
    DEFAULT_CONFIG,
    GUITAR_IMAGE_CANDIDATES,
    LEFT_HAND_ICON_CANDIDATES,
    METRONOME_IMAGE_CANDIDATES,
    PIANO_IMAGE_CANDIDATES,
    RIGHT_HAND_ICON_CANDIDATES,
    TREBLE_CLEF_IMAGE_CANDIDATES,
)
from midichords.core.guitar_chord_cache import get_cached_variations, load_guitar_chord_cache
from midichords.core.image_utils import fit_photo_image, pad_photo_image, prepare_icon_for_dark_ui, recolor_dark_pixels
from midichords.core.i18n import SCALE_NAME_TEXTS, UI_TEXTS
from midichords.core.music_theory import CHORD_PATTERNS, SCALE_PATTERNS, WHITE_PCS, ChordPattern
from midichords.core.verbose_log import is_verbose, vlog
from midichords.ui.widgets_qt import GrayRoundedButton, GreenRoundedButton, RoundedChoiceButton
from midichords.mixins.tuner_mixin import TunerMixin
from midichords.mixins.metronome_mixin import MetronomeMixin
from midichords.mixins.scales_mixin import ScalesMixin
from midichords.mixins.generation_mixin import GenerationMixin
from midichords.mixins.circle_fifths_mixin import CircleFifthsMixin
from midichords.mixins.midi_io_mixin import MidiIOMixin
from midichords.mixins.input_detection_mixin import InputDetectionMixin
from midichords.mixins.ui_mixin import UiMixin
from midichords.mixins.render_mixin import RenderMixin
from midichords.mixins.overlays_mixin import OverlaysMixin
from midichords.mixins.changelog_mixin import ChangelogMixin

class MidiChordAnalyzerApp(
    UiMixin,
    RenderMixin,
    OverlaysMixin,
    TunerMixin,
    MetronomeMixin,
    ScalesMixin,
    GenerationMixin,
    CircleFifthsMixin,
    MidiIOMixin,
    InputDetectionMixin,
    ChangelogMixin,
    QtSchedulerMixin,
    QMainWindow,
):
    def __init__(self) -> None:
        super().__init__()
        self.setGeometry(0, 0, 1300, 800)
        self.setMinimumSize(980, 620)

        self.config_data = dict(DEFAULT_CONFIG)
        self.load_config()
        self.brace_base_image: Optional[QPixmap] = None
        self.brace_image_cache: dict[tuple[int, int], QPixmap] = {}
        self.app_logo_image: Optional[QPixmap] = None
        self.piano_image: Optional[QPixmap] = None
        self.metronome_image: Optional[QPixmap] = None
        self.guitar_image: Optional[QPixmap] = None
        self.right_hand_icon_image: Optional[QPixmap] = None
        self.left_hand_icon_image: Optional[QPixmap] = None
        self.treble_clef_image: Optional[QPixmap] = None
        self.bass_clef_image: Optional[QPixmap] = None
        self._clef_font_family: str = "serif"
        self.instrument_buttons_are_images = False
        self.scale_transport_buttons_are_images = False
        self.handedness_buttons_are_images = False
        self._load_brace_image()
        self._load_app_logo()
        # MacOS muestra el icono genérico de Python si no se define el icono de
        # la ventana desde Qt. Aplicamos el logo como window icon.
        if self.app_logo_image is not None and not self.app_logo_image.isNull():
            try:
                # Cmd-Tab en macOS a veces usa el icono de QApplication,
                # por eso lo propagamos también.
                base = self.app_logo_image
                sizes = [16, 32, 64, 128, 256]
                icon = QIcon()
                for s in sizes:
                    try:
                        pm = base.scaled(s, s, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    except Exception:
                        pm = base
                    icon.addPixmap(pm)

                self.setWindowIcon(icon)
                qa = QApplication.instance()
                if qa is not None:
                    qa.setWindowIcon(icon)
            except Exception:
                pass
        self._load_instrument_icons()
        self._load_clef_images()
        self._resolve_clef_font()

        self.active_notes: set[int] = set()
        self.generated_preview_notes: set[int] = set()
        self.detection_extra_notes: set[int] = set()
        self.detection_overlay_note_names: dict[int, str] = {}
        self.midi_held_notes: set[int] = set()
        self.mouse_held_notes: set[int] = set()
        self.sustain_latched_notes: set[int] = set()
        self.note_velocity: dict[int, int] = {}
        self.pedal_active = False
        self.mouse_current_note: Optional[int] = None
        self.sounding_notes: set[int] = set()
        self.midi_latched_notes: set[int] = set()
        self.generated_playing_notes: set[int] = set()
        self.generated_note_highlight_after: dict[int, str] = {}
        self.generated_play_after_id: Optional[str] = None
        self.generation_play_button_pressed = False
        self._preview_chord_after_id: Optional[str] = None
        self.generation_play_space_pressed = False
        self.detection_play_button_pressed = False
        self.generation_space_release_after_id: Optional[str] = None
        self.white_key_regions: list[tuple[int, float, float, float, float]] = []
        self.black_key_regions: list[tuple[int, float, float, float, float]] = []
        self.message_queue: queue.Queue = queue.Queue()
        self.blocked_note_until: dict[int, float] = {}

        self.input_port: Optional[mido.ports.BaseInput] = None
        self.midi_bridge_proc: Optional[subprocess.Popen] = None
        self.midi_bridge_thread: Optional[threading.Thread] = None
        self.midi_bridge_connected = False

        # MIDI Output support
        self.midi_output_port: Optional[mido.ports.BaseOutput] = None
        self.sound_output: str = str(self.config_data.get("sound_output", "audio"))  # "audio" o "midi"

        self.input_names: list[str] = []
        self.audio_input_names: list[str] = []
        self.audio_input_map: dict[str, int] = {}
        self.audio_output_names: list[str] = []
        self.audio_output_map: dict[str, int] = {}
        self.midi_backend_available = True
        self.midi_backend_warning = ""
        self.audio_engine = PianoAudioEngine()
        self.audio_engine.set_preset(str(self.config_data.get("sound_preset", "acoustic")))
        self.audio_engine.set_guitar_preset(str(self.config_data.get("guitar_sound_preset", "steel_clean")))
        self.tuner_enabled = str(os.getenv("MIDICHORDS_ENABLE_TUNER_DESKTOP", "0")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.current_mode = str(self.config_data.get("mode", "detection"))
        allowed_modes = {"detection", "generation", "circle_fifths", "scales", "metronome"}
        if self.tuner_enabled:
            allowed_modes.add("tuner")
        if self.current_mode not in allowed_modes:
            self.current_mode = "detection"
        self.generation_tab_active = False
        self.scale_tab_active = False
        self.metronome_tab_active = False
        self.tuner_tab_active = False
        self.mode_var = QtStringVar()
        loaded_note_accidental = str(self.config_data.get("note_accidental", "sharp")).lower()
        self.note_accidental = "flat" if loaded_note_accidental == "flat" else "sharp"
        self.midi_input_sound_enabled = bool(self.config_data.get("midi_input_sound_enabled", True))
        self.generation_root_pc = 0
        self.generation_pattern_suffix = ""
        self.generation_inversion = 0
        self.circle_tonic_pc = 0
        self.circle_key_mode = "major"
        self.circle_chord_root_pc = 0
        self.circle_fifths_tab_active = False
        self._circle_generated_chord = None
        self.scale_tonic_pc = 0
        self.scale_pattern_name = SCALE_PATTERNS[0].name
        self.scale_preview_notes: list[int] = []
        self.scale_guitar_start_note: Optional[int] = None
        self.scale_playing_notes: set[int] = set()
        self.scale_loop_active = False
        self.scale_loop_after_id: Optional[str] = None
        self.scale_loop_index = 0
        self.scale_loop_direction = 1
        self.scale_current_note: Optional[int] = None
        self.scale_input_raw_note: Optional[int] = None
        self.scale_space_pressed = False
        self.scale_space_release_after_id: Optional[str] = None
        self.metronome_space_pressed = False
        self.metronome_space_release_after_id: Optional[str] = None
        self.tuner_space_pressed = False
        self.tuner_space_release_after_id: Optional[str] = None
        self.staff_hover_note: Optional[int] = None
        self.staff_hover_scale_degree: Optional[int] = None
        self.staff_pressed_scale_notes: set[int] = set()
        self.staff_pressed_scale_degrees: set[int] = set()
        self.staff_scale_note_regions: list[tuple[int, float, float, float, float, float, float, int]] = []
        self.staff_generation_note_regions: list[tuple[int, float, float, float, float]] = []
        self.scale_tonic_overlay: Optional[QWidget] = None
        self.scale_type_overlay: Optional[QWidget] = None
        self.generation_selection_overlay: Optional[QWidget] = None
        self.settings_overlay: Optional[QWidget] = None
        self._settings_overlay_opened_ts: float = 0.0
        self.mode_selector_overlay: Optional[QWidget] = None
        self.instrument_view = "piano"
        self.scale_play_mode = "piano"
        self.scale_metronome_only = False
        self.scale_bpm_min = 1
        self.scale_bpm_max = 300
        self.scale_bpm_value = int(self.config_data.get("metronome_bpm", 120))
        self.scale_transport_pressed_mode: Optional[str] = None
        self.guitar_handedness = "right"
        self.guitar_variations: list[dict] = []
        self.guitar_variations_all: list[dict] = []
        self.guitar_selected_variation_idx: Optional[int] = None
        self.guitar_selected_variation_notes: set[int] = set()
        self.guitar_variation_buttons: list[tk.Button] = []
        self._last_guitar_chord_key: Optional[tuple[int, str]] = None
        self.guitar_current_root_pc: Optional[int] = None
        self.scale_guitar_tonic_regions: list[tuple[int, float, float, float, float]] = []
        self.scale_guitar_note_regions: list[tuple[int, float, float, float, float]] = []
        self.scale_guitar_click_highlight_exact_notes: set[int] = set()
        self.scale_guitar_click_highlight_pcs: set[int] = set()
        self.scale_guitar_click_highlight_notes: set[int] = set()
        self.scale_guitar_drag_active = False
        self.scale_guitar_drag_moved = False
        self.scale_guitar_drag_exact_notes: set[int] = set()
        self.scale_guitar_drag_staff_notes: set[int] = set()
        self.scale_staff_drag_active = False
        self.guitar_generation_note_regions: list[tuple[int, float, float, float, float]] = []
        self.generation_guitar_drag_active = False
        self.generation_staff_drag_active = False
        self.generation_piano_staff_drag_active = False
        self.generation_drag_notes: set[int] = set()
        self.generation_drag_moved = False
        self.generation_midi_held_notes: set[int] = set()  # MIDI notes held in chord generation mode
        self._settings_save_callback = None
        self.detect_hold_notes: set[int] = set()
        self.detect_hold_active = False
        self.detection_mouse_chord_notes: set[int] = set()
        self.detection_midi_held_notes: set[int] = set()
        self.detection_last_playable_notes: set[int] = set()
        self.detection_shift_pressed = False
        self._scroll_targets: list[tuple[tk.Widget, tk.Canvas]] = []
        self.guitar_chord_cache = load_guitar_chord_cache()
        self.metronome_bpm = max(1, min(300, int(self.config_data.get("metronome_bpm", 120))))
        self.metronome_volume = max(0, min(100, int(self.config_data.get("metronome_volume", 100))))
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
        self.tuner_tuning_defs = [
            {"key": "standard_e", "es": "Estándar", "en": "Standard", "notes": [40, 45, 50, 55, 59, 64]},
            {"key": "drop_d", "es": "Drop D", "en": "Drop D", "notes": [38, 45, 50, 55, 59, 64]},
            {"key": "drop_c", "es": "Drop C", "en": "Drop C", "notes": [36, 43, 48, 53, 57, 62]},
            {"key": "half_step_down", "es": "1/2 tono abajo", "en": "Half-step down", "notes": [39, 44, 49, 54, 58, 63]},
            {"key": "whole_step_down", "es": "1 tono abajo", "en": "Whole-step down", "notes": [38, 43, 48, 53, 57, 62]},
            {"key": "open_g", "es": "Open G", "en": "Open G", "notes": [38, 43, 50, 55, 59, 62]},
            {"key": "open_d", "es": "Open D", "en": "Open D", "notes": [38, 45, 50, 54, 57, 62]},
            {"key": "dadgad", "es": "DADGAD", "en": "DADGAD", "notes": [38, 45, 50, 55, 57, 62]},
        ]
        loaded_tuning = str(self.config_data.get("tuner_tuning", "standard_e"))
        if loaded_tuning not in {str(t["key"]) for t in self.tuner_tuning_defs}:
            loaded_tuning = "standard_e"
        self.tuner_tuning_key = loaded_tuning
        self.tuner_input_name = str(self.config_data.get("tuner_input", ""))
        self.tuner_input_gain = max(0, min(200, int(self.config_data.get("tuner_input_gain", 100))))
        self.tuner_spectrum_min_hz = max(0, min(3000, int(self.config_data.get("tuner_spectrum_min_hz", 0))))
        self.tuner_spectrum_max_hz = max(1, min(3000, int(self.config_data.get("tuner_spectrum_max_hz", 500))))
        if self.tuner_spectrum_max_hz <= self.tuner_spectrum_min_hz + 10:
            self.tuner_spectrum_max_hz = min(3000, self.tuner_spectrum_min_hz + 200)
        self.tuner_spectrum_dragging: Optional[str] = None
        self.tuner_running = False
        self.tuner_stream: Optional[sd.InputStream] = None
        self.tuner_audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self.tuner_audio_buffer = np.zeros(0, dtype=np.float32)
        self.tuner_last_analysis_ts = 0.0
        self.tuner_current_string_idx: Optional[int] = None
        self.tuner_current_cents = 0.0
        self.tuner_current_freq = 0.0
        self.tuner_detected_note_midi: Optional[int] = None
        self.tuner_last_candidate_midi: Optional[int] = None
        self.tuner_note_stable_count = 0
        self.tuner_silence_frames = 0
        self.tuner_string_buttons: list[tk.Button] = []
        self.tuner_button_active_until: dict[int, float] = {}
        self.tuner_reference_note: Optional[int] = None
        self.tuner_reference_off_after_id: Optional[str] = None
        self.tuner_tuning_overlay: Optional[tk.Frame] = None
        self.tuner_string_regions: list[tuple[int, float, float, float, float]] = []
        self.tuner_spectrum_freqs = np.zeros(0, dtype=np.float32)
        self.tuner_spectrum_mags = np.zeros(0, dtype=np.float32)
        self.tuner_pitch_detector = None
        self.tuner_pitch_hop = 256

        self._build_ui()
        _qa = QApplication.instance()
        if _qa is not None:
            _qa.installEventFilter(self)
        loaded_instrument_view = str(
            self.config_data.get(
                "generation_instrument_view",
                self.config_data.get("instrument_view", "piano"),
            )
        )
        loaded_handedness = str(self.config_data.get("guitar_handedness", "right"))
        self.guitar_handedness = "left" if loaded_handedness == "left" else "right"
        loaded_scale_play_mode = str(self.config_data.get("scale_play_mode", "piano"))
        if loaded_scale_play_mode in {"piano", "guitar"}:
            self.scale_play_mode = loaded_scale_play_mode
        elif loaded_scale_play_mode == "metronome":
            loaded_scale_instrument_mode = str(self.config_data.get("scale_instrument_mode", "piano"))
            self.scale_play_mode = "guitar" if loaded_scale_instrument_mode == "guitar" else "piano"
        else:
            self.scale_play_mode = "piano"
        self.scale_metronome_only = bool(
            self.config_data.get("scale_metronome_only", loaded_scale_play_mode == "metronome")
        )
        self.instrument_view = "guitar" if loaded_instrument_view == "guitar" else "piano"
        self._set_instrument_view(self.instrument_view)
        self.apply_ui_language()
        self._on_mode_combo_changed(None)
        self._startup_after_id: Optional[str] = self.after(0, self._complete_startup)

    def tr(self, key: str) -> str:
        language = self.config_data.get("language", "es")
        return UI_TEXTS.get(language, UI_TEXTS["en"]).get(key, key)

    def _complete_startup(self) -> None:
        self._startup_after_id = None
        self.refresh_devices()
        self.connect_ports()
        # Precalentar el OutputStream para que la primera tecla no bloquee la UI.
        try:
            threading.Thread(
                target=self.audio_engine.ensure_started,
                daemon=True,
            ).start()
        except Exception:
            pass
        self.after(20, self._process_midi_queue)

    def scale_name(self, canonical_name: str) -> str:
        language = self.config_data.get("language", "es")
        return SCALE_NAME_TEXTS.get(language, SCALE_NAME_TEXTS["en"]).get(canonical_name, canonical_name)




































    # Audio/MIDI output wrapper methods
    def play_note(self, midi_note: int, velocity: int = 80) -> bool:
        """Play a note via audio engine or MIDI output based on sound_output setting."""
        if self.sound_output == "midi" and self.midi_output_port is not None:
            self.send_midi_note_on(self.midi_output_port, midi_note, velocity)
            return True
        else:
            return self.audio_engine.note_on(midi_note, velocity)

    def stop_note(self, midi_note: int) -> None:
        """Stop a note via audio engine or MIDI output based on sound_output setting."""
        if self.sound_output == "midi" and self.midi_output_port is not None:
            self.send_midi_note_off(self.midi_output_port, midi_note)
        else:
            self.audio_engine.note_off(midi_note)

    def _set_instrument_view(self, view: str) -> None:
        self.instrument_view = "guitar" if view == "guitar" else "piano"
        self.config_data["instrument_view"] = self.instrument_view
        self.config_data["generation_instrument_view"] = self.instrument_view
        self.save_config()
        # Instrument controls now live in the top-right toolbar.
        # Keep this legacy spacer frame hidden to avoid vertical gaps.
        self.instrument_switch_frame.pack_forget()
        if self.instrument_view == "guitar":
            self.guitar_handedness_combo.pack_forget()
            self.guitar_handedness_combo.pack(side=tk.TOP, pady=(8, 0), fill=tk.X)
            self.keyboard_qscroll.pack_forget()
            # En Qt, `expand=False` + sizeHint pequeño puede dejar el canvas
            # sin estirarse (se ve como si ocupara solo la mitad).
            # Fijamos altura para conservar proporciones del diagrama.
            try:
                self.guitar_canvas.setFixedHeight(196)
                self.guitar_canvas.setMinimumHeight(196)
            except Exception:
                pass
            # En Qt, `expand=True` introduce "stretch" en el VBoxLayout y puede
            # dejar el subpanel de variaciones sin altura visible.
            self.guitar_canvas.pack(fill=tk.X, expand=False)
            self.guitar_variations_frame.pack(fill=tk.X, pady=(6, 0))
        else:
            self.guitar_handedness_combo.pack_forget()
            self.guitar_variations_frame.pack_forget()
            self.guitar_canvas.pack_forget()
            # Igual que el caso guitarra: asegurar que el canvas rellene el ancho.
            # Fijamos altura para que el teclado no se estire en generación.
            try:
                self.keyboard_canvas.setFixedHeight(156)
                self.keyboard_canvas.setMinimumHeight(156)
            except Exception:
                pass
            # En Qt, `expand=True` mete "stretch" y suele crear hueco arriba/abajo
            # dentro del panel inferior. Para piano mantenemos el canvas con altura fija.
            self.keyboard_qscroll.pack(fill=tk.X, expand=False)
        self._fit_instrument_panel_height()
        self._refresh_instrument_toggle_styles()
        self._refresh_handedness_toggle_styles()
        self._refresh_generation_selection_buttons()
        self._refresh_guitar_variations()
        self.redraw_keyboard()
        self.redraw_guitar_fretboard()





































    def _set_guitar_handedness(self, handedness: str) -> None:
        self.guitar_handedness = "left" if handedness == "left" else "right"
        self.config_data["guitar_handedness"] = self.guitar_handedness
        self.save_config()
        self._refresh_handedness_toggle_styles()
        self.redraw_guitar_fretboard()

    def _on_guitar_handedness_combo_changed(self, _event: tk.Event) -> None:
        right_label = self.tr("handed_right")
        left_label = self.tr("handed_left")
        # En Qt, el orden de señales puede hacer que `guitar_handedness_var`
        # se actualice después del callback. Usamos el texto actual del combo
        # para decidir con fiabilidad.
        try:
            selected = str(self.guitar_handedness_combo.currentText())
        except Exception:
            selected = str(self.guitar_handedness_var.get())

        if selected == left_label:
            self._set_guitar_handedness("left")
        else:
            self._set_guitar_handedness("right")

    def _refresh_instrument_toggle_styles(self) -> None:
        if self.instrument_buttons_are_images:
            panel_bg = str(self.instrument_view_switch_side.cget("background"))
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
        right_label = self.tr("handed_right")
        left_label = self.tr("handed_left")
        self.guitar_handedness_combo.configure(values=(right_label, left_label))
        target = left_label if self.guitar_handedness == "left" else right_label
        if str(self.guitar_handedness_var.get()) != target:
            self.guitar_handedness_var.set(target)
            # Mantener sincronizado el combobox visual en Qt.
            try:
                self.guitar_handedness_combo.blockSignals(True)
                self.guitar_handedness_combo.setCurrentText(target)
            finally:
                try:
                    self.guitar_handedness_combo.blockSignals(False)
                except Exception:
                    pass
        self._apply_guitar_handedness_combo_geometry()






    def _compute_guitar_variations(self, root_pc: int, pattern: ChordPattern) -> list[dict]:
        cached = get_cached_variations(self.guitar_chord_cache, root_pc, pattern.suffix)
        if cached:
            processed = self._postprocess_cached_guitar_variations(cached=cached, root_pc=root_pc, pattern=pattern)
            if processed:
                return processed

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
                    # Las formas "cerradas" (posición > 0) a veces se muestran con notas
                    # "por delante" si conservan cuerdas abiertas, especialmente en cejillas.
                    # En vez de descartar cualquier forma con min(fretted) > 0 y open_count > 0,
                    # lo refinamos: solo descartamos cuando la menor posición (min fret)
                    # aparece en 2+ cuerdas (heurística de barre).
                    if fretted and min(fretted) > 0 and open_count > 0:
                        min_fret = min(fretted)
                        min_fret_count = sum(1 for f in fretted if f == min_fret)
                        if min_fret_count >= 2:
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

    def _postprocess_cached_guitar_variations(self, cached: list[dict], root_pc: int, pattern: ChordPattern) -> list[dict]:
        """
        Filtra y reordena variaciones cacheadas para alinearlas con el algoritmo de generación.
        En particular, evita formas cerradas (min fretted > 0) que conservan cuerdas abiertas
        (fret==0), porque se ve una cejilla pero aparecen notas por delante de ella.
        """
        tuning = [40, 45, 50, 55, 59, 64]  # E2 A2 D3 G3 B3 E4 (6->1)
        pcs = {(root_pc + interval) % 12 for interval in pattern.intervals}

        def _as_frets(v: object) -> Optional[list[int]]:
            if not isinstance(v, list) or len(v) < 6:
                return None
            try:
                out = [int(x) for x in v[:6]]
            except Exception:
                return None
            if any(f < -1 for f in out):
                return None
            return out

        candidate_shapes: list[tuple[tuple[int, int, int, int, int, int, int, int], dict]] = []
        for entry in cached:
            frets = _as_frets(entry.get("frets"))
            if frets is None:
                continue

            fretted = [f for f in frets if f > 0]
            open_count = sum(1 for f in frets if f == 0)
            mute_count = sum(1 for f in frets if f < 0)

            if fretted and (max(fretted) - min(fretted) > 4):
                continue
            # Mismo refinamiento que en `_compute_guitar_variations`: descartar solo
            # cuando la menor posición (min fret) actúa como barre (2+ cuerdas).
            if fretted and min(fretted) > 0 and open_count > 0:
                min_fret = min(fretted)
                min_fret_count = sum(1 for f in fretted if f == min_fret)
                if min_fret_count >= 2:
                    continue

            sounding = [(i, f) for i, f in enumerate(frets) if f >= 0]
            if len(sounding) < 3:
                continue
            notes = [tuning[i] + f for i, f in sounding]
            note_pcs = {n % 12 for n in notes}
            if root_pc not in note_pcs:
                continue
            if len(note_pcs) < min(3, len(pcs)):
                continue

            bass_pc = notes[0] % 12
            span = (max(fretted) - min(fretted)) if fretted else 0
            position = min(fretted) if fretted else 0
            complexity = len({f for f in fretted})

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

        if not candidate_shapes:
            return []

        candidate_shapes.sort(key=lambda item: item[0])

        by_position: set[int] = set()
        variations: list[dict] = []
        for _key, entry in candidate_shapes:
            fretted = [f for f in entry["frets"] if f > 0]
            pos = min(fretted) if fretted else 0
            if pos in by_position:
                continue
            by_position.add(pos)
            variations.append(entry)

        chosen = {tuple(v["frets"]) for v in variations}
        for _key, entry in candidate_shapes:
            shape_key = tuple(entry["frets"])
            if shape_key in chosen:
                continue
            variations.append(entry)
            chosen.add(shape_key)

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

    @staticmethod
    def _variation_bass_pc(variation: dict) -> Optional[int]:
        string_notes = variation.get("string_notes")
        if isinstance(string_notes, list) and len(string_notes) >= 6:
            for note in string_notes:
                if note is not None:
                    return int(note) % 12
        frets = variation.get("frets")
        if isinstance(frets, list) and len(frets) >= 6:
            tuning = [40, 45, 50, 55, 59, 64]  # 6->1
            for i, fret in enumerate(frets):
                if isinstance(fret, int) and fret >= 0:
                    return (tuning[i] + fret) % 12
        notes = variation.get("notes")
        if isinstance(notes, list) and notes:
            return int(min(int(n) for n in notes)) % 12
        return None

    def _refresh_guitar_variations(self) -> None:
        for btn in self.guitar_variation_buttons:
            btn.destroy()
        self.guitar_variation_buttons.clear()

        root, pattern = self._resolve_guitar_chord_context()
        if root is None or pattern is None:
            self.guitar_variations_all = []
            self.guitar_variations = []
            self.guitar_selected_variation_idx = None
            self.guitar_selected_variation_notes = set()
            self._last_guitar_chord_key = None
            return

        chord_key = (root, pattern.suffix)
        self.guitar_current_root_pc = root
        if chord_key != self._last_guitar_chord_key:
            self.guitar_variations_all = self._compute_guitar_variations(root, pattern)
            self.guitar_selected_variation_idx = 0 if self.guitar_variations_all else None
            self._last_guitar_chord_key = chord_key

        prev_selected_key: Optional[tuple[int, ...]] = None
        if (
            self.guitar_selected_variation_idx is not None
            and 0 <= self.guitar_selected_variation_idx < len(self.guitar_variations)
        ):
            prev_selected_key = tuple(int(f) for f in self.guitar_variations[self.guitar_selected_variation_idx].get("frets", []))

        displayed_variations = list(self.guitar_variations_all)
        if self.generation_tab_active and displayed_variations:
            inversion_idx = min(max(0, int(self.generation_inversion)), max(0, len(pattern.intervals) - 1))
            target_bass_pc = (root + int(pattern.intervals[inversion_idx])) % 12
            filtered = [v for v in displayed_variations if self._variation_bass_pc(v) == target_bass_pc]
            if filtered:
                displayed_variations = filtered

        self.guitar_variations = displayed_variations

        if not self.guitar_variations:
            self.guitar_selected_variation_notes = set()
            self.guitar_selected_variation_idx = None
            return

        selected_idx: Optional[int] = None
        if prev_selected_key is not None:
            for idx, variation in enumerate(self.guitar_variations):
                if tuple(int(f) for f in variation.get("frets", [])) == prev_selected_key:
                    selected_idx = idx
                    break
        if selected_idx is None:
            selected_idx = 0
        self.guitar_selected_variation_idx = selected_idx
        self.guitar_selected_variation_notes = set(self.guitar_variations[self.guitar_selected_variation_idx]["notes"])

        for idx in range(len(self.guitar_variations)):
            selected = idx == self.guitar_selected_variation_idx
            btn = GrayRoundedButton(
                self.guitar_variations_inner,
                text=str(idx + 1),
                command=lambda i=idx: self._select_guitar_variation(i),
                font_family=self.ui_font_family,
                width=40,
                height=28,
                radius=6,
                font_size=12,
                text_color="#b8c2d1",
                selected_text_color="#0e1320",
                selected_fill_color="#f3bf2f",
                selected_outline_color="#c9961f",
                selected_border_width=2.0,
            )
            btn.set_selected(selected)
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

    def _on_guitar_canvas_press(self, event: tk.Event) -> None:
        if self.generation_tab_active and self.instrument_view == "guitar":
            x = float(event.x)
            y = float(event.y)
            for note, x1, y1, x2, y2 in self.guitar_generation_note_regions:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self._clear_generation_drag_state()
                    self.generation_guitar_drag_active = True
                    self.generation_drag_moved = False
                    self._activate_generation_drag_note(note)
                    break
            return
        if not (self.scale_tab_active and self.scale_play_mode == "guitar"):
            return
        x = float(event.x)
        y = float(event.y)
        clicked_note = self._scale_guitar_note_at_position(x, y)
        clicked_tonic_note: Optional[int] = None
        for note, x1, y1, x2, y2 in self.scale_guitar_tonic_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                clicked_tonic_note = int(note)
                break
        if clicked_tonic_note is not None and self.pedal_active:
            self.scale_guitar_start_note = clicked_tonic_note
            self._refresh_scale_preview()
            self.redraw_guitar_fretboard()
        if clicked_note is not None:
            self.scale_guitar_drag_active = True
            self.scale_guitar_drag_moved = False
            self.scale_guitar_drag_exact_notes.clear()
            self.scale_guitar_drag_staff_notes.clear()
            self._activate_scale_guitar_drag_note(clicked_note)

    def _on_guitar_canvas_drag(self, event: tk.Event) -> None:
        if self.generation_tab_active and self.instrument_view == "guitar" and self.generation_guitar_drag_active:
            x = float(event.x)
            y = float(event.y)
            for note, x1, y1, x2, y2 in self.guitar_generation_note_regions:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    if note not in self.generation_drag_notes:
                        self.generation_drag_moved = True
                    self._activate_generation_drag_note(note)
                    break
            return
        if not (self.scale_tab_active and self.scale_play_mode == "guitar" and self.scale_guitar_drag_active):
            return
        note = self._scale_guitar_note_at_position(float(event.x), float(event.y))
        if note is None or note in self.scale_guitar_drag_exact_notes:
            return
        self.scale_guitar_drag_moved = True
        self._activate_scale_guitar_drag_note(note)

    def _on_guitar_canvas_release(self, _event: tk.Event) -> None:
        if self.generation_tab_active and self.instrument_view == "guitar" and self.generation_guitar_drag_active:
            self._clear_generation_drag_state()
            return
        if not (self.scale_tab_active and self.scale_play_mode == "guitar" and self.scale_guitar_drag_active):
            return
        dragged_exact = set(self.scale_guitar_drag_exact_notes)
        dragged_staff = set(self.scale_guitar_drag_staff_notes)
        self.scale_guitar_drag_active = False
        self.scale_guitar_drag_exact_notes.clear()
        self.scale_guitar_drag_staff_notes.clear()
        if not self.scale_guitar_drag_moved:
            for note in dragged_exact:
                self.scale_guitar_click_highlight_exact_notes.add(note)
                self.after(520, lambda n=note: self._clear_scale_guitar_exact_highlight(n))
            for note in dragged_staff:
                self.scale_guitar_click_highlight_notes.add(note)
                self.after(520, lambda n=note: self._clear_scale_guitar_click_highlight(n))
        self.redraw_guitar_fretboard()
        self.redraw_staff()
        self.redraw_keyboard()
















    def _inversion_label(self, inversion: int) -> str:
        if inversion == 0:
            return self.tr("inversion_root")
        language = self.config_data.get("language", "es")
        if language == "es":
            return f"{inversion}ª inversión"
        ord_map = {1: "1st", 2: "2nd", 3: "3rd"}
        ord_txt = ord_map.get(inversion, f"{inversion}th")
        return f"{ord_txt} inversion"
























































    def _on_staff_motion(self, event: tk.Event) -> None:
        if self.tuner_tab_active:
            idx = self._tuner_string_at_position(float(event.x), float(event.y))
            self.staff_canvas.configure(cursor="hand2" if idx is not None else "")
            return
        if self.generation_tab_active and self.instrument_view == "piano" and self.generation_piano_staff_drag_active:
            note = self._generation_staff_note_at_position(float(event.x), float(event.y))
            if note is not None:
                if (
                    len(self.generated_playing_notes) == 1
                    and note in self.generated_playing_notes
                    and note in self.generated_note_highlight_after
                ):
                    self.staff_canvas.configure(cursor="hand2")
                    return
                self._trigger_generated_single_note(note)
            self.staff_canvas.configure(cursor="hand2" if note is not None else "")
            return
        if self.generation_tab_active and self.instrument_view == "guitar" and self.generation_staff_drag_active:
            note = self._generation_staff_note_at_position(float(event.x), float(event.y))
            if note is not None:
                if note not in self.generation_drag_notes:
                    self.generation_drag_moved = True
                self._activate_generation_drag_note(note)
            self.staff_canvas.configure(cursor="hand2" if note is not None else "")
            return
        if not self.scale_tab_active:
            return
        hit = self._staff_scale_hit_at_position(float(event.x), float(event.y))
        note = hit[0] if hit is not None else None
        degree = int(hit[1]) if hit is not None else None
        if self.scale_staff_drag_active and note is not None:
            if self.staff_pressed_scale_notes == {note} and self.staff_pressed_scale_degrees == {int(degree)}:
                self.staff_canvas.configure(cursor="hand2")
                return
            self.staff_pressed_scale_notes = {note}
            self.staff_pressed_scale_degrees = {int(degree)}
            if self.scale_play_mode == "guitar":
                self.audio_engine.pluck_guitar_note(note, velocity=106, duration_seconds=1.1)
                self.scale_guitar_drag_exact_notes = {int(note)}
                self.scale_guitar_drag_staff_notes = {int(note)}
                self.redraw_guitar_fretboard()
            else:
                self.audio_engine.note_on(note, 106)
            self.redraw_keyboard()
            self.redraw_staff()
            self.staff_canvas.configure(cursor="hand2")
            return
        if note != self.staff_hover_note or degree != self.staff_hover_scale_degree:
            self.staff_hover_note = note
            self.staff_hover_scale_degree = degree
            self.redraw_staff()
        self.staff_canvas.configure(cursor="hand2" if note is not None else "")

    def _on_staff_leave(self, _event: tk.Event) -> None:
        if self.tuner_tab_active:
            self.staff_canvas.configure(cursor="")
            return
        if not self.scale_tab_active:
            return
        if self.staff_hover_note is not None or self.staff_hover_scale_degree is not None:
            self.staff_hover_note = None
            self.staff_hover_scale_degree = None
            self.redraw_staff()
        self.staff_canvas.configure(cursor="")

    def _on_staff_press(self, event: tk.Event) -> None:
        if self.tuner_tab_active:
            idx = self._tuner_string_at_position(float(event.x), float(event.y))
            if idx is not None:
                self._play_tuner_string(idx)
            return
        if self.generation_tab_active and self.instrument_view == "guitar":
            note = self._generation_staff_note_at_position(float(event.x), float(event.y))
            if note is not None:
                self._clear_generation_drag_state()
                self.generation_staff_drag_active = True
                self.generation_drag_moved = False
                self._activate_generation_drag_note(note)
            return
        if self.generation_tab_active and self.instrument_view == "piano":
            note = self._generation_staff_note_at_position(float(event.x), float(event.y))
            if note is not None:
                self.generation_piano_staff_drag_active = True
                self._trigger_generated_single_note(note)
            return
        if not self.scale_tab_active:
            return
        hit = self._staff_scale_hit_at_position(float(event.x), float(event.y))
        if hit is None:
            return
        note, degree = hit
        self.scale_staff_drag_active = True
        self.staff_hover_note = note
        self.staff_hover_scale_degree = int(degree)
        if self.scale_play_mode == "guitar":
            self.staff_pressed_scale_notes = {note}
            self.staff_pressed_scale_degrees = {int(degree)}
            self.audio_engine.pluck_guitar_note(note, velocity=106, duration_seconds=1.1)
            self.scale_guitar_drag_exact_notes = {int(note)}
            self.redraw_guitar_fretboard()
        else:
            for prev in list(self.staff_pressed_scale_notes):
                if prev != note:
                    self.audio_engine.note_off(prev)
            self.staff_pressed_scale_notes = {note}
            self.staff_pressed_scale_degrees = {int(degree)}
            self.audio_engine.note_on(note, 106)
        self.redraw_staff()
        self.redraw_keyboard()

    def _on_staff_release(self, event: tk.Event) -> None:
        if self.generation_tab_active and self.instrument_view == "piano":
            self.generation_piano_staff_drag_active = False
            return
        if self.generation_tab_active and self.instrument_view == "guitar":
            self._clear_generation_drag_state()
            return
        if not self.scale_tab_active:
            return
        self.scale_staff_drag_active = False
        if self.staff_pressed_scale_notes:
            for note in list(self.staff_pressed_scale_notes):
                self.audio_engine.note_off(note)
            self.staff_pressed_scale_notes.clear()
            self.staff_pressed_scale_degrees.clear()
        if self.scale_play_mode == "guitar" and self.scale_guitar_drag_exact_notes:
            self.scale_guitar_drag_exact_notes.clear()
            self.scale_guitar_drag_staff_notes.clear()
            self.redraw_guitar_fretboard()
        hit = self._staff_scale_hit_at_position(float(event.x), float(event.y))
        self.staff_hover_note = hit[0] if hit is not None else None
        self.staff_hover_scale_degree = int(hit[1]) if hit is not None else None
        self.redraw_staff()
        self.redraw_keyboard()












    def _on_global_mouse_release(self, _event: tk.Event) -> None:
        if self.scale_transport_buttons_are_images and self.scale_transport_pressed_mode is not None:
            self._set_scale_transport_icon_pressed(self.scale_transport_pressed_mode, False)
            self.scale_transport_pressed_mode = None
        if self.detection_play_button_pressed:
            self._stop_detection_hold()
        if self.generation_play_button_pressed:
            self._stop_generated_hold(source="button")



    def load_config(self) -> None:
        self.config_data = load_config_file(CONFIG_PATH, DEFAULT_CONFIG)

    def _load_brace_image(self) -> None:
        self.brace_base_image = None
        self.brace_image_cache.clear()
        for path in BRACE_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                pm = QPixmap(str(path))
                if not pm.isNull():
                    self.brace_base_image = pm
                return
            except Exception:
                continue

    def _load_app_logo(self) -> None:
        self.app_logo_image = None
        for path in APP_LOGO_CANDIDATES:
            if not path.exists():
                continue
            try:
                pm = QPixmap(str(path))
                if not pm.isNull():
                    self.app_logo_image = pm
                return
            except Exception:
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
                img = QPixmap(str(path))
                if img.isNull():
                    continue
                self.piano_image = fit_photo_image(img, max_w=86, max_h=34)
                break
            except Exception:
                continue

        for path in METRONOME_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = QPixmap(str(path))
                if img.isNull():
                    continue
                fitted = fit_photo_image(img, max_w=86, max_h=34)
                self.metronome_image = prepare_icon_for_dark_ui(fitted, bg=(43, 47, 55), fg=(246, 246, 246))
                break
            except Exception:
                continue

        for path in GUITAR_IMAGE_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = QPixmap(str(path))
                if img.isNull():
                    continue
                fitted = fit_photo_image(img, max_w=86, max_h=34)
                self.guitar_image = recolor_dark_pixels(fitted, threshold=56, target=(255, 255, 255))
                break
            except Exception:
                continue

        for path in RIGHT_HAND_ICON_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = QPixmap(str(path))
                if img.isNull():
                    continue
                fitted = fit_photo_image(img, max_w=44, max_h=22)
                self.right_hand_icon_image = pad_photo_image(fitted, pad_x=6, pad_y=4)
                break
            except Exception:
                continue

        for path in LEFT_HAND_ICON_CANDIDATES:
            if not path.exists():
                continue
            try:
                img = QPixmap(str(path))
                if img.isNull():
                    continue
                fitted = fit_photo_image(img, max_w=44, max_h=22)
                self.left_hand_icon_image = pad_photo_image(fitted, pad_x=6, pad_y=4)
                break
            except Exception:
                continue

    def _load_clef_images(self) -> None:
        self.treble_clef_image = None
        self.bass_clef_image = None
        for path in TREBLE_CLEF_IMAGE_CANDIDATES:
            if path.exists():
                try:
                    pm = QPixmap(str(path))
                    if not pm.isNull():
                        self.treble_clef_image = pm
                    break
                except Exception:
                    continue
        for path in BASS_CLEF_IMAGE_CANDIDATES:
            if path.exists():
                try:
                    pm = QPixmap(str(path))
                    if not pm.isNull():
                        self.bass_clef_image = pm
                    break
                except Exception:
                    continue

    def _resolve_clef_font(self) -> None:
        """Elige la primera fuente disponible que suele tener símbolos de clave (𝄞 𝄢)."""
        from PySide6.QtGui import QFontDatabase

        available = {f.lower(): f for f in QFontDatabase().families()}
        for candidate in CLEF_FONT_FAMILIES:
            if candidate.lower() in available:
                self._clef_font_family = available[candidate.lower()]
                return
        self._clef_font_family = "serif"

    def _get_brace_image_for_height(self, target_height: int) -> Optional[QPixmap]:
        if self.brace_base_image is None or target_height <= 0:
            return None
        base_h = int(self.brace_base_image.height())
        if base_h <= 0:
            return None

        best_zoom, best_sub = 1, 1
        best_diff = abs(base_h - int(target_height))
        for zoom in range(1, 6):
            for sub in range(1, 10):
                h = max(1, (base_h * zoom) // sub)
                diff = abs(h - int(target_height))
                if diff < best_diff:
                    best_zoom, best_sub = zoom, sub
                    best_diff = diff

        if best_zoom == 1 and best_sub == 1:
            return self.brace_base_image

        key = (best_zoom, best_sub)
        cached = self.brace_image_cache.get(key)
        if cached is not None:
            return cached
        base_w = int(self.brace_base_image.width())
        # Escalar: en Tk sería zoom(best_zoom)/subsample(best_sub); aquí aplicamos el mismo factor.
        scale = float(best_zoom) / float(best_sub)
        new_w = max(1, int(round(base_w * scale)))
        new_h = max(1, int(round(base_h * scale)))
        pm = self.brace_base_image.scaled(new_w, new_h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)  # type: ignore[name-defined]
        self.brace_image_cache[key] = pm
        return pm

    def save_config(self) -> None:
        save_config_file(CONFIG_PATH, self.config_data)






























    def on_close(self) -> None:
        if self._startup_after_id is not None:
            try:
                self.after_cancel(self._startup_after_id)
            except Exception:
                pass
            self._startup_after_id = None
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
        if self.tuner_reference_off_after_id is not None:
            try:
                self.after_cancel(self.tuner_reference_off_after_id)
            except Exception:
                pass
            self.tuner_reference_off_after_id = None
        self._stop_generated_playback()
        self._stop_scale_playback()
        self._stop_metronome()
        self._stop_tuner_stream()
        self._stop_tuner_reference_note()
        self._stop_staff_scale_note_playback()
        self.disconnect_ports()
        self.deleteLater()

    # Qt: interceptar el cierre de ventana para ejecutar el apagado ordenado.
    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self.on_close()
        finally:
            try:
                event.accept()
            except Exception:
                pass


def _argv_for_qt_and_verbose_env(argv: list[str]) -> list[str]:
    """Quita flags de verbose del argv de Qt y activa MIDICHORDS_VERBOSE si vienen en CLI."""
    if not argv:
        return argv
    out = [argv[0]]
    for a in argv[1:]:
        low = str(a).lower().replace("\\", "/")
        if low in ("--verbose", "-v", "/verbose"):
            os.environ["MIDICHORDS_VERBOSE"] = "1"
            continue
        out.append(a)
    return out


def main() -> None:
    from PySide6.QtWidgets import QApplication

    qt_argv = _argv_for_qt_and_verbose_env(list(sys.argv))
    qt_app = QApplication.instance() or QApplication(qt_argv)
    # En macOS el Cmd-Tab a veces usa el icono de QApplication (no el de la ventana),
    # así que lo fijamos antes de crear/show la UI.
    try:
        icon_pixmap: Optional[QPixmap] = None
        for path in APP_LOGO_CANDIDATES:
            if not path.exists():
                continue
            pm = QPixmap(str(path))
            if not pm.isNull():
                icon_pixmap = pm
                break
        if icon_pixmap is not None and not icon_pixmap.isNull():
            sizes = [16, 32, 64, 128, 256]
            icon = QIcon()
            for s in sizes:
                try:
                    pm = icon_pixmap.scaled(
                        s,
                        s,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                except Exception:
                    pm = icon_pixmap
                icon.addPixmap(pm)
            qt_app.setWindowIcon(icon)
    except Exception:
        pass
    if is_verbose():
        vlog("app", "Modo verbose activo (audio/MIDI en stderr). MIDICHORDS_VERBOSE=1")
    window = MidiChordAnalyzerApp()
    window.update_music_views()
    window.show()
    raise SystemExit(qt_app.exec())


if __name__ == "__main__":
    main()
