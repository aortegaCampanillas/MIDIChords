"""Primitivas Qt para la migración del desktop (Tkinter -> PySide6).

Este módulo intenta ofrecer pequeñas abstracciones (Canvas-like, Vars-like y
`after`/`after_cancel`) para reducir cambios en la lógica de los mixins.
"""

from .qt_primitives import QtCanvas, QtStringVar, QtBooleanVar, QtSchedulerMixin

__all__ = [
    "QtCanvas",
    "QtStringVar",
    "QtBooleanVar",
    "QtSchedulerMixin",
]

