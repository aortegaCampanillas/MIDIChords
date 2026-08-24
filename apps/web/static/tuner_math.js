(function initTunerMath(global) {
  "use strict";

  function autoCorrelate(buffer, sampleRate) {
    if (!buffer || !Number.isFinite(Number(sampleRate)) || Number(sampleRate) <= 0) return null;
    const size = buffer.length;

    let rms = 0;
    for (let i = 0; i < size; i += 1) rms += buffer[i] * buffer[i];
    rms = Math.sqrt(rms / size);
    // Below this level the true tone has decayed enough that background
    // noise/room resonance can dominate the autocorrelation and lock onto a
    // spurious sub-harmonic (e.g. a note appearing to slide to a different
    // pitch as it fades out) — better to stop reporting than report wrong.
    if (rms < 0.01) return null;

    const maxOffset = Math.min(1200, size);
    const correlations = new Array(maxOffset).fill(0);
    let bestOffset = -1;
    let bestCorrelation = 0;
    for (let offset = 8; offset < maxOffset; offset += 1) {
      let correlation = 0;
      for (let index = 0; index < size - offset; index += 1) {
        correlation += buffer[index] * buffer[index + offset];
      }
      correlation /= (size - offset);
      correlations[offset] = correlation;
      if (correlation > bestCorrelation) {
        bestCorrelation = correlation;
        bestOffset = offset;
      }
    }
    if (bestOffset === -1 || bestCorrelation < rms * rms * 0.5) return null;

    // Prefer the smallest local-maximum offset whose correlation is a strong
    // fraction of the global best: pure/periodic tones correlate almost as
    // strongly at integer multiples of the true period (half/quarter
    // frequency), so taking the raw maximum tends to lock onto a sub-harmonic
    // instead of the fundamental. Requiring a local peak (rather than just
    // crossing the threshold) avoids latching onto a decaying envelope's
    // monotonic falloff near the start of the search range.
    const threshold = bestCorrelation * 0.9;
    for (let offset = 9; offset < bestOffset; offset += 1) {
      const isLocalPeak = correlations[offset] >= correlations[offset - 1]
        && correlations[offset] >= correlations[offset + 1];
      if (isLocalPeak && correlations[offset] >= threshold) {
        bestOffset = offset;
        break;
      }
    }

    return Number(sampleRate) / bestOffset;
  }

  function freqToMidi(frequency) {
    return 69 + (12 * Math.log2(Number(frequency) / 440));
  }

  function midiToFreq(midi) {
    return 440 * (2 ** ((Number(midi) - 69) / 12));
  }

  global.MidiChordsTunerMath = Object.freeze({ autoCorrelate, freqToMidi, midiToFreq });
})(globalThis);
