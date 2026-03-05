const NOTE_NAMES = {
  en: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
  es: ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
};

const FLAT_ALIASES = {
  en: { 1: "Db", 3: "Eb", 6: "Gb", 8: "Ab", 10: "Bb" },
  es: { 1: "Reb", 3: "Mib", 6: "Solb", 8: "Lab", 10: "Sib" },
};

const CHORD_PATTERNS = [
  { suffix: "", intervals: [0, 4, 7] },
  { suffix: "5", intervals: [0, 7] },
  { suffix: "-5", intervals: [0, 4, 6] },
  { suffix: "m", intervals: [0, 3, 7] },
  { suffix: "dim", intervals: [0, 3, 6] },
  { suffix: "aug", intervals: [0, 4, 8] },
  { suffix: "sus2", intervals: [0, 2, 7] },
  { suffix: "sus4", intervals: [0, 5, 7] },
  { suffix: "sus2sus4", intervals: [0, 2, 5, 7] },
  { suffix: "add9", intervals: [0, 4, 7, 14] },
  { suffix: "madd9", intervals: [0, 3, 7, 14] },
  { suffix: "6", intervals: [0, 4, 7, 9] },
  { suffix: "6add9", intervals: [0, 4, 7, 9, 14] },
  { suffix: "m6", intervals: [0, 3, 7, 9] },
  { suffix: "m6add9", intervals: [0, 3, 7, 9, 14] },
  { suffix: "7", intervals: [0, 4, 7, 10] },
  { suffix: "7sus4", intervals: [0, 5, 7, 10] },
  { suffix: "7#5", intervals: [0, 4, 8, 10] },
  { suffix: "7b5", intervals: [0, 4, 6, 10] },
  { suffix: "7#9", intervals: [0, 4, 7, 10, 15] },
  { suffix: "7b9", intervals: [0, 4, 7, 10, 13] },
  { suffix: "9", intervals: [0, 4, 7, 10, 14] },
  { suffix: "11", intervals: [0, 4, 7, 10, 14, 17] },
  { suffix: "13", intervals: [0, 4, 7, 10, 14, 21] },
  { suffix: "maj7", intervals: [0, 4, 7, 11] },
  { suffix: "maj9", intervals: [0, 4, 7, 11, 14] },
  { suffix: "maj11", intervals: [0, 4, 7, 11, 14, 17] },
  { suffix: "maj13", intervals: [0, 4, 7, 11, 14, 21] },
  { suffix: "m7", intervals: [0, 3, 7, 10] },
  { suffix: "m9", intervals: [0, 3, 7, 10, 14] },
  { suffix: "m11", intervals: [0, 3, 7, 10, 14, 17] },
  { suffix: "m13", intervals: [0, 3, 7, 10, 14, 21] },
  { suffix: "mMaj7", intervals: [0, 3, 7, 11] },
  { suffix: "dim7", intervals: [0, 3, 6, 9] },
  { suffix: "m7b5", intervals: [0, 3, 6, 10] },
];

const COMMON_CHORD_SUFFIX_ORDER = [
  "", "m", "7", "maj7", "m7", "sus4", "sus2", "dim", "aug", "5", "6", "m6",
  "add9", "madd9", "9", "maj9", "m9", "11", "m11", "13", "m13", "dim7", "m7b5",
];

const SCALE_PATTERNS = [
  { name: "Ionian", intervals: [0, 2, 4, 5, 7, 9, 11, 12] },
  { name: "Dorian", intervals: [0, 2, 3, 5, 7, 9, 10, 12] },
  { name: "Phrygian", intervals: [0, 1, 3, 5, 7, 8, 10, 12] },
  { name: "Lydian", intervals: [0, 2, 4, 6, 7, 9, 11, 12] },
  { name: "Mixolydian", intervals: [0, 2, 4, 5, 7, 9, 10, 12] },
  { name: "Aeolian", intervals: [0, 2, 3, 5, 7, 8, 10, 12] },
  { name: "Locrian", intervals: [0, 1, 3, 5, 6, 8, 10, 12] },
  { name: "Chromatic", intervals: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] },
  { name: "Harmonic Minor", intervals: [0, 2, 3, 5, 7, 8, 11, 12] },
  { name: "Melodic Minor", intervals: [0, 2, 3, 5, 7, 9, 11, 12] },
  { name: "Major Pentatonic", intervals: [0, 2, 4, 7, 9, 12] },
  { name: "Minor Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Blues Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Neutral Pentatonic", intervals: [0, 2, 5, 7, 10, 12] },
  { name: "Bebop", intervals: [0, 2, 4, 5, 7, 9, 10, 11, 12] },
  { name: "Whole Tone (WT)", intervals: [0, 2, 4, 6, 8, 10, 12] },
  { name: "Minor Blues", intervals: [0, 3, 5, 6, 7, 10, 12] },
  { name: "Super Locrian", intervals: [0, 1, 3, 4, 6, 8, 10, 12] },
  { name: "Spanish Gypsy", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
  { name: "Flamenco", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
];

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
    },
  });
}

