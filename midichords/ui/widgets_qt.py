from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QFont, QFontMetricsF, QPainter, QPainterPath, QColor, QPolygonF
from PySide6.QtWidgets import QWidget, QSizePolicy

from midichords.qt.tk_compat import _qt_grid_attach_widget, _qt_pack_forget_widget, _qt_place_widget, qt_pack_attach


def _qcolor(value: str) -> QColor:
    c = QColor(value)
    if not c.isValid():
        return QColor("#000000")
    return c


def _font(family: str, size: int, bold: bool = False) -> QFont:
    qf = QFont(family)
    qf.setPointSize(int(size))
    qf.setBold(bool(bold))
    return qf


def _rounded_path(w: float, h: float, radius: float) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, float(w), float(h)), float(radius), float(radius))
    return path


class _QtWidgetBase(QWidget):
    # Helpers para compat superficial con tk widgets.
    def winfo_width(self) -> int:
        return max(1, int(self.width()))

    def winfo_height(self) -> int:
        return max(1, int(self.height()))

    def configure(self, **_kwargs) -> None:
        # compat: algunos mixins legacy usan configure() en tk.
        self.update()

    def bind(self, sequence: str, func) -> None:
        if not hasattr(self, "_qt_bind_handlers"):
            self._qt_bind_handlers: dict[str, list[callable]] = {}
        self._qt_bind_handlers.setdefault(str(sequence), []).append(func)

    def _emit_bind(self, sequence: str, event) -> None:
        handlers = getattr(self, "_qt_bind_handlers", {}).get(str(sequence), [])
        for cb in handlers:
            try:
                cb(event)
            except TypeError:
                cb()

    # Layout helpers (subset tk): mismo `padx`/`pady` que `tk_compat.Widget.pack`.
    def pack(self, **_kwargs) -> None:
        qt_pack_attach(self, **_kwargs)

    def pack_forget(self) -> None:
        _qt_pack_forget_widget(self)

    def grid(self, row: int = 0, column: int = 0, **kwargs) -> None:
        _qt_grid_attach_widget(self, row, column, **kwargs)

    def grid_remove(self) -> None:
        self.setVisible(False)

    def grid_forget(self) -> None:
        self.setVisible(False)

    def place(self, **kwargs) -> None:
        _qt_place_widget(self, **kwargs)

    def destroy(self) -> None:
        self.deleteLater()


class RoundedChoiceButton(_QtWidgetBase):
    def __init__(
        self,
        master: QWidget | None,
        text: str,
        command: Callable[[], None],
        *,
        width: int = 70,
        height: int = 30,
        radius: int = 12,
        font_family: str = "Helvetica",
        font_size: int = 12,
    ) -> None:
        super().__init__(master)
        self.setFixedSize(int(width), int(height))
        self._text = str(text)
        self._command = command
        self._radius = int(radius)
        self._hover = False
        self._selected = False
        self._enabled = True

        self._font_family = str(font_family)
        self._font_size = int(font_size)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_text(self, text: str) -> None:
        self._text = str(text)
        self.update()

    def set_selected(self, selected: bool) -> None:
        self._selected = bool(selected)
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ArrowCursor)
        if not self._enabled:
            self._hover = False
        self.update()

    def mousePressEvent(self, _event) -> None:
        if not self._enabled:
            return
        # La llamada real va en release para emular tk.
        self._pressed = True
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if not self._enabled:
            return
        was_pressed = getattr(self, "_pressed", False)
        self._pressed = False
        self.update()
        if was_pressed and self.rect().contains(event.position().toPoint()):
            self._command()

    def enterEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._hover = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._hover = False
        self.update()

    def paintEvent(self, _event) -> None:
        w = float(self.width())
        h = float(self.height())
        path = _rounded_path(w, h, float(self._radius))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._selected:
            fill = _qcolor("#303842")
            outline = _qcolor("#f3bf2f")
            text_color = _qcolor("#f0f2f5")
        else:
            fill = _qcolor("#252b33" if not self._hover else "#2c333d")
            outline = _qcolor("#444b56")
            text_color = _qcolor("#c8ced7")

        painter.fillPath(path, fill)
        pen = painter.pen()
        pen.setWidthF(2.0)
        pen.setColor(outline)
        painter.setPen(pen)
        painter.drawPath(path)

        # Texto centrado (# / ♭); tamaño como widgets.Tk RoundedChoiceButton (12 bold por defecto).
        painter.setPen(text_color)
        painter.setFont(_font(self._font_family, self._font_size, bold=True))
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


