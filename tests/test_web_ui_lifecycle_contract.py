import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_JS = PROJECT_ROOT / "apps" / "web" / "static" / "app.js"


class WebUiLifecycleContractTests(unittest.TestCase):
    def test_bind_events_registers_controls_through_the_shared_lifecycle(self):
        source = APP_JS.read_text(encoding="utf-8")
        bind_events = source.split("function bindEvents() {", 1)[1].split(
            "async function main() {", 1
        )[0]

        self.assertIn("uiLifecycle.listen", bind_events)
        self.assertNotIn(".addEventListener(", bind_events)


if __name__ == "__main__":
    unittest.main()
