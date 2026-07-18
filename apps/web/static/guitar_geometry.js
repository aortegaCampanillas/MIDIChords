(function initGuitarGeometry(global) {
  "use strict";

  function findBarreSegments(frets, fingers) {
    if (!Array.isArray(frets) || !Array.isArray(fingers) || frets.length !== fingers.length) {
      return { segments: [], coveredIndexes: [] };
    }
    const soundedIndexes = [];
    for (let index = 0; index < frets.length; index += 1) {
      if (Number(frets[index]) >= 0) soundedIndexes.push(index);
    }
    if (!soundedIndexes.length) return { segments: [], coveredIndexes: [] };

    const minSounded = Math.min(...soundedIndexes);
    const maxSounded = Math.max(...soundedIndexes);
    const uniqueFrets = Array.from(new Set(frets.filter((fret) => Number(fret) > 0)))
      .sort((a, b) => Number(a) - Number(b));
    const segments = [];
    const coveredIndexes = new Set();

    const addSegment = (fret, finger, start, end, indexes) => {
      const covered = Array.from(indexes);
      segments.push({ fret: Number(fret), finger: Number(finger), start, end, covered });
      covered.forEach((index) => coveredIndexes.add(index));
    };

    uniqueFrets.forEach((fret) => {
      const indexesByFinger = new Map();
      for (let index = 0; index < frets.length; index += 1) {
        if (Number(frets[index]) !== Number(fret)) continue;
        const finger = Number(fingers[index]);
        if (!Number.isFinite(finger) || finger <= 0) continue;
        const indexes = indexesByFinger.get(finger) || [];
        indexes.push(index);
        indexesByFinger.set(finger, indexes);
      }

      indexesByFinger.forEach((indexes, finger) => {
        if (indexes.length < 2) return;
        if (indexes[0] === minSounded && indexes[indexes.length - 1] === maxSounded) {
          addSegment(fret, finger, indexes[0], indexes[indexes.length - 1], indexes);
          return;
        }

        let runStart = indexes[0];
        let runEnd = indexes[0];
        for (let position = 1; position <= indexes.length; position += 1) {
          const index = indexes[position];
          if (index === runEnd + 1) {
            runEnd = index;
            continue;
          }
          if (runEnd - runStart + 1 >= 2) {
            const covered = [];
            for (let coveredIndex = runStart; coveredIndex <= runEnd; coveredIndex += 1) {
              covered.push(coveredIndex);
            }
            addSegment(fret, finger, runStart, runEnd, covered);
          }
          runStart = index;
          runEnd = index;
        }
      });
    });

    return {
      segments,
      coveredIndexes: Array.from(coveredIndexes).sort((a, b) => a - b),
    };
  }

  global.MidiChordsGuitarGeometry = Object.freeze({ findBarreSegments });
})(globalThis);
