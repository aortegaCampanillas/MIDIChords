from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional

from midichords.core.i18n import NOTE_NAMES, SCALE_NAME_TEXTS
from midichords.core.music_theory import CHORD_PATTERNS, SCALE_PATTERNS, analyze_chord_notes, chord_patterns_for_ui


FLAT_ALIASES = {
    "es": {
        1: "Re♭",
        3: "Mi♭",
        6: "Sol♭",
        8: "La♭",
        10: "Si♭",
    },
    "en": {
        1: "D♭",
        3: "E♭",
        6: "G♭",
        8: "A♭",
        10: "B♭",
    },
}


def note_name(
    midi_note: int,
    language: str = "es",
    prefer_flat: bool = False,
    with_octave: bool = True,
) -> str:
    names = NOTE_NAMES.get(language, NOTE_NAMES["en"])
    pc = int(midi_note) % 12
    sharp_name = names[pc]
    flat_name = FLAT_ALIASES.get(language, FLAT_ALIASES["en"]).get(pc)
    name = flat_name if (prefer_flat and flat_name is not None) else sharp_name
    if not with_octave:
        return name
    octave = int(midi_note) // 12 - 1
    return f"{name}{octave}"


def _tonic_letter_index(tonic_pc: int, prefer_flats: bool) -> int:
    tonic_pc = int(tonic_pc) % 12
    if prefer_flats:
        mapping = {
            0: 0,
            1: 1,
            2: 1,
            3: 2,
            4: 2,
            5: 3,
            6: 4,
            7: 4,
            8: 5,
            9: 5,
            10: 6,
            11: 6,
        }
    else:
        mapping = {
            0: 0,
            1: 0,
            2: 1,
            3: 1,
            4: 2,
            5: 3,
            6: 3,
            7: 4,
            8: 4,
            9: 5,
            10: 5,
            11: 6,
        }
    return int(mapping.get(tonic_pc, 0))


def _apply_accidental(base: str, diff: int) -> Optional[str]:
    if diff == 0:
        return f"{base}"
    if diff == 1:
        return f"{base}#"
    if diff == -1:
        return f"{base}♭"
    if diff == 2:
        return f"{base}##"
    if diff == -2:
        return f"{base}♭♭"
    return None


def _spell_by_degree(
    root_pc: int,
    target_pc: int,
    degree: int,
    language: str,
    prefer_flats: bool,
    midi_note: Optional[int] = None,
    with_octave: bool = False,
) -> str:
    letter_names = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] if language == "es" else ["C", "D", "E", "F", "G", "A", "B"]
    base_pcs = [0, 2, 4, 5, 7, 9, 11]
    tonic_letter = _tonic_letter_index(root_pc, prefer_flats)
    letter_idx = (tonic_letter + int(degree)) % 7
    natural_pc = base_pcs[letter_idx]
    diff = (int(target_pc) - natural_pc) % 12
    if diff > 6:
        diff -= 12
    spelled = _apply_accidental(letter_names[letter_idx], diff)
    if spelled is None:
        fallback_note = int(target_pc if midi_note is None else midi_note)
        return note_name(fallback_note, language=language, prefer_flat=prefer_flats, with_octave=with_octave)
    if with_octave and midi_note is not None:
        octave = int(midi_note) // 12 - 1
        return f"{spelled}{octave}"
    return spelled


def _chord_interval_degree(interval: int, suffix: str) -> int:
    value = int(interval)
    suffix_text = str(suffix)
    if value in {0, 12}:
        return 0
    if value in {1, 2, 13, 14}:
        return 1
    if value in {3, 4, 15}:
        return 2
    if value in {5, 17}:
        return 3
    if value in {6, 18}:
        if ("b5" in suffix_text) or ("dim" in suffix_text):
            return 4
        return 3
    if value == 7:
        return 4
    if value == 8:
        if ("#5" in suffix_text) or ("aug" in suffix_text):
            return 4
        return 5
    if value in {9, 21}:
        return 5
    if value in {10, 11}:
        return 6
    return max(0, min(6, value % 7))


def list_chord_patterns() -> list[dict[str, Any]]:
    return [asdict(pattern) for pattern in chord_patterns_for_ui()]


def list_scale_patterns(language: str = "es") -> list[dict[str, Any]]:
    localized = SCALE_NAME_TEXTS.get(language, SCALE_NAME_TEXTS["en"])
    out: list[dict[str, Any]] = []
    for pattern in SCALE_PATTERNS:
        out.append(
            {
                "name": pattern.name,
                "localized_name": localized.get(pattern.name, pattern.name),
                "intervals": list(pattern.intervals),
            }
        )
    return out


