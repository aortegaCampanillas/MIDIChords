#!/usr/bin/env python3
"""
Si PyInstaller no incluyó Qt en el .app (p. ej. --collect-all PySide6 sin efecto),
copia los paquetes PySide6 y shiboken6 desde el venv de build a Contents/Frameworks.

Sin libqcocoa.dylib la app sale al instante en sandbox / TestFlight al importar Qt.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _has_cocoa_plugin(app: Path) -> bool:
    try:
        next(app.rglob("libqcocoa.dylib"))
        return True
    except StopIteration:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    p.add_argument("app_bundle", type=Path, help="Ruta al .app (p. ej. dist/MIDIChords.app)")
    args = p.parse_args()
    app = args.app_bundle.resolve()
    fw = app / "Contents" / "Frameworks"
    if not fw.is_dir():
        print(f"error: no existe {fw} (¿es un bundle .app válido?)", file=sys.stderr)
        return 1

    if _has_cocoa_plugin(app):
        print("Qt: libqcocoa.dylib ya está en el bundle.")
        return 0

    try:
        import PySide6  # noqa: F401
        import shiboken6  # noqa: F401
    except ImportError as e:
        print(
            "error: no se puede importar PySide6/shiboken6 con este intérprete. "
            "Instala requirements.txt y pyinstaller-hooks-contrib en el venv MAS.",
            file=sys.stderr,
        )
        print(f"  ({e})", file=sys.stderr)
        return 1

    import PySide6 as _ps
    import shiboken6 as _sh

    for mod in (_ps, _sh):
        src = Path(mod.__file__).resolve().parent
        dest = fw / mod.__name__
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, symlinks=True)
        print(f"incrustado {mod.__name__}: {src} -> {dest}", file=sys.stderr)

    if not _has_cocoa_plugin(app):
        print(
            "error: tras copiar PySide6/shiboken6 sigue sin encontrarse libqcocoa.dylib en el .app.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
