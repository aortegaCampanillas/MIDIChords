from __future__ import annotations

import unittest

from midichords.core.music_service import generate_chord
from midichords.core.music_theory import CHORD_PATTERNS
from midichords.mixins.generation_mixin import GenerationMixin


def _expected_bass_pc(intervals: list[int], inversion: int) -> int:
    return int(intervals[inversion]) % 12


class ChordInversionTests(unittest.TestCase):
    def test_generate_chord_inversions_match_expected_bass_pc(self) -> None:
        root_pc = 0  # C
        for pattern in CHORD_PATTERNS:
            intervals = list(pattern.intervals)
            if not intervals:
                continue
            for inversion in range(len(intervals)):
                out = generate_chord(
                    root_pc=root_pc,
                    suffix=pattern.suffix,
                    inversion=inversion,
                    language="en",
                    prefer_flat=False,
                )
                notes_midi = [int(n) for n in out["notes_midi"]]
                self.assertTrue(notes_midi, f"Empty notes for suffix={pattern.suffix!r}")
                bass_pc = notes_midi[0] % 12
                self.assertEqual(
                    bass_pc,
                    _expected_bass_pc(intervals, inversion),
                    (
                        f"Wrong bass for suffix={pattern.suffix!r} inversion={inversion}: "
                        f"got_pc={bass_pc} expected_pc={_expected_bass_pc(intervals, inversion)} "
                        f"intervals={intervals} voiced={out['intervals']}"
                    ),
                )

    def test_generate_chord_extended_inversion_name_uses_correct_bass(self) -> None:
        out = generate_chord(
            root_pc=0,  # C
            suffix="add9",
            inversion=3,
            language="en",
            prefer_flat=False,
        )
        self.assertEqual(out["name"], "Cadd9/D")

    def test_backend_and_desktop_inversion_voicing_match(self) -> None:
        samples = [
            ("add9", [0, 4, 7, 14], 3),
            ("9", [0, 4, 7, 10, 14], 4),
            ("11", [0, 4, 7, 10, 14, 17], 4),
            ("13", [0, 4, 7, 10, 14, 21], 4),
            ("mMaj9", [0, 3, 7, 11, 14], 4),
            ("", [0, 4, 7], 2),
        ]
        for suffix, intervals, inversion in samples:
            desktop_voiced = GenerationMixin._voiced_intervals_for_inversion(intervals, inversion)
            backend_out = generate_chord(
                root_pc=0,
                suffix=suffix,
                inversion=inversion,
                language="en",
                prefer_flat=False,
            )
            backend_voiced = [int(i) for i in backend_out["intervals"]]
            self.assertEqual(desktop_voiced, backend_voiced)


if __name__ == "__main__":
    unittest.main()
