import math

import numpy as np

from midichords.core.audio_engine import PianoAudioEngine


def _synth_engine(monkeypatch) -> PianoAudioEngine:
    monkeypatch.setattr(PianoAudioEngine, "_load_default_metronome_sample", lambda _self: None)
    monkeypatch.setattr(PianoAudioEngine, "_load_sample_bank", lambda _self, *_args, **_kwargs: {})
    engine = PianoAudioEngine()
    engine.ensure_started = lambda: None
    return engine


def _render(engine: PianoAudioEngine, blocks: int = 24) -> np.ndarray:
    chunks = []
    for _ in range(blocks):
        output = np.zeros((1024, 2), dtype=np.float32)
        engine._audio_callback(output, 1024, None, None)
        assert np.array_equal(output[:, 0], output[:, 1])
        chunks.append(output[:, 0].copy())
    return np.concatenate(chunks)


def test_default_piano_level_is_audible_with_safe_chord_headroom(monkeypatch) -> None:
    note_engine = _synth_engine(monkeypatch)
    assert note_engine.note_on(60, 100)
    note_signal = _render(note_engine)
    note_rms = float(np.sqrt(np.mean(note_signal * note_signal)))
    note_dbfs = 20.0 * math.log10(note_rms)

    chord_engine = _synth_engine(monkeypatch)
    for note in (60, 64, 67, 71):
        assert chord_engine.note_on(note, 78)
    chord_signal = _render(chord_engine)

    assert -22.0 <= note_dbfs <= -17.0
    assert float(np.max(np.abs(chord_signal))) < 0.75
