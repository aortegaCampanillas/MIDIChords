(function initAudioSampleLoader(global) {
  "use strict";

  function createAudioSampleLoader({
    getContext,
    sampleUrls,
    metronomeUrl,
    normalizeBuffer,
    fetchImpl = global.fetch,
    warn = (...args) => console.warn(...args),
  }) {
    let cache = Object.create(null);
    let loadPromise = null;

    async function decode(ctx, url) {
      const response = await fetchImpl(url);
      if (!response.ok) throw new Error(`sample fetch failed: ${url} (${response.status})`);
      const bytes = await response.arrayBuffer();
      return ctx.decodeAudioData(bytes.slice(0));
    }

    function preload() {
      if (loadPromise) return loadPromise;
      loadPromise = (async () => {
        const ctx = getContext();
        const loaded = Object.create(null);
        await Promise.all(sampleUrls.map(async (url) => {
          try {
            const decoded = await decode(ctx, url);
            loaded[url] = url === metronomeUrl
              ? normalizeBuffer(ctx, decoded, { targetPeak: 0.98, extraGain: 1.8 })
              : decoded;
          } catch (error) {
            warn("Sample load failed:", url, error);
          }
        }));
        cache = loaded;
        return cache;
      })();
      return loadPromise;
    }

    function get(url) {
      return cache[url] || null;
    }

    return Object.freeze({ preload, get });
  }

  global.MidiChordsAudioSampleLoader = Object.freeze({ createAudioSampleLoader });
})(globalThis);
