"""Modo círculo de quintas (escritorio), alineado con la web."""

from __future__ import annotations

from typing import Any, Optional

import midichords.qt.tk_compat as tk

from midichords.core.music_service import generate_chord
from midichords.ui.circle_of_fifths import (
    CircleDrawState,
    circle_chord_root_pc_from_click,
    circle_chord_shift_click_is_diatonic,
    circle_fifths_click_inner_minor_band,
    circle_major_tonic_pc_for_theory,
    diatonic_triad_suffix_major_key,
    diatonic_triad_suffix_natural_minor_key,
    draw_circle_of_fifths,
)


class CircleFifthsMixin:
    circle_canvas: tk.Canvas
    _circle_draw_after_id: Optional[str] = None
    _circle_generated_chord: Optional[dict[str, Any]] = None

    def _circle_note_name_pc(self, pc: int) -> str:
        return self.note_name(60 + (int(pc) % 12), with_octave=False)

    def _circle_schedule_redraw(self) -> None:
        if self._circle_draw_after_id is not None:
            try:
                self.after_cancel(self._circle_draw_after_id)
            except Exception:
                pass
            self._circle_draw_after_id = None

        def _do() -> None:
            self._circle_draw_after_id = None
            if not getattr(self, "circle_fifths_tab_active", False):
                return
            self._circle_redraw_canvas()

        self._circle_draw_after_id = self.after(0, _do)

    def _circle_redraw_canvas(self) -> None:
        if not getattr(self, "circle_fifths_tab_active", False):
            return
        canvas = getattr(self, "circle_canvas", None)
        if canvas is None:
            return
        try:
            w = max(260, int(canvas.winfo_width()))
            h = max(260, int(canvas.winfo_height()))
        except Exception:
            w, h = 480, 480
        state = CircleDrawState(
            circle_tonic_pc=int(getattr(self, "circle_tonic_pc", 0)),
            circle_key_mode=str(getattr(self, "circle_key_mode", "major")),
            circle_chord_root_pc=int(getattr(self, "circle_chord_root_pc", 0)),
            generated_chord=self._circle_generated_chord,
        )
        draw_circle_of_fifths(
            canvas,
            width=w,
            height=h,
            state=state,
            note_name_fn=self._circle_note_name_pc,
            font_family=getattr(self, "ui_font_family", "Helvetica"),
            tag="circle_fifths",
        )

    def _on_circle_canvas_configure(self, _event: tk.Event) -> None:
        self._circle_schedule_redraw()

    def _on_circle_canvas_click(self, event: tk.Event) -> None:
        if not getattr(self, "circle_fifths_tab_active", False):
            return
        canvas = self.circle_canvas
        w = max(1, int(canvas.winfo_width()))
        h = max(1, int(canvas.winfo_height()))
        cx = w / 2
        cy = h / 2
        x = float(event.x)
        y = float(event.y)
        st = int(getattr(event, "state", 0))
        shift = bool(st & 0x0001) or bool(st & 0x20000)
        pc = circle_chord_root_pc_from_click(float(w), float(h), cx, cy, x, y, shift)
        if pc is None:
            return
        theory_tonic = circle_major_tonic_pc_for_theory(self.circle_tonic_pc, self.circle_key_mode)
        if shift:
            if not circle_chord_shift_click_is_diatonic(
                theory_tonic,
                float(w),
                float(h),
                cx,
                cy,
                x,
                y,
                circle_key_mode=self.circle_key_mode,
                circle_tonic_pc=self.circle_tonic_pc,
            ):
                return
            self.circle_chord_root_pc = int(pc)
        else:
            band = circle_fifths_click_inner_minor_band(float(w), float(h), cx, cy, x, y)
            if band is None:
                return
            self.circle_key_mode = "minor" if band else "major"
            self.circle_tonic_pc = int(pc)
            self.circle_chord_root_pc = int(pc)
        self._circle_run_generate(play_preview=True)

    def _circle_run_generate(self, *, play_preview: bool = False) -> None:
        root_pc = int(self.circle_chord_root_pc) % 12
        tonic_pc = circle_major_tonic_pc_for_theory(self.circle_tonic_pc, self.circle_key_mode)
        if self.circle_key_mode == "minor":
            mt = int(self.circle_tonic_pc) % 12
            suf, _iv, _r = diatonic_triad_suffix_natural_minor_key(mt, root_pc)
            suffix = suf or ""
        else:
            _suf, _deg = diatonic_triad_suffix_major_key(tonic_pc, root_pc)
            suffix = _suf or ""
        lang = str(self.config_data.get("language", "es"))
        prefer_flat = self.note_accidental == "flat"
        out = generate_chord(
            root_pc=root_pc,
            suffix=suffix,
            inversion=0,
            language=lang,
            prefer_flat=prefer_flat,
        )
        self._circle_generated_chord = dict(out)
        self.generation_root_pc = root_pc
        self.generation_pattern_suffix = str(out.get("suffix") or "")
        self.generation_inversion = 0
        self._refresh_generation_selection_buttons()
        self._update_generation_preview()
        if play_preview:
            self._preview_generated_chord_short()
        self._circle_schedule_redraw()
