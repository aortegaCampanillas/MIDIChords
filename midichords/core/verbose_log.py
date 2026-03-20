"""Trazas opcionales (audio, MIDI) activadas con MIDICHORDS_VERBOSE o --verbose en launch."""

from __future__ import annotations

import os
import sys
import time
from typing import Any


def is_verbose() -> bool:
    v = os.environ.get("MIDICHORDS_VERBOSE", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def vlog(category: str, msg: str, *args: Any) -> None:
    """Escribe en stderr con prefijo de categoría si el modo verbose está activo."""
    if not is_verbose():
        return
    ts = time.strftime("%H:%M:%S")
    if args:
        try:
            body = msg % args
        except (TypeError, ValueError):
            body = f"{msg} {' '.join(str(a) for a in args)}"
    else:
        body = msg
    print(f"[{ts}] [MIDIChords:{category}] {body}", file=sys.stderr, flush=True)
