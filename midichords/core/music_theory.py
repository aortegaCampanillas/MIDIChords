from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from midichords.core.i18n import NOTE_NAMES


WHITE_PCS = {0, 2, 4, 5, 7, 9, 11}
# Indice diatonico por clase de pitch (C..B), manteniendo sostenidos en la misma linea/espacio base.
PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]
# Igual que PC_TO_DIATONIC_LETTER pero con convencion de bemoles (p. ej. pc=1 -> Re
# en vez de Do), para que la posicion en el pentagrama tambien "se mueva" al
# cambiar el ajuste global #/b, no solo el simbolo dibujado junto a la nota.
PC_TO_DIATONIC_FLAT = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6]

# Combo de tonica dividido en nota natural + alteracion: pc de cada letra natural
# (Do..Si) y que alteraciones son reales para cada una (sin enarmonias inventadas
# como Fb/Cb/E#/B#, que no existen en NOTE_NAMES).
ROOT_LETTER_PCS: tuple[int, ...] = (0, 2, 4, 5, 7, 9, 11)  # Do, Re, Mi, Fa, Sol, La, Si
ROOT_LETTER_ACCIDENTALS: dict[int, tuple[str, ...]] = {
    0: ("natural", "sharp"),
    2: ("flat", "natural", "sharp"),
    4: ("flat", "natural"),
    5: ("natural", "sharp"),
    7: ("flat", "natural", "sharp"),
    9: ("flat", "natural", "sharp"),
    11: ("flat", "natural"),
}


def root_pc_from_letter_accidental(letter_pc: int, accidental: str) -> int:
    offset = 1 if accidental == "sharp" else -1 if accidental == "flat" else 0
    return (letter_pc + offset) % 12


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
    ChordPattern("add2", (0, 2, 4, 7)),
    ChordPattern("add4", (0, 4, 5, 7)),
    ChordPattern("madd2", (0, 2, 3, 7)),
    ChordPattern("madd4", (0, 3, 5, 7)),
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

# Preferred UI order: common/popular variants first, then extended/altered ones.
COMMON_CHORD_SUFFIX_ORDER = (
    "",
    "m",
    "7",
    "maj7",
    "m7",
    "add2",
    "add4",
    "madd2",
    "madd4",
    "sus2",
    "sus4",
    "dim",
    "aug",
    "5",
    "6",
    "m6",
    "add9",
    "madd9",
    "9",
    "maj9",
    "m9",
    "11",
    "m11",
    "13",
    "m13",
    "dim7",
    "m7b5",
)

# Escalas básicas/más comunes para filtrar en UI
SCALE_BASIC_NAMES = {
    "Ionian",
    "Aeolian",
    "Harmonic Minor",
    "Melodic Minor",
    "Dorian",
    "Phrygian",
    "Lydian",
    "Mixolydian",
    "Locrian",
    "Major Pentatonic",
    "Minor Pentatonic",
    "Blues Pentatonic",
    "Minor Blues",
    "Chromatic",
    "Whole Tone (WT)",
}

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
    if not ordered:
        return "-"
    result = ["0"]
    for i in range(1, len(ordered)):
        increment = ordered[i] - ordered[i - 1]
        result.append(f"+{increment}")
    return " ".join(result)


# Grado (con alteracion respecto a la escala mayor) por semitonos desde la
# tonica, hasta 24 semitonos (2 octavas) para cubrir 9a/11a/13a.
DEGREE_BY_SEMITONE: dict[int, str] = {
    0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5", 7: "5",
    8: "#5", 9: "6", 10: "b7", 11: "7", 12: "8",
    13: "b9", 14: "9", 15: "#9", 17: "11", 18: "#11", 20: "b13", 21: "13",
}

# Grado diatonico (1-7) por semitonos desde la tonica, para escalas. A
# diferencia de DEGREE_BY_SEMITONE (pensada para acordes, donde 8 semitonos se
# interpreta como quinta aumentada), aqui cada semitono siempre resuelve a una
# alteracion del grado numerico correspondiente (8 semitonos -> b6, no #5).
SCALE_DEGREE_BY_SEMITONE: dict[int, str] = {
    0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5",
    7: "5", 8: "b6", 9: "6", 10: "b7", 11: "7", 12: "8",
}

