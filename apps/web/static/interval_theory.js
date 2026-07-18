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

function intervalName(language, semitones) {
  const lang = language in INTERVAL_NAMES ? language : "es";
  return INTERVAL_NAMES[lang][semitones] || "-";
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
  INTERVAL_MELODIES,
  formatIntervalsFromMidi,
  intervalName,
  intervalSemitones,
  intervalMelodyNotes,
  intervalMelodySongName,
});
})(globalThis);
