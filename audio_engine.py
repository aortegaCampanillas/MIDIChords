from __future__ import annotations

import math
import threading
from dataclasses import dataclass
from typing import Optional

import numpy as np
import sounddevice as sd


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


class PianoAudioEngine:
    def __init__(self, sample_rate: int = 48000) -> None:
        self.sample_rate = sample_rate
        self.channels = 2
        self.master_gain = 0.14
        self.preset = "acoustic"
        self.stream: Optional[sd.OutputStream] = None
        self.lock = threading.Lock()
        self.voices: dict[int, Voice] = {}

    def set_preset(self, preset: str) -> None:
        if preset not in {"acoustic", "warm", "bright", "soft"}:
            preset = "acoustic"
        self.preset = preset

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

                if self.preset == "warm":
                    partial_count = 6
                    harmonic_shape_base = 1.15
                    harmonic_shape_vel = 0.85
                    decay_base = 0.24
                    decay_step = 0.10
                    sustain_base = 0.65
                    sustain_freq = 3200.0
                    release_rate = 5.2
                    local_gain = 0.95
                elif self.preset == "bright":
                    partial_count = 9
                    harmonic_shape_base = 0.78
                    harmonic_shape_vel = 0.95
                    decay_base = 0.36
                    decay_step = 0.14
                    sustain_base = 0.9
                    sustain_freq = 2200.0
                    release_rate = 7.2
                    local_gain = 1.05
                elif self.preset == "soft":
                    partial_count = 5
                    harmonic_shape_base = 1.35
                    harmonic_shape_vel = 0.70
                    decay_base = 0.20
                    decay_step = 0.08
                    sustain_base = 0.58
                    sustain_freq = 3600.0
                    release_rate = 4.6
                    local_gain = 0.88
                else:
                    partial_count = 7
                    harmonic_shape_base = 0.95
                    harmonic_shape_vel = 1.10
                    decay_base = 0.30
                    decay_step = 0.12
                    sustain_base = 0.78
                    sustain_freq = 2900.0
                    release_rate = 6.5
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
                    release_env = np.exp(-release_rate * release_age)
                    env = hold_env * release_env
                else:
                    env = hold_env

                tone = spectrum / max(1, len(voice.detune_ratios))
                signal += (tone * env * voice.velocity_gain * local_gain).astype(np.float32)

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