class RoundedPanel(_QtWidgetBase):
    def __init__(
        self,
        master: QWidget | None,
        *,
        radius: int = 16,
        bg_color: str = "#2f3f56",
        border_color: str = "#56627a",
        border_width: float = 1.2,
        padding: tuple[int, int, int, int] = (12, 12, 12, 12),
    ) -> None:
        super().__init__(master)
        self._radius = int(radius)
        self._bg_color = str(bg_color)
        self._border_color = str(border_color)
        self._border_width = float(border_width)
        self._padding = padding

        self.content = QWidget(self)
        self.content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.content.setStyleSheet(f"background-color: {self._bg_color}; border: none;")

        # Layout sin dependencia: manejamos el tamaño del content en resizeEvent.
        self._update_content_geometry()

    def _update_content_geometry(self) -> None:
        l, t, r, b = self._padding
        self.content.setGeometry(int(l), int(t), max(1, self.width() - int(l) - int(r)), max(1, self.height() - int(t) - int(b)))

    def sizeHint(self) -> QSize:  # type: ignore[override]
        l, t, r, b = self._padding
        ch = self.content.sizeHint()
        return QSize(ch.width() + l + r, ch.height() + t + b)

    def minimumSizeHint(self) -> QSize:  # type: ignore[override]
        l, t, r, b = self._padding
        cm = self.content.minimumSizeHint()
        return QSize(cm.width() + l + r, cm.height() + t + b)

    def resizeEvent(self, _event) -> None:
        self._update_content_geometry()
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        path = _rounded_path(float(self.width()), float(self.height()), float(self._radius))
        painter.fillPath(path, _qcolor(self._bg_color))
        from PySide6.QtGui import QPen

        painter.setPen(QPen(_qcolor(self._border_color), float(self._border_width)))
        painter.drawPath(path)
        painter.end()


class GreenRoundedButton(_QtWidgetBase):
    def __init__(
        self,
        master: QWidget | None,
        text: str,
        command: Callable[[], None],
        *,
        width: int = 130,
        height: int = 52,
        radius: int = 24,
        font_family: str = "Helvetica",
    ) -> None:
        super().__init__(master)
        self.setFixedSize(int(width), int(height))
        self._text = str(text)
        self._command = command
        self._radius = int(radius)
        self._hover = False
        self._selected = False
        self._pressed = False
        self._enabled = True
        self._font_family = str(font_family)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_text(self, text: str) -> None:
        self._text = str(text)
        self.update()

    def set_selected(self, selected: bool) -> None:
        self._selected = bool(selected)
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ArrowCursor)
        if not self._enabled:
            self._hover = False
            self._pressed = False
        self.update()

    def mousePressEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._pressed = True
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if not self._enabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if was_pressed and self.rect().contains(event.position().toPoint()):
            self._command()

    def enterEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._hover = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._hover = False
        self._pressed = False
        self.update()

    def paintEvent(self, _event) -> None:
        w = float(self.width())
        h = float(self.height())
        path = _rounded_path(w, h, float(self._radius))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._selected:
            fill = _qcolor("#10b574" if self._hover else "#12c37d")
            outline = _qcolor("#11a96c")
        else:
            fill = _qcolor("#0da267" if self._hover else "#0eaf70")
            outline = _qcolor("#0f9460")

        painter.fillPath(path, fill)
        from PySide6.QtGui import QPen

        painter.setPen(QPen(outline, 1.5))
        painter.drawPath(path)

        painter.setPen(_qcolor("#ffffff"))
        # Misma lógica que widgets.Tk GreenRoundedButton: 16 bold; ♭ más pequeño y elevado.
        base_sz = 16
        draw_flats = "♭" in self._text and self._text.count("♭") == 1 and " " not in self._text
        if draw_flats:
            base = self._text.replace("♭", "")
            acc = "♭"
            if not base:
                painter.setFont(_font(self._font_family, base_sz, bold=True))
                painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self._text)
            else:
                base_font = _font(self._font_family, base_sz, bold=True)
                acc_font_size = max(10, int(round(base_sz * 0.68)))
                acc_font = _font(self._font_family, acc_font_size, bold=True)
                base_metrics = QFontMetricsF(base_font)
                acc_metrics = QFontMetricsF(acc_font)
                base_w = base_metrics.horizontalAdvance(base)
                acc_w = acc_metrics.horizontalAdvance(acc)
                group_w = base_w + (acc_w * 0.65)
                left = (w - group_w) / 2.0
                base_x_center = left + base_w / 2.0
                acc_x_center = left + base_w + (acc_w * 0.32)
                base_y = h / 2.0
                acc_y = (h / 2.0) - 8.0
                painter.setFont(base_font)
                painter.drawText(
                    QRectF(base_x_center - base_w / 2.0, base_y - base_metrics.height() / 2.0, base_w, base_metrics.height()),
                    Qt.AlignmentFlag.AlignCenter,
                    base,
                )
                painter.setFont(acc_font)
                painter.drawText(
                    QRectF(acc_x_center - acc_w / 2.0, acc_y - acc_metrics.height() / 2.0, acc_w, acc_metrics.height()),
                    Qt.AlignmentFlag.AlignCenter,
                    acc,
                )
        else:
            painter.setFont(_font(self._font_family, base_sz, bold=True))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


