const NOTE_NAMES = {
  en: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
  es: ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
};

const FLAT_ALIASES = {
  es: { 1: "Re♭", 3: "Mi♭", 6: "Sol♭", 8: "La♭", 10: "Si♭" },
  en: { 1: "D♭", 3: "E♭", 6: "G♭", 8: "A♭", 10: "B♭" },
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
  { suffix: "7(#5,#9)", intervals: [0, 4, 8, 10, 15] },
  { suffix: "7(#5,b9)", intervals: [0, 4, 8, 10, 13] },
  { suffix: "7(b5,#9)", intervals: [0, 4, 6, 10, 15] },
  { suffix: "7(b5,b9)", intervals: [0, 4, 6, 10, 13] },
  { suffix: "9", intervals: [0, 4, 7, 10, 14] },
  { suffix: "9#5", intervals: [0, 4, 8, 10, 14] },
  { suffix: "9b5", intervals: [0, 4, 6, 10, 14] },
  { suffix: "11", intervals: [0, 4, 7, 10, 14, 17] },
  { suffix: "11b9", intervals: [0, 4, 7, 10, 13, 17] },
  { suffix: "13", intervals: [0, 4, 7, 10, 14, 21] },
  { suffix: "13b9", intervals: [0, 4, 7, 10, 13, 21] },
  { suffix: "13#11", intervals: [0, 4, 7, 10, 14, 18, 21] },
  { suffix: "maj7", intervals: [0, 4, 7, 11] },
  { suffix: "maj7#5", intervals: [0, 4, 8, 11] },
  { suffix: "maj7b5", intervals: [0, 4, 6, 11] },
  { suffix: "maj9", intervals: [0, 4, 7, 11, 14] },
  { suffix: "maj11", intervals: [0, 4, 7, 11, 14, 17] },
  { suffix: "maj13", intervals: [0, 4, 7, 11, 14, 21] },
  { suffix: "maj9#11", intervals: [0, 4, 7, 11, 14, 18] },
  { suffix: "maj13#11", intervals: [0, 4, 7, 11, 14, 18, 21] },
  { suffix: "m7", intervals: [0, 3, 7, 10] },
  { suffix: "m7#5", intervals: [0, 3, 8, 10] },
  { suffix: "m9", intervals: [0, 3, 7, 10, 14] },
  { suffix: "m11", intervals: [0, 3, 7, 10, 14, 17] },
  { suffix: "m13", intervals: [0, 3, 7, 10, 14, 21] },
  { suffix: "mMaj7", intervals: [0, 3, 7, 11] },
  { suffix: "mMaj9", intervals: [0, 3, 7, 11, 14] },
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
  { name: "Locrian #2", intervals: [0, 2, 3, 5, 6, 8, 10, 12] },
  { name: "Harmonic Minor", intervals: [0, 2, 3, 5, 7, 8, 11, 12] },
  { name: "Melodic Minor", intervals: [0, 2, 3, 5, 7, 9, 11, 12] },
  { name: "Major Pentatonic", intervals: [0, 2, 4, 7, 9, 12] },
  { name: "Minor Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Blues Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Neutral Pentatonic", intervals: [0, 2, 5, 7, 10, 12] },
  { name: "Bebop", intervals: [0, 2, 4, 5, 7, 9, 10, 11, 12] },
  { name: "Bebop Major", intervals: [0, 2, 4, 5, 7, 8, 9, 11, 12] },
  { name: "Bebop Minor", intervals: [0, 2, 3, 4, 5, 7, 9, 10, 12] },
  { name: "Half Diminished", intervals: [0, 2, 3, 5, 6, 8, 10, 12] },
  { name: "Diminished", intervals: [0, 2, 3, 5, 6, 8, 9, 11, 12] },
  { name: "Whole Tone (WT)", intervals: [0, 2, 4, 6, 8, 10, 12] },
  { name: "Diminished WT", intervals: [0, 1, 3, 4, 6, 7, 9, 10, 12] },
  { name: "Minor Blues", intervals: [0, 3, 5, 6, 7, 10, 12] },
  { name: "Super Locrian", intervals: [0, 1, 3, 4, 6, 8, 10, 12] },
  { name: "Romanian Minor", intervals: [0, 2, 3, 6, 7, 9, 10, 12] },
  { name: "Spanish Gypsy", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
  { name: "Eight Tone Spanish", intervals: [0, 1, 3, 4, 5, 6, 8, 10, 12] },
  { name: "Enigmatic", intervals: [0, 1, 4, 6, 8, 10, 11, 12] },
  { name: "Neapolitan Major", intervals: [0, 1, 3, 5, 7, 9, 11, 12] },
  { name: "Neapolitan Minor", intervals: [0, 1, 3, 5, 7, 8, 11, 12] },
  { name: "Pelog", intervals: [0, 1, 3, 7, 8, 10, 12] },
  { name: "Prometheus", intervals: [0, 2, 4, 6, 9, 10, 12] },
  { name: "Prometheus Neapolitan", intervals: [0, 1, 4, 6, 9, 10, 12] },
  { name: "Six Tone Symmetric", intervals: [0, 1, 4, 5, 8, 9, 12] },
  { name: "Lydian Minor", intervals: [0, 2, 3, 6, 7, 9, 11, 12] },
  { name: "Lydian Augmented", intervals: [0, 2, 4, 6, 8, 9, 11, 12] },
  { name: "Lydian Diminished", intervals: [0, 2, 3, 6, 7, 9, 10, 12] },
  { name: "Lydian Augmented #6", intervals: [0, 2, 4, 6, 8, 10, 11, 12] },
  { name: "Hungarian Major", intervals: [0, 3, 4, 6, 7, 9, 10, 12] },
  { name: "Hungarian Minor", intervals: [0, 2, 3, 6, 7, 8, 11, 12] },
  { name: "Ichikosucho", intervals: [0, 2, 4, 5, 6, 8, 10, 12] },
  { name: "Persian", intervals: [0, 1, 4, 5, 6, 8, 11, 12] },
  { name: "Flamenco", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
  { name: "Hawaiian", intervals: [0, 2, 3, 5, 7, 8, 11, 12] },
  { name: "Maqam", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
  { name: "Oriental", intervals: [0, 1, 4, 5, 6, 9, 10, 12] },
  { name: "Iwato", intervals: [0, 1, 5, 6, 10, 12] },
  { name: "Raga Malakosh", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Balinese", intervals: [0, 1, 3, 7, 8, 12] },
  { name: "Kafi Raga", intervals: [0, 2, 3, 5, 7, 9, 10, 12] },
  { name: "Todi Raga", intervals: [0, 1, 3, 6, 7, 8, 11, 12] },
  { name: "Purvi Raga", intervals: [0, 1, 4, 6, 7, 8, 11, 12] },
  { name: "In Sen", intervals: [0, 1, 5, 7, 10, 12] },
];

const SCALE_NAME_TEXTS = {
  en: {
    Ionian: "Ionian",
    Dorian: "Dorian",
    Phrygian: "Phrygian",
    Lydian: "Lydian",
    Mixolydian: "Mixolydian",
    Aeolian: "Aeolian",
    Locrian: "Locrian",
    Chromatic: "Chromatic",
    "Locrian #2": "Locrian #2",
    "Harmonic Minor": "Harmonic Minor",
    "Melodic Minor": "Melodic Minor",
    "Major Pentatonic": "Major Pentatonic",
    "Minor Pentatonic": "Minor Pentatonic",
    "Blues Pentatonic": "Blues Pentatonic",
    "Neutral Pentatonic": "Neutral Pentatonic",
    Bebop: "Bebop",
    "Bebop Major": "Bebop Major",
    "Bebop Minor": "Bebop Minor",
    "Half Diminished": "Half Diminished",
    Diminished: "Diminished",
    "Whole Tone (WT)": "Whole Tone (WT)",
    "Diminished WT": "Diminished WT",
    "Minor Blues": "Minor Blues",
    "Super Locrian": "Super Locrian",
    "Romanian Minor": "Romanian Minor",
    "Spanish Gypsy": "Spanish Gypsy",
    "Eight Tone Spanish": "Eight Tone Spanish",
    Enigmatic: "Enigmatic",
    "Neapolitan Major": "Neapolitan Major",
    "Neapolitan Minor": "Neapolitan Minor",
    Pelog: "Pelog",
    Prometheus: "Prometheus",
    "Prometheus Neapolitan": "Prometheus Neapolitan",
    "Six Tone Symmetric": "Six Tone Symmetric",
    "Lydian Minor": "Lydian Minor",
    "Lydian Augmented": "Lydian Augmented",
    "Lydian Diminished": "Lydian Diminished",
    "Lydian Augmented #6": "Lydian Augmented #6",
    "Hungarian Major": "Hungarian Major",
    "Hungarian Minor": "Hungarian Minor",
    Ichikosucho: "Ichikosucho",
    Persian: "Persian",
    Flamenco: "Flamenco",
    Hawaiian: "Hawaiian",
    Maqam: "Maqam",
    Oriental: "Oriental",
    Iwato: "Iwato",
    "Raga Malakosh": "Raga Malakosh",
    Balinese: "Balinese",
    "Kafi Raga": "Kafi Raga",
    "Todi Raga": "Todi Raga",
    "Purvi Raga": "Purvi Raga",
    "In Sen": "In Sen",
  },
  es: {
    Ionian: "Jónica",
    Dorian: "Dórica",
    Phrygian: "Frigia",
    Lydian: "Lidia",
    Mixolydian: "Mixolidia",
    Aeolian: "Eólica",
    Locrian: "Locria",
    Chromatic: "Cromática",
    "Locrian #2": "Locria #2",
    "Harmonic Minor": "Menor armónica",
    "Melodic Minor": "Menor melódica",
    "Major Pentatonic": "Pentatónica mayor",
    "Minor Pentatonic": "Pentatónica menor",
    "Blues Pentatonic": "Pentatónica blues",
    "Neutral Pentatonic": "Pentatónica neutral",
    Bebop: "Bebop",
    "Bebop Major": "Bebop mayor",
    "Bebop Minor": "Bebop menor",
    "Half Diminished": "Semidisminuida",
    Diminished: "Disminuida",
    "Whole Tone (WT)": "Tonos enteros (WT)",
    "Diminished WT": "Disminuida WT",
    "Minor Blues": "Blues menor",
    "Super Locrian": "Superlocria",
    "Romanian Minor": "Menor rumana",
    "Spanish Gypsy": "Gitana española",
    "Eight Tone Spanish": "Española de ocho tonos",
    Enigmatic: "Enigmática",
    "Neapolitan Major": "Napolitana mayor",
    "Neapolitan Minor": "Napolitana menor",
    Pelog: "Pelog",
    Prometheus: "Prometeo",
    "Prometheus Neapolitan": "Prometeo napolitana",
    "Six Tone Symmetric": "Simétrica de seis tonos",
    "Lydian Minor": "Lidia menor",
    "Lydian Augmented": "Lidia aumentada",
    "Lydian Diminished": "Lidia disminuida",
    "Lydian Augmented #6": "Lidia aumentada #6",
    "Hungarian Major": "Húngara mayor",
    "Hungarian Minor": "Menor húngara",
    Ichikosucho: "Ichikosucho",
    Persian: "Persa",
    Flamenco: "Flamenca",
    Hawaiian: "Hawaiana",
    Maqam: "Maqam",
    Oriental: "Oriental",
    Iwato: "Iwato",
    "Raga Malakosh": "Raga Malakosh",
    Balinese: "Balinesa",
    "Kafi Raga": "Raga Kafi",
    "Todi Raga": "Raga Todi",
    "Purvi Raga": "Raga Purvi",
    "In Sen": "In Sen",
  },
};

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

function tonicLetterIndex(tonicPc, preferFlats) {
  const pc = ((Number(tonicPc) % 12) + 12) % 12;
  const mapping = preferFlats
    ? { 0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5, 10: 6, 11: 6 }
    : { 0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5, 11: 6 };
  return Number(mapping[pc] ?? 0);
}

function applyAccidental(base, diff) {
  if (diff === 0) return `${base}`;
  if (diff === 1) return `${base}#`;
  if (diff === -1) return `${base}♭`;
  if (diff === 2) return `${base}##`;
  if (diff === -2) return `${base}♭♭`;
  return null;
}

function spellByDegree(rootPc, targetPc, degree, language, preferFlats, midiNote = null, withOctave = false) {
  const letterNames = language === "es" ? ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] : ["C", "D", "E", "F", "G", "A", "B"];
  const basePcs = [0, 2, 4, 5, 7, 9, 11];
  const tonicLetter = tonicLetterIndex(rootPc, preferFlats);
  const letterIdx = (tonicLetter + Number(degree)) % 7;
  const naturalPc = basePcs[letterIdx];
  let diff = ((Number(targetPc) - naturalPc) % 12 + 12) % 12;
  if (diff > 6) diff -= 12;
  const spelled = applyAccidental(letterNames[letterIdx], diff);
  if (spelled == null) {
    const fallbackNote = Number(midiNote == null ? targetPc : midiNote);
    return noteName(fallbackNote, language, preferFlats, withOctave);
  }
  if (withOctave && midiNote != null) {
    const octave = Math.floor(Number(midiNote) / 12) - 1;
    return `${spelled}${octave}`;
  }
  return spelled;
}

function chordIntervalDegree(interval, suffix) {
  const value = Number(interval);
  const suffixText = String(suffix || "");
  if (value === 0 || value === 12) return 0;
  if ([1, 2, 13, 14].includes(value)) return 1;
  if ([3, 4, 15].includes(value)) return 2;
  if ([5, 17].includes(value)) return 3;
  if ([6, 18].includes(value)) {
    if (suffixText.includes("b5") || suffixText.includes("dim")) return 4;
    return 3;
  }
  if (value === 7) return 4;
  if (value === 8) {
    if (suffixText.includes("#5") || suffixText.includes("aug")) return 4;
    return 5;
  }
  if ([9, 21].includes(value)) return 5;
  if ([10, 11].includes(value)) return 6;
  return Math.max(0, Math.min(6, value % 7));
}

function voicedIntervalsForInversion(intervals, inversion) {
  if (!intervals.length) return [];
  const total = intervals.length;
  const idx = Math.max(0, Math.min(Number(inversion) || 0, total - 1));
  const rotated = Array.from({ length: total }, (_, i) => Number(intervals[(idx + i) % total]));
  const voiced = [];
  for (const raw of rotated) {
    let value = Number(raw);
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
  const priority = new Map(COMMON_CHORD_SUFFIX_ORDER.map((suffix, idx) => [suffix, idx]));
  return [...CHORD_PATTERNS]
    .sort((a, b) => {
      const pa = priority.has(a.suffix) ? priority.get(a.suffix) : COMMON_CHORD_SUFFIX_ORDER.length;
      const pb = priority.has(b.suffix) ? priority.get(b.suffix) : COMMON_CHORD_SUFFIX_ORDER.length;
      if (pa !== pb) return pa - pb;
      if (a.intervals.length !== b.intervals.length) return a.intervals.length - b.intervals.length;
      if (a.suffix < b.suffix) return -1;
      if (a.suffix > b.suffix) return 1;
      return 0;
    })
    .map((p) => ({ suffix: p.suffix, intervals: [...p.intervals] }));
}

function listScalePatterns(language = "es") {
  const localized = SCALE_NAME_TEXTS[language] || SCALE_NAME_TEXTS.en;
  return SCALE_PATTERNS.map((pattern) => ({
    name: pattern.name,
    localized_name: localized[pattern.name] || pattern.name,
    intervals: [...pattern.intervals],
  }));
}

function generateChord({ rootPc = 0, suffix = "", inversion = 0, language = "es", preferFlat = false }) {
  const selected = CHORD_PATTERNS.find((p) => p.suffix === suffix) || CHORD_PATTERNS[0];
  if (!selected.intervals.length) {
    return { root_pc: Number(rootPc) % 12, suffix: selected.suffix, inversion: 0, name: "-", notes_midi: [], notes: [] };
  }
  const safeInversion = Math.max(0, Math.min(Number(inversion) || 0, selected.intervals.length - 1));
  const rootMidi = 60 + (Number(rootPc) % 12);
  const voicedIntervals = voicedIntervalsForInversion(selected.intervals, safeInversion);
  const notesMidi = voicedIntervals.map((i) => rootMidi + i);
  const notes = [];
  const notesNoOctave = [];
  for (let i = 0; i < notesMidi.length; i += 1) {
    const interval = voicedIntervals[i];
    const midiNote = notesMidi[i];
    const degree = chordIntervalDegree(interval, selected.suffix);
    const pc = midiNote % 12;
    notes.push(spellByDegree(rootPc, pc, degree, language, preferFlat, midiNote, true));
    notesNoOctave.push(spellByDegree(rootPc, pc, degree, language, preferFlat, midiNote, false));
  }
  const rootName = spellByDegree(rootPc, Number(rootPc) % 12, 0, language, preferFlat, rootPc, false);
  let chordName = `${rootName}${selected.suffix}`;
  if (safeInversion > 0 && notesMidi.length) chordName = `${chordName}/${notesNoOctave[0]}`;
  return {
    root_pc: Number(rootPc) % 12,
    suffix: selected.suffix,
    inversion: safeInversion,
    name: chordName,
    notes_midi: notesMidi,
    notes,
    notes_no_octave: notesNoOctave,
    intervals: voicedIntervals,
  };
}

function detectChord({ notes = [], language = "es", preferFlat = false }) {
  const midiNotes = [...new Set((Array.isArray(notes) ? notes : []).map((n) => Number(n)).filter((n) => Number.isFinite(n)))].sort((a, b) => a - b);
  if (!midiNotes.length) return { name: "-", extras_midi: [], notes_midi: [], notes: [], extras: [] };

  const pcs = new Set(midiNotes.map((n) => n % 12));
  if (pcs.size === 1) {
    const single = midiNotes[0];
    return {
      name: noteName(single, language, preferFlat, false),
      notes_midi: midiNotes,
      notes: midiNotes.map((n) => noteName(n, language, preferFlat, true)),
      extras_midi: [],
      extras: [],
    };
  }

  const { root, pattern, bassPc } = analyzeChordNotes(new Set(midiNotes));
  if (root == null || pattern == null) {
    return {
      name: midiNotes.map((n) => noteName(n, language, preferFlat, false)).join(" + "),
      notes_midi: midiNotes,
      notes: midiNotes.map((n) => noteName(n, language, preferFlat, true)),
      extras_midi: [],
      extras: [],
    };
  }

  const degreeByPc = {};
  for (const interval of pattern.intervals) {
    const pc = (Number(root) + Number(interval)) % 12;
    if (!(pc in degreeByPc)) degreeByPc[pc] = chordIntervalDegree(interval, pattern.suffix);
  }

  const rootName = spellByDegree(root, root, 0, language, preferFlat, root, false);
  let chordName = `${rootName}${pattern.suffix}`;
  if (bassPc != null && bassPc !== root) {
    const bassDegree = degreeByPc[Number(bassPc)];
    const bassName = bassDegree == null
      ? noteName(bassPc, language, preferFlat, false)
      : spellByDegree(root, bassPc, bassDegree, language, preferFlat, bassPc, false);
    chordName = `${chordName}/${bassName}`;
  }

  const expectedPcs = new Set(pattern.intervals.map((i) => (Number(root) + Number(i)) % 12));
  const extrasMidi = midiNotes.filter((n) => !expectedPcs.has(n % 12));
  const noteLabels = midiNotes.map((n) => {
    const degree = degreeByPc[n % 12];
    if (degree == null) return noteName(n, language, preferFlat, true);
    return spellByDegree(root, n % 12, degree, language, preferFlat, n, true);
  });

  return {
    name: chordName,
    notes_midi: midiNotes,
    notes: noteLabels,
    extras_midi: extrasMidi,
    extras: extrasMidi.map((n) => noteName(n, language, preferFlat, true)),
    root_pc: Number(root),
    suffix: pattern.suffix,
  };
}

function generateScale({ tonicPc = 0, patternName = "Ionian", language = "es", preferFlat = false }) {
  const pattern = SCALE_PATTERNS.find((p) => p.name === patternName) || SCALE_PATTERNS[0];
  const rootMidi = 60 + (Number(tonicPc) % 12);
  const intervals = [...pattern.intervals];
  const notesMidi = intervals.map((i) => rootMidi + Number(i));
  const notes = notesMidi.map((midiNote, degree) =>
    spellByDegree(tonicPc, midiNote % 12, degree, language, preferFlat, midiNote, true));
  const localized = (SCALE_NAME_TEXTS[language] || SCALE_NAME_TEXTS.en)[pattern.name] || pattern.name;
  return {
    tonic_pc: Number(tonicPc) % 12,
    pattern_name: pattern.name,
    pattern_localized_name: localized,
    notes_midi: notesMidi,
    notes,
    intervals,
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
      const language = normalizeLanguage(url.searchParams.get("language"));
      return json({
        chord_patterns: listChordPatterns(),
        scale_patterns: listScalePatterns(language),
      });
    }

    if (pathname === "/api/detect" && request.method === "POST") {
      const body = await readJson(request);
      return json(detectChord({
        notes: Array.isArray(body.notes) ? body.notes : [],
        language: normalizeLanguage(body.language),
        preferFlat: normalizePreferFlat(body.accidental),
      }));
    }

    if (pathname === "/api/generate/chord" && request.method === "POST") {
      const body = await readJson(request);
      return json(generateChord({
        rootPc: Number(body.root_pc) || 0,
        suffix: String(body.suffix || ""),
        inversion: Number(body.inversion) || 0,
        language: normalizeLanguage(body.language),
        preferFlat: normalizePreferFlat(body.accidental),
      }));
    }

    if (pathname === "/api/generate/scale" && request.method === "POST") {
      const body = await readJson(request);
      return json(generateScale({
        tonicPc: Number(body.tonic_pc) || 0,
        patternName: String(body.pattern_name || "Ionian"),
        language: normalizeLanguage(body.language),
        preferFlat: normalizePreferFlat(body.accidental),
      }));
    }

    if (pathname === "/api/generate/guitar-variations" && request.method === "POST") return json({ variations: [] });
    if (pathname.startsWith("/api/")) return json({ error: "Not found" }, 404);

    return env.ASSETS.fetch(request);
  },
};
