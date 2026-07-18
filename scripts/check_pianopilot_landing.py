#!/usr/bin/env python3
"""Valida los datos públicos de PianoPilot y, si existe, su repositorio fuente."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "apps/web/static/fp30x/product.json"
SIBLING_ROOT = ROOT.parent / "RolandFP30xController"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _project_version(pyproject_path: Path) -> str:
    match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        pyproject_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise AssertionError("No se encontró la versión de PianoPilot en pyproject.toml")
    return match.group(1)


def _tone_count(catalog_path: Path) -> int:
    module = ast.parse(catalog_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "TONE_PRESETS":
            if not isinstance(node.value, ast.List):
                break
            return len(node.value.elts)
    raise AssertionError("No se encontró TONE_PRESETS en el catálogo de PianoPilot")


def check_manifest(manifest: dict) -> None:
    assert manifest["product"] == "PianoPilot"
    assert manifest["supported_model"] == "Roland FP-30X"
    assert manifest["connections"]["bluetooth_audio"] is False
    assert manifest["tone_count"] > 0
    assert manifest["release_notes"][0]["version"] == manifest["version"]
    for release in manifest["release_notes"]:
        assert release["en"] and release["es"]


def check_sibling(manifest: dict) -> None:
    if not SIBLING_ROOT.is_dir():
        print("[pianopilot] Repositorio hermano ausente; validación local completada.")
        return

    source_notes = _load_json(
        SIBLING_ROOT / "src/roland_fp30x_controller/resources/whatsnew.json"
    )
    source_releases = sorted(
        source_notes["versions"], key=lambda release: release["version"], reverse=True
    )
    assert manifest["version"] == _project_version(SIBLING_ROOT / "pyproject.toml")
    assert manifest["tone_count"] == _tone_count(
        SIBLING_ROOT / "src/roland_fp30x_controller/midi/tone_catalog.py"
    )
    assert manifest["release_notes"] == source_releases
    print("[pianopilot] Manifiesto sincronizado con RolandFP30xController.")


def main() -> None:
    manifest = _load_json(MANIFEST_PATH)
    check_manifest(manifest)
    check_sibling(manifest)


if __name__ == "__main__":
    main()
