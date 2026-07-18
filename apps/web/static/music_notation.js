(function initMusicNotation(global) {
  "use strict";

const NOTE_LABELS = {
  es: {
    sharp: ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
    flat: ["Do", "Re♭", "Re", "Mi♭", "Mi", "Fa", "Sol♭", "Sol", "La♭", "La", "Si♭", "Si"],
  },
  en: {
    sharp: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    flat: ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"],
  },
};

/**
 * Combo tónica dividido en Nota + Alteración: 7 letras naturales, cada una con
 * solo las alteraciones que corresponden a una de las 12 notas reales (no se
 * inventan enarmonías como Fb/Cb/E#/B# que no existen en NOTE_LABELS).
 */
const ROOT_LETTERS = [
  { es: "Do", en: "C", pc: 0 },
  { es: "Re", en: "D", pc: 2 },
  { es: "Mi", en: "E", pc: 4 },
  { es: "Fa", en: "F", pc: 5 },
  { es: "Sol", en: "G", pc: 7 },
  { es: "La", en: "A", pc: 9 },
  { es: "Si", en: "B", pc: 11 },
];
const ACCIDENTAL_SYMBOLS = { natural: "♮", sharp: "♯", flat: "♭" };
const ROOT_LETTER_ACCIDENTALS = {
  0: ["natural", "sharp"],
  2: ["flat", "natural", "sharp"],
  4: ["flat", "natural"],
  5: ["natural", "sharp"],
  7: ["flat", "natural", "sharp"],
  9: ["flat", "natural", "sharp"],
  11: ["flat", "natural"],
};
function rootPcFromLetterAccidental(letterPc, accidental) {
  const offset = accidental === "sharp" ? 1 : accidental === "flat" ? -1 : 0;
  return ((letterPc + offset) % 12 + 12) % 12;
}

const SHARP_KEY_SIGNATURES = ["F", "C", "G", "D", "A", "E", "B"];
const FLAT_KEY_SIGNATURES = ["B", "E", "A", "D", "G", "C", "F"];
const PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]; // convención sostenidos
const PC_TO_DIATONIC_FLAT   = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6]; // convención bemoles


function noteLabelFromPc(language, pc, preferFlat) {
  const lang = language === "en" ? "en" : "es";
  return NOTE_LABELS[lang][preferFlat ? "flat" : "sharp"][((pc % 12) + 12) % 12];
}

global.MidiChordsMusicNotation = Object.freeze({
  NOTE_LABELS,
  ROOT_LETTERS,
  ACCIDENTAL_SYMBOLS,
  ROOT_LETTER_ACCIDENTALS,
  SHARP_KEY_SIGNATURES,
  FLAT_KEY_SIGNATURES,
  PC_TO_DIATONIC_LETTER,
  PC_TO_DIATONIC_FLAT,
  rootPcFromLetterAccidental,
  noteLabelFromPc,
});
})(globalThis);
