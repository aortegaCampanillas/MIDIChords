(function initAudioVoice(global) {
  "use strict";

  function instrumentSampleEnvelope(startTime, durationSeconds = 0.46, instrument = "piano") {
    const start = Number(startTime);
    const safeStart = Number.isFinite(start) ? start : 0;
    const baseDuration = Math.max(0.16, Number(durationSeconds) || 0.46);
    const guitar = instrument === "guitar";
    const sustainEnd = safeStart + (baseDuration * (guitar ? 1.9 : 1.7));
    return Object.freeze({
      start: safeStart,
      attackEnd: safeStart + 0.01,
      attackPeak: guitar ? 0.96 : 0.88,
      sustainEnd,
      releaseEnd: sustainEnd + (guitar ? 0.62 : 0.48),
      sourceStop: sustainEnd + 0.75,
    });
  }

  function heldVoiceReleaseTiming(instrument = "piano", overrides = {}) {
    const guitar = instrument === "guitar";
    return Object.freeze({
      releaseSeconds: overrides.releaseSeconds ?? (guitar ? 0.52 : 0.40),
      sourceTail: overrides.sourceTail ?? (guitar ? 0.60 : 0.48),
      noiseTail: overrides.noiseTail ?? (guitar ? 0.14 : 0.10),
    });
  }

  function releaseAudioVoice(voice, atTime, timing = heldVoiceReleaseTiming(voice?.instrument)) {
    const start = Number(atTime);
    if (!voice || !Number.isFinite(start)) return false;
    try {
      if (voice.gain?.gain) {
        const param = voice.gain.gain;
        param.cancelScheduledValues(start);
        param.setValueAtTime(Math.max(0.0001, param.value || 0.001), start);
        param.exponentialRampToValueAtTime(0.0001, start + timing.releaseSeconds);
      }
      (voice.oscs || []).forEach((source) => {
        try { source.stop(start + timing.sourceTail); } catch (_error) {}
      });
      if (voice.noise) {
        try { voice.noise.stop(start + timing.noiseTail); } catch (_error) {}
      }
      return true;
    } catch (_error) {
      return false;
    }
  }

  global.MidiChordsAudioVoice = Object.freeze({
    instrumentSampleEnvelope,
    heldVoiceReleaseTiming,
    releaseAudioVoice,
  });
})(globalThis);
