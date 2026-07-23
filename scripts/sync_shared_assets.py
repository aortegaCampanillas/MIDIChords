#!/usr/bin/env python3
"""Genera las copias empaquetables de los assets con fuente canónica compartida."""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Sequence
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_SOURCE = PROJECT_ROOT / "assets" / "changelog.json"
CHANGELOG_TARGETS = (
    PROJECT_ROOT / "apps" / "web" / "static" / "changelog.json",
    PROJECT_ROOT / "apps" / "mobile_flutter" / "assets" / "changelog.json",
)


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
