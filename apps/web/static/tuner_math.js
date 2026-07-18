(function initTunerMath(global) {
  "use strict";

  function autoCorrelate(buffer, sampleRate) {
    if (!buffer || !Number.isFinite(Number(sampleRate)) || Number(sampleRate) <= 0) return null;
    let bestOffset = -1;
    let bestCorrelation = 0;
    const size = buffer.length;
    for (let offset = 8; offset < Math.min(1200, size); offset += 1) {
      let correlation = 0;
      for (let index = 0; index < size - offset; index += 1) {
        correlation += buffer[index] * buffer[index + offset];
      }
      correlation /= (size - offset);
      if (correlation > bestCorrelation) {
        bestCorrelation = correlation;
        bestOffset = offset;
      }
    }
    if (bestOffset === -1 || bestCorrelation < 0.01) return null;
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
