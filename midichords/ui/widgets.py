from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Callable, Optional


def _resolve_canvas_bg(master: tk.Misc, fallback: str) -> str:
    current: Optional[tk.Misc] = master
    while isinstance(current, tk.Misc):
        try:
            value = str(current.cget("background"))
            if value:
                current.winfo_rgb(value)
                return value
        except Exception:
            pass
        parent = getattr(current, "master", None)
        if not isinstance(parent, tk.Misc):
            break
        current = parent
    return fallback


def _pick_font_family(root: tk.Misc, preferred: list[str], fallback: str) -> str:
    try:
        available = {name.lower(): name for name in tkfont.families(root)}
    except Exception:
        return fallback
    for name in preferred:
        match = available.get(name.lower())
        if match:
            return match
    return fallback


class RoundedChoiceButton(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        width: int = 70,
        height: int = 30,
        radius: int = 12,
    ) -> None:
        parent_bg = _resolve_canvas_bg(master, "#f0f0f0")
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            highlightbackground=parent_bg,
            highlightcolor=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._selected = False
        self._radius = radius
        self._shape_id: Optional[int] = None
        self._label_id: Optional[int] = None
        self._hover = False
        self._font_family = _pick_font_family(self, ["Avenir Next", "SF Pro Text", "Segoe UI", "Helvetica Neue"], "Helvetica")

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        if self._label_id is not None:
            self.itemconfigure(self._label_id, text=self._text)

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self._redraw()

    def _on_click(self, _event: tk.Event) -> None:
        self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._redraw()

    def _rounded_points(self, x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
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

    def _redraw(self) -> None:
        parent_bg = _resolve_canvas_bg(self.master, str(self.cget("bg")))
        if parent_bg != str(self.cget("bg")):
            self.configure(bg=parent_bg, highlightbackground=parent_bg, highlightcolor=parent_bg)
        self.delete("all")
        w = max(4, int(self.winfo_width()))
        h = max(4, int(self.winfo_height()))
        r = max(4, min(self._radius, int(min(w, h) / 2) - 1))

        if self._selected:
            fill = "#303842"
            outline = "#f3bf2f"
            text_color = "#f0f2f5"
        else:
            fill = "#252b33" if not self._hover else "#2c333d"
            outline = "#444b56"
            text_color = "#c8ced7"

        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self._shape_id = self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=fill,
            outline=outline,
            width=2.0,
        )
        self._label_id = self.create_text(
            14,
            h / 2,
            text=self._text,
            fill=text_color,
            font=(self._font_family, 12, "bold"),
            anchor="w",
        )


class RoundedPanel(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        *,
        radius: int = 16,
        bg_color: str = "#2f3f56",
        border_color: str = "#56627a",
        border_width: float = 1.2,
        padding: tuple[int, int, int, int] = (12, 12, 12, 12),
    ) -> None:
        parent_bg = _resolve_canvas_bg(master, "#1b2534")
        super().__init__(
            master,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            highlightbackground=parent_bg,
            highlightcolor=parent_bg,
        )
        self._radius = radius
        self._bg_color = bg_color
        self._border_color = border_color
        self._border_width = border_width
        self._padding = padding
        self.content = tk.Frame(self, bg=self._bg_color, bd=0, highlightthickness=0)
        self._content_window = self.create_window(0, 0, anchor="nw", window=self.content)
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    def _rounded_points(self, x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
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

    def _redraw(self) -> None:
        parent_bg = _resolve_canvas_bg(self.master, str(self.cget("bg")))
        if parent_bg != str(self.cget("bg")):
            self.configure(bg=parent_bg, highlightbackground=parent_bg, highlightcolor=parent_bg)
        self.delete("panel")
        w = max(4, int(self.winfo_width()))
        h = max(4, int(self.winfo_height()))
        r = max(6, min(self._radius, int(min(w, h) / 2) - 1))
        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=self._bg_color,
            outline=self._border_color,
            width=self._border_width,
            tags="panel",
        )
        left, top, right, bottom = self._padding
        inner_w = max(1, w - left - right)
        inner_h = max(1, h - top - bottom)
        self.coords(self._content_window, left, top)
        self.itemconfigure(self._content_window, width=inner_w, height=inner_h)


