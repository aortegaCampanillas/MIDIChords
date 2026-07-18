from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

import midichords.main_app as main_app
from midichords.main_app import MidiChordAnalyzerApp


class _SilentAudioEngine:
    def __getattr__(self, _name: str):
        return lambda *args, **kwargs: None


def test_desktop_ui_exposes_stable_widget_and_mode_contract(monkeypatch) -> None:
    qt_app = QApplication.instance() or QApplication(["midichords-ui-contract"])
    monkeypatch.setattr(main_app, "PianoAudioEngine", _SilentAudioEngine)
    monkeypatch.setattr(main_app, "load_guitar_chord_cache", lambda: {})
    monkeypatch.setattr(MidiChordAnalyzerApp, "load_config", lambda self: None)
    monkeypatch.setattr(MidiChordAnalyzerApp, "save_config", lambda self: None)
    monkeypatch.setattr(MidiChordAnalyzerApp, "_complete_startup", lambda self: None)

    window = MidiChordAnalyzerApp()
    try:
        required_widgets = (
            "mode_picker_trigger",
            "top_right_controls",
            "left_panel",
            "right_panel",
            "staff_canvas",
            "keyboard_canvas",
            "guitar_canvas",
            "tab_generation_frame",
            "tab_circle_frame",
            "tab_scale_frame",
            "tab_interval_frame",
            "tab_metronome_frame",
            "generation_variant_combo",
            "generation_inversion_combo",
        )
        for attribute in required_widgets:
            assert isinstance(getattr(window, attribute), QWidget), attribute
        assert window.staff_canvas.parent() is window.left_panel.content
        assert window.chord_panel.parent() is window.right_side_panel
        assert window.tab_generation_frame.parent() is window.chord_panel
        assert window.generation_root_combo.maxVisibleItems() == 12
        assert window.generation_root_combo.parent() is window.generation_root_row
        assert (
            window.generation_root_accidental_combo.parent()
            is window.generation_root_row
        )
        assert window.generation_root_row.parent() is window.tab_generation_frame
        assert window.generation_root_combo.isEditable() is False
        assert window.generation_root_accidental_combo.isEditable() is False
        assert window.generation_variant_combo.parent() is window.tab_generation_frame
        assert window.generation_variant_combo.isEditable() is False
        assert window.generation_variant_combo.maxVisibleItems() == 16
        assert window.generation_inversion_combo.parent() is window.tab_generation_frame
        assert window.generation_inversion_combo.isEditable() is False
        assert window.scale_tonic_combo.maxVisibleItems() == 15
        assert window.scale_tonic_combo.parent() is window.scale_tonic_row
        assert window.scale_tonic_accidental_combo.parent() is window.scale_tonic_row
        assert window.scale_tonic_row.parent() is window.tab_scale_frame
        assert window.scale_type_combo.maxVisibleItems() == 20
        assert window.scale_type_combo.parent() is not window.tab_scale_frame
        assert window.scale_type_combo.parent().parent() is window.tab_scale_frame
        assert window.scale_inline_filter_btn.parent() is window.scale_type_combo.parent()

        window._apply_mode("circle_fifths")
        qt_app.processEvents()

        assert window.current_mode == "circle_fifths"
        assert window.generation_tab_active is True
        assert window.circle_fifths_tab_active is True
        assert window.scale_tab_active is False

        window._apply_mode("scales")
        qt_app.processEvents()

        assert window.current_mode == "scales"
        assert window.generation_tab_active is False
        assert window.circle_fifths_tab_active is False
        assert window.scale_tab_active is True
    finally:
        window.close()
        window.deleteLater()
        qt_app.processEvents()
