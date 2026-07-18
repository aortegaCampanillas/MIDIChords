const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/audio_samples.js");

const {
  PIANO_SAMPLE_URLS,
  GUITAR_SAMPLE_URLS,
  METRONOME_SAMPLE_URL,
  allAudioSampleUrls,
  nearestSampleRoot,
  samplePlaybackRate,
  normalizeAudioBuffer,
} = globalThis.MidiChordsAudioSamples;

function fakeBuffer(channelValues, sampleRate = 44100) {
  const channels = channelValues.map((values) => Float32Array.from(values));
  return {
    numberOfChannels: channels.length,
    length: channels[0]?.length || 0,
    sampleRate,
    getChannelData: (channel) => channels[channel],
  };
}

const fakeContext = {
  createBuffer(channels, length, sampleRate) {
    return fakeBuffer(Array.from({ length: channels }, () => Array(length).fill(0)), sampleRate);
  },
};

test("audio sample catalog exposes every unique asset", () => {
  const urls = allAudioSampleUrls();
  const expected = new Set([
    METRONOME_SAMPLE_URL,
    ...Object.values(PIANO_SAMPLE_URLS),
    ...Object.values(GUITAR_SAMPLE_URLS),
  ]);

  assert.deepEqual(new Set(urls), expected);
  assert.equal(urls.length, expected.size);
  assert.equal(urls[0], METRONOME_SAMPLE_URL);
});

test("nearest sample root preserves catalog order when distances tie", () => {
  assert.equal(nearestSampleRoot(62, PIANO_SAMPLE_URLS), 60);
  assert.equal(nearestSampleRoot(63, PIANO_SAMPLE_URLS), 64);
  assert.equal(nearestSampleRoot(47, GUITAR_SAMPLE_URLS), 45);
  assert.equal(nearestSampleRoot("invalid", PIANO_SAMPLE_URLS), null);
  assert.equal(nearestSampleRoot(60, {}), null);
});

test("playback rate transposes samples by semitones", () => {
  assert.equal(samplePlaybackRate(60, 60), 1);
  assert.equal(samplePlaybackRate(72, 60), 2);
  assert.equal(samplePlaybackRate(48, 60), 0.5);
  assert.equal(samplePlaybackRate("invalid", 60), 1);
});

test("normalization preserves shape and scales the peak", () => {
  const source = fakeBuffer([[0.25, -0.5], [0.1, -0.2]], 48000);
  const normalized = normalizeAudioBuffer(fakeContext, source, { targetPeak: 0.8 });

  assert.equal(normalized.numberOfChannels, 2);
  assert.equal(normalized.length, 2);
  assert.equal(normalized.sampleRate, 48000);
  assert.ok(Math.abs(normalized.getChannelData(0)[0] - 0.4) < 1e-6);
  assert.ok(Math.abs(normalized.getChannelData(0)[1] + 0.8) < 1e-6);
  assert.ok(Math.abs(normalized.getChannelData(1)[0] - 0.16) < 1e-6);
});

test("normalization clips amplified samples and preserves empty inputs", () => {
  const source = fakeBuffer([[0.5, -0.25]]);
  const normalized = normalizeAudioBuffer(fakeContext, source, { targetPeak: 1, extraGain: 2 });

  assert.deepEqual(Array.from(normalized.getChannelData(0)), [1, -1]);
  assert.equal(normalizeAudioBuffer(fakeContext, null), null);
  const empty = fakeBuffer([[]]);
  assert.equal(normalizeAudioBuffer(fakeContext, empty), empty);
});
