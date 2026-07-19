import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_TEXTS_JS = PROJECT_ROOT / "apps" / "web" / "static" / "ui_texts.js"
APP_JS = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"
APP_HTML = PROJECT_ROOT / "apps" / "web" / "app.html"


class WebUiTextsTests(unittest.TestCase):
    def test_languages_have_the_same_keys(self):
        source = UI_TEXTS_JS.read_text(encoding="utf-8")
        spanish = source.split("  es: {", 1)[1].split("\n  },", 1)[0]
        english = source.split("  en: {", 1)[1].split("\n  },", 1)[0]
        key_pattern = re.compile(r"^    ([a-z0-9_]+):", re.MULTILINE)
        spanish_keys = set(key_pattern.findall(spanish))
        english_keys = set(key_pattern.findall(english))

        self.assertGreater(len(spanish_keys), 100)
        self.assertEqual(spanish_keys, english_keys)

    def test_catalog_is_loaded_before_the_spa(self):
        source = UI_TEXTS_JS.read_text(encoding="utf-8")
        app_source = APP_JS.read_text(encoding="utf-8")
        html = APP_HTML.read_text(encoding="utf-8")

        self.assertIn("global.MidiChordsUiTexts", source)
        self.assertIn("globalThis.MidiChordsUiTexts", app_source)
        self.assertLess(html.index("/static/ui_texts.js"), html.index("/static/app.js"))


if __name__ == "__main__":
    unittest.main()
