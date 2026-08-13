// Círculo de quintas — lógica y dibujo alineados con `apps/web/static/app.js`.
// ignore_for_file: library_private_types_in_public_api

import 'dart:math' as math;
import 'package:flutter/material.dart';

const List<int> kCircleFifthsOrder = <int>[
  0,
  7,
  2,
  9,
  4,
  11,
  6,
  1,
  8,
  3,
  10,
  5,
];

const Map<int, String> kDiatonicDegreeSuffix = <int, String>{
  0: '',
  2: 'm',
  4: 'm',
  5: '',
  7: '',
  9: 'm',
  11: 'dim',
};

const Map<int, String> kRomanByDegree = <int, String>{
  0: 'I',
  2: 'ii',
  4: 'iii',
  5: 'IV',
  7: 'V',
  9: 'vi',
  11: 'vii°',
};

const Map<int, String> kRomanByMinorNaturalInterval = <int, String>{
  0: 'i',
  2: 'ii°',
  3: '♭III',
  5: 'iv',
  7: 'v',
  8: '♭VI',
  10: '♭VII',
};

const double kCircleSliceRad = (math.pi * 2) / 12;

({double mid, double a0, double a1}) circleSliceAngles(int i) {
  final mid = (-math.pi / 2) + (i * kCircleSliceRad);
  final half = kCircleSliceRad / 2;
  return (mid: mid, a0: mid - half, a1: mid + half);
}

int circleSliceIndexForPitchClass(int pc) {
  final p = ((pc % 12) + 12) % 12;
  for (int i = 0; i < 12; i += 1) {
    if (kCircleFifthsOrder[i] == p) return i;
  }
  return 0;
}

int chordRootPcForMajorScaleDegree(int tonicPc, int degree) {
  const inter = <int, int>{0: 0, 2: 2, 4: 4, 5: 5, 7: 7, 9: 9, 11: 11};
  return (((tonicPc + (inter[degree] ?? 0)) % 12) + 12) % 12;
}

({String suffix, int? degree}) diatonicTriadSuffixMajorKey(
  int tonicPc,
  int rootPc,
) {
  final d = (rootPc - tonicPc + 12) % 12;
  if (kDiatonicDegreeSuffix.containsKey(d)) {
    return (suffix: kDiatonicDegreeSuffix[d]!, degree: d);
  }
  return (suffix: '', degree: null);
}

({String suffix, int? interval, String roman})
diatonicTriadSuffixNaturalMinorKey(int minorTonicPc, int rootPc) {
  final d = (rootPc - minorTonicPc + 12) % 12;
  const map = <int, String>{
    0: 'm',
    2: 'dim',
    3: '',
    5: 'm',
    7: 'm',
    8: '',
    10: '',
  };
  if (!map.containsKey(d)) {
    return (suffix: '', interval: null, roman: '');
  }
  return (
    suffix: map[d]!,
    interval: d,
    roman: kRomanByMinorNaturalInterval[d] ?? '',
  );
}

int circleMinorIntervalToMajorDegreeKey(int intervalD) {
  const map = <int, int>{0: 0, 2: 11, 3: 4, 5: 5, 7: 7, 8: 9, 10: 9};
  return map[intervalD] ?? 0;
}

int relativeMinorPcFromMajorPc(int majorPc) => (majorPc + 9 + 12) % 12;

String circleMinorLabel(String Function(int pc) noteNameFromPc, int majorPc) {
  final mpc = relativeMinorPcFromMajorPc(majorPc);
  return '${noteNameFromPc(mpc)}m';
}

bool circleUpperBandIsDiatonicMajorTriad(int degree) =>
    degree == 0 || degree == 5 || degree == 7;

bool circleLowerBandIsDiatonicMinorTriad(int minorDeg) =>
    minorDeg == 2 || minorDeg == 4 || minorDeg == 9;

Color circleDiatonicSliceFillColor(int degree, int pc, int tonicPc) {
  const base = Color(0xFFF0D5B8);
  const tonic = Color(0xFFC9A06A);
  const lav = Color(0xFFDDD0E8);
  const vii = Color(0xFFF5D4DC);
  if (degree == 0) {
    return pc == tonicPc ? tonic : base;
  }
  switch (degree) {
    case 2:
    case 4:
      return lav;
    case 5:
    case 7:
      return base;
    case 11:
      return vii;
    default:
      return base;
  }
}

String circleSignatureLabelForSliceIndex(int i) {
  if (i <= 6) {
    if (i == 0) return '0';
    return '$i♯';
  }
  final fb = 12 - i;
  return '$fb♭';
}

class CircleFifthsRadii {
  CircleFifthsRadii({
    required this.rOuter,
    required this.rHole,
    required this.rSigInner,
    required this.rSig,
    required this.rMajName,
    required this.rMajRoman,
    required this.rMin,
    required this.rMinRoman,
    required this.rGuideSigMaj,
    required this.rGuideMajMin,
  });

