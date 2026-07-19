#!/usr/bin/env python3
"""Audit or synchronize guitar voicings against AutoChords' public metadata."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CACHE_PATHS = (
    ROOT / "assets" / "guitar_chord_cache.json",
    ROOT / "apps" / "web" / "static" / "guitar_chord_cache.json",
    ROOT / "apps" / "mobile_flutter" / "assets" / "guitar_chord_cache.json",
)
CATALOG_URL = (
    "https://auto-chords.com/generate/donnees/available_positions/"
    "available-positions-v2.json"
)
IMAGE_ROOT = "https://auto-chords.com/fr/images/guitare"
ROOT_SLUGS = (
    "C",
    "C-sharp",
    "D",
    "D-sharp",
    "E",
    "F",
    "F-sharp",
    "G",
    "G-sharp",
    "A",
    "A-sharp",
    "B",
)
TUNING = (40, 45, 50, 55, 59, 64)
POSITION_ORDER = {name: index for index, name in enumerate(("open", "E", "A", "D", "G", "B", "C", "E-high"))}

# Current catalog slugs. Types absent here have no exact public counterpart and
# must retain locally curated/generated voicings.
REFERENCE_SLUG_BY_SUFFIX = {
    "": "maj",
    "5": "5",
    "m": "m",
    "dim": "dim",
    "aug": "aug",
    "sus2": "sus2",
    "sus4": "sus4",
    "add2": "add2",
    "add4": "add4",
    "madd2": "madd2",
    "madd4": "madd4",
    "add9": "add9",
    "madd9": "madd9",
    "6": "6",
    "6add9": "6-9",
    "m6": "m6",
    "7": "7",
    "7sus4": "7sus4",
    "7#5": "7-diese5",
    "7b5": "7b5",
    "7#9": "7-diese9",
    "7b9": "7b9",
    "9": "9",
    "9#5": "9-diese5",
    "9b5": "9b5",
    "11": "11",
    "13": "13",
    "13b9": "13b9",
    "13#11": "13-diese11",
    "maj7": "maj7",
    "maj7#5": "augmaj7",
    "maj9": "maj9",
    "maj11": "maj11",
    "maj13": "maj13",
    "m7": "m7",
    "m9": "m9",
    "m11": "m11",
    "m13": "m13",
    "mMaj7": "mmaj7",
    "mMaj9": "mmaj9",
    "dim7": "dim7",
    "m7b5": "m7b5",
}
UNSUPPORTED_REFERENCE_SUFFIXES = {
    "-5",
    "sus2sus4",
    "m6add9",
    "7(#5,#9)",
    "7(#5,b9)",
    "7(b5,#9)",
    "7(b5,b9)",
    "11b9",
    "maj7b5",
    "maj9#11",
    "maj13#11",
    "m7#5",
}


def _read_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def _read_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def _metadata(svg: str, name: str) -> list[int]:
    match = re.search(rf'<metadata id="{name}">(\[[^<]+\])</metadata>', svg)
    if match is None:
        raise ValueError(f"SVG metadata {name!r} not found")
    values = json.loads(match.group(1))
    if not isinstance(values, list) or len(values) != 6:
        raise ValueError(f"Invalid SVG metadata {name!r}: {values!r}")
    return [int(value) for value in values]


def _reference_entries(catalog: dict[str, Any], root_pc: int, suffix: str) -> list[dict[str, Any]]:
    slug = REFERENCE_SLUG_BY_SUFFIX[suffix]
    positions = catalog.get(f"{ROOT_SLUGS[root_pc]}-{slug}", [])
    positions = [
        position
        for position in positions
        if position.get("inversion") is False and not position.get("is_triad")
    ]
    positions.sort(key=lambda item: POSITION_ORDER.get(item.get("position"), 99))
    entries = []
    for variation, position in enumerate(positions, start=1):
        filename = position["filenames"]["fr"]
        folder = position.get("folder")
        url = f"{IMAGE_ROOT}/{folder}/{filename}" if folder else f"{IMAGE_ROOT}/{filename}"
        svg = _read_text(url)
        frets = _metadata(svg, "frets")
        fingers = _metadata(svg, "fingers")
        string_notes = [
            open_note + fret if fret >= 0 else None
            for open_note, fret in zip(TUNING, frets, strict=True)
        ]
        entries.append(
            {
                "frets": frets,
                "fingers": fingers,
                "notes": [note for note in string_notes if note is not None],
                "string_notes": string_notes,
                "variation": variation,
            }
        )
    if not entries:
        raise ValueError(f"No reference positions for root={root_pc}, suffix={suffix!r}")
    return entries


def _signature(entries: list[dict[str, Any]]) -> list[tuple[list[int], list[int]]]:
    return [(entry["frets"], entry["fingers"]) for entry in entries]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sync",
        nargs="*",
        metavar="SUFFIX",
        help="replace these suffixes; without this option, audit all mapped types",
    )
    args = parser.parse_args()
    suffixes = list(REFERENCE_SLUG_BY_SUFFIX) if args.sync is None else args.sync
    unknown = sorted(set(suffixes) - REFERENCE_SLUG_BY_SUFFIX.keys())
    if unknown:
        parser.error(f"suffixes without an AutoChords mapping: {unknown}")

    cache = json.loads(CACHE_PATHS[0].read_text(encoding="utf-8"))
    by_app_key = cache["by_app_key"]
    catalog = _read_json(CATALOG_URL)["guitare"]
    jobs = [(suffix, root_pc) for suffix in suffixes for root_pc in range(12)]
    references: dict[str, list[dict[str, Any]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_jobs = {
            executor.submit(_reference_entries, catalog, root_pc, suffix): (
                suffix,
                root_pc,
            )
            for suffix, root_pc in jobs
        }
        for future in concurrent.futures.as_completed(future_jobs):
            suffix, root_pc = future_jobs[future]
            references[f"{root_pc}|{suffix}"] = future.result()

    differences = []
    for suffix, root_pc in jobs:
        key = f"{root_pc}|{suffix}"
        reference = references[key]
        if _signature(by_app_key.get(key, [])) != _signature(reference):
            differences.append(key)
            if args.sync is not None:
                by_app_key[key] = reference

    if args.sync is not None:
        serialized = json.dumps(cache, ensure_ascii=False, indent=2) + "\n"
        for path in CACHE_PATHS:
            path.write_text(serialized, encoding="utf-8")
        print(f"Synchronized {len(differences)} chord keys: {', '.join(suffixes)}")
        return 0

    if differences:
        print(f"Reference differences ({len(differences)}):")
        print("\n".join(differences))
        return 1
    print(f"All {len(suffixes) * 12} mapped chord keys match the reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
