import unittest

from midichords.core.music_theory import CHORD_PATTERNS
from scripts.sync_guitar_chord_reference import (
    REFERENCE_SLUG_BY_SUFFIX,
    UNSUPPORTED_REFERENCE_SUFFIXES,
    _metadata,
    _signature,
)


class GuitarChordReferenceSyncTests(unittest.TestCase):
    def test_every_app_suffix_is_mapped_or_explicitly_unsupported(self):
        app_suffixes = {pattern.suffix for pattern in CHORD_PATTERNS}
        self.assertEqual(
            app_suffixes,
            set(REFERENCE_SLUG_BY_SUFFIX) | UNSUPPORTED_REFERENCE_SUFFIXES,
        )
        self.assertFalse(set(REFERENCE_SLUG_BY_SUFFIX) & UNSUPPORTED_REFERENCE_SUFFIXES)

    def test_svg_metadata_parser_requires_six_values(self):
        svg = '<metadata id="frets">[-1, 3, 2, 0, 1, 0]</metadata>'
        self.assertEqual([-1, 3, 2, 0, 1, 0], _metadata(svg, "frets"))
        with self.assertRaises(ValueError):
            _metadata('<metadata id="frets">[1, 2]</metadata>', "frets")
        with self.assertRaises(ValueError):
            _metadata(svg, "fingers")

    def test_signature_compares_only_reference_frets_and_fingers(self):
        entries = [
            {
                "frets": [-1, 3, 2, 0, 1, 0],
                "fingers": [0, 3, 2, 0, 1, 0],
                "notes": [48, 52, 55, 60, 64],
            }
        ]
        self.assertEqual(
            [([-1, 3, 2, 0, 1, 0], [0, 3, 2, 0, 1, 0])],
            _signature(entries),
        )


if __name__ == "__main__":
    unittest.main()