class GrayRoundedButton(_QtWidgetBase):
    def __init__(
        self,
        master: QWidget | None,
        text: str,
        command: Callable[[], None],
        *,
        width: int = 120,
        height: int = 72,
        radius: int = 26,
        font_family: str = "Helvetica",
        font_size: int = 22,
        text_color: str = "#dde2e8",
        selected_text_color: str = "#16dfa0",
        selected_fill_color: str = "#f3bf2f",
        selected_outline_color: str = "#f3bf2f",
        selected_border_width: float = 2.2,
        expand_h: bool = False,
        shrink_to_text: bool = False,
    ) -> None:
        super().__init__(master)
        self._expand_h = bool(expand_h)
        self._shrink_to_text = bool(shrink_to_text)
        h, w = int(height), int(width)
        self._fixed_h = h
        if self._expand_h:
            self.setFixedHeight(h)
            self.setMinimumWidth(w)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedSize(w, h)
        self._text = str(text)
        self._command = command
        self._radius = int(radius)
        self._hover = False
        self._selected = False
        self._enabled = True
        self._pressed = False

        self._font_family = str(font_family)
        self._font_size = int(font_size)
        self._text_color = str(text_color)
        self._selected_text_color = str(selected_text_color)
        self._selected_fill_color = str(selected_fill_color)
        self._selected_outline_color = str(selected_outline_color)
        self._selected_border_width = float(selected_border_width)

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_text(self, text: str) -> None:
        self._text = str(text)
        if not self._expand_h and self._shrink_to_text:
            f = _font(self._font_family, self._font_size, bold=True)
            fm = QFontMetricsF(f)
            s = self._text if self._text else " "
            tw = float(fm.horizontalAdvance(s))
            pad = 28.0
            new_w = max(96.0, tw + pad)
            self.setFixedSize(int(round(new_w)), int(self._fixed_h))
        self.update()

    def set_selected(self, selected: bool) -> None:
        self._selected = bool(selected)
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ArrowCursor)
        if not self._enabled:
            self._hover = False
            self._pressed = False
        self.update()

    def mousePressEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._pressed = True
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if not self._enabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if was_pressed and self.rect().contains(event.position().toPoint()):
            self._command()

    def enterEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._hover = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._hover = False
        self._pressed = False
        self.update()

    def paintEvent(self, _event) -> None:
        w = float(self.width())
        h = float(self.height())
        path = _rounded_path(w, h, float(self._radius))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self._enabled:
            outline = "#434a54"
            fill = "#1f252d"
            text_color = "#7f8894"
            border_w = 1.4
        elif self._selected:
            outline = self._selected_outline_color
            fill = self._selected_fill_color
            text_color = self._selected_text_color
            border_w = self._selected_border_width
        else:
            outline = "#4a5360"
            fill = "#2b323b" if self._hover else "#262c34"
            if self._pressed:
                fill = "#323943"
            text_color = self._text_color
            border_w = 1.6

        painter.fillPath(path, _qcolor(fill))
        from PySide6.QtGui import QPen

        painter.setPen(QPen(_qcolor(outline), float(border_w)))
        painter.drawPath(path)

        # Texto (especial separador ♭).
        painter.setPen(_qcolor(text_color))
        base_text = self._text
        draw_flats = "♭" in self._text and self._text.count("♭") == 1 and " " not in self._text

        if draw_flats:
            base = self._text.replace("♭", "")
            acc = "♭"
            base_font = _font(self._font_family, self._font_size, bold=True)
            acc_font_size = max(10, int(round(self._font_size * 0.68)))
            acc_font = _font(self._font_family, acc_font_size, bold=True)

            base_metrics = QFontMetricsF(base_font)
            acc_metrics = QFontMetricsF(acc_font)
            base_w = base_metrics.horizontalAdvance(base)
            acc_w = acc_metrics.horizontalAdvance(acc)
            group_w = base_w + (acc_w * 0.65)
            left = (w - group_w) / 2.0

            base_x_center = left + base_w / 2.0
            acc_x_center = left + base_w + (acc_w * 0.32)
            base_y = h / 2.0
            acc_y = (h / 2.0) - max(6, int(round(self._font_size * 0.34)))

            painter.setFont(base_font)
            painter.drawText(QRectF(base_x_center - base_w / 2.0, base_y - base_metrics.height() / 2.0, base_w, base_metrics.height()),
                             Qt.AlignmentFlag.AlignCenter,
                             base)

            painter.setFont(acc_font)
            painter.drawText(QRectF(acc_x_center - acc_w / 2.0, acc_y - acc_metrics.height() / 2.0, acc_w, acc_metrics.height()),
                             Qt.AlignmentFlag.AlignCenter,
                             acc)
        else:
            painter.setFont(_font(self._font_family, self._font_size, bold=True))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self._text)

        painter.end()


