from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from midichords.core.i18n import NOTE_NAMES


WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
# Indice diatonico por clase de pitch (C..B), manteniendo sostenidos en la misma linea/espacio base.
PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]


@dataclass(frozen=True)
class ChordPattern:
    suffix: str
    intervals: tuple[int, ...]


@dataclass(frozen=True)
class ScalePattern:
    name: str
    intervals: tuple[int, ...]


CHORD_PATTERNS = [
    ChordPattern("", (0, 4, 7)),
    ChordPattern("5", (0, 7)),
    ChordPattern("-5", (0, 4, 6)),
    ChordPattern("m", (0, 3, 7)),
    ChordPattern("dim", (0, 3, 6)),
    ChordPattern("aug", (0, 4, 8)),
    ChordPattern("sus2", (0, 2, 7)),
    ChordPattern("sus4", (0, 5, 7)),
    ChordPattern("sus2sus4", (0, 2, 5, 7)),
    ChordPattern("add9", (0, 4, 7, 14)),
    ChordPattern("madd9", (0, 3, 7, 14)),
    ChordPattern("6", (0, 4, 7, 9)),
    ChordPattern("6add9", (0, 4, 7, 9, 14)),
    ChordPattern("m6", (0, 3, 7, 9)),
    ChordPattern("m6add9", (0, 3, 7, 9, 14)),
    ChordPattern("7", (0, 4, 7, 10)),
    ChordPattern("7sus4", (0, 5, 7, 10)),
    ChordPattern("7#5", (0, 4, 8, 10)),
    ChordPattern("7b5", (0, 4, 6, 10)),
    ChordPattern("7#9", (0, 4, 7, 10, 15)),
    ChordPattern("7b9", (0, 4, 7, 10, 13)),
    ChordPattern("7(#5,#9)", (0, 4, 8, 10, 15)),
    ChordPattern("7(#5,b9)", (0, 4, 8, 10, 13)),
    ChordPattern("7(b5,#9)", (0, 4, 6, 10, 15)),
    ChordPattern("7(b5,b9)", (0, 4, 6, 10, 13)),
    ChordPattern("9", (0, 4, 7, 10, 14)),
    ChordPattern("9#5", (0, 4, 8, 10, 14)),
    ChordPattern("9b5", (0, 4, 6, 10, 14)),
    ChordPattern("11", (0, 4, 7, 10, 14, 17)),
    ChordPattern("11b9", (0, 4, 7, 10, 13, 17)),
    ChordPattern("13", (0, 4, 7, 10, 14, 21)),
    ChordPattern("13b9", (0, 4, 7, 10, 13, 21)),
    ChordPattern("13#11", (0, 4, 7, 10, 14, 18, 21)),
    ChordPattern("maj7", (0, 4, 7, 11)),
    ChordPattern("maj7#5", (0, 4, 8, 11)),
    ChordPattern("maj7b5", (0, 4, 6, 11)),
    ChordPattern("maj9", (0, 4, 7, 11, 14)),
    ChordPattern("maj11", (0, 4, 7, 11, 14, 17)),
    ChordPattern("maj13", (0, 4, 7, 11, 14, 21)),
    ChordPattern("maj9#11", (0, 4, 7, 11, 14, 18)),
    ChordPattern("maj13#11", (0, 4, 7, 11, 14, 18, 21)),
    ChordPattern("m7", (0, 3, 7, 10)),
    ChordPattern("m7#5", (0, 3, 8, 10)),
    ChordPattern("m9", (0, 3, 7, 10, 14)),
    ChordPattern("m11", (0, 3, 7, 10, 14, 17)),
    ChordPattern("m13", (0, 3, 7, 10, 14, 21)),
    ChordPattern("mMaj7", (0, 3, 7, 11)),
    ChordPattern("mMaj9", (0, 3, 7, 11, 14)),
    ChordPattern("dim7", (0, 3, 6, 9)),
    ChordPattern("m7b5", (0, 3, 6, 10)),
]

