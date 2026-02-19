from __future__ import annotations

import math
import time
import tkinter as tk
from tkinter import ttk


class MetronomeMixin:
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
    def _metronome_preset_text(self, bpm: int, language: str) -> str:
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
        self.metronome_play_btn.set_playing(self.metronome_running)
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
    def _format_timer_mmss(self, total_seconds: float) -> str:
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
    def _finalize_metronome_space_release(self) -> None:
        self.metronome_space_release_after_id = None
        self.metronome_space_pressed = False
    def _play_metronome_click(self, accent: bool) -> None:
        if self.scale_play_mode != "metronome":
            return
        self.audio_engine.metronome_click(accent=accent, bar=False)
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
