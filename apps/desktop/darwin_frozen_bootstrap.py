"""
Ajustes de entorno *antes* de importar PySide6 en un .app de macOS empaquetado
(PyInstaller). Si los plugins de Qt no están en el PATH que Qt espera, la app
puede salir al instante (icono en Dock y cierre) sin crash report — típico en
Mac App Store / sandbox tras firma.

También instala un excepthook que escribe trazas en Application Support.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _bundle_resource_root() -> Path | None:
    """Directorio tipo _internal donde PyInstaller coloca PySide6 y assets."""
    if not getattr(sys, "frozen", False) or sys.platform != "darwin":
        return None
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    exe = Path(sys.executable).resolve()
    for cand in (exe.parent / "_internal", exe.parent):
        if cand.is_dir() and ((cand / "PySide6").exists() or (cand / "assets").exists()):
            return cand
    return exe.parent if exe.parent.is_dir() else None


def apply_qt_plugin_path() -> None:
    """Debe llamarse antes de `import PySide6` / `QtWidgets`."""
    base = _bundle_resource_root()
    if base is None:
        return
    for rel in (
        "PySide6/Qt/plugins",
        "PySide6/lib/Qt/plugins",
        "PySide6/Qt6/plugins",
    ):
        p = base / rel
        if p.is_dir():
            os.environ.setdefault("QT_PLUGIN_PATH", str(p.resolve()))
            break
    # Refuerzo en macOS (por defecto ya es cocoa)
    os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")


def install_crash_log_excepthook() -> None:
    """Solo errores Python; fallos nativos de Qt no pasan por aquí."""

    def _hook(exc_type, exc, tb) -> None:
        try:
            log_dir = Path.home() / "Library" / "Application Support" / "MIDIChords"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "python-startup-error.log"
            log_file.write_text(
                "".join(traceback.format_exception(exc_type, exc, tb)),
                encoding="utf-8",
            )
        except OSError:
            pass
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _hook


def bootstrap_before_qt() -> None:
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        apply_qt_plugin_path()
        install_crash_log_excepthook()
