import 'dart:math' as math;

/// Teclado móvil: proporción web (`style.css` 124px / 36px).
const double pianoMinWhiteKeyWidth = 28.0;
const double pianoMaxWhiteKeyWidth = 36.0;
const double pianoWhiteKeyHeight = 124.0;
const double pianoKeyAspect = pianoWhiteKeyHeight / pianoMaxWhiteKeyWidth;

/// Teclas visibles en viewport cuando hay scroll (recorte lateral).
const double pianoTargetVisibleWhiteKeys = 9.5;

class PianoKeyMetrics {
  const PianoKeyMetrics({
    required this.whiteW,
    required this.whiteH,
    required this.scrollable,
  });

  final double whiteW;
  final double whiteH;
  final bool scrollable;
}

PianoKeyMetrics computePianoKeyMetrics({
  required double viewportW,
  required double viewportH,
  required int whiteKeyCount,
}) {
  final availH = math.max(88.0, viewportH - 6.0);
  final n = whiteKeyCount.toDouble();

  // 1) Caben todas las teclas: rellenar ancho del panel.
  var whiteW = (viewportW / n).clamp(
    pianoMinWhiteKeyWidth,
    pianoMaxWhiteKeyWidth,
  );
  var whiteH = whiteW * pianoKeyAspect;
  if (whiteH <= availH && whiteW * n <= viewportW) {
    return PianoKeyMetrics(whiteW: whiteW, whiteH: whiteH, scrollable: false);
  }

  // 2) Altura del panel manda; scroll horizontal si hace falta.
  whiteH = availH;
  whiteW = math.max(pianoMinWhiteKeyWidth, whiteH / pianoKeyAspect);
  var keyboardW = whiteW * n;
  if (keyboardW <= viewportW) {
    whiteW = viewportW / n;
    whiteH = math.min(availH, whiteW * pianoKeyAspect);
    return PianoKeyMetrics(whiteW: whiteW, whiteH: whiteH, scrollable: false);
  }

  // 3) Scroll: priorizar altura y dejar ~media tecla cortada al borde.
  final targetW = (viewportW / pianoTargetVisibleWhiteKeys).clamp(
    0.0,
    pianoMaxWhiteKeyWidth,
  );
  if (targetW > whiteW) {
    whiteW = targetW;
    whiteH = math.min(availH, whiteW * pianoKeyAspect);
    keyboardW = whiteW * n;
  }
  return PianoKeyMetrics(
    whiteW: whiteW,
    whiteH: whiteH,
    scrollable: keyboardW > viewportW + 1,
  );
}
