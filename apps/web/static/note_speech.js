(function initNoteSpeech(global) {
  "use strict";

  // Third-party files live under /vendor (immutable cache); see vendor/vosk/NOTICE.md.
  const VOSK_LIBRARY_URL = "/vendor/vosk/vosk-browser-0.0.8.js";
  // Cloudflare Pages caps files at 25 MiB, so each model ships in two parts.
  const VOSK_MODELS = Object.freeze({
    es: Object.freeze([
      Object.freeze({ url: "/vendor/vosk/vosk-model-small-es-0.42.tar.gz.part0", bytes: 20000000 }),
      Object.freeze({ url: "/vendor/vosk/vosk-model-small-es-0.42.tar.gz.part1", bytes: 19817465 }),
    ]),
    en: Object.freeze([
      Object.freeze({ url: "/vendor/vosk/vosk-model-small-en-us-0.15.tar.gz.part0", bytes: 21000000 }),
      Object.freeze({ url: "/vendor/vosk/vosk-model-small-en-us-0.15.tar.gz.part1", bytes: 20185099 }),
    ]),
  });

  let libraryPromise = null;
  // One loaded model per language, kept for the page's lifetime.
  const modelPromises = new Map();

  function loadLibrary() {
    if (global.Vosk) return Promise.resolve(global.Vosk);
    if (!libraryPromise) {
      libraryPromise = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = VOSK_LIBRARY_URL;
        script.async = true;
        script.onload = () => (global.Vosk ? resolve(global.Vosk) : reject(new Error("Vosk unavailable")));
        script.onerror = () => {
          libraryPromise = null;
          reject(new Error("Vosk library failed to load"));
        };
        document.head.appendChild(script);
      });
    }
    return libraryPromise;
  }

  async function downloadModel(parts, onProgress) {
    const total = parts.reduce((sum, part) => sum + part.bytes, 0);
    let loaded = 0;
    const blobs = [];
    for (const part of parts) {
      const response = await fetch(part.url);
      if (!response.ok || !response.body) throw new Error(`Model download failed (${response.status})`);
      const reader = response.body.getReader();
      const chunks = [];
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        loaded += value.byteLength;
        onProgress(Math.min(1, loaded / total));
      }
      blobs.push(new Blob(chunks));
    }
    return new Blob(blobs, { type: "application/gzip" });
  }

  function loadModel(language, onStatus) {
    const parts = VOSK_MODELS[language] || VOSK_MODELS.es;
    if (!modelPromises.has(parts)) {
      modelPromises.set(parts, (async () => {
        const Vosk = await loadLibrary();
        onStatus({ phase: "downloading", progress: 0 });
        const archive = await downloadModel(parts, (progress) => onStatus({ phase: "downloading", progress }));
        onStatus({ phase: "loading" });
        const url = URL.createObjectURL(archive);
        try {
          return await Vosk.createModel(url, -1);
        } finally {
          URL.revokeObjectURL(url);
        }
      })().catch((error) => {
        modelPromises.delete(parts);
        throw error;
      }));
    }
    return modelPromises.get(parts);
  }

  // start({ language, vocabulary }): vocabulary lists the words the recognizer
  // may output ("[unk]" absorbs anything else). onText(kind, text) receives
  // "partial" and "final" results.
  function createNoteSpeechRecognizer({ onText, onStatus = () => {} }) {
    let session = null;
    // Lightweight counters to tell "no audio" apart from "no words" when debugging.
    const diagnostics = { audioFrames: 0, peakLevel: 0, device: null, lastText: null, lastError: null };
    // Bumped by stop() so a start() still loading the model or waiting for the
    // microphone permission does not open the mic after being cancelled.
    let startToken = 0;

    async function start({ language = "es", vocabulary }) {
      if (session) return;
      if (!global.navigator?.mediaDevices?.getUserMedia) throw new Error("Microphone not supported");
      const token = ++startToken;
      Object.assign(diagnostics, { audioFrames: 0, peakLevel: 0, device: null, lastText: null, lastError: null });
      const model = await loadModel(language, onStatus);
      if (token !== startToken) return;
      onStatus({ phase: "microphone" });
      const stream = await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 },
      });
      if (token !== startToken) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      const AudioCtx = global.AudioContext || global.webkitAudioContext;
      const ctx = new AudioCtx();
      const recognizer = new model.KaldiRecognizer(ctx.sampleRate, JSON.stringify([...vocabulary, "[unk]"]));
      recognizer.on("partialresult", (message) => {
        if (message.result.partial) diagnostics.lastText = message.result.partial;
        onText("partial", message.result.partial);
      });
      recognizer.on("result", (message) => {
        if (message.result.text) diagnostics.lastText = message.result.text;
        onText("final", message.result.text);
      });
      recognizer.on("error", (message) => {
        diagnostics.lastError = String(message?.error || message);
      });

      const source = ctx.createMediaStreamSource(stream);
      // ScriptProcessor is deprecated but is what vosk-browser consumes
      // (AudioBuffer input); its output is muted, it only feeds the recognizer.
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (event) => {
        diagnostics.audioFrames += 1;
        // Read before acceptWaveform, which may transfer the buffer to the worker.
        const samples = event.inputBuffer.getChannelData(0);
        let peak = 0;
        for (let i = 0; i < samples.length; i += 1) peak = Math.max(peak, Math.abs(samples[i]));
        diagnostics.peakLevel = Math.max(diagnostics.peakLevel, Number(peak.toFixed(4)));
        try {
          recognizer.acceptWaveform(event.inputBuffer);
        } catch (error) {
          diagnostics.lastError = String(error?.message || error);
        }
      };
      const mute = ctx.createGain();
      mute.gain.value = 0;
      source.connect(processor);
      processor.connect(mute);
      mute.connect(ctx.destination);
      diagnostics.device = stream.getAudioTracks()[0]?.label || null;
      session = { stream, ctx, recognizer, source, processor, mute, language };
      onStatus({ phase: "listening" });
    }

    function stop() {
      startToken += 1;
      if (!session) return;
      const { stream, ctx, recognizer, source, processor, mute } = session;
      session = null;
      processor.onaudioprocess = null;
      try { source.disconnect(); processor.disconnect(); mute.disconnect(); } catch (_error) {}
      stream.getTracks().forEach((track) => track.stop());
      try { recognizer.remove(); } catch (_error) {}
      void ctx.close().catch(() => {});
      onStatus({ phase: "idle" });
    }

    return Object.freeze({
      start,
      stop,
      get listening() { return !!session; },
      get language() { return session ? session.language : null; },
      get diagnostics() {
        return { ...diagnostics, audioState: session ? session.ctx.state : null };
      },
    });
  }

  global.MidiChordsNoteSpeech = Object.freeze({
    VOSK_LIBRARY_URL,
    VOSK_MODELS,
    createNoteSpeechRecognizer,
  });
})(globalThis);