function noteName(midiNote, language = "es", preferFlat = false, withOctave = true) {
  const names = NOTE_NAMES[language] || NOTE_NAMES.en;
  const pc = ((Number(midiNote) % 12) + 12) % 12;
  const sharpName = names[pc];
  const flatName = (FLAT_ALIASES[language] || FLAT_ALIASES.en)[pc];
  const name = preferFlat && flatName ? flatName : sharpName;
  if (!withOctave) return name;
  const octave = Math.floor(Number(midiNote) / 12) - 1;
  return `${name}${octave}`;
}

function voicedIntervalsForInversion(intervals, inversion) {
  if (!intervals.length) return [];
  const idx = Math.max(0, Math.min(Number(inversion) || 0, intervals.length - 1));
  const rotated = intervals.map((_, i) => Number(intervals[(idx + i) % intervals.length]));
  const voiced = [];
  for (const raw of rotated) {
    let value = raw;
    if (voiced.length) while (value <= voiced[voiced.length - 1]) value += 12;
    voiced.push(value);
  }
  return voiced;
}

function analyzeChordNotes(notesSet) {
  if (!notesSet.size) return { root: null, pattern: null, bassPc: null };
  const pcs = new Set(Array.from(notesSet, (n) => Number(n) % 12));
  let bestScore = -999;
  let bestComplexity = -999;
  let bestRoot = null;
  let bestPattern = null;
  for (let root = 0; root < 12; root += 1) {
    for (const pattern of CHORD_PATTERNS) {
      const template = new Set(pattern.intervals.map((i) => (root + i) % 12));
      const extra = Array.from(pcs).filter((pc) => !template.has(pc)).length;
      const missing = Array.from(template).filter((pc) => !pcs.has(pc)).length;
      let score = -999;
      if (extra === 0 && missing === 0) score = 100;
      else if (missing === 0) score = 70 - extra;
      else if (extra === 0) score = 40 - missing;
      else continue;
      const complexity = -pattern.intervals.length;
      if (score > bestScore || (score === bestScore && complexity > bestComplexity)) {
        bestScore = score;
        bestComplexity = complexity;
        bestRoot = root;
        bestPattern = pattern;
      }
    }
  }
  const bassPc = Math.min(...Array.from(notesSet)) % 12;
  return { root: bestRoot, pattern: bestPattern, bassPc };
}

function listChordPatterns() {
  const priority = new Map(COMMON_CHORD_SUFFIX_ORDER.map((s, i) => [s, i]));
  return [...CHORD_PATTERNS]
    .sort((a, b) => {
      const pa = priority.has(a.suffix) ? priority.get(a.suffix) : 999;
      const pb = priority.has(b.suffix) ? priority.get(b.suffix) : 999;
      if (pa !== pb) return pa - pb;
      if (a.intervals.length !== b.intervals.length) return a.intervals.length - b.intervals.length;
      return a.suffix.localeCompare(b.suffix);
    })
    .map((p) => ({ suffix: p.suffix, intervals: [...p.intervals] }));
}

function listScalePatterns() {
  return SCALE_PATTERNS.map((p) => ({ name: p.name, localized_name: p.name, intervals: [...p.intervals] }));
}

function generateChord({ rootPc = 0, suffix = "", inversion = 0, language = "es", preferFlat = false }) {
  const selected = CHORD_PATTERNS.find((p) => p.suffix === suffix) || CHORD_PATTERNS[0];
  const safeInversion = Math.max(0, Math.min(Number(inversion) || 0, selected.intervals.length - 1));
  const rootMidi = 60 + (Number(rootPc) % 12);
  const voicedIntervals = voicedIntervalsForInversion(selected.intervals, safeInversion);
  const notesMidi = voicedIntervals.map((v) => rootMidi + v);
  const notesNoOct = notesMidi.map((n) => noteName(n, language, preferFlat, false));
  const notes = notesMidi.map((n) => noteName(n, language, preferFlat, true));
  const rootName = noteName(Number(rootPc) % 12, language, preferFlat, false);
  let chordName = `${rootName}${selected.suffix}`;
  if (safeInversion > 0 && notesNoOct.length) chordName = `${chordName}/${notesNoOct[0]}`;
  return {
    root_pc: Number(rootPc) % 12,
    suffix: selected.suffix,
    inversion: safeInversion,
    name: chordName,
    notes_midi: notesMidi,
    notes,
    notes_no_octave: notesNoOct,
    intervals: voicedIntervals,
  };
}

