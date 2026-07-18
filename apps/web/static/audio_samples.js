(function initAudioSamples(global) {
  "use strict";

  const PIANO_SAMPLE_URLS = Object.freeze({
    48: "/static/samples/grand_piano/C3.mp3",
    52: "/static/samples/grand_piano/E3.mp3",
    55: "/static/samples/grand_piano/G3.mp3",
    60: "/static/samples/grand_piano/C4.mp3",
    64: "/static/samples/grand_piano/E4.mp3",
    67: "/static/samples/grand_piano/G4.mp3",
    72: "/static/samples/grand_piano/C5.mp3",
  });

  const GUITAR_SAMPLE_URLS = Object.freeze({
    40: "/static/samples/guitar_nylon/E2.mp3",
    45: "/static/samples/guitar_nylon/A2.mp3",
    50: "/static/samples/guitar_nylon/D3.mp3",
    52: "/static/samples/guitar_nylon/E3.mp3",
    55: "/static/samples/guitar_nylon/G3.mp3",
    59: "/static/samples/guitar_nylon/B3.mp3",
    64: "/static/samples/guitar_nylon/E4.mp3",
  });

  const METRONOME_SAMPLE_URL = "/static/metronome.mp3";

  function allAudioSampleUrls() {
    return Array.from(new Set([
      METRONOME_SAMPLE_URL,
      ...Object.values(PIANO_SAMPLE_URLS),
      ...Object.values(GUITAR_SAMPLE_URLS),
    ]));
  }

  function nearestSampleRoot(note, sampleMap) {
    const midi = Number(note);
    const roots = Object.keys(sampleMap || {})
      .map((key) => Number(key))
      .filter((root) => Number.isFinite(root));
    if (!roots.length || !Number.isFinite(midi)) return null;
    return roots.reduce((best, current) => (
      best == null || Math.abs(current - midi) < Math.abs(best - midi) ? current : best
    ), null);
  }

  function samplePlaybackRate(note, sampleRoot) {
    const midi = Number(note);
    const root = Number(sampleRoot);
    if (!Number.isFinite(midi) || !Number.isFinite(root)) return 1;
    return 2 ** ((midi - root) / 12);
  }

  function normalizeAudioBuffer(ctx, buffer, { targetPeak = 0.98, extraGain = 1.0 } = {}) {
    if (!buffer) return buffer;
    const channels = buffer.numberOfChannels || 1;
    const length = buffer.length || 0;
    if (!length) return buffer;
    let peak = 0;
    for (let channel = 0; channel < channels; channel += 1) {
      const data = buffer.getChannelData(channel);
      for (let index = 0; index < data.length; index += 1) {
        peak = Math.max(peak, Math.abs(data[index]));
      }
    }
    const safePeak = Math.max(1e-6, peak);
    const gain = Math.max(0, (targetPeak / safePeak) * Math.max(0, Number(extraGain) || 1));
    const out = ctx.createBuffer(channels, length, buffer.sampleRate);
    for (let channel = 0; channel < channels; channel += 1) {
      const src = buffer.getChannelData(channel);
      const dst = out.getChannelData(channel);
      for (let index = 0; index < src.length; index += 1) {
        dst[index] = Math.max(-1, Math.min(1, src[index] * gain));
      }
    }
    return out;
  }

  global.MidiChordsAudioSamples = Object.freeze({
    PIANO_SAMPLE_URLS,
    GUITAR_SAMPLE_URLS,
    METRONOME_SAMPLE_URL,
    allAudioSampleUrls,
    nearestSampleRoot,
    samplePlaybackRate,
    normalizeAudioBuffer,
  });
})(globalThis);
