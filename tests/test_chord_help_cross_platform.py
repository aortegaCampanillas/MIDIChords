import json
import unittest
from pathlib import Path

from midichords.core.chord_help import chord_variant_groups, chord_variant_help
from midichords.core.music_theory import CHORD_PATTERNS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHARED_CATALOG = PROJECT_ROOT / "assets" / "chord_variant_theory.json"
MOBILE_CATALOG = PROJECT_ROOT / "apps" / "mobile_flutter" / "assets" / "chord_variant_theory.json"


class ChordHelpCrossPlatformTests(unittest.TestCase):
    def test_desktop_and_mobile_catalogs_are_identical_and_complete(self):
        shared = json.loads(SHARED_CATALOG.read_text(encoding="utf-8"))
        mobile = json.loads(MOBILE_CATALOG.read_text(encoding="utf-8"))
        suffixes = {pattern.suffix for pattern in CHORD_PATTERNS}

        self.assertEqual(shared, mobile)
        self.assertEqual(suffixes, set(shared["theory"]))
        self.assertEqual(52, len(shared["theory"]))

    def test_every_desktop_variant_and_inversion_has_help(self):
        for language in ("es", "en"):
            for pattern in CHORD_PATTERNS:
                for inversion in range(len(pattern.intervals)):
                    with self.subTest(language=language, suffix=pattern.suffix, inversion=inversion):
                        formula, theory, inversion_text = chord_variant_help(
                            pattern.suffix, inversion, language
                        )
                        self.assertTrue(formula)
                        self.assertGreater(len(theory), 40)
                        self.assertGreater(len(inversion_text), 40)

    def test_desktop_groups_contain_every_variant_once(self):
        suffixes = {pattern.suffix for pattern in CHORD_PATTERNS}
        for language in ("es", "en"):
            groups = chord_variant_groups(language, suffixes)
            grouped = [suffix for _label, values in groups for suffix in values]
            self.assertEqual(7, len(groups))
            self.assertEqual(len(grouped), len(set(grouped)))
            self.assertEqual(suffixes, set(grouped))

    def test_flutter_bundle_declares_and_uses_theory_catalog(self):
        pubspec = (PROJECT_ROOT / "apps" / "mobile_flutter" / "pubspec.yaml").read_text(encoding="utf-8")
        main = (PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main.dart").read_text(encoding="utf-8")
        helper = (PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "chord_variant_help.dart").read_text(
            encoding="utf-8"
        )

        self.assertIn("assets/chord_variant_theory.json", pubspec)
        self.assertIn("buildChordVariantDropdownItems", main)
        self.assertIn("_showChordVariantHelpDialog", main)
        self.assertIn("helpId: 'detection_variant_theory'", main)
        self.assertIn("'inversion': inversionIndex", main)
        self.assertIn("enabled: false", helper)

    def test_desktop_detection_reuses_variant_help_dialog(self):
        ui = (PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py").read_text(encoding="utf-8")
        generation = (PROJECT_ROOT / "midichords" / "mixins" / "generation_mixin.py").read_text(
            encoding="utf-8"
        )
        detection = (PROJECT_ROOT / "midichords" / "mixins" / "input_detection_mixin.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("self.detection_variant_help_btn = GrayRoundedButton", ui)
        self.assertIn("command=self.open_detection_variant_help_dialog", ui)
        self.assertIn("def open_detection_variant_help_dialog", generation)
        self.assertIn("self._open_chord_variant_help_dialog(", generation)
        self.assertIn("self.detection_variant_help_inversion = next(", detection)

    def test_desktop_help_dialog_fits_content_and_keeps_close_button_last(self):
        generation = (PROJECT_ROOT / "midichords" / "mixins" / "generation_mixin.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('dialog.geometry("640x430")', generation)
        self.assertNotIn('close_btn.pack(side=tk.BOTTOM', generation)
        self.assertIn('close_btn.pack(anchor="e"', generation)
        self.assertIn("padding=(20, 18, 20, 18)", generation)
        self.assertIn("dialog.setFixedSize(640, content_height)", generation)


if __name__ == "__main__":
    unittest.main()