  final double rOuter;
  final double rHole;
  final double rSigInner;
  final double rSig;
  final double rMajName;
  final double rMajRoman;
  final double rMin;
  final double rMinRoman;
  final double rGuideSigMaj;
  final double rGuideMajMin;

  static CircleFifthsRadii fromLogicalSize(double w, double h) {
    final rOuter = math.min(w, h) * 0.46;
    final rHole = rOuter * 0.18;
    final rGuideSigMajRef = rOuter * 0.775;
    final bandSig = (rOuter - rGuideSigMajRef) / 2;
    final rSigInner = rOuter - bandSig;
    final rSig = (rOuter + rSigInner) / 2;
    final rGuideMajMin = rOuter * 0.52;
    return CircleFifthsRadii(
      rOuter: rOuter,
      rHole: rHole,
      rSigInner: rSigInner,
      rSig: rSig,
      rMajName: rOuter * 0.72,
      rMajRoman: rOuter * 0.60,
      rMin: rOuter * 0.38,
      rMinRoman: rOuter * 0.292,
      rGuideSigMaj: rSigInner,
      rGuideMajMin: rGuideMajMin,
    );
  }
}

int circleMajorTonicPcForTheory(int circleTonicPc, String circleKeyMode) {
  final t = ((circleTonicPc % 12) + 12) % 12;
  if (circleKeyMode == 'minor') {
    return (t + 3 + 12) % 12;
  }
  return t;
}

({int sliceIdx, String band}) circleChordHighlightGeom(
  int tonicPcTheory,
  int chordRootPc,
  String circleKeyMode,
  int circleTonicPc,
  Map<String, dynamic>? generatedChord,
) {
  final rootFromState = ((chordRootPc % 12) + 12) % 12;
  int? rootFromApi;
  final rpc = generatedChord?['root_pc'];
  if (rpc is num && rpc.isFinite) {
    rootFromApi = (((rpc.toInt() % 12) + 12) % 12);
  }
  final root = rootFromApi ?? rootFromState;
  var suffix = '';
  final suf = generatedChord?['suffix'];
  if (suf != null && '$suf'.isNotEmpty && '$suf' != 'undefined') {
    suffix = '$suf';
  }
  if (suffix.isEmpty || suffix == 'undefined') {
    if (circleKeyMode == 'minor') {
      final mt = ((circleTonicPc % 12) + 12) % 12;
      suffix = diatonicTriadSuffixNaturalMinorKey(mt, root).suffix;
    } else {
      suffix = diatonicTriadSuffixMajorKey(tonicPcTheory, root).suffix;
    }
  }
  if (suffix == 'm') {
    final relMajPc = (root - 9 + 12) % 12;
    return (sliceIdx: circleSliceIndexForPitchClass(relMajPc), band: 'minor');
  }
  if (suffix == 'dim') {
    final relMajPc = (root + 3 + 12) % 12;
    return (sliceIdx: circleSliceIndexForPitchClass(relMajPc), band: 'minor');
  }
  return (sliceIdx: circleSliceIndexForPitchClass(root), band: 'major');
}

Color circleDegreeTextColor(int degree) {
  switch (degree) {
    case 0:
      return const Color(0xFF1B5E20);
    case 2:
      return const Color(0xFF0D47A1);
    case 4:
      return const Color(0xFFB71C1C);
    case 5:
      return const Color(0xFF1565C0);
    case 7:
      return const Color(0xFFC62828);
    case 9:
      return const Color(0xFF2E7D32);
    case 11:
      return const Color(0xFFC62828);
    default:
      return const Color(0xFF1B5E20);
  }
}

void _pathArcShort(Path path, double r, double fromAng, double toAng) {
  var delta = math.atan2(math.sin(toAng - fromAng), math.cos(toAng - fromAng));
  final steps = math.max(
    8,
    math.min(64, (48 * delta.abs() / (math.pi * 2)).ceil()),
  );
  for (int j = 1; j <= steps; j += 1) {
    final t = j / steps;
    final ang = fromAng + delta * t;
    path.lineTo(math.cos(ang) * r, math.sin(ang) * r);
  }
}

void _strokeCircleChordSelectionBand(
  Canvas canvas,
  double rOut,
  double rIn,
  double a0,
  double a1,
  double dpr,
) {
  final p = Path()..moveTo(rOut * math.cos(a0), rOut * math.sin(a0));
  p.lineTo(rIn * math.cos(a0), rIn * math.sin(a0));
  _pathArcShort(p, rIn, a0, a1);
  p.lineTo(rOut * math.cos(a1), rOut * math.sin(a1));
  _pathArcShort(p, rOut, a1, a0);
  p.close();
  canvas.drawPath(
    p,
    Paint()
      ..style = PaintingStyle.stroke
      ..color = const Color(0xFFF2BF2F)
      ..strokeWidth = math.max(2.5, 3 * dpr)
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round,
  );
}

