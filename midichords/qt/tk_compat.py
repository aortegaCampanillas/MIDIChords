from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QSizePolicy,
)

from midichords.qt.qt_primitives import QtCanvas, QtBooleanVar, QtStringVar, _font_from_tk_tuple

# ---- Constantes estilo tkinter (subset) ----
LEFT = "left"
RIGHT = "right"
TOP = "top"
BOTTOM = "bottom"
HORIZONTAL = "horizontal"
VERTICAL = "vertical"
X = "x"
Y = "y"
BOTH = "both"

CENTER = "center"
N = "n"
S = "s"
E = "e"
W = "w"
NW = "nw"
NE = "ne"
SW = "sw"
SE = "se"

SUNKEN = "sunken"
FLAT = "flat"
ROUND = 1  # usado como valor booleano para capstyle/joinstyle en el código

NORMAL = "normal"
DISABLED = "disabled"

# tkinter.Canvas.create_arc style (valores literales de tkinter)
PIESLICE = "pieslice"
ARC = "arc"
CHORD = "chord"


def _qt_grid_attach_widget(widget: QWidget, row: int, column: int, **kwargs: Any) -> None:
    """Coloca un hijo en el QGridLayout del padre (equiv. aprox. a Tk grid + columnconfigure)."""
    parent = widget.parentWidget()
    if parent is None:
        return
    grid = parent.layout()
    if grid is None or not isinstance(grid, QGridLayout):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        parent.setLayout(grid)
    _qt_apply_parent_frame_padding(parent, grid)
    sticky_kw = str(kwargs.get("sticky", "") or "")
    row_span = int(kwargs.get("rowspan", 1) or 1)
    col_span = int(kwargs.get("columnspan", 1) or 1)
    align, h_exp, v_exp = _parse_grid_sticky(sticky_kw)
    hp = QSizePolicy.Policy.Expanding if h_exp else QSizePolicy.Policy.Preferred
    vp = QSizePolicy.Policy.Expanding if v_exp else QSizePolicy.Policy.Preferred
    if h_exp or v_exp:
        widget.setSizePolicy(hp, vp)
    if row_span > 1 or col_span > 1:
        grid.addWidget(widget, int(row), int(column), row_span, col_span, align)
    else:
        grid.addWidget(widget, int(row), int(column), align)
    for col, w in getattr(parent, "_tk_col_weights", {}).items():
        grid.setColumnStretch(int(col), int(w))
    for r, w in getattr(parent, "_tk_row_weights", {}).items():
        grid.setRowStretch(int(r), int(w))
    widget.setVisible(True)


def _parse_ttk_padding(p: Any) -> tuple[int, int, int, int]:
    """Convierte `padding` de ttk (1–4 valores) a (left, top, right, bottom)."""
    if p is None:
        return (0, 0, 0, 0)
    if isinstance(p, (int, float)):
        v = int(p)
        return (v, v, v, v)
    if isinstance(p, (tuple, list)):
        seq = [int(x) for x in p]
        n = len(seq)
        if n == 0:
            return (0, 0, 0, 0)
        if n == 1:
            v = seq[0]
            return (v, v, v, v)
        if n == 2:
            x, y = seq[0], seq[1]
            return (x, y, x, y)
        if n == 3:
            top, lr, bot = seq[0], seq[1], seq[2]
            return (lr, top, lr, bot)
        return (seq[0], seq[1], seq[2], seq[3])
    try:
        v = int(p)  # type: ignore[arg-type]
        return (v, v, v, v)
    except (TypeError, ValueError):
        return (0, 0, 0, 0)


def _qt_apply_parent_frame_padding(parent: QWidget, layout: Any) -> None:
    """Aplica `padding` tipo ttk al layout del contenedor (si se definió en el Widget)."""
    pads = getattr(parent, "_tk_frame_padding", None)
    if pads is None:
        return
    l, t, r, b = pads
    try:
        layout.setContentsMargins(int(l), int(t), int(r), int(b))
    except Exception:
        pass


def _parse_grid_sticky(sticky: str) -> tuple[Qt.AlignmentFlag, bool, bool]:
    """Convierte sticky de Tk grid a alineación Qt y flags de expansión."""
    s = (sticky or "").strip().lower()
    if not s:
        return Qt.AlignmentFlag.AlignCenter, False, False
    if "nsew" in s:
        return Qt.AlignmentFlag(0), True, True
    h_fill = "e" in s and "w" in s
    v_fill = "n" in s and "s" in s
    # QGridLayout: con alignment != 0 el hijo NO se estira a la celda (usa sizeHint/mínimo).
    # Sticky ew / ns / combinaciones de relleno deben usar 0 para llenar la celda
    # (p. ej. sliders BPM/volumen: si no, un canvas con minWidth=1 queda invisible).
    if h_fill or v_fill:
        return Qt.AlignmentFlag(0), h_fill, v_fill
    a = Qt.AlignmentFlag(0)
    if "n" in s:
        a |= Qt.AlignmentFlag.AlignTop
    if "s" in s:
        a |= Qt.AlignmentFlag.AlignBottom
    if "e" in s:
        a |= Qt.AlignmentFlag.AlignRight
    if "w" in s:
        a |= Qt.AlignmentFlag.AlignLeft
    if a == Qt.AlignmentFlag(0):
        a = Qt.AlignmentFlag.AlignCenter
    else:
        if not (a & (Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignBottom)):
            a |= Qt.AlignmentFlag.AlignVCenter
        if not (a & (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight)):
            a |= Qt.AlignmentFlag.AlignHCenter
    return a, h_fill, v_fill


