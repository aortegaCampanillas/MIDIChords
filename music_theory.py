from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from i18n import NOTE_NAMES


WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
# Indice diatonico por clase de pitch (C..B), manteniendo sostenidos en la misma linea/espacio base.
PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]


@dataclass(frozen=True)
class ChordPattern:
    suffix: str
    intervals: tuple[int, ...]


CHORD_PATTERNS = [
    ChordPattern("", (0, 4, 7)),
    ChordPattern("m", (0, 3, 7)),
    ChordPattern("dim", (0, 3, 6)),
    ChordPattern("aug", (0, 4, 8)),
    ChordPattern("sus2", (0, 2, 7)),
    ChordPattern("sus4", (0, 5, 7)),
    ChordPattern("6", (0, 4, 7, 9)),
    ChordPattern("m6", (0, 3, 7, 9)),
    ChordPattern("7", (0, 4, 7, 10)),
    ChordPattern("maj7", (0, 4, 7, 11)),
    ChordPattern("m7", (0, 3, 7, 10)),
    ChordPattern("mMaj7", (0, 3, 7, 11)),
    ChordPattern("dim7", (0, 3, 6, 9)),
    ChordPattern("m7b5", (0, 3, 6, 10)),
]


def note_name(language: str, midi_note: int, with_octave: bool = True) -> str:
    base_names = NOTE_NAMES.get(language, NOTE_NAMES["en"])
    name = base_names[midi_note % 12]
    if not with_octave:
        return name
    octave = midi_note // 12 - 1
    return f"{name}{octave}"


def format_intervals(notes: set[int]) -> str:
    if not notes:
        return "-"
    ordered = sorted(notes)
    base = ordered[0]
    return " - ".join(f"+{note - base}" for note in ordered)


def analyze_chord_notes(notes: set[int]) -> tuple[Optional[int], Optional[ChordPattern], Optional[int]]:
    if not notes:
        return None, None, None
    pcs = {note % 12 for note in notes}
    best_score = -999
    best_complexity = -999
    best_root: Optional[int] = None
    best_pattern: Optional[ChordPattern] = None
    for root in range(12):
        for pattern in CHORD_PATTERNS:
            template = {(root + interval) % 12 for interval in pattern.intervals}
            extra = len(pcs - template)
            missing = len(template - pcs)

            if extra == 0 and missing == 0:
                score = 100
            elif missing == 0:
                score = 70 - extra
            elif extra == 0:
                score = 40 - missing
            else:
                continue

            complexity = -len(pattern.intervals)
            if score > best_score or (score == best_score and complexity > best_complexity):
                best_score = score
                best_complexity = complexity
                best_root = root
                best_pattern = pattern

    bass_pc = min(notes) % 12 if notes else None
    return best_root, best_pattern, bass_pc
