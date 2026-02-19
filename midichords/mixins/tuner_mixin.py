from __future__ import annotations

import math
import queue
import time
import tkinter as tk
from typing import Optional

import numpy as np
import sounddevice as sd
from midichords.core.music_theory import WHITE_PCS

try:
    import aubio  # type: ignore
except Exception:
    aubio = None


class TunerMixin:
    def _tuner_tuning_def(self) -> dict:
        for tuning in self.tuner_tuning_defs:
            if str(tuning["key"]) == self.tuner_tuning_key:
                return tuning
        return self.tuner_tuning_defs[0]
    def _tuner_tuning_display_name(self) -> str:
        language = str(self.config_data.get("language", "es"))
        tuning = self._tuner_tuning_def()
        return str(tuning["es"] if language == "es" else tuning["en"])
    def _guitar_string_ordinal(self, index_6_to_1: int, language: str) -> str:
        num = 6 - index_6_to_1
        return f"{num}ª" if language == "es" else f"{num}th"
    def _refresh_tuner_string_buttons(self) -> None:
        if self.tuner_tab_active:
            self.redraw_staff()
    def _draw_tuner_meter(self) -> None:
        if self.tuner_tab_active:
            self.redraw_staff()
    def _draw_tuner_gain_slider(self) -> None:
        canvas = self.tuner_gain_slider_canvas
        canvas.delete("all")
        w = max(120, int(canvas.winfo_width()))
        h = max(24, int(canvas.winfo_height()))
        y = h / 2
        x1 = 12
        x2 = w - 12
        canvas.create_line(x1, y, x2, y, fill="#9aa6b2", width=4)
        ratio = self.tuner_input_gain / 200.0
        knob_x = x1 + ratio * (x2 - x1)
        r = 10
        canvas.create_oval(knob_x - r, y - r, knob_x + r, y + r, fill="#ff533d", outline="")
    def _set_tuner_input_gain(self, gain: int, save: bool = True) -> None:
        self.tuner_input_gain = max(0, min(200, int(gain)))
        self.tuner_gain_var.set(f"{self.tuner_input_gain}%")
        self._draw_tuner_gain_slider()
        if save:
            self.config_data["tuner_input_gain"] = self.tuner_input_gain
            self.save_config()
    def _on_tuner_gain_minus(self, _event: tk.Event) -> str:
        self._set_tuner_input_gain(self.tuner_input_gain - 1)
        return "break"
    def _on_tuner_gain_plus(self, _event: tk.Event) -> str:
        self._set_tuner_input_gain(self.tuner_input_gain + 1)
        return "break"
    def _on_tuner_gain_slider_interact(self, event: tk.Event) -> str:
        w = max(120, int(self.tuner_gain_slider_canvas.winfo_width()))
        x1 = 12
        x2 = w - 12
        x = min(max(float(event.x), x1), x2)
        ratio = (x - x1) / max(1.0, (x2 - x1))
        gain = int(round(ratio * 200.0))
        self._set_tuner_input_gain(gain)
        return "break"
    def _draw_tuner_spectrum_range_slider(self) -> None:
        canvas = self.tuner_spectrum_range_canvas
        canvas.delete("all")
        w = max(180, int(canvas.winfo_width()))
        h = max(24, int(canvas.winfo_height()))
        y = h / 2
        x1 = 12
        x2 = w - 12
        hz_min_limit = 0.0
        hz_max_limit = 3000.0
        canvas.create_line(x1, y, x2, y, fill="#9aa6b2", width=4)
        r1 = (float(self.tuner_spectrum_min_hz) - hz_min_limit) / (hz_max_limit - hz_min_limit)
        r2 = (float(self.tuner_spectrum_max_hz) - hz_min_limit) / (hz_max_limit - hz_min_limit)
        r1 = max(0.0, min(1.0, r1))
        r2 = max(0.0, min(1.0, r2))
        kx1 = x1 + r1 * (x2 - x1)
        kx2 = x1 + r2 * (x2 - x1)
        canvas.create_line(kx1, y, kx2, y, fill="#ff533d", width=6)
        r = 9
        canvas.create_oval(kx1 - r, y - r, kx1 + r, y + r, fill="#ff533d", outline="")
        canvas.create_oval(kx2 - r, y - r, kx2 + r, y + r, fill="#ff533d", outline="")
    def _set_tuner_spectrum_range(self, min_hz: int, max_hz: int, save: bool = True) -> None:
        hz_min_limit = 0
        hz_max_limit = 3000
        min_hz = max(hz_min_limit, min(hz_max_limit - 10, int(min_hz)))
        max_hz = max(hz_min_limit + 10, min(hz_max_limit, int(max_hz)))
        if max_hz <= min_hz + 10:
            max_hz = min(hz_max_limit, min_hz + 10)
        self.tuner_spectrum_min_hz = min_hz
        self.tuner_spectrum_max_hz = max_hz
        self.tuner_spectrum_range_var.set(f"{self.tuner_spectrum_min_hz} - {self.tuner_spectrum_max_hz} Hz")
        self._draw_tuner_spectrum_range_slider()
        if save:
            self.config_data["tuner_spectrum_min_hz"] = self.tuner_spectrum_min_hz
            self.config_data["tuner_spectrum_max_hz"] = self.tuner_spectrum_max_hz
            self.save_config()
        if self.tuner_tab_active:
            self._draw_tuner_spectrum()
    def _tuner_spectrum_hz_from_x(self, x: float) -> int:
        w = max(180, int(self.tuner_spectrum_range_canvas.winfo_width()))
        x1 = 12.0
        x2 = float(w - 12)
        xx = min(max(float(x), x1), x2)
        ratio = (xx - x1) / max(1.0, (x2 - x1))
        return int(round(0.0 + ratio * 3000.0))
    def _on_tuner_spectrum_range_press(self, event: tk.Event) -> str:
        w = max(180, int(self.tuner_spectrum_range_canvas.winfo_width()))
        x1 = 12.0
        x2 = float(w - 12)
        r1 = float(self.tuner_spectrum_min_hz) / 3000.0
        r2 = float(self.tuner_spectrum_max_hz) / 3000.0
        kx1 = x1 + r1 * (x2 - x1)
        kx2 = x1 + r2 * (x2 - x1)
        if abs(float(event.x) - kx1) <= abs(float(event.x) - kx2):
            self.tuner_spectrum_dragging = "min"
        else:
            self.tuner_spectrum_dragging = "max"
        return self._on_tuner_spectrum_range_drag(event)
    def _on_tuner_spectrum_range_drag(self, event: tk.Event) -> str:
        if self.tuner_spectrum_dragging is None:
            return "break"
        hz = self._tuner_spectrum_hz_from_x(float(event.x))
        if self.tuner_spectrum_dragging == "min":
            self._set_tuner_spectrum_range(hz, self.tuner_spectrum_max_hz)
        else:
            self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz, hz)
        return "break"
    def _on_tuner_spectrum_range_release(self, _event: tk.Event) -> str:
        self.tuner_spectrum_dragging = None
        return "break"
    def _on_tuner_spectrum_min_minus(self, _event: tk.Event) -> str:
        self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz - 1, self.tuner_spectrum_max_hz)
        return "break"
    def _on_tuner_spectrum_max_minus(self, _event: tk.Event) -> str:
        self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz, self.tuner_spectrum_max_hz - 1)
        return "break"
    def _on_tuner_spectrum_min_plus(self, _event: tk.Event) -> str:
        self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz + 1, self.tuner_spectrum_max_hz)
        return "break"
    def _on_tuner_spectrum_max_plus(self, _event: tk.Event) -> str:
        self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz, self.tuner_spectrum_max_hz + 1)
        return "break"
    def _refresh_tuner_ui(self) -> None:
        self.tuner_tuning_btn.set_text(self._tuner_tuning_display_name())
        if hasattr(self, "tuner_input_combo"):
            vals = [""] + self.audio_input_names
            self.tuner_input_combo.configure(values=vals)
            if self.tuner_input_name in vals:
                self.tuner_input_var.set(self.tuner_input_name)
        if self.tuner_current_string_idx is None:
            self.tuner_status_var.set("-")
        else:
            if self.tuner_detected_note_midi is not None:
                note_name = self.note_name(int(self.tuner_detected_note_midi), with_octave=False)
            else:
                tuning = self._tuner_tuning_def()
                note = int(tuning["notes"][self.tuner_current_string_idx])
                note_name = self.note_name(note, with_octave=False)
            self.tuner_status_var.set(f"{note_name}  {self.tuner_current_freq:.1f} Hz")
        self._refresh_tuner_string_buttons()
        self._set_tuner_input_gain(self.tuner_input_gain, save=False)
        self._set_tuner_spectrum_range(self.tuner_spectrum_min_hz, self.tuner_spectrum_max_hz, save=False)
        if self.tuner_tab_active:
            self.redraw_staff()
    def _on_tuner_input_changed(self, _event: Optional[tk.Event] = None) -> None:
        self.tuner_input_name = self.tuner_input_var.get().strip()
        self.config_data["tuner_input"] = self.tuner_input_name
        self.save_config()
        if self.tuner_running:
            self._start_tuner_stream()
    def _play_tuner_string(self, idx: int) -> None:
        tuning = self._tuner_tuning_def()
        notes = list(tuning["notes"])
        if idx < 0 or idx >= len(notes):
            return
        note = int(notes[idx])
        self.tuner_current_string_idx = idx
        self.tuner_current_cents = 0.0
        self.tuner_current_freq = self.audio_engine.midi_note_to_freq(note)
        self.tuner_detected_note_midi = note
        self.tuner_last_candidate_midi = note
        self.tuner_note_stable_count = 0
        self.tuner_button_active_until[idx] = time.monotonic() + 0.9
        self.tuner_reference_note = note
        if self.tuner_reference_off_after_id is not None:
            try:
                self.after_cancel(self.tuner_reference_off_after_id)
            except Exception:
                pass
            self.tuner_reference_off_after_id = None
        self.audio_engine.pluck_guitar_note(note, velocity=106, duration_seconds=1.8)
        self.tuner_reference_off_after_id = self.after(750, self._stop_tuner_reference_note)
        self._refresh_tuner_ui()
        self.redraw_keyboard()
    def _stop_tuner_reference_note(self) -> None:
        self.tuner_reference_off_after_id = None
        self.tuner_reference_note = None
        if self.tuner_tab_active:
            self.redraw_keyboard()
    def _toggle_tuner(self) -> None:
        if not self.tuner_tab_active:
            return
        if self.tuner_running:
            self._stop_tuner_stream()
        else:
            self._start_tuner_stream()
        self._refresh_tuner_ui()
    def _tuner_audio_callback(self, indata: np.ndarray, _frames: int, _time, _status) -> None:
        try:
            mono = np.asarray(indata[:, 0], dtype=np.float32).copy()
            self.tuner_audio_queue.put_nowait(mono)
        except Exception:
            pass
    def _start_tuner_stream(self) -> None:
        self._stop_tuner_stream()
        device_index = self.audio_input_map.get(self.tuner_input_name)
        try:
            self._init_tuner_pitch_detector()
            self.tuner_stream = sd.InputStream(
                samplerate=48000,
                channels=1,
                device=device_index,
                dtype="float32",
                blocksize=0,
                latency="low",
                callback=self._tuner_audio_callback,
            )
            self.tuner_stream.start()
            self.tuner_running = True
            self.tuner_audio_buffer = np.zeros(0, dtype=np.float32)
            self.tuner_last_analysis_ts = 0.0
        except Exception as exc:
            self.tuner_running = False
            self.tuner_stream = None
            self.status_var.set(f"{self.tr('status_audio_error')}: {exc}")
    def _stop_tuner_stream(self) -> None:
        self.tuner_running = False
        self.tuner_pitch_detector = None
        if self.tuner_stream is not None:
            try:
                self.tuner_stream.stop()
            except Exception:
                pass
            try:
                self.tuner_stream.close()
            except Exception:
                pass
            self.tuner_stream = None
        self.tuner_audio_buffer = np.zeros(0, dtype=np.float32)
        self.tuner_current_string_idx = None
        self.tuner_current_cents = 0.0
        self.tuner_current_freq = 0.0
        self.tuner_detected_note_midi = None
        self.tuner_last_candidate_midi = None
        self.tuner_note_stable_count = 0
        self.tuner_silence_frames = 0
        self.tuner_spectrum_freqs = np.zeros(0, dtype=np.float32)
        self.tuner_spectrum_mags = np.zeros(0, dtype=np.float32)
    def _estimate_pitch_hz(self, samples: np.ndarray, sample_rate: int) -> Optional[float]:
        if samples.size < 1024:
            return None
        x = samples.astype(np.float64, copy=False)
        x = x - np.mean(x)
        rms = float(np.sqrt(np.mean(x * x)))
        if rms < 0.003:
            return None
        x = x * np.hanning(x.size)
        corr = np.correlate(x, x, mode="full")[x.size - 1:]
        if corr.size < 8:
            return None
        min_lag = max(8, int(sample_rate / 420))
        max_lag = min(corr.size - 1, int(sample_rate / 70))
        if max_lag <= min_lag:
            return None
        corr[:min_lag] = 0.0
        region = corr[min_lag:max_lag + 1]
        if region.size == 0:
            return None
        rel_idx = int(np.argmax(region))
        peak_lag = min_lag + rel_idx
        peak_val = float(corr[peak_lag])
        zero = float(corr[0]) if corr[0] != 0 else 1.0
        if peak_val <= 0.0 or (peak_val / max(1e-9, zero)) < 0.10:
            return None
        if 1 <= peak_lag < corr.size - 1:
            y0 = corr[peak_lag - 1]
            y1 = corr[peak_lag]
            y2 = corr[peak_lag + 1]
            denom = (y0 - 2.0 * y1 + y2)
            if abs(denom) > 1e-12:
                peak_lag = peak_lag + float(0.5 * (y0 - y2) / denom)
        if peak_lag <= 0:
            return None
        freq = float(sample_rate / peak_lag)
        if freq < 70.0 or freq > 420.0:
            return None
        return freq
    def _init_tuner_pitch_detector(self) -> None:
        self.tuner_pitch_detector = None
        if aubio is None:
            return
        try:
            detector = aubio.pitch("yinfft", 2048, self.tuner_pitch_hop, 48000)
            detector.set_unit("Hz")
            detector.set_silence(-45)
            detector.set_tolerance(0.86)
            self.tuner_pitch_detector = detector
        except Exception:
            self.tuner_pitch_detector = None
    def _detect_tuner_pitch(self, frame: np.ndarray) -> Optional[float]:
        if frame.size < 1024:
            return None
        if self.tuner_pitch_detector is not None and aubio is not None:
            try:
                hop = int(self.tuner_pitch_hop)
                if hop <= 0:
                    hop = 256
                block = frame[-max(hop, 2048):]
                value: Optional[float] = None
                for i in range(0, len(block) - hop + 1, hop):
                    chunk = np.asarray(block[i:i + hop], dtype=np.float32)
                    hz = float(self.tuner_pitch_detector(chunk)[0])
                    if 70.0 <= hz <= 420.0:
                        value = hz
                return value
            except Exception:
                pass
        return self._estimate_pitch_hz(frame, 48000)
    def _filter_tuner_noise(self, frame: np.ndarray, sample_rate: int = 48000) -> np.ndarray:
        if frame.size < 128:
            return frame.astype(np.float32, copy=True)
        x = frame.astype(np.float64, copy=False)
        x = x - np.mean(x)
        rms = float(np.sqrt(np.mean(x * x)))
        if rms < 0.0018:
            return np.zeros_like(frame, dtype=np.float32)

        n = x.size
        window = np.hanning(n)
        spec = np.fft.rfft(x * window)
        freqs = np.fft.rfftfreq(n, d=1.0 / float(sample_rate))

        # Keep guitar-relevant band and attenuate tiny bins (spectral gate).
        band = (freqs >= 65.0) & (freqs <= 3000.0)
        mag = np.abs(spec)
        if np.any(band):
            band_mag = mag[band]
            floor = float(np.percentile(band_mag, 35))
            gate = floor * 1.8
            keep = band & (mag >= gate)
            spec[~keep] *= 0.15
        else:
            spec[:] = 0.0

        y = np.fft.irfft(spec, n=n)
        return y.astype(np.float32)
    def _process_tuner_audio(self) -> None:
        if not self.tuner_running:
            return
        has_data = False
        while True:
            try:
                chunk = self.tuner_audio_queue.get_nowait()
            except queue.Empty:
                break
            if chunk.size:
                has_data = True
                gain = max(0.0, float(self.tuner_input_gain) / 100.0)
                self.tuner_audio_buffer = np.concatenate((self.tuner_audio_buffer, (chunk * gain).astype(np.float32)))
        if self.tuner_audio_buffer.size > 12000:
            self.tuner_audio_buffer = self.tuner_audio_buffer[-12000:]
        now = time.monotonic()
        if not has_data and (now - self.tuner_last_analysis_ts) < 0.08:
            return
        if self.tuner_audio_buffer.size < 4096:
            return
        self.tuner_last_analysis_ts = now
        raw_frame = self.tuner_audio_buffer[-4096:]
        frame = self._filter_tuner_noise(raw_frame, 48000)
        self._update_tuner_spectrum(frame)
        freq = self._detect_tuner_pitch(frame)
        if freq is None:
            self.tuner_silence_frames += 1
            self.tuner_current_cents *= 0.72
            self.tuner_current_freq *= 0.75
            if self.tuner_silence_frames >= 4:
                self.tuner_current_string_idx = None
                self.tuner_current_cents = 0.0
                self.tuner_current_freq = 0.0
                self.tuner_detected_note_midi = None
                self.tuner_last_candidate_midi = None
                self.tuner_note_stable_count = 0
            self._refresh_tuner_ui()
            return
        self.tuner_silence_frames = 0
        tuning = self._tuner_tuning_def()
        notes = list(tuning["notes"])
        best_idx = 0
        best_cents = 9999.0
        for i, note in enumerate(notes):
            target = self.audio_engine.midi_note_to_freq(int(note))
            cents = 1200.0 * math.log2(max(1e-9, freq) / target)
            if abs(cents) < abs(best_cents):
                best_cents = cents
                best_idx = i
        # Smooth freq to reduce jitter.
        if self.tuner_current_freq <= 0.0:
            self.tuner_current_freq = freq
        else:
            self.tuner_current_freq = (self.tuner_current_freq * 0.82) + (freq * 0.18)

        detected_midi = int(round(69.0 + 12.0 * math.log2(max(1e-9, freq) / 440.0)))
        candidate_midi = max(0, min(127, detected_midi))
        if candidate_midi == self.tuner_last_candidate_midi:
            self.tuner_note_stable_count += 1
        else:
            self.tuner_last_candidate_midi = candidate_midi
            self.tuner_note_stable_count = 1

        if self.tuner_detected_note_midi is None:
            self.tuner_detected_note_midi = candidate_midi
        else:
            # Hysteresis: only change note after a few stable frames.
            if candidate_midi != self.tuner_detected_note_midi and self.tuner_note_stable_count >= 3:
                self.tuner_detected_note_midi = candidate_midi

        self.tuner_current_string_idx = best_idx
        target_cents = max(-50.0, min(50.0, float(best_cents)))
        self.tuner_current_cents = (self.tuner_current_cents * 0.78) + (target_cents * 0.22)
        self.tuner_button_active_until[best_idx] = time.monotonic() + 0.20
        self._refresh_tuner_ui()
    def _update_tuner_spectrum(self, frame: np.ndarray) -> None:
        if frame.size < 1024:
            return
        n = min(8192, int(frame.size))
        data = frame[-n:].astype(np.float64, copy=False)
        data = data - np.mean(data)
        window = np.hanning(n)
        spec = np.abs(np.fft.rfft(data * window))
        freqs = np.fft.rfftfreq(n, d=1.0 / 48000.0)
        fmin = float(self.tuner_spectrum_min_hz)
        fmax = float(self.tuner_spectrum_max_hz)
        mask = (freqs >= fmin) & (freqs <= fmax)
        if not np.any(mask):
            self.tuner_spectrum_freqs = np.zeros(0, dtype=np.float32)
            self.tuner_spectrum_mags = np.zeros(0, dtype=np.float32)
            return
        sel_freqs = freqs[mask].astype(np.float32)
        sel_spec = spec[mask]
        db = 20.0 * np.log10(sel_spec + 1e-9)
        db_min = float(np.percentile(db, 8))
        db_max = float(np.percentile(db, 99))
        if db_max - db_min < 1e-6:
            norm = np.zeros_like(db, dtype=np.float32)
        else:
            norm = np.clip((db - db_min) / (db_max - db_min), 0.0, 1.0).astype(np.float32)
        # Visual smoothing to reduce jitter from residual noise.
        if norm.size >= 7:
            kernel = np.ones(7, dtype=np.float32) / 7.0
            norm = np.convolve(norm, kernel, mode="same").astype(np.float32)
        self.tuner_spectrum_freqs = sel_freqs
        self.tuner_spectrum_mags = norm
        if self.tuner_tab_active:
            self._draw_tuner_spectrum()
    def _draw_tuner_spectrum(self) -> None:
        canvas = self.tuner_spectrum_canvas
        if not self.tuner_tab_active:
            canvas.delete("all")
            return
        canvas.delete("all")
        w = max(320, int(canvas.winfo_width()))
        h = max(140, int(canvas.winfo_height()))
        canvas.create_rectangle(0, 0, w, h, fill="#0b0c10", outline="")
        pad_l = 42.0
        pad_r = 14.0
        pad_t = 12.0
        pad_b = 30.0
        x1, x2 = pad_l, w - pad_r
        y1, y2 = pad_t, h - pad_b
        canvas.create_rectangle(x1, y1, x2, y2, outline="#465062", width=1, fill="#10131a")

        fmin = float(self.tuner_spectrum_min_hz)
        fmax = float(self.tuner_spectrum_max_hz)
        if fmax <= fmin + 1.0:
            fmax = fmin + 1.0

        # Log scale cannot represent 0 Hz, so map from at least 1 Hz for drawing.
        fmin_log = max(1.0, fmin)
        log_min = math.log10(fmin_log)
        log_max = math.log10(fmax)

        def fx(freq: float) -> float:
            safe_f = max(fmin_log, min(fmax, float(freq)))
            ratio = (math.log10(safe_f) - log_min) / max(1e-6, (log_max - log_min))
            ratio = max(0.0, min(1.0, ratio))
            return x1 + ratio * (x2 - x1)

        # Grid and Hz labels in log domain.
        tick_hz = [70, 80, 90, 100, 120, 140, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1400, 1600, 2000, 2500, 3000]
        major_hz = {100, 200, 400, 800, 1000}
        for hz in tick_hz:
            if hz < fmin or hz > fmax:
                continue
            x = fx(float(hz))
            main = hz in major_hz
            canvas.create_line(x, y1, x, y2, fill="#293140" if main else "#1f2531", width=1)
            if main:
                canvas.create_text(x, y2 + 12, text=str(hz), fill="#8f98a8", font=("Helvetica", 8))
        canvas.create_text((x1 + x2) / 2, h - 8, text="Hz", fill="#a0a8b7", font=("Helvetica", 9, "bold"))

        # All chromatic notes in selected range.
        min_midi = max(0, int(math.floor(69.0 + 12.0 * math.log2(max(1e-9, fmin) / 440.0))) - 1)
        max_midi = min(127, int(math.ceil(69.0 + 12.0 * math.log2(max(1e-9, fmax) / 440.0))) + 1)
        for midi in range(min_midi, max_midi + 1):
            freq = self.audio_engine.midi_note_to_freq(midi)
            if freq < fmin or freq > fmax:
                continue
            x = fx(freq)
            is_natural = (midi % 12) in WHITE_PCS
            line_color = "#ff9f2a" if is_natural else "#8a5f22"
            canvas.create_line(x, y1, x, y2, fill=line_color, width=1)
            # Stagger labels to reduce overlap in narrow ranges.
            label_y = y1 + (8 if (midi % 2 == 0) else 18)
            label_color = "#ffbf6c" if is_natural else "#b58a4f"
            canvas.create_text(
                x,
                label_y,
                text=self.note_name(midi, with_octave=False),
                fill=label_color,
                font=("Helvetica", 7, "bold"),
            )

        if self.tuner_spectrum_freqs.size >= 2 and self.tuner_spectrum_mags.size == self.tuner_spectrum_freqs.size:
            pts: list[float] = []
            for f, mag in zip(self.tuner_spectrum_freqs.tolist(), self.tuner_spectrum_mags.tolist()):
                x = fx(float(f))
                y = y2 - float(mag) * (y2 - y1)
                pts.extend([x, y])
            if len(pts) >= 4:
                canvas.create_line(*pts, fill="#50c6ff", width=1.6, smooth=True)
    def _set_tuner_spectrum_visible(self, visible: bool) -> None:
        if visible:
            if not self.tuner_spectrum_canvas.winfo_ismapped():
                self.tuner_spectrum_canvas.pack(fill=tk.X, expand=False)
            self._draw_tuner_spectrum()
        else:
            if self.tuner_spectrum_canvas.winfo_ismapped():
                self.tuner_spectrum_canvas.pack_forget()
        self._fit_instrument_panel_height()
    def _tuner_string_at_position(self, x: float, y: float) -> Optional[int]:
        if not self.tuner_tab_active:
            return None
        for idx, x1, y1, x2, y2 in self.tuner_string_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return idx
        return None
