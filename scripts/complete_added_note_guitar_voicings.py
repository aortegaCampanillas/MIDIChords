#!/usr/bin/env python3
"""Complete the shared guitar cache for the four-note added-tone chords."""

from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE_PATHS = (
    ROOT / "assets/guitar_chord_cache.json",
    ROOT / "apps/web/static/guitar_chord_cache.json",
    ROOT / "apps/mobile_flutter/assets/guitar_chord_cache.json",
)
TUNING = (40, 45, 50, 55, 59, 64)  # E2 A2 D3 G3 B3 E4, 6 -> 1
PATTERNS = {
    "add2": (0, 2, 4, 7),
    "add4": (0, 4, 5, 7),
    "madd2": (0, 2, 3, 7),
    "madd4": (0, 3, 5, 7),
}


def _fingers(frets: tuple[int, ...]) -> list[int]:
    pressed = sorted({fret for fret in frets if fret > 0})
    mapping = {fret: min(4, index + 1) for index, fret in enumerate(pressed)}
    return [mapping.get(fret, 0) if fret > 0 else 0 for fret in frets]


def _entry(
    frets: tuple[int, ...], fingers: tuple[int, ...] | list[int], variation: int
) -> dict[str, object]:
    string_notes = [
        TUNING[index] + fret if fret >= 0 else None
        for index, fret in enumerate(frets)
    ]
    return {
        "frets": list(frets),
        "fingers": list(fingers),
        "notes": [note for note in string_notes if note is not None],
        "string_notes": string_notes,
        "variation": variation,
    }


def _reference_add2_voicings(
    root_pc: int,
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Return the three root-position shapes published by AutoChords."""

    a_first = (-1, root_pc + 3, root_pc + 2, root_pc, root_pc + 3, -1)
    a_second_shift = 12 if root_pc >= 9 else 0
    a_second = (
        -1,
        *(root_pc + offset - a_second_shift for offset in (3, 5, 7, 5, 3)),
    )
    d_shift = 12 if root_pc >= 4 else 0
    d_shape = (
        -1,
        -1,
        *(root_pc + offset - d_shift for offset in (10, 9, 8, 10)),
    )
    a_first_fingers = (0, 2, 1, 0, 3, 0) if root_pc == 0 else (0, 3, 2, 1, 4, 0)
    a_second_fingers = (0, 0, 1, 4, 2, 0) if root_pc == 9 else (0, 1, 2, 4, 3, 1)
    d_fingers = (0, 0, 2, 1, 0, 3) if root_pc == 4 else (0, 0, 3, 2, 1, 4)
    shapes = (
        (a_first, a_first_fingers),
        (a_second, a_second_fingers),
        (d_shape, d_fingers),
    )
    if root_pc == 4:
        return shapes[2], shapes[0], shapes[1]
    if root_pc == 9:
        return shapes[1], shapes[0], shapes[2]
    return shapes


def _voicings(root_pc: int, intervals: tuple[int, ...]) -> list[dict[str, object]]:
    required_pcs = {(root_pc + interval) % 12 for interval in intervals}
    candidates: list[tuple[tuple[int, ...], tuple[int, ...], list[int]]] = []

    for start in range(0, 12):
        end = start + 4
        options: list[list[int]] = []
        for open_note in TUNING:
            string_frets = [-1]
            for fret in range(0, 16):
                if (open_note + fret) % 12 not in required_pcs:
                    continue
                if fret == 0 or start <= fret <= end:
                    string_frets.append(fret)
            options.append(string_frets)

        for frets in itertools.product(*options):
            sounding = [(index, fret) for index, fret in enumerate(frets) if fret >= 0]
            if len(sounding) < 4:
                continue
            notes = [TUNING[index] + fret for index, fret in sounding]
            if {note % 12 for note in notes} != required_pcs:
                continue
            fretted = [fret for fret in frets if fret > 0]
            if len(set(fretted)) > 4:
                continue
            if fretted and max(fretted) - min(fretted) > 4:
                continue
            position = min(fretted) if fretted else 0
            bass_pc = notes[0] % 12
            score = (
                0 if bass_pc == root_pc else 1,
                0 if position == 0 else 1,
                position,
                abs(len(sounding) - 4),
                sum(1 for fret in frets if fret < 0),
                (max(fretted) - min(fretted)) if fretted else 0,
            )
            candidates.append((score, frets, notes))

    candidates.sort(key=lambda item: item[0])
    best_by_bass: dict[int, tuple[tuple[int, ...], list[int]]] = {}
    for _score, frets, notes in candidates:
        best_by_bass.setdefault(notes[0] % 12, (frets, notes))

    selected: list[dict[str, object]] = []
    for interval in intervals:
        target_bass_pc = (root_pc + interval) % 12
        candidate = best_by_bass.get(target_bass_pc)
        if candidate is None:
            raise RuntimeError(
                f"No guitar voicing found for root {root_pc}, bass {target_bass_pc}: {intervals}"
            )
        frets, notes = candidate
        selected.append(_entry(frets, _fingers(frets), len(selected) + 1))
    if not selected:
        raise RuntimeError(f"No guitar voicing found for root {root_pc}: {intervals}")
    return selected


def main() -> None:
    cache = json.loads(CACHE_PATHS[0].read_text(encoding="utf-8"))
    by_key = cache["by_app_key"]
    for root_pc in range(12):
        for suffix, intervals in PATTERNS.items():
            by_key[f"{root_pc}|{suffix}"] = _voicings(root_pc, intervals)
    for root_pc in range(12):
        by_key[f"{root_pc}|add2"] = [
            _entry(frets, fingers, index)
            for index, (frets, fingers) in enumerate(
                _reference_add2_voicings(root_pc), start=1
            )
        ]
    site_types = set(cache.get("site_types", []))
    site_types.update(PATTERNS)
    cache["site_types"] = sorted(site_types)
    serialized = json.dumps(cache, ensure_ascii=False, indent=2) + "\n"
    for path in CACHE_PATHS:
        path.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
