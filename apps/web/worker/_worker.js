/** Alineado con escritorio (`APP_RELEASE_NAME`) y móvil (`pubspec.yaml`). */
const APP_VERSION = "1.0.2";

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
  { suffix: "add2", intervals: [0, 2, 4, 7] },
  { suffix: "add4", intervals: [0, 4, 5, 7] },
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
  "", "m", "7", "maj7", "m7", "add2", "add4", "sus2", "sus4", "dim", "aug", "5", "6", "m6",
  "add9", "madd9", "9", "maj9", "m9", "11", "m11", "13", "m13", "dim7", "m7b5",
];

const CHORD_SUFFIX_NAMES = {
  es: {
    "": "Mayor",
    "m": "Menor",
    "5": "Quinta (power chord)",
    "-5": "Mayor quinta disminuida",
    "dim": "Disminuido",
    "aug": "Aumentado",
    "sus2": "Suspendido 2ª",
    "sus4": "Suspendido 4ª",
    "sus2sus4": "Suspendido 2ª y 4ª",
    "add2": "Mayor con 2ª añadida",
    "add4": "Mayor con 4ª añadida",
    "add9": "Mayor con 9ª añadida",
    "madd9": "Menor con 9ª añadida",
    "6": "Mayor con 6ª",
    "6add9": "Mayor con 6ª y 9ª",
    "m6": "Menor con 6ª",
    "m6add9": "Menor con 6ª y 9ª",
    "7": "Mayor dominante (7ª menor)",
    "7sus4": "Dominante suspendido 4ª",
    "7#5": "Dominante aumentado",
    "7b5": "Dominante quinta disminuida",
    "7#9": "Dominante con 9ª aumentada",
    "7b9": "Dominante con 9ª disminuida",
    "7(#5,#9)": "Dominante aumentado con 9ª aumentada",
    "7(#5,b9)": "Dominante aumentado con 9ª disminuida",
    "7(b5,#9)": "Dominante quinta disminuida con 9ª aumentada",
    "7(b5,b9)": "Dominante quinta disminuida con 9ª disminuida",
    "9": "Dominante con 9ª",
    "9#5": "Dominante aumentado con 9ª",
    "9b5": "Dominante quinta disminuida con 9ª",
    "11": "Dominante con 11ª",
    "11b9": "Dominante con 11ª y 9ª disminuida",
    "13": "Dominante con 13ª",
    "13b9": "Dominante con 13ª y 9ª disminuida",
    "13#11": "Dominante con 13ª y 11ª aumentada",
    "maj7": "Mayor con 7ª mayor",
    "maj7#5": "Mayor aumentado con 7ª mayor",
    "maj7b5": "Mayor quinta disminuida con 7ª mayor",
    "maj9": "Mayor con 9ª y 7ª mayor",
    "maj11": "Mayor con 11ª y 7ª mayor",
    "maj13": "Mayor con 13ª y 7ª mayor",
    "maj9#11": "Mayor con 9ª, 11ª aumentada y 7ª mayor",
    "maj13#11": "Mayor con 13ª, 11ª aumentada y 7ª mayor",
    "m7": "Menor con 7ª menor",
    "m7#5": "Menor aumentado con 7ª menor",
    "m9": "Menor con 9ª y 7ª menor",
    "m11": "Menor con 11ª y 7ª menor",
    "m13": "Menor con 13ª y 7ª menor",
    "mMaj7": "Menor con 7ª mayor",
    "mMaj9": "Menor con 9ª y 7ª mayor",
    "dim7": "Disminuido con 7ª disminuida",
    "m7b5": "Semidisminuido (menor con quinta disminuida)",
  },
  en: {
    "": "Major",
    "m": "Minor",
    "5": "Power chord",
    "-5": "Major flat five",
    "dim": "Diminished",
    "aug": "Augmented",
    "sus2": "Suspended 2nd",
    "sus4": "Suspended 4th",
    "sus2sus4": "Suspended 2nd and 4th",
    "add2": "Major add 2nd",
    "add4": "Major add 4th",
    "add9": "Major add 9th",
    "madd9": "Minor add 9th",
    "6": "Major 6th",
    "6add9": "Major 6th add 9th",
    "m6": "Minor 6th",
    "m6add9": "Minor 6th add 9th",
    "7": "Dominant 7th (major with minor 7th)",
    "7sus4": "Dominant suspended 4th",
    "7#5": "Augmented dominant",
    "7b5": "Dominant flat five",
    "7#9": "Dominant sharp 9th",
    "7b9": "Dominant flat 9th",
    "7(#5,#9)": "Augmented dominant sharp 9th",
    "7(#5,b9)": "Augmented dominant flat 9th",
    "7(b5,#9)": "Dominant flat five sharp 9th",
    "7(b5,b9)": "Dominant flat five flat 9th",
    "9": "Dominant 9th",
    "9#5": "Augmented dominant 9th",
    "9b5": "Dominant flat five 9th",
    "11": "Dominant 11th",
    "11b9": "Dominant 11th flat 9th",
    "13": "Dominant 13th",
    "13b9": "Dominant 13th flat 9th",
    "13#11": "Dominant 13th sharp 11th",
    "maj7": "Major 7th",
    "maj7#5": "Augmented major 7th",
    "maj7b5": "Major flat five major 7th",
    "maj9": "Major 9th",
    "maj11": "Major 11th",
    "maj13": "Major 13th",
    "maj9#11": "Major 9th sharp 11th",
    "maj13#11": "Major 13th sharp 11th",
    "m7": "Minor 7th",
    "m7#5": "Augmented minor 7th",
    "m9": "Minor 9th",
    "m11": "Minor 11th",
    "m13": "Minor 13th",
    "mMaj7": "Minor major 7th",
    "mMaj9": "Minor major 9th",
    "dim7": "Diminished 7th",
    "m7b5": "Half-diminished (minor flat five)",
  },
};

