const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/audio_voice.js");

const {
  instrumentSampleEnvelope,
  heldVoiceReleaseTiming,
  releaseAudioVoice,
} = globalThis.MidiChordsAudioVoice;

test("sample envelopes preserve piano and guitar timing", () => {
  const piano = instrumentSampleEnvelope(10, 1, "piano");
  const guitar = instrumentSampleEnvelope(10, 1, "guitar");

  assert.deepEqual(piano, {
    start: 10,
    attackEnd: 10.01,
    attackPeak: 0.88,
    sustainEnd: 11.7,
    releaseEnd: 12.18,
    sourceStop: 12.45,
  });
  assert.deepEqual(guitar, {
    start: 10,
    attackEnd: 10.01,
    attackPeak: 0.96,
    sustainEnd: 11.9,
    releaseEnd: 12.52,
    sourceStop: 12.65,
  });
  assert.equal(instrumentSampleEnvelope(0, 0.01).sustainEnd, 0.272);
});

test("held voice release timing supports instrument defaults and explicit overrides", () => {
  assert.deepEqual(heldVoiceReleaseTiming("piano"), {
    releaseSeconds: 0.4,
    sourceTail: 0.48,
    noiseTail: 0.1,
  });
  assert.deepEqual(heldVoiceReleaseTiming("guitar"), {
    releaseSeconds: 0.52,
    sourceTail: 0.6,
    noiseTail: 0.14,
  });
  assert.deepEqual(heldVoiceReleaseTiming("piano", { releaseSeconds: 0.09 }), {
    releaseSeconds: 0.09,
    sourceTail: 0.48,
    noiseTail: 0.1,
  });
});

test("release schedules gain, sample sources, and noise at the requested time", () => {
  const events = [];
  const param = {
    value: 0.5,
    cancelScheduledValues: (time) => events.push(["cancel", time]),
    setValueAtTime: (value, time) => events.push(["set", value, time]),
    exponentialRampToValueAtTime: (value, time) => events.push(["ramp", value, time]),
  };
  const voice = {
    gain: { gain: param },
    oscs: [{ stop: (time) => events.push(["source", time]) }],
    noise: { stop: (time) => events.push(["noise", time]) },
    instrument: "guitar",
  };

  assert.equal(releaseAudioVoice(voice, 4), true);
  assert.deepEqual(events, [
    ["cancel", 4],
    ["set", 0.5, 4],
    ["ramp", 0.0001, 4.52],
    ["source", 4.6],
    ["noise", 4.14],
  ]);
});

test("release tolerates already stopped sources and rejects invalid input", () => {
  const voice = {
    oscs: [{ stop: () => { throw new Error("already stopped"); } }],
    noise: { stop: () => { throw new Error("already stopped"); } },
  };

  assert.equal(releaseAudioVoice(voice, 2), true);
  assert.equal(releaseAudioVoice(null, 2), false);
  assert.equal(releaseAudioVoice(voice, Number.NaN), false);
});
