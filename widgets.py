from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional


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
        try:
            parent_bg = str(master.cget("background"))
        except tk.TclError:
            parent_bg = "#f0f0f0"
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._selected = False
        self._radius = radius
        self._shape_id: Optional[int] = None
        self._label_id: Optional[int] = None
        self._hover = False

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
        self.delete("all")
        w = max(4, int(self.winfo_width()))
        h = max(4, int(self.winfo_height()))
        r = max(4, min(self._radius, int(min(w, h) / 2) - 1))

        if self._selected:
            fill = "#136780"
            outline = "#11b5c6"
            text_color = "#f4f7f9"
        else:
            fill = "#0b465a" if not self._hover else "#0d536a"
            outline = "#0caab9"
            text_color = "#c8d1d8"

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
            font=("Helvetica", 12, "bold"),
            anchor="w",
        )


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
        try:
            parent_bg = str(master.cget("background"))
        except tk.TclError:
            parent_bg = "#1f1f1f"
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._radius = radius
        self._hover = False
        self._selected = False

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
        self.delete("all")
        w = max(8, int(self.winfo_width()))
        h = max(8, int(self.winfo_height()))
        r = max(6, min(self._radius, int(min(w, h) / 2) - 1))
        if self._selected:
            fill = "#10bf74" if not self._hover else "#0eab67"
            outline = "#0f9d60"
        else:
            fill = "#0f8f5b" if not self._hover else "#0d7f50"
            outline = "#0b7047"
        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=fill,
            outline=outline,
            width=1.5,
        )
        self.create_text(
            w / 2,
            h / 2,
            text=self._text,
            fill="#ffffff",
            font=("Helvetica", 15),
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
        text_color: str = "#f2f2f2",
        selected_text_color: str = "#ffffff",
    ) -> None:
        try:
            parent_bg = str(master.cget("background"))
        except tk.TclError:
            parent_bg = "#2b2d38"
        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=parent_bg,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._radius = radius
        self._font_size = font_size
        self._text_color = text_color
        self._selected_text_color = selected_text_color
        self._hover = False
        self._selected = False

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
        self.delete("all")
        w = max(8, int(self.winfo_width()))
        h = max(8, int(self.winfo_height()))
        r = max(6, min(self._radius, int(min(w, h) / 2) - 1))

        if self._selected:
            outline = "#f39c12"
            fill = "#3b3f49"
            text_color = self._selected_text_color
            border_w = 2.2
        else:
            outline = "#3b3f49"
            fill = "#3b3f49" if not self._hover else "#464b57"
            text_color = self._text_color
            border_w = 1.2

        points = self._rounded_points(1, 1, w - 1, h - 1, r)
        self.create_polygon(
            points,
            smooth=True,
            splinesteps=20,
            fill=fill,
            outline=outline,
            width=border_w,
        )
        self.create_text(
            w / 2,
            h / 2,
            text=self._text,
            fill=text_color,
            font=("Helvetica", self._font_size),
            anchor="center",
        )
