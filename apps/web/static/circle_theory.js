(function initCircleTheory(global) {
  "use strict";

/** Sentido horario desde arriba (Do), avanzando de quinta en quinta. */
const CIRCLE_FIFTHS_ORDER = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5];

const DIATONIC_DEGREE_SUFFIX = {
  0: "",
  2: "m",
  4: "m",
  5: "",
  7: "",
  9: "m",
  11: "dim",
};

const ROMAN_BY_DEGREE = {
  0: "I",
  2: "ii",
  4: "iii",
  5: "IV",
  7: "V",
  9: "vi",
  11: "vii°",
};

/**
 * Fondos diatónicos (referencia visual): mayor = melocotón claro; tónica I = beige/marrón más oscuro;
 * menor = lavanda claro; vii° = rosa pálido (como en la maqueta del círculo).
 */
const CIRCLE_DEGREE_FILL = {
  0: { base: "#f0d5b8", tonic: "#c9a06a" },
  2: "#ddd0e8",
  4: "#ddd0e8",
  5: "#f0d5b8",
  7: "#f0d5b8",
  9: "#ddd0e8",
  11: "#f5d4dc",
};

/** Texto diatónico: I/vi verde; IV/ii azul; V/iii/vii° rojo (legible sobre fondos claros). */
const CIRCLE_DEGREE_TEXT = {
  0: "#1b5e20",
  2: "#0d47a1",
  4: "#b71c1c",
  5: "#1565c0",
  7: "#c62828",
  9: "#2e7d32",
  11: "#c62828",
};

function diatonicTriadSuffixMajorKey(tonicPc, rootPc) {
  const d = (rootPc - tonicPc + 12) % 12;
  if (Object.prototype.hasOwnProperty.call(DIATONIC_DEGREE_SUFFIX, d)) {
    return { suffix: DIATONIC_DEGREE_SUFFIX[d], degree: d };
  }
  return { suffix: "", degree: null };
}

/**
 * Triadas diatónicas en tonalidad menor natural (intervalos desde la tónica menor).
 * III/VI/VII como ♭ respecto a la mayor paralela (p. ej. en Lam: Do = ♭III).
 */
const ROMAN_BY_MINOR_NATURAL_INTERVAL = {
  0: "i",
  2: "ii°",
  3: "\u266DIII",
  5: "iv",
  7: "v",
  8: "\u266DVI",
  10: "\u266DVII",
};

/** En canvas, dibuja numerales con el bem (\u266D) en superíndice respecto al número romano. */
function fillTextRomanMaybeFlatSuperscript(ctx, roman, x, y, fsRoman) {
  const ff = `"Avenir Next", "Segoe UI", sans-serif`;
  const flat = "\u266D";
  if (!roman) return;
  if (roman.charAt(0) !== flat) {
    ctx.font = `${fsRoman}px ${ff}`;
    ctx.fillText(roman, x, y);
    return;
  }
  const body = roman.slice(1);
  const supFs = Math.max(7, Math.round(fsRoman * 0.58));
  const rise = Math.round(fsRoman * 0.4);
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";
  ctx.font = `${supFs}px ${ff}`;
  const wFlat = ctx.measureText(flat).width;
  ctx.font = `${fsRoman}px ${ff}`;
  const wBody = ctx.measureText(body).width;
  const gap = Math.max(2, Math.round(fsRoman * 0.14));
  const total = wFlat + gap + wBody;
  let drawX = x - total / 2;
  ctx.font = `${supFs}px ${ff}`;
  ctx.fillText(flat, drawX, y - rise);
  drawX += wFlat + gap;
  ctx.font = `${fsRoman}px ${ff}`;
  ctx.fillText(body, drawX, y);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
}

function diatonicTriadSuffixNaturalMinorKey(minorTonicPc, rootPc) {
  const d = (rootPc - minorTonicPc + 12) % 12;
  const MAP = {
    0: { suffix: "m" },
    2: { suffix: "dim" },
    3: { suffix: "" },
    5: { suffix: "m" },
    7: { suffix: "m" },
    8: { suffix: "" },
    10: { suffix: "" },
  };
  if (!Object.prototype.hasOwnProperty.call(MAP, d)) {
    return { suffix: "", interval: null, roman: "" };
  }
  return {
    suffix: MAP[d].suffix,
    interval: d,
    roman: ROMAN_BY_MINOR_NATURAL_INTERVAL[d] || "",
  };
}

/**
 * Mapea intervalo menor natural → clave de grado mayor para CIRCLE_DEGREE_TEXT / rellenos.
 * VII comparte lavanda con III/VI (no el rosa de vii°); ii° usa el rosa de grado 11.
 */
function circleMinorIntervalToMajorDegreeKey(intervalD) {
  const map = { 0: 0, 2: 11, 3: 4, 5: 5, 7: 7, 8: 9, 10: 9 };
  return map[intervalD] !== undefined ? map[intervalD] : 0;
}

function circleDiatonicSliceFill(degree, pc, tonicPc) {
  if (degree === 0) {
    return pc === tonicPc ? CIRCLE_DEGREE_FILL[0].tonic : CIRCLE_DEGREE_FILL[0].base;
  }
  return CIRCLE_DEGREE_FILL[degree];
}

/** En el anillo mayor del sector solo la triada mayor I, IV o V es la función diatónica (no Re mayor = ii ni Si mayor = vii°). */
function circleUpperBandIsDiatonicMajorTriad(degree) {
  return degree === 0 || degree === 5 || degree === 7;
}

/** El anillo inferior muestra la menor relativa; ii/iii/vi coinciden con Rem/Mim/Lam en los sectores correctos. */
function circleLowerBandIsDiatonicMinorTriad(minorDeg) {
  return minorDeg === 2 || minorDeg === 4 || minorDeg === 9;
}

/** Índice 0..11 en orden de quintas (C arriba): 0–6 → #, 7–11 → ♭. */
function circleSignatureLabelForSliceIndex(i) {
  if (i <= 6) {
    const n = i;
    if (n === 0) return "0";
    return `${n}♯`;
  }
  const fb = 12 - i;
  return `${fb}♭`;
}

/** Menor relativa de una mayor (ej. Do → La). */
function relativeMinorPcFromMajorPc(majorPc) {
  return (Number(majorPc) + 9 + 12) % 12;
}

function circleFifthsRadiiPx(w, h) {
  const rOuter = Math.min(w, h) * 0.46;
  const rHole = rOuter * 0.18;
  /** Anillo de ♯/♭: mitad del ancho que tenía la franja exterior respecto a la guía antigua (0.775·R). */
  const rGuideSigMajRef = rOuter * 0.775;
  const bandSig = (rOuter - rGuideSigMajRef) / 2;
  const rSigInner = rOuter - bandSig;
  const rSig = (rOuter + rSigInner) / 2;
  /** Frontera mayor/menor: más cerca del centro → anillo mayor más estrecho y anillo menor más ancho (menos solape de textos). */
  const rGuideMajMin = rOuter * 0.52;
  return {
    rOuter,
    rHole,
    rSigInner,
    rSig,
    rMajName: rOuter * 0.72,
    rMajRoman: rOuter * 0.60,
    rMin: rOuter * 0.38,
    /** Romano bajo el nombre menor; más hacia el centro del anillo menor que el agujero. */
    rMinRoman: rOuter * 0.292,
    /** Líneas entre anillo de armadura / mayor / menor. */
    rGuideSigMaj: rSigInner,
    rGuideMajMin,
  };
}

const CIRCLE_SLICE_RAD = (Math.PI * 2) / 12;

/** Do (índice 0) con eje en el norte (−90°); cada sector centrado en −90° + i·30°. */
function circleSliceAngles(index) {
  const mid = (-Math.PI / 2) + (index * CIRCLE_SLICE_RAD);
  const half = CIRCLE_SLICE_RAD / 2;
  return { mid, a0: mid - half, a1: mid + half };
}

function circleSliceIndexFromCanvas(cx, cy, x, y) {
  const angle = Math.atan2(y - cy, x - cx);
  const normalized = (angle + Math.PI / 2 + Math.PI * 2) % (Math.PI * 2);
  return Math.floor((normalized + CIRCLE_SLICE_RAD / 2) / CIRCLE_SLICE_RAD) % 12;
}

function pitchClassFromCircleClick(cx, cy, x, y) {
  return CIRCLE_FIFTHS_ORDER[circleSliceIndexFromCanvas(cx, cy, x, y)];
}

function circleClickInfo(canvasW, canvasH, cx, cy, x, y) {
  const distance = Math.hypot(x - cx, y - cy);
  const { rOuter, rHole, rGuideMajMin } = circleFifthsRadiiPx(canvasW, canvasH);
  if (distance < rHole * 1.02 || distance > rOuter * 1.02) return null;
  const sliceIdx = circleSliceIndexFromCanvas(cx, cy, x, y);
  return {
    sliceIdx,
    majorPc: CIRCLE_FIFTHS_ORDER[sliceIdx],
    innerMinorBand: distance < rGuideMajMin,
  };
}

function circleChordRootPcFromClick(canvasW, canvasH, cx, cy, x, y) {
  const click = circleClickInfo(canvasW, canvasH, cx, cy, x, y);
  if (!click) return null;
  return click.innerMinorBand ? relativeMinorPcFromMajorPc(click.majorPc) : click.majorPc;
}

function circleChordShiftClickIsDiatonic(
  tonicPc,
  canvasW,
  canvasH,
  cx,
  cy,
  x,
  y,
  keyMode = "major",
  circleTonicPc = tonicPc,
) {
  const click = circleClickInfo(canvasW, canvasH, cx, cy, x, y);
  if (!click) return false;
  const { majorPc, innerMinorBand } = click;
  if (keyMode === "minor") {
    const minorTonic = ((Number(circleTonicPc) % 12) + 12) % 12;
    if (!innerMinorBand) return [3, 8, 10].includes((majorPc - minorTonic + 12) % 12);
    return diatonicTriadSuffixNaturalMinorKey(
      minorTonic,
      relativeMinorPcFromMajorPc(majorPc),
    ).interval != null;
  }
  const viiRootPc = chordRootPcForMajorScaleDegree(tonicPc, 11);
  const viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
  if (!innerMinorBand) {
    const { degree } = diatonicTriadSuffixMajorKey(tonicPc, majorPc);
    return degree != null && circleUpperBandIsDiatonicMajorTriad(degree);
  }
  const rootMinor = relativeMinorPcFromMajorPc(majorPc);
  const { degree: minorDegree } = diatonicTriadSuffixMajorKey(tonicPc, rootMinor);
  if (minorDegree != null && circleLowerBandIsDiatonicMinorTriad(minorDegree)) return true;
  return minorDegree === 11 && majorPc === viiLabelSlicePc;
}

function circleFifthsClickInnerMinorBand(canvasW, canvasH, cx, cy, x, y) {
  const click = circleClickInfo(canvasW, canvasH, cx, cy, x, y);
  return click ? click.innerMinorBand : null;
}

function circleChordHighlightGeom(
  tonicPc,
  chordRootPc,
  generatedChord,
  keyMode = "major",
  circleTonicPc = tonicPc,
) {
  const rootFromState = ((Number(chordRootPc) % 12) + 12) % 12;
  const rootFromApi = generatedChord != null && generatedChord.root_pc != null
    ? ((Number(generatedChord.root_pc) % 12) + 12) % 12
    : null;
  const root = rootFromApi != null ? rootFromApi : rootFromState;
  let suffix = generatedChord?.suffix != null ? String(generatedChord.suffix) : "";
  if (suffix === "" || suffix === "undefined") {
    suffix = keyMode === "minor"
      ? diatonicTriadSuffixNaturalMinorKey(circleTonicPc, root).suffix || ""
      : diatonicTriadSuffixMajorKey(tonicPc, root).suffix || "";
  }
  if (suffix === "m") {
    return { sliceIdx: circleSliceIndexForPitchClass((root - 9 + 12) % 12), band: "minor" };
  }
  if (suffix === "dim") {
    return { sliceIdx: circleSliceIndexForPitchClass((root + 3) % 12), band: "minor" };
  }
  return { sliceIdx: circleSliceIndexForPitchClass(root), band: "major" };
}

function circleSliceIndexForPitchClass(pc) {
  const p = ((pc % 12) + 12) % 12;
  for (let i = 0; i < 12; i += 1) {
    if (CIRCLE_FIFTHS_ORDER[i] === p) return i;
  }
  return 0;
}

/** Raíz del acorde diatónico en tonalidad mayor (I, ii, iii, IV, V, vi, vii°). */
function chordRootPcForMajorScaleDegree(tonicPc, degree) {
  const inter = { 0: 0, 2: 2, 4: 4, 5: 5, 7: 7, 9: 9, 11: 11 };
  return (((tonicPc + inter[degree]) % 12) + 12) % 12;
}

/**
 * Arco entre dos ángulos en r: elige tramo corto o largo según preferNorth (−sin) o sur (+sin).
 * Usado para el arco superior IV–I–V (pasar por el norte, por encima de Do).
 */
function circlePathArc(ctx, r, aFrom, aTo, preferNorth) {
  let d = aTo - aFrom;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const shortSweep = d > Math.PI ? Math.PI * 2 - d : d;
  const longSweep = Math.PI * 2 - shortSweep;
  const midShort = aFrom + shortSweep / 2;
  const midLong = aFrom + longSweep / 2;
  const scoreNorth = (a) => -Math.sin(a);
  const scoreSouth = (a) => Math.sin(a);
  const score = preferNorth ? scoreNorth : scoreSouth;
  const sweep = score(midLong) > score(midShort) ? longSweep : shortSweep;
  const steps = 40;
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = aFrom + sweep * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/**
 * Arco en rHole entre dos ángulos: tramo por la parte inferior (Mi, Si, Fa#…),
 * coherente con ii–iii–vi en el anillo interior.
 */
function circlePathArcHoleBottom(ctx, r, aFrom, aTo) {
  let d = aTo - aFrom;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const shortSweep = d > Math.PI ? Math.PI * 2 - d : d;
  const longSweep = Math.PI * 2 - shortSweep;
  function avgSin(sweep) {
    let s = 0;
    for (let k = 0; k <= 16; k += 1) {
      const t = k / 16;
      const ang = aFrom + sweep * t;
      s += Math.sin(ang);
    }
    return s / 17;
  }
  const sweep = avgSin(longSweep) > avgSin(shortSweep) ? longSweep : shortSweep;
  const steps = 40;
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = aFrom + sweep * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/** Arco en r constante de ang0 a ang1 (recorrido corto positivo, hasta 2π). */
function circlePathArcSpan(ctx, r, ang0, ang1) {
  let d = ang1 - ang0;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const steps = Math.max(8, Math.min(64, Math.ceil(48 * d / (Math.PI * 2))));
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = ang0 + d * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/**
 * Perímetro de la unión de celdas diatónicas en la grilla (3 radios × 12 sectores):
 * solo aristas de celda (arcos en rHole, rGuideMajMin, rSigInner y radiales en límites de sector).
 * Diferencia simétrica de aristas → borde de la unión (mínimo en el sentido de perímetro de polígono ortogonal).
 * Esquina superior izquierda del IV = vértice (radial del a0 del IV, banda rSigInner).
 */

global.MidiChordsCircleTheory = Object.freeze({
  CIRCLE_FIFTHS_ORDER,
  ROMAN_BY_DEGREE,
  CIRCLE_DEGREE_FILL,
  CIRCLE_DEGREE_TEXT,
  ROMAN_BY_MINOR_NATURAL_INTERVAL,
  diatonicTriadSuffixMajorKey,
  fillTextRomanMaybeFlatSuperscript,
  diatonicTriadSuffixNaturalMinorKey,
  circleMinorIntervalToMajorDegreeKey,
  circleDiatonicSliceFill,
  circleUpperBandIsDiatonicMajorTriad,
  circleLowerBandIsDiatonicMinorTriad,
  circleSignatureLabelForSliceIndex,
  relativeMinorPcFromMajorPc,
  circleFifthsRadiiPx,
  circleSliceAngles,
  circleSliceIndexFromCanvas,
  pitchClassFromCircleClick,
  circleChordRootPcFromClick,
  circleChordShiftClickIsDiatonic,
  circleFifthsClickInnerMinorBand,
  circleChordHighlightGeom,
  circleSliceIndexForPitchClass,
  chordRootPcForMajorScaleDegree,
  circlePathArc,
  circlePathArcHoleBottom,
  circlePathArcSpan,
});
})(globalThis);
