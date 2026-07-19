from __future__ import annotations

import pytest

from midichords.mixins.render_mixin import RenderMixin


def test_secondary_beam_stub_follows_rising_primary_beam() -> None:
    end_x, end_y = RenderMixin._parallel_beam_endpoint(
        100.0, 50.0, 70.0, 40.0, 60.0, 100.0, 48.0
    )

    assert end_x == 70.0
    assert end_y == pytest.approx(56.0)


def test_secondary_beam_stub_follows_falling_primary_beam() -> None:
    end_x, end_y = RenderMixin._parallel_beam_endpoint(
        40.0, 50.0, 70.0, 40.0, 48.0, 100.0, 60.0
    )

    assert end_x == 70.0
    assert end_y == pytest.approx(56.0)


def test_secondary_beam_stub_remains_horizontal_for_vertical_group() -> None:
    assert RenderMixin._parallel_beam_endpoint(
        40.0, 50.0, 70.0, 40.0, 48.0, 40.0, 60.0
    ) == (70.0, 50.0)


def test_generation_note_maps_to_sharp_key_signature_accidental() -> None:
    assert RenderMixin._key_signature_index_for_midi(66, 3, False) == 0
    assert RenderMixin._key_signature_index_for_midi(68, 3, False) == 2
    assert RenderMixin._key_signature_index_for_midi(70, 3, False) == -1


def test_generation_note_maps_to_flat_key_signature_accidental() -> None:
    assert RenderMixin._key_signature_index_for_midi(70, 3, True) == 0
    assert RenderMixin._key_signature_index_for_midi(68, 3, True) == 2
    assert RenderMixin._key_signature_index_for_midi(66, 2, True) == -1
