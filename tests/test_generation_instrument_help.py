import unittest
from pathlib import Path

from midichords.core.i18n import UI_TEXTS


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class GenerationInstrumentHelpTests(unittest.TestCase):
    def test_desktop_generation_help_describes_read_only_instruments(self):
        for language in ("es", "en"):
            chord_help = UI_TEXTS[language]["help_gen_instrument_piano"]
            interval_help = UI_TEXTS[language]["help_interval_gen_instrument"]

            self.assertNotIn("interactive", chord_help.lower())
            self.assertNotIn("interactive", interval_help.lower())
            self.assertNotIn("pulsa", chord_help.lower())
            self.assertNotIn("press ", chord_help.lower())
            self.assertIn(
                "reproducción" if language == "es" else "play",
                chord_help.lower(),
            )

    def test_web_interval_generation_has_its_own_surface_help(self):
        texts = (
            PROJECT_ROOT / "apps" / "web" / "static" / "ui_texts.js"
        ).read_text(encoding="utf-8")
        callouts = (
            PROJECT_ROOT / "apps" / "web" / "static" / "help_callouts.js"
        ).read_text(encoding="utf-8")

        self.assertIn("help_instrument_surface_interval_generation", texts)
        self.assertIn(
            'textKey: "help_instrument_surface_interval_generation"',
            callouts,
        )
        self.assertIn(
            'textKey: "help_staff_interval_generation"',
            callouts,
        )
        self.assertIn("Click one to preview it and highlight it", texts)
        self.assertNotIn("does not detect or change the interval", texts)
        self.assertIn("shown as a reference", texts)

    def test_mobile_interval_generation_does_not_reuse_detection_help(self):
        main = (
            PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main.dart"
        ).read_text(encoding="utf-8")
        help_source = (
            PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main_help.dart"
        ).read_text(encoding="utf-8")

        self.assertIn("7 => 'interval_generation_instrument'", main)
        self.assertIn("7 => 'interval_generation_staff'", help_source)
        self.assertIn("Shows the generated interval notes as a reference.", help_source)
        self.assertIn("Generated interval staff", help_source)
        self.assertIn("a note to preview it and highlight it", help_source)
        self.assertNotIn("this does not detect or change the interval", help_source)

    def test_desktop_interval_generation_has_its_own_staff_help(self):
        ui_mixin = (
            PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py"
        ).read_text(encoding="utf-8")

        for language in ("es", "en"):
            text = UI_TEXTS[language]["help_interval_gen_staff"]
            self.assertIn(
                "previsualizar" if language == "es" else "preview",
                text.lower(),
            )
        self.assertIn(
            '"staff_canvas:help_interval_gen_staff"',
            ui_mixin,
        )


if __name__ == "__main__":
    unittest.main()