# Calidad abreviada de un intervalo (par de notas consecutivas de un acorde)
# por semitonos, en notacion estandar: P=justo, M=mayor, m=menor, TT=tritono.
INTERVAL_QUALITY_BY_SEMITONE: dict[int, str] = {
    0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4", 6: "TT", 7: "P5",
    8: "m6", 9: "M6", 10: "m7", 11: "M7", 12: "P8",
}


def interval_quality_abbrev(semitones: int) -> str:
    value = int(semitones)
    octaves, remainder = divmod(value, 12)
    base = INTERVAL_QUALITY_BY_SEMITONE.get(remainder)
    if not base:
        return f"{value}st"
    return f"{base}+{octaves * 12}" if octaves > 0 else base


def chord_formula_from_root(root_pc: int, notes_midi: list[int]) -> str:
    ordered = sorted({int(n) for n in notes_midi})
    if not ordered:
        return "-"
    root_midi = ordered[0] - ((ordered[0] % 12 - int(root_pc)) + 12) % 12
    return " ".join(DEGREE_BY_SEMITONE.get(n - root_midi, f"{n - root_midi}st") for n in ordered)


def chord_construction_from_midi(notes_midi: list[int]) -> str:
    ordered = sorted({int(n) for n in notes_midi})
    if len(ordered) < 2:
        return "-"
    return " + ".join(
        interval_quality_abbrev(ordered[i] - ordered[i - 1]) for i in range(1, len(ordered))
    )


def root_position_voicing(root_pc: int, notes_midi: list[int]) -> list[int]:
    root = int(root_pc) % 12
    pcs = sorted({int(n) % 12 for n in notes_midi})
    offsets = sorted((pc - root + 12) % 12 for pc in pcs)
    return [60 + offset for offset in offsets]


def rotate_degrees(formula: str, inversion: int) -> str:
    degrees = [part for part in str(formula).split(" - ") if part]
    if not degrees:
        return formula
    idx = max(0, min(int(inversion), len(degrees) - 1))
    return " - ".join(degrees[idx:] + degrees[:idx])


def scale_step_label(semitones: int) -> str:
    value = int(semitones)
    if value <= 0:
        return ""
    tones, has_semitone = divmod(value, 2)
    parts = ["T"] * tones
    if has_semitone:
        parts.append("S")
    return "+".join(parts)


def scale_pattern_from_midi(notes_midi: list[int]) -> str:
    ordered = sorted({int(n) for n in notes_midi})
    if len(ordered) < 2:
        return "-"
    return " ".join(scale_step_label(ordered[i] - ordered[i - 1]) for i in range(1, len(ordered)))


def scale_formula_from_midi(notes_midi: list[int]) -> str:
    ordered = sorted({int(n) for n in notes_midi})
    if not ordered:
        return "-"
    root_midi = ordered[0]
    # La nota final (octava) no se cuenta como grado nuevo en la formula.
    degree_notes = ordered[:-1] if len(ordered) > 1 and ordered[-1] - root_midi == 12 else ordered
    return " ".join(SCALE_DEGREE_BY_SEMITONE.get(n - root_midi, f"{n - root_midi}st") for n in degree_notes)


