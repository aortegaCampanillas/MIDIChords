"""Tests sin red para el parser del chequeo de salud web."""

import importlib.util
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "check_production_web_health.py"
_spec = importlib.util.spec_from_file_location("check_production_web_health", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class TestAssetParser(unittest.TestCase):
    def test_finds_stylesheet_and_script(self) -> None:
        p = _mod.AssetParser()
        p.feed(
            '<html><head><link rel="stylesheet" href="/static/style.css" /></head>'
            '<body><script src="/static/app.js"></script></body></html>'
        )
        p.close()
        self.assertTrue(any("style.css" in h for h in p.stylesheet_hrefs))
        self.assertTrue(any("app.js" in s for s in p.script_srcs))

    def test_relative_urls_resolved(self) -> None:
        from urllib.parse import urljoin

        base = "https://example.com/"
        p = _mod.AssetParser()
        p.feed(
            '<link rel="stylesheet" href="/static/style.css?v=1"/>'
            '<script src="/static/app.js?v=1"></script>'
        )
        p.close()
        css = [urljoin(base, h) for h in p.stylesheet_hrefs]
        js = [urljoin(base, h) for h in p.script_srcs]
        self.assertTrue(_mod.pick_static_url(css, "style.css"))
        self.assertTrue(_mod.pick_static_url(js, "app.js"))


if __name__ == "__main__":
    unittest.main()
