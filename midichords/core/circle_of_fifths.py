"""Circle of Fifths logic and utilities."""

from midichords.core.music_theory import PC_TO_NOTE_NAME, ChordPattern

# Pitch class names in circle order (C at top, going clockwise by fifths)
CIRCLE_POSITIONS = [
    "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"
]

# Map PC to position in circle (0-11)
PC_TO_CIRCLE_IDX = {
    0: 0,    # C
    7: 1,    # G
    2: 2,    # D
    9: 3,    # A
    4: 4,    # E
    11: 5,   # B
    6: 6,    # F#
    1: 7,    # C#
    8: 8,    # G#
    3: 9,    # D#
    10: 10,  # A#
    5: 11,   # F
}

CIRCLE_IDX_TO_PC = {v: k for k, v in PC_TO_CIRCLE_IDX.items()}

def get_key_signature(root_pc: int, is_major: bool) -> dict[str, int]:
    """Get key signature accidentals for a major or minor key.

    Returns: {'sharps': count} or {'flats': count}
    """
    circle_idx = PC_TO_CIRCLE_IDX.get(root_pc, 0)

    if is_major:
        # Major: clockwise from C
        if circle_idx <= 6:
            return {'sharps': circle_idx}
        else:
            return {'flats': 12 - circle_idx}
    else:
        # Minor: same signature as relative major (3 semitones up)
        relative_major_pc = (root_pc + 3) % 12
        return get_key_signature(relative_major_pc, True)


def diatonic_chords(root_pc: int, mode: str = 'major') -> list[dict]:
    """Get diatonic triads for a key.

    Args:
        root_pc: Root pitch class (0-11)
        mode: 'major' or 'minor'

    Returns:
        List of {'root': pc, 'suffix': 'chord_type'} for scale degrees I-VII
    """
    major_intervals = [0, 2, 4, 5, 7, 9, 11]
    minor_intervals = [0, 2, 3, 5, 7, 8, 10]

    intervals = major_intervals if mode == 'major' else minor_intervals

    # Chord qualities for major scale degrees
    major_qualities = ['', 'm', 'm', '', '7', 'm', 'dim']
    # Chord qualities for natural minor scale degrees
    minor_qualities = ['m', 'dim', '', 'm', 'm', '', '']

    qualities = major_qualities if mode == 'major' else minor_qualities

    chords = []
    for degree in range(7):
        note_pc = (root_pc + intervals[degree]) % 12
        quality = qualities[degree]
        chords.append({'root': note_pc, 'suffix': quality})

    return chords
