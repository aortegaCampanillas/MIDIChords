from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from midichords.core.app_constants import PROJECT_ROOT

CACHE_PATH = PROJECT_ROOT / "assets" / "guitar_chord_cache.json"
APP_SUFFIX_TO_SITE_TYPE = {
    "": "major",
    "5": "5",
    "-5": "-5",
    "m": "minor",
    "dim": "dim",
    "aug": "aug",
    "sus2": "sus2",
    "sus4": "sus4",
    "sus2sus4": "sus2sus4",
    "add9": "add9",
    "madd9": "madd9",
    "6": "6",
    "6add9": "6add9",
    "m6": "m6",
    "m6add9": "m6add9",
    "7": "7",
    "7sus4": "7sus4",
    "7#5": "7*5",
    "7b5": "7b5",
    "7#9": "7*9",
    "7b9": "7b9",
    "7(#5,#9)": "7%28*5,*9%29",
    "7(#5,b9)": "7%28*5,b9%29",
    "7(b5,#9)": "7%28b5,*9%29",
    "7(b5,b9)": "7%28b5,b9%29",
    "9": "9",
    "9#5": "9*5",
    "9b5": "9b5",
    "11": "11",
    "11b9": "11b9",
    "13": "13",
    "13b9": "13b9",
    "13#11": "13*11",
    "maj7": "maj7",
    "maj7#5": "maj7*5",
    "maj7b5": "maj7b5",
    "maj9": "maj9",
    "maj11": "maj11",
    "maj13": "maj13",
    "maj9#11": "maj9*11",
    "maj13#11": "maj13*11",
    "m7": "m7",
    "m7#5": "m7*5",
    "m9": "m9",
    "m11": "m11",
    "m13": "m13",
    "mMaj7": "mmaj7",
    "mMaj9": "mmaj9",
    "dim7": "dim7",
    "m7b5": "m7b5",
}


def load_guitar_chord_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_cached_variations(cache: dict[str, Any], root_pc: int, suffix: str) -> list[dict[str, Any]]:
    by_app_key = cache.get("by_app_key")
    if not isinstance(by_app_key, dict):
        return []
    key = f"{int(root_pc) % 12}|{suffix}"
    values = by_app_key.get(key, [])
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, dict)]
