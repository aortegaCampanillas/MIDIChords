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
        mobile_ui = main + (
            PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main_pages.dart"
        ).read_text(encoding="utf-8")
        help_source = (
            PROJECT_ROOT / "apps" / "mobile_flutter" / "lib" / "main_help.dart"
        ).read_text(encoding="utf-8")

        self.assertIn("7 => 'interval_generation_instrument'", main)
        self.assertIn("7 => 'interval_generation_staff'", help_source)
        self.assertIn("Piano or guitar view of the generated interval.", help_source)
        self.assertIn("Generated interval staff", help_source)
        self.assertIn("Tap one to preview it and highlight it", help_source)
        self.assertNotIn("this does not detect or change the interval", help_source)

        for help_id in (
            "interval_generation_root",
            "interval_generation_notes",
            "interval_generation_name",
            "interval_generation_semitones",
            "interval_generation_table",
        ):
            self.assertIn(f"'{help_id}'", mobile_ui)
            self.assertIn(f"id: '{help_id}'", help_source)

        for text in (
            "Notes: the tonic and the resulting note of the chosen interval.",
            "Name of the interval selected in the table.",
            "Number of semitones between the two notes.",
            "Tonic from which the chosen table interval is generated.",
            "each column is a number of semitones",
        ):
            self.assertIn(text, help_source)

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

    def test_desktop_interval_generation_result_help_matches_web(self):
        ui_mixin = (
            PROJECT_ROOT / "midichords" / "mixins" / "ui_mixin.py"
        ).read_text(encoding="utf-8")

        expected = {
            "es": {
                "help_interval_gen_notes": "Notas: la tónica y la nota resultante del intervalo elegido.",
                "help_interval_gen_name": "Nombre del intervalo seleccionado en la tabla.",
                "help_interval_gen_alt": "Otros nombres enarmónicos válidos para el mismo número de semitonos.",
                "help_interval_gen_semitones": "Número de semitonos entre las dos notas.",
            },
            "en": {
                "help_interval_gen_notes": "Notes: the tonic and the resulting note of the chosen interval.",
                "help_interval_gen_name": "Name of the interval selected in the table.",
                "help_interval_gen_alt": "Other valid enharmonic names for the same number of semitones.",
                "help_interval_gen_semitones": "Number of semitones between the two notes.",
            },
        }
        for language, texts in expected.items():
            for key, value in texts.items():
                self.assertEqual(UI_TEXTS[language][key], value)

        self.assertIn(
            '"interval_gen_notes_row:help_interval_gen_notes"',
            ui_mixin,
        )
        self.assertNotIn(
            '"interval_gen_notes_row:help_interval_notes"',
            ui_mixin,
        )


if __name__ == "__main__":
    unittest.main()
