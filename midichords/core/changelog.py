"""Changelog loader and utilities."""

import json
from pathlib import Path
from typing import Any, Optional


def get_changelog_path() -> Path:
    """Obtiene la ruta al archivo changelog.json."""
    import sys
    # PyInstaller incluye el directorio compartido `assets`.
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets" / "changelog.json"  # type: ignore[attr-defined]
    try:
        from midichords.core.app_constants import PROJECT_ROOT
        return Path(PROJECT_ROOT) / "assets" / "changelog.json"
    except Exception:
        return Path("assets/changelog.json")


def load_changelog() -> list[dict[str, Any]]:
    """Carga el changelog.json y retorna la lista de versiones."""
    path = get_changelog_path()
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_changelog_items_for_platform(platform: str) -> list[dict[str, Any]]:
    """Retorna los items publicados para la plataforma especificada.

    Args:
        platform: 'web', 'desktop', o 'mobile'

    Returns:
        Lista de items {version, date, es, en, platforms, ...}
    """
    changelog = load_changelog()
    items = []

    for version_entry in changelog:
        for item in version_entry.get("items", []):
            if not item.get("publish", False):
                continue

            platforms = item.get("platforms", ["web"])
            if platform not in platforms:
                continue

            # Enriquecer el item con la versión
            enriched_item = {
                **item,
                "version": version_entry["version"],
                "version_date": version_entry["date"],
            }
            items.append(enriched_item)

    return items
