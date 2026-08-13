part of 'main.dart';

class _MiniStaffPainter extends CustomPainter {
  _MiniStaffPainter({
    required this.notes,
    required this.extras,
    this.detectionActiveNotes = const <int>{},
    this.generationRhNotes = const <int>[],
    this.generationLhNotes = const <int>[],
    this.generationPlayingNotes = const <int>{},
    this.generationGuitarMode = false,
    this.scaleRhNotes = const <int>[],
    this.scaleLhNotes = const <int>[],
    this.scaleCurrentNote,
    this.scaleCurrentIsLeft,
    this.scaleGuitarMode = false,
    this.keySignatureCount = 0,
    this.keySignaturePreferFlats = false,
    this.activeKeySignatureIndex = -1,
    this.intervalMelodyMode = false,
    this.intervalMelodyNotes = const <int?>[],
    this.intervalMelodyDurations = const <String>[],
    this.intervalPlayingIdx,
    this.intervalPlayingNotes = const <int>{},
    this.intervalSequenceMode = false,
    this.intervalQuestion = false,
    this.intervalCorrectNote,
    this.intervalWrongNote,
    this.intervalBeatsPerBar = 4,
    this.intervalAnacrusis = 0.0,
  });

  /// Orden F# C# G# D# A# E# B# — mismos MIDI que `app.js`.
  static const List<double> _keySigTrebleSharpMidis = <double>[
    78,
    73,
    80,
    75,
    70,
    76,
    71,
  ];
  static const List<double> _keySigBassSharpMidis = <double>[
    54,
    49,
    56,
    51,
    46,
    52,
    47,
  ];
  static const List<double> _keySigTrebleFlatOffsets = <double>[
    2,
    0.5,
    2.5,
    1,
    3,
    1.5,
    3.5,
  ];
  static const List<double> _keySigBassFlatOffsets = <double>[
    3,
    1.5,
    3.5,
    2,
    4,
    2.5,
    4.5,
  ];

