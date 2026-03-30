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


def _frozen_mac_search_bases() -> list[Path]:
    """Posibles raíces donde PyInstaller dejó PySide6 (layout varía por versión)."""
    if not getattr(sys, "frozen", False) or sys.platform != "darwin":
        return []
    seen: set[Path] = set()
    out: list[Path] = []

    def add(p: Path) -> None:
        rp = p.resolve()
        if rp.is_dir() and rp not in seen:
            seen.add(rp)
            out.append(rp)

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        add(Path(meipass))
    exe = Path(sys.executable).resolve()
    add(exe.parent / "_internal")
    add(exe.parent)
    for parent in exe.parents:
        if parent.name == "Contents":
            add(parent / "Frameworks")
            add(parent / "Resources")
            break
    return out


def _plugins_dir_from_cocoa_dylib(cocoa: Path) -> Path | None:
    """.../plugins/platforms/libqcocoa.dylib -> .../plugins"""
    platforms = cocoa.parent
    if platforms.name != "platforms":
        return None
    plugins = platforms.parent
    return plugins if plugins.is_dir() else None


def _find_qt_plugins_dir_under(base: Path) -> Path | None:
    """Busca libqcocoa.dylib bajo base (p. ej. _MEIPASS)."""
    try:
        for cocoa in base.rglob("libqcocoa.dylib"):
            found = _plugins_dir_from_cocoa_dylib(cocoa.resolve())
            if found is not None:
                return found
    except OSError:
        return None
    return None


def _pick_qt_plugins_dir() -> tuple[Path | None, str]:
    """Devuelve (ruta plugins, motivo breve para log)."""
    bases = _frozen_mac_search_bases()
    rels = (
        "PySide6/Qt/plugins",
        "PySide6/lib/Qt/plugins",
        "PySide6/Qt6/plugins",
    )
    for base in bases:
        for rel in rels:
            p = (base / rel).resolve()
            if p.is_dir() and (p / "platforms").is_dir():
                return p, f"fixed:{rel} under {base.name}"
        found = _find_qt_plugins_dir_under(base)
        if found is not None:
            return found.resolve(), f"rglob under {base.name}"
    return None, "not_found"


def _write_bootstrap_log(
    *,
    plugins: Path | None,
    reason: str,
    meipass: str,
) -> None:
    try:
        log_dir = Path.home() / "Library" / "Application Support" / "MIDIChords"
        log_dir.mkdir(parents=True, exist_ok=True)
        exe = str(Path(sys.executable).resolve())
        text = (
            f"executable={exe}\n"
            f"_MEIPASS={meipass}\n"
            f"qt_plugins_reason={reason}\n"
            f"QT_PLUGIN_PATH={plugins}\n"
            f"QT_QPA_PLATFORM_PLUGIN_PATH={os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', '')}\n"
        )
        (log_dir / "mas_bootstrap_last.txt").write_text(text, encoding="utf-8")
    except OSError:
        pass


def apply_qt_plugin_path() -> None:
    """Debe llamarse antes de `import PySide6` / `QtWidgets`."""
    if not getattr(sys, "frozen", False) or sys.platform != "darwin":
        return
    meipass_s = str(getattr(sys, "_MEIPASS", "") or "")
    plugins, reason = _pick_qt_plugins_dir()
    if plugins is not None:
        pstr = str(plugins)
        os.environ["QT_PLUGIN_PATH"] = pstr
        platforms = plugins / "platforms"
        if platforms.is_dir():
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms.resolve())
    else:
        # Último recurso: lógica antigua por si rglob falla en volúmenes raros
        base = _bundle_resource_root()
        if base is not None:
            for rel in (
                "PySide6/Qt/plugins",
                "PySide6/lib/Qt/plugins",
                "PySide6/Qt6/plugins",
            ):
                p = base / rel
                if p.is_dir():
                    os.environ.setdefault("QT_PLUGIN_PATH", str(p.resolve()))
                    reason = f"fallback_setdefault:{rel}"
                    break
    os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")
    qp_raw = os.environ.get("QT_PLUGIN_PATH", "").strip()
    _write_bootstrap_log(
        plugins=Path(qp_raw) if qp_raw else None,
        reason=reason,
        meipass=meipass_s,
    )


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