def _qt_box_layout_index_of_widget(layout: QVBoxLayout | QHBoxLayout, target: QWidget) -> int | None:
    """Índice del ítem cuyo widget es `target`, o None si no está en el layout."""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is None:
            continue
        w = item.widget()
        if w is target:
            return i
    return None


def qt_pack_attach(widget: QWidget, **kwargs: Any) -> None:
    """Empaquetado estilo Tk: `padx`/`pady` son márgenes por widget (entre hermanos).

    Antes se usaba `QBoxLayout.setSpacing(left+right)`, lo que unificaba mal el hueco
    y el último `pack` lo sobrescribía (p. ej. ⚙ pegado a ♭, o #/♭ sin separación).
    """
    before_w = kwargs.pop("before", None)
    after_w = kwargs.pop("after", None)
    parent = widget.parentWidget()
    if parent is None:
        return
    # A diferencia de Tk (donde volver a llamar pack() sobre un widget ya
    # empaquetado es idempotente), insertWidget() sin retirar primero deja
    # huérfano el QSpacerItem de padding de la llamada anterior: se repite
    # pack(side=..., padx/pady=...) sobre el mismo widget sin pack_forget()
    # de por medio (p. ej. cada cambio de modo vuelve a hacer
    # instrument_view_switch_side.pack(side=tk.RIGHT, padx=(10, 0))), y cada
    # ciclo añade un spacer más, empujando el contenido progresivamente.
    # Retirar cualquier instancia previa (widget + su padding) antes de
    # insertar de nuevo hace la llamada idempotente, como en Tk.
    if parent.layout() is not None:
        _qt_remove_widget_from_parent_layout(widget)
    side = str(kwargs.get("side", TOP)).lower()
    padx = kwargs.get("padx", 0)
    pady = kwargs.get("pady", 0)
    if isinstance(padx, tuple):
        left_pad, right_pad = int(padx[0]), int(padx[1] if len(padx) > 1 else padx[0])
    else:
        left_pad = right_pad = int(padx or 0)
    if isinstance(pady, tuple):
        top_pad, bot_pad = int(pady[0]), int(pady[1] if len(pady) > 1 else pady[0])
    else:
        top_pad = bot_pad = int(pady or 0)
    fill = str(kwargs.get("fill", "")).lower()
    expand = bool(kwargs.get("expand", False))
    stretch = 1 if expand else 0

    if fill == X:
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    elif fill == Y:
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
    elif fill == BOTH:
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    else:
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    layout = parent.layout()
    if side in {LEFT, RIGHT}:
        if layout is None or not isinstance(layout, QHBoxLayout):
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            parent.setLayout(layout)
        else:
            layout.setSpacing(0)
        _qt_apply_parent_frame_padding(parent, layout)

        if side == RIGHT:
            if not getattr(parent, "_tk_pack_right_stretch", False):
                # Tk no "consume" espacio por un stretch ficticio al hacer pack(side=RIGHT);
                # en Qt ese stretch se queda y puede partir en dos el ancho de widgets
                # (p. ej. panel de teclado/guitarra en modo generación).
                layout.addStretch(0)
                setattr(parent, "_tk_pack_right_stretch", True)
            insert_at = 1
            if left_pad > 0:
                layout.insertSpacing(insert_at, left_pad)
                insert_at += 1
            layout.insertWidget(insert_at, widget, stretch)
            insert_at += 1
            if right_pad > 0:
                layout.insertSpacing(insert_at, right_pad)
        else:
            if left_pad > 0:
                layout.addSpacing(left_pad)
            layout.addWidget(widget, stretch)
            if right_pad > 0:
                layout.addSpacing(right_pad)
    else:
        if layout is None or not isinstance(layout, QVBoxLayout):
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            parent.setLayout(layout)
        else:
            layout.setSpacing(0)
        _qt_apply_parent_frame_padding(parent, layout)

        anchor_kw = str(kwargs.get("anchor", "") or "").strip().lower()

        def _vbox_alignment() -> Qt.AlignmentFlag:
            if anchor_kw in {"w", "nw", "sw"}:
                return Qt.AlignmentFlag.AlignLeft
            if anchor_kw in {"e", "ne", "se"}:
                return Qt.AlignmentFlag.AlignRight
            if anchor_kw in {"center", "n", "s"}:
                return Qt.AlignmentFlag.AlignHCenter
            return Qt.AlignmentFlag(0)

        valign = _vbox_alignment()

        if side == BOTTOM:
            if not getattr(parent, "_tk_pack_bottom_stretch", False):
                layout.addStretch(1)
                setattr(parent, "_tk_pack_bottom_stretch", True)
            insert_at = 1
            if top_pad > 0:
                layout.insertSpacing(insert_at, top_pad)
                insert_at += 1
            if valign != Qt.AlignmentFlag(0):
                layout.insertWidget(insert_at, widget, stretch, valign)
            else:
                layout.insertWidget(insert_at, widget, stretch)
            insert_at += 1
            if bot_pad > 0:
                layout.insertSpacing(insert_at, bot_pad)
        else:
            insert_idx: int | None = None
            if before_w is not None:
                insert_idx = _qt_box_layout_index_of_widget(layout, before_w)
            elif after_w is not None:
                j = _qt_box_layout_index_of_widget(layout, after_w)
                if j is not None:
                    insert_idx = j + 1
            if insert_idx is not None:
                if top_pad > 0:
                    layout.insertSpacing(insert_idx, top_pad)
                    insert_idx += 1
                if valign != Qt.AlignmentFlag(0):
                    layout.insertWidget(insert_idx, widget, stretch, valign)
                else:
                    layout.insertWidget(insert_idx, widget, stretch)
                insert_idx += 1
                if bot_pad > 0:
                    layout.insertSpacing(insert_idx, bot_pad)
            else:
                if top_pad > 0:
                    layout.addSpacing(top_pad)
                if valign != Qt.AlignmentFlag(0):
                    layout.addWidget(widget, stretch, valign)
                else:
                    layout.addWidget(widget, stretch)
                if bot_pad > 0:
                    layout.addSpacing(bot_pad)
    widget.setVisible(True)


