from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject, QPointF, QRect, QRectF, Qt, QTimer, QEvent, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QMouseEvent, QPainter, QPen, QBrush, QPolygonF
from PySide6.QtWidgets import QWidget, QApplication

# Invocador lazy: ejecuta callbacks en el hilo de la GUI (QTimer/widgets no son seguros en otros hilos).
_main_thread_invoker: Optional["_MainThreadInvoker"] = None


class _MainThreadInvoker(QObject):
    """Reenvía `fn()` al hilo donde vive QApplication (event loop Qt)."""

    _invoke = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._invoke.connect(self._run, Qt.ConnectionType.QueuedConnection)

    @Slot(object)
    def _run(self, fn: object) -> None:
        if callable(fn):
            fn()


def run_on_main_thread(fn: Callable[[], None]) -> None:
    """Ejecuta `fn` en el hilo GUI; si ya estamos ahí, llama directamente."""
    app = QApplication.instance()
    if app is None:
        fn()
        return
    if QThread.currentThread() == app.thread():
        fn()
        return
    global _main_thread_invoker
    if _main_thread_invoker is None:
        _main_thread_invoker = _MainThreadInvoker()
        _main_thread_invoker.moveToThread(app.thread())
    _main_thread_invoker._invoke.emit(fn)


def _color(value: Any, default: QColor | None = None) -> QColor:
    if value is None:
        return default if default is not None else QColor(0, 0, 0, 0)
    if isinstance(value, QColor):
        return value
    s = str(value).strip()
    if not s:
        return default if default is not None else QColor(0, 0, 0, 0)
    try:
        return QColor(s)
    except Exception:
        return default if default is not None else QColor(0, 0, 0, 0)


def _tk_state_from_qt_modifiers(mods: Any) -> int:
    """Bits parecidos a `tk.Event.state` (Shift, Control, Alt, Meta/Cmd) para handlers migrados."""
    if mods is None:
        return 0
    try:
        state = 0
        if mods & Qt.KeyboardModifier.ShiftModifier:
            state |= 0x0001
        if mods & Qt.KeyboardModifier.ControlModifier:
            state |= 0x0004
        if mods & Qt.KeyboardModifier.AltModifier:
            state |= 0x0008
        if mods & Qt.KeyboardModifier.MetaModifier:
            state |= 0x20000
        return int(state)
    except (TypeError, ValueError):
        return 0


def _font_from_tk_tuple(font: Any) -> QFont:
    # Tkinter suele pasar font=(family, size, "bold") o similar.
    # En Tk, tamaño negativo = píxeles; positivo = puntos tipográficos.
    if isinstance(font, QFont):
        return font
    if not font:
        return QFont()
    if isinstance(font, (list, tuple)) and len(font) >= 2:
        family = str(font[0])
        size = int(font[1])
        qf = QFont(family)
        if size < 0:
            qf.setPixelSize(max(1, abs(size)))
        else:
            qf.setPointSize(max(1, size))
        weight = QFont.Normal
        for part in font[2:]:
            if str(part).lower() == "bold":
                weight = QFont.Bold
        qf.setWeight(weight)
        return qf
    # Fallback: try interpreting as family name
    qf = QFont(str(font))
    return qf


def _qt_canvas_text_rect_and_flags(
    payload: dict[str, Any], canvas_w: float, canvas_h: float
) -> tuple[QRectF, int]:
    """(x,y) + anchor como Tk Canvas; devuelve QRectF y flags para QPainter.drawText."""
    x = float(payload["x"])
    y = float(payload["y"])
    anchor = str(payload.get("anchor", "center")).lower()
    cw = max(1.0, float(canvas_w))
    ch = max(1.0, float(canvas_h))
    txt = str(payload.get("text", ""))
    font = _font_from_tk_tuple(payload.get("font"))
    fm = QFontMetricsF(font)
    tw = max(1.0, float(fm.horizontalAdvance(txt)))
    th = max(1.0, float(fm.height()))

    a = anchor
    if a == "w":
        # Tk anchor="w": izquierda en x y el centro vertical en y.
        rect = QRectF(x, y - th * 0.5, max(1.0, cw - x), th)
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    elif a == "e":
        # Tk anchor="e": derecha en x y el centro vertical en y.
        rect = QRectF(0.0, y - th * 0.5, max(1.0, x), th)
        flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    elif a == "nw":
        rect = QRectF(x, y, cw - x, ch - y)
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
    elif a == "n":
        # Tk: (x,y) es el punto medio-superior del texto.
        rect = QRectF(x - tw * 0.5, y, tw, th)
        flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
    elif a == "ne":
        rect = QRectF(0.0, y, x, ch - y)
        flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
    elif a == "sw":
        rect = QRectF(x, 0.0, cw - x, y)
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
    elif a == "s":
        # Tk: (x,y) es el punto medio-inferior del texto. No usar todo el ancho del canvas
        # para AlignHCenter (desplazaría la etiqueta al centro del teclado, p. ej. en negras).
        rect = QRectF(x - tw * 0.5, y - th, tw, th)
        flags = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
    elif a == "se":
        rect = QRectF(0.0, 0.0, x, y)
        flags = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
    elif a in ("center", "c"):
        rect = QRectF(x - tw * 0.5, y - th * 0.5, tw, th)
        flags = Qt.AlignmentFlag.AlignCenter
    else:
        rect = QRectF(x - tw * 0.5, y - th * 0.5, tw, th)
        flags = Qt.AlignmentFlag.AlignCenter
    return rect, int(flags) | int(Qt.TextFlag.TextDontClip)