void strokeCircleDiatonicEnvelope(
  Canvas canvas,
  int tonicPc,
  double rSigInner,
  double rGuideMajMin,
  double rHole,
  double dpr,
  String circleKeyMode,
  int circleTonicPc,
) {
  final r = <double>[rHole, rGuideMajMin, rSigInner];
  final cell = List<List<bool>>.generate(
    12,
    (_) => <bool>[false, false],
    growable: false,
  );
  final minorMode = circleKeyMode == 'minor';
  final minorTonic = minorMode ? (((circleTonicPc % 12) + 12) % 12) : null;
  if (minorMode && minorTonic != null) {
    final iiDimRoot = (minorTonic + 2 + 12) % 12;
    final iiLabelPc = (iiDimRoot + 3 + 12) % 12;
    for (int s = 0; s < 12; s += 1) {
      final pc = kCircleFifthsOrder[s];
      final mpcRel = relativeMinorPcFromMajorPc(pc);
      final dU = (pc - minorTonic + 12) % 12;
      if (<int>[3, 8, 10].contains(dU)) {
        cell[s][1] = true;
      }
      final dL = (mpcRel - minorTonic + 12) % 12;
      if (<int>[0, 5, 7].contains(dL)) {
        cell[s][0] = true;
      } else if (pc == iiLabelPc) {
        cell[s][0] = true;
      }
    }
  } else {
    final viiRootPc = chordRootPcForMajorScaleDegree(tonicPc, 11);
    final viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
    for (int s = 0; s < 12; s += 1) {
      final pc = kCircleFifthsOrder[s];
      final deg = diatonicTriadSuffixMajorKey(tonicPc, pc);
      final mpcRel = relativeMinorPcFromMajorPc(pc);
      final minorDeg = diatonicTriadSuffixMajorKey(tonicPc, mpcRel).degree;
      if (deg.degree != null &&
          circleUpperBandIsDiatonicMajorTriad(deg.degree!)) {
        cell[s][1] = true;
      }
      if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
        cell[s][0] = true;
      } else if (deg.degree != null && pc == viiLabelSlicePc) {
        cell[s][0] = true;
      }
    }
  }

  String vKey(int k, int rBand) => '$k|$rBand';
  ({int k, int rBand}) parseVKey(String key) {
    final parts = key.split('|');
    return (k: int.parse(parts[0]), rBand: int.parse(parts[1]));
  }

  ({double x, double y, double ang, double rad}) vertexXY(String key) {
    final parsed = parseVKey(key);
    final ang = circleSliceAngles(parsed.k).a0;
    final rad = r[parsed.rBand];
    return (x: math.cos(ang) * rad, y: math.sin(ang) * rad, ang: ang, rad: rad);
  }

  final edgeSet = <String>{};
  void toggleEdge(String id) {
    if (edgeSet.contains(id)) {
      edgeSet.remove(id);
    } else {
      edgeSet.add(id);
    }
  }

  for (int s = 0; s < 12; s += 1) {
    for (int b = 0; b < 2; b += 1) {
      if (!cell[s][b]) continue;
      final ri = b;
      final ro = b + 1;
      toggleEdge('arc|$s|$ro');
      toggleEdge('arc|$s|$ri');
      toggleEdge('rad|$s|$ri|$ro');
      toggleEdge('rad|${(s + 1) % 12}|$ri|$ro');
    }
  }

  final adj = <String, List<String>>{};
  void addAdj(String a, String b) {
    adj.putIfAbsent(a, () => <String>[]);
    adj[a]!.add(b);
  }

  final segByEndpoints = <String, Map<String, Object>>{};
  String undirKey(String a, String b) => a.compareTo(b) < 0 ? '$a↔$b' : '$b↔$a';

  for (final eid in edgeSet) {
    final parts = eid.split('|');
    final type = parts[0];
    if (type == 'arc') {
      final s = int.parse(parts[1]);
      final rBand = int.parse(parts[2]);
      final k0 = vKey(s, rBand);
      final k1 = vKey((s + 1) % 12, rBand);
      final a0 = circleSliceAngles(s).a0;
      final a1 = circleSliceAngles(s).a1;
      addAdj(k0, k1);
      addAdj(k1, k0);
      segByEndpoints[undirKey(k0, k1)] = <String, Object>{
        'kind': 'arc',
        'r': r[rBand],
        'a0': a0,
        'a1': a1,
      };
    } else {
      final k = int.parse(parts[1]);
      final ri = int.parse(parts[2]);
      final ro = int.parse(parts[3]);
      final ka = vKey(k, ri);
      final kb = vKey(k, ro);
      final ang = circleSliceAngles(k).a0;
      addAdj(ka, kb);
      addAdj(kb, ka);
      segByEndpoints[undirKey(ka, kb)] = <String, Object>{
        'kind': 'rad',
        'ang': ang,
        'r0': r[ri],
        'r1': r[ro],
      };
    }
  }

  int ivIdx;
  if (minorMode && minorTonic != null) {
    final ivMajorPc = (minorTonic + 8 + 12) % 12;
    ivIdx = circleSliceIndexForPitchClass(ivMajorPc);
  } else {
    ivIdx = circleSliceIndexForPitchClass(
      chordRootPcForMajorScaleDegree(tonicPc, 5),
    );
  }
  final startKey = vKey(ivIdx, 2);
  if (!adj.containsKey(startKey) ||
      (adj[startKey] ?? const <String>[]).isEmpty) {
    return;
  }

  final firstNeighbor = vKey((ivIdx + 1) % 12, 2);

  void circlePathArcShortOnPath(
    Path path,
    double rad,
    double fromAng,
    double toAng,
  ) {
    var delta = math.atan2(
      math.sin(toAng - fromAng),
      math.cos(toAng - fromAng),
    );
    final steps = math.max(
      8,
      math.min(64, (48 * delta.abs() / (math.pi * 2)).ceil()),
    );
    for (int j = 1; j <= steps; j += 1) {
      final t = j / steps;
      final ang = fromAng + delta * t;
      path.lineTo(math.cos(ang) * rad, math.sin(ang) * rad);
    }
  }

  final pathKeys = <String>[startKey];
  var cur = startKey;
  String? prev;
  final maxSteps = edgeSet.length * 4 + 24;
  for (int step = 0; step < maxSteps; step += 1) {
    final neigh = (adj[cur] ?? const <String>[])
        .where((n) => n != prev)
        .toList();
    if (neigh.isEmpty) break;
    late String next;
    if (prev == null) {
      next = neigh.contains(firstNeighbor) ? firstNeighbor : neigh.first;
    } else {
      next = neigh.first;
    }
    prev = cur;
    cur = next;
    pathKeys.add(cur);
    if (cur == startKey) break;
  }

  final path = Path();
  final p0 = vertexXY(pathKeys[0]);
  path.moveTo(p0.x, p0.y);
  for (int i = 0; i < pathKeys.length - 1; i += 1) {
    final a = pathKeys[i];
    final b = pathKeys[i + 1];
    final seg = segByEndpoints[undirKey(a, b)];
    if (seg == null) continue;
    final kind = seg['kind'] as String?;
    if (kind == 'arc') {
      final va = vertexXY(a);
      final vb = vertexXY(b);
      final sr = seg['r']! as double;
      circlePathArcShortOnPath(path, sr, va.ang, vb.ang);
    } else {
      final vb = vertexXY(b);
      path.lineTo(vb.x, vb.y);
    }
  }
  path.close();
  canvas.drawPath(
    path,
    Paint()
      ..style = PaintingStyle.stroke
      ..color = const Color(0xFF0A0A0A)
      ..strokeWidth = math.max(4, 4.8 * dpr)
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round,
  );
}

