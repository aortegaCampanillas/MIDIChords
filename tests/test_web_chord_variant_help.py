import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"
WORKER_JS = PROJECT_ROOT / "apps" / "web" / "worker" / "_worker.js"
APP_HTML = PROJECT_ROOT / "apps" / "web" / "app.html"


class WebChordVariantHelpTests(unittest.TestCase):
    @staticmethod
    def chord_pattern_suffixes():
        worker_source = WORKER_JS.read_text(encoding="utf-8")
        pattern_block = worker_source.split("const COMMON_CHORD_SUFFIX_ORDER", 1)[0]
        return set(re.findall(r'\{ suffix: "([^"]*)", intervals:', pattern_block))

    def test_every_generated_chord_variant_has_bilingual_theory(self):
        pattern_suffixes = self.chord_pattern_suffixes()

        app_source = APP_JS.read_text(encoding="utf-8")
        theory_block = app_source.split("const CHORD_VARIANT_THEORY = {", 1)[1].split("\n};", 1)[0]
        theory_entries = re.findall(r'^  "([^"]*)": \["([^"]+)", "(.+)", "(.+)"\],$', theory_block, re.MULTILINE)
        theory_by_suffix = {suffix: (formula, es, en) for suffix, formula, es, en in theory_entries}

        self.assertEqual(52, len(pattern_suffixes))
        self.assertEqual(pattern_suffixes, set(theory_by_suffix))
        for suffix, (formula, es, en) in theory_by_suffix.items():
            with self.subTest(suffix=suffix):
                self.assertTrue(formula.strip())
                self.assertGreater(len(es), 40)
                self.assertGreater(len(en), 40)

    def test_variant_groups_classify_every_chord_once(self):
        app_source = APP_JS.read_text(encoding="utf-8")
        groups_block = app_source.split("const CHORD_VARIANT_GROUPS = [", 1)[1].split("\n];", 1)[0]
        suffix_lists = re.findall(r'labelKey: "[^"]+", suffixes: \[([^\]]*)\]', groups_block)
        grouped_suffixes = [
            suffix
            for suffix_list in suffix_lists
            for suffix in re.findall(r'"([^"]*)"', suffix_list)
        ]

        self.assertEqual(7, len(suffix_lists))
        self.assertEqual(52, len(grouped_suffixes))
        self.assertEqual(len(grouped_suffixes), len(set(grouped_suffixes)))
        self.assertEqual(self.chord_pattern_suffixes(), set(grouped_suffixes))
        self.assertIn('document.createElement("optgroup")', app_source)
        self.assertIn('tr("chord_group_other")', app_source)

    def test_help_button_and_accessible_modal_are_present(self):
        html = APP_HTML.read_text(encoding="utf-8")
        self.assertIn('id="genVariantHelp"', html)
        self.assertIn('id="detectVariantHelp"', html)
        self.assertIn('id="chordVariantHelpModal"', html)
        self.assertIn('id="chordVariantHelpInversionText"', html)
        self.assertIn('aria-modal="true"', html)
        self.assertIn('aria-labelledby="chordVariantHelpTitle"', html)

        app_source = APP_JS.read_text(encoding="utf-8")
        self.assertIn('showChordVariantHelpModal("detection")', app_source)
        self.assertIn('state.detectionResult?.suffix', app_source)

        worker_source = WORKER_JS.read_text(encoding="utf-8")
        self.assertIn("inversion: inversionIndex", worker_source)

    def test_help_describes_inversions_for_every_formula_degree(self):
        app_source = APP_JS.read_text(encoding="utf-8")
        inversion_block = app_source.split("const MAJOR_CHORD_INVERSION_THEORY = [", 1)[1].split("\n];", 1)[0]
        entries = re.findall(r'^  \["(.+)", "(.+)"\],$', inversion_block, re.MULTILINE)

        self.assertEqual(3, len(entries))
        self.assertTrue(entries[0][0].startswith("Posición fundamental:"))
        self.assertTrue(entries[1][0].startswith("Primera inversión:"))
        self.assertTrue(entries[2][0].startswith("Segunda inversión:"))

        theory_block = app_source.split("const CHORD_VARIANT_THEORY = {", 1)[1].split("\n};", 1)[0]
        formulas = re.findall(r'^  "[^"]*": \["([^"]+)"', theory_block, re.MULTILINE)
        formula_degrees = {degree for formula in formulas for degree in formula.split(" - ")}
        degree_names_block = app_source.split("const CHORD_DEGREE_NAMES = {", 1)[1].split("\n};", 1)[0]
        spanish_block = degree_names_block.split("es: {", 1)[1].split("\n  },", 1)[0]
        named_degrees = set(re.findall(r'^    "([^"]+)":', spanish_block, re.MULTILINE))

        self.assertEqual(formula_degrees, named_degrees)
        self.assertLessEqual(max(len(formula.split(" - ")) for formula in formulas), 7)
        self.assertIn("function chordInversionTheory", app_source)
        self.assertIn(": chordInversionTheory(theory[0], inversion, state.language)", app_source)


if __name__ == "__main__":
    unittest.main()