SCALE_PATTERNS = [
    ScalePattern("Ionian", (0, 2, 4, 5, 7, 9, 11, 12)),
    ScalePattern("Dorian", (0, 2, 3, 5, 7, 9, 10, 12)),
    ScalePattern("Phrygian", (0, 1, 3, 5, 7, 8, 10, 12)),
    ScalePattern("Lydian", (0, 2, 4, 6, 7, 9, 11, 12)),
    ScalePattern("Mixolydian", (0, 2, 4, 5, 7, 9, 10, 12)),
    ScalePattern("Aeolian", (0, 2, 3, 5, 7, 8, 10, 12)),
    ScalePattern("Locrian", (0, 1, 3, 5, 6, 8, 10, 12)),
    ScalePattern("Chromatic", (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    ScalePattern("Locrian #2", (0, 2, 3, 5, 6, 8, 10, 12)),
    ScalePattern("Harmonic Minor", (0, 2, 3, 5, 7, 8, 11, 12)),
    ScalePattern("Melodic Minor", (0, 2, 3, 5, 7, 9, 11, 12)),
    ScalePattern("Major Pentatonic", (0, 2, 4, 7, 9, 12)),
    ScalePattern("Minor Pentatonic", (0, 3, 5, 7, 10, 12)),
    ScalePattern("Blues Pentatonic", (0, 3, 5, 7, 10, 12)),
    ScalePattern("Neutral Pentatonic", (0, 2, 5, 7, 10, 12)),
    ScalePattern("Bebop", (0, 2, 4, 5, 7, 9, 10, 11, 12)),
    ScalePattern("Bebop Major", (0, 2, 4, 5, 7, 8, 9, 11, 12)),
    ScalePattern("Bebop Minor", (0, 2, 3, 4, 5, 7, 9, 10, 12)),
    ScalePattern("Half Diminished", (0, 2, 3, 5, 6, 8, 10, 12)),
    ScalePattern("Diminished", (0, 2, 3, 5, 6, 8, 9, 11, 12)),
    ScalePattern("Whole Tone (WT)", (0, 2, 4, 6, 8, 10, 12)),
    ScalePattern("Diminished WT", (0, 1, 3, 4, 6, 7, 9, 10, 12)),
    ScalePattern("Minor Blues", (0, 3, 5, 6, 7, 10, 12)),
    ScalePattern("Super Locrian", (0, 1, 3, 4, 6, 8, 10, 12)),
    ScalePattern("Romanian Minor", (0, 2, 3, 6, 7, 9, 10, 12)),
    ScalePattern("Spanish Gypsy", (0, 1, 4, 5, 7, 8, 10, 12)),
    ScalePattern("Eight Tone Spanish", (0, 1, 3, 4, 5, 6, 8, 10, 12)),
    ScalePattern("Enigmatic", (0, 1, 4, 6, 8, 10, 11, 12)),
    ScalePattern("Neapolitan Major", (0, 1, 3, 5, 7, 9, 11, 12)),
    ScalePattern("Neapolitan Minor", (0, 1, 3, 5, 7, 8, 11, 12)),
    ScalePattern("Pelog", (0, 1, 3, 7, 8, 10, 12)),
    ScalePattern("Prometheus", (0, 2, 4, 6, 9, 10, 12)),
    ScalePattern("Prometheus Neapolitan", (0, 1, 4, 6, 9, 10, 12)),
    ScalePattern("Six Tone Symmetric", (0, 1, 4, 5, 8, 9, 12)),
    ScalePattern("Lydian Minor", (0, 2, 3, 6, 7, 9, 11, 12)),
    ScalePattern("Lydian Augmented", (0, 2, 4, 6, 8, 9, 11, 12)),
    ScalePattern("Lydian Diminished", (0, 2, 3, 6, 7, 9, 10, 12)),
    ScalePattern("Lydian Augmented #6", (0, 2, 4, 6, 8, 10, 11, 12)),
    ScalePattern("Hungarian Major", (0, 3, 4, 6, 7, 9, 10, 12)),
    ScalePattern("Hungarian Minor", (0, 2, 3, 6, 7, 8, 11, 12)),
    ScalePattern("Ichikosucho", (0, 2, 4, 5, 6, 8, 10, 12)),
    ScalePattern("Persian", (0, 1, 4, 5, 6, 8, 11, 12)),
    ScalePattern("Flamenco", (0, 1, 4, 5, 7, 8, 10, 12)),
    ScalePattern("Hawaiian", (0, 2, 3, 5, 7, 8, 11, 12)),
    ScalePattern("Maqam", (0, 1, 4, 5, 7, 8, 10, 12)),
    ScalePattern("Oriental", (0, 1, 4, 5, 6, 9, 10, 12)),
    ScalePattern("Iwato", (0, 1, 5, 6, 10, 12)),
    ScalePattern("Raga Malakosh", (0, 3, 5, 7, 10, 12)),
    ScalePattern("Balinese", (0, 1, 3, 7, 8, 12)),
    ScalePattern("Kafi Raga", (0, 2, 3, 5, 7, 9, 10, 12)),
    ScalePattern("Todi Raga", (0, 1, 3, 6, 7, 8, 11, 12)),
    ScalePattern("Purvi Raga", (0, 1, 4, 6, 7, 8, 11, 12)),
    ScalePattern("In Sen", (0, 1, 5, 7, 10, 12)),
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
