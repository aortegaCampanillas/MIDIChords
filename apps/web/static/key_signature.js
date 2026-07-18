(function initKeySignature(global) {
  "use strict";

function keySignatureSharpFlatCounts(tonicPc, isMinor) {
  const pc = ((Number(tonicPc) % 12) + 12) % 12;
  const sharpMap = isMinor
    ? { 4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7 }
    : { 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7 };
  const flatMap = isMinor
    ? { 2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6 }
    : { 5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6 };
  return { pc, sharpCount: sharpMap[pc], flatCount: flatMap[pc] };
}

/** Misma regla que el nombre del acorde en API/worker: menos alteraciones; empate → bemoles. */
function chordSymbolPreferFlat(rootPc, isMinor) {
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(rootPc, isMinor);
  if (sharpCount == null && flatCount == null) return false;
  if (sharpCount == null) return true;
  if (flatCount == null) return false;
  if (flatCount < sharpCount) return true;
  if (sharpCount < flatCount) return false;
  return true;
}

// tiePreferFlat: null/undefined → empate enarmónico a sostenidos. true/false → empate explícito (#/♭ o convención armónica).
function keySignatureCountForTonic(tonicPc, isMinor, tiePreferFlat = null) {
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(tonicPc, isMinor);
  if (sharpCount == null && flatCount == null) return { count: 0, preferFlats: false };
  if (sharpCount == null) return { count: flatCount, preferFlats: true };
  if (flatCount == null) return { count: sharpCount, preferFlats: false };
  if (flatCount < sharpCount) return { count: flatCount, preferFlats: true };
  if (sharpCount < flatCount) return { count: sharpCount, preferFlats: false };
  if (tiePreferFlat === true) return { count: flatCount, preferFlats: true };
  return { count: sharpCount, preferFlats: false };
}

/** Empate enarmónico (mismo nº de # y ♭): armadura bemol si el usuario eligió ♭ en el desplegable. */
function applyFlatKeySignatureTie(sig, tonicPc, isMinor, preferFlat) {
  if (!preferFlat) return sig;
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(tonicPc, isMinor);
  if (sharpCount != null && flatCount != null && sharpCount === flatCount) {
    return { count: flatCount, preferFlats: true };
  }
  return sig;
}

function keySignatureIndexForMidi(midi, sig) {
  if (!sig || !Number(sig.count) || !Number.isFinite(Number(midi))) return -1;
  const pc = ((Number(midi) % 12) + 12) % 12;
  const order = sig.preferFlats
    ? [10, 3, 8, 1, 6, 11, 4]
    : [6, 1, 8, 3, 10, 5, 0];
  const index = order.indexOf(pc);
  return index >= 0 && index < Number(sig.count) ? index : -1;
}

function isMinorSuffix(suffix) {
  return String(suffix || "").startsWith("m") && !String(suffix || "").startsWith("maj");
}

function scalePrefersMinor(patternName) {
  const minorNames = new Set([
    "Aeolian",
    "Dorian",
    "Phrygian",
    "Locrian",
    "Super Locrian",
    "Half Diminished",
    "Minor Pentatonic",
    "Minor Blues",
    "Dorian b2",
  ]);
  return String(patternName || "").includes("Minor") || minorNames.has(String(patternName || ""));
}

// Semitonos que hay que SUMAR a la tónica del modo para llegar a su mayor
// relativo real (el que comparte exactamente las mismas notas). Verificado
// nota a nota: Do Dórico = Sib Mayor (+10), Do Frigio = Lab Mayor (+8), Do
// Locrio = Reb Mayor (+1), Do Eolio = Mib Mayor (+3, ya era el
// comportamiento previo/correcto), Fa Lidio = Do Mayor (+7), Sol
// Mixolidio = Do Mayor (+5). Ionian/Mayor no necesita entrada (offset 0).
// Sin esto, cada modo "no jónico" heredaba o bien la armadura del menor
// natural (los de sabor menor) o la de su propia tónica como si fuera
// Mayor normal (los de sabor mayor: Lidio, Mixolidio), ambas incorrectas
// salvo casualidad.
const MODE_RELATIVE_MAJOR_OFFSET = {
  Dorian: 10,
  Phrygian: 8,
  Locrian: 1,
  Aeolian: 3,
  Lydian: 7,
  Mixolydian: 5,
  Minor: 3,
  "Natural Minor": 3,
  "Minor Pentatonic": 3,
  "Minor Blues": 3,
};


global.MidiChordsKeySignature = Object.freeze({
  MODE_RELATIVE_MAJOR_OFFSET,
  keySignatureSharpFlatCounts,
  chordSymbolPreferFlat,
  keySignatureCountForTonic,
  applyFlatKeySignatureTie,
  keySignatureIndexForMidi,
  isMinorSuffix,
  scalePrefersMinor,
});
})(globalThis);
