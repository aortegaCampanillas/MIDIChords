(function initStaffBeamGeometry(global) {
  "use strict";

  function commonStemUp(noteYs, staffMiddleY) {
    const values = Array.from(noteYs || []).map(Number).filter(Number.isFinite);
    if (!values.length) return true;
    const averageY = values.reduce((sum, value) => sum + value, 0) / values.length;
    return averageY >= Number(staffMiddleY);
  }

  function beamSegments(positions, barThickness = 4, barGap = 3) {
    const points = Array.from(positions || []);
    if (points.length < 2) return [];
    const first = points[0];
    const last = points[points.length - 1];
    const direction = first.stemUp ? 1 : -1;
    const segments = [{
      xa: first.stemX,
      ya: first.stemEndY,
      xb: last.stemX,
      yb: last.stemEndY,
      direction,
    }];
    const dx = last.stemX - first.stemX;
    const dy = last.stemEndY - first.stemEndY;
    points.forEach((point, index) => {
      if (point.base !== "s") return;
      const adjacent = index > 0 ? points[index - 1] : points[index + 1];
      if (!adjacent) return;
      const halfX = (point.stemX + adjacent.stemX) / 2;
      const ratio = dx !== 0 ? (halfX - first.stemX) / dx : 0;
      const halfY = first.stemEndY + ratio * dy;
      const offset = direction * (barThickness + barGap);
      segments.push(index > 0
        ? { xa: halfX, ya: halfY + offset, xb: point.stemX, yb: point.stemEndY + offset, direction }
        : { xa: point.stemX, ya: point.stemEndY + offset, xb: halfX, yb: halfY + offset, direction });
    });
    return segments;
  }

  global.MidiChordsStaffBeamGeometry = Object.freeze({ commonStemUp, beamSegments });
})(globalThis);
