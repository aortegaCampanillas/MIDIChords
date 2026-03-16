from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class QtDetectionWindow(QMainWindow):
    """
    Ventana base para la futura UI Qt del modo Detection.
    De momento solo muestra un texto; servirá como punto de entrada estable.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MIDIChords (Qt Detection)")
        self.resize(1300, 800)

        label = QLabel(
            "MIDIChords – UI Qt (Detection)\n\n"
            "Esta ventana será la versión Qt del modo Detection.\n"
            "La lógica existente (audio, detección, MIDI) se reutilizará aquí.",
            self,
        )
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)


def run_qt_detection_app() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = QtDetectionWindow()
    window.show()
    app.exec()

from __future__ import annotations

import sys
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from midichords.qt_widgets import PianoWidget


MODES: Dict[str, str] = {
    "detection": "Detection (modo actual en Tkinter)",
    "generation": "Generation",
    "scales": "Scales",
    "metronome": "Metronome",
    "tuner": "Tuner",
}


class QtMidiChordAnalyzerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MIDIChords (Qt experimental)")
        self.resize(1300, 800)

        self._current_mode = "detection"
        self._mode_combo: QComboBox | None = None

        self._setup_toolbar()
        self._setup_central_layout()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Modes", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Combo de modo (similar al combo de Tkinter)
        mode_combo = QComboBox(toolbar)
        for mode_key, label in MODES.items():
            mode_combo.addItem(label, userData=mode_key)
        mode_combo.setCurrentIndex(list(MODES.keys()).index(self._current_mode))
        mode_combo.currentIndexChanged.connect(self._on_mode_combo_changed)  # type: ignore[arg-type]
        toolbar.addWidget(mode_combo)
        self._mode_combo = mode_combo

    def _setup_central_layout(self) -> None:
        """
        Layout principal inspirado en el modo Detection de Tkinter:
        - Izquierda: piano.
        - Derecha: placeholder de acordes / info.
        - Abajo: barra con texto de estado (por ahora).
        """
        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 8, 12, 12)
        root_layout.setSpacing(8)

        # Fila principal: piano + panel derecho
        main_row = QHBoxLayout()
        main_row.setSpacing(8)

        # Piano a la izquierda
        self._piano = PianoWidget(central)
        main_row.addWidget(self._piano, 3)

        # Panel derecho (placeholder)
        right_panel = QWidget(central)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(4)

        self._info_label = QLabel(right_panel)
        self._info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_layout.addWidget(self._info_label)

        main_row.addWidget(right_panel, 2)
        root_layout.addLayout(main_row, 1)

        # Barra inferior de estado (placeholder)
        self._status_label = QLabel(central)
        self._status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root_layout.addWidget(self._status_label, 0)

        self.setCentralWidget(central)

        self._update_central_label()

    def _update_central_label(self) -> None:
        human_label = MODES.get(self._current_mode, self._current_mode)
        self._info_label.setText(
            f"<b>Qt UI experimental</b><br><br>"
            f"<b>Modo actual:</b> {human_label}<br><br>"
            "Aquí migrarán el teclado, la guitarra y el resto de controles "
            "desde la versión Tkinter."
        )
        self._status_label.setText("Listo. (Estado Qt experimental; sin lógica aún).")

    def _on_mode_combo_changed(self, index: int) -> None:
        if index < 0 or index >= len(MODES):
            return
        if self._mode_combo is None:
            return
        mode_key = self._mode_combo.itemData(index)
        if isinstance(mode_key, str):
            self._current_mode = mode_key
            self._update_central_label()


def run_qt_app() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = QtMidiChordAnalyzerWindow()
    window.show()
    app.exec()