/// Pintado del círculo (coordenadas con origen en el centro del widget).
class CircleOfFifthsPainter extends CustomPainter {
  CircleOfFifthsPainter({
    required this.devicePixelRatio,
    required this.circleTonicPc,
    required this.circleKeyMode,
    required this.circleChordRootPc,
    required this.generatedChord,
    required this.noteNameFromPc,
  });

  final double devicePixelRatio;
  final int circleTonicPc;
  final String circleKeyMode;
  final int circleChordRootPc;
  final Map<String, dynamic>? generatedChord;
  final String Function(int pc) noteNameFromPc;

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final dpr = devicePixelRatio.clamp(1.0, 2.0);
    canvas.save();
    final cx = size.width / 2;
    final cy = size.height / 2;
    canvas.translate(cx, cy);

    final rad = CircleFifthsRadii.fromLogicalSize(w, h);
    final rOuter = rad.rOuter;
    final rHole = rad.rHole;
    final rSigInner = rad.rSigInner;
    final rSig = rad.rSig;
    final rMajName = rad.rMajName;
    final rMajRoman = rad.rMajRoman;
    final rMin = rad.rMin;
    final rMinRoman = rad.rMinRoman;
    final rGuideMajMin = rad.rGuideMajMin;
    final rGuideSigMaj = rad.rGuideSigMaj;

    final tonicTheory = circleMajorTonicPcForTheory(
      circleTonicPc,
      circleKeyMode,
    );
    final chordRoot = ((circleChordRootPc % 12) + 12) % 12;
    final viiRootPc = chordRootPcForMajorScaleDegree(tonicTheory, 11);
    final viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
    final minorMode = circleKeyMode == 'minor';
    final minorTonic = minorMode ? (((circleTonicPc % 12) + 12) % 12) : null;
    final relMajFromMinor = minorMode && minorTonic != null
        ? (minorTonic + 3 + 12) % 12
        : null;
    final iiDimRootMinor = minorMode && minorTonic != null
        ? (minorTonic + 2 + 12) % 12
        : null;
    final iiLabelPcMinor = minorMode && iiDimRootMinor != null
        ? (iiDimRootMinor + 3 + 12) % 12
        : null;

