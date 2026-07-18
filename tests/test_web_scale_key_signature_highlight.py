import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"


class WebScaleKeySignatureHighlightTests(unittest.TestCase):
    def test_scale_current_note_drives_key_signature_highlight(self):
        source = APP_JS.read_text(encoding="utf-8")

        self.assertIn("function activeScaleKeySignatureIndex(sig)", source)
        self.assertIn('state.mode !== "scales" || state.scaleCurrentNote == null', source)
        self.assertIn("scaleLabelForMidi(state.scaleCurrentNote)", source)
        self.assertIn("activeScaleKeySignatureIndex(staffCtx.signature)", source)
        self.assertIn("active ? \"#6fe0ff\" : \"#e9edf2\"", source)

    def test_all_seven_sharp_and_flat_signature_positions_are_supported(self):
        source = APP_JS.read_text(encoding="utf-8")

        self.assertIn("KEY_SIG_SHARP_NATURAL_PC_ORDER = [5, 0, 7, 2, 9, 4, 11]", source)
        self.assertIn("KEY_SIG_FLAT_NATURAL_PC_ORDER = [11, 4, 9, 2, 7, 0, 5]", source)
        self.assertIn("accidentalCount !== 1", source)
        self.assertIn("index < Number(sig.count)", source)

    def test_both_staves_receive_the_same_active_accidental(self):
        source = APP_JS.read_text(encoding="utf-8")
        grand_block = source.split("function drawGrandKeySignature", 1)[1].split("\n}", 1)[0]

        self.assertEqual(2, grand_block.count(", activeIndex)"))
        self.assertIn("false, activeIndex", grand_block)
        self.assertIn("true, activeIndex", grand_block)


if __name__ == "__main__":
    unittest.main()