def _qt_remove_widget_from_parent_layout(widget: QWidget) -> None:
    """Si el padre tiene QLayout y contiene este widget, lo saca (necesario para place absoluto).

    `qt_pack_attach` inserta hasta un `QSpacerItem` de padding inmediatamente
    antes y/o después del widget (left_pad/right_pad, top_pad/bot_pad). Esos
    spacers no están vinculados al widget (no tienen `.widget()`), así que si
    solo se quita el propio widget, quedan huérfanos en el layout. Repetir
    pack_forget()+pack() en el mismo padre (p. ej. al alternar entre modos
    que comparten un contenedor) los va acumulando indefinidamente,
    descuadrando el layout tras varios ciclos. Se eliminan aquí también.
    """
    parent = widget.parentWidget()
    if parent is None:
        return
    lay = parent.layout()
    if lay is None:
        return

    is_horizontal = isinstance(lay, QHBoxLayout)

    def _is_padding_spacer(layout_item: Any) -> bool:
        # Distingue el padding fijo (addSpacing/insertSpacing) del stretch
        # persistente de índice 0 (addStretch), que debe sobrevivir a
        # pack_forget() (solo se añade una vez por padre). addStretch marca
        # Expanding en el eje del layout (horizontal en QHBoxLayout, vertical
        # en QVBoxLayout); addSpacing/insertSpacing marcan Fixed en ese mismo
        # eje. El otro eje no es distintivo (Minimum en ambos casos).
        if layout_item is None or layout_item.widget() is not None:
            return False
        spacer = layout_item.spacerItem()
        if spacer is None:
            return False
        policy = spacer.sizePolicy()
        axis_policy = policy.horizontalPolicy() if is_horizontal else policy.verticalPolicy()
        return axis_policy == QSizePolicy.Policy.Fixed

    for i in range(lay.count()):
        item = lay.itemAt(i)
        if item is None:
            continue
        if item.widget() is widget:
            lay.takeAt(i)
            # El spacer siguiente (si lo hay) era el padding "después" del widget.
            if _is_padding_spacer(lay.itemAt(i)):
                lay.takeAt(i)
            # El spacer anterior (si lo hay) era el padding "antes" del widget.
            if i > 0 and _is_padding_spacer(lay.itemAt(i - 1)):
                lay.takeAt(i - 1)
            return


def _qt_pack_forget_widget(widget: QWidget) -> None:
    """Equiv. a Tk pack_forget: quitar del layout del padre y ocultar."""
    _qt_remove_widget_from_parent_layout(widget)
    widget.setVisible(False)


def _place_anchor_offset(anchor: str, w: int, h: int) -> tuple[int, int]:
    """Desplazamiento top-left del hijo para que el punto de anclaje quede en (refx, refy)."""
    a = (anchor or "nw").strip().lower()
    if a in {"nw"}:
        return 0, 0
    if a in {"n", "north"}:
        return int(round(-w / 2)), 0
    if a in {"ne"}:
        return -w, 0
    if a in {"w", "west"}:
        return 0, int(round(-h / 2))
    if a in {"center", "c"}:
        return int(round(-w / 2)), int(round(-h / 2))
    if a in {"e", "east"}:
        return -w, int(round(-h / 2))
    if a in {"sw"}:
        return 0, -h
    if a in {"s", "south"}:
        return int(round(-w / 2)), -h
    if a in {"se"}:
        return -w, -h
    return 0, 0


def _qt_place_widget(widget: QWidget, **kwargs: Any) -> None:
    """Tk place: x/y o relx/rely + relwidth/relheight; respeta anchor (p. ej. selector de modo)."""
    parent = widget.parentWidget()
    if parent is None:
        return
    _qt_remove_widget_from_parent_layout(widget)
    pw = max(0, int(parent.width()))
    ph = max(0, int(parent.height()))
    anchor = str(kwargs.get("anchor", "nw") or "nw")
    has_abs = any(k in kwargs for k in ("x", "y", "width", "height"))
    if has_abs:
        ref_x = int(kwargs.get("x", 0))
        ref_y = int(kwargs.get("y", 0))
        w_raw = kwargs.get("width")
        h_raw = kwargs.get("height")
        w = max(1, int(w_raw) if w_raw is not None else max(1, pw - ref_x))
        h = max(1, int(h_raw) if h_raw is not None else max(1, ph - ref_y))
        dx, dy = _place_anchor_offset(anchor, w, h)
        x = ref_x + dx
        y = ref_y + dy
    else:
        relx = float(kwargs.get("relx", 0.0))
        rely = float(kwargs.get("rely", 0.0))
        relw = float(kwargs.get("relwidth", 1.0))
        relh = float(kwargs.get("relheight", 1.0))
        w = max(1, int(round(pw * relw)))
        h = max(1, int(round(ph * relh)))
        cx = pw * relx
        cy = ph * rely
        dx, dy = _place_anchor_offset(anchor, w, h)
        x = int(round(cx + dx))
        y = int(round(cy + dy))
    widget.setGeometry(x, y, w, h)
    widget.setVisible(True)
    try:
        widget.raise_()
    except Exception:
        pass