    final fsSig = math.max(10.0, math.min(24.0, 0.026 * w));
    final fsMaj = math.max(14.0, math.min(32.0, 0.036 * w));
    final fsMajR = math.max(12.0, math.min(28.0, 0.03 * w));
    final fsMin = math.max(13.0, math.min(30.0, 0.034 * w));
    final fsMinR = math.max(11.0, math.min(26.0, 0.028 * w));

    final bg = Paint()..color = const Color(0xFF1A2330);
    canvas.drawRect(Rect.fromLTWH(-cx, -cy, size.width, size.height), bg);

    const sigRingFill = Color(0xFFFFFFFF);
    const sigRingStroke = Color(0xA6C8CDD7);
    const grayFill = Color(0xFF3D4658);

    for (int i = 0; i < 12; i += 1) {
      final pc = kCircleFifthsOrder[i];
      final ang = circleSliceAngles(i);
      final a0 = ang.a0;
      final a1 = ang.a1;
      final mpcRel = relativeMinorPcFromMajorPc(pc);
      var upperFill = grayFill;
      var lowerFill = grayFill;
      if (minorMode && minorTonic != null && relMajFromMinor != null) {
        final dU = (pc - minorTonic + 12) % 12;
        if (<int>[3, 8, 10].contains(dU)) {
          final mk = circleMinorIntervalToMajorDegreeKey(dU);
          upperFill = circleDiatonicSliceFillColor(mk, pc, relMajFromMinor);
        }
        final dL = (mpcRel - minorTonic + 12) % 12;
        if (<int>[0, 5, 7].contains(dL)) {
          final mk = circleMinorIntervalToMajorDegreeKey(dL);
          lowerFill = dL == 0
              ? circleDiatonicSliceFillColor(0, pc, relMajFromMinor)
              : circleDiatonicSliceFillColor(mk, mpcRel, tonicTheory);
        } else if (iiLabelPcMinor != null &&
            pc == iiLabelPcMinor &&
            iiDimRootMinor != null) {
          lowerFill = circleDiatonicSliceFillColor(
            11,
            iiDimRootMinor,
            tonicTheory,
          );
        }
      } else {
        final deg = diatonicTriadSuffixMajorKey(tonicTheory, pc);
        final minorDeg = diatonicTriadSuffixMajorKey(
          tonicTheory,
          mpcRel,
        ).degree;
        final diatonic = deg.degree != null;
        if (diatonic &&
            deg.degree != null &&
            circleUpperBandIsDiatonicMajorTriad(deg.degree!)) {
          upperFill = circleDiatonicSliceFillColor(
            deg.degree!,
            pc,
            tonicTheory,
          );
        }
        if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
          lowerFill = circleDiatonicSliceFillColor(
            minorDeg,
            mpcRel,
            tonicTheory,
          );
        } else if (diatonic && pc == viiLabelSlicePc) {
          lowerFill = circleDiatonicSliceFillColor(11, viiRootPc, tonicTheory);
        }
      }

