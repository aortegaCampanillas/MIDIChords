import json
import re
import unittest
from pathlib import Path

from midichords.core.changelog import get_changelog_path
from midichords.core.music_theory import CHORD_PATTERNS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ASSETS = PROJECT_ROOT / "assets"
WEB_ASSETS = PROJECT_ROOT / "apps" / "web" / "static"
MOBILE_ASSETS = PROJECT_ROOT / "apps" / "mobile_flutter" / "assets"


class SharedAssetsCrossPlatformTests(unittest.TestCase):
    def assert_same_copy(self, relative_path: str) -> None:
        paths = [
            DESKTOP_ASSETS / relative_path,
            WEB_ASSETS / relative_path,
            MOBILE_ASSETS / relative_path,
        ]
        for path in paths:
            self.assertTrue(path.is_file(), f"Falta la copia compartida: {path}")
        canonical = paths[0].read_bytes()
        for path in paths[1:]:
            self.assertEqual(canonical, path.read_bytes(), f"Copia desincronizada: {path}")

    def test_shared_data_and_metronome_sample_are_identical(self):
        for relative_path in ("guitar_chord_cache.json", "metronome.mp3"):
            with self.subTest(relative_path=relative_path):
                self.assert_same_copy(relative_path)

    def test_guitar_cache_covers_every_chord_pattern(self):
        cache = json.loads(
            (DESKTOP_ASSETS / "guitar_chord_cache.json").read_text(encoding="utf-8")
        )["by_app_key"]
        for pattern in CHORD_PATTERNS:
            for root_pc in range(12):
                key = f"{root_pc}|{pattern.suffix}"
                with self.subTest(key=key):
                    self.assertTrue(cache.get(key), f"Faltan digitaciones para {key}")

    def test_added_note_voicings_show_one_playable_shape(self):
        cache = json.loads(
            (DESKTOP_ASSETS / "guitar_chord_cache.json").read_text(encoding="utf-8")
        )["by_app_key"]
        patterns = {
            pattern.suffix: pattern.intervals
            for pattern in CHORD_PATTERNS
            if pattern.suffix in {"add2", "add4", "madd2", "madd4"}
        }
        for suffix, intervals in patterns.items():
            for root_pc in range(12):
                expected_pcs = {(root_pc + interval) % 12 for interval in intervals}
                for variation in cache[f"{root_pc}|{suffix}"]:
                    frets = variation["frets"]
                    notes = variation["notes"]
                    with self.subTest(suffix=suffix, root_pc=root_pc, frets=frets):
                        self.assertEqual(6, len(frets))
                        self.assertLessEqual(len(notes), 6)
                        self.assertEqual(expected_pcs, {note % 12 for note in notes})

    def test_add2_exposes_the_three_reference_voicings_for_every_root(self):
        cache = json.loads(
            (DESKTOP_ASSETS / "guitar_chord_cache.json").read_text(encoding="utf-8")
        )["by_app_key"]
        expected = {
            0: [[-1, 3, 2, 0, 3, -1], [-1, 3, 5, 7, 5, 3], [-1, -1, 10, 9, 8, 10]],
            1: [[-1, 4, 3, 1, 4, -1], [-1, 4, 6, 8, 6, 4], [-1, -1, 11, 10, 9, 11]],
            2: [[-1, 5, 4, 2, 5, -1], [-1, 5, 7, 9, 7, 5], [-1, -1, 12, 11, 10, 12]],
            3: [[-1, 6, 5, 3, 6, -1], [-1, 6, 8, 10, 8, 6], [-1, -1, 13, 12, 11, 13]],
            4: [[-1, -1, 2, 1, 0, 2], [-1, 7, 6, 4, 7, -1], [-1, 7, 9, 11, 9, 7]],
            5: [[-1, 8, 7, 5, 8, -1], [-1, 8, 10, 12, 10, 8], [-1, -1, 3, 2, 1, 3]],
            6: [[-1, 9, 8, 6, 9, -1], [-1, 9, 11, 13, 11, 9], [-1, -1, 4, 3, 2, 4]],
            7: [[-1, 10, 9, 7, 10, -1], [-1, 10, 12, 14, 12, 10], [-1, -1, 5, 4, 3, 5]],
            8: [[-1, 11, 10, 8, 11, -1], [-1, 11, 13, 15, 13, 11], [-1, -1, 6, 5, 4, 6]],
            9: [[-1, 0, 2, 4, 2, 0], [-1, 12, 11, 9, 12, -1], [-1, -1, 7, 6, 5, 7]],
            10: [[-1, 13, 12, 10, 13, -1], [-1, 1, 3, 5, 3, 1], [-1, -1, 8, 7, 6, 8]],
            11: [[-1, 14, 13, 11, 14, -1], [-1, 2, 4, 6, 4, 2], [-1, -1, 9, 8, 7, 9]],
        }
        standard_fingers = [[0, 3, 2, 1, 4, 0], [0, 1, 2, 4, 3, 1], [0, 0, 3, 2, 1, 4]]
        expected_fingers = {root_pc: standard_fingers for root_pc in range(12)}
        expected_fingers[0] = [[0, 2, 1, 0, 3, 0], standard_fingers[1], standard_fingers[2]]
        expected_fingers[4] = [[0, 0, 2, 1, 0, 3], standard_fingers[0], standard_fingers[1]]
        expected_fingers[9] = [[0, 0, 1, 4, 2, 0], standard_fingers[0], standard_fingers[2]]
        for root_pc, frets in expected.items():
            with self.subTest(root_pc=root_pc):
                self.assertEqual(
                    frets,
                    [variation["frets"] for variation in cache[f"{root_pc}|add2"]],
                )
                self.assertEqual(
                    expected_fingers[root_pc],
                    [variation["fingers"] for variation in cache[f"{root_pc}|add2"]],
                )

    def test_add4_exposes_the_two_reference_voicings_for_every_root(self):
        cache = json.loads(
            (DESKTOP_ASSETS / "guitar_chord_cache.json").read_text(encoding="utf-8")
        )["by_app_key"]
        expected = {
            0: [[8, 8, 10, 9, 8, 8], [-1, 3, 3, 5, 5, 3]],
            1: [[9, 9, 11, 10, 9, 9], [-1, 4, 4, 6, 6, 4]],
            2: [[10, 10, 12, 11, 10, 10], [-1, 5, 5, 7, 7, 5]],
            3: [[11, 11, 13, 12, 11, 11], [-1, 6, 6, 8, 8, 6]],
            4: [[0, 0, 2, 1, 0, 0], [-1, 7, 7, 9, 9, 7]],
            5: [[1, 1, 3, 2, 1, 1], [-1, 8, 8, 10, 10, 8]],
            6: [[2, 2, 4, 3, 2, 2], [-1, 9, 9, 11, 11, 9]],
            7: [[3, 3, 5, 4, 3, 3], [-1, 10, 10, 12, 12, 10]],
            8: [[4, 4, 6, 5, 4, 4], [-1, 11, 11, 13, 13, 11]],
            9: [[-1, 0, 0, 2, 2, 0], [5, 5, 7, 6, 5, 5]],
            10: [[6, 6, 8, 7, 6, 6], [-1, 1, 1, 3, 3, 1]],
            11: [[7, 7, 9, 8, 7, 7], [-1, 2, 2, 4, 4, 2]],
        }
        e_fingers = [1, 1, 3, 2, 1, 1]
        a_fingers = [0, 1, 1, 3, 4, 1]
        expected_fingers = {root_pc: [e_fingers, a_fingers] for root_pc in range(12)}
        expected_fingers[4] = [[0, 0, 2, 1, 0, 0], a_fingers]
        expected_fingers[9] = [[0, 0, 0, 2, 3, 0], e_fingers]
        for root_pc, frets in expected.items():
            with self.subTest(root_pc=root_pc):
                variations = cache[f"{root_pc}|add4"]
                self.assertEqual(frets, [variation["frets"] for variation in variations])
                self.assertEqual(
                    expected_fingers[root_pc],
                    [variation["fingers"] for variation in variations],
                )

    def test_shared_guitar_sample_bank_is_complete_and_identical(self):
        relative_dir = Path("samples/guitar_nylon")
        expected_names = {path.name for path in (DESKTOP_ASSETS / relative_dir).glob("*.mp3")}
        self.assertEqual(
            {"A2.mp3", "B3.mp3", "D3.mp3", "E2.mp3", "E3.mp3", "E4.mp3", "G3.mp3"},
            expected_names,
        )
        for asset_root in (WEB_ASSETS, MOBILE_ASSETS):
            self.assertEqual(
                expected_names,
                {path.name for path in (asset_root / relative_dir).glob("*.mp3")},
            )
        for name in sorted(expected_names):
            with self.subTest(sample=name):
                self.assert_same_copy(str(relative_dir / name))

    def test_changelog_copy_used_by_mobile_matches_web_and_desktop_source(self):
        web_changelog = WEB_ASSETS / "changelog.json"
        mobile_changelog = MOBILE_ASSETS / "changelog.json"
        self.assertEqual(web_changelog.resolve(), get_changelog_path().resolve())
        self.assertEqual(web_changelog.read_bytes(), mobile_changelog.read_bytes())

    def test_changelog_text_does_not_repeat_platform_field(self):
        changelog = json.loads((WEB_ASSETS / "changelog.json").read_text(encoding="utf-8"))
        redundant_prefix = re.compile(
            r"^(?:Web|Escritorio|Móvil|Todas las plataformas|Desktop|Mobile|All platforms)\b|^[^:]{1,60} "
            r"(?:en (?:web|escritorio|móvil|todas las plataformas)|on every platform):",
            re.IGNORECASE,
        )
        for version in changelog:
            for item in version.get("items", []):
                if not item.get("platforms"):
                    continue
                for language in ("es", "en"):
                    text = str(item.get(language, ""))
                    with self.subTest(version=version.get("version"), date=item.get("date"), language=language):
                        self.assertIsNone(redundant_prefix.search(text), text)


if __name__ == "__main__":
    unittest.main()
