from __future__ import annotations

import math
from pathlib import Path
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import sounddevice as sd

from midichords.core.app_constants import PROJECT_ROOT
from midichords.core.verbose_log import vlog


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
    # Nivel de envolvente al pasar a release (primer bloque de audio tras note_off).
    # Evita mezclar sustain decreciente × exp(release), que puede dar transiente tipo “clic”.
    release_peak: float = 1.0
    release_peak_set: bool = False
    # True para voces desplazadas a fading_voices en un retrigger (crossfade):
    # usan un release mucho más rápido (~380ms) que el normal (~1.4-2.2s), ya
    # que solo necesitan evitar el corte brusco, no sostener el timbre. Sin
    # esto, cambiar de acorde rápido (p. ej. círculo de quintas) acumula
    # decenas de voces fantasma sonando a la vez y genera ruido audible.
    fast_release: bool = False


@dataclass
class ClickVoice:
    accent_level: int
    sample: Optional[np.ndarray] = None
    sample_pos: int = 0
    sample_gain: float = 1.0
    age_samples: int = 0


@dataclass
class GuitarVoice:
    buffer: np.ndarray
    pos: int
    gain: float
    decay: float
    remaining_samples: int


@dataclass
class SampleVoice:
    note: int
    buffer: np.ndarray
    pos: float
    step: float
    gain: float
    decay: float
    release: float = 1.0
    rendered_samples: int = 0
    max_samples: int = 0
    attack_samples: int = 0   # smoothstep ramp 0→1 on note start to avoid click
    fade_out_total: int = 0   # when > 0, note_off smoothstep fade is active
    fade_out_remaining: int = 0
    amplitude_cap: float = 1.0  # caps ramp if note_off fires during attack phase


