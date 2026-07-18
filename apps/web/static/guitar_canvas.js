(function initGuitarCanvas(global) {
  "use strict";

  function drawFretboardFrame(ctx, options) {
    const { layout, width, height, frets } = options;
    const { top, bottom, nutX, boardEdgeX, step, dir, openX } = layout;

    ctx.fillStyle = "#f9f9f7";
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = "#34363c";
    ctx.strokeStyle = "#4a4f58";
    ctx.lineWidth = 1;
    ctx.fillRect(Math.min(nutX, boardEdgeX), top - 10, Math.abs(boardEdgeX - nutX), bottom - top + 20);
    ctx.strokeRect(Math.min(nutX, boardEdgeX), top - 10, Math.abs(boardEdgeX - nutX), bottom - top + 20);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(Math.min(openX, nutX), top - 10, Math.abs(nutX - openX), bottom - top + 20);
    ctx.strokeStyle = "#c8b79f";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(nutX, top - 10);
    ctx.lineTo(nutX, bottom + 10);
    ctx.stroke();

    for (let fret = 1; fret <= frets; fret += 1) {
      const x = nutX + dir * fret * step;
      ctx.strokeStyle = "#c8b79f";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, top - 10);
      ctx.lineTo(x, bottom + 10);
      ctx.stroke();
      ctx.strokeStyle = "#8f8576";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + (dir > 0 ? 2 : -2), top - 10);
      ctx.lineTo(x + (dir > 0 ? 2 : -2), bottom + 10);
      ctx.stroke();
    }

    ctx.fillStyle = "#222";
    ctx.font = "bold 13px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (let fret = 0; fret < frets; fret += 1) {
      const x = fret <= 0 ? (openX + nutX) / 2 : nutX + dir * (fret - 0.5) * step;
      ctx.fillText(String(fret), x, 16);
    }
    ctx.textAlign = "start";
    ctx.textBaseline = "alphabetic";
  }

  function drawFretboardStrings(ctx, options) {
    const { layout, width, stringNames, leftHanded } = options;
    const { top, boardEdgeX, openX, yGap } = layout;
    stringNames.forEach((name, index) => {
      const y = top + index * yGap;
      ctx.strokeStyle = "#bdbdbd";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(Math.min(openX, boardEdgeX), y);
      ctx.lineTo(Math.max(openX, boardEdgeX), y);
      ctx.stroke();
      ctx.strokeStyle = "#8a8a8a";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(Math.min(openX, boardEdgeX), y + 1);
      ctx.lineTo(Math.max(openX, boardEdgeX), y + 1);
      ctx.stroke();
      ctx.fillStyle = "#111";
      ctx.font = "bold 11px sans-serif";
      ctx.textBaseline = "middle";
      if (leftHanded) {
        ctx.textAlign = "left";
        const rightEdge = Math.max(openX, boardEdgeX);
        ctx.fillText(name, Math.min(width - 2, rightEdge + 10), y);
      } else {
        ctx.textAlign = "right";
        const leftEdge = Math.min(openX, boardEdgeX);
        ctx.fillText(name, Math.max(2, leftEdge - 10), y);
      }
      ctx.textAlign = "start";
    });
    ctx.textBaseline = "alphabetic";
  }

  global.MidiChordsGuitarCanvas = { drawFretboardFrame, drawFretboardStrings };
})(typeof globalThis !== "undefined" ? globalThis : window);
