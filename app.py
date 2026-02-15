from __future__ import annotations

import json
import math
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Optional

import mido
import numpy as np
import sounddevice as sd


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
NOTE_NAMES = {
    "en": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "es": ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
}
WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
# Indice diatonico por clase de pitch (C..B), manteniendo sostenidos en la misma linea/espacio base.
PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]


@dataclass(frozen=True)
class ChordPattern:
    suffix: str
    intervals: tuple[int, ...]


@dataclass
class Voice:
    note: int
    freq: float
    detune_ratios: list[float]
    brightness: float
    velocity_gain: float
    age_samples: int = 0
    released: bool = False
    release_samples: int = 0


CHORD_PATTERNS = [
    ChordPattern("", (0, 4, 7)),
    ChordPattern("m", (0, 3, 7)),
    ChordPattern("dim", (0, 3, 6)),
    ChordPattern("aug", (0, 4, 8)),
    ChordPattern("sus2", (0, 2, 7)),
    ChordPattern("sus4", (0, 5, 7)),
    ChordPattern("6", (0, 4, 7, 9)),
    ChordPattern("m6", (0, 3, 7, 9)),
    ChordPattern("7", (0, 4, 7, 10)),
    ChordPattern("maj7", (0, 4, 7, 11)),
    ChordPattern("m7", (0, 3, 7, 10)),
    ChordPattern("mMaj7", (0, 3, 7, 11)),
    ChordPattern("dim7", (0, 3, 6, 9)),
    ChordPattern("m7b5", (0, 3, 6, 10)),
]


