const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/audio_sample_loader.js");

const { createAudioSampleLoader } = globalThis.MidiChordsAudioSampleLoader;

function responseFor(bytes, ok = true, status = 200) {
  return {
    ok,
    status,
    arrayBuffer: async () => Uint8Array.from(bytes).buffer,
  };
}

test("loader fetches each sample once and shares concurrent preload work", async () => {
  const fetched = [];
  const decoded = [];
  const ctx = {
    decodeAudioData: async (bytes) => {
      const value = new Uint8Array(bytes)[0];
      decoded.push(value);
      return { value };
    },
  };
  const loader = createAudioSampleLoader({
    getContext: () => ctx,
    sampleUrls: ["piano", "guitar"],
    metronomeUrl: "metronome",
    normalizeBuffer: (_ctx, buffer) => buffer,
    fetchImpl: async (url) => {
      fetched.push(url);
      return responseFor([url === "piano" ? 1 : 2]);
    },
  });

  const first = loader.preload();
  const second = loader.preload();
  assert.equal(first, second);
  await first;

  assert.deepEqual(fetched, ["piano", "guitar"]);
  assert.deepEqual(decoded, [1, 2]);
  assert.deepEqual(loader.get("piano"), { value: 1 });
  assert.equal(loader.get("missing"), null);
  await loader.preload();
  assert.equal(fetched.length, 2);
});

test("loader normalizes only the metronome sample", async () => {
  const calls = [];
  const ctx = { decodeAudioData: async (bytes) => ({ byte: new Uint8Array(bytes)[0] }) };
  const loader = createAudioSampleLoader({
    getContext: () => ctx,
    sampleUrls: ["metronome", "piano"],
    metronomeUrl: "metronome",
    normalizeBuffer: (receivedCtx, buffer, options) => {
      calls.push({ receivedCtx, buffer, options });
      return { normalized: buffer.byte };
    },
    fetchImpl: async (url) => responseFor([url === "metronome" ? 8 : 4]),
  });

  await loader.preload();

  assert.deepEqual(loader.get("metronome"), { normalized: 8 });
  assert.deepEqual(loader.get("piano"), { byte: 4 });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].receivedCtx, ctx);
  assert.deepEqual(calls[0].options, { targetPeak: 0.98, extraGain: 1.8 });
});

test("loader keeps successful samples when another download fails", async () => {
  const warnings = [];
  const loader = createAudioSampleLoader({
    getContext: () => ({ decodeAudioData: async () => ({ decoded: true }) }),
    sampleUrls: ["good", "bad"],
    metronomeUrl: "metronome",
    normalizeBuffer: (_ctx, buffer) => buffer,
    fetchImpl: async (url) => (url === "bad" ? responseFor([], false, 503) : responseFor([1])),
    warn: (...args) => warnings.push(args),
  });

  await loader.preload();

  assert.deepEqual(loader.get("good"), { decoded: true });
  assert.equal(loader.get("bad"), null);
  assert.equal(warnings.length, 1);
  assert.match(warnings[0][2].message, /bad \(503\)/);
});