function detectChord({ notes = [], language = "es", preferFlat = false }) {
  const midiNotes = [...new Set((Array.isArray(notes) ? notes : []).map((n) => Number(n)).filter((n) => Number.isFinite(n)))].sort((a, b) => a - b);
  if (!midiNotes.length) return { name: "-", extras_midi: [], notes_midi: [], notes: [], extras: [] };
  const pcs = new Set(midiNotes.map((n) => n % 12));
  if (pcs.size === 1) {
    return {
      name: noteName(midiNotes[0], language, preferFlat, false),
      notes_midi: midiNotes,
      notes: midiNotes.map((n) => noteName(n, language, preferFlat, true)),
      extras_midi: [],
      extras: [],
    };
  }
  const { root, pattern, bassPc } = analyzeChordNotes(new Set(midiNotes));
  if (root == null || !pattern) {
    return {
      name: midiNotes.map((n) => noteName(n, language, preferFlat, false)).join(" + "),
      notes_midi: midiNotes,
      notes: midiNotes.map((n) => noteName(n, language, preferFlat, true)),
      extras_midi: [],
      extras: [],
    };
  }
  let chordName = `${noteName(root, language, preferFlat, false)}${pattern.suffix}`;
  if (bassPc != null && bassPc !== root) chordName = `${chordName}/${noteName(bassPc, language, preferFlat, false)}`;
  const expectedPcs = new Set(pattern.intervals.map((i) => (root + i) % 12));
  const extrasMidi = midiNotes.filter((n) => !expectedPcs.has(n % 12));
  return {
    name: chordName,
    notes_midi: midiNotes,
    notes: midiNotes.map((n) => noteName(n, language, preferFlat, true)),
    extras_midi: extrasMidi,
    extras: extrasMidi.map((n) => noteName(n, language, preferFlat, true)),
    root_pc: root,
    suffix: pattern.suffix,
  };
}

function generateScale({ tonicPc = 0, patternName = "Ionian", language = "es", preferFlat = false }) {
  const pattern = SCALE_PATTERNS.find((p) => p.name === patternName) || SCALE_PATTERNS[0];
  const rootMidi = 60 + (Number(tonicPc) % 12);
  const notesMidi = pattern.intervals.map((i) => rootMidi + Number(i));
  return {
    tonic_pc: Number(tonicPc) % 12,
    pattern_name: pattern.name,
    pattern_localized_name: pattern.name,
    notes_midi: notesMidi,
    notes: notesMidi.map((n) => noteName(n, language, preferFlat, true)),
    intervals: [...pattern.intervals],
  };
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return {};
  }
}

function normalizeLanguage(language) {
  return String(language || "es").toLowerCase() === "en" ? "en" : "es";
}

function normalizePreferFlat(accidental) {
  return String(accidental || "sharp").toLowerCase() === "flat";
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname } = url;
    if (request.method === "OPTIONS" && pathname.startsWith("/api/")) {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET,POST,OPTIONS",
          "access-control-allow-headers": "content-type",
        },
      });
    }

    if (pathname === "/api/health" && request.method === "GET") return json({ status: "ok" });
    if (pathname === "/api/meta" && request.method === "GET") {
      return json({
        chord_patterns: listChordPatterns(),
        scale_patterns: listScalePatterns(normalizeLanguage(url.searchParams.get("language"))),
      });
    }
    if (pathname === "/api/detect" && request.method === "POST") {
      const body = await readJson(request);
      return json(
        detectChord({
          notes: Array.isArray(body.notes) ? body.notes : [],
          language: normalizeLanguage(body.language),
          preferFlat: normalizePreferFlat(body.accidental),
        }),
      );
    }
    if (pathname === "/api/generate/chord" && request.method === "POST") {
      const body = await readJson(request);
      return json(
        generateChord({
          rootPc: Number(body.root_pc) || 0,
          suffix: String(body.suffix || ""),
          inversion: Number(body.inversion) || 0,
          language: normalizeLanguage(body.language),
          preferFlat: normalizePreferFlat(body.accidental),
        }),
      );
    }
    if (pathname === "/api/generate/scale" && request.method === "POST") {
      const body = await readJson(request);
      return json(
        generateScale({
          tonicPc: Number(body.tonic_pc) || 0,
          patternName: String(body.pattern_name || "Ionian"),
          language: normalizeLanguage(body.language),
          preferFlat: normalizePreferFlat(body.accidental),
        }),
      );
    }
    if (pathname === "/api/generate/guitar-variations" && request.method === "POST") return json({ variations: [] });
    if (pathname.startsWith("/api/")) return json({ error: "Not found" }, 404);

    return env.ASSETS.fetch(request);
  },
};