  final List<int> notes;
  final Set<int> extras;
  final Set<int> detectionActiveNotes;
  final List<int> generationRhNotes;
  final List<int> generationLhNotes;
  final Set<int> generationPlayingNotes;
  final bool generationGuitarMode;
  final List<int> scaleRhNotes;
  final List<int> scaleLhNotes;
  final int? scaleCurrentNote;
  final bool? scaleCurrentIsLeft;
  final bool scaleGuitarMode;
  final int keySignatureCount;
  final bool keySignaturePreferFlats;
  final int activeKeySignatureIndex;
  final bool intervalMelodyMode;
  final List<int?> intervalMelodyNotes;
  final List<String> intervalMelodyDurations;
  final int? intervalPlayingIdx;
  final Set<int> intervalPlayingNotes;
  final bool intervalSequenceMode;
  final bool intervalQuestion;
  final int? intervalCorrectNote;
  final int? intervalWrongNote;
  final int intervalBeatsPerBar;
  final double intervalAnacrusis;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0F1621);
    canvas.drawRect(Offset.zero & size, bg);

    final linePaint = Paint()
      ..color = const Color(0xFFCAD3E0)
      ..strokeWidth = 1.4;
    final noteOutline = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.8;

    final compactWidth = size.width < 520;
    final left = compactWidth ? 28.0 : 52.0;
    final right = size.width - 16;
    final gap = math.max(10.0, math.min(16.0, size.height / 24));
    final grandGap = math.max(64.0, gap * 6.2);
    final systemH = grandGap + (4 * gap);
    final trebleTop = (size.height - systemH) / 2;
    final bassTop = trebleTop + grandGap;
    final clefInset = compactWidth ? 6.0 : 12.0;
    final clefBassInset = compactWidth ? 8.0 : 14.0;
    var noteStartX = left + (compactWidth ? 72.0 : 110.0);
    final scaleStepX = compactWidth ? 24.0 : 32.0;
    final noteW = compactWidth ? 13.0 : 16.0;
    final noteH = compactWidth ? 10.0 : 12.0;
    final noteColumnStep = compactWidth ? noteW * 1.4 : noteW * 1.8;

    for (int i = 0; i < 5; i += 1) {
      final yT = trebleTop + i * gap;
      final yB = bassTop + i * gap;
      canvas.drawLine(Offset(left, yT), Offset(right, yT), linePaint);
      canvas.drawLine(Offset(left, yB), Offset(right, yB), linePaint);
    }
    canvas.drawLine(
      Offset(left, trebleTop),
      Offset(left, bassTop + 4 * gap),
      linePaint..strokeWidth = 1.6,
    );

    final clefStyle = TextStyle(
      color: const Color(0xFFE9EDF2),
      fontSize: gap * 3.5,
      fontWeight: FontWeight.w700,
    );
    final tpTreble = TextPainter(
      text: TextSpan(text: '𝄞', style: clefStyle),
      textDirection: TextDirection.ltr,
    )..layout();
    tpTreble.paint(canvas, Offset(left + clefInset, trebleTop + gap * 0.6));
    final tpBass = TextPainter(
      text: TextSpan(text: '𝄢', style: clefStyle),
      textDirection: TextDirection.ltr,
    )..layout();
    tpBass.paint(canvas, Offset(left + clefBassInset, bassTop + gap * 0.5));

    if (keySignatureCount > 0) {
      final sigStep = compactWidth ? 13.5 : 18.0;
      final keyX0 = left + (compactWidth ? 54.0 : 82.0);
      final accBase = math.max(15.0, gap * 1.55);
      final accStyleSharp = TextStyle(
        color: const Color(0xFFE9EDF2),
        fontSize: accBase,
      );
      final accStyleFlat = accStyleSharp.copyWith(fontSize: accBase * 1.14);
      var xKey = keyX0;
      final n = keySignatureCount.clamp(0, 7);
      for (int i = 0; i < n; i += 1) {
        final sym = keySignaturePreferFlats ? '♭' : '♯';
        final double yTreble;
        final double yBass;
        if (keySignaturePreferFlats) {
          yTreble = trebleTop + gap * _keySigTrebleFlatOffsets[i];
          yBass = bassTop + gap * _keySigBassFlatOffsets[i];
        } else {
          yTreble = _midiToTrebleY(_keySigTrebleSharpMidis[i], trebleTop, gap);
          yBass = _midiToBassY(_keySigBassSharpMidis[i], bassTop, gap);
        }
        final active = i == activeKeySignatureIndex;
        final baseStyle = keySignaturePreferFlats
            ? accStyleFlat
            : accStyleSharp;
        final accStyle = active
            ? baseStyle.copyWith(
                color: const Color(0xFF6FE0FF),
                fontWeight: FontWeight.bold,
                shadows: const <Shadow>[
                  Shadow(color: Color(0x996FE0FF), blurRadius: 7),
                ],
              )
            : baseStyle;
        final tpAcc = TextPainter(
          text: TextSpan(text: sym, style: accStyle),
          textDirection: TextDirection.ltr,
        )..layout();
        final ox = xKey + sigStep / 2 - tpAcc.width / 2;
        final oyOff = tpAcc.height / 2;
        tpAcc.paint(canvas, Offset(ox, yTreble - oyOff));
        tpAcc.paint(canvas, Offset(ox, yBass - oyOff));
        xKey += sigStep;
      }
      noteStartX = xKey + (compactWidth ? 8.0 : 12.0);
    }

    if (intervalMelodyMode && intervalMelodyNotes.isNotEmpty) {
      _drawIntervalMelody(
        canvas,
        trebleTop,
        bassTop,
        gap,
        noteStartX,
        right,
        noteW,
        noteH,
        keySignatureCount,
        keySignaturePreferFlats,
      );
    } else if (scaleRhNotes.isNotEmpty) {
      final noteFill = Paint()..style = PaintingStyle.fill;
      final pairCount = math.min(scaleRhNotes.length, scaleLhNotes.length);
      for (int degree = 0; degree < scaleRhNotes.length; degree += 1) {
        final x = noteStartX + (degree * scaleStepX);
        if (degree < pairCount) {
          final bassMidi = scaleLhNotes[degree];
          final yBass = _midiToBassY(bassMidi.toDouble(), bassTop, gap);
          final currentBass =
              scaleCurrentNote != null &&
              scaleCurrentNote == bassMidi &&
              (scaleCurrentIsLeft != false);
          noteOutline.color = currentBass
              ? const Color(0xFFFF8A2B)
              : const Color(0xFFE9EDF2);
          _drawLedgerLines(
            canvas,
            x: x,
            midi: bassMidi.toDouble(),
            top: bassTop,
            gap: gap,
            treble: false,
            color: noteOutline.color,
          );
          final bassRect = Rect.fromCenter(
            center: Offset(x, yBass),
            width: noteW,
            height: noteH,
          );
          if (currentBass) {
            noteFill.color = const Color(0xFFFF8A2B);
            canvas.drawOval(bassRect, noteFill);
          }
          canvas.drawOval(bassRect, noteOutline);
        }
        final trebleMidi = scaleRhNotes[degree];
        final yTreble = _midiToTrebleY(trebleMidi.toDouble(), trebleTop, gap);
        final currentTreble =
            scaleCurrentNote != null &&
            scaleCurrentNote == trebleMidi &&
            (scaleCurrentIsLeft != true);
        noteOutline.color = currentTreble
            ? const Color(0xFF4DA3EA)
            : const Color(0xFFE9EDF2);
        _drawLedgerLines(
          canvas,
          x: x,
          midi: trebleMidi.toDouble(),
          top: trebleTop,
          gap: gap,
          treble: true,
          color: noteOutline.color,
        );
        if (currentTreble) {
          noteFill.color = const Color(0xFF4DA3EA);
          canvas.drawOval(
            Rect.fromCenter(
              center: Offset(x, yTreble),
              width: noteW,
              height: noteH,
            ),
            noteFill,
          );
        }
        canvas.drawOval(
          Rect.fromCenter(
            center: Offset(x, yTreble),
            width: noteW,
            height: noteH,
          ),
          noteOutline,
        );
      }
    } else {
      final list = notes.toList();
      if (!intervalSequenceMode) {
        list.sort();
      }
      final placedTrebleCols = <int, List<double>>{};
      final placedBassCols = <int, List<double>>{};
      final rhSet = generationRhNotes.toSet();
      final lhSet = generationLhNotes.toSet();
      final overlapThreshold = math.max(1.0, noteH - 1.0);
      for (int i = 0; i < list.length; i += 1) {
        final midi = list[i];
        final y = midi >= 60
            ? _midiToTrebleY(
                midi.toDouble(),
                trebleTop,
                gap,
                keySignaturePreferFlats,
              )
            : _midiToBassY(
                midi.toDouble(),
                bassTop,
                gap,
                keySignaturePreferFlats,
              );
        final placedCols = midi >= 60 ? placedTrebleCols : placedBassCols;
        var col = 0;
        while (true) {
          final ys = placedCols[col] ?? const <double>[];
          final overlaps = ys.any(
            (prevY) => (y - prevY).abs() < overlapThreshold,
          );
          if (!overlaps) break;
          col += 1;
        }
        final x = intervalSequenceMode
            ? intervalStaffNoteX(
                startX: noteStartX,
                index: i,
                compactWidth: compactWidth,
              )
            : noteStartX + (col * noteColumnStep);
        final ys = List<double>.from(placedCols[col] ?? const <double>[])
          ..add(y);
        placedCols[col] = ys;
        Color? fillColor;
        noteOutline.strokeWidth = 1.8;
        if (intervalPlayingNotes.contains(midi) ||
            (intervalSequenceMode && intervalPlayingIdx == i)) {
          fillColor = const Color(0xFF4DA3EA);
          noteOutline.color = const Color(0xFFE9EDF2);
        } else if (intervalCorrectNote == midi) {
          fillColor = const Color(0xFF39C66D);
          noteOutline.color = const Color(0xFFBFF6CE);
        } else if (intervalWrongNote == midi) {
          fillColor = const Color(0xFFE35D67);
          noteOutline.color = const Color(0xFFFFCED2);
        } else if (detectionActiveNotes.contains(midi)) {
          fillColor = const Color(0xFF4DA3EA);
          noteOutline.color = const Color(0xFFE9EDF2);
        } else if (generationPlayingNotes.contains(midi)) {
          noteOutline.strokeWidth = 2.45;
          if (!generationGuitarMode &&
              lhSet.contains(midi) &&
              !rhSet.contains(midi)) {
            fillColor = const Color(0xFFFFA040);
            noteOutline.color = const Color(0xFFFFE0C2);
          } else {
            fillColor = const Color(0xFF5ECEFF);
            noteOutline.color = const Color(0xFFE9EDF2);
          }
        } else if (rhSet.contains(midi) || lhSet.contains(midi)) {
          // Mismo criterio que piano: contorno del acorde sin relleno en reposo.
          // En guitarra, si además rellenábamos todas las notas en rhSet, al
          // alinear rhSet con el pentagrama quedaban todas “marcadas”.
          fillColor = null;
          noteOutline.strokeWidth = 2.05;
          if (lhSet.contains(midi) && !rhSet.contains(midi)) {
            noteOutline.color = const Color(0xFFFF8A2B);
          } else {
            noteOutline.color = const Color(0xFF6FE0FF);
          }
        } else if (extras.contains(midi)) {
          fillColor = const Color(0xFFBF2F2F);
          noteOutline.color = const Color(0xFFF48F8F);
        } else {
          fillColor = null;
          noteOutline.color = const Color(0xFFE9EDF2);
        }
        final oval = Rect.fromCenter(
          center: Offset(x, y),
          width: noteW,
          height: noteH,
        );
        _drawLedgerLines(
          canvas,
          x: x,
          midi: midi.toDouble(),
          top: midi >= 60 ? trebleTop : bassTop,
          gap: gap,
          treble: midi >= 60,
          color: noteOutline.color,
        );
        if (fillColor != null) {
          canvas.drawOval(oval, Paint()..color = fillColor);
        }
        canvas.drawOval(oval, noteOutline);
        final accSym = _noteAccidentalSymbol(
          midi,
          keySignatureCount: keySignatureCount,
          keySignaturePreferFlats: keySignaturePreferFlats,
        );
        if (accSym != null) {
          final accStyle = TextStyle(
            color: noteOutline.color,
            fontSize: math.max(11.0, noteH * (accSym == '♭' ? 1.35 : 1.05)),
          );
          final tpAcc = TextPainter(
            text: TextSpan(text: accSym, style: accStyle),
            textDirection: TextDirection.ltr,
          )..layout();
          tpAcc.paint(
            canvas,
            Offset(x - noteW / 2 - tpAcc.width - 2, y - tpAcc.height / 2),
          );
        }
      }
      if (intervalQuestion) {
        final questionPainter = TextPainter(
          text: const TextSpan(
            text: '?',
            style: TextStyle(
              color: Color(0xFFE9EDF2),
              fontSize: 24,
              fontWeight: FontWeight.w800,
            ),
          ),
          textDirection: TextDirection.ltr,
        )..layout();
        questionPainter.paint(
          canvas,
          Offset(
            intervalStaffNoteX(
                  startX: noteStartX,
                  index: 1,
                  compactWidth: compactWidth,
                ) -
                questionPainter.width / 2,
            trebleTop + gap * 1.25,
          ),
        );
      }
    }
  }

  double _midiToTrebleY(
    double midi,
    double top,
    double gap, [
    bool preferFlat = false,
  ]) {
    const bottomLineDiatonic = 30.0; // E4
    final d = _midiToDiatonic(midi, preferFlat);
    final baseY = top + 4 * gap;
    return baseY - ((d - bottomLineDiatonic) * (gap / 2));
  }

  double _midiToBassY(
    double midi,
    double top,
    double gap, [
    bool preferFlat = false,
  ]) {
    const bottomLineDiatonic = 18.0; // G2
    final d = _midiToDiatonic(midi, preferFlat);
    final baseY = top + 4 * gap;
    return baseY - ((d - bottomLineDiatonic) * (gap / 2));
  }

  /// pc -> índice de letra diatónica (C..B) con convención de sostenidos.
  static const List<int> _pcToDiatonicSharp = <int>[
    0,
    0,
    1,
    1,
    2,
    3,
    3,
    4,
    4,
    5,
    5,
    6,
  ];

  /// Igual pero con convención de bemoles (p. ej. pc=1 -> Re, no Do), para
  /// que la posición en el pentagrama también "se mueva" al cambiar el
  /// ajuste global #/♭, no solo el símbolo dibujado junto a la nota.
  static const List<int> _pcToDiatonicFlat = <int>[
    0,
    1,
    1,
    2,
    2,
    3,
    4,
    4,
    5,
    5,
    6,
    6,
  ];

  double _midiToDiatonic(double midi, [bool preferFlat = false]) {
    final table = preferFlat ? _pcToDiatonicFlat : _pcToDiatonicSharp;
    final n = midi.round();
    final pc = ((n % 12) + 12) % 12;
    final octave = (n ~/ 12) - 1;
    return (octave * 7 + table[pc]).toDouble();
  }

  /// Símbolo de alteración a dibujar junto a una nota concreta (null si es
  /// natural o si ya está cubierta por la armadura). Análogo a
  /// `getNoteAccidental` en apps/web/static/app.js.
  String? _noteAccidentalSymbol(
    int midi, {
    required int keySignatureCount,
    required bool keySignaturePreferFlats,
  }) {
    final pc = ((midi % 12) + 12) % 12;
    const naturalPcs = <int>{0, 2, 4, 5, 7, 9, 11};
    if (naturalPcs.contains(pc)) return null;
    const sharpPcOrder = <int>[6, 1, 8, 3, 10]; // F# C# G# D# A#
    const flatPcOrder = <int>[10, 3, 8, 1, 6]; // Bb Eb Ab Db Gb
    if (keySignaturePreferFlats) {
      final covered = flatPcOrder.take(keySignatureCount).toSet();
      if (covered.contains(pc)) return null;
      return '♭';
    }
    final covered = sharpPcOrder.take(keySignatureCount).toSet();
    if (covered.contains(pc)) return null;
    return '♯';
  }

  void _drawLedgerLines(
    Canvas canvas, {
    required double x,
    required double midi,
    required double top,
    required double gap,
    required bool treble,
    required Color color,
  }) {
    final d = _midiToDiatonic(midi).round();
    final bottomLineD = treble ? 30 : 18;
    final topLineD = bottomLineD + 8;
    if (d >= bottomLineD && d <= topLineD) return;

    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round;
    final lineLeft = x - 11.0;
    final lineRight = x + 11.0;
    if (d < bottomLineD) {
      for (int ld = bottomLineD - 2; ld >= d; ld -= 2) {
        final y = _staffYForDiatonic(
          diatonic: ld.toDouble(),
          bottomLineDiatonic: bottomLineD.toDouble(),
          top: top,
          gap: gap,
        );
        canvas.drawLine(Offset(lineLeft, y), Offset(lineRight, y), paint);
      }
      return;
    }
    for (int ld = topLineD + 2; ld <= d; ld += 2) {
      final y = _staffYForDiatonic(
        diatonic: ld.toDouble(),
        bottomLineDiatonic: bottomLineD.toDouble(),
        top: top,
        gap: gap,
      );
      canvas.drawLine(Offset(lineLeft, y), Offset(lineRight, y), paint);
    }
  }

  double _staffYForDiatonic({
    required double diatonic,
    required double bottomLineDiatonic,
    required double top,
    required double gap,
  }) {
    final baseY = top + 4 * gap;
    return baseY - ((diatonic - bottomLineDiatonic) * (gap / 2));
  }

  void _drawIntervalMelody(
    Canvas canvas,
    double trebleTop,
    double bassTop,
    double gap,
    double noteStartX,
    double right,
    double noteW,
    double noteH,
    int keySignatureCount,
    bool keySignaturePreferFlats,
  ) {
    final n = intervalMelodyNotes.length;
    if (n == 0) return;

    const noteColor = Color(0xFFD7DDE7);
    const playColor = Color(0xFF4DA3EA);
    final stemLen = gap * 3.5;
    final dotR = math.max(1.5, gap * 0.18);

    // Time signature
    final tsFontSize = math.max(14.0, gap * 1.7);
    TextPainter makeTp(String text) => TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: const Color(0xFFFFFFFF),
          fontSize: tsFontSize,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    final tpNum = makeTp(intervalBeatsPerBar.toString());
    final tpDen = makeTp('4');
    final tsHW = math.max(tpNum.width, tpDen.width) / 2;
    final tsX = noteStartX + tsHW;
    tpNum.paint(canvas, Offset(tsX - tpNum.width / 2, trebleTop + gap * 0.3));
    tpDen.paint(canvas, Offset(tsX - tpDen.width / 2, trebleTop + gap * 2.3));
    tpNum.paint(canvas, Offset(tsX - tpNum.width / 2, bassTop + gap * 0.3));
    tpDen.paint(canvas, Offset(tsX - tpDen.width / 2, bassTop + gap * 2.3));
    final melLeft = tsX + tsHW + 10.0;

    // Tick durations
    const qt = 1000;
    int tickFor(String d) {
      final dotted = d.endsWith('.');
      final code = dotted ? d.substring(0, d.length - 1) : d;
      const tmap = <String, int>{
        'w': 4 * qt,
        'h': 2 * qt,
        'q': qt,
        'e': qt ~/ 2,
        'et': qt ~/ 3,
        's': qt ~/ 4,
      };
      var t = tmap[code] ?? qt;
      if (dotted) t = t * 3 ~/ 2;
      return t;
    }

    final ticks = List<int>.generate(n, (i) {
      final d = i < intervalMelodyDurations.length
          ? intervalMelodyDurations[i]
          : 'q';
      return tickFor(d);
    });
    final totalTicks = ticks.fold(0, (a, b) => a + b);
    if (totalTicks == 0) return;
    final availW = (right - 16.0) - melLeft;
    final xPos = List<double>.generate(n, (i) {
      final cum = ticks.sublist(0, i).fold(0, (a, b) => a + b);
      return melLeft + cum / totalTicks * availW;
    });
    // El espaciado proporcional puro deja las notas que siguen a un
    // tresillo (duración muy corta) pegadas a la última nota del tresillo.
    // Forzamos una separación mínima entre notas consecutivas, empujando
    // el resto de posiciones hacia la derecha cuando haga falta.
    final minGap = math.max(noteW * 1.15, gap * 1.3);
    for (int i = 1; i < n; i++) {
      if (xPos[i] - xPos[i - 1] < minGap) {
        xPos[i] = xPos[i - 1] + minGap;
      }
    }

    // Bar lines
    final barTicks = intervalBeatsPerBar * qt;
    var barRun = -(intervalAnacrusis * qt).round();
    final blPaint = Paint()
      ..color = const Color(0xFF5A6A7A)
      ..strokeWidth = 1.0;
    for (int i = 0; i < n; i++) {
      final prev = barRun;
      barRun += ticks[i];
      if (i > 0 && (prev ~/ barTicks) < (barRun ~/ barTicks)) {
        final bx = (xPos[i - 1] + xPos[i]) / 2;
        canvas.drawLine(
          Offset(bx, trebleTop),
          Offset(bx, bassTop + 4 * gap),
          blPaint,
        );
      }
    }

    // Beam groups
    final beamGroupOf = <int, int>{};
    final beamGroups = <List<int>>[];
    var tickPos = 0;
    var bgCurrent = <int>[];
    var bgBeat = 0;
    var bgIsTreble = true;
    for (int i = 0; i < n; i++) {
      final dur = i < intervalMelodyDurations.length
          ? intervalMelodyDurations[i]
          : 'q';
      final durBase = dur.endsWith('.')
          ? dur.substring(0, dur.length - 1)
          : dur;
      final isSubQ =
          (durBase == 'e' || durBase == 'et' || durBase == 's') &&
          intervalMelodyNotes[i] != null;
      final beat = tickPos ~/ qt;
      // Una nota puede estar en clave de sol o de fa; no unimos con barra
      // notas que caen en pentagramas distintos, aunque sean corcheas
      // consecutivas del mismo grupo rítmico (se vería como una línea
      // cruzando de un pentagrama a otro, como una ligadura fuera de lugar).
      final noteIsTreble = isSubQ
          ? (intervalMelodyNotes[i]! >= 60)
          : bgIsTreble;
      if (isSubQ) {
        if (bgCurrent.isNotEmpty &&
            (beat != bgBeat || noteIsTreble != bgIsTreble)) {
          if (bgCurrent.length > 1) {
            final gid = beamGroups.length;
            for (final g in bgCurrent) {
              beamGroupOf[g] = gid;
            }
            beamGroups.add(List<int>.from(bgCurrent));
          }
          bgCurrent = [];
        }
        if (bgCurrent.isEmpty) {
          bgBeat = beat;
          bgIsTreble = noteIsTreble;
        }
        bgCurrent.add(i);
      } else {
        if (bgCurrent.length > 1) {
          final gid = beamGroups.length;
          for (final g in bgCurrent) {
            beamGroupOf[g] = gid;
          }
          beamGroups.add(List<int>.from(bgCurrent));
        }
        bgCurrent = [];
      }
      tickPos += ticks[i];
    }
    if (bgCurrent.length > 1) {
      final gid = beamGroups.length;
      for (final g in bgCurrent) {
        beamGroupOf[g] = gid;
      }
      beamGroups.add(List<int>.from(bgCurrent));
    }

    // Todas las notas de un grupo barrado deben compartir dirección de plica.
    // Decidirla nota a nota puede unir un extremo superior con otro inferior y
    // producir una diagonal que atraviesa las cabezas (p. ej. Do3–La3).
    final beamStemUpByNote = <int, bool>{};
    for (final group in beamGroups) {
      if (group.isEmpty) continue;
      final firstMidi = intervalMelodyNotes[group.first];
      if (firstMidi == null) continue;
      final isTreble = firstMidi >= 60;
      final staffTop = isTreble ? trebleTop : bassTop;
      final noteYs = group
          .map((index) => intervalMelodyNotes[index])
          .whereType<int>()
          .map(
            (midi) => isTreble
                ? _midiToTrebleY(
                    midi.toDouble(),
                    trebleTop,
                    gap,
                    keySignaturePreferFlats,
                  )
                : _midiToBassY(
                    midi.toDouble(),
                    bassTop,
                    gap,
                    keySignaturePreferFlats,
                  ),
          );
      final stemUp = beamGroupStemUp(noteYs, staffTop + 2 * gap);
      for (final index in group) {
        beamStemUpByNote[index] = stemUp;
      }
    }

    // Draw notes and rests
    final stemData =
        <int, ({double x, double yEnd, bool stemUp, int flagCount})>{};
    for (int i = 0; i < n; i++) {
      final midiNull = intervalMelodyNotes[i];
      final dur = i < intervalMelodyDurations.length
          ? intervalMelodyDurations[i]
          : 'q';
      final durBase = dur.endsWith('.')
          ? dur.substring(0, dur.length - 1)
          : dur;
      final isDotted = dur.endsWith('.');
      final x = xPos[i];
      final flagCount = (durBase == 'e' || durBase == 'et')
          ? 1
          : (durBase == 's' ? 2 : 0);
      final hasStem = durBase != 'w';
      final isHollow = durBase == 'w' || durBase == 'h';
      final col = intervalPlayingIdx == i ? playColor : noteColor;

      if (midiNull == null) {
        _drawRestSymbolMelody(
          canvas,
          x,
          trebleTop + 2 * gap,
          durBase,
          gap,
          noteColor,
          trebleTop,
        );
      } else {
        final midi = midiNull;
        final isT = midi >= 60;
        final y = isT
            ? _midiToTrebleY(
                midi.toDouble(),
                trebleTop,
                gap,
                keySignaturePreferFlats,
              )
            : _midiToBassY(
                midi.toDouble(),
                bassTop,
                gap,
                keySignaturePreferFlats,
              );
        final staffTop = isT ? trebleTop : bassTop;
        _drawLedgerLines(
          canvas,
          x: x,
          midi: midi.toDouble(),
          top: staffTop,
          gap: gap,
          treble: isT,
          color: col,
        );
        final nw = durBase == 'w' ? noteW * 1.25 : noteW;
        canvas.drawOval(
          Rect.fromCenter(center: Offset(x, y), width: nw, height: noteH),
          Paint()
            ..style = isHollow ? PaintingStyle.stroke : PaintingStyle.fill
            ..color = col
            ..strokeWidth = 2.0,
        );
        final accSym = _noteAccidentalSymbol(
          midi,
          keySignatureCount: keySignatureCount,
          keySignaturePreferFlats: keySignaturePreferFlats,
        );
        if (accSym != null) {
          final accStyle = TextStyle(
            color: col,
            fontSize: math.max(11.0, noteH * (accSym == '♭' ? 1.35 : 1.05)),
          );
          final tpAcc = TextPainter(
            text: TextSpan(text: accSym, style: accStyle),
            textDirection: TextDirection.ltr,
          )..layout();
          tpAcc.paint(
            canvas,
            Offset(x - nw / 2 - tpAcc.width - 2, y - tpAcc.height / 2),
          );
        }
        if (isDotted) {
          canvas.drawCircle(
            Offset(x + nw / 2 + dotR * 2.5, y),
            dotR,
            Paint()..color = col,
          );
        }
        if (hasStem) {
          final stemMid = staffTop + 2 * gap;
          final stemUp = beamStemUpByNote[i] ?? (y > stemMid);
          final sx = stemUp ? x + nw / 2 - 1 : x - nw / 2 + 1;
          final syEnd = stemUp ? y - stemLen : y + stemLen;
          canvas.drawLine(
            Offset(sx, y),
            Offset(sx, syEnd),
            Paint()
              ..color = col
              ..strokeWidth = 1.8,
          );
          if (flagCount > 0) {
            if (beamGroupOf.containsKey(i)) {
              stemData[i] = (
                x: sx,
                yEnd: syEnd,
                stemUp: stemUp,
                flagCount: flagCount,
              );
            } else {
              _drawMelodyFlag(canvas, sx, syEnd, flagCount, stemUp, gap, col);
            }
          }
        }
      }
    }

    // Beams
    final beamW = math.max(2.5, gap * 0.25);
    for (final group in beamGroups) {
      final data = <({double x, double yEnd, bool stemUp, int flagCount})>[];
      for (final gi in group) {
        if (stemData.containsKey(gi)) data.add(stemData[gi]!);
      }
      if (data.length < 2) continue;
      final nPrim = data.map((d) => d.flagCount).reduce(math.min);
      final su = data.first.stemUp;
      // Pendiente de la barra principal (une la primera y última nota del
      // grupo): los "stubs" de las notas con más banderas (p. ej. una
      // semicorchea junto a una corchea) deben seguir esta misma pendiente
      // en vez de salir horizontales desde su propia plica.
      final dx = data.last.x - data.first.x;
      final slope = dx.abs() < 0.001
          ? 0.0
          : (data.last.yEnd - data.first.yEnd) / dx;
      for (int bar = 0; bar < nPrim; bar++) {
        final bOff = bar * gap * 0.3;
        final y0 = su ? data.first.yEnd + bOff : data.first.yEnd - bOff;
        final y1 = su ? data.last.yEnd + bOff : data.last.yEnd - bOff;
        canvas.drawLine(
          Offset(data.first.x, y0),
          Offset(data.last.x, y1),
          Paint()
            ..color = noteColor
            ..strokeWidth = beamW,
        );
      }
      final grpLast = group.length - 1;
      for (int gi = 0; gi < group.length; gi++) {
        final idx = group[gi];
        if (!stemData.containsKey(idx)) continue;
        final d = stemData[idx]!;
        final extra = d.flagCount - nPrim;
        if (extra <= 0) continue;
        final stubDir = gi == grpLast ? -1.0 : 1.0;
        final stubW = math.max(gap * 1.2, 14.0);
        // Punto sobre la barra principal en la X de esta nota (en vez de
        // d.yEnd, que ignoraría la inclinación del grupo).
        final baseY = data.first.yEnd + slope * (d.x - data.first.x);
        for (int be = 0; be < extra; be++) {
          final stubOff = (nPrim + be) * gap * 0.3;
          final sy = su ? baseY + stubOff : baseY - stubOff;
          final sxEnd = d.x + stubDir * stubW;
          final syEnd = sy + slope * (stubDir * stubW);
          canvas.drawLine(
            Offset(d.x, sy),
            Offset(sxEnd, syEnd),
            Paint()
              ..color = noteColor
              ..strokeWidth = beamW,
          );
        }
      }
    }
  }

  void _drawMelodyFlag(
    Canvas canvas,
    double sx,
    double syEnd,
    int flagCount,
    bool stemUp,
    double gap,
    Color col,
  ) {
    // Bandera de corchea: trazo curvo fino (no relleno) desde la punta de la
    // plica (p0) hacia el lado de la cabeza de nota, con extremos
    // redondeados — evita las siluetas rellenas anchas de los intentos
    // anteriores.
    final fw = gap * 0.62;
    final fh = gap * 1.15;
    final sign = stemUp ? 1.0 : -1.0;
    final paint = Paint()
      ..color = col
      ..style = PaintingStyle.stroke
      ..strokeWidth = gap * 0.32
      ..strokeCap = StrokeCap.round;
    for (int fi = 0; fi < flagCount; fi++) {
      final fy0 = syEnd + sign * fi * gap * 0.55;
      final p0 = Offset(sx, fy0);
      final p1 = Offset(sx + fw, fy0 + sign * fh);
      final ctrl = Offset(sx + fw * 1.15, fy0 + sign * fh * 0.25);
      final path = Path()
        ..moveTo(p0.dx, p0.dy)
        ..quadraticBezierTo(ctrl.dx, ctrl.dy, p1.dx, p1.dy);
      canvas.drawPath(path, paint);
    }
  }

  void _drawRestSymbolMelody(
    Canvas canvas,
    double x,
    double cy,
    String dur,
    double gap,
    Color col,
    double trebleTop,
  ) {
    final paint = Paint()..color = col;
    if (dur == 'w') {
      final rw = gap * 1.3;
      canvas.drawRect(
        Rect.fromLTWH(x - rw / 2, trebleTop + gap, rw, gap * 0.48),
        paint,
      );
    } else if (dur == 'h') {
      final rw = gap * 1.3;
      final rh = gap * 0.48;
      canvas.drawRect(Rect.fromLTWH(x - rw / 2, cy - rh, rw, rh), paint);
    } else if (dur == 'q') {
      final lp = Paint()
        ..color = col
        ..strokeWidth = 1.8
        ..style = PaintingStyle.stroke;
      final r = gap * 0.35;
      final y0 = cy - gap * 0.75;
      final pts = [
        Offset(x + r, y0),
        Offset(x - r * 0.4, y0 + gap * 0.5),
        Offset(x + r * 0.8, y0 + gap * 0.9),
        Offset(x, y0 + gap * 1.25),
        Offset(x - r * 0.5, y0 + gap * 1.55),
      ];
      for (int k = 0; k < pts.length - 1; k++) {
        canvas.drawLine(pts[k], pts[k + 1], lp);
      }
    } else if (dur == 'e' || dur == 'et') {
      final dr = math.max(3.5, gap * 0.43);
      final span = gap * 2.4;
      final xt = x + gap * 0.3;
      final yt = cy - span * 0.5;
      final xb = x - gap * 0.2;
      final yb = cy + span * 0.5;
      canvas.drawLine(
        Offset(xt, yt),
        Offset(xb, yb),
        Paint()
          ..color = col
          ..strokeWidth = 2.2,
      );
      const t = 0.24;
      canvas.drawCircle(
        Offset(xt + (xb - xt) * t - dr * 0.65, yt + (yb - yt) * t),
        dr,
        paint,
      );
    } else if (dur == 's') {
      final dr = math.max(2.8, gap * 0.35);
      final span = gap * 3.0;
      final xt = x + gap * 0.3;
      final yt = cy - span * 0.5;
      final xb = x - gap * 0.2;
      final yb = cy + span * 0.5;
      canvas.drawLine(
        Offset(xt, yt),
        Offset(xb, yb),
        Paint()
          ..color = col
          ..strokeWidth = 2.2,
      );
      for (final t in [0.18, 0.44]) {
        canvas.drawCircle(
          Offset(xt + (xb - xt) * t - dr * 0.65, yt + (yb - yt) * t),
          dr,
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _MiniStaffPainter oldDelegate) {
    if (oldDelegate.intervalMelodyMode != intervalMelodyMode) return true;
    if (oldDelegate.intervalPlayingIdx != intervalPlayingIdx) return true;
    if (!setEquals(oldDelegate.intervalPlayingNotes, intervalPlayingNotes)) {
      return true;
    }
    if (oldDelegate.intervalSequenceMode != intervalSequenceMode) return true;
    if (oldDelegate.intervalQuestion != intervalQuestion) return true;
    if (oldDelegate.intervalCorrectNote != intervalCorrectNote) return true;
    if (oldDelegate.intervalWrongNote != intervalWrongNote) return true;
    if (oldDelegate.intervalMelodyNotes.length != intervalMelodyNotes.length) {
      return true;
    }
    if (oldDelegate.keySignatureCount != keySignatureCount) return true;
    if (oldDelegate.keySignaturePreferFlats != keySignaturePreferFlats) {
      return true;
    }
    if (oldDelegate.activeKeySignatureIndex != activeKeySignatureIndex) {
      return true;
    }
    if (oldDelegate.notes.length != notes.length) return true;
    if (oldDelegate.extras.length != extras.length) return true;
    if (oldDelegate.generationRhNotes.length != generationRhNotes.length) {
      return true;
    }
    if (oldDelegate.generationLhNotes.length != generationLhNotes.length) {
      return true;
    }
    if (!setEquals(
      oldDelegate.generationPlayingNotes,
      generationPlayingNotes,
    )) {
      return true;
    }
    if (oldDelegate.generationGuitarMode != generationGuitarMode) return true;
    if (oldDelegate.scaleRhNotes.length != scaleRhNotes.length) return true;
    if (oldDelegate.scaleLhNotes.length != scaleLhNotes.length) return true;
    if (oldDelegate.scaleCurrentNote != scaleCurrentNote) return true;
    if (oldDelegate.scaleCurrentIsLeft != scaleCurrentIsLeft) return true;
    if (oldDelegate.scaleGuitarMode != scaleGuitarMode) return true;
    for (int i = 0; i < notes.length; i += 1) {
      if (oldDelegate.notes[i] != notes[i]) return true;
    }
    for (int i = 0; i < scaleRhNotes.length; i += 1) {
      if (oldDelegate.scaleRhNotes[i] != scaleRhNotes[i]) return true;
    }
    for (int i = 0; i < scaleLhNotes.length; i += 1) {
      if (oldDelegate.scaleLhNotes[i] != scaleLhNotes[i]) return true;
    }
    for (int i = 0; i < generationRhNotes.length; i += 1) {
      if (oldDelegate.generationRhNotes[i] != generationRhNotes[i]) return true;
    }
    for (int i = 0; i < generationLhNotes.length; i += 1) {
      if (oldDelegate.generationLhNotes[i] != generationLhNotes[i]) return true;
    }
    return false;
  }
}

class _MiniMetronomePainter extends CustomPainter {
  _MiniMetronomePainter({
    required this.beatsPerBar,
    required this.clicksPerBeat,
    required this.currentBeat,
    required this.running,
    required this.direction,
    required this.motionProgress,
    required this.timerEnabled,
    required this.timerRemaining,
    required this.idleLabel,
  });

  final int beatsPerBar;
  final int clicksPerBeat;
  final int currentBeat;
  final bool running;
  final int direction;
  final double motionProgress;
  final bool timerEnabled;
  final Duration timerRemaining;
  final String idleLabel;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0F1621);
    canvas.drawRect(Offset.zero & size, bg);
    final count = math.max(1, beatsPerBar);
    final clicks = math.max(1, clicksPerBeat);
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    final spacing = count == 1 ? (right - left) : (right - left) / (count - 1);
    final xs = count == 1
        ? <double>[(left + right) * 0.5]
        : List<double>.generate(count, (i) => left + i * spacing);

    final rail = Paint()
      ..color = const Color(0xFF8F98A3)
      ..strokeWidth = 3;
    canvas.drawLine(Offset(left, axisY), Offset(right, axisY), rail);

    for (int k = 0; k <= clicks; k += 1) {
      final xTick = left + ((right - left) * (k / clicks));
      final isEnd = k == 0 || k == clicks;
      final tickH = isEnd ? 18.0 : 13.0;
      final tickPaint = Paint()
        ..color = isEnd ? const Color(0xFF9AA6B2) : const Color(0xFF747F8D)
        ..strokeWidth = isEnd ? 2.8 : 2.0;
      canvas.drawLine(
        Offset(xTick, axisY - (tickH / 2)),
        Offset(xTick, axisY + (tickH / 2)),
        tickPaint,
      );
    }

    final current = count > 0 ? ((currentBeat % count) + count) % count : 0;
    final baseR = (30 - (count * 0.75)).clamp(7.0, 24.0);
    final maxRBySpacing = (spacing * 0.42 - 2).clamp(6.0, 1000.0);
    final normalR = math.min(baseR, maxRBySpacing);
    final activeR = math.min(normalR + 2.0, maxRBySpacing + 1.5);
    for (int i = 0; i < xs.length; i += 1) {
      final x = xs[i];
      final active = running && i == current && currentBeat >= 0;
      final r = active ? activeR : normalR;
      canvas.drawCircle(
        Offset(x, yTop),
        r,
        Paint()
          ..color = active ? const Color(0xFFFFD24A) : const Color(0xFFC8A832),
      );
      canvas.drawCircle(
        Offset(x, yTop),
        r,
        Paint()
          ..color = active ? const Color(0xFFF3DA7A) : const Color(0xFF9F8427)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );
      final tp = TextPainter(
        text: TextSpan(
          text: '${i + 1}',
          style: TextStyle(
            color: const Color(0xFF1A1A1A),
            fontSize: (normalR * 0.82).clamp(8.0, 12.0),
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(x - (tp.width / 2), yTop - (tp.height / 2)));
    }

    final p = motionProgress.clamp(0.0, 1.0);
    final ballX = direction >= 0
        ? left + ((right - left) * p)
        : right - ((right - left) * p);
    final redBall = Paint()..color = const Color(0xFFFF4D4D);
    final redBallOutline = Paint()
      ..color = const Color(0xFFB61F1F)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;
    canvas.drawCircle(Offset(ballX, axisY), 11, redBall);
    canvas.drawCircle(Offset(ballX, axisY), 11, redBallOutline);

    if (timerEnabled) {
      final total = math.max(0, timerRemaining.inSeconds);
      final mm = (total ~/ 60).toString().padLeft(2, '0');
      final ss = (total % 60).toString().padLeft(2, '0');
      final tp = TextPainter(
        text: TextSpan(
          text: '$mm:$ss',
          style: TextStyle(
            color: const Color(0xFFFFB17A),
            fontSize: math.min(44.0, size.height * 0.24),
            fontWeight: FontWeight.w800,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      tp.paint(
        canvas,
        Offset(
          (size.width - tp.width) / 2,
          axisY + ((size.height - axisY) * 0.5) - (tp.height / 2),
        ),
      );
    } else if (!running) {
      final idle = TextPainter(
        text: TextSpan(
          text: idleLabel,
          style: const TextStyle(
            color: Color(0xFF8090A8),
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      idle.paint(canvas, Offset((size.width - idle.width) / 2, axisY + 44));
    }
  }

  @override
  bool shouldRepaint(covariant _MiniMetronomePainter oldDelegate) {
    return oldDelegate.beatsPerBar != beatsPerBar ||
        oldDelegate.clicksPerBeat != clicksPerBeat ||
        oldDelegate.currentBeat != currentBeat ||
        oldDelegate.running != running ||
        oldDelegate.direction != direction ||
        oldDelegate.timerEnabled != timerEnabled ||
        oldDelegate.timerRemaining.inSeconds != timerRemaining.inSeconds ||
        oldDelegate.idleLabel != idleLabel ||
        (oldDelegate.motionProgress - motionProgress).abs() > 0.001;
  }
}

class _MiniTunerPainter extends CustomPainter {
  _MiniTunerPainter({
    required this.noteLabel,
    required this.cents,
    required this.currentFreq,
    required this.currentStringIdx,
    required this.tuningLabels,
  });

  final String noteLabel;
  final int cents;
  final double currentFreq;
  final int? currentStringIdx;
  final List<String> tuningLabels;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF000000);
    canvas.drawRect(Offset.zero & size, bg);

    final labels = tuningLabels.isEmpty
        ? const <String>['Mi', 'La', 'Re', 'Sol', 'Si', 'Mi']
        : tuningLabels;
    const ordinals = <String>['6', '5', '4', '3', '2', '1'];

    final padX = 20.0;
    final cardGap = math.max(6.0, math.min(12.0, size.width * 0.012));
    final cardsH = math.max(68.0, math.min(114.0, size.height * 0.34));
    final cardW = (size.width - (padX * 2) - (cardGap * 5)) / 6;
    final cardsY = 16.0;

    for (int i = 0; i < 6; i += 1) {
      final x = padX + i * (cardW + cardGap);
      final active = currentStringIdx == i;
      final fill = Paint()
        ..color = active ? const Color(0xFFF39C12) : const Color(0xFFD2D8DF);
      final rect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, cardsY, cardW, cardsH),
        Radius.circular(math.min(cardsH / 2, math.max(10, cardW * 0.26))),
      );
      canvas.drawRRect(rect, fill);

      final top = TextPainter(
        text: TextSpan(
          text: ordinals[i],
          style: TextStyle(
            color: active ? Colors.white : const Color(0xFF2B2E34),
            fontSize: 12,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: cardW - 4);
      top.paint(
        canvas,
        Offset(x + (cardW - top.width) / 2, cardsY + cardsH * 0.22),
      );

      final mid = TextPainter(
        text: TextSpan(
          text: labels[i % labels.length],
          style: TextStyle(
            color: active ? Colors.white : const Color(0xFF2B2E34),
            fontSize: 24,
            fontWeight: FontWeight.w800,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: cardW - 4);
      mid.paint(
        canvas,
        Offset(
          x + (cardW - mid.width) / 2,
          cardsY + cardsH * 0.54 - mid.height / 2,
        ),
      );
    }

    final liveText = currentFreq > 0.0
        ? '$noteLabel (${currentFreq.toStringAsFixed(1)} Hz)'
        : noteLabel;
    final live = TextPainter(
      text: TextSpan(
        text: liveText,
        style: const TextStyle(
          color: Color(0xFFFF9E34),
          fontSize: 30,
          fontWeight: FontWeight.w800,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: size.width - 24);
    live.paint(
      canvas,
      Offset((size.width - live.width) / 2, cardsY + cardsH + 18),
    );

    final meterTop = cardsY + cardsH + 68;
    final meterBottom = meterTop + 46;
    final meterLeft = 24.0;
    final meterRight = size.width - 24.0;
    final meterRect = RRect.fromRectAndRadius(
      Rect.fromLTRB(meterLeft, meterTop, meterRight, meterBottom),
      const Radius.circular(23),
    );
    canvas.drawRRect(meterRect, Paint()..color = const Color(0xFFC8C8CA));
    final centerX = (meterLeft + meterRight) / 2;
    canvas.drawLine(
      Offset(centerX, meterTop + 2),
      Offset(centerX, meterBottom - 2),
      Paint()
        ..color = const Color(0xFF16A05F)
        ..strokeWidth = 4,
    );
    final limited = cents.clamp(-50, 50).toDouble();
    final knobX = meterLeft + ((limited + 50) / 100) * (meterRight - meterLeft);
    canvas.drawCircle(
      Offset(knobX, (meterTop + meterBottom) / 2),
      12,
      Paint()..color = const Color(0xFFFF5A2F),
    );

    if (currentStringIdx != null) {
      final cText = TextPainter(
        text: TextSpan(
          text: '${cents >= 0 ? '+' : ''}$cents cents',
          style: const TextStyle(
            color: Color(0xFF9FB2C8),
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      cText.paint(
        canvas,
        Offset((size.width - cText.width) / 2, meterBottom + 10),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _MiniTunerPainter oldDelegate) {
    if (oldDelegate.noteLabel != noteLabel) return true;
    if (oldDelegate.cents != cents) return true;
    if ((oldDelegate.currentFreq - currentFreq).abs() > 0.01) return true;
    if (oldDelegate.currentStringIdx != currentStringIdx) return true;
    if (oldDelegate.tuningLabels.length != tuningLabels.length) return true;
    for (int i = 0; i < tuningLabels.length; i += 1) {
      if (oldDelegate.tuningLabels[i] != tuningLabels[i]) return true;
    }
    return false;
  }
}

class _MiniTunerSpectrumPainter extends CustomPainter {
  _MiniTunerSpectrumPainter({
    required this.rangeMinHz,
    required this.rangeMaxHz,
    required this.currentFreq,
    required this.currentStringIdx,
    required this.tuningLabels,
    required this.tuningFreqs,
    required this.spectrumBins,
  });

  final double rangeMinHz;
  final double rangeMaxHz;
  final double currentFreq;
  final int? currentStringIdx;
  final List<String> tuningLabels;
  final List<double> tuningFreqs;
  final List<double> spectrumBins;

  double _midiToFreq(int midi) => 440.0 * math.pow(2.0, (midi - 69) / 12.0);
  double _freqToMidi(double freq) =>
      69 + 12 * (math.log(freq / 440.0) / math.ln2);

  String _noteNameFromPc(int pc) {
    const names = <String>[
      'C',
      'C#',
      'D',
      'D#',
      'E',
      'F',
      'F#',
      'G',
      'G#',
      'A',
      'A#',
      'B',
    ];
    return names[((pc % 12) + 12) % 12];
  }

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Offset.zero & size,
      Paint()..color = const Color(0xFF0F1621),
    );
    final outer = RRect.fromRectAndRadius(
      Rect.fromLTWH(10, 10, size.width - 20, size.height - 20),
      const Radius.circular(10),
    );
    canvas.drawRRect(outer, Paint()..color = const Color(0xFF0B1018));
    canvas.drawRRect(
      outer,
      Paint()
        ..color = const Color(0xFF2F3743)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2,
    );

    final x1 = 42.0;
    final y1 = 12.0;
    final x2 = math.max(x1 + 1.0, size.width - 14.0);
    final y2 = math.max(y1 + 1.0, size.height - 30.0);
    final frameRect = Rect.fromLTRB(x1, y1, x2, y2);
    canvas.drawRect(frameRect, Paint()..color = const Color(0xFF10131A));
    canvas.drawRect(
      frameRect,
      Paint()
        ..color = const Color(0xFF465062)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.0,
    );

    final fmin = math.max(1.0, rangeMinHz);
    final fmaxRaw = math.max(10.0, rangeMaxHz);
    final fmax = fmaxRaw <= fmin + 1 ? (fmin + 1) : fmaxRaw;
    final logMin = math.log(fmin) / math.ln10;
    final logMax = math.log(fmax) / math.ln10;
    final hzTicks = <int>[
      70,
      80,
      90,
      100,
      120,
      140,
      160,
      200,
      250,
      315,
      400,
      500,
      630,
      800,
      1000,
      1250,
      1400,
      1600,
      2000,
      2500,
      3000,
    ];
    final majorHz = <int>{100, 200, 400, 800, 1000};

    double fx(double hz) {
      final safe = hz.clamp(fmin, fmax);
      final logHz = math.log(safe) / math.ln10;
      final ratio = (logHz - logMin) / math.max(1e-6, (logMax - logMin));
      return x1 + ratio.clamp(0.0, 1.0) * (x2 - x1);
    }

    for (final hz in hzTicks) {
      final h = hz.toDouble();
      if (h < fmin || h > fmax) continue;
      final x = fx(h);
      final isMajor = majorHz.contains(hz);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = isMajor ? const Color(0xFF293140) : const Color(0xFF1F2531)
          ..strokeWidth = 1,
      );
      if (isMajor) {
        final tp = TextPainter(
          text: TextSpan(
            text: '$hz',
            style: const TextStyle(color: Color(0xFF8F98A8), fontSize: 8),
          ),
          textDirection: TextDirection.ltr,
        )..layout();
        tp.paint(canvas, Offset(x - (tp.width / 2), y2 + 4));
      }
    }

    const whitePcs = <int>{0, 2, 4, 5, 7, 9, 11};
    final minMidi = math.max(0, _freqToMidi(fmin).floor() - 1);
    final maxMidi = math.min(127, _freqToMidi(fmax).ceil() + 1);
    for (int midi = minMidi; midi <= maxMidi; midi += 1) {
      final hz = _midiToFreq(midi);
      if (hz < fmin || hz > fmax) continue;
      final x = fx(hz);
      final isNatural = whitePcs.contains(midi % 12);
      final lineColor = isNatural
          ? const Color(0xFFFF9F2A)
          : const Color(0xFF8A5F22);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = lineColor
          ..strokeWidth = 1.0,
      );
      final label = _noteNameFromPc(midi % 12);
      final tp = TextPainter(
        text: TextSpan(
          text: label,
          style: TextStyle(
            color: isNatural
                ? const Color(0xFFFFBF6C)
                : const Color(0xFFB58A4F),
            fontSize: 7,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: 14);
      final labelY = y1 + (midi.isEven ? 8 : 18);
      tp.paint(canvas, Offset(x - (tp.width / 2), labelY));
    }

    if (spectrumBins.isNotEmpty) {
      final innerW = x2 - x1;
      final innerH = y2 - y1 - 6;
      final bars = spectrumBins.length;
      final barW = math.max(1.2, innerW / math.max(40, bars * 1.35));
      for (int i = 0; i < bars; i += 1) {
        final v = spectrumBins[i].clamp(0.0, 1.0);
        if (v <= 0.005) continue;
        final x = x1 + (innerW * (i / math.max(1, bars - 1)));
        final h = v * innerH;
        canvas.drawRect(
          Rect.fromLTWH(x, y2 - h, barW, h),
          Paint()..color = const Color(0xFF49B5FF),
        );
      }
    }

    final n = math.min(tuningLabels.length, tuningFreqs.length);
    for (int i = 0; i < n; i += 1) {
      final hz = tuningFreqs[i];
      if (hz < fmin || hz > fmax) continue;
      final x = fx(hz);
      final active = currentStringIdx == i;
      final color = active ? const Color(0xFFFFBF6C) : const Color(0xFFB58A4F);
      canvas.drawLine(
        Offset(x, y1 + 2),
        Offset(x, y2 - 2),
        Paint()
          ..color = color
          ..strokeWidth = active ? 2.0 : 1.2,
      );
      final tp = TextPainter(
        text: TextSpan(
          text: tuningLabels[i],
          style: TextStyle(
            color: color,
            fontSize: 9,
            fontWeight: active ? FontWeight.w700 : FontWeight.w600,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: 22);
      tp.paint(canvas, Offset(x - (tp.width / 2), y1 + (i.isEven ? 8 : 18)));
    }

    if (currentFreq > 0.0 && currentFreq >= fmin && currentFreq <= fmax) {
      final x = fx(currentFreq);
      final markerColor = const Color(0xFF49B5FF);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = markerColor
          ..strokeWidth = 2.2,
      );
      canvas.drawCircle(Offset(x, y1 + 8), 3.5, Paint()..color = markerColor);
      final tp = TextPainter(
        text: TextSpan(
          text: '${currentFreq.toStringAsFixed(1)} Hz',
          style: const TextStyle(
            color: Color(0xFF7CC8FF),
            fontSize: 10,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: math.max(80.0, x2 - x1));
      final dx = (x - (tp.width / 2)).clamp(x1, x2 - tp.width);
      tp.paint(canvas, Offset(dx, y1 + 2));
    } else if (spectrumBins.isEmpty || spectrumBins.every((v) => v < 0.01)) {
      final tp = TextPainter(
        text: const TextSpan(
          text: '-',
          style: TextStyle(
            color: Color(0xFF8796AB),
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(
        canvas,
        Offset((x1 + x2 - tp.width) / 2, (y1 + y2 - tp.height) / 2),
      );
    }

    final hzLabel = TextPainter(
      text: const TextSpan(
        text: 'Hz',
        style: TextStyle(
          color: Color(0xFFA0A8B7),
          fontSize: 9,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    hzLabel.paint(
      canvas,
      Offset(((x1 + x2) / 2) - (hzLabel.width / 2), size.height - 16),
    );
  }

  @override
  bool shouldRepaint(covariant _MiniTunerSpectrumPainter oldDelegate) {
    if ((oldDelegate.rangeMinHz - rangeMinHz).abs() > 0.01) return true;
    if ((oldDelegate.rangeMaxHz - rangeMaxHz).abs() > 0.01) return true;
    if ((oldDelegate.currentFreq - currentFreq).abs() > 0.01) return true;
    if (oldDelegate.currentStringIdx != currentStringIdx) return true;
    if (oldDelegate.tuningLabels.length != tuningLabels.length) return true;
    if (oldDelegate.tuningFreqs.length != tuningFreqs.length) return true;
    if (oldDelegate.spectrumBins.length != spectrumBins.length) return true;
    for (int i = 0; i < tuningLabels.length; i += 1) {
      if (oldDelegate.tuningLabels[i] != tuningLabels[i]) return true;
    }
    for (int i = 0; i < tuningFreqs.length; i += 1) {
      if ((oldDelegate.tuningFreqs[i] - tuningFreqs[i]).abs() > 0.001) {
        return true;
      }
    }
    for (int i = 0; i < spectrumBins.length; i += 1) {
      if ((oldDelegate.spectrumBins[i] - spectrumBins[i]).abs() > 0.01) {
        return true;
      }
    }
    return false;
  }
}