def generate_chord(
    root_pc: int,
    suffix: str,
    inversion: int = 0,
    language: str = "es",
    prefer_flat: bool = False,
) -> dict[str, Any]:
    selected = next((p for p in CHORD_PATTERNS if p.suffix == suffix), CHORD_PATTERNS[0])
    intervals = list(selected.intervals)
    if not intervals:
        return {
            "root_pc": int(root_pc) % 12,
            "suffix": selected.suffix,
            "inversion": 0,
            "name": "-",
            "notes_midi": [],
            "notes": [],
        }
    inversion = max(0, min(int(inversion), len(intervals) - 1))
    root_midi = 60 + (int(root_pc) % 12)
    voiced_intervals = sorted(interval + (12 if idx < inversion else 0) for idx, interval in enumerate(intervals))
    notes_midi = [root_midi + interval for interval in voiced_intervals]

    note_labels: list[str] = []
    note_labels_no_oct: list[str] = []
    for interval, midi_note in zip(voiced_intervals, notes_midi):
        degree = _chord_interval_degree(interval, selected.suffix)
        pc = midi_note % 12
        note_labels.append(
            _spell_by_degree(
                root_pc=int(root_pc),
                target_pc=pc,
                degree=degree,
                language=language,
                prefer_flats=prefer_flat,
                midi_note=midi_note,
                with_octave=True,
            )
        )
        note_labels_no_oct.append(
            _spell_by_degree(
                root_pc=int(root_pc),
                target_pc=pc,
                degree=degree,
                language=language,
                prefer_flats=prefer_flat,
                midi_note=midi_note,
                with_octave=False,
            )
        )
    root_name = _spell_by_degree(
        root_pc=int(root_pc),
        target_pc=int(root_pc) % 12,
        degree=0,
        language=language,
        prefer_flats=prefer_flat,
        midi_note=int(root_pc),
        with_octave=False,
    )
    chord_name = f"{root_name}{selected.suffix}"
    if inversion > 0 and notes_midi:
        chord_name = f"{chord_name}/{note_labels_no_oct[0]}"
    return {
        "root_pc": int(root_pc) % 12,
        "suffix": selected.suffix,
        "inversion": inversion,
        "name": chord_name,
        "notes_midi": notes_midi,
        "notes": note_labels,
        "notes_no_octave": note_labels_no_oct,
        "intervals": voiced_intervals,
    }


def detect_chord(
    notes: list[int],
    language: str = "es",
    prefer_flat: bool = False,
) -> dict[str, Any]:
    midi_notes = sorted({int(n) for n in notes})
    if not midi_notes:
        return {"name": "-", "extras_midi": [], "notes_midi": [], "notes": [], "extras": []}
    pcs = {n % 12 for n in midi_notes}
    if len(pcs) == 1:
        single = midi_notes[0]
        return {
            "name": note_name(single, language=language, prefer_flat=prefer_flat, with_octave=False),
            "notes_midi": midi_notes,
            "notes": [note_name(n, language=language, prefer_flat=prefer_flat, with_octave=True) for n in midi_notes],
            "extras_midi": [],
            "extras": [],
        }

    root, pattern, bass_pc = analyze_chord_notes(set(midi_notes))
    if root is None or pattern is None:
        return {
            "name": " + ".join(note_name(n, language=language, prefer_flat=prefer_flat, with_octave=False) for n in midi_notes),
            "notes_midi": midi_notes,
            "notes": [note_name(n, language=language, prefer_flat=prefer_flat, with_octave=True) for n in midi_notes],
            "extras_midi": [],
            "extras": [],
        }

    degree_by_pc: dict[int, int] = {}
    for interval in pattern.intervals:
        pc = (int(root) + int(interval)) % 12
        if pc not in degree_by_pc:
            degree_by_pc[pc] = _chord_interval_degree(int(interval), pattern.suffix)

    root_name = _spell_by_degree(int(root), int(root), 0, language, prefer_flat, midi_note=int(root), with_octave=False)
    chord_name = f"{root_name}{pattern.suffix}"
    if bass_pc is not None and bass_pc != root:
        bass_degree = degree_by_pc.get(int(bass_pc))
        if bass_degree is None:
            bass_name = note_name(int(bass_pc), language=language, prefer_flat=prefer_flat, with_octave=False)
        else:
            bass_name = _spell_by_degree(int(root), int(bass_pc), bass_degree, language, prefer_flat, midi_note=int(bass_pc), with_octave=False)
        chord_name = f"{chord_name}/{bass_name}"

    expected_pcs = {(int(root) + int(interval)) % 12 for interval in pattern.intervals}
    extras = [n for n in midi_notes if (n % 12) not in expected_pcs]
    note_labels: list[str] = []
    for n in midi_notes:
        degree = degree_by_pc.get(n % 12)
        if degree is None:
            note_labels.append(note_name(n, language=language, prefer_flat=prefer_flat, with_octave=True))
        else:
            note_labels.append(_spell_by_degree(int(root), n % 12, degree, language, prefer_flat, midi_note=n, with_octave=True))
    return {
        "name": chord_name,
        "notes_midi": midi_notes,
        "notes": note_labels,
        "extras_midi": extras,
        "extras": [note_name(n, language=language, prefer_flat=prefer_flat, with_octave=True) for n in extras],
        "root_pc": int(root),
        "suffix": pattern.suffix,
    }


def generate_scale(
    tonic_pc: int,
    pattern_name: str,
    language: str = "es",
    prefer_flat: bool = False,
) -> dict[str, Any]:
    pattern = next((p for p in SCALE_PATTERNS if p.name == pattern_name), SCALE_PATTERNS[0])
    root_midi = 60 + (int(tonic_pc) % 12)
    intervals = list(pattern.intervals)
    notes_midi = [root_midi + i for i in intervals]
    names: list[str] = []
    for idx, midi_note in enumerate(notes_midi):
        names.append(
            _spell_by_degree(
                root_pc=int(tonic_pc),
                target_pc=int(midi_note) % 12,
                degree=idx,
                language=language,
                prefer_flats=prefer_flat,
                midi_note=int(midi_note),
                with_octave=True,
            )
        )
    localized = SCALE_NAME_TEXTS.get(language, SCALE_NAME_TEXTS["en"]).get(pattern.name, pattern.name)
    return {
        "tonic_pc": int(tonic_pc) % 12,
        "pattern_name": pattern.name,
        "pattern_localized_name": localized,
        "notes_midi": notes_midi,
        "notes": names,
        "intervals": intervals,
    }
