const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/tuner_math.js");

const { autoCorrelate, freqToMidi, midiToFreq } = globalThis.MidiChordsTunerMath;

test("frequency and MIDI conversion preserve concert pitch and octaves", () => {
  assert.equal(freqToMidi(440), 69);
  assert.equal(midiToFreq(69), 440);
  assert.equal(midiToFreq(81), 880);
  assert.ok(Math.abs(freqToMidi(261.625565) - 60) < 1e-6);

  for (const midi of [21, 40, 60, 69, 108]) {
    assert.ok(Math.abs(freqToMidi(midiToFreq(midi)) - midi) < 1e-10);
  }
});

test("autocorrelation detects a decaying synthetic instrument signal", () => {
  const sampleRate = 48000;
  const frequency = 480;
  const signal = Float32Array.from({ length: 4096 }, (_, index) => (
    Math.sin((2 * Math.PI * frequency * index) / sampleRate) * Math.exp(-index / 1200)
  ));

  const detected = autoCorrelate(signal, sampleRate);
  assert.ok(Math.abs(detected - frequency) < 0.01);
});

test("autocorrelation rejects silence and invalid inputs", () => {
  assert.equal(autoCorrelate(new Float32Array(2048), 48000), null);
  assert.equal(autoCorrelate(null, 48000), null);
  assert.equal(autoCorrelate(new Float32Array(32), 0), null);
});