CHORD_SUFFIX_NAMES: dict[str, dict[str, str]] = {
    "es": {
        "": "Mayor",
        "m": "Menor",
        "5": "Quinta (power chord)",
        "-5": "Mayor quinta disminuida",
        "dim": "Disminuido",
        "aug": "Aumentado",
        "sus2": "Suspendido 2ª",
        "sus4": "Suspendido 4ª",
        "sus2sus4": "Suspendido 2ª y 4ª",
        "add2": "Mayor con 2ª añadida",
        "add4": "Mayor con 4ª añadida",
        "madd2": "Menor con 2ª añadida",
        "madd4": "Menor con 4ª añadida",
        "add9": "Mayor con 9ª añadida",
        "madd9": "Menor con 9ª añadida",
        "6": "Mayor con 6ª",
        "6add9": "Mayor con 6ª y 9ª",
        "m6": "Menor con 6ª",
        "m6add9": "Menor con 6ª y 9ª",
        "7": "Mayor dominante (7ª menor)",
        "7sus4": "Dominante suspendido 4ª",
        "7#5": "Dominante aumentado",
        "7b5": "Dominante quinta disminuida",
        "7#9": "Dominante con 9ª aumentada",
        "7b9": "Dominante con 9ª disminuida",
        "7(#5,#9)": "Dominante aumentado con 9ª aumentada",
        "7(#5,b9)": "Dominante aumentado con 9ª disminuida",
        "7(b5,#9)": "Dominante quinta disminuida con 9ª aumentada",
        "7(b5,b9)": "Dominante quinta disminuida con 9ª disminuida",
        "9": "Dominante con 9ª",
        "9#5": "Dominante aumentado con 9ª",
        "9b5": "Dominante quinta disminuida con 9ª",
        "11": "Dominante con 11ª",
        "11b9": "Dominante con 11ª y 9ª disminuida",
        "13": "Dominante con 13ª",
        "13b9": "Dominante con 13ª y 9ª disminuida",
        "13#11": "Dominante con 13ª y 11ª aumentada",
        "maj7": "Mayor con 7ª mayor",
        "maj7#5": "Mayor aumentado con 7ª mayor",
        "maj7b5": "Mayor quinta disminuida con 7ª mayor",
        "maj9": "Mayor con 9ª y 7ª mayor",
        "maj11": "Mayor con 11ª y 7ª mayor",
        "maj13": "Mayor con 13ª y 7ª mayor",
        "maj9#11": "Mayor con 9ª, 11ª aumentada y 7ª mayor",
        "maj13#11": "Mayor con 13ª, 11ª aumentada y 7ª mayor",
        "m7": "Menor con 7ª menor",
        "m7#5": "Menor aumentado con 7ª menor",
        "m9": "Menor con 9ª y 7ª menor",
        "m11": "Menor con 11ª y 7ª menor",
        "m13": "Menor con 13ª y 7ª menor",
        "mMaj7": "Menor con 7ª mayor",
        "mMaj9": "Menor con 9ª y 7ª mayor",
        "dim7": "Disminuido con 7ª disminuida",
        "m7b5": "Semidisminuido (menor con quinta disminuida)",
    },
    "en": {
        "": "Major",
        "m": "Minor",
        "5": "Power chord",
        "-5": "Major flat five",
        "dim": "Diminished",
        "aug": "Augmented",
        "sus2": "Suspended 2nd",
        "sus4": "Suspended 4th",
        "sus2sus4": "Suspended 2nd and 4th",
        "add2": "Major add 2nd",
        "add4": "Major add 4th",
        "madd2": "Minor add 2nd",
        "madd4": "Minor add 4th",
        "add9": "Major add 9th",
        "madd9": "Minor add 9th",
        "6": "Major 6th",
        "6add9": "Major 6th add 9th",
        "m6": "Minor 6th",
        "m6add9": "Minor 6th add 9th",
        "7": "Dominant 7th (major with minor 7th)",
        "7sus4": "Dominant suspended 4th",
        "7#5": "Augmented dominant",
        "7b5": "Dominant flat five",
        "7#9": "Dominant sharp 9th",
        "7b9": "Dominant flat 9th",
        "7(#5,#9)": "Augmented dominant sharp 9th",
        "7(#5,b9)": "Augmented dominant flat 9th",
        "7(b5,#9)": "Dominant flat five sharp 9th",
        "7(b5,b9)": "Dominant flat five flat 9th",
        "9": "Dominant 9th",
        "9#5": "Augmented dominant 9th",
        "9b5": "Dominant flat five 9th",
        "11": "Dominant 11th",
        "11b9": "Dominant 11th flat 9th",
        "13": "Dominant 13th",
        "13b9": "Dominant 13th flat 9th",
        "13#11": "Dominant 13th sharp 11th",
        "maj7": "Major 7th",
        "maj7#5": "Augmented major 7th",
        "maj7b5": "Major flat five major 7th",
        "maj9": "Major 9th",
        "maj11": "Major 11th",
        "maj13": "Major 13th",
        "maj9#11": "Major 9th sharp 11th",
        "maj13#11": "Major 13th sharp 11th",
        "m7": "Minor 7th",
        "m7#5": "Augmented minor 7th",
        "m9": "Minor 9th",
        "m11": "Minor 11th",
        "m13": "Minor 13th",
        "mMaj7": "Minor major 7th",
        "mMaj9": "Minor major 9th",
        "dim7": "Diminished 7th",
        "m7b5": "Half-diminished (minor flat five)",
    },
}

