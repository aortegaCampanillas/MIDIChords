from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent


def _resolve_config_path() -> Path:
    if not getattr(sys, "frozen", False):
        return PROJECT_ROOT / "config.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MIDIChords" / "config.json"
    config_root = os.environ.get("XDG_CONFIG_HOME")
    if config_root:
        return Path(config_root) / "MIDIChords" / "config.json"
    return Path.home() / ".config" / "MIDIChords" / "config.json"


CONFIG_PATH = _resolve_config_path()

FORCE_RTMIDI_SCAN_ENV = "MIDICHORDS_FORCE_RTMIDI_SCAN"
DISABLE_RTMIDI_SCAN_ENV = "MIDICHORDS_DISABLE_RTMIDI_SCAN"
FORCE_MIDI_OPEN_ENV = "MIDICHORDS_FORCE_MIDI_OPEN"

BRACE_IMAGE_CANDIDATES = [
    PROJECT_ROOT / "assets" / "brace_left.png",
    PROJECT_ROOT / "assets" / "brace_left.jpg",
    PROJECT_ROOT / "assets" / "brace_left.jpeg",
    PROJECT_ROOT / "assets" / "brace_left.gif",
    PROJECT_ROOT / "assets" / "brace_left.ppm",
]

APP_LOGO_CANDIDATES = [
    PROJECT_ROOT / "assets" / "app_logo.png",
    PROJECT_ROOT / "assets" / "app_logo.gif",
    PROJECT_ROOT / "assets" / "app_logo.ppm",
]

PIANO_IMAGE_CANDIDATES = [
    PROJECT_ROOT / "assets" / "piano.png",
    PROJECT_ROOT / "assets" / "piano.gif",
    PROJECT_ROOT / "assets" / "piano.ppm",
]

METRONOME_IMAGE_CANDIDATES = [
    PROJECT_ROOT / "assets" / "metronome.png",
    PROJECT_ROOT / "assets" / "metronome.gif",
    PROJECT_ROOT / "assets" / "metronome.ppm",
]

GUITAR_IMAGE_CANDIDATES = [
    PROJECT_ROOT / "assets" / "guitar.png",
    PROJECT_ROOT / "assets" / "guitar.gif",
    PROJECT_ROOT / "assets" / "guitar.ppm",
]

RIGHT_HAND_ICON_CANDIDATES = [
    PROJECT_ROOT / "assets" / "right_hand.png",
    PROJECT_ROOT / "assets" / "right_hand.gif",
    PROJECT_ROOT / "assets" / "right_hand.ppm",
]

LEFT_HAND_ICON_CANDIDATES = [
    PROJECT_ROOT / "assets" / "left_hand.png",
    PROJECT_ROOT / "assets" / "left_hand.gif",
    PROJECT_ROOT / "assets" / "left_hand.ppm",
]

DEFAULT_CONFIG = {
    "language": "es",
    "midi_input": "",
    "audio_output": "",
    "midi_input_sound_enabled": True,
    "sound_preset": "acoustic",
    "guitar_sound_preset": "steel_clean",
    "show_keyboard_note_labels": False,
    "metronome_bpm": 120,
    "metronome_volume": 100,
    "metronome_beats_per_bar": 4,
    "metronome_clicks_per_beat": 1,
    "metronome_timer_enabled": False,
    "metronome_timer_minutes": 2,
    "metronome_timer_seconds": 0,
    "metronome_bar_accent_enabled": True,
    "scale_play_mode": "piano",
    "mode": "detection",
    "note_accidental": "sharp",
    "instrument_view": "piano",
    "generation_instrument_view": "piano",
    "guitar_handedness": "right",
    "tuner_tuning": "standard_e",
    "tuner_input": "",
    "tuner_input_gain": 100,
    "tuner_spectrum_min_hz": 0,
    "tuner_spectrum_max_hz": 500,
}
