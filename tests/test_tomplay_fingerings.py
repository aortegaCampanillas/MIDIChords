"""Regression tests for desktop scale fingering lookup."""

from __future__ import annotations

import unittest

from midichords.core.tomplay_fingerings import get_fingering_for_scale


class TomplayFingeringsTests(unittest.TestCase):
    def test_major_pentatonic_returns_fingers_for_all_tonics(self) -> None:
        for tonic_pc in range(12):
            with self.subTest(tonic_pc=tonic_pc):
                right = get_fingering_for_scale("Major Pentatonic", tonic_pc, "right", count=6)
                left = get_fingering_for_scale("major_pentatonic", tonic_pc, "left", count=6)
                self.assertEqual(len(right), 6)
                self.assertEqual(len(left), 6)
                self.assertTrue(all(1 <= finger <= 5 for finger in right + left))

    def test_short_scale_patterns_extend_for_multiple_octaves(self) -> None:
        self.assertEqual(
            len(get_fingering_for_scale("major_pentatonic", 0, "right", count=11)),
            11,
        )
        self.assertEqual(
            len(get_fingering_for_scale("whole_tone_(wt)", 10, "left", count=13)),
            13,
        )
        self.assertEqual(
            len(get_fingering_for_scale("chromatic", 0, "right", count=25)),
            25,
        )

    def test_blues_pentatonic_uses_minor_pentatonic_table(self) -> None:
        self.assertEqual(
            get_fingering_for_scale("Blues Pentatonic", 9, "right", count=6),
            get_fingering_for_scale("Minor Pentatonic", 9, "right", count=6),
        )


if __name__ == "__main__":
    unittest.main()
