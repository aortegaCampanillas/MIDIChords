from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config_file(path: Path, defaults: dict[str, Any]) -> dict[str, Any]:
    data = dict(defaults)
    if not path.exists():
        return data
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return data
    if not isinstance(loaded, dict):
        return data
    data.update(loaded)
    return data


def save_config_file(path: Path, config_data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config_data, indent=2, ensure_ascii=False), encoding="utf-8")