      final p1 = Path()
        ..moveTo(rOuter * math.cos(a0), rOuter * math.sin(a0))
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rOuter),
          a0,
          a1 - a0,
          false,
        )
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rSigInner),
          a1,
          a0 - a1,
          false,
        )
        ..close();
      canvas.drawPath(p1, Paint()..color = sigRingFill);
      canvas.drawPath(
        p1,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = sigRingStroke
          ..strokeWidth = math.max(1, 1.05 * dpr),
      );

      final p2 = Path()
        ..moveTo(rSigInner * math.cos(a0), rSigInner * math.sin(a0))
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rSigInner),
          a0,
          a1 - a0,
          false,
        )
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rGuideMajMin),
          a1,
          a0 - a1,
          false,
        )
        ..close();
      canvas.drawPath(p2, Paint()..color = upperFill);

      final p3 = Path()
        ..moveTo(rGuideMajMin * math.cos(a0), rGuideMajMin * math.sin(a0))
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rGuideMajMin),
          a0,
          a1 - a0,
          false,
        )
        ..arcTo(
          Rect.fromCircle(center: Offset.zero, radius: rHole),
          a1,
          a0 - a1,
          false,
        )
        ..close();
      canvas.drawPath(p3, Paint()..color = lowerFill);
    }

    final guidePaint = Paint()
      ..style = PaintingStyle.stroke
      ..color = const Color(0x48E2E8F2)
      ..strokeWidth = math.max(1, 1.15 * dpr);
    canvas.drawCircle(Offset.zero, rGuideSigMaj, guidePaint);
    canvas.drawCircle(Offset.zero, rGuideMajMin, guidePaint);

    canvas.drawCircle(
      Offset.zero,
      rHole,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = const Color(0x66E2E8F2)
        ..strokeWidth = math.max(1, 1.05 * dpr),
    );

    final radPaint = Paint()
      ..style = PaintingStyle.stroke
      ..color = const Color(0xE6FFFFFF)
      ..strokeWidth = math.max(1.2, 1.35 * dpr)
      ..strokeCap = StrokeCap.round;
    for (int ri = 0; ri < 12; ri += 1) {
      final a1 = circleSliceAngles(ri).a1;
      final ca = math.cos(a1);
      final sa = math.sin(a1);
      canvas.drawLine(
        Offset(rHole * ca, rHole * sa),
        Offset(rOuter * ca, rOuter * sa),
        radPaint,
      );
    }

    strokeCircleDiatonicEnvelope(
      canvas,
      tonicTheory,
      rSigInner,
      rGuideMajMin,
      rHole,
      dpr,
      circleKeyMode,
      circleTonicPc,
    );

    final hl = circleChordHighlightGeom(
      tonicTheory,
      chordRoot,
      circleKeyMode,
      circleTonicPc,
      generatedChord,
    );
    final ha = circleSliceAngles(hl.sliceIdx);
    final ha0 = ha.a0;
    final ha1 = ha.a1;
    final selInset = math.max(2.5, 3.2 * dpr);
    var rHiOut = rSigInner - selInset;
    var rHiIn = rGuideMajMin + selInset;
    if (hl.band == 'minor') {
      rHiOut = rGuideMajMin - selInset;
      rHiIn = rHole + selInset;
    }
    _strokeCircleChordSelectionBand(canvas, rHiOut, rHiIn, ha0, ha1, dpr);

    for (int i = 0; i < 12; i += 1) {
      final pc = kCircleFifthsOrder[i];
      final mid = circleSliceAngles(i).mid;
      final cos = math.cos(mid);
      final sin = math.sin(mid);
      final sigLabel = circleSignatureLabelForSliceIndex(i);
      final majorName = noteNameFromPc(pc);
      final minorName = circleMinorLabel(noteNameFromPc, pc);

      _drawCenteredText(
        canvas,
        sigLabel,
        Offset(cos * rSig, sin * rSig),
        TextStyle(
          color: const Color(0xFF0D0D0D),
          fontSize: fsSig,
          fontWeight: FontWeight.w800,
        ),
      );

      if (minorMode &&
          minorTonic != null &&
          iiDimRootMinor != null &&
          iiLabelPcMinor != null) {
        final dU = (pc - minorTonic + 12) % 12;
        final dL = (relativeMinorPcFromMajorPc(pc) - minorTonic + 12) % 12;
        final hasUpperDiat = <int>[3, 8, 10].contains(dU);
        final hasLowerDiat = <int>[0, 5, 7].contains(dL);
        final isIiDimSector = pc == iiLabelPcMinor;
        if (hasUpperDiat) {
          final mk = circleMinorIntervalToMajorDegreeKey(dU);
          _drawCenteredText(
            canvas,
            majorName,
            Offset(cos * rMajName, sin * rMajName),
            TextStyle(
              color: circleDegreeTextColor(mk),
              fontSize: fsMaj,
              fontWeight: FontWeight.w800,
            ),
          );
          _drawRomanMaybeFlat(
            canvas,
            kRomanByMinorNaturalInterval[dU] ?? '',
            Offset(cos * rMajRoman, sin * rMajRoman),
            fsMajR,
          );
        } else {
          _drawCenteredText(
            canvas,
            majorName,
            Offset(cos * rMajName, sin * rMajName),
            TextStyle(
              color: const Color(0xFFA8B0BD),
              fontSize: fsMaj,
              fontWeight: FontWeight.w800,
            ),
          );
        }
        if (isIiDimSector) {
          final rSimVii = rOuter * 0.405;
          final dimChordLabel = '${noteNameFromPc(iiDimRootMinor)}°';
          _drawCenteredText(
            canvas,
            dimChordLabel,
            Offset(cos * rSimVii, sin * rSimVii),
            TextStyle(
              color: circleDegreeTextColor(11),
              fontSize: fsMin,
              fontWeight: FontWeight.w800,
            ),
          );
          _drawRomanMaybeFlat(
            canvas,
            kRomanByMinorNaturalInterval[2] ?? '',
            Offset(cos * rMinRoman, sin * rMinRoman),
            fsMinR,
          );
        } else if (hasLowerDiat) {
          final mk = circleMinorIntervalToMajorDegreeKey(dL);
          _drawCenteredText(
            canvas,
            minorName,
            Offset(cos * rMin, sin * rMin),
            TextStyle(
              color: circleDegreeTextColor(mk),
              fontSize: fsMin,
              fontWeight: FontWeight.w800,
            ),
          );
          _drawRomanMaybeFlat(
            canvas,
            kRomanByMinorNaturalInterval[dL] ?? '',
            Offset(cos * rMinRoman, sin * rMinRoman),
            fsMinR,
          );
        } else {
          _drawCenteredText(
            canvas,
            minorName,
            Offset(cos * rMin, sin * rMin),
            TextStyle(
              color: const Color(0xFF8B95A3),
              fontSize: fsMin,
              fontWeight: FontWeight.w800,
            ),
          );
        }
      } else {
        final mpcRel = relativeMinorPcFromMajorPc(pc);
        final deg = diatonicTriadSuffixMajorKey(tonicTheory, pc);
        final diatonic = deg.degree != null;
        final minorDeg = diatonicTriadSuffixMajorKey(
          tonicTheory,
          mpcRel,
        ).degree;
        if (diatonic) {
          if (deg.degree != null &&
              circleUpperBandIsDiatonicMajorTriad(deg.degree!)) {
            _drawCenteredText(
              canvas,
              majorName,
              Offset(cos * rMajName, sin * rMajName),
              TextStyle(
                color: circleDegreeTextColor(deg.degree!),
                fontSize: fsMaj,
                fontWeight: FontWeight.w800,
              ),
            );
            _drawCenteredText(
              canvas,
              kRomanByDegree[deg.degree!] ?? '',
              Offset(cos * rMajRoman, sin * rMajRoman),
              TextStyle(
                color: circleDegreeTextColor(deg.degree!),
                fontSize: fsMajR,
                fontWeight: FontWeight.w500,
              ),
            );
          } else if (deg.degree == 11) {
            _drawCenteredText(
              canvas,
              majorName,
              Offset(cos * rMajName, sin * rMajName),
              const TextStyle(
                color: Color(0xFFA8B0BD),
                fontWeight: FontWeight.w800,
              ).copyWith(fontSize: fsMaj),
            );
          } else {
            _drawCenteredText(
              canvas,
              majorName,
              Offset(cos * rMajName, sin * rMajName),
              const TextStyle(
                color: Color(0xFFA8B0BD),
                fontWeight: FontWeight.w800,
              ).copyWith(fontSize: fsMaj),
            );
          }
          if (minorDeg == 11) {
            final simLabel = '${noteNameFromPc(viiRootPc)}m';
            final rSimVii = rOuter * 0.405;
            _drawCenteredText(
              canvas,
              simLabel,
              Offset(cos * rSimVii, sin * rSimVii),
              TextStyle(
                color: circleDegreeTextColor(11),
                fontSize: fsMin,
                fontWeight: FontWeight.w800,
              ),
            );
            _drawCenteredText(
              canvas,
              kRomanByDegree[11] ?? '',
              Offset(cos * rMinRoman, sin * rMinRoman),
              TextStyle(color: circleDegreeTextColor(11), fontSize: fsMinR),
            );
          } else if (minorDeg != null &&
              circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
            _drawCenteredText(
              canvas,
              minorName,
              Offset(cos * rMin, sin * rMin),
              TextStyle(
                color: circleDegreeTextColor(minorDeg),
                fontSize: fsMin,
                fontWeight: FontWeight.w800,
              ),
            );
            _drawCenteredText(
              canvas,
              kRomanByDegree[minorDeg] ?? '',
              Offset(cos * rMinRoman, sin * rMinRoman),
              TextStyle(
                color: circleDegreeTextColor(minorDeg),
                fontSize: fsMinR,
              ),
            );
          } else {
            _drawCenteredText(
              canvas,
              minorName,
              Offset(cos * rMin, sin * rMin),
              const TextStyle(
                color: Color(0xFF8B95A3),
                fontWeight: FontWeight.w800,
              ).copyWith(fontSize: fsMin),
            );
          }
        } else {
          _drawCenteredText(
            canvas,
            majorName,
            Offset(cos * rMajName, sin * rMajName),
            const TextStyle(
              color: Color(0xFFA8B0BD),
              fontWeight: FontWeight.w800,
            ).copyWith(fontSize: fsMaj),
          );
          _drawCenteredText(
            canvas,
            minorName,
            Offset(cos * rMin, sin * rMin),
            const TextStyle(
              color: Color(0xFF8B95A3),
              fontWeight: FontWeight.w800,
            ).copyWith(fontSize: fsMin),
          );
        }
      }
    }

    canvas.restore();
  }

  void _drawCenteredText(
    Canvas canvas,
    String text,
    Offset o,
    TextStyle style,
  ) {
    if (text.isEmpty) return;
    final tp = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, o - Offset(tp.width / 2, tp.height / 2));
  }

  void _drawRomanMaybeFlat(
    Canvas canvas,
    String roman,
    Offset o,
    double fsRoman,
  ) {
    if (roman.isEmpty) return;
    const flat = '♭';
    if (!roman.startsWith(flat)) {
      _drawCenteredText(
        canvas,
        roman,
        o,
        TextStyle(
          fontSize: fsRoman,
          fontWeight: FontWeight.w600,
          color: const Color(0xFF0D0D0D),
        ),
      );
      return;
    }
    final body = roman.substring(1);
    final supFs = math.max(7.0, (fsRoman * 0.58).roundToDouble());
    final rise = (fsRoman * 0.4).roundToDouble();
    final flatTp = TextPainter(
      text: TextSpan(
        text: flat,
        style: TextStyle(fontSize: supFs, fontWeight: FontWeight.w600),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    final bodyTp = TextPainter(
      text: TextSpan(
        text: body,
        style: TextStyle(fontSize: fsRoman, fontWeight: FontWeight.w600),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    final gap = math.max(2.0, fsRoman * 0.14);
    final total = flatTp.width + gap + bodyTp.width;
    var drawX = o.dx - total / 2;
    flatTp.paint(canvas, Offset(drawX, o.dy - rise - flatTp.height / 2));
    drawX += flatTp.width + gap;
    bodyTp.paint(canvas, Offset(drawX, o.dy - bodyTp.height / 2));
  }

  @override
  bool shouldRepaint(covariant CircleOfFifthsPainter oldDelegate) {
    return oldDelegate.circleTonicPc != circleTonicPc ||
        oldDelegate.circleKeyMode != circleKeyMode ||
        oldDelegate.circleChordRootPc != circleChordRootPc ||
        oldDelegate.generatedChord != generatedChord ||
        oldDelegate.devicePixelRatio != devicePixelRatio;
  }
}

/// Geometría de hit-test (mismas fórmulas que en web).
class CircleFifthsHit {
  CircleFifthsHit._();

  static int sliceIndexFromLocal(Offset local, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final dx = local.dx - cx;
    final dy = local.dy - cy;
    final a = math.atan2(dy, dx);
    final t = (a + math.pi / 2 + math.pi * 2) % (math.pi * 2);
    return ((t + kCircleSliceRad / 2) / kCircleSliceRad).floor() % 12;
  }

  static bool? clickInnerMinorBand(Offset local, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final dx = local.dx - cx;
    final dy = local.dy - cy;
    final dist = math.sqrt(dx * dx + dy * dy);
    final rad = CircleFifthsRadii.fromLogicalSize(size.width, size.height);
    if (dist < rad.rHole * 1.02 || dist > rad.rOuter * 1.02) return null;
    return dist < rad.rGuideMajMin;
  }

  static int? chordRootPcFromClick(
    Offset local,
    Size size, {
    required bool shiftClick,
  }) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final dx = local.dx - cx;
    final dy = local.dy - cy;
    final dist = math.sqrt(dx * dx + dy * dy);
    final rad = CircleFifthsRadii.fromLogicalSize(size.width, size.height);
    if (dist < rad.rHole * 1.02 || dist > rad.rOuter * 1.02) return null;
    final idx = sliceIndexFromLocal(local, size);
    final majorPc = kCircleFifthsOrder[idx];
    if (!shiftClick) {
      if (dist < rad.rGuideMajMin) {
        return (majorPc + 9) % 12;
      }
      return (majorPc % 12 + 12) % 12;
    }
    if (dist < rad.rGuideMajMin) {
      return (majorPc + 9) % 12;
    }
    return (majorPc % 12 + 12) % 12;
  }

  static bool chordShiftClickIsDiatonic(
    int tonicPcTheory,
    Offset local,
    Size size,
    String circleKeyMode,
    int circleTonicPc,
  ) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final dx = local.dx - cx;
    final dy = local.dy - cy;
    final dist = math.sqrt(dx * dx + dy * dy);
    final rad = CircleFifthsRadii.fromLogicalSize(size.width, size.height);
    if (dist < rad.rHole * 1.02 || dist > rad.rOuter * 1.02) return false;
    final idx = sliceIndexFromLocal(local, size);
    final majorPc = kCircleFifthsOrder[idx];
    final innerMinorBand = dist < rad.rGuideMajMin;
    if (circleKeyMode == 'minor') {
      final minorTonic = ((circleTonicPc % 12) + 12) % 12;
      if (!innerMinorBand) {
        final dU = (majorPc - minorTonic + 12) % 12;
        return <int>[3, 8, 10].contains(dU);
      }
      final rootMinor = (majorPc + 9 + 12) % 12;
      return diatonicTriadSuffixNaturalMinorKey(
            minorTonic,
            rootMinor,
          ).interval !=
          null;
    }
    final viiRootPc = chordRootPcForMajorScaleDegree(tonicPcTheory, 11);
    final viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
    if (!innerMinorBand) {
      final deg = diatonicTriadSuffixMajorKey(tonicPcTheory, majorPc);
      return deg.degree != null &&
          circleUpperBandIsDiatonicMajorTriad(deg.degree!);
    }
    final rootMinor = (majorPc + 9 + 12) % 12;
    final minorDeg = diatonicTriadSuffixMajorKey(
      tonicPcTheory,
      rootMinor,
    ).degree;
    if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
      return true;
    }
    if (minorDeg == 11 && majorPc == viiLabelSlicePc) return true;
    return false;
  }
}