class GreenRoundedButton(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        width: int = 130,
        height: int = 52,
        radius: int = 24,
    ) -> None:
        parent_bg = _resolve_canvas_bg(master, "#1f2329")
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            highlightbackground=parent_bg,
            highlightcolor=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._radius = radius
        self._hover = False
        self._selected = False
        self._font_family = _pick_font_family(self, ["Avenir Next", "SF Pro Text", "Segoe UI", "Helvetica Neue"], "Helvetica")

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        self._redraw()

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self._redraw()

    def _on_click(self, _event: tk.Event) -> None:
        self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._redraw()

    def _rounded_points(self, x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
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

    def _redraw(self) -> None:
        parent_bg = _resolve_canvas_bg(self.master, str(self.cget("bg")))
        if parent_bg != str(self.cget("bg")):
            self.configure(bg=parent_bg, highlightbackground=parent_bg, highlightcolor=parent_bg)
        self.delete("all")
        w = max(8, int(self.winfo_width()))
        h = max(8, int(self.winfo_height()))
        r = max(6, min(self._radius, int(min(w, h) / 2) - 1))
        if self._selected:
            fill = "#12c37d" if not self._hover else "#10b574"
            outline = "#11a96c"
        else:
            fill = "#0eaf70" if not self._hover else "#0da267"
            outline = "#0f9460"
        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=fill,
            outline=outline,
            width=1.5,
        )
        if "♭" in self._text and self._text.count("♭") == 1 and " " not in self._text:
            base_text = self._text.replace("♭", "")
            if base_text:
                base_font = tkfont.Font(family=self._font_family, size=16, weight="bold")
                acc_font_size = max(10, int(round(16 * 0.68)))
                acc_font = tkfont.Font(family=self._font_family, size=acc_font_size, weight="bold")
                base_w = float(base_font.measure(base_text))
                acc_w = float(acc_font.measure("♭"))
                group_w = base_w + (acc_w * 0.65)
                left = (w - group_w) / 2.0
                base_x = left + (base_w / 2.0)
                acc_x = left + base_w + (acc_w * 0.32)
                self.create_text(
                    base_x,
                    h / 2,
                    text=base_text,
                    fill="#ffffff",
                    font=(self._font_family, 16, "bold"),
                    anchor="center",
                )
                self.create_text(
                    acc_x,
                    (h / 2) - 8,
                    text="♭",
                    fill="#ffffff",
                    font=(self._font_family, acc_font_size, "bold"),
                    anchor="center",
                )
            else:
                self.create_text(
                    w / 2,
                    h / 2,
                    text=self._text,
                    fill="#ffffff",
                    font=(self._font_family, 16, "bold"),
                    anchor="center",
                )
        else:
            self.create_text(
                w / 2,
                h / 2,
                text=self._text,
                fill="#ffffff",
                font=(self._font_family, 16, "bold"),
                anchor="center",
            )


class GrayRoundedButton(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None],
        width: int = 120,
        height: int = 72,
        radius: int = 26,
        font_size: int = 22,
        text_color: str = "#dde2e8",
        selected_text_color: str = "#16dfa0",
        selected_fill_color: str = "#f3bf2f",
        selected_outline_color: str = "#f3bf2f",
        selected_border_width: float = 2.2,
    ) -> None:
        parent_bg = _resolve_canvas_bg(master, "#2a2f36")
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            highlightbackground=parent_bg,
            highlightcolor=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._radius = radius
        self._font_size = font_size
        self._text_color = text_color
        self._selected_text_color = selected_text_color
        self._selected_fill_color = selected_fill_color
        self._selected_outline_color = selected_outline_color
        self._selected_border_width = float(selected_border_width)
        self._hover = False
        self._selected = False
        self._font_family = _pick_font_family(self, ["Avenir Next", "SF Pro Text", "Segoe UI", "Helvetica Neue"], "Helvetica")

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        self._redraw()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._redraw()

    def _on_click(self, _event: tk.Event) -> None:
        self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._redraw()

    def _rounded_points(self, x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
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

    def _redraw(self) -> None:
        parent_bg = _resolve_canvas_bg(self.master, str(self.cget("bg")))
        if parent_bg != str(self.cget("bg")):
            self.configure(bg=parent_bg, highlightbackground=parent_bg, highlightcolor=parent_bg)
        self.delete("all")
        w = max(8, int(self.winfo_width()))
        h = max(8, int(self.winfo_height()))
        r = max(6, min(self._radius, int(min(w, h) / 2) - 1))

        if self._selected:
            outline = self._selected_outline_color
            fill = self._selected_fill_color
            text_color = self._selected_text_color
            border_w = self._selected_border_width
        else:
            outline = "#4a5360"
            fill = "#262c34" if not self._hover else "#2b323b"
            text_color = self._text_color
            border_w = 1.6

        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=fill,
            outline=outline,
            width=border_w,
        )
        if "♭" in self._text and self._text.count("♭") == 1 and " " not in self._text:
            base_text = self._text.replace("♭", "")
            if base_text:
                base_font = tkfont.Font(family=self._font_family, size=self._font_size, weight="bold")
                acc_font_size = max(10, int(round(self._font_size * 0.68)))
                acc_font = tkfont.Font(family=self._font_family, size=acc_font_size, weight="bold")
                base_w = float(base_font.measure(base_text))
                acc_w = float(acc_font.measure("♭"))
                group_w = base_w + (acc_w * 0.65)
                left = (w - group_w) / 2.0
                base_x = left + (base_w / 2.0)
                acc_x = left + base_w + (acc_w * 0.32)
                self.create_text(
                    base_x,
                    h / 2,
                    text=base_text,
                    fill=text_color,
                    font=(self._font_family, self._font_size, "bold"),
                    anchor="center",
                )
                self.create_text(
                    acc_x,
                    (h / 2) - max(6, int(round(self._font_size * 0.34))),
                    text="♭",
                    fill=text_color,
                    font=(self._font_family, acc_font_size, "bold"),
                    anchor="center",
                )
            else:
                self.create_text(
                    w / 2,
                    h / 2,
                    text=self._text,
                    fill=text_color,
                    font=(self._font_family, self._font_size, "bold"),
                    anchor="center",
                )
        else:
            self.create_text(
                w / 2,
                h / 2,
                text=self._text,
                fill=text_color,
                font=(self._font_family, self._font_size, "bold"),
                anchor="center",
            )