class PianoAudioEngine:
    def __init__(self, sample_rate: int = 48000) -> None:
        self.sample_rate = sample_rate
        self.channels = 2
        self.master_gain = 0.14
        self.stream: Optional[sd.OutputStream] = None
        self.lock = threading.Lock()
        self.voices: dict[int, Voice] = {}

    @staticmethod
    def midi_note_to_freq(note: int) -> float:
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    def start(self, output_device: Optional[int]) -> None:
        self.stop()
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            device=output_device,
            dtype="float32",
            callback=self._audio_callback,
            blocksize=0,
            latency="low",
        )
        self.stream.start()

    def stop(self) -> None:
        with self.lock:
            self.voices.clear()

        if self.stream is not None:
            try:
                self.stream.stop()
            except Exception:
                pass
            try:
                self.stream.close()
            except Exception:
                pass
            self.stream = None

    def note_on(self, note: int, velocity: int) -> None:
        if velocity <= 0:
            self.note_off(note)
            return

        gain = max(0.05, min(1.0, velocity / 127.0))
        brightness = min(1.0, max(0.0, (velocity / 127.0) ** 0.7))
        detune_cents = self._detune_cents_for_note(note)
        detune_ratios = [2.0 ** (c / 1200.0) for c in detune_cents]
        voice = Voice(
            note=note,
            freq=self.midi_note_to_freq(note),
            detune_ratios=detune_ratios,
            brightness=brightness,
            velocity_gain=gain,
            age_samples=0,
            released=False,
            release_samples=0,
        )
        with self.lock:
            self.voices[note] = voice

    @staticmethod
    def _detune_cents_for_note(note: int) -> list[float]:
        # Piano real: 1 cuerda en graves muy bajos, 2 en graves-medios, 3 en el resto.
        if note < 40:
            return [0.0]
        if note < 52:
            return [-1.8, 1.8]
        return [-3.2, 0.0, 3.2]

    def note_off(self, note: int) -> None:
        with self.lock:
            voice = self.voices.get(note)
            if voice is not None:
                voice.released = True
                voice.release_samples = 0

    def _audio_callback(self, outdata: np.ndarray, frames: int, _time, _status) -> None:
        signal = np.zeros(frames, dtype=np.float32)

        with self.lock:
            if not self.voices:
                outdata.fill(0)
                return

            to_remove: list[int] = []
            n = np.arange(frames, dtype=np.float64)

            for note, voice in list(self.voices.items()):
                start_age = voice.age_samples
                age = (start_age + n) / self.sample_rate
                attack = 1.0 - np.exp(-age / 0.0035)

                # Inharmonicidad de cuerdas reales (mayor en agudos).
                b_coeff = 0.000015 + (voice.freq / 4200.0) ** 2 * 0.00022
                partial_count = 7
                spectrum = np.zeros(frames, dtype=np.float64)
                nyquist_guard = self.sample_rate * 0.45

                # Simulacion de varias cuerdas por nota (batidos por detune).
                for ratio in voice.detune_ratios:
                    string_tone = np.zeros(frames, dtype=np.float64)
                    for k in range(1, partial_count + 1):
                        inharmonic = math.sqrt(1.0 + b_coeff * (k * k))
                        harmonic_freq = voice.freq * ratio * k * inharmonic
                        if harmonic_freq >= nyquist_guard:
                            continue

                        phases = (2.0 * math.pi * harmonic_freq * age) + (k * 0.17)

                        # Brillo dependiente de velocidad y decaimiento por parcial.
                        harmonic_shape = 0.95 + (1.10 * (1.0 - voice.brightness))
                        harmonic_amp = 1.0 / (k ** harmonic_shape)
                        decay_rate = 0.30 + 0.12 * k + 0.015 * max(0.0, voice.freq - 220.0) / 220.0
                        partial_env = np.exp(-decay_rate * age)
                        string_tone += harmonic_amp * np.sin(phases) * partial_env

                    spectrum += string_tone

                hold_floor = 0.10 + 0.08 * (1.0 - voice.brightness)
                sustain_decay = np.exp(-(0.78 + voice.freq / 2900.0) * age)
                hold_env = attack * (hold_floor + (1.0 - hold_floor) * sustain_decay)

                if voice.released:
                    release_age = (voice.release_samples + n) / self.sample_rate
                    release_env = np.exp(-6.5 * release_age)
                    env = hold_env * release_env
                else:
                    env = hold_env

                tone = spectrum / max(1, len(voice.detune_ratios))
                signal += (tone * env * voice.velocity_gain).astype(np.float32)

                voice.age_samples += frames
                if voice.released:
                    voice.release_samples += frames

                end_env = float(env[-1]) if frames else 0.0
                if voice.released and end_env < 0.0005:
                    to_remove.append(note)

            for note in to_remove:
                self.voices.pop(note, None)

        signal = np.clip(signal * self.master_gain, -0.98, 0.98)
        outdata[:, 0] = signal
        if outdata.shape[1] > 1:
            outdata[:, 1] = signal


class MidiChordAnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MIDI Chords Analyzer")
        self.geometry("1300x800")
        self.minsize(980, 620)

        self.config_data = {
            "language": "es",
            "midi_input": "",
            "audio_output": "",
            "show_keyboard_note_labels": False,
        }
        self.load_config()
        self.brace_base_image: Optional[tk.PhotoImage] = None
        self.brace_image_cache: dict[tuple[int, int], tk.PhotoImage] = {}
        self.app_logo_image: Optional[tk.PhotoImage] = None
        self._load_brace_image()
        self._load_app_logo()

        self.active_notes: set[int] = set()
        self.midi_held_notes: set[int] = set()
        self.mouse_held_notes: set[int] = set()
        self.sustain_latched_notes: set[int] = set()
        self.note_velocity: dict[int, int] = {}
        self.pedal_active = False
        self.mouse_current_note: Optional[int] = None
        self.white_key_regions: list[tuple[int, float, float, float, float]] = []
        self.black_key_regions: list[tuple[int, float, float, float, float]] = []
        self.message_queue: queue.Queue = queue.Queue()

        self.input_port: Optional[mido.ports.BaseInput] = None

        self.input_names: list[str] = []
        self.audio_output_names: list[str] = []
        self.audio_output_map: dict[str, int] = {}
        self.audio_engine = PianoAudioEngine()

        self._build_ui()
        self.refresh_devices()
        self.connect_ports()
        self.after(20, self._process_midi_queue)

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

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
        side_panel.rowconfigure(1, weight=1)

        chord_panel = ttk.LabelFrame(side_panel, text="Acorde", padding=(12, 10))
        chord_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        settings_panel = ttk.LabelFrame(side_panel, text="Configuración", padding=(12, 10))
        settings_panel.grid(row=1, column=0, sticky="nsew", pady=(6, 0))

        title = ttk.Label(chord_panel, text="Acorde", font=("Helvetica", 18, "bold"))
        title.pack(anchor="w", pady=(4, 8))

        self.chord_var = tk.StringVar(value="-")
        self.chord_label = ttk.Label(chord_panel, textvariable=self.chord_var, font=("Helvetica", 36, "bold"))
        self.chord_label.pack(anchor="w", pady=(0, 18))

        notes_caption = ttk.Label(chord_panel, text="Notas activas", font=("Helvetica", 12, "bold"))
        notes_caption.pack(anchor="w")

        self.notes_var = tk.StringVar(value="-")
        self.notes_label = ttk.Label(chord_panel, textvariable=self.notes_var, wraplength=420, font=("Menlo", 12))
        self.notes_label.pack(anchor="w", pady=(6, 12))

        self.status_var = tk.StringVar(value="Sin notas")
        status_label = ttk.Label(settings_panel, textvariable=self.status_var, wraplength=420)
        status_label.pack(anchor="w", pady=(8, 14))

        config_btn = ttk.Button(settings_panel, text="Abrir configuración", command=self.open_settings_dialog)
        config_btn.pack(anchor="w")

        separator = ttk.Separator(container, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(10, 10))

        self.keyboard_canvas = tk.Canvas(
            container,
            bg="#f5f4ef",
            height=120,
            highlightthickness=1,
            highlightbackground="#cfc9bc",
        )
        self.keyboard_canvas.pack(fill=tk.BOTH, expand=False)

        self.staff_canvas.bind("<Configure>", lambda _event: self.redraw_staff())
        self.keyboard_canvas.bind("<Configure>", lambda _event: self.redraw_keyboard())
        self.keyboard_canvas.bind("<ButtonPress-1>", self._on_keyboard_press)
        self.keyboard_canvas.bind("<B1-Motion>", self._on_keyboard_drag)
        self.keyboard_canvas.bind("<ButtonRelease-1>", self._on_keyboard_release)
        self.bind_all("<KeyPress-Shift_L>", self._on_shift_press)
        self.bind_all("<KeyPress-Shift_R>", self._on_shift_press)
        self.bind_all("<KeyRelease-Shift_L>", self._on_shift_release)
        self.bind_all("<KeyRelease-Shift_R>", self._on_shift_release)

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
            self.status_var.set(f"Error listando entradas MIDI: {exc}")
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
            self.status_var.set(f"Error listando salidas de audio: {exc}")
            self.audio_output_names = []
            self.audio_output_map = {}

    def connect_ports(self) -> None:
        self.disconnect_ports()

        input_name = self.config_data.get("midi_input", "")
        audio_name = self.config_data.get("audio_output", "")
        audio_error: Optional[str] = None

        if input_name:
            try:
                self.input_port = mido.open_input(input_name, callback=self._on_midi_message)
            except Exception as exc:
                self.status_var.set(f"No se pudo abrir entrada MIDI: {exc}")
                self.input_port = None

        audio_device_index = self.audio_output_map.get(audio_name)
        try:
            self.audio_engine.start(audio_device_index)
        except Exception as exc:
            audio_error = str(exc)

        in_state = input_name if self.input_port else "Sin entrada"
        if self.audio_engine.stream is None:
            out_state = "No disponible"
        elif audio_name and audio_name in self.audio_output_map:
            out_state = audio_name
        else:
            out_state = "Salida por defecto"

        status = f"Entrada MIDI: {in_state}\nSalida audio: {out_state}"
        if audio_error:
            status += f"\nError audio: {audio_error}"
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
        self.pedal_active = True

    def _on_shift_release(self, _event: tk.Event) -> None:
        self.pedal_active = False
        self.sustain_latched_notes.clear()
        self._refresh_sounding_notes()

    def _process_midi_queue(self) -> None:
        changed = False
        while True:
            try:
                message = self.message_queue.get_nowait()
            except queue.Empty:
                break

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
    def _diatonic_index(midi_note: int) -> int:
        octave = midi_note // 12 - 1
        letter_index = PC_TO_DIATONIC_LETTER[midi_note % 12]
        return octave * 7 + letter_index

    def detect_chord(self) -> str:
        if not self.active_notes:
            return "-"

        pcs = {note % 12 for note in self.active_notes}
        if len(pcs) == 1:
            note = next(iter(pcs))
            return self.note_name(note, with_octave=False)

        best_score = -999
        best_complexity = -999
        best_root: Optional[int] = None
        best_pattern: Optional[ChordPattern] = None
        for root in range(12):
            for pattern in CHORD_PATTERNS:
                template = {(root + interval) % 12 for interval in pattern.intervals}
                extra = len(pcs - template)
                missing = len(template - pcs)

                if extra == 0 and missing == 0:
                    score = 100
                elif missing == 0:
                    score = 70 - extra
                elif extra == 0:
                    score = 40 - missing
                else:
                    continue

                complexity = -len(pattern.intervals)
                if score > best_score or (score == best_score and complexity > best_complexity):
                    best_score = score
                    best_complexity = complexity
                    best_root = root
                    best_pattern = pattern

        if best_root is None or best_pattern is None:
            ordered = sorted(self.active_notes)
            return " + ".join(self.note_name(n, with_octave=False) for n in ordered)

        root = best_root
        pattern = best_pattern
        chord = f"{self.note_name(root, with_octave=False)}{pattern.suffix}"

        bass_pc = min(self.active_notes) % 12
        if bass_pc != root:
            chord = f"{chord}/{self.note_name(bass_pc, with_octave=False)}"

        return chord

    def update_music_views(self) -> None:
        if self.active_notes:
            ordered = sorted(self.active_notes)
            self.notes_var.set(" - ".join(self.note_name(note) for note in ordered))
        else:
            self.notes_var.set("-")

        self.chord_var.set(self.detect_chord())
        self.redraw_keyboard()
        self.redraw_staff()

    def redraw_keyboard(self) -> None:
        canvas = self.keyboard_canvas
        canvas.delete("all")
        self.white_key_regions = []
        self.black_key_regions = []

        w = max(100, canvas.winfo_width())
        h = max(120, canvas.winfo_height())

        low_note, high_note = 21, 108
        notes = list(range(low_note, high_note + 1))
        white_notes = [n for n in notes if (n % 12) in WHITE_PCS]
        white_w = w / len(white_notes)
        key_top = 10
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

            if note in self.active_notes:
                top_fill = "#4da3ea"
                base_fill = "#4da3ea"
            else:
                top_fill = "#f9f9f5"
                base_fill = "#ecebe7"

            canvas.create_rectangle(x1, key_top, x2, key_bottom, fill=base_fill, outline="#9a9a9a", width=1)
            canvas.create_rectangle(x1 + 1, key_top + 1, x2 - 1, key_top + (key_bottom - key_top) * 0.42, fill=top_fill, outline="")
            canvas.create_line(x1 + 1, key_bottom - 2, x2 - 1, key_bottom - 2, fill="#c8c8c8")
            if self.config_data.get("show_keyboard_note_labels", False):
                label_color = "#0b2540" if note in self.active_notes else "#5f5f5f"
                canvas.create_text(
                    (x1 + x2) / 2,
                    key_bottom - 16,
                    text=self.note_name(note, with_octave=False),
                    fill=label_color,
                    font=("Helvetica", 8, "bold"),
                )
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

            if note in self.active_notes:
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
            self.black_key_regions.append((note, x1, key_top, x2, key_top + black_h))

        # Franja inferior para dar profundidad y etiquetas de octava.
        canvas.create_rectangle(0, key_bottom, w, h, fill="#101010", outline="")
        if not self.config_data.get("show_keyboard_note_labels", False):
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

        w = max(300, canvas.winfo_width())
        h = max(260, canvas.winfo_height())

        margin_x = 72
        right_x = w - 20
        line_space = min(19, max(12, h // 24))
        treble_top = max(24, int(h * 0.08))
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

        if not self.active_notes:
            canvas.create_text(
                w / 2,
                min(h - 30, bass_top + 5.6 * line_space),
                text="Sin notas activas",
                fill="#cfcfcf",
                font=("Helvetica", 13, "italic"),
            )
            return

        ordered = sorted(self.active_notes)
        chord_x = margin_x + max(110, min(w - margin_x - 70, (w - margin_x) * 0.45))

        # Todas las notas se dibujan en el mismo tiempo (misma x) y en
        # posiciones diatonicas exactas (linea/espacio real del pentagrama).
        treble_bottom_line_diatonic = 4 * 7 + 2  # E4
        bass_bottom_line_diatonic = 2 * 7 + 4    # G2
        staff_step = line_space / 2.0
        for note in ordered:
            x = chord_x
            if note >= 60:
                diatonic_steps = self._diatonic_index(note) - treble_bottom_line_diatonic
                y = treble_top + 4 * line_space - diatonic_steps * staff_step
            else:
                diatonic_steps = self._diatonic_index(note) - bass_bottom_line_diatonic
                y = bass_top + 4 * line_space - diatonic_steps * staff_step

            canvas.create_oval(x - 9, y - 6, x + 9, y + 6, fill="#000000", outline="#ffffff", width=2)

    def open_settings_dialog(self) -> None:
        self.refresh_devices()

        dialog = tk.Toplevel(self)
        dialog.title("Configuración")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Idioma").grid(row=0, column=0, sticky="w", pady=4)
        lang_var = tk.StringVar(value=self.config_data.get("language", "es"))
        lang_combo = ttk.Combobox(frame, textvariable=lang_var, state="readonly", values=["es", "en"], width=18)
        lang_combo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Entrada MIDI").grid(row=1, column=0, sticky="w", pady=4)
        in_values = [""] + self.input_names
        in_var = tk.StringVar(value=self.config_data.get("midi_input", ""))
        in_combo = ttk.Combobox(frame, textvariable=in_var, state="readonly", values=in_values, width=48)
        in_combo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Salida de audio").grid(row=2, column=0, sticky="w", pady=4)
        out_values = [""] + self.audio_output_names
        out_var = tk.StringVar(value=self.config_data.get("audio_output", ""))
        out_combo = ttk.Combobox(frame, textvariable=out_var, state="readonly", values=out_values, width=48)
        out_combo.grid(row=2, column=1, sticky="ew", pady=4)

        show_labels_var = tk.BooleanVar(value=bool(self.config_data.get("show_keyboard_note_labels", False)))
        show_labels_chk = ttk.Checkbutton(
            frame,
            text="Mostrar notas en teclas blancas",
            variable=show_labels_var,
        )
        show_labels_chk.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 4))

        def do_refresh() -> None:
            self.refresh_devices()
            in_combo["values"] = [""] + self.input_names
            out_combo["values"] = [""] + self.audio_output_names

        def do_save() -> None:
            self.config_data["language"] = lang_var.get() if lang_var.get() in ("es", "en") else "es"
            self.config_data["midi_input"] = in_var.get().strip()
            self.config_data["audio_output"] = out_var.get().strip()
            self.config_data["show_keyboard_note_labels"] = bool(show_labels_var.get())
            self.save_config()
            self.connect_ports()
            self.update_music_views()
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e")

        ttk.Button(buttons, text="Actualizar", command=do_refresh).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="Guardar", command=do_save).pack(side=tk.LEFT)

        frame.columnconfigure(1, weight=1)

    def on_close(self) -> None:
        self.disconnect_ports()
        self.destroy()


def main() -> None:
    app = MidiChordAnalyzerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.update_music_views()
    app.mainloop()


if __name__ == "__main__":
    main()
