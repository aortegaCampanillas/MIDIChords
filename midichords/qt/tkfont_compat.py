from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtGui import QFont, QFontDatabase, QFontMetricsF


def families(_root: Any = None) -> list[str]:
    # Tk returns a list of family names; order is not critical for this app.
    try:
        return list(QFontDatabase.families())
    except Exception:
        return ["Helvetica"]


@dataclass
class Font:
    family: str = "Helvetica"
    size: int = 12
    weight: str | int | None = None

    def __post_init__(self) -> None:
        qf = QFont(self.family)
        qf.setPointSize(int(self.size))
        if self.weight is not None and str(self.weight).lower() == "bold":
            qf.setBold(True)
        self._qfont = qf

    def measure(self, text: str) -> int:
        try:
            metrics = QFontMetricsF(self._qfont)
            return int(round(metrics.horizontalAdvance(str(text))))
        except Exception:
            return len(str(text)) * int(self.size * 0.6)


class _NoopNamedFont:
    def configure(self, **_kwargs: Any) -> None:
        pass


def nametofont(_name: str) -> _NoopNamedFont:
    return _NoopNamedFont()