class PianoAudioEngine:
    def __init__(self, sample_rate: int = 48000) -> None:
        self.sample_rate = sample_rate
        self.channels = 2
        # Nivel nominal común para escritorio. 0.14 dejaba una nota normal
        # alrededor de -25 dBFS RMS, sensiblemente por debajo de los motores
        # web/móvil y especialmente perceptible en el mezclador de Windows.
        # 0.28 aporta +6 dB y conserva margen en acordes gracias al soft-clip.
        self.master_gain = 0.28
        self.preset = "acoustic"
        self.guitar_preset = "steel_clean"
        self.output_device: Optional[int] = None
        self.stream: Optional[sd.OutputStream] = None
        self._stream_lock = threading.Lock()
        self.lock = threading.Lock()
        self.voices: dict[int, Voice] = {}
        self.fading_voices: list[Voice] = []
        self.click_voices: list[ClickVoice] = []
        self.guitar_voices: list[GuitarVoice] = []
        self.sample_voices: list[SampleVoice] = []
        self._last_activity_monotonic: float = 0.0
        self.metronome_sample: Optional[np.ndarray] = self._load_default_metronome_sample()
        self.metronome_sample_accent: Optional[np.ndarray] = self._build_accent_sample(self.metronome_sample)
        self.metronome_sample_bar: Optional[np.ndarray] = self._build_accent_sample(self.metronome_sample, ratio=1.34)
        self.rng = np.random.default_rng()
        self.piano_sample_map = self._load_sample_bank(
            PROJECT_ROOT / "assets" / "samples" / "grand_piano",
            {
                36: "C2.mp3",
                48: "C3.mp3",
                60: "C4.mp3",
                72: "C5.mp3",
                84: "C6.mp3",
            },
            max_seconds=10.0,
        )
        self.guitar_sample_map = self._load_sample_bank(
            PROJECT_ROOT / "assets" / "samples" / "guitar_nylon",
            {
                40: "E2.mp3",
                45: "A2.mp3",
                50: "D3.mp3",
                52: "E3.mp3",
                55: "G3.mp3",
                59: "B3.mp3",
                64: "E4.mp3",
            },
            max_seconds=4.0,
        )

    @staticmethod
    def _one_pole_lowpass(x: np.ndarray, alpha: float) -> np.ndarray:
        """Filtro low-pass simple para suavizar el ruido del pick."""
        if x.size == 0:
            return x
        a = float(max(0.0, min(1.0, alpha)))
        y = np.empty_like(x)
        y[0] = x[0]
        # y[n] = y[n-1] + a * (x[n] - y[n-1])
        for i in range(1, x.size):
            prev = y[i - 1]
            y[i] = prev + a * (x[i] - prev)
        return y

    def set_preset(self, preset: str) -> None:
        if preset not in {"acoustic", "warm", "bright", "soft", "grand_sample"}:
            preset = "acoustic"
        self.preset = preset

    def set_guitar_preset(self, preset: str) -> None:
        if preset not in {"steel_clean", "steel_bright", "nylon_warm", "muted_short", "nylon_sample"}:
            preset = "steel_clean"
        self.guitar_preset = preset

    @staticmethod
    def midi_note_to_freq(note: int) -> float:
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    def start(self, output_device: Optional[int]) -> None:
        self.stop()
        self.output_device = output_device
        if sys.platform == "win32":
            # En Windows, "high"/"low" son solo hints: con el host API MME
            # (el que PortAudio usa por defecto aquí si no se fuerza otro),
            # "low" + 256 medía ~96ms reales (frente a ~213ms con el ajuste
            # de macOS de abajo) — mejor, pero sigue siendo lag perceptible al
            # tocar. Pasando un valor numérico en segundos en vez del string,
            # PortAudio/MME lo respeta de forma mucho más literal. 128/0.01
            # medía ~10.7ms reales pero producía cortes audibles (underruns)
            # bajo carga pesada (acordes de muchas notas con sample_piano).
            # 512/0.03 no mostró underruns en las pruebas originales, pero en
            # otros equipos (con `--verbose`, trazas de `callback late` +
            # `status flags: output underflow`) el callback llegaba tarde de
            # forma sistemática incluso sin voces sonando — el margen de
            # ~10.7ms del bloque de 512 es insuficiente ahí. 1024/0.06 casi
            # duplica el margen (~21ms) a cambio de algo más de latencia.
            blocksize = 1024
            latency: object = 0.06
        else:
            # Buffer más grande que el original (256/"low"): con buffers muy
            # pequeños, si el hilo de audio de CoreAudio queda desalojado del
            # CPU (p. ej. tras un rato sin sonar nada, o mientras se enumeran
            # dispositivos), el primer bloque al retomar puede producir un
            # glitch/click audible. Coste: unos 10-20 ms más de latencia,
            # normalmente imperceptible al tocar.
            blocksize = 1024
            latency = "high"
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            device=output_device,
            dtype="float32",
            callback=self._audio_callback,
            blocksize=blocksize,
            latency=latency,
        )
        self.stream.start()
        vlog(
            "audio",
            "OutputStream started: device=%s sample_rate=%s blocksize=%s latency=%s channels=%s",
            output_device,
            self.sample_rate,
            blocksize,
            latency,
            self.channels,
        )

    def set_output_device(self, output_device: Optional[int]) -> None:
        restart_stream = self.stream is not None and self.output_device != output_device
        self.output_device = output_device
        vlog("audio", "set_output_device: index=%s restart_stream=%s", output_device, restart_stream)
        if restart_stream:
            self.start(output_device)

    def ensure_started(self) -> None:
        # Evita que dos rutas (hilo de precalentamiento + primer note_on) arranquen
        # el stream simultáneamente.
        with self._stream_lock:
            if self.stream is None:
                vlog("audio", "ensure_started: opening stream (output_device=%s)", self.output_device)
                self.start(self.output_device)

    def stop(self) -> None:
        with self.lock:
            self.voices.clear()
            self.fading_voices.clear()
            self.click_voices.clear()
            self.guitar_voices.clear()
            self.sample_voices.clear()

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
        vlog("audio", "OutputStream stopped")

    def _mark_activity(self) -> None:
        self._last_activity_monotonic = time.monotonic()

    def has_recent_activity(self, within_seconds: float = 2.0) -> bool:
        """True si hay voces sonando ahora o hubo actividad hace poco.

        Usado para evitar operaciones (como enumerar dispositivos de audio)
        que pueden introducir un glitch/ruido en un stream de audio activo.
        """
        if self.voices or self.click_voices or self.guitar_voices or self.sample_voices:
            return True
        return (time.monotonic() - self._last_activity_monotonic) < within_seconds

    def note_on(self, note: int, velocity: int) -> bool:
        """Start a note. Returns True if a new voice was started, False if ignored (duplicate) or failed."""
        if velocity <= 0:
            self.note_off(note)
            return False
        try:
            self.ensure_started()
        except Exception:
            return False
        self._mark_activity()
        if self.preset == "grand_sample" and self.piano_sample_map:
            self._trigger_sample_voice(
                note=note,
                velocity=velocity,
                sample_bank=self.piano_sample_map,
                gain_mul=0.92,
                decay=0.999985,
                max_seconds=7.0,
            )
            return True

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
            release_peak=1.0,
            release_peak_set=False,
        )
        with self.lock:
            prev = self.voices.get(note)
            if prev is not None and not prev.released:
                vlog("audio", "note_on ignored while holding: note=%s", note)
                return False
            if prev is not None and prev.released:
                # La nota anterior seguía sonando su cola de apagado (release):
                # esto pasa a menudo al cambiar de acorde con una nota en común.
                # Sustituirla de golpe corta su envolvente en mitad de la
                # amplitud, lo que se oye como un click/ruido. Se deja seguir
                # sonando en una lista aparte, con fade rápido (ver
                # Voice.fast_release) para que no se acumulen decenas de voces
                # fantasma si el usuario cambia de acorde repetidamente.
                prev.fast_release = True
                self.fading_voices.append(prev)
            self.voices[note] = voice
        return True

    @staticmethod
    def _detune_cents_for_note(note: int) -> list[float]:
        # Piano real: 1 cuerda en graves muy bajos, 2 en graves-medios, 3 en el resto.
        if note < 40:
            return [0.0]
        if note < 52:
            return [-1.8, 1.8]
        return [-3.2, 0.0, 3.2]

    # Nº máximo de voces en cola de apagado (released) toleradas antes de
    # forzar un fade rápido en las más antiguas. El release normal del piano
    # dura ~1.4-2.2s; si se cambia de acorde varias veces por segundo (p. ej.
    # clics rápidos en el círculo de quintas), decenas de esas colas pueden
    # solaparse y su suma de energía se oye como ruido/distorsión.
    MAX_RELEASED_VOICES = 12

    # Igual que MAX_RELEASED_VOICES pero para plucks de guitarra (ver
    # pluck_guitar_note): sin tope, retriggerar el mismo acorde rápido en
    # Generación/Círculo de quintas acumula decenas de voces vivas y su
    # render en Python puro (no vectorizado) satura la CPU del hilo de audio.
    # Medido: 16 voces ya consume ~20ms de un presupuesto de ~21ms/callback
    # (bloque 1024 @48kHz) sin margen para nada más; 8 deja un margen real
    # (~13ms) y sigue permitiendo que un acorde nuevo suene mientras se apaga
    # el anterior.
    MAX_GUITAR_VOICES = 8

    def note_off(self, note: int, fast: bool = False) -> None:
        """`fast=True` usa un release corto (~380ms) en vez del normal (1.4-2.2s).

        Pensado para previews cortos de acorde completo (p. ej. círculo de
        quintas): ahí no interesa el timbre sostenido de una nota real, y
        varios acordes cambiando rápido con release largo acumulan muchas
        voces solapadas cuya suma se oye como ruido.
        """
        fade_samples = int(0.080 * self.sample_rate)  # 80 ms smoothstep fade-out
        with self.lock:
            voice = self.voices.get(note)
            if voice is not None:
                if not voice.released:
                    # Solo (re)iniciar la cola de release la primera vez: si
                    # la voz ya estaba soltándose y se vuelve a llamar
                    # note_off (p. ej. release normal seguido de un release
                    # rápido), reiniciar release_samples/release_peak_set
                    # fuerza un recálculo del pico de referencia a partir del
                    # nivel de "sostenido" en vez del nivel real ya decaído,
                    # produciendo un salto de amplitud audible como click.
                    voice.released = True
                    voice.release_samples = 0
                    voice.release_peak_set = False
                if fast:
                    voice.fast_release = True
            released_voices = [v for v in self.voices.values() if v.released]
            excess = len(released_voices) - self.MAX_RELEASED_VOICES
            if excess > 0:
                released_voices.sort(key=lambda v: v.release_samples, reverse=True)
                for old_voice in released_voices[:excess]:
                    old_voice.fast_release = True
            for sample_voice in self.sample_voices:
                if sample_voice.note == note and sample_voice.fade_out_total == 0:
                    if sample_voice.attack_samples > 0 and sample_voice.rendered_samples < sample_voice.attack_samples:
                        t = float(sample_voice.rendered_samples) / sample_voice.attack_samples
                        sample_voice.amplitude_cap = t * t * (3.0 - 2.0 * t)
                    sample_voice.fade_out_total = fade_samples
                    sample_voice.fade_out_remaining = fade_samples

    def metronome_click(self, accent: bool = False, bar: bool = False, volume_scale: float = 1.0) -> None:
        try:
            self.ensure_started()
        except Exception:
            return
        with self.lock:
            level_gain = max(0.0, min(1.0, float(volume_scale)))
            if level_gain <= 0.0:
                return
            level = 2 if bar else (1 if accent else 0)
            vlog(
                "audio",
                "metronome_click: accent=%s bar=%s level=%s volume_scale=%s",
                accent,
                bar,
                level,
                volume_scale,
            )
            if self.metronome_sample is not None and len(self.metronome_sample) > 0:
                if level >= 2 and self.metronome_sample_bar is not None:
                    sample = self.metronome_sample_bar
                    gain = 1.02
                elif level == 1 and self.metronome_sample_accent is not None:
                    sample = self.metronome_sample_accent
                    gain = 0.96
                else:
                    sample = self.metronome_sample
                    gain = 0.82
                self.click_voices.append(
                    ClickVoice(
                        accent_level=level,
                        sample=sample,
                        sample_pos=0,
                        sample_gain=gain * level_gain,
                        age_samples=0,
                    )
                )
            else:
                self.click_voices.append(ClickVoice(accent_level=level, sample_gain=level_gain, age_samples=0))

    def pluck_guitar_note(self, note: int, velocity: int = 100, duration_seconds: float = 1.6) -> None:
        try:
            self.ensure_started()
        except Exception:
            return
        vlog(
            "audio",
            "pluck_guitar_note: note=%s velocity=%s duration=%s preset=%s",
            note,
            velocity,
            duration_seconds,
            self.guitar_preset,
        )
        self._mark_activity()
        # La guitarra sintética (noise+envolvente) suele quedar por debajo del
        # piano en volumen percibido. Subimos el gain para igualar la dinámica.
        # Medido con audio_engine._audio_callback en modo offline (RMS de nota
        # suelta C4 vel=108 vs piano "acoustic"): con guitar_synth_gain_scale=2
        # la guitarra sonaba ~14x más floja en RMS; 18 iguala el RMS (ratio
        # ~1.0-1.2) en los 4 presets sintéticos manteniendo pico < 0.6 (sin
        # clipping duro). No toca la muestra grabada (nylon_sample) porque
        # ese balance no se ha podido remedir aquí (requiere ffmpeg/assets).
        guitar_sample_gain_scale = 2.0
        guitar_synth_gain_scale = 18.0
        if self.guitar_preset == "nylon_sample" and self.guitar_sample_map:
            self._trigger_sample_voice(
                note=note,
                velocity=velocity,
                sample_bank=self.guitar_sample_map,
                gain_mul=0.96 * guitar_sample_gain_scale,
                decay=0.99994,
                max_seconds=max(0.3, min(4.0, duration_seconds * 1.45)),
            )
            return
        freq = self.midi_note_to_freq(note)
        period = max(8, int(round(self.sample_rate / max(40.0, freq))))
        noise = self.rng.uniform(-1.0, 1.0, period).astype(np.float32)
        env_end = 0.35
        gain_mul = 0.35 * guitar_synth_gain_scale
        decay = 0.9965 if freq < 180 else 0.9958
        duration_mul = 1.0
        # Suavizamos el “white noise” del pick para que, al tocar varios acordes,
        # no se perciba como hiss estático. Ajustado por preset para mantener carácter.
        lowpass_alpha = 0.18  # steel_clean (default)
        if self.guitar_preset == "steel_bright":
            env_end = 0.28
            gain_mul = 0.38 * guitar_synth_gain_scale
            decay = 0.9971 if freq < 180 else 0.9963
            lowpass_alpha = 0.22
        elif self.guitar_preset == "nylon_warm":
            env_end = 0.46
            gain_mul = 0.33 * guitar_synth_gain_scale
            decay = 0.9960 if freq < 180 else 0.9953
            lowpass_alpha = 0.14
        elif self.guitar_preset == "muted_short":
            env_end = 0.25
            gain_mul = 0.32 * guitar_synth_gain_scale
            decay = 0.9928 if freq < 180 else 0.9920
            duration_mul = 0.55
            lowpass_alpha = 0.10
        # Short pick envelope at start.
        noise *= np.linspace(1.0, env_end, period, dtype=np.float32)
        noise = self._one_pole_lowpass(noise, lowpass_alpha).astype(np.float32, copy=False)
        gain = max(0.08, min(0.9, velocity / 127.0)) * gain_mul
        remaining = max(1, int(duration_seconds * duration_mul * self.sample_rate))
        with self.lock:
            # A diferencia de las voces de piano (Voice/fading_voices, topadas
            # en MAX_RELEASED_VOICES), aquí no había límite: retriggerar el
            # mismo acorde repetidamente en Generación/Círculo de quintas
            # (p. ej. clics rápidos) acumulaba decenas de GuitarVoice vivas a
            # la vez (medido con --verbose: 45-50). El bucle de render de
            # cada una es Python puro (no vectorizado como el piano), así que
            # tantas voces saturan la CPU del hilo de audio y provocan
            # underruns reales ("output underflow"), oídos como un eco/ruido.
            # Se descartan las más antiguas (ya muy decaídas) para dejar
            # sitio a la nueva.
            if len(self.guitar_voices) >= self.MAX_GUITAR_VOICES:
                excess = len(self.guitar_voices) - self.MAX_GUITAR_VOICES + 1
                del self.guitar_voices[:excess]
            self.guitar_voices.append(
                GuitarVoice(
                    buffer=noise.copy(),
                    pos=0,
                    gain=gain,
                    decay=decay,
                    remaining_samples=remaining,
                )
            )

    def _load_sample_bank(self, directory: Path, note_to_filename: dict[int, str], max_seconds: float) -> dict[int, np.ndarray]:
        bank: dict[int, np.ndarray] = {}
        for note, filename in sorted(note_to_filename.items()):
            data = self._load_audio_sample(directory / filename, max_seconds=max_seconds)
            if data is not None and data.size > 0:
                bank[note] = data
        return bank

    def _load_audio_sample(self, path: Path, max_seconds: float) -> Optional[np.ndarray]:
        if not path.exists():
            return None
        try:
            out = subprocess.check_output(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-i",
                    str(path),
                    "-f",
                    "f32le",
                    "-ac",
                    "1",
                    "-ar",
                    str(self.sample_rate),
                    "-",
                ]
            )
        except Exception:
            return None
        if not out:
            return None
        data = np.frombuffer(out, dtype=np.float32).copy()
        if data.size == 0:
            return None
        peak = float(np.max(np.abs(data)))
        if peak > 0.0001:
            data = data / peak
        max_len = int(self.sample_rate * max_seconds)
        if data.size > max_len:
            data = data[:max_len]
        return data

    def _trigger_sample_voice(
        self,
        note: int,
        velocity: int,
        sample_bank: dict[int, np.ndarray],
        gain_mul: float,
        decay: float,
        max_seconds: float,
    ) -> None:
        if not sample_bank:
            return
        root_note = min(sample_bank.keys(), key=lambda candidate: abs(candidate - note))
        sample = sample_bank.get(root_note)
        if sample is None or sample.size < 2:
            return
        rate = float(2.0 ** ((note - root_note) / 12.0))
        gain = max(0.05, min(1.0, velocity / 127.0)) * gain_mul
        max_samples = max(1, int(max_seconds * self.sample_rate))
        attack_samples = int(0.010 * self.sample_rate)  # 10 ms ramp
        fade_retrigger = int(0.020 * self.sample_rate)  # 20 ms fade for same-note retrigger
        with self.lock:
            for sample_voice in self.sample_voices:
                if sample_voice.note == note and sample_voice.fade_out_total == 0:
                    sample_voice.fade_out_total = fade_retrigger
                    sample_voice.fade_out_remaining = fade_retrigger
            self.sample_voices.append(
                SampleVoice(
                    note=note,
                    buffer=sample,
                    pos=0.0,
                    step=rate,
                    gain=gain,
                    decay=decay,
                    max_samples=max_samples,
                    attack_samples=attack_samples,
                )
            )

    def _load_default_metronome_sample(self) -> Optional[np.ndarray]:
        candidates = [
            PROJECT_ROOT / "assets" / "metronome.mp3",
            PROJECT_ROOT / "assets" / "samples" / "metronome.mp3",
        ]
        sample_path = next((p for p in candidates if p.exists()), None)
        if sample_path is None:
            return None
        try:
            out = subprocess.check_output(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-i",
                    str(sample_path),
                    "-f",
                    "f32le",
                    "-ac",
                    "1",
                    "-ar",
                    str(self.sample_rate),
                    "-",
                ]
            )
        except Exception:
            return None
        if not out:
            return None
        data = np.frombuffer(out, dtype=np.float32).copy()
        if data.size == 0:
            return None
        peak = float(np.max(np.abs(data)))
        if peak > 0.0001:
            data = data / peak
        max_len = int(self.sample_rate * 0.22)
        if data.size > max_len:
            data = data[:max_len]
        return data

    def _build_accent_sample(self, sample: Optional[np.ndarray], ratio: float = 1.22) -> Optional[np.ndarray]:
        if sample is None or sample.size == 0:
            return None
        # Resample >1x to make accent slightly higher in pitch.
        x_old = np.arange(sample.size, dtype=np.float64)
        x_new = np.arange(0.0, sample.size - 1, ratio, dtype=np.float64)
        if x_new.size < 4:
            return sample.copy()
        pitched = np.interp(x_new, x_old, sample).astype(np.float32)
        peak = float(np.max(np.abs(pitched)))
        if peak > 0.0001:
            pitched = pitched / peak
        return pitched

    def _render_voice(self, voice: Voice, n: np.ndarray, frames: int) -> tuple[np.ndarray, bool]:
        """Sintetiza el bloque de audio de una voz (activa o en fading_voices).

        Devuelve (señal, terminada). `terminada=True` indica que la voz ya
        llegó a silencio y puede descartarse.
        """
        start_age = voice.age_samples
        age = (start_age + n) / self.sample_rate
        attack = 1.0 - np.exp(-age / 0.0052)

        if self.preset == "warm":
            partial_count = 6
            harmonic_shape_base = 1.15
            harmonic_shape_vel = 0.85
            decay_base = 0.24
            decay_step = 0.10
            sustain_base = 0.65
            sustain_freq = 3200.0
            release_rate = 3.9
            local_gain = 0.95
        elif self.preset == "bright":
            partial_count = 9
            harmonic_shape_base = 0.78
            harmonic_shape_vel = 0.95
            decay_base = 0.36
            decay_step = 0.14
            sustain_base = 0.9
            sustain_freq = 2200.0
            release_rate = 5.4
            local_gain = 1.05
        elif self.preset == "soft":
            partial_count = 5
            harmonic_shape_base = 1.35
            harmonic_shape_vel = 0.70
            decay_base = 0.20
            decay_step = 0.08
            sustain_base = 0.58
            sustain_freq = 3600.0
            release_rate = 3.45
            local_gain = 0.88
        else:
            partial_count = 7
            harmonic_shape_base = 0.95
            harmonic_shape_vel = 1.10
            decay_base = 0.30
            decay_step = 0.12
            sustain_base = 0.78
            sustain_freq = 2900.0
            release_rate = 4.05
            local_gain = 1.0

        # Inharmonicidad de cuerdas reales (mayor en agudos).
        b_coeff = 0.000015 + (voice.freq / 4200.0) ** 2 * 0.00022
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
                harmonic_shape = harmonic_shape_base + (harmonic_shape_vel * (1.0 - voice.brightness))
                harmonic_amp = 1.0 / (k ** harmonic_shape)
                decay_rate = decay_base + decay_step * k + 0.015 * max(0.0, voice.freq - 220.0) / 220.0
                partial_env = np.exp(-decay_rate * age)
                string_tone += harmonic_amp * np.sin(phases) * partial_env

            spectrum += string_tone

        hold_floor = 0.10 + 0.08 * (1.0 - voice.brightness)
        sustain_decay = np.exp(-(sustain_base + voice.freq / sustain_freq) * age)
        hold_env = attack * (hold_floor + (1.0 - hold_floor) * sustain_decay)

        if voice.released:
            release_age = (voice.release_samples + n) / self.sample_rate
            if not voice.release_peak_set:
                voice.release_peak = float(np.clip(hold_env[0], 1e-4, 1.0))
                voice.release_peak_set = True
            # 20.0 ≈ 380ms hasta silencio. Con 42.0 (~180ms) el propio
            # decaimiento tan rápido de una señal rica en armónicos generaba
            # un leve chasquido (un cambio de amplitud muy veloz mete energía
            # de banda ancha, percibida como click).
            effective_release_rate = 20.0 if voice.fast_release else release_rate
            # Cola solo exponencial desde el pico al soltar (no sustain × release).
            env = voice.release_peak * np.exp(-effective_release_rate * release_age)
        else:
            env = hold_env

        tone = spectrum / max(1, len(voice.detune_ratios))
        tone_signal = (tone * env * voice.velocity_gain * local_gain).astype(np.float32)

        voice.age_samples += frames
        if voice.released:
            voice.release_samples += frames

        end_env = float(env[-1]) if frames else 0.0
        done = voice.released and end_env < 0.0005
        return tone_signal, done

    def _audio_callback(self, outdata: np.ndarray, frames: int, _time, status) -> None:
        if status:
            vlog("audio", "callback status flags: %s", status)
        signal = np.zeros(frames, dtype=np.float32)

        with self.lock:
            if (
                not self.voices
                and not self.fading_voices
                and not self.click_voices
                and not self.guitar_voices
                and not self.sample_voices
            ):
                outdata.fill(0)
                return

            to_remove: list[int] = []
            n = np.arange(frames, dtype=np.float64)

            for note, voice in list(self.voices.items()):
                tone_signal, done = self._render_voice(voice, n, frames)
                signal += tone_signal
                if done:
                    to_remove.append(note)

            for note in to_remove:
                self.voices.pop(note, None)

            remaining_fading: list[Voice] = []
            for voice in self.fading_voices:
                tone_signal, done = self._render_voice(voice, n, frames)
                signal += tone_signal
                if not done:
                    remaining_fading.append(voice)
            self.fading_voices = remaining_fading

            remaining_guitars: list[GuitarVoice] = []
            # Compensación de polifonía: con guitar_synth_gain_scale alto (ver
            # pluck_guitar_note) una nota suelta suena a la par del piano,
            # pero varios rasgueos solapados (los plucks siguen sonando ~1s
            # tras soltarlos, así que cambiar de acorde rápido en
            # Generación/Círculo acumula voces) podían saturar por encima de
            # 1.0 antes del tanh (medido con trazas --verbose: picos de hasta
            # 1.2 con 10-11 voces). División por raíz del nº de voces
            # (mezcla a potencia constante) mantiene una nota sola a volumen
            # pleno y atenúa la suma cuando se acumulan varias.
            guitar_voice_divisor = max(1.0, math.sqrt(len(self.guitar_voices)))
            for gvoice in self.guitar_voices:
                if gvoice.remaining_samples <= 0 or gvoice.buffer.size < 2:
                    continue
                local = np.zeros(frames, dtype=np.float32)
                buf = gvoice.buffer
                pos = gvoice.pos
                buf_len = buf.size
                for i in range(frames):
                    if gvoice.remaining_samples <= 0:
                        break
                    nxt = (pos + 1) % buf_len
                    y = float(buf[pos])
                    new_val = np.float32((y + float(buf[nxt])) * 0.5 * gvoice.decay)
                    buf[pos] = new_val
                    local[i] = np.float32(y)
                    pos = nxt
                    gvoice.remaining_samples -= 1
                gvoice.pos = pos
                signal += local * (gvoice.gain / guitar_voice_divisor)
                if gvoice.remaining_samples > 0:
                    remaining_guitars.append(gvoice)
            self.guitar_voices = remaining_guitars

            remaining_samples: list[SampleVoice] = []
            for sample_voice in self.sample_voices:
                if sample_voice.buffer.size < 2:
                    continue
                local = np.zeros(frames, dtype=np.float32)
                buf = sample_voice.buffer
                buf_len = buf.size
                pos = sample_voice.pos
                release = sample_voice.release
                rendered = sample_voice.rendered_samples
                attack_n = sample_voice.attack_samples
                fade_total = sample_voice.fade_out_total
                fade_rem = sample_voice.fade_out_remaining
                for i in range(frames):
                    if pos >= (buf_len - 1):
                        break
                    if sample_voice.max_samples > 0 and rendered >= sample_voice.max_samples:
                        break
                    if fade_total > 0 and fade_rem <= 0:
                        break
                    idx = int(pos)
                    frac = float(pos - idx)
                    raw = (float(buf[idx]) * (1.0 - frac)) + (float(buf[idx + 1]) * frac)
                    if attack_n > 0 and rendered < attack_n:
                        t = float(rendered) / attack_n
                        ramp = min(t * t * (3.0 - 2.0 * t), sample_voice.amplitude_cap)
                    else:
                        ramp = 1.0
                    if fade_total > 0:
                        x = float(fade_rem) / fade_total
                        fade = x * x * (3.0 - 2.0 * x)
                    else:
                        fade = 1.0
                    local[i] = np.float32(raw * release * ramp * fade)
                    release *= sample_voice.decay
                    if fade_total > 0:
                        fade_rem -= 1
                    pos += sample_voice.step
                    rendered += 1
                sample_voice.pos = pos
                sample_voice.release = release
                sample_voice.rendered_samples = rendered
                sample_voice.fade_out_remaining = fade_rem
                signal += local * sample_voice.gain
                still_active = (
                    pos < (buf_len - 1)
                    and (sample_voice.max_samples <= 0 or rendered < sample_voice.max_samples)
                    and release > 0.00015
                    and not (fade_total > 0 and fade_rem <= 0)
                )
                if still_active:
                    remaining_samples.append(sample_voice)
            self.sample_voices = remaining_samples

            remaining_clicks: list[ClickVoice] = []
            for click in self.click_voices:
                if click.sample is not None:
                    start = click.sample_pos
                    end = min(start + frames, len(click.sample))
                    chunk = click.sample[start:end]
                    if chunk.size > 0:
                        signal[: chunk.size] += (chunk * click.sample_gain).astype(np.float32)
                    click.sample_pos = end
                    if click.sample_pos < len(click.sample):
                        remaining_clicks.append(click)
                else:
                    start_age = click.age_samples
                    age = (start_age + n) / self.sample_rate
                    if click.accent_level >= 2:
                        freq = 2550.0
                        decay = 78.0
                        gain = 0.34
                    elif click.accent_level == 1:
                        freq = 2200.0
                        decay = 82.0
                        gain = 0.30
                    else:
                        freq = 1500.0
                        decay = 95.0
                        gain = 0.22

                    # Fallback: click sintetico corto si no se pudo cargar el mp3.
                    burst = np.exp(-decay * age) * (
                        np.sin(2.0 * math.pi * freq * age) +
                        0.35 * np.sin(2.0 * math.pi * (freq * 2.3) * age)
                    )
                    signal += (gain * click.sample_gain * burst).astype(np.float32)

                    click.age_samples += frames
                    if (click.age_samples / self.sample_rate) < 0.06:
                        remaining_clicks.append(click)
            self.click_voices = remaining_clicks

        signal = signal * self.master_gain
        # Soft-clip en vez de np.clip duro: al disparar un acorde completo,
        # varias voces arrancan en el mismo instante y sus armónicos pueden
        # sumar picos que superan el rango; un corte brusco ahí se oye como
        # un crack/ruido. tanh comprime el pico suavemente y para señal normal
        # (|x| bajo) es prácticamente idéntico (tanh(x) ≈ x).
        signal = np.tanh(signal).astype(np.float32)
        outdata[:, 0] = signal
        if outdata.shape[1] > 1:
            outdata[:, 1] = signal
