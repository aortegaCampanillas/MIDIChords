from __future__ import annotations

from typing import Any, Callable, Optional, cast

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPaintEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QListView,
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
    """Sin uso en la app (metrónomo y configuración usan canvas propios en su
    lugar — ver `_draw_metronome_checkbox`/`_build_checkbox_row`): con el
    estilo nativo "windows11" de Qt, y también con Fusion, el indicador
    marcado solo pinta el check sin la caja alrededor. Si se reutiliza, probar
    antes visualmente en estado marcado."""

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
    """Sin uso en la app (Configuración usa `OverlaysMixin._build_radio_row`,
    canvas propio, en su lugar): con el estilo nativo "windows11" de Qt, y
    también con Fusion, el punto de la opción marcada no se pinta. Si se
    reutiliza, probar antes visualmente en estado marcado."""

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
        self._popup_bg: str = "#3a4452"
        self._postcommand: Callable[[], None] | None = (
            cast(Callable[[], None], postcommand) if callable(postcommand) else None
        )
        popup_view = QListView(self)
        popup_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        popup_view.setTextElideMode(Qt.TextElideMode.ElideRight)
        popup_view.setUniformItemSizes(False)
        popup_view.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        popup_view.viewport().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setView(popup_view)
        self.setMaxVisibleItems(8)
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
        self._position_popup_under_combo()
        QTimer.singleShot(0, self._position_popup_under_combo)

    def _position_popup_under_combo(self) -> None:
        view = self.view()
        if view is None:
            return
        try:
            combo_width = max(1, int(self.width()))
            row_count = max(1, int(self.count()))
            visible_rows = min(row_count, max(1, int(self.maxVisibleItems())))
            fallback_row_height = max(28, int(self.fontMetrics().height()) + 12)
            rows_height = 0
            for row in range(visible_rows):
                row_height = int(view.sizeHintForRow(row))
                rows_height += row_height if row_height > 0 else fallback_row_height
            popup_height = rows_height + (2 * int(view.frameWidth())) + 4
            popup_height = max(fallback_row_height + 6, popup_height)

            view.setMinimumWidth(combo_width)
            view.setMaximumWidth(combo_width)
            view.setFixedWidth(combo_width)
            view.setFixedHeight(popup_height)

            popup = view.window()
            if popup is not view:
                popup.setStyleSheet(f"background-color: {self._popup_bg};")
            popup.resize(combo_width, popup_height)
            popup.move(self.mapToGlobal(self.rect().bottomLeft()))
        except Exception:
            return

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
            # `activated` se emite después de que Qt actualiza currentIndex/currentText,
            # garantizando que StringVar ya tiene el nuevo valor cuando el handler lo lee.
            # `currentIndexChanged` se emitía antes y el var llegaba stale al handler.
            self.activated.connect(lambda _idx=None: func(None))

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
        command: Callable[[], None] | None = None,
        **_kwargs: Any,
    ) -> None:
        font_spec = _kwargs.pop("font", None)
        increment = _kwargs.pop("increment", None)
        super().__init__(master)
        # Nota: con el estilo nativo "windows11" de Qt, el hit-test de los
        # botones +/- de QSpinBox puede no coincidir con dónde se pintan (el
        # clic en la flecha cae sobre el campo de texto en vez de incrementar)
        # — visto en el temporizador del metrónomo, que por eso usa ahora los
        # botones -/+ redondos ya existentes en este panel en vez de este
        # widget. Si se reutiliza Spinbox en otro sitio, probar primero con
        # QTest.mouseClick en la posición real (style().subControlRect) antes
        # de asumir que el clic del usuario cae donde se ve la flecha.
        if font_spec is not None:
            self.setFont(_font_from_tk_tuple(font_spec))
        self.setRange(int(from_), int(to))
        if increment is not None:
            try:
                self.setSingleStep(int(increment))
            except (TypeError, ValueError):
                pass
        self._textvariable = textvariable
        if textvariable is not None:
            try:
                self.setValue(int(float(textvariable.get())))
            except Exception:
                self.setValue(int(from_))
            self.valueChanged.connect(lambda v: textvariable.set(str(v)))
        # Tk invoca `command` en cada cambio de valor (flechas, rueda, teclado);
        # sin esto, los +/- solo movían el número mostrado sin avisar al resto
        # de la app.
        if command is not None:
            self.valueChanged.connect(lambda _v: command())

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
