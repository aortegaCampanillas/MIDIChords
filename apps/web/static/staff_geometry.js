(function initStaffGeometry(global) {
  "use strict";

  const {
    PC_TO_DIATONIC_LETTER,
    PC_TO_DIATONIC_FLAT,
  } = global.MidiChordsMusicNotation;

  function midiToDiatonicIndex(midi, preferFlat = false) {
    const note = Number(midi);
    if (!Number.isFinite(note)) return null;
    const pc = ((note % 12) + 12) % 12;
    const octave = Math.floor(note / 12) - 1;
    const map = preferFlat ? PC_TO_DIATONIC_FLAT : PC_TO_DIATONIC_LETTER;
    return (octave * 7) + map[pc];
  }

  function midiToTrebleY(midi, trebleTop, gap, preferFlat = false) {
    const diatonicIndex = midiToDiatonicIndex(midi, preferFlat);
    if (diatonicIndex == null) return Number(trebleTop);
    const trebleBottomLineDiatonic = (4 * 7) + 2; // E4
    return Number(trebleTop) + (4 * Number(gap))
      - ((diatonicIndex - trebleBottomLineDiatonic) * (Number(gap) / 2));
  }

  function midiToBassY(midi, bassTop, gap, preferFlat = false) {
    const diatonicIndex = midiToDiatonicIndex(midi, preferFlat);
    if (diatonicIndex == null) return Number(bassTop);
    const bassBottomLineDiatonic = (2 * 7) + 4; // G2
    return Number(bassTop) + (4 * Number(gap))
      - ((diatonicIndex - bassBottomLineDiatonic) * (Number(gap) / 2));
  }

  function ledgerLineYs(noteY, staffTop, gap) {
    const y = Number(noteY);
    const top = Number(staffTop);
    const spacing = Number(gap);
    if (![y, top, spacing].every(Number.isFinite) || spacing <= 0) return [];
    const bottom = top + (spacing * 4);
    const lines = [];
    if (y < top - 1) {
      for (let lineY = top - spacing; lineY >= y - 1; lineY -= spacing) lines.push(lineY);
    } else if (y > bottom + 1) {
      for (let lineY = bottom + spacing; lineY <= y + 1; lineY += spacing) lines.push(lineY);
    }
    return lines;
  }

  global.MidiChordsStaffGeometry = Object.freeze({
    midiToDiatonicIndex,
    midiToTrebleY,
    midiToBassY,
    ledgerLineYs,
  });
})(globalThis);