class PlayTransportButton(_QtWidgetBase):
    def __init__(
        self,
        master: QWidget | None,
        command: Callable[[], None],
        *,
        width: int = 58,
        height: int = 34,
        radius: int = 14,
    ) -> None:
        super().__init__(master)
        self.setFixedSize(int(width), int(height))
        self._command = command
        self._radius = int(radius)
        self._hover = False
        self._pressed = False
        self._playing = False
        self._enabled = True
        self._font_family = "Helvetica"
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_playing(self, playing: bool) -> None:
        self._playing = bool(playing)
        self.update()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if self._enabled else Qt.CursorShape.ArrowCursor)
        if not self._enabled:
            self._hover = False
            self._pressed = False
            self._playing = False
        self.update()

    def mousePressEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._pressed = True
        self._emit_bind("<ButtonPress-1>", _event)
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if not self._enabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._emit_bind("<ButtonRelease-1>", event)
        self.update()
        if was_pressed and self.rect().contains(event.position().toPoint()):
            self._command()

    def enterEvent(self, _event) -> None:
        if not self._enabled:
            return
        self._hover = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._hover = False
        self._pressed = False
        self.update()

    def paintEvent(self, _event) -> None:
        w = float(self.width())
        h = float(self.height())
        path = _rounded_path(w, h, float(self._radius))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self._enabled:
            fill = "#1f252d"
            outline = "#434a54"
            icon_color = "#7f8894"
        elif self._playing:
            fill = "#d8a624" if self._pressed else "#f3bf2f"
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

        painter.fillPath(path, _qcolor(fill))
        from PySide6.QtGui import QPen

        painter.setPen(QPen(_qcolor(outline), 1.6))
        painter.drawPath(path)

        cx = w / 2.0
        cy = h / 2.0
        if self._playing:
            side = max(10, int(min(w, h) * 0.34))
            x1 = cx - side / 2.0
            y1 = cy - side / 2.0
            x2 = cx + side / 2.0
            y2 = cy + side / 2.0
            painter.setBrush(_qcolor(icon_color))
            painter.setPen(_qcolor(icon_color))
            painter.drawRect(QRectF(x1, y1, x2 - x1, y2 - y1))
        else:
            tri_w = max(12, int(min(w, h) * 0.44))
            tri_h = max(12, int(min(w, h) * 0.52))
            x_left = cx - tri_w * 0.42
            x_right = cx + tri_w * 0.45
            y_top = cy - tri_h / 2.0
            y_bot = cy + tri_h / 2.0
            triangle = QPolygonF([QPointF(x_left, y_top), QPointF(x_right, cy), QPointF(x_left, y_bot)])
            painter.setBrush(_qcolor(icon_color))
            painter.setPen(_qcolor(icon_color))
            painter.drawPolygon(triangle)

        painter.end()