class PlayTransportButton(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        command: Callable[[], None],
        width: int = 58,
        height: int = 34,
        radius: int = 14,
    ) -> None:
        parent_bg = _resolve_canvas_bg(master, "#1f2329")
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            highlightbackground=parent_bg,
            highlightcolor=parent_bg,
            cursor="hand2",
        )
        self._command = command
        self._radius = radius
        self._hover = False
        self._pressed = False
        self._playing = False
        self._font_family = _pick_font_family(self, ["Avenir Next", "SF Pro Text", "Segoe UI", "Helvetica Neue"], "Helvetica")

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", lambda _e: self._redraw())
        self._redraw()

    def set_playing(self, playing: bool) -> None:
        self._playing = bool(playing)
        self._redraw()

    def _on_press(self, _event: tk.Event) -> None:
        self._pressed = True
        self._redraw()

    def _on_release(self, event: tk.Event) -> None:
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if not was_pressed:
            return
        x = float(getattr(event, "x", -1))
        y = float(getattr(event, "y", -1))
        if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
            self._command()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hover = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hover = False
        self._pressed = False
        self._redraw()

    def _rounded_points(self, x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
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

    def _redraw(self) -> None:
        parent_bg = _resolve_canvas_bg(self.master, str(self.cget("bg")))
        if parent_bg != str(self.cget("bg")):
            self.configure(bg=parent_bg, highlightbackground=parent_bg, highlightcolor=parent_bg)
        self.delete("all")
        w = max(12, int(self.winfo_width()))
        h = max(12, int(self.winfo_height()))
        r = max(8, min(self._radius, int(min(w, h) / 2) - 1))

        if self._playing:
            fill = "#f3bf2f" if not self._pressed else "#d8a624"
            outline = "#c9961f"
            icon_color = "#111318"
        else:
            if self._pressed:
                fill = "#323943"
            elif self._hover:
                fill = "#2b323b"
            else:
                fill = "#262c34"
            outline = "#4a5360"
            icon_color = "#f0f2f5"

        self.create_polygon(
            self._rounded_points(1, 1, w - 1, h - 1, r),
            smooth=True,
            splinesteps=18,
            fill=fill,
            outline=outline,
            width=1.6,
        )
        cx = w / 2
        cy = h / 2
        if self._playing:
            side = max(10, int(min(w, h) * 0.34))
            x1 = cx - side / 2
            y1 = cy - side / 2
            x2 = cx + side / 2
            y2 = cy + side / 2
            self.create_rectangle(x1, y1, x2, y2, fill=icon_color, outline=icon_color, width=1)
        else:
            tri_w = max(12, int(min(w, h) * 0.44))
            tri_h = max(12, int(min(w, h) * 0.52))
            x_left = cx - tri_w * 0.42
            x_right = cx + tri_w * 0.45
            y_top = cy - tri_h / 2
            y_bot = cy + tri_h / 2
            self.create_polygon(
                x_left,
                y_top,
                x_right,
                cy,
                x_left,
                y_bot,
                fill=icon_color,
                outline=icon_color,
                width=1,
                joinstyle=tk.ROUND,
            )
