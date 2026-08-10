import inspect

from midichords.mixins.interval_mixin import IntervalMixin
from midichords.mixins.ui_mixin import UiMixin
from midichords.core.i18n import UI_TEXTS


class _Canvas:
    def __init__(self) -> None:
        self.visible = True

    def setVisible(self, visible: bool) -> None:
        self.visible = visible


class _Button:
    def __init__(self) -> None:
        self.text = ""
        self.selected = False

    def set_text(self, text: str) -> None:
        self.text = text

    def set_selected(self, selected: bool) -> None:
        self.selected = selected


class _ChordDetectionHarness(UiMixin):
    def __init__(self) -> None:
        self.detection_result_canvas = _Canvas()
        self.detection_details_toggle_btn = _Button()

    def tr(self, key: str) -> str:
        return key


class _IntervalDetectionHarness(IntervalMixin):
    def __init__(self) -> None:
        self.interval_result_canvas = _Canvas()
        self.interval_details_toggle_btn = _Button()

    def _get_ui_text(self, key: str) -> str:
        return key


def test_chord_detection_details_toggle_hides_and_restores_the_subpanel() -> None:
    app = _ChordDetectionHarness()

    app._toggle_detection_details()
    assert app.detection_result_canvas.visible is False
    assert app.detection_details_toggle_btn.text == "button_show_detection_details"
    assert app.detection_details_toggle_btn.selected is True

    app._toggle_detection_details()
    assert app.detection_result_canvas.visible is True
    assert app.detection_details_toggle_btn.text == "button_hide_detection_details"
    assert app.detection_details_toggle_btn.selected is False


def test_interval_detection_details_toggle_hides_and_restores_the_subpanel() -> None:
    app = _IntervalDetectionHarness()

    app._toggle_interval_details()
    assert app.interval_result_canvas.visible is False
    assert app.interval_details_toggle_btn.text == "button_show_detection_details"
    assert app.interval_details_toggle_btn.selected is True

    app._toggle_interval_details()
    assert app.interval_result_canvas.visible is True
    assert app.interval_details_toggle_btn.text == "button_hide_detection_details"
    assert app.interval_details_toggle_btn.selected is False


def test_detection_details_buttons_are_registered_in_contextual_help() -> None:
    help_items_source = inspect.getsource(UiMixin._help_items_for_mode)

    assert (
        "detection_details_toggle_btn:help_detect_details_toggle"
        in help_items_source
    )
    assert (
        "interval_details_toggle_btn:help_interval_details_toggle"
        in help_items_source
    )
    for language in ("es", "en"):
        assert UI_TEXTS[language]["help_detect_details_toggle"]
        assert UI_TEXTS[language]["help_interval_details_toggle"]
    assert "fines didácticos" in UI_TEXTS["es"]["help_detect_details_toggle"]
    assert "fines didácticos" in UI_TEXTS["es"]["help_interval_details_toggle"]
    assert "learning purposes" in UI_TEXTS["en"]["help_detect_details_toggle"]
    assert "learning purposes" in UI_TEXTS["en"]["help_interval_details_toggle"]
