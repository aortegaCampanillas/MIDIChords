from pathlib import Path

from midichords.mixins.generation_mixin import GenerationMixin


ROOT = Path(__file__).resolve().parents[1]


class _DesktopGenerationHarness(GenerationMixin):
    generation_tab_active = True
    instrument_view = "piano"
    generated_preview_notes = {60, 64, 67}


def test_desktop_generation_hand_controls_playback_registers():
    harness = _DesktopGenerationHarness()
    harness.generation_hand = "right"
    assert harness._generation_piano_staff_midi_notes() == {60, 64, 67}
    harness.generation_hand = "left"
    assert harness._generation_piano_staff_midi_notes() == {48, 52, 55}
    harness.generation_hand = "both"
    assert harness._generation_piano_staff_midi_notes() == {48, 52, 55, 60, 64, 67}


def test_desktop_keeps_distinct_idle_colors_for_each_hand():
    source = (ROOT / "midichords/mixins/render_mixin.py").read_text(encoding="utf-8")
    assert "display_active_notes = set(self.generated_playing_notes)" in source
    assert 'note in generation_lh_display_notes:\n                fill_color = "#ff8a2b"' in source
    assert 'note in generation_rh_display_notes:\n                fill_color = "#4da3ea"' in source


def test_mobile_generation_hand_defaults_to_both_and_mode_entry_is_silent():
    source = (ROOT / "apps/mobile_flutter/lib/main.dart").read_text(encoding="utf-8")
    pages = (ROOT / "apps/mobile_flutter/lib/main_pages.dart").read_text(encoding="utf-8")
    assert "String _generationHand = 'both'" in source
    assert "Future<void> _callGenerateChord({bool playPreview = false})" in source
    assert "if (playPreview) unawaited(_playChordPreviewFromSelection())" in source
    assert "_generationPlaybackNotes()" in pages
    assert "_buildGenerationHandRow()" in pages
