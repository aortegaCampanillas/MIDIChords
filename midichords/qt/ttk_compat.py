from __future__ import annotations

from typing import Any, Callable, Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QPaintEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QScrollBar,
)

from midichords.qt.qt_primitives import _font_from_tk_tuple
from midichords.qt.tk_compat import (
    BooleanVar,
    Frame,
    Label as TkLabel,
    StringVar,
    _qt_grid_attach_widget,
    _qt_pack_forget_widget,
    _qt_place_widget,
    qt_pack_attach,
)


class Style:
    def configure(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def map(self, *_args: Any, **_kwargs: Any) -> None:
        pass


class _BindMixin:
    def bind(self, sequence: str, func: Callable[..., None]) -> None:
        # Solo eventos usados por la app: "<<ComboboxSelected>>" y "<Return>".
        self._binding = (sequence, func)


class Frame(Frame):
    pass


class Label(TkLabel):
    pass


class _LayoutCompat:
    def pack(self, **_kwargs: Any) -> None:
        qt_pack_attach(self, **_kwargs)

    def pack_forget(self) -> None:
        _qt_pack_forget_widget(self)

    def grid(self, row: int = 0, column: int = 0, **kwargs: Any) -> None:
        _qt_grid_attach_widget(self, row, column, **kwargs)

    def grid_remove(self) -> None:
        self.setVisible(False)

    def grid_forget(self) -> None:
        self.setVisible(False)

    def place(self, **kwargs: Any) -> None:
        _qt_place_widget(self, **kwargs)

    def destroy(self) -> None:
        self.deleteLater()


class Button(QPushButton, _LayoutCompat):
    def __init__(self, master=None, text: str = "", command: Callable[[], None] | None = None, **_kwargs: Any) -> None:
        super().__init__(text, master)
        if command is not None:
            # En Qt `clicked` se emite al soltar; para que el feedback (p. ej.
            # 🔊 de previsualización) ocurra al instante del pulsado, usamos
            # la señal `pressed`.
            self.pressed.connect(command)

    def configure(self, **kwargs: Any) -> None:
        if "state" in kwargs:
            self.setEnabled(str(kwargs["state"]).lower() != "disabled")


class Checkbutton(QCheckBox, _LayoutCompat):
    def __init__(self, master=None, text: str = "", variable: BooleanVar | None = None, command: Callable[[], None] | None = None, **_kwargs: Any) -> None:
        font_spec = _kwargs.pop("font", None)
        super().__init__(text, master)
        if font_spec is not None:
            self.setFont(_font_from_tk_tuple(font_spec))
        self._variable = variable
        if command is not None:
            self.clicked.connect(command)
        if variable is not None:
            self.setChecked(bool(variable.get()))
            self.stateChanged.connect(lambda _: variable.set(self.isChecked()))

    def configure(self, **kwargs: Any) -> None:
        if "state" in kwargs:
            self.setEnabled(str(kwargs["state"]) != "disabled")
        if "text" in kwargs:
            # Compat: en Tk/ttk se usa configure(text=...) para actualizar la etiqueta.
            self.setText(str(kwargs["text"]))


class Radiobutton(QRadioButton, _LayoutCompat):
    def __init__(self, master=None, text: str = "", variable: StringVar | None = None, value: str | None = None, command: Callable[[], None] | None = None, **_kwargs: Any) -> None:
        font_spec = _kwargs.pop("font", None)
        super().__init__(text, master)
        if font_spec is not None:
            self.setFont(_font_from_tk_tuple(font_spec))
        self._variable = variable
        self._value = str(value) if value is not None else ""
        if command is not None:
            self.toggled.connect(command)
        if variable is not None:
            is_selected = str(variable.get()) == self._value
            self.setChecked(is_selected)
            self.toggled.connect(lambda checked: self._on_toggled(checked, variable))

    def _on_toggled(self, checked: bool, variable: StringVar) -> None:
        if checked:
            variable.set(self._value)

    def configure(self, **kwargs: Any) -> None:
        if "state" in kwargs:
            self.setEnabled(str(kwargs["state"]) != "disabled")
        if "text" in kwargs:
            self.setText(str(kwargs["text"]))


class Combobox(QComboBox, _LayoutCompat):
    def __init__(
        self,
        master=None,
        textvariable: StringVar | None = None,
        state: str | None = None,
        values: list[str] | None = None,
        width: int | None = None,
        **_kwargs: Any,
    ) -> None:
        font_spec = _kwargs.pop("font", None)
        postcommand = _kwargs.pop("postcommand", None)
        super().__init__(master)
        self._postcommand: Callable[[], None] | None = (
            cast(Callable[[], None], postcommand) if callable(postcommand) else None
        )
        if font_spec is not None:
            self.setFont(_font_from_tk_tuple(font_spec))
        self._textvariable = textvariable
        if values:
            self.addItems([str(v) for v in values])
        if width is not None:
            # ttk width suele ser "caracteres". Aproximamos.
            self.setMinimumWidth(max(80, int(width) * 9))
        if state == "readonly":
            self.setEditable(False)
        if textvariable is not None:
            # Inicialización desde var.
            current = str(textvariable.get())
            if current in [self.itemText(i) for i in range(self.count())]:
                self.setCurrentText(current)
            self.currentTextChanged.connect(lambda v: textvariable.set(v))

    def showPopup(self) -> None:  # type: ignore[override]
        if self._postcommand is not None:
            try:
                self._postcommand()
            except Exception:
                pass
        super().showPopup()

    def configure(self, **kwargs: Any) -> None:
        if "postcommand" in kwargs:
            pc = kwargs.pop("postcommand")
            self._postcommand = cast(Callable[[], None], pc) if callable(pc) else None
        if "values" in kwargs:
            # Tk/ttk suelen actualizar sin re-disparar callbacks en bucles.
            # Para evitar recursión en el shim, bloqueamos señales durante el refresh.
            self.blockSignals(True)
            try:
                self.clear()
                items = [str(v) for v in kwargs["values"]]
                self.addItems(items)
                # Tras `clear()`+`addItems()` Qt suele dejar el índice en 0 (p. ej. "").
                # Solo enlazamos combo→var (`currentTextChanged`), no var→combo: si otro
                # código repuebla `values` (p. ej. Ajustes al abrir un combo), el otro
                # combobox parece “borrarse” aunque el StringVar siga bien.
                if self._textvariable is not None:
                    tv = str(self._textvariable.get())
                    if tv in items:
                        self.setCurrentText(tv)
            finally:
                self.blockSignals(False)
        if "state" in kwargs:
            st = str(kwargs["state"]).lower()
            self.setEnabled(st != "disabled")

    def bind(self, sequence: str, func: Callable[..., None]) -> None:  # type: ignore[override]
        if sequence == "<<ComboboxSelected>>":
            self.currentIndexChanged.connect(lambda _idx=None: func(None))

    def __setitem__(self, key: str, value: Any) -> None:
        k = str(key)
        if k == "values":
            self.configure(values=list(value))
        elif k == "state":
            st = str(value).lower()
            self.setEnabled(st != "disabled")

    def __getitem__(self, key: str) -> Any:
        k = str(key)
        if k == "values":
            return [self.itemText(i) for i in range(self.count())]
        if k == "state":
            return "disabled" if not self.isEnabled() else "normal"
        raise KeyError(key)


class HandednessComboBox(Combobox):
    """Flecha del desplegable dibujada en `paintEvent` (QSS `image:` en `::down-arrow` suele fallar en macOS/Qt)."""

    def __init__(self, master=None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._arrow_pix: QPixmap | None = None
        try:
            from midichords.core.app_constants import ASSETS_DIR

            p = ASSETS_DIR / "ui" / "combo_arrow_down.png"
            if p.is_file():
                pix = QPixmap()
                if pix.load(str(p)):
                    self._arrow_pix = pix
        except Exception:
            self._arrow_pix = None

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if self._arrow_pix is None or self._arrow_pix.isNull():
            return
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            if not self.isEnabled():
                painter.setOpacity(0.45)
            aw = self._arrow_pix.width()
            ah = self._arrow_pix.height()
            margin = 6
            x = float(self.width()) - margin - aw
            y = (float(self.height()) - ah) / 2.0
            painter.drawPixmap(int(round(x)), int(round(y)), self._arrow_pix)
        finally:
            painter.end()


class Spinbox(QSpinBox, _LayoutCompat):
    def __init__(
        self,
        master=None,
        textvariable: StringVar | None = None,
        from_: int = 0,
        to: int = 100,
        width: int | None = None,
        **_kwargs: Any,
    ) -> None:
        font_spec = _kwargs.pop("font", None)
        super().__init__(master)
        if font_spec is not None:
            self.setFont(_font_from_tk_tuple(font_spec))
        self.setRange(int(from_), int(to))
        self._textvariable = textvariable
        if textvariable is not None:
            try:
                self.setValue(int(float(textvariable.get())))
            except Exception:
                self.setValue(int(from_))
            self.valueChanged.connect(lambda v: textvariable.set(str(v)))

    def configure(self, **kwargs: Any) -> None:
        if "state" in kwargs:
            st = str(kwargs["state"]).lower()
            self.setEnabled(st != "disabled")

    def bind(self, _sequence: str, _func: Callable[..., None]) -> None:
        # Se ignorará por simplicidad (en esta migración funcional).
        pass


class Scrollbar(QScrollBar, _LayoutCompat):
    def __init__(self, master=None, orient: Any = Qt.Orientation.Vertical, command: Callable[..., Any] | None = None, **_kwargs: Any) -> None:
        super().__init__(orient, master)
        if command is not None:
            # Cuando el scrollbar cambia, notifica.
            self.valueChanged.connect(lambda _v: command("moveto", _v))