@dataclass
class _CanvasItem:
    item_id: int
    kind: str
    tags: set[str]
    visible: bool = True
    z: int = 0
    # Common geometry
    # - line: (x1,y1,x2,y2)
    # - rect/oval: (x1,y1,x2,y2)
    # - polygon: list[points]
    # - text: (x,y,text)
    payload: dict[str, Any] | None = None


class QtCanvas(QWidget):
    """Canvas-like widget con API parcial de tk.Canvas.

    Se implementa solo lo necesario para migrar el desktop sin tocar la lógica
    de dibujo (RenderMixin y parte de UiMixin/Overlays).
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        width: int = 0,
        height: int = 0,
        bg: str = "#000000",
        cursor: str | None = None,
        highlightthickness: int = 0,  # compat: ignorado
        bd: int = 0,  # compat: ignorado
        highlightbackground: str | None = None,  # compat: ignorado
        highlightcolor: str | None = None,  # compat: ignorado
    ) -> None:
        super().__init__(parent)
        self._bg = str(bg)
        self._items: dict[int, _CanvasItem] = {}
        self._z_counter = 0
        self._next_id = 1
        self._window_children: dict[int, QWidget] = {}
        self._window_anchor: dict[int, str] = {}
        self._window_coords: dict[int, tuple[float, float]] = {}
        self._window_wh: dict[int, tuple[int, int]] = {}
        self._item_handlers: dict[tuple[str, int], Callable[[Any], None]] = {}
        self._tag_handlers: dict[tuple[str, str], Callable[[Any], None]] = {}
        self._canvas_handlers: dict[str, Callable[[Any], None]] = {}
        self._pressed = False

        # Tk suele pasar width+height como tamaño inicial; con `setFixedSize` el canvas
        # no puede crecer en QGridLayout aunque la columna tenga stretch (p. ej. sliders
        # BPM/volumen del metrónomo). Usamos mínimos para respetar expansión horizontal.
        if width and height:
            self.setMinimumSize(int(width), int(height))
        elif height:
            self.setMinimumHeight(int(height))
        elif width:
            self.setMinimumWidth(int(width))
        if cursor:
            self._apply_cursor(cursor)

        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)

    def _apply_cursor(self, cursor: str) -> None:
        # Map mínima: Tk usa "hand2"; Qt usa CursorShape.PointingHandCursor.
        if cursor in {"hand2", "pointinghand"}:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.unsetCursor()

    # ---- Compat geometry / tk-ish ----
    def winfo_width(self) -> int:
        return max(1, int(self.width()))

    def winfo_height(self) -> int:
        return max(1, int(self.height()))

    def winfo_ismapped(self) -> bool:
        return bool(self.isVisible())

    def cget(self, key: str) -> str:
        if key == "background" or key == "bg":
            return self._bg
        raise KeyError(key)

    # ---- Event bindings (parcial) ----
    def bind(self, sequence: str, func: Callable[[Any], None], add: str | None = None) -> None:
        seq = str(sequence)
        if add == "+" and seq in self._canvas_handlers:
            prev = self._canvas_handlers[seq]

            def _chain(ev: Any) -> None:
                prev(ev)
                func(ev)

            self._canvas_handlers[seq] = _chain
        else:
            self._canvas_handlers[seq] = func

    def tag_bind(self, tag_or_id: object, sequence: str, func: Callable[[Any], None]) -> None:
        if isinstance(tag_or_id, int):
            self._item_handlers[(sequence, int(tag_or_id))] = func
            return
        self._tag_handlers[(sequence, str(tag_or_id))] = func

    # ---- Canvas item management ----
    def delete(self, tag_or_all: str) -> None:
        if str(tag_or_all) == "all":
            # Quitar ventanas
            for wid in list(self._window_children.keys()):
                w = self._window_children.pop(wid, None)
                if w is not None:
                    w.setParent(None)
                self._window_coords.pop(wid, None)
                self._window_wh.pop(wid, None)
                self._window_anchor.pop(wid, None)
            self._items.clear()
            self._next_id = 1
            self.update()
            return
        tag = str(tag_or_all)
        to_del = [iid for iid, it in self._items.items() if tag in it.tags]
        for iid in to_del:
            self._items.pop(iid, None)
        # También borrar widgets anclados si tenían tag implícito (no usado en esta migración).
        self.update()

    def tag_lower(self, tag: str) -> None:
        # Lower mueve a los elementos con tag al principio de la pila.
        tag = str(tag)
        lowered = [it for it in self._items.values() if tag in it.tags]
        for it in lowered:
            it.z = 0
        for it in sorted(self._items.values(), key=lambda x: x.z):
            # Re-numerar z de forma estable.
            it.z = self._z_counter
            self._z_counter += 1
        self.update()

    def lower(self, tag: str) -> None:
        # Alias estilo tk.Canvas.lower(...)
        self.tag_lower(tag)

    def itemconfigure(self, item_id: int, **kwargs: Any) -> None:
        iid = int(item_id)
        # Ventanas embebidas (create_window): Tk usa width/height en itemconfigure.
        if iid in self._window_children:
            w = self._window_children[iid]
            if "state" in kwargs and str(kwargs["state"]).lower() == "hidden":
                w.setVisible(False)
            elif "state" in kwargs:
                w.setVisible(True)
            if "width" in kwargs or "height" in kwargs:
                cur = self._window_wh.get(iid, (max(1, w.width()), max(1, w.height())))
                nw = int(kwargs["width"]) if "width" in kwargs else cur[0]
                nh = int(kwargs["height"]) if "height" in kwargs else cur[1]
                self._window_wh[iid] = (max(1, nw), max(1, nh))
            if iid in self._window_coords:
                x, y = self._window_coords[iid]
                self._position_window(iid, x, y)
            w.raise_()
            self.update()
            return
        it = self._items.get(iid)
        if it is None:
            return
        if "state" in kwargs:
            state = str(kwargs["state"]).lower()
            it.visible = state != "hidden"
        if "text" in kwargs and it.kind == "text":
            assert it.payload is not None
            it.payload["text"] = str(kwargs["text"])
        if "fill" in kwargs and "fill" in kwargs:
            assert it.payload is not None
            it.payload["fill"] = kwargs["fill"]
        self.update()

    def _new_id(self) -> int:
        iid = self._next_id
        self._next_id += 1
        return iid

    def _parse_tags(self, tags: Any) -> set[str]:
        if tags is None:
            return set()
        if isinstance(tags, str):
            return {tags}
        try:
            # Accept list/tuple
            return {str(x) for x in tags}
        except Exception:
            return {str(tags)}

    # ---- Create primitives ----
    def create_line(self, x1: float, y1: float, x2: float, y2: float, **kwargs: Any) -> int:
        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="line",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
                "width": float(kwargs.get("width", 1.0)),
                "fill": kwargs.get("fill", "#000000"),
                "capstyle": kwargs.get("capstyle"),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_rectangle(self, x1: float, y1: float, x2: float, y2: float, **kwargs: Any) -> int:
        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="rect",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
                "fill": kwargs.get("fill", ""),
                "outline": kwargs.get("outline", ""),
                "width": float(kwargs.get("width", 1.0)),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_oval(self, x1: float, y1: float, x2: float, y2: float, **kwargs: Any) -> int:
        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="oval",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
                "fill": kwargs.get("fill", ""),
                "outline": kwargs.get("outline", ""),
                "width": float(kwargs.get("width", 1.0)),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_arc(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        **kwargs: Any,
    ) -> int:
        """Arco tipo tk.Canvas: bbox, start/extent en grados (0=Este, CCW), style pieslice|arc|chord."""
        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="arc",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "x1": float(x1),
                "y1": float(y1),
                "x2": float(x2),
                "y2": float(y2),
                "start": float(kwargs.get("start", 0)),
                "extent": float(kwargs.get("extent", 0)),
                "style": str(kwargs.get("style", "pieslice")),
                "fill": kwargs.get("fill", ""),
                "outline": kwargs.get("outline", ""),
                "width": float(kwargs.get("width", 1.0)),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_polygon(self, points: list[float] | tuple[float, ...], **kwargs: Any) -> int:
        item_id = self._new_id()
        pts = list(points)
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="poly",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "points": pts,
                "fill": kwargs.get("fill", ""),
                "outline": kwargs.get("outline", ""),
                "width": float(kwargs.get("width", 1.0)),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_text(self, x: float, y: float, **kwargs: Any) -> int:
        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="text",
            tags=self._parse_tags(kwargs.get("tags")),
            z=self._z_counter,
            payload={
                "x": float(x),
                "y": float(y),
                "text": str(kwargs.get("text", "")),
                "fill": kwargs.get("fill", "#000000"),
                "font": kwargs.get("font"),
                "anchor": kwargs.get("anchor", "center"),
            },
        )
        self._z_counter += 1
        self.update()
        return item_id

    def create_window(self, x: float | tuple[float, float], y: float | None = None, *, window: QWidget, anchor: str = "nw", height: int | None = None) -> int:  # type: ignore[override]
        # Tk usa create_window(x, y, window=..., anchor=..., height=...)
        if isinstance(x, (tuple, list)) and y is None:
            x_val, y_val = float(x[0]), float(x[1])
        else:
            if y is None:
                raise TypeError("create_window requires y or (x,y) tuple")
            x_val, y_val = float(x), float(y)

        item_id = self._new_id()
        self._window_children[item_id] = window
        self._window_anchor[item_id] = str(anchor)
        window.setParent(self)
        if height is not None:
            window.setFixedHeight(int(height))
            self._window_wh[item_id] = (max(1, window.width()), max(1, int(height)))
        self._position_window(item_id, x_val, y_val)
        window.raise_()
        self.update()
        return item_id

    def _position_window(self, item_id: int, x: float, y: float) -> None:
        self._window_coords[item_id] = (float(x), float(y))
        w = self._window_children.get(item_id)
        if w is None:
            return
        anchor = self._window_anchor.get(item_id, "nw")
        if item_id in self._window_wh:
            w_w, w_h = self._window_wh[item_id]
        else:
            geo = w.frameGeometry()
            w_w = max(1, int(geo.width()))
            w_h = max(1, int(geo.height()))

        # Anchors: implement the ones used in this codebase.
        ax = 0
        ay = 0
        if anchor in {"nw", "w"}:
            ax = 0
            ay = 0
        elif anchor in {"n", "center", "c"}:
            ax = w_w / 2
            ay = 0
        elif anchor in {"s"}:
            ax = w_w / 2
            ay = w_h
        else:
            # Default to top-left.
            ax = 0
            ay = 0

        geom = QRectF(x - ax, y - ay, w_w, w_h)
        w.setGeometry(int(geom.x()), int(geom.y()), int(geom.width()), int(geom.height()))

    def coords(self, item_id: int, *coord_args: float) -> None:
        """Tk coords: ventanas (x,y); texto (x,y); línea/óvalo/rect (x1,y1,x2,y2); imagen (x,y)."""
        iid = int(item_id)
        if iid in self._window_children:
            if len(coord_args) >= 2:
                self._position_window(iid, float(coord_args[0]), float(coord_args[1]))
            self.update()
            return
        it = self._items.get(iid)
        if it is None or it.payload is None:
            self.update()
            return
        pl = it.payload
        n = len(coord_args)
        if it.kind == "text" and n >= 2:
            pl["x"] = float(coord_args[0])
            pl["y"] = float(coord_args[1])
        elif it.kind == "line" and n >= 4:
            pl["x1"], pl["y1"] = float(coord_args[0]), float(coord_args[1])
            pl["x2"], pl["y2"] = float(coord_args[2]), float(coord_args[3])
        elif it.kind in {"rect", "oval"} and n >= 4:
            pl["x1"], pl["y1"] = float(coord_args[0]), float(coord_args[1])
            pl["x2"], pl["y2"] = float(coord_args[2]), float(coord_args[3])
        elif it.kind == "image" and n >= 2:
            pl["x"] = float(coord_args[0])
            pl["y"] = float(coord_args[1])
        self.update()

    def create_image(self, x: float, y: float, *, image: Any, anchor: str = "center") -> int:
        # Tk Canvas usa `create_image(..., image=...)`. Aquí soportamos QPixmap.
        from PySide6.QtGui import QImage

        if hasattr(image, "isNull") and hasattr(image, "width") and hasattr(image, "height"):
            pixmap = image
        elif isinstance(image, QImage):
            pixmap = QPixmap.fromImage(image)
        else:
            pixmap = QPixmap()

        item_id = self._new_id()
        self._items[item_id] = _CanvasItem(
            item_id=item_id,
            kind="image",
            tags=set(),
            z=self._z_counter,
            payload={"x": float(x), "y": float(y), "pixmap": pixmap, "anchor": str(anchor)},
        )
        self._z_counter += 1
        self.update()
        return item_id

    # ---- Painting ----
    def paintEvent(self, _event: Any) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if self._bg and self._bg.lower() not in ("transparent", "none", ""):
            painter.fillRect(self.rect(), _color(self._bg, QColor(0, 0, 0)))

        # Draw items in z order.
        for it in sorted(self._items.values(), key=lambda x: x.z):
            if not it.visible or it.payload is None:
                continue
            payload = it.payload
            if it.kind == "line":
                pen = QPen(_color(payload.get("fill", "#000")), payload.get("width", 1.0))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap if payload.get("capstyle") else Qt.PenCapStyle.FlatCap)
                painter.setPen(pen)
                painter.drawLine(QPointF(payload["x1"], payload["y1"]), QPointF(payload["x2"], payload["y2"]))
            elif it.kind in {"rect", "oval"}:
                x1, y1, x2, y2 = payload["x1"], payload["y1"], payload["x2"], payload["y2"]
                rx1, ry1 = min(x1, x2), min(y1, y2)
                rx2, ry2 = max(x1, x2), max(y1, y2)
                rect = QRectF(rx1, ry1, rx2 - rx1, ry2 - ry1)
                fill = str(payload.get("fill", "")).strip()
                outline = str(payload.get("outline", "")).strip()
                width = float(payload.get("width", 1.0))
                if it.kind == "rect":
                    painter.setBrush(_color(fill, QColor(0, 0, 0, 0)) if fill else Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(_color(outline, QColor(0, 0, 0)), width) if outline else QPen(Qt.transparent))
                    painter.drawRect(rect)
                else:
                    painter.setBrush(_color(fill, QColor(0, 0, 0, 0)) if fill else Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(_color(outline, QColor(0, 0, 0)), width) if outline else QPen(Qt.transparent))
                    painter.drawEllipse(rect)
            elif it.kind == "arc":
                ax1, ay1, ax2, ay2 = payload["x1"], payload["y1"], payload["x2"], payload["y2"]
                rx, ry = min(ax1, ax2), min(ay1, ay2)
                rw = max(1, int(round(abs(ax2 - ax1))))
                rh = max(1, int(round(abs(ay2 - ay1))))
                rect = QRect(int(rx), int(ry), rw, rh)
                start_q = int(round(float(payload["start"]) * 16))
                span_q = int(round(float(payload["extent"]) * 16))
                style = str(payload.get("style", "pieslice"))
                fill = str(payload.get("fill", "") or "").strip()
                outline = str(payload.get("outline", "") or "").strip()
                width = float(payload.get("width", 1.0))
                if style == "pieslice":
                    painter.setBrush(_color(fill, QColor(0, 0, 0, 0)) if fill else Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(_color(outline, QColor(0, 0, 0)), width) if outline else QPen(Qt.transparent))
                    painter.drawPie(rect, start_q, span_q)
                elif style == "chord":
                    painter.setBrush(_color(fill, QColor(0, 0, 0, 0)) if fill else Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(_color(outline, QColor(0, 0, 0)), width) if outline else QPen(Qt.transparent))
                    painter.drawChord(rect, start_q, span_q)
                else:
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(_color(outline or "#000000", QColor(0, 0, 0)), width))
                    painter.drawArc(rect, start_q, span_q)
            elif it.kind == "poly":
                pts = payload.get("points", [])
                fill = str(payload.get("fill", "")).strip()
                outline = str(payload.get("outline", "")).strip()
                width = float(payload.get("width", 1.0))
                poly = QPolygonF([QPointF(pts[i], pts[i + 1]) for i in range(0, len(pts) - 1, 2)])
                painter.setBrush(_color(fill, QColor(0, 0, 0, 0)) if fill else Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(_color(outline, QColor(0, 0, 0)), width) if outline else QPen(Qt.transparent))
                painter.drawPolygon(poly)
            elif it.kind == "text":
                painter.setPen(_color(payload.get("fill", "#000"), QColor(0, 0, 0)))
                painter.setFont(_font_from_tk_tuple(payload.get("font")))
                txt = str(payload.get("text", ""))
                rect, flags = _qt_canvas_text_rect_and_flags(payload, float(self.width()), float(self.height()))
                painter.drawText(rect, flags, txt)
            elif it.kind == "image":
                x, y = float(payload["x"]), float(payload["y"])
                pixmap = payload.get("pixmap")
                if pixmap is not None and hasattr(pixmap, "isNull") and not bool(pixmap.isNull()):
                    img_w = int(pixmap.width())
                    img_h = int(pixmap.height())
                    anchor = str(payload.get("anchor", "center"))
                    if anchor in {"nw", "n"}:
                        draw_x = x
                        draw_y = y
                    else:
                        draw_x = x - img_w / 2.0
                        draw_y = y - img_h / 2.0
                    painter.drawPixmap(int(draw_x), int(draw_y), pixmap)

        # Child widgets (create_window) are separate layers, no need to paint them here.
        painter.end()

    # ---- Hit-test for bindings ----
    def _item_rect(self, it: _CanvasItem) -> QRectF:
        payload = it.payload or {}
        if it.kind == "line":
            x1, y1, x2, y2 = payload["x1"], payload["y1"], payload["x2"], payload["y2"]
            return QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        if it.kind in {"rect", "oval"}:
            x1, y1, x2, y2 = payload["x1"], payload["y1"], payload["x2"], payload["y2"]
            return QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        if it.kind == "arc":
            x1, y1, x2, y2 = payload["x1"], payload["y1"], payload["x2"], payload["y2"]
            return QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        if it.kind == "poly":
            pts = payload.get("points", [])
            xs = [float(pts[i]) for i in range(0, len(pts) - 1, 2)]
            ys = [float(pts[i]) for i in range(1, len(pts) - 1, 2)]
            return QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        if it.kind == "text":
            rect, _flags = _qt_canvas_text_rect_and_flags(payload, float(self.width()), float(self.height()))
            return rect
        if it.kind == "image":
            x, y = float(payload["x"]), float(payload["y"])
            pixmap = payload.get("pixmap")
            if pixmap is None or not hasattr(pixmap, "width"):
                return QRectF()
            img_w = float(pixmap.width())
            img_h = float(pixmap.height())
            anchor = str(payload.get("anchor", "center"))
            if anchor in {"nw", "n"}:
                return QRectF(x, y, img_w, img_h)
            return QRectF(x - img_w / 2.0, y - img_h / 2.0, img_w, img_h)
        return QRectF()

    def _dispatch_mouse(self, canvas_seq: str | list[str], pos, *, modifiers: Any = None) -> None:
        x = float(pos.x())
        y = float(pos.y())
        state = _tk_state_from_qt_modifiers(modifiers)
        ev = _QtEventLike(x=x, y=y, state=state)
        seqs: list[str] = [canvas_seq] if isinstance(canvas_seq, str) else list(canvas_seq)
        # Canvas: Tk suele usar <ButtonPress-1>; el shim antiguo solo buscaba <Button-1>.
        for seq in seqs:
            if seq in self._canvas_handlers:
                self._canvas_handlers[seq](ev)
                break

        # Item / tag: probar las mismas secuencias (p. ej. tag_bind con <Button-1>).
        hit_items = [it for it in self._items.values() if it.visible and self._item_rect(it).contains(QPointF(x, y))]
        if hit_items:
            hit_items.sort(key=lambda i: i.z, reverse=True)
            top = hit_items[0]
            for seq in seqs:
                cb_item = self._item_handlers.get((seq, top.item_id))
                if cb_item:
                    cb_item(ev)
                    break
            for tag in top.tags:
                for seq in seqs:
                    cb_tag = self._tag_handlers.get((seq, tag))
                    if cb_tag:
                        cb_tag(ev)
                        break

    def mousePressEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self._dispatch_mouse(
                ["<ButtonPress-1>", "<Button-1>"],
                event.position(),
                modifiers=event.modifiers(),
            )

    def mouseMoveEvent(self, event: Any) -> None:
        if self._pressed and (event.buttons() & Qt.MouseButton.LeftButton):
            self._dispatch_mouse("<B1-Motion>", event.position(), modifiers=event.modifiers())

    def mouseReleaseEvent(self, event: Any) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self._dispatch_mouse("<ButtonRelease-1>", event.position(), modifiers=event.modifiers())
            self.update()

    def wheelEvent(self, event: Any) -> None:
        # Tk manda MouseWheel con delta. Aquí no mapeamos exacto; se usará en migración para scroll ligero.
        # Se conserva la firma: _on_any_mousewheel(event) suele leer event.delta o event.num.
        delta = float(event.angleDelta().y())
        _ = delta  # solo para compat; se usará en handlers reescritos
        seq = "<MouseWheel>"
        if seq in self._canvas_handlers:
            st = _tk_state_from_qt_modifiers(event.modifiers())
            self._canvas_handlers[seq](
                _QtEventLike(
                    x=float(event.position().x()),
                    y=float(event.position().y()),
                    delta=delta,
                    state=st,
                )
            )

    def enterEvent(self, _event: Any) -> None:
        if "<Enter>" in self._canvas_handlers:
            self._canvas_handlers["<Enter>"](_QtEventLike(x=0, y=0))

    def leaveEvent(self, _event: Any) -> None:
        if "<Leave>" in self._canvas_handlers:
            self._canvas_handlers["<Leave>"](_QtEventLike(x=0, y=0))

    def resizeEvent(self, _event: Any) -> None:
        # Configure event
        if "<Configure>" in self._canvas_handlers:
            self._canvas_handlers["<Configure>"](_QtEventLike(x=0, y=0))


class _QtEventLike:
    """Objeto simple para pasar x/y a handlers migrados sin tk.Event."""

    def __init__(self, *, x: float, y: float, delta: float | None = None, state: int = 0) -> None:
        self.x = x
        self.y = y
        self.delta = delta
        self.state = int(state)
        # Compat: algunas funciones usan event.widget / event.x_root, etc. Se agregan donde haga falta.


class QtStringVar:
    def __init__(self, value: str = "") -> None:
        self._value = str(value)
        self._callbacks: list[Callable[..., None]] = []

    def set(self, value: Any) -> None:
        new_value = str(value)
        if new_value == self._value:
            return
        self._value = new_value
        for cb in list(self._callbacks):
            try:
                cb(None, None, "write")
            except TypeError:
                cb()

    def get(self) -> str:
        return str(self._value)

    def trace_add(self, _mode: str, callback: Callable[..., None]) -> None:
        self._callbacks.append(callback)


class QtBooleanVar:
    def __init__(self, value: bool = False) -> None:
        self._value = bool(value)
        self._callbacks: list[Callable[..., None]] = []

    def set(self, value: Any) -> None:
        new_value = bool(value)
        if new_value == self._value:
            return
        self._value = new_value
        for cb in list(self._callbacks):
            try:
                cb(None, None, "write")
            except TypeError:
                cb()

    def get(self) -> bool:
        return bool(self._value)

    def trace_add(self, _mode: str, callback: Callable[..., None]) -> None:
        self._callbacks.append(callback)


class QtSchedulerMixin:
    """Implementa `after` y `after_cancel` usando QTimer/Qt."""

    def __init__(self) -> None:
        super().__init__()  # type: ignore[misc]
        self._qt_after_timers: dict[str, QTimer] = {}
        self._qt_after_seq = 0
        self._qt_bind_all_handlers: dict[str, list[Callable[..., None]]] = {}
        self._qt_bg: str = ""

    def after(self, ms: int, callback: Callable[[], None]) -> str:
        # QTimer solo es válido en el hilo que tiene el event loop Qt (normalmente el GUI).
        app = QApplication.instance()
        if app is not None and QThread.currentThread() != app.thread():

            def _defer() -> None:
                self.after(ms, callback)

            run_on_main_thread(_defer)
            self._qt_after_seq += 1
            return f"defer-{self._qt_after_seq}"

        self._qt_after_seq += 1
        timer_id = str(self._qt_after_seq)
        timer = QTimer()
        timer.setSingleShot(True)

        def _run() -> None:
            self._qt_after_timers.pop(timer_id, None)
            callback()

        timer.timeout.connect(_run)  # type: ignore[arg-type]
        timer.start(int(ms))
        self._qt_after_timers[timer_id] = timer
        return timer_id

    def after_cancel(self, timer_id: str) -> None:
        tid = str(timer_id)
        timer = self._qt_after_timers.pop(tid, None)
        if timer is not None:
            timer.stop()

    # ---- Tk-like bind_all (global keyboard/mousewheel) ----
    def bind_all(self, sequence: str, func: Callable[..., None], add: str | None = None) -> None:
        # `add` se ignora: en Tk existe para acumular bindings.
        seq = str(sequence)
        self._qt_bind_all_handlers.setdefault(seq, []).append(func)

    def _dispatch_bind_all(self, sequences: list[str], event: Any) -> None:
        for seq in sequences:
            for cb in list(self._qt_bind_all_handlers.get(seq, [])):
                try:
                    cb(event)
                except TypeError:
                    cb()

    def keyPressEvent(self, event: Any) -> None:  # type: ignore[override]
        key = int(event.key())

        sequences: list[str] = []
        if key == int(Qt.Key.Key_Escape):
            sequences.append("<Escape>")
        elif key == int(Qt.Key.Key_Return) or key == int(Qt.Key.Key_Enter):
            sequences.append("<Return>")
        elif key == int(Qt.Key.Key_Space):
            sequences.append("<space>")
        elif key == int(Qt.Key.Key_Shift):
            sequences.extend(["<KeyPress-Shift_L>", "<KeyPress-Shift_R>"])

        self._dispatch_bind_all(sequences, event)
        super_method = getattr(super(), "keyPressEvent", None)
        if callable(super_method):
            super_method(event)

    def keyReleaseEvent(self, event: Any) -> None:  # type: ignore[override]
        key = int(event.key())
        sequences: list[str] = []
        if key == int(Qt.Key.Key_Space):
            sequences.append("<KeyRelease-space>")
        elif key == int(Qt.Key.Key_Shift):
            sequences.extend(["<KeyRelease-Shift_L>", "<KeyRelease-Shift_R>"])
        self._dispatch_bind_all(sequences, event)
        super_method = getattr(super(), "keyReleaseEvent", None)
        if callable(super_method):
            super_method(event)

    def wheelEvent(self, event: Any) -> None:  # type: ignore[override]
        mods = event.modifiers()
        sequences: list[str] = []
        if bool(mods & Qt.KeyboardModifier.ShiftModifier):
            sequences.append("<Shift-MouseWheel>")
        else:
            sequences.append("<MouseWheel>")
        self._dispatch_bind_all(sequences, event)
        super_method = getattr(super(), "wheelEvent", None)
        if callable(super_method):
            super_method(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        """Despacha `bind_all('<ButtonPress-1>')` para cualquier widget (cerrar overlays, etc.)."""
        if isinstance(event, QMouseEvent) and isinstance(watched, QWidget):
            if event.button() == Qt.MouseButton.LeftButton:
                if event.type() == QEvent.Type.MouseButtonPress:
                    class _SyntheticPress:
                        pass

                    se = _SyntheticPress()
                    se.widget = watched
                    self._dispatch_bind_all(["<ButtonPress-1>"], se)
                elif event.type() == QEvent.Type.MouseButtonRelease:
                    class _SyntheticRelease:
                        pass

                    se = _SyntheticRelease()
                    se.widget = watched
                    self._dispatch_bind_all(["<ButtonRelease-1>"], se)
        return False

    def focus_get(self) -> Any:
        # Tk-like helper: devuelve el widget con foco actual.
        try:
            from PySide6.QtWidgets import QApplication

            return QApplication.focusWidget()
        except Exception:
            return None

    # ---- Compat Tk: configure/cget para el root ----
    def configure(self, **kwargs: Any) -> None:
        if "bg" in kwargs:
            self._qt_bg = str(kwargs["bg"])
        if "background" in kwargs:
            self._qt_bg = str(kwargs["background"])
        if self._qt_bg:
            try:
                self.setStyleSheet(f"background-color: {self._qt_bg};")
            except Exception:
                pass

    def cget(self, key: str) -> str:
        k = str(key)
        if k in {"bg", "background"}:
            return self._qt_bg
        return ""

    # Alias Tk: `root.title("...")` -> Qt `setWindowTitle`.
    def title(self, text: str) -> None:
        try:
            self.setWindowTitle(str(text))
        except Exception:
            pass