const SCALE_PATTERNS = [
  { name: "Ionian", intervals: [0, 2, 4, 5, 7, 9, 11, 12] },
  { name: "Aeolian", intervals: [0, 2, 3, 5, 7, 8, 10, 12] },
  { name: "Harmonic Minor", intervals: [0, 2, 3, 5, 7, 8, 11, 12] },
  { name: "Melodic Minor", intervals: [0, 2, 3, 5, 7, 9, 11, 12] },
  { name: "Dorian", intervals: [0, 2, 3, 5, 7, 9, 10, 12] },
  { name: "Phrygian", intervals: [0, 1, 3, 5, 7, 8, 10, 12] },
  { name: "Lydian", intervals: [0, 2, 4, 6, 7, 9, 11, 12] },
  { name: "Mixolydian", intervals: [0, 2, 4, 5, 7, 9, 10, 12] },
  { name: "Locrian", intervals: [0, 1, 3, 5, 6, 8, 10, 12] },
  { name: "Major Pentatonic", intervals: [0, 2, 4, 7, 9, 12] },
  { name: "Minor Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Blues Major", intervals: [0, 2, 3, 4, 7, 9, 12] },
  { name: "Minor Blues", intervals: [0, 3, 5, 6, 7, 10, 12] },
  { name: "Chromatic", intervals: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] },
  { name: "Whole Tone (WT)", intervals: [0, 2, 4, 6, 8, 10, 12] },
  { name: "Diminished", intervals: [0, 2, 3, 5, 6, 8, 9, 11, 12] },
  { name: "Diminished WT", intervals: [0, 1, 3, 4, 6, 7, 9, 10, 12] },
  { name: "Spanish Gypsy", intervals: [0, 1, 4, 5, 7, 8, 10, 12] },
  { name: "Double Harmonic", intervals: [0, 1, 4, 5, 7, 8, 11, 12] },
  { name: "Dorian b2", intervals: [0, 1, 3, 5, 7, 9, 10, 12] },
  { name: "Lydian Augmented", intervals: [0, 2, 4, 6, 8, 9, 11, 12] },
  { name: "Lydian Dominant", intervals: [0, 2, 4, 6, 7, 9, 10, 12] },
  { name: "Mixolydian b6", intervals: [0, 2, 4, 5, 7, 8, 10, 12] },
  { name: "Locrian #2", intervals: [0, 2, 3, 5, 6, 8, 10, 12] },
  { name: "Super Locrian", intervals: [0, 1, 3, 4, 6, 8, 10, 12] },
  { name: "Blues Pentatonic", intervals: [0, 3, 5, 7, 10, 12] },
  { name: "Neutral Pentatonic", intervals: [0, 2, 5, 7, 10, 12] },
  { name: "Bebop", intervals: [0, 2, 4, 5, 7, 9, 10, 11, 12] },
  { name: "Bebop Major", intervals: [0, 2, 4, 5, 7, 8, 9, 11, 12] },
  { name: "Bebop Minor", intervals: [0, 2, 3, 4, 5, 7, 9, 10, 12] },
  { name: "Half Diminished", intervals: [0, 2, 3, 5, 6, 8, 10, 12] },
  { name: "Romanian Minor", intervals: [0, 2, 3, 6, 7, 9, 10, 12] },
  { name: "Eight Tone Spanish", intervals: [0, 1, 3, 4, 5, 6, 8, 10, 12] },
  { name: "Enigmatic", intervals: [0, 1, 4, 6, 8, 10, 11, 12] },
  { name: "Neapolitan Major", intervals: [0, 1, 3, 5, 7, 9, 11, 12] },
  { name: "Neapolitan Minor", intervals: [0, 1, 3, 5, 7, 8, 11, 12] },
  { name: "Pelog", intervals: [0, 1, 3, 7, 8, 10, 12] },
  { name: "Prometheus", intervals: [0, 2, 4, 6, 9, 10, 12] },
  { name: "Prometheus Neapolitan", intervals: [0, 1, 4, 6, 9, 10, 12] },
  { name: "Six Tone Symmetric", intervals: [0, 1, 4, 5, 8, 9, 12] },
  { name: "Lydian Minor", intervals: [0, 2, 3, 6, 7, 9, 11, 12] },
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
    "Locrian #2": "Locrian ♮2",
    "Harmonic Minor": "Harmonic Minor",
    "Melodic Minor": "Melodic Minor",
    "Major Pentatonic": "Major Pentatonic",
    "Minor Pentatonic": "Minor Pentatonic",
    "Blues Major": "Blues Major",
    "Blues Pentatonic": "Blues Pentatonic",
    "Neutral Pentatonic": "Neutral Pentatonic",
    Bebop: "Bebop",
    "Bebop Major": "Bebop Major",
    "Bebop Minor": "Bebop Minor",
    "Half Diminished": "Half Diminished",
    Diminished: "Diminished (WH)",
    "Whole Tone (WT)": "Whole Tone",
    "Diminished WT": "Diminished (HW)",
    "Minor Blues": "Minor Blues",
    "Super Locrian": "Super Locrian",
    "Romanian Minor": "Romanian Minor",
    "Spanish Gypsy": "Phrygian Dominant",
    "Double Harmonic": "Double Harmonic",
    "Dorian b2": "Dorian ♭2",
    "Lydian Dominant": "Lydian Dominant",
    "Mixolydian b6": "Mixolydian ♭6",
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
    "Locrian #2": "Locria ♮2",
    "Harmonic Minor": "Menor armónica",
    "Melodic Minor": "Menor melódica",
    "Major Pentatonic": "Pentatónica mayor",
    "Minor Pentatonic": "Pentatónica menor",
    "Blues Major": "Blues mayor",
    "Blues Pentatonic": "Pentatónica blues",
    "Neutral Pentatonic": "Pentatónica neutral",
    Bebop: "Bebop",
    "Bebop Major": "Bebop mayor",
    "Bebop Minor": "Bebop menor",
    "Half Diminished": "Semidisminuida",
    Diminished: "Disminuida (tono-semitono)",
    "Whole Tone (WT)": "Tonos enteros",
    "Diminished WT": "Disminuida (semitono-tono)",
    "Minor Blues": "Blues menor",
    "Super Locrian": "Superlocria",
    "Romanian Minor": "Menor rumana",
    "Spanish Gypsy": "Frigia dominante",
    "Double Harmonic": "Doble armónica",
    "Dorian b2": "Dórica ♭2",
    "Lydian Dominant": "Lidia dominante",
    "Mixolydian b6": "Mixolidia ♭6",
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

