import json
import re
import unittest
from pathlib import Path

from midichords.core.changelog import get_changelog_path


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