class TclError(Exception):
    pass


class Event:
    # Solo para tipos; no se usa en runtime.
    def __init__(self, **_kwargs: Any) -> None:
        pass


class _BindMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._qt_bindings: dict[str, Callable[[Any], Any]] = {}

    def bind(self, sequence: str, func: Callable[[Any], Any], add: str | None = None) -> None:
        # `add` se ignora: en Tk controla si se reemplaza o se acumula.
        _ = add
        self._qt_bindings[str(sequence)] = func

    def _call_binding(self, sequence: str, event: Any) -> None:
        cb = self._qt_bindings.get(sequence)
        if cb is None:
            return
        try:
            cb(event)
        except TypeError:
            cb()

    # Hover (Enter/Leave)
    def enterEvent(self, event) -> None:  # type: ignore[override]
        super_method = getattr(super(), "enterEvent", None)
        if callable(super_method):
            super_method(event)
        self._call_binding("<Enter>", event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        super_method = getattr(super(), "leaveEvent", None)
        if callable(super_method):
            super_method(event)
        self._call_binding("<Leave>", event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        super_method = getattr(super(), "mousePressEvent", None)
        if callable(super_method):
            super_method(event)
        if event.button() == Qt.MouseButton.LeftButton:
            # Tk usa <ButtonPress-1> o <Button-1>; no disparar ambos si existieran.
            if "<ButtonPress-1>" in self._qt_bindings:
                self._call_binding("<ButtonPress-1>", event)
            else:
                self._call_binding("<Button-1>", event)

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        super_method = getattr(super(), "focusInEvent", None)
        if callable(super_method):
            super_method(event)
        self._call_binding("<FocusIn>", event)

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        super_method = getattr(super(), "focusOutEvent", None)
        if callable(super_method):
            super_method(event)
        self._call_binding("<FocusOut>", event)


class Widget(_BindMixin, QWidget):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        requested_width = kwargs.get("width")
        requested_height = kwargs.get("height")
        args = list(args)
        if args and isinstance(args[0], QMainWindow):
            main = args[0]
            central = main.centralWidget()
            if central is None:
                central = QWidget(main)
                main.setCentralWidget(central)
            args[0] = central
        # Tk pasa opciones que Qt no reconoce; bg/borde sí los aplicamos (paneles, overlays).
        bg_val = kwargs.pop("bg", None) or kwargs.pop("background", None)
        hl_thick = kwargs.pop("highlightthickness", None)
        hl_bgc = kwargs.pop("highlightbackground", None)
        kwargs.pop("highlightcolor", None)
        padding_raw = kwargs.pop("padding", None)
        self._tk_frame_padding: tuple[int, int, int, int] | None = (
            _parse_ttk_padding(padding_raw) if padding_raw is not None else None
        )
        if self._tk_frame_padding == (0, 0, 0, 0):
            self._tk_frame_padding = None
        for k in [
            "bd",
            "cursor",
            "relief",
            "padx",
            "pady",
            "width",
            "height",
            "highlightwidth",
        ]:
            kwargs.pop(k, None)
        QWidget.__init__(self, *args, **kwargs)
        _BindMixin.__init__(self)
        self._bg: str = str(bg_val or "")
        self._highlight_thickness: Any = hl_thick
        self._highlight_background: Any = hl_bgc
        # Pesos grid (Tk columnconfigure/rowconfigure weight)
        self._tk_col_weights: dict[int, int] = {}
        self._tk_row_weights: dict[int, int] = {}
        if requested_width is not None:
            try:
                self.setMinimumWidth(int(requested_width))
            except Exception:
                pass
        if requested_height is not None:
            try:
                self.setMinimumHeight(int(requested_height))
            except Exception:
                pass
        self._apply_tk_frame_surface()

    def _apply_tk_frame_surface(self) -> None:
        """Fondo y borde tipo Tk (highlightthickness + highlightbackground)."""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        bg = (self._bg or "").strip()
        if not bg:
            bg = "transparent"
        try:
            th = int(self._highlight_thickness) if self._highlight_thickness is not None else 0
        except (TypeError, ValueError):
            th = 0
        hc = self._highlight_background
        hc_s = str(hc).strip() if hc is not None else ""
        if th > 0 and hc_s:
            border = f"border: {th}px solid {hc_s};"
        elif th > 0:
            border = f"border: {th}px solid #888888;"
        else:
            # Sin borde explícito: el tema puede dibujar un marco de 1px entre celdas (p. ej. Acorde + nombre).
            border = "border: none; outline: none;"
        self.setStyleSheet(f"background-color: {bg}; {border}".strip())

    @property
    def master(self) -> Optional[QWidget]:
        """Compat Tk: widget padre (`parentWidget()` en Qt)."""
        return self.parentWidget()

    def winfo_children(self) -> list[QWidget]:
        return list(self.findChildren(QWidget))

    def winfo_width(self) -> int:
        return max(1, int(self.width()))

    def winfo_height(self) -> int:
        return max(1, int(self.height()))

    def winfo_reqwidth(self) -> int:
        return max(1, int(self.sizeHint().width()))

    def winfo_reqheight(self) -> int:
        return max(1, int(self.sizeHint().height()))

    def cget(self, key: str) -> str:
        if key in {"background", "bg"}:
            return self._bg
        return ""

    def configure(self, **kwargs: Any) -> None:
        # Compat mínima para bg/fg y state.
        if "bg" in kwargs:
            self._bg = str(kwargs["bg"])
        if "background" in kwargs:
            self._bg = str(kwargs["background"])
        if "highlightthickness" in kwargs:
            self._highlight_thickness = kwargs["highlightthickness"]
        if "highlightbackground" in kwargs:
            self._highlight_background = kwargs["highlightbackground"]
        if "padding" in kwargs:
            pr = kwargs["padding"]
            self._tk_frame_padding = _parse_ttk_padding(pr) if pr is not None else None
            if self._tk_frame_padding == (0, 0, 0, 0):
                self._tk_frame_padding = None
            lay = self.layout()
            if lay is not None:
                _qt_apply_parent_frame_padding(self, lay)
        if any(
            k in kwargs
            for k in ("bg", "background", "highlightthickness", "highlightbackground")
        ):
            self._apply_tk_frame_surface()
        if "state" in kwargs:
            st = str(kwargs["state"])
            self.setEnabled(st != DISABLED and st != "disabled" and st != "disabled")
        self.update()

    # Layout: pack/grid/place muy simplificado (funcional, no pixel-perfect).
    def _ensure_pack_layout(self) -> QVBoxLayout:
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)
        if not isinstance(layout, QVBoxLayout):
            # Caso raro: fallback a QVBoxLayout.
            new_layout = QVBoxLayout()
            new_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(new_layout)
            layout = new_layout
        return layout

    def pack(self, **kwargs: Any) -> None:
        qt_pack_attach(self, **kwargs)

    def pack_forget(self) -> None:
        _qt_pack_forget_widget(self)

    def pack_propagate(self, _flag: bool) -> None:
        # Tk usa pack_propagate para control de tamaño. En Qt no lo necesitamos.
        return

    def grid(self, row: int = 0, column: int = 0, **kwargs: Any) -> None:
        _qt_grid_attach_widget(self, row, column, **kwargs)

    def grid_remove(self) -> None:
        self.setVisible(False)

    def grid_forget(self) -> None:
        self.setVisible(False)

    def place(self, **kwargs: Any) -> None:
        _qt_place_widget(self, **kwargs)

    def focus_set(self) -> None:
        self.setFocus()

    def focus_get(self) -> Optional[QWidget]:
        return self.parentWidget().focusWidget() if self.parentWidget() is not None else None

    def destroy(self) -> None:
        # Tk uses destroy() to remove widget. En Qt usamos deleteLater().
        self.deleteLater()

    def nametowidget(self, _name: str) -> QWidget:
        raise KeyError(_name)

    def winfo_class(self) -> str:
        return self.__class__.__name__

    def winfo_manager(self) -> str:
        # Tk widget manager name; UiMixin usa "" para saber que no está colocado.
        return ""

    def columnconfigure(self, index: int, **_kwargs: Any) -> None:
        if "weight" in _kwargs:
            self._tk_col_weights[int(index)] = int(_kwargs["weight"])
            lay = self.layout()
            if isinstance(lay, QGridLayout):
                lay.setColumnStretch(int(index), int(_kwargs["weight"]))

    def rowconfigure(self, index: int, **_kwargs: Any) -> None:
        if "weight" in _kwargs:
            self._tk_row_weights[int(index)] = int(_kwargs["weight"])
            lay = self.layout()
            if isinstance(lay, QGridLayout):
                lay.setRowStretch(int(index), int(_kwargs["weight"]))


class Frame(Widget):
    pass


class Toplevel(_BindMixin, QDialog):
    def __init__(self, master: QWidget | None = None, **kwargs: Any) -> None:
        QDialog.__init__(self, master)
        _BindMixin.__init__(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._tk_col_weights: dict[int, int] = {}
        self._tk_row_weights: dict[int, int] = {}

    def title(self, text: str | None = None) -> str:
        if text is not None:
            self.setWindowTitle(text)
        return self.windowTitle()

    def focus_set(self) -> None:
        self.setFocus()

    def geometry(self, geom: str | None = None) -> str:
        if geom is None:
            rect = self.frameGeometry()
            return f"{rect.width()}x{rect.height()}+{rect.x()}+{rect.y()}"
        # Parse geometry string "WxH+X+Y"
        try:
            parts = geom.replace("+", "x").split("x")
            if len(parts) >= 2:
                w, h = int(parts[0]), int(parts[1])
                x = int(parts[2]) if len(parts) > 2 else 0
                y = int(parts[3]) if len(parts) > 3 else 0
                self.resize(w, h)
                if x > 0 or y > 0:
                    self.move(x, y)
                else:
                    # Centrar respecto al padre o a la pantalla
                    try:
                        from PySide6.QtWidgets import QApplication
                        screen = QApplication.primaryScreen().availableGeometry()
                        parent = self.parent()
                        if parent is not None:
                            pg = parent.frameGeometry()
                            cx = pg.x() + (pg.width() - w) // 2
                            cy = pg.y() + (pg.height() - h) // 2
                        else:
                            cx = (screen.width() - w) // 2
                            cy = (screen.height() - h) // 2
                        self.move(cx, cy)
                    except Exception:
                        pass
        except Exception:
            pass
        return self.geometry()

    def resizable(self, width: bool, height: bool) -> None:
        self.setSizeGripEnabled(width and height)

    def transient(self, parent: QWidget | None = None) -> None:
        if parent is not None:
            self.setParent(parent)

    def grab_set(self) -> None:
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def grab_release(self) -> None:
        self.setWindowModality(Qt.WindowModality.NonModal)

    def configure(self, **kwargs: Any) -> None:
        bg = kwargs.get("bg") or kwargs.get("background")
        if bg:
            self.setStyleSheet(f"background-color: {bg};")

    def columnconfigure(self, index: int, **kwargs: Any) -> None:
        self._tk_col_weights[index] = int(kwargs.get("weight", 0) or 0)

    def rowconfigure(self, index: int, **kwargs: Any) -> None:
        self._tk_row_weights[index] = int(kwargs.get("weight", 0) or 0)

    def pack(self, **kwargs: Any) -> None:
        pass  # No soportado para Toplevel

    def grid(self, **kwargs: Any) -> None:
        pass  # No soportado para Toplevel


class Label(Widget):
    def __init__(self, master: QWidget | None = None, text: str = "", **_kwargs: Any) -> None:
        _frame_kw: dict[str, Any] = {}
        for _k in (
            "bg",
            "background",
            "highlightthickness",
            "highlightbackground",
            "highlightcolor",
            "padding",
            "width",
            "height",
        ):
            if _k in _kwargs:
                _frame_kw[_k] = _kwargs.pop(_k)
        # El fondo va en el QLabel interno, no en el QWidget contenedor: si ambos llevan el mismo
        # color con WA_StyledBackground, Qt/macOS puede dibujar solo trozos de borde en las esquinas.
        self._label_bg: str = ""
        if "bg" in _frame_kw:
            self._label_bg = str(_frame_kw.pop("bg") or "")
        elif "background" in _frame_kw:
            self._label_bg = str(_frame_kw.pop("background") or "")
        super().__init__(master, **_frame_kw)
        self._textvariable: QtStringVar | None = _kwargs.pop("textvariable", None)
        self._wraplength: int | None = None
        wraplength = _kwargs.pop("wraplength", None)
        initial = str(self._textvariable.get()) if self._textvariable is not None else text
        self._label = QLabel(initial, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Sin esto el QLabel hijo recibe el clic y el `tk.Label` padre no dispara `<Button-1>` (p. ej. ⚙).
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        if wraplength is not None:
            try:
                wl = int(wraplength)
                if wl > 0:
                    self._wraplength = wl
                    self._label.setWordWrap(True)
                    self._label.setMaximumWidth(wl)
            except (TypeError, ValueError):
                pass
        _fg_raw = _kwargs.get("fg") or _kwargs.get("foreground")
        self._label_fg: str | None = None
        if _fg_raw is not None:
            s = str(_fg_raw).strip()
            self._label_fg = s if s else None
        self._apply_label_alignment(_kwargs)
        self._apply_label_style(_kwargs)
        cur = str(_kwargs.get("cursor", "") or "")
        if cur in {"hand2", "hand1"}:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        if self._textvariable is not None:

            def _sync_var(*_args: Any) -> None:
                self._label.setText(str(self._textvariable.get()))
                self._refresh_label_minsize()
                self.updateGeometry()

            self._textvariable.trace_add("write", _sync_var)
        self._label.setGeometry(0, 0, self.width(), self.height())
        self._refresh_label_minsize()
        self._apply_label_container_surface()

    def _apply_label_container_surface(self) -> None:
        """Contenedor transparente; el color de fondo real está solo en `self._label`."""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: transparent; border: none; outline: none; margin: 0; padding: 0;")

    def _apply_label_alignment(self, spec: dict[str, Any]) -> None:
        anchor = str(spec.get("anchor", "w") or "w").lower()
        justify = str(spec.get("justify", "left") or "left").lower()
        ha = Qt.AlignmentFlag.AlignLeft
        if anchor in {"center", "c"}:
            ha = Qt.AlignmentFlag.AlignHCenter
        elif anchor in {"e", "right"}:
            ha = Qt.AlignmentFlag.AlignRight
        va = Qt.AlignmentFlag.AlignVCenter
        if anchor in {"n", "nw", "ne"}:
            va = Qt.AlignmentFlag.AlignTop
        elif anchor in {"s", "sw", "se"}:
            va = Qt.AlignmentFlag.AlignBottom
        if justify == "center":
            ha = Qt.AlignmentFlag.AlignHCenter
        self._label.setAlignment(ha | va)

    def _refresh_label_minsize(self) -> None:
        # QLabel sin layout propio: hint mínimo para no colapsar en QLayout.
        fm = QFontMetrics(self._label.font())
        text = self._label.text() or " "
        max_w = int(self._label.maximumWidth())
        uses_wrap = bool(self._label.wordWrap()) and max_w < 16777215 - 1000

        if uses_wrap:
            w = max(1, max_w)
            br = fm.boundingRect(QRect(0, 0, w, 10_000_000), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, text)
            self.setMinimumSize(w + 8, max(br.height() + 8, fm.height() + 4))
        else:
            tw = max(1, fm.horizontalAdvance(text))
            th = max(1, fm.height())
            self.setMinimumSize(tw + 8, th + 4)

    def _apply_label_style(self, spec: dict[str, Any]) -> None:
        fg = spec.get("fg") or spec.get("foreground")
        if fg is None:
            fg = getattr(self, "_label_fg", None)
        bg = (getattr(self, "_label_bg", "") or "").strip() or "transparent"
        css_parts = [
            f"background-color: {bg};",
            "border: none;",
            "outline: none;",
            "margin: 0px;",
            "padding: 0px;",
        ]
        if fg is not None:
            css_parts.insert(0, f"color: {fg};")
        self._label.setStyleSheet(" ".join(css_parts))
        font_spec = spec.get("font")
        if font_spec is not None:
            self._label.setFont(_font_from_tk_tuple(font_spec))

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._label.setGeometry(0, 0, self.width(), self.height())

    def configure(self, **kwargs: Any) -> None:
        if "bg" in kwargs:
            self._label_bg = str(kwargs.pop("bg") or "")
        if "background" in kwargs:
            self._label_bg = str(kwargs.pop("background") or "")
        if "fg" in kwargs:
            v = kwargs.pop("fg", None)
            self._label_fg = str(v).strip() if v is not None and str(v).strip() else None
        if "foreground" in kwargs:
            v = kwargs.pop("foreground", None)
            self._label_fg = str(v).strip() if v is not None and str(v).strip() else None
        text = kwargs.get("text")
        if text is not None:
            self._label.setText(str(text))
            self._refresh_label_minsize()
        if "wraplength" in kwargs:
            wl_raw = kwargs.get("wraplength")
            try:
                wl = int(wl_raw) if wl_raw is not None else 0
            except (TypeError, ValueError):
                wl = 0
            if wl > 0:
                self._wraplength = wl
                self._label.setWordWrap(True)
                self._label.setMaximumWidth(wl)
            else:
                self._wraplength = None
                self._label.setWordWrap(False)
                self._label.setMaximumWidth(16777215)
            self._refresh_label_minsize()
        self._apply_label_alignment(kwargs)
        self._apply_label_style(kwargs)
        self._apply_label_container_surface()
        if "cursor" in kwargs and str(kwargs["cursor"]) in {"hand2", "hand1"}:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().configure(**kwargs)

    def cget(self, key: str) -> str:  # type: ignore[override]
        k = str(key)
        if k in {"background", "bg"}:
            return getattr(self, "_label_bg", "") or ""
        if k in {"fg", "foreground"}:
            return getattr(self, "_label_fg", "") or ""
        return super().cget(key)


class Button(Widget):
    def __init__(self, master: QWidget | None = None, text: str = "", command: Callable[[], None] | None = None, **_kwargs: Any) -> None:
        super().__init__(master)
        self._btn = QPushButton(text, self)
        self._btn.clicked.connect(command or (lambda: None))
        self._btn.setGeometry(0, 0, self.width(), self.height())
        self.setFixedSize(self._btn.size())

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._btn.setGeometry(0, 0, self.width(), self.height())

    def configure(self, **kwargs: Any) -> None:
        if "text" in kwargs:
            self._btn.setText(str(kwargs["text"]))
        super().configure(**kwargs)


class Radiobutton(Widget):
    def __init__(
        self,
        master: QWidget | None = None,
        text: str = "",
        variable: QtStringVar | None = None,
        value: str = "",
        command: Callable[[], None] | None = None,
        **_kwargs: Any,
    ) -> None:
        super().__init__(master)
        self._rb = QRadioButton(text, self)
        self._variable = variable
        self._value = value
        self._command = command
        if variable is not None:
            self._rb.setChecked(str(variable.get()) == str(value))
            variable.trace_add("write", lambda *_: self._rb.setChecked(str(self._variable.get()) == str(self._value)))  # type: ignore[union-attr]
        self._rb.toggled.connect(self._on_toggled)
        self._rb.adjustSize()
        self.setFixedSize(self._rb.size())

    def _on_toggled(self, checked: bool) -> None:
        if checked:
            if self._variable is not None:
                self._variable.set(self._value)
            if self._command is not None:
                self._command()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._rb.setGeometry(0, 0, self.width(), self.height())

    def configure(self, **kwargs: Any) -> None:
        if "text" in kwargs:
            self._rb.setText(str(kwargs["text"]))
        if "state" in kwargs:
            self._rb.setEnabled(str(kwargs["state"]) != DISABLED)
        super().configure(**kwargs)

    def pack(self, **kwargs: Any) -> None:
        super().pack(**kwargs)


class Entry(Widget):
    def __init__(self, master: QWidget | None = None, textvariable: QtStringVar | None = None, **_kwargs: Any) -> None:
        super().__init__(master)
        self._entry = QLineEdit(self)
        self._entry.setGeometry(0, 0, self.width(), self.height())
        self._entry.textChanged.connect(lambda v: textvariable.set(v) if textvariable is not None else None)
        self._textvariable = textvariable

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._entry.setGeometry(0, 0, self.width(), self.height())

    def configure(self, **kwargs: Any) -> None:
        if "state" in kwargs:
            self.setEnabled(str(kwargs["state"]) != DISABLED)
        super().configure(**kwargs)

    def focus_set(self) -> None:
        self._entry.setFocus()


class KeyboardStripScroll(QScrollArea):
    """Contenedor con scroll horizontal para el teclado (ancho mínimo por tecla blanca)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

    def _apply_wheel_scroll(self, event: Any) -> bool:
        """Aplica el scroll horizontal a partir de un wheelEvent. Retorna True si lo consumió."""
        try:
            from PySide6.QtCore import QEvent
            # pixelDelta: trackpad de alta resolución en macOS
            pixel = event.pixelDelta()
            angle = event.angleDelta()
            px, py = pixel.x(), pixel.y()
            ax, ay = angle.x(), angle.y()

            if px != 0 or py != 0:
                delta = px if abs(px) >= abs(py) else -py
            elif ax != 0 or ay != 0:
                delta = ax if abs(ax) >= abs(ay) else -ay
            else:
                return False

            bar = self.horizontalScrollBar()
            if bar is not None and delta != 0:
                bar.setValue(bar.value() - delta)
            event.accept()
            return True
        except Exception:
            return False

    def wheelEvent(self, event: Any) -> None:
        if not self._apply_wheel_scroll(event):
            super().wheelEvent(event)

    def eventFilter(self, obj: Any, event: Any) -> bool:
        try:
            from PySide6.QtCore import QEvent
            if event.type() == QEvent.Type.Wheel:
                if self._apply_wheel_scroll(event):
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def setWidget(self, widget: Any) -> None:
        super().setWidget(widget)
        # Instalar el filtro en el widget hijo y en el viewport para capturar
        # wheel events antes de que el hijo los consuma.
        try:
            if widget is not None:
                widget.installEventFilter(self)
            vp = self.viewport()
            if vp is not None:
                vp.installEventFilter(self)
        except Exception:
            pass

    def pack(self, **_kwargs: Any) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        side = str(_kwargs.get("side", TOP)).lower()
        fill = str(_kwargs.get("fill", "")).lower()
        expand = bool(_kwargs.get("expand", False))
        stretch = 1 if expand else 0
        if fill == X:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif fill == Y:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        elif fill == BOTH:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = parent.layout()
        if side in {LEFT, RIGHT}:
            if layout is None or not isinstance(layout, QHBoxLayout):
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                parent.setLayout(layout)
            if side == RIGHT:
                if not getattr(parent, "_tk_pack_right_stretch", False):
                    layout.addStretch(0)
                    setattr(parent, "_tk_pack_right_stretch", True)
                layout.addWidget(self, stretch)
            else:
                layout.addWidget(self, stretch)
        else:
            if layout is None or not isinstance(layout, QVBoxLayout):
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                parent.setLayout(layout)
            layout.addWidget(self, stretch)
        self.setVisible(True)

    def pack_forget(self) -> None:
        _qt_pack_forget_widget(self)


class Canvas(QtCanvas):
    def __init__(self, master: QWidget | None = None, **kwargs: Any) -> None:
        if isinstance(master, QMainWindow):
            central = master.centralWidget()
            if central is None:
                central = QWidget(master)
                master.setCentralWidget(central)
            master = central
        requested_width = kwargs.get("width")
        requested_height = kwargs.get("height")
        kwargs.pop("relief", None)
        super().__init__(master, **kwargs)
        if requested_width is not None:
            try:
                self.setMinimumWidth(int(requested_width))
            except Exception:
                pass
        if requested_height is not None:
            try:
                self.setMinimumHeight(int(requested_height))
            except Exception:
                pass

    # Layout helpers (subset tk): mismo comportamiento que Frame (incl. before/after).
    def pack(self, **_kwargs: Any) -> None:
        qt_pack_attach(self, **_kwargs)

    def pack_forget(self) -> None:
        _qt_pack_forget_widget(self)

    def grid(self, row: int = 0, column: int = 0, **_kwargs: Any) -> None:
        _qt_grid_attach_widget(self, row, column, **_kwargs)

    def grid_remove(self) -> None:
        self.setVisible(False)

    def grid_forget(self) -> None:
        self.setVisible(False)

    def place(self, **kwargs: Any) -> None:
        _qt_place_widget(self, **kwargs)

    def destroy(self) -> None:
        self.deleteLater()

    def configure(self, **_kwargs: Any) -> None:
        self.update()


# ---- Variables ----
StringVar = QtStringVar
BooleanVar = QtBooleanVar


class PhotoImage:
    def __init__(self, file: str | None = None, width: int | None = None, height: int | None = None, **_kwargs: Any) -> None:
        if file:
            self._pixmap = QPixmap(file)
        else:
            w = int(width or 1)
            h = int(height or 1)
            self._pixmap = QPixmap(w, h)
            self._pixmap.fill(Qt.GlobalColor.transparent)

    def width(self) -> int:
        return int(self._pixmap.width())

    def height(self) -> int:
        return int(self._pixmap.height())

    def zoom(self, x: int, y: int) -> "PhotoImage":
        w = max(1, self.width() * int(x))
        h = max(1, self.height() * int(y))
        out = PhotoImage(width=w, height=h)
        out._pixmap = self._pixmap.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return out

    def subsample(self, x: int, y: int) -> "PhotoImage":
        w = max(1, self.width() // int(max(1, x)))
        h = max(1, self.height() // int(max(1, y)))
        out = PhotoImage(width=w, height=h)
        out._pixmap = self._pixmap.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return out

    def toPixmap(self) -> QPixmap:
        return self._pixmap


# Alias para compat de imports que usan `tk.Misc`, etc.
Misc = QWidget