/** HEAD para monitorización sin cuerpo (mismo status que GET). */
function apiHeadOk() {
  return new Response(null, {
    status: 200,
    headers: {
      "access-control-allow-origin": "*",
      "cache-control": "no-store",
      "cdn-cache-control": "no-store",
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

// pc de cada letra natural (Do..Si), en el mismo orden que ROOT_LETTERS del
// cliente — usado para mapear tonicLetterPc (pc de letra elegida en el combo
// de tónica) a un índice de letra 0-6.
const ROOT_LETTER_PCS_ORDERED = [0, 2, 4, 5, 7, 9, 11];

function tonicLetterIndex(tonicPc, preferFlats, tonicLetterPc = null) {
  if (tonicLetterPc != null) {
    const idx = ROOT_LETTER_PCS_ORDERED.indexOf(((Number(tonicLetterPc) % 12) + 12) % 12);
    if (idx >= 0) return idx;
  }
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

function spellByDegree(rootPc, targetPc, degree, language, preferFlats, midiNote = null, withOctave = false, tonicLetterPc = null) {
  const letterNames = language === "es" ? ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"] : ["C", "D", "E", "F", "G", "A", "B"];
  const basePcs = [0, 2, 4, 5, 7, 9, 11];
  const tonicLetter = tonicLetterIndex(rootPc, preferFlats, tonicLetterPc);
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
  const bassPc = Math.min(...Array.from(notesSet)) % 12;
  const suffixPriority = new Map(COMMON_CHORD_SUFFIX_ORDER.map((s, i) => [s, i]));
  let bestScore = -999;
  let bestComplexity = -999;
  let bestRootIsBass = false;
  let bestPriority = 999;
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
      // Distintos acordes pueden compartir exactamente las mismas notas
      // (p. ej. Do sus2 = Do-Re-Sol y Sol sus4 = Sol-Do-Re son el mismo
      // conjunto de pitch-classes). En ese empate exacto, la nota más
      // grave realmente tocada (bassPc) es la señal más fuerte de cuál es
      // la raíz percibida, y debe primar sobre la prioridad fija de
      // sufijos (que si no, siempre elegía "sus4" sobre "sus2").
      const rootIsBass = root === bassPc;
      const priority = suffixPriority.has(pattern.suffix) ? suffixPriority.get(pattern.suffix) : COMMON_CHORD_SUFFIX_ORDER.length;
      const better = score > bestScore
        || (score === bestScore && complexity > bestComplexity)
        || (score === bestScore && complexity === bestComplexity && rootIsBass && !bestRootIsBass)
        || (score === bestScore && complexity === bestComplexity && rootIsBass === bestRootIsBass && priority < bestPriority);
      if (better) {
        bestScore = score;
        bestComplexity = complexity;
        bestRootIsBass = rootIsBass;
        bestPriority = priority;
        bestRoot = root;
        bestPattern = pattern;
      }
    }
  }
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

function isMinorChordSuffix(suffix) {
  const s = String(suffix || "");
  return s.startsWith("m") && !s.startsWith("maj");
}

/** Nombre del acorde (tónica/bajo): menos alteraciones; empate enarmónico → bemoles. */
function chordSymbolPreferFlat(rootPc, isMinor) {
  const pc = ((Number(rootPc) % 12) + 12) % 12;
  const sharpMap = isMinor
    ? { 4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7 }
    : { 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7 };
  const flatMap = isMinor
    ? { 2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6 }
    : { 5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6 };
  const sc = sharpMap[pc];
  const fc = flatMap[pc];
  if (sc == null && fc == null) return false;
  if (sc == null) return true;
  if (fc == null) return false;
  if (fc < sc) return true;
  if (sc < fc) return false;
  return true;
}

function generateChord({ rootPc = 0, suffix = "", inversion = 0, language = "es", preferFlat = false, tonicLetterPc = null }) {
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
    notes.push(spellByDegree(rootPc, pc, degree, language, preferFlat, midiNote, true, tonicLetterPc));
    notesNoOctave.push(spellByDegree(rootPc, pc, degree, language, preferFlat, midiNote, false, tonicLetterPc));
  }
  const rootName = spellByDegree(rootPc, Number(rootPc) % 12, 0, language, preferFlat, rootPc, false, tonicLetterPc);
  let chordName = `${rootName}${selected.suffix}`;
  let bassName = null;
  if (safeInversion > 0 && notesMidi.length) {
    bassName = notesNoOctave[0];
    chordName = `${chordName}/${bassName}`;
  }

  const suffixDesc = (CHORD_SUFFIX_NAMES[language] || CHORD_SUFFIX_NAMES.en)[selected.suffix] || null;
  let description = suffixDesc;
  if (suffixDesc && bassName) {
    const INVERSION_NAMES = {
      es: ["", "primera inversión", "segunda inversión", "tercera inversión"],
      en: ["", "first inversion", "second inversion", "third inversion"],
    };
    const lang = INVERSION_NAMES[language] ? language : "en";
    const invName = safeInversion > 0 && safeInversion < INVERSION_NAMES[lang].length
      ? INVERSION_NAMES[lang][safeInversion]
      : null;
    description = invName
      ? `${suffixDesc}, ${invName}`
      : `${suffixDesc}, ${language === "es" ? "bajo en" : "bass on"} ${bassName}`;
  }

  return {
    root_pc: Number(rootPc) % 12,
    suffix: selected.suffix,
    inversion: safeInversion,
    name: chordName,
    notes_midi: notesMidi,
    notes,
    notes_no_octave: notesNoOctave,
    intervals: voicedIntervals,
    description,
  };
}

function detectChord({ notes = [], language = "es", preferFlat = false }) {
  const midiNotes = [...new Set((Array.isArray(notes) ? notes : []).map((n) => Number(n)).filter((n) => Number.isFinite(n)))].sort((a, b) => a - b);
  if (!midiNotes.length) return { name: "-", extras_midi: [], notes_midi: [], notes: [], extras: [] };

  const pcs = new Set(midiNotes.map((n) => n % 12));
  if (pcs.size === 1) {
    const single = midiNotes[0];
    const namePf = chordSymbolPreferFlat(single % 12, false);
    return {
      name: noteName(single, language, namePf, false),
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

  const namePf = chordSymbolPreferFlat(root, isMinorChordSuffix(pattern.suffix));
  const rootName = spellByDegree(root, root, 0, language, namePf, root, false);
  let chordName = `${rootName}${pattern.suffix}`;
  let bassName = null;
  if (bassPc != null && bassPc !== root) {
    const bassDegree = degreeByPc[Number(bassPc)];
    bassName = bassDegree == null
      ? noteName(bassPc, language, namePf, false)
      : spellByDegree(root, bassPc, bassDegree, language, namePf, bassPc, false);
    chordName = `${chordName}/${bassName}`;
  }

  const expectedPcs = new Set(pattern.intervals.map((i) => (Number(root) + Number(i)) % 12));
  const extrasMidi = midiNotes.filter((n) => !expectedPcs.has(n % 12));
  // Notas dentro del acorde reconocido: ortografía diatónica fija respecto a su
  // tónica (p. ej. la 3ª de Mi mayor siempre es Sol#, nunca Lab) — el ajuste
  // #/♭ del usuario solo decide notas "extra" que caen fuera del acorde.
  const noteLabels = midiNotes.map((n) => {
    const pc = n % 12;
    const degree = degreeByPc[pc];
    return degree == null
      ? noteName(n, language, preferFlat, true)
      : spellByDegree(root, pc, degree, language, namePf, n, true);
  });

  const suffixDesc = (CHORD_SUFFIX_NAMES[language] || CHORD_SUFFIX_NAMES.en)[pattern.suffix] || null;
  let description = suffixDesc;
  if (suffixDesc && bassName) {
    const bassInterval = (Number(bassPc) - Number(root) + 12) % 12;
    const inversionIndex = pattern.intervals.indexOf(bassInterval);
    const INVERSION_NAMES = {
      es: ["", "primera inversión", "segunda inversión", "tercera inversión"],
      en: ["", "first inversion", "second inversion", "third inversion"],
    };
    const lang = INVERSION_NAMES[language] ? language : "en";
    const invName = inversionIndex > 0 ? INVERSION_NAMES[lang][inversionIndex] : null;
    description = invName
      ? `${suffixDesc}, ${invName}`
      : `${suffixDesc}, ${language === "es" ? "bajo en" : "bass on"} ${bassName}`;
  }

  return {
    name: chordName,
    notes_midi: midiNotes,
    notes: noteLabels,
    extras_midi: extrasMidi,
    extras: extrasMidi.map((n) => noteName(n, language, preferFlat, true)),
    root_pc: Number(root),
    suffix: pattern.suffix,
    inversion: inversionIndex,
    description,
  };
}

function generateScale({ tonicPc = 0, patternName = "Ionian", language = "es", preferFlat = false, tonicLetterPc = null }) {
  const pattern = SCALE_PATTERNS.find((p) => p.name === patternName) || SCALE_PATTERNS[0];
  const rootMidi = 60 + (Number(tonicPc) % 12);
  const intervals = [...pattern.intervals];
  const notesMidi = intervals.map((i) => rootMidi + Number(i));
  const notes = notesMidi.map((midiNote, degree) =>
    spellByDegree(tonicPc, midiNote % 12, degree, language, preferFlat, midiNote, true, tonicLetterPc));
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

function isPreviewDeployment(env) {
  const branch = String(env?.CF_PAGES_BRANCH || "").trim().toLowerCase();
  if (!branch) return false;
  return branch !== "main" && branch !== "master";
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function sendFeedbackViaResend({ to, name, email, message, env }) {
  const apiKey = String(env?.RESEND_API_KEY || "").trim();
  const from = String(env?.MIDICHORDS_FEEDBACK_FROM || "").trim();
  const preview = isPreviewDeployment(env);
  if (!apiKey || !from) {
    return json({ ok: false, error: "feedback provider misconfigured", provider: "resend" }, 500);
  }

  const subjectPrefix = preview ? "[MIDIChords Preview]" : "[MIDIChords]";
  const subject = `${subjectPrefix} Nuevo comentario de ${name}`;
  const text = [
    `Nombre: ${name}`,
    `Email: ${email}`,
    "",
    "Mensaje:",
    message,
  ].join("\n");
  const html = [
    `<p><strong>Nombre:</strong> ${escapeHtml(name)}</p>`,
    `<p><strong>Email:</strong> ${escapeHtml(email)}</p>`,
    "<p><strong>Mensaje:</strong></p>",
    `<pre style="white-space:pre-wrap;font-family:inherit;">${escapeHtml(message)}</pre>`,
  ].join("");

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      from,
      to: [to],
      reply_to: email,
      subject,
      text,
      html,
    }),
  });

  if (!resp.ok) {
    const body = await resp.text();
    return json(
      { ok: false, error: "feedback provider error", provider: "resend", status: resp.status, body },
      502,
    );
  }
  return json({ ok: true, sent: true, provider: "resend", sent_to: to });
}

async function forwardFeedbackByEmail(body, env) {
  const to = String(env?.MIDICHORDS_FEEDBACK_TO || "aortega98@gmail.com").trim();
  const provider = String(env?.MIDICHORDS_FEEDBACK_PROVIDER || "none").trim().toLowerCase();
  const name = String(body?.name || "").trim();
  const email = String(body?.email || "").trim();
  const message = String(body?.message || "").trim();

  if (!name || !email || !message) {
    return json({ error: "missing required fields" }, 400);
  }

  if (provider === "resend") {
    return sendFeedbackViaResend({ to, name, email, message, env });
  }

  return json({ ok: true, sent: false, queued: true, provider, sent_to: to, reason: "provider_disabled" });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let pathname = url.pathname;
    while (pathname.length > 1 && pathname.endsWith("/")) {
      pathname = pathname.slice(0, -1);
    }

    if (request.method === "OPTIONS" && pathname.startsWith("/api/")) {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET,HEAD,POST,OPTIONS",
          "access-control-allow-headers": "content-type",
        },
      });
    }

    if (pathname === "/api/health" && (request.method === "GET" || request.method === "HEAD")) {
      if (request.method === "HEAD") return apiHeadOk();
      return json({ status: "ok" });
    }

    if (pathname === "/api/meta" && (request.method === "GET" || request.method === "HEAD")) {
      if (request.method === "HEAD") return apiHeadOk();
      const language = normalizeLanguage(url.searchParams.get("language"));
      return json({
        app_version: APP_VERSION,
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
        tonicLetterPc: body.tonic_letter_pc != null ? Number(body.tonic_letter_pc) : null,
      }));
    }

    if (pathname === "/api/generate/scale" && request.method === "POST") {
      const body = await readJson(request);
      return json(generateScale({
        tonicPc: Number(body.tonic_pc) || 0,
        patternName: String(body.pattern_name || "Ionian"),
        language: normalizeLanguage(body.language),
        preferFlat: normalizePreferFlat(body.accidental),
        tonicLetterPc: body.tonic_letter_pc != null ? Number(body.tonic_letter_pc) : null,
      }));
    }

    if (pathname === "/api/feedback" && request.method === "POST") {
      const body = await readJson(request);
      return forwardFeedbackByEmail(body, env);
    }

    if (pathname === "/api/generate/guitar-variations" && request.method === "POST") return json({ variations: [] });
    if (pathname.startsWith("/api/")) return json({ error: "Not found" }, 404);

    // Estáticos con ?v=… o #…: en Pages, env.ASSETS.fetch a menudo devuelve 404 aunque el
    // fichero exista. Redirigir al recurso canónico (sin query) es fiable: el navegador
    // y urllib (chequeo CI) siguen la 307 y cargan el asset.
    if (
      pathname.startsWith("/static/") &&
      (url.search || url.hash) &&
      (request.method === "GET" || request.method === "HEAD")
    ) {
      const target = `${url.origin}${pathname}`;
      return new Response(null, {
        status: 307,
        headers: {
          location: target,
          "cache-control": "no-store",
          "cdn-cache-control": "no-store",
        },
      });
    }

    const assetResp = await env.ASSETS.fetch(request);

    // Evita que Cloudflare/cliente se queden con CSS/JS viejos tras desplegar.
    // (En local no pasa porque no hay cache CDN.)
    // cdn-cache-control: el edge de Cloudflare puede cachear aunque Cache-Control sea no-store
    // si una regla del zona lo ignora; CDN-Cache-Control refuerza el comportamiento en edge.
    if (
      pathname === "/" ||
      pathname === "/app" ||
      pathname === "/fp30x" ||
      pathname.endsWith(".html") ||
      pathname.startsWith("/static/")
    ) {
      const headers = new Headers(assetResp.headers);
      headers.set("cache-control", "no-store");
      headers.set("cdn-cache-control", "no-store");
      headers.delete("age");
      return new Response(assetResp.body, {
        status: assetResp.status,
        statusText: assetResp.statusText,
        headers,
      });
    }

    return assetResp;
  },
};