_INVERSION_NAMES: dict[str, tuple[str, ...]] = {
    "es": ("", "primera inversión", "segunda inversión", "tercera inversión"),
    "en": ("", "first inversion", "second inversion", "third inversion"),
}


def chord_description(
    suffix: str,
    language: str,
    bass_pc: Optional[int],
    root: Optional[int],
    bass_name: Optional[str],
    pattern_intervals: tuple[int, ...],
) -> Optional[str]:
    names = CHORD_SUFFIX_NAMES.get(language, CHORD_SUFFIX_NAMES["en"])
    base = names.get(suffix)
    if not base:
        return None
    if bass_pc is not None and root is not None and bass_name is not None and bass_pc != root:
        bass_interval = (bass_pc - root + 12) % 12
        inv_index = list(pattern_intervals).index(bass_interval) if bass_interval in pattern_intervals else -1
        inv_names = _INVERSION_NAMES.get(language, _INVERSION_NAMES["en"])
        if 0 < inv_index < len(inv_names):
            return f"{base}, {inv_names[inv_index]}"
        bass_word = "bajo en" if language == "es" else "bass on"
        return f"{base}, {bass_word} {bass_name}"
    return base


def analyze_chord_notes(notes: set[int]) -> tuple[Optional[int], Optional[ChordPattern], Optional[int]]:
    if not notes:
        return None, None, None
    pcs = {note % 12 for note in notes}
    bass_pc = min(notes) % 12
    suffix_priority = {suffix: idx for idx, suffix in enumerate(COMMON_CHORD_SUFFIX_ORDER)}
    best_score = -999
    best_complexity = -999
    best_root_is_bass = False
    best_priority = len(COMMON_CHORD_SUFFIX_ORDER)
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
            # Distintos acordes pueden compartir exactamente las mismas notas
            # (p. ej. Do sus2 = Do-Re-Sol y Sol sus4 = Sol-Do-Re son el mismo
            # conjunto de pitch-classes). En ese empate exacto, la nota más
            # grave realmente tocada (bass_pc) es la señal más fuerte de cuál
            # es la raíz percibida, y debe primar sobre la prioridad fija de
            # sufijos (que si no, siempre elegía "sus4" sobre "sus2" pese a
            # que el bajo tocado fuera la tónica del sus2).
            root_is_bass = root == bass_pc
            priority = suffix_priority.get(pattern.suffix, len(COMMON_CHORD_SUFFIX_ORDER))
            better = (
                score > best_score
                or (score == best_score and complexity > best_complexity)
                or (
                    score == best_score
                    and complexity == best_complexity
                    and root_is_bass
                    and not best_root_is_bass
                )
                or (
                    score == best_score
                    and complexity == best_complexity
                    and root_is_bass == best_root_is_bass
                    and priority < best_priority
                )
            )
            if better:
                best_score = score
                best_complexity = complexity
                best_root_is_bass = root_is_bass
                best_priority = priority
                best_root = root
                best_pattern = pattern

    return best_root, best_pattern, bass_pc


def chord_patterns_for_ui() -> tuple[ChordPattern, ...]:
    priority = {suffix: idx for idx, suffix in enumerate(COMMON_CHORD_SUFFIX_ORDER)}
    return tuple(
        sorted(
            CHORD_PATTERNS,
            key=lambda pattern: (
                priority.get(pattern.suffix, len(COMMON_CHORD_SUFFIX_ORDER)),
                len(pattern.intervals),
                pattern.suffix,
            ),
        )
    )
