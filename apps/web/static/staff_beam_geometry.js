(function initStaffBeamGeometry(global) {
  "use strict";

  function commonStemUp(noteYs, staffMiddleY) {
    const values = Array.from(noteYs || []).map(Number).filter(Number.isFinite);
    if (!values.length) return true;
    const averageY = values.reduce((sum, value) => sum + value, 0) / values.length;
    return averageY >= Number(staffMiddleY);
  }

  global.MidiChordsStaffBeamGeometry = Object.freeze({ commonStemUp });
})(globalThis);
