#!/usr/bin/env python3
"""Genera las copias empaquetables de los assets con fuente canónica compartida."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections.abc import Sequence
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_SOURCE = PROJECT_ROOT / "assets" / "changelog.json"
CHANGELOG_TARGETS = (
    PROJECT_ROOT / "apps" / "web" / "static" / "changelog.json",
    PROJECT_ROOT / "apps" / "mobile_flutter" / "assets" / "changelog.json",
)

# Fuente única de la versión de producto; escritorio, web y móvil se derivan de aquí.
VERSION_SOURCE = PROJECT_ROOT / "VERSION"
APP_CONSTANTS_PATH = PROJECT_ROOT / "midichords" / "core" / "app_constants.py"
WORKER_PATH = PROJECT_ROOT / "apps" / "web" / "worker" / "_worker.js"
WEB_APP_JS_PATH = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"
WEB_HTML_PATHS = (
    PROJECT_ROOT / "apps" / "web" / "app.html",
    PROJECT_ROOT / "apps" / "web" / "index.html",
)
PUBSPEC_PATH = PROJECT_ROOT / "apps" / "mobile_flutter" / "pubspec.yaml"


def _validate_changelog(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: falta la fuente canónica: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: changelog JSON inválido en {path}: {exc}") from exc
    if not isinstance(data, list):
        raise SystemExit(f"ERROR: el changelog debe contener una lista: {path}")


def sync_changelog(*, check: bool = False) -> tuple[Path, ...]:
    """Comprueba o actualiza las copias del changelog y devuelve las divergentes."""
    _validate_changelog(CHANGELOG_SOURCE)
    source_bytes = CHANGELOG_SOURCE.read_bytes()
    divergent = tuple(
        target
        for target in CHANGELOG_TARGETS
        if not target.is_file() or target.read_bytes() != source_bytes
    )
    if check:
        return divergent
    for target in divergent:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CHANGELOG_SOURCE, target)
    return divergent


def _read_version() -> str:
    try:
        text = VERSION_SOURCE.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"ERROR: falta la fuente canónica: {VERSION_SOURCE}") from exc
    version = text.strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit(
            f"ERROR: VERSION debe tener el formato X.Y.Z (leído: {version!r})"
        )
    return version


def _sync_regex(path: Path, pattern: str, replacement: str, *, flags: int = 0) -> bool:
    """Sustituye `pattern` por `replacement` en `path`; devuelve si cambió algo."""
    original = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, original, count=1, flags=flags)
    if count == 0:
        raise SystemExit(f"ERROR: no se encontró el patrón de versión esperado en {path}")
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def sync_version(*, check: bool = False) -> tuple[Path, ...]:
    """Comprueba o propaga /VERSION a escritorio, web y móvil. Devuelve lo divergente."""
    version = _read_version()
    targets: list[tuple[Path, str, str]] = [
        (
            APP_CONSTANTS_PATH,
            r'APP_RELEASE_NAME = "[^"]*"',
            f'APP_RELEASE_NAME = "{version}"',
        ),
        (
            WORKER_PATH,
            r'const APP_VERSION = "[^"]*";',
            f'const APP_VERSION = "{version}";',
        ),
        (
            WEB_APP_JS_PATH,
            r'const WEB_APP_VERSION_FALLBACK = "[^"]*";',
            f'const WEB_APP_VERSION_FALLBACK = "{version}";',
        ),
    ]
    for html_path in WEB_HTML_PATHS:
        targets.append((html_path, r'"softwareVersion": "[^"]*"', f'"softwareVersion": "{version}"'))

    divergent: list[Path] = []
    for path, pattern, replacement in targets:
        current = path.read_text(encoding="utf-8")
        if re.search(re.escape(replacement), current):
            continue
        divergent.append(path)
        if not check:
            _sync_regex(path, pattern, replacement)

    pubspec_current = PUBSPEC_PATH.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$", pubspec_current, re.MULTILINE)
    if not match:
        raise SystemExit(f"ERROR: no se encontró 'version: X.Y.Z+N' en {PUBSPEC_PATH}")
    pubspec_version, build_number = match.group(1), int(match.group(2))
    if pubspec_version != version:
        divergent.append(PUBSPEC_PATH)
        if not check:
            new_build = build_number + 1
            _sync_regex(
                PUBSPEC_PATH,
                r"^version:\s*\d+\.\d+\.\d+\+\d+\s*$",
                f"version: {version}+{new_build}",
                flags=re.MULTILINE,
            )

    return tuple(divergent)


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sincroniza assets generados desde sus fuentes canónicas.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="No escribe: falla si alguna copia no coincide con la fuente.",
    )
    args = parser.parse_args(argv)
    divergent = sync_changelog(check=args.check)
    if args.check and divergent:
        targets = ", ".join(_relative(path) for path in divergent)
        raise SystemExit(
            "ERROR: copias de changelog desactualizadas: "
            f"{targets}. Ejecuta: python scripts/sync_shared_assets.py"
        )
    if divergent:
        print(
            "Changelog sincronizado: "
            + ", ".join(_relative(path) for path in divergent)
        )
    else:
        print("Changelog ya sincronizado.")

    version_divergent = sync_version(check=args.check)
    if args.check and version_divergent:
        targets = ", ".join(_relative(path) for path in version_divergent)
        raise SystemExit(
            "ERROR: versión desactualizada respecto a VERSION en: "
            f"{targets}. Ejecuta: python scripts/sync_shared_assets.py"
        )
    if version_divergent:
        print(
            "Versión sincronizada: "
            + ", ".join(_relative(path) for path in version_divergent)
        )
    else:
        print("Versión ya sincronizada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
