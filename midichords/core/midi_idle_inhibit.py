"""Inhibir reposo de pantalla / sistema mientras hay actividad MIDI en detección.

Equivalente práctico al wakelock móvil: cada evento renueva una ventana (~3 min).
- Windows: SetThreadExecutionState (ctypes, sin dependencias).
- macOS: `caffeinate -di` en subproceso.
- Linux: no implementado (ampliar con dbus/systemd si hace falta).
"""

from __future__ import annotations

import atexit
import ctypes
import subprocess
import sys
import threading
from typing import Optional

_DURATION_SEC = 180.0

_timer: Optional[threading.Timer] = None
_timer_lock = threading.Lock()
_caffeinate_proc: Optional[subprocess.Popen] = None


def _win_set_busy(busy: bool) -> None:
    if sys.platform != "win32":
        return
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        if busy:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
        else:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except Exception:
        pass


def _darwin_ensure_caffeinate() -> None:
    global _caffeinate_proc
    if sys.platform != "darwin":
        return
    if _caffeinate_proc is not None and _caffeinate_proc.poll() is None:
        return
    _caffeinate_proc = None
    try:
        _caffeinate_proc = subprocess.Popen(
            ["caffeinate", "-di"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        _caffeinate_proc = None


def _darwin_stop_caffeinate() -> None:
    global _caffeinate_proc
    if _caffeinate_proc is None:
        return
    try:
        _caffeinate_proc.terminate()
        try:
            _caffeinate_proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            _caffeinate_proc.kill()
    except Exception:
        pass
    _caffeinate_proc = None


def _release_platform() -> None:
    if sys.platform == "win32":
        _win_set_busy(False)
    elif sys.platform == "darwin":
        _darwin_stop_caffeinate()


def _activate_platform() -> None:
    if sys.platform == "win32":
        _win_set_busy(True)
    elif sys.platform == "darwin":
        _darwin_ensure_caffeinate()


def _on_timer_fire() -> None:
    global _timer
    with _timer_lock:
        _timer = None
    _release_platform()


def bump_after_midi_detection_activity() -> None:
    """Llamar por cada note on/off MIDI procesado en modo detección."""
    _activate_platform()
    global _timer
    with _timer_lock:
        if _timer is not None:
            _timer.cancel()
        _timer = threading.Timer(_DURATION_SEC, _on_timer_fire)
        _timer.daemon = True
        _timer.start()


def cancel_midi_idle_inhibit() -> None:
    """Al salir de detección, cerrar app o desactivar MIDI."""
    global _timer
    with _timer_lock:
        if _timer is not None:
            _timer.cancel()
            _timer = None
    _release_platform()


def _atexit_release() -> None:
    try:
        cancel_midi_idle_inhibit()
    except Exception:
        pass


atexit.register(_atexit_release)
