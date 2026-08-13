(function initIntervalTheory(global) {
  "use strict";

function formatIntervalsFromMidi(notesMidi) {
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (ordered.length === 0) return "-";
  const result = ["0"];
  for (let i = 1; i < ordered.length; i++) {
    result.push(`+${ordered[i] - ordered[i - 1]}`);
  }
  return result.join(" ");
}

// Grado (con alteración respecto a la escala mayor) por semitonos desde la
// tónica, hasta 24 semitonos (2 octavas) para cubrir 9ª/11ª/13ª.
const DEGREE_BY_SEMITONE = {
  0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5", 7: "5",
  8: "#5", 9: "6", 10: "b7", 11: "7", 12: "8",
  13: "b9", 14: "9", 15: "#9", 17: "11", 18: "#11", 20: "b13", 21: "13",
};

// Calidad abreviada de un intervalo (par de notas consecutivas de un acorde)
// por semitonos, en notación estándar: P=justo, M=mayor, m=menor, TT=tritono.
const INTERVAL_QUALITY_BY_SEMITONE = {
  0: "P1", 1: "m2", 2: "M2", 3: "m3", 4: "M3", 5: "P4", 6: "TT", 7: "P5",
  8: "m6", 9: "M6", 10: "m7", 11: "M7", 12: "P8",
};

function intervalQualityAbbrev(semitones) {
  const value = Number(semitones);
  const octaves = Math.floor(value / 12);
  const base = INTERVAL_QUALITY_BY_SEMITONE[value - octaves * 12];
  if (!base) return `${value}st`;
  return octaves > 0 ? `${base}+${octaves * 12}` : base;
}

// Fórmula de grados de un acorde: p. ej. root_pc=0 (Do), notesMidi=[60,64,67] -> "1 3 5".
function chordFormulaFromRoot(rootPc, notesMidi) {
  const root = Number(rootPc);
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (!ordered.length || !Number.isFinite(root)) return "-";
  const rootMidi = ordered[0] - ((((ordered[0] % 12) - root) + 12) % 12);
  return ordered.map((n) => DEGREE_BY_SEMITONE[n - rootMidi] || `${n - rootMidi}st`).join(" ");
}

// Construcción de un acorde como intervalos apilados entre notas consecutivas:
// p. ej. Do-Mi-Sol -> "M3 + m3".
function chordConstructionFromMidi(notesMidi) {
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (ordered.length < 2) return "-";
  const parts = [];
  for (let i = 1; i < ordered.length; i++) {
    parts.push(intervalQualityAbbrev(ordered[i] - ordered[i - 1]));
  }
  return parts.join(" + ");
}

// Paso entre dos notas consecutivas de una escala en tonos (T) y semitonos (S):
// 1 -> "S", 2 -> "T", 3 -> "T+S", 4 -> "T+T", etc. (combinación de T's y, si es
// impar, una S final).
function scaleStepLabel(semitones) {
  const value = Number(semitones);
  if (value <= 0) return "";
  const tones = Math.floor(value / 2);
  const hasSemitone = value % 2 === 1;
  const parts = Array(tones).fill("T");
  if (hasSemitone) parts.push("S");
  return parts.join("+");
}

// Patrón T/S de una escala a partir de sus notas MIDI ordenadas:
// p. ej. Do jónico [60,62,64,65,67,69,71,72] -> "T T S T T T S".
function scalePatternFromMidi(notesMidi) {
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (ordered.length < 2) return "-";
  const parts = [];
  for (let i = 1; i < ordered.length; i++) {
    parts.push(scaleStepLabel(ordered[i] - ordered[i - 1]));
  }
  return parts.join(" ");
}

// Grado diatónico (1-7) por semitonos desde la tónica, para escalas. A
// diferencia de DEGREE_BY_SEMITONE (pensada para acordes, donde 8 semitonos
// se interpreta como quinta aumentada), aquí cada semitono siempre resuelve a
// una alteración del grado numérico correspondiente (8 semitonos -> ♭6, no ♯5).
const SCALE_DEGREE_BY_SEMITONE = {
  0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5",
  7: "5", 8: "b6", 9: "6", 10: "b7", 11: "7", 12: "8",
};

// Fórmula de grados de una escala a partir de sus notas MIDI ordenadas:
// p. ej. Do jónico -> "1 2 3 4 5 6 7".
function scaleFormulaFromMidi(notesMidi) {
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (!ordered.length) return "-";
  const rootMidi = ordered[0];
  // La nota final (octava) no se cuenta como grado nuevo en la fórmula.
  const degreeNotes = ordered.length > 1 && ordered[ordered.length - 1] - rootMidi === 12
    ? ordered.slice(0, -1)
    : ordered;
  return degreeNotes.map((n) => SCALE_DEGREE_BY_SEMITONE[n - rootMidi] || `${n - rootMidi}st`).join(" ");
}

// Reconstruye el voicing en posición fundamental (raíz en el bajo, resto apilado
// ascendente) a partir de las pitch-classes presentes en un voicing invertido.
function rootPositionVoicing(rootPc, notesMidi) {
  const root = ((Number(rootPc) % 12) + 12) % 12;
  const pcs = Array.from(new Set((notesMidi || []).map((n) => ((Number(n) % 12) + 12) % 12)));
  const offsets = pcs.map((pc) => ((pc - root) + 12) % 12).sort((a, b) => a - b);
  return offsets.map((offset) => 60 + offset);
}

// Rota una fórmula "1 - 3 - 5" tantas posiciones como indique el índice de
// inversión: inversion=1 -> "3 - 5 - 1".
function rotateDegrees(formula, inversion) {
  const degrees = String(formula || "").split(" - ").filter(Boolean);
  if (!degrees.length) return formula;
  const idx = Math.max(0, Math.min(Number(inversion) || 0, degrees.length - 1));
  return degrees.slice(idx).concat(degrees.slice(0, idx)).join(" - ");
}

const INTERVAL_NAMES = {
  es: {
    0: "Unísono justo", 1: "Segunda menor", 2: "Segunda mayor",
    3: "Tercera menor", 4: "Tercera mayor", 5: "Cuarta justa",
    6: "Cuarta aum. / Quinta dim.", 7: "Quinta justa",
    8: "Sexta menor", 9: "Sexta mayor", 10: "Séptima menor",
    11: "Séptima mayor", 12: "Octava justa",
  },
  en: {
    0: "Perfect Unison", 1: "Minor Second", 2: "Major Second",
    3: "Minor Third", 4: "Major Third", 5: "Perfect Fourth",
    6: "Aug. Fourth / Dim. Fifth", 7: "Perfect Fifth",
    8: "Minor Sixth", 9: "Major Sixth", 10: "Minor Seventh",
    11: "Major Seventh", 12: "Perfect Octave",
  },
};

// Nombres enarmónicos alternativos por semitono (excluyendo el nombre principal
// de INTERVAL_NAMES). No todos los semitonos tienen alternativas de uso común.
const INTERVAL_ALT_NAMES = {
  es: {
    0: ["Segunda disminuida"],
    1: ["Unísono aumentado"],
    2: ["Tercera disminuida"],
    3: ["Segunda aumentada"],
    4: ["Cuarta disminuida"],
    5: ["Tercera aumentada"],
    6: ["Tritono"],
    7: ["Sexta disminuida"],
    8: ["Quinta aumentada"],
    9: ["Séptima disminuida"],
    10: ["Sexta aumentada"],
    11: ["Octava disminuida"],
    12: ["Séptima aumentada"],
  },
  en: {
    0: ["Diminished Second"],
    1: ["Augmented Unison"],
    2: ["Diminished Third"],
    3: ["Augmented Second"],
    4: ["Diminished Fourth"],
    5: ["Augmented Third"],
    6: ["Tritone"],
    7: ["Diminished Sixth"],
    8: ["Augmented Fifth"],
    9: ["Diminished Seventh"],
    10: ["Augmented Sixth"],
    11: ["Diminished Octave"],
    12: ["Augmented Seventh"],
  },
};

// durations: "w"=redonda  "h"=blanca  "q"=negra  "e"=corchea  "s"=semicorchea
//            Añadir "." para puntillo. null=silencio
// jumpAt: índice donde ocurre el intervalo (por defecto 0 = salto entre notas 0 y 1)
const INTERVAL_MELODIES = {
  1:  { name_es: "Tiburón (Jaws)",             name_en: "Jaws Theme",
        beatsPerBar: 4,
        showFull: true,
        accent: true,
        beams: [[0, 7]],
        offsets:   [0, 1, 0, 1, 0, 1, 0, 1],
        durations: ["e","e","e","e","e","e","e","e"] },

  2:  { name_es: "Cumpleaños feliz",            name_en: "Happy Birthday",
        beatsPerBar: 3, anacrusis: 1,
        jumpAt: 1,
        beams: [[0, 1]],
        offsets:   [0, 0, 2, 0, 5, 4],
        durations: ["e.","s","q","q","q","h"] },

  3:  { name_es: "Smoke on the Water",          name_en: "Smoke on the Water",
        beatsPerBar: 4,
        offsets:   [0, 3, 5, null, 0, null, 3, 6, 5],
        durations: ["q","q","q","e","e","e","q","e","h"] },

  4:  { name_es: "When the Saints Go Marching In", name_en: "When the Saints Go Marching In",
        beatsPerBar: 4, anacrusis: 1,
        playbackStepMs: 320,
        offsets:   [0, 4, 5, 7],
        durations: ["q","q","q","w"] },

  5:  { name_es: "Here Comes the Bride",  name_en: "Here Comes the Bride",
        beatsPerBar: 4,
        jumpAt: 3,
        setupSlur: false,
        highlightUntil: 1,
        offsets:   [0, 5, 5, 5, 0, 7, 4, 5],
        durations: ["q","e.","s","h","q","e.","s","h"] },

  6:  { name_es: "María (West Side Story)",     name_en: "Maria (West Side Story)",
        beatsPerBar: 3,
        setupSlur: false,
        offsets:   [0, 6, 7, 4, 0, -5],
        durations: ["q.","e","h","q","q","h"] },

  7:  { name_es: "Star Wars",                   name_en: "Star Wars",
        beatsPerBar: 4,
        beams: [[2, 3, 4]],
        tuplets: [[2, 3, 4]],
        offsets:   [0, 7, 5, 4, 2, 12, 7],
        durations: ["h","h","et","et","et","h","q"] },

  8:  { name_es: "Love Story",                 name_en: "Love Story",
        beatsPerBar: 4, anacrusis: 1,
        playbackStepMs: 520,
        highlightUntil: 2,
        offsets:   [0, 0, 8, 8, 0, 1, 0, -2],
        durations: ["e","e","e","e","e","e","e","e"] },

  9:  { name_es: "My Way",                      name_en: "My Way",
        beatsPerBar: 4, anacrusis: 1.5,
        offsets:   [0, 9, 7, 9],
        durations: ["e","e","e","h"] },

  10: { name_es: "Somewhere (West Side Story)", name_en: "Somewhere (West Side Story)",
        beatsPerBar: 4,
        offsets:   [0, 10, 9, 5, 2],
        durations: ["h","h","q.","e","h"] },

  11: { name_es: "Take On Me",                  name_en: "Take On Me",
        beatsPerBar: 4,
        offsets:   [0, 11, 12],
        durations: ["h","h","h"] },

  12: { name_es: "Somewhere Over the Rainbow",  name_en: "Somewhere Over the Rainbow",
        beatsPerBar: 4,
        offsets:   [0, 12, 11, 7, 9, 11, 12],
        durations: ["h","h","q","e","e","q","q"] },
};

// Matriz de la tabla de Generación de Intervalos: cada columna agrupa
// intervalos de la misma categoría (disminuida/menor/mayor/justa/aumentada).
// cellsBySemitone mapea semitono -> { short, name: {es, en} } en esa columna;
// los semitonos ausentes no tienen intervalo válido en esa columna (celda vacía).
const INTERVAL_GRID_COLUMNS = [
  {
    key: "diminished",
    title: { es: "Disminuidas", en: "Diminished" },
    cellsBySemitone: {
      0: { short: "d2", name: { es: "Segunda disminuida", en: "Diminished Second" } },
      2: { short: "d3", name: { es: "Tercera disminuida", en: "Diminished Third" } },
      4: { short: "d4", name: { es: "Cuarta disminuida", en: "Diminished Fourth" } },
      6: { short: "d5", name: { es: "Quinta disminuida", en: "Diminished Fifth" } },
      7: { short: "d6", name: { es: "Sexta disminuida", en: "Diminished Sixth" } },
      9: { short: "d7", name: { es: "Séptima disminuida", en: "Diminished Seventh" } },
      11: { short: "d8", name: { es: "Octava disminuida", en: "Diminished Octave" } },
    },
  },
  {
    key: "minor",
    title: { es: "Menores", en: "Minor" },
    cellsBySemitone: {
      1: { short: "m2", name: { es: "Segunda menor", en: "Minor Second" } },
      3: { short: "m3", name: { es: "Tercera menor", en: "Minor Third" } },
      8: { short: "m6", name: { es: "Sexta menor", en: "Minor Sixth" } },
      10: { short: "m7", name: { es: "Séptima menor", en: "Minor Seventh" } },
    },
  },
  {
    key: "major",
    title: { es: "Mayores", en: "Major" },
    cellsBySemitone: {
      2: { short: "M2", name: { es: "Segunda mayor", en: "Major Second" } },
      4: { short: "M3", name: { es: "Tercera mayor", en: "Major Third" } },
      9: { short: "M6", name: { es: "Sexta mayor", en: "Major Sixth" } },
      11: { short: "M7", name: { es: "Séptima mayor", en: "Major Seventh" } },
    },
  },
  {
    key: "perfect",
    title: { es: "Justas", en: "Perfect" },
    cellsBySemitone: {
      0: { short: "P1", name: { es: "Unísono justo", en: "Perfect Unison" } },
      5: { short: "P4", name: { es: "Cuarta justa", en: "Perfect Fourth" } },
      7: { short: "P5", name: { es: "Quinta justa", en: "Perfect Fifth" } },
      12: { short: "P8", name: { es: "Octava justa", en: "Perfect Octave" } },
    },
  },
  {
    key: "augmented",
    title: { es: "Aumentadas", en: "Augmented" },
    cellsBySemitone: {
      1: { short: "A1", name: { es: "Unísono aumentado", en: "Augmented Unison" } },
      3: { short: "A2", name: { es: "Segunda aumentada", en: "Augmented Second" } },
      5: { short: "A3", name: { es: "Tercera aumentada", en: "Augmented Third" } },
      6: { short: "A4", name: { es: "Cuarta aumentada", en: "Augmented Fourth" } },
      8: { short: "A5", name: { es: "Quinta aumentada", en: "Augmented Fifth" } },
      10: { short: "A6", name: { es: "Sexta aumentada", en: "Augmented Sixth" } },
      12: { short: "A7", name: { es: "Séptima aumentada", en: "Augmented Seventh" } },
    },
  },
];

/** Nombre completo de una celda concreta (columnKey + semitono), o null si no existe. */
function intervalGridCellName(language, columnKey, semitones) {
  const col = INTERVAL_GRID_COLUMNS.find((c) => c.key === columnKey);
  const cell = col && col.cellsBySemitone[semitones];
  if (!cell) return null;
  return cell.name[language] || cell.name.es;
}

/** Todos los nombres completos válidos (de cualquier columna) para un semitono dado. */
function intervalGridNamesForSemitones(language, semitones) {
  const lang = language in INTERVAL_ALT_NAMES ? language : "es";
  const names = [];
  INTERVAL_GRID_COLUMNS.forEach((col) => {
    const cell = col.cellsBySemitone[semitones];
    if (cell) names.push(cell.name[language] || cell.name.es);
  });
  (INTERVAL_ALT_NAMES[lang][semitones] || []).forEach((name) => names.push(name));
  return Array.from(new Set(names));
}

function intervalName(language, semitones) {
  const lang = language in INTERVAL_NAMES ? language : "es";
  return INTERVAL_NAMES[lang][semitones] || "-";
}

function intervalAltNames(language, semitones) {
  const lang = language in INTERVAL_ALT_NAMES ? language : "es";
  return INTERVAL_ALT_NAMES[lang][semitones] || [];
}

function intervalSemitones(notes) {
  const n = notes || [];
  if (n.length < 2) return null;
  const raw = Math.abs(n[1] - n[0]);
  const mod = raw % 12;
  return (mod === 0 && raw > 0) ? 12 : mod;
}

function intervalMelodyNotes(notes) {
  const values = notes || [];
  if (values.length < 2) return [...values].sort((a, b) => a - b);
  const semitones = intervalSemitones(values);
  const melody = INTERVAL_MELODIES[semitones];
  if (!melody) return [...values].sort((a, b) => a - b);
  const base = Math.min(...values);
  // Mapear a null en vez de filtrar: preserva longitud de array y alineación con durations[]
  return melody.offsets.map((offset) => {
    if (offset === null) return null;
    const n = base + offset;
    return (n >= 0 && n <= 127) ? n : null;
  });
}

function intervalMelodySongName(language, notes) {
  const semitones = intervalSemitones(notes);
  if (semitones === null) return null;
  const entry = INTERVAL_MELODIES[semitones];
  if (!entry) return null;
  return language === "en" ? entry.name_en : entry.name_es;
}


global.MidiChordsIntervalTheory = Object.freeze({
  INTERVAL_NAMES,
  INTERVAL_ALT_NAMES,
  INTERVAL_MELODIES,
  INTERVAL_GRID_COLUMNS,
  formatIntervalsFromMidi,
  chordFormulaFromRoot,
  chordConstructionFromMidi,
  rootPositionVoicing,
  rotateDegrees,
  scaleFormulaFromMidi,
  scalePatternFromMidi,
  intervalName,
  intervalAltNames,
  intervalSemitones,
  intervalMelodyNotes,
  intervalMelodySongName,
  intervalGridCellName,
  intervalGridNamesForSemitones,
});
})(globalThis);
