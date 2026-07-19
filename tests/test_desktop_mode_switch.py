from __future__ import annotations

import sys
import unittest

from midichords.main_app import _configure_qt_application_identity
from midichords.mixins.ui_mixin import UiMixin
from midichords.mixins.input_detection_mixin import InputDetectionMixin


class _Variable:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value


class _ModeSwitchHarness:
    def __init__(self) -> None:
        self.mode_var = _Variable()
        self.closed = 0
        self.changed = 0
        self.scheduled: list[tuple[str, object]] = []
        self.cancelled: list[str] = []

    def _available_mode_keys(self) -> list[str]:
        return ["detection", "generation", "circle_fifths"]

    def _mode_label(self, mode_key: str) -> str:
        return mode_key

    def _close_mode_selector_overlay(self) -> None:
        self.closed += 1

    def _on_mode_combo_changed(self, _event: object) -> None:
        self.changed += 1

    def after(self, delay: int, callback: object) -> str:
        identifier = f"after-{len(self.scheduled) + 1}"
        self.scheduled.append((identifier, callback))
        self.last_delay = delay
        return identifier

    def after_cancel(self, identifier: str) -> None:
        self.cancelled.append(identifier)

    _schedule_mode_change = UiMixin._schedule_mode_change


class DesktopModeSwitchTests(unittest.TestCase):
    def test_mode_card_closes_before_deferred_transition(self) -> None:
        harness = _ModeSwitchHarness()

        UiMixin._apply_mode(harness, "circle_fifths")

        self.assertEqual(harness.mode_var.value, "circle_fifths")
        self.assertEqual(harness.closed, 1)
        self.assertEqual(harness.changed, 0)
        self.assertEqual(harness.last_delay, 0)
        callback = harness.scheduled[0][1]
        callback()  # type: ignore[operator]
        self.assertEqual(harness.changed, 1)
        self.assertIsNone(harness._mode_change_after_id)

    def test_new_selection_cancels_pending_transition(self) -> None:
        harness = _ModeSwitchHarness()

        UiMixin._apply_mode(harness, "generation")
        UiMixin._apply_mode(harness, "circle_fifths")

        self.assertEqual(harness.cancelled, ["after-1"])
        self.assertEqual(harness.mode_var.value, "circle_fifths")


class _MusicViewsHarness:
    def __init__(self, instrument_view: str) -> None:
        self.instrument_view = instrument_view


class DesktopGuitarRefreshTests(unittest.TestCase):
    def test_piano_updates_do_not_compute_guitar_variations(self) -> None:
        harness = _MusicViewsHarness("piano")

        should_refresh = InputDetectionMixin._guitar_variations_should_refresh(harness)  # type: ignore[arg-type]

        self.assertFalse(should_refresh)

    def test_guitar_updates_refresh_guitar_variations(self) -> None:
        harness = _MusicViewsHarness("guitar")

        should_refresh = InputDetectionMixin._guitar_variations_should_refresh(harness)  # type: ignore[arg-type]

        self.assertTrue(should_refresh)


class _ApplicationIdentityHarness:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def setApplicationName(self, value: str) -> None:
        self.values["name"] = value

    def setApplicationDisplayName(self, value: str) -> None:
        self.values["display_name"] = value

    def setOrganizationName(self, value: str) -> None:
        self.values["organization"] = value

    def setOrganizationDomain(self, value: str) -> None:
        self.values["domain"] = value

    def setDesktopFileName(self, value: str) -> None:
        self.values["desktop_file_name"] = value


class DesktopApplicationIdentityTests(unittest.TestCase):
    def test_qt_identity_uses_product_name(self) -> None:
        app = _ApplicationIdentityHarness()

        _configure_qt_application_identity(app)  # type: ignore[arg-type]

        self.assertEqual(app.values["name"], "MIDIChords")
        self.assertEqual(app.values["display_name"], "MIDIChords")
        self.assertEqual(app.values["organization"], "MIDIChords")
        self.assertEqual(app.values["domain"], "midichords.app")
        if sys.platform.startswith("linux"):
            self.assertEqual(app.values["desktop_file_name"], "midichords")

if __name__ == "__main__":
    unittest.main()
