import 'dart:math' as math;

import 'package:flutter/widgets.dart';

class ScaleStaffHitRegion {
  const ScaleStaffHitRegion({
    required this.midi,
    required this.degree,
    required this.isLeftHand,
    required this.center,
    required this.radiusX,
    required this.radiusY,
  });

  final int midi;
  final int degree;
  final bool isLeftHand;
  final Offset center;
  final double radiusX;
  final double radiusY;

  double normalizedDistanceSquared(Offset position) {
    final dx = (position.dx - center.dx) / radiusX;
    final dy = (position.dy - center.dy) / radiusY;
    return dx * dx + dy * dy;
  }
}

List<ScaleStaffHitRegion> buildScaleStaffHitRegions({
  required Size size,
  required List<int> rightHandNotes,
  required List<int> leftHandNotes,
  required int keySignatureCount,
}) {
  if (size.isEmpty || rightHandNotes.isEmpty) {
    return const <ScaleStaffHitRegion>[];
  }
  final compactWidth = size.width < 520;
  final left = compactWidth ? 28.0 : 52.0;
  final gap = math.max(10.0, math.min(16.0, size.height / 24));
  final grandGap = math.max(64.0, gap * 6.2);
  final systemHeight = grandGap + 4 * gap;
  final trebleTop = (size.height - systemHeight) / 2;
  final bassTop = trebleTop + grandGap;
  var noteStartX = left + (compactWidth ? 72.0 : 110.0);
  if (keySignatureCount > 0) {
    final signatureStep = compactWidth ? 13.5 : 18.0;
    final signatureStartX = left + (compactWidth ? 54.0 : 82.0);
    final signatureEndX =
        signatureStartX + keySignatureCount.clamp(0, 7) * signatureStep;
    noteStartX = signatureEndX + (compactWidth ? 8.0 : 12.0);
  }
  final noteStepX = compactWidth ? 24.0 : 32.0;
  final noteWidth = compactWidth ? 13.0 : 16.0;
  final noteHeight = compactWidth ? 10.0 : 12.0;
  final radiusX = math.max(14.0, noteWidth / 2 + 6.0);
  final radiusY = math.max(12.0, noteHeight / 2 + 5.0);
  final pairCount = math.min(rightHandNotes.length, leftHandNotes.length);
  final regions = <ScaleStaffHitRegion>[];
  for (var degree = 0; degree < rightHandNotes.length; degree += 1) {
    final x = noteStartX + degree * noteStepX;
    if (degree < pairCount) {
      final midi = leftHandNotes[degree];
      regions.add(
        ScaleStaffHitRegion(
          midi: midi,
          degree: degree,
          isLeftHand: true,
          center: Offset(x, _midiToBassY(midi, bassTop, gap)),
          radiusX: radiusX,
          radiusY: radiusY,
        ),
      );
    }
    final midi = rightHandNotes[degree];
    regions.add(
      ScaleStaffHitRegion(
        midi: midi,
        degree: degree,
        isLeftHand: false,
        center: Offset(x, _midiToTrebleY(midi, trebleTop, gap)),
        radiusX: radiusX,
        radiusY: radiusY,
      ),
    );
  }
  return regions;
}

ScaleStaffHitRegion? scaleStaffHitAt({
  required Offset position,
  required Size size,
  required List<int> rightHandNotes,
  required List<int> leftHandNotes,
  required int keySignatureCount,
}) {
  ScaleStaffHitRegion? best;
  var bestDistance = double.infinity;
  for (final region in buildScaleStaffHitRegions(
    size: size,
    rightHandNotes: rightHandNotes,
    leftHandNotes: leftHandNotes,
    keySignatureCount: keySignatureCount,
  )) {
    final distance = region.normalizedDistanceSquared(position);
    if (distance <= 1 && distance < bestDistance) {
      best = region;
      bestDistance = distance;
    }
  }
  return best;
}

List<ScaleStaffHitRegion> buildStaffNoteHitRegions({
  required Size size,
  required Iterable<int> notes,
  required int keySignatureCount,
  required bool preferFlats,
}) {
  final sortedNotes = notes.toSet().toList()..sort();
  if (size.isEmpty || sortedNotes.isEmpty) {
    return const <ScaleStaffHitRegion>[];
  }
  final compactWidth = size.width < 520;
  final left = compactWidth ? 28.0 : 52.0;
  final gap = math.max(10.0, math.min(16.0, size.height / 24));
  final grandGap = math.max(64.0, gap * 6.2);
  final systemHeight = grandGap + 4 * gap;
  final trebleTop = (size.height - systemHeight) / 2;
  final bassTop = trebleTop + grandGap;
  var noteStartX = left + (compactWidth ? 72.0 : 110.0);
  if (keySignatureCount > 0) {
    final signatureStep = compactWidth ? 13.5 : 18.0;
    final signatureStartX = left + (compactWidth ? 54.0 : 82.0);
    noteStartX =
        signatureStartX +
        keySignatureCount.clamp(0, 7) * signatureStep +
        (compactWidth ? 8.0 : 12.0);
  }
  final noteWidth = compactWidth ? 13.0 : 16.0;
  final noteHeight = compactWidth ? 10.0 : 12.0;
  final noteColumnStep = compactWidth ? noteWidth * 1.4 : noteWidth * 1.8;
  final overlapThreshold = math.max(1.0, noteHeight - 1.0);
  final radiusX = math.max(14.0, noteWidth / 2 + 6.0);
  final radiusY = math.max(12.0, noteHeight / 2 + 5.0);
  final placedTrebleColumns = <int, List<double>>{};
  final placedBassColumns = <int, List<double>>{};
  final regions = <ScaleStaffHitRegion>[];
  for (var index = 0; index < sortedNotes.length; index += 1) {
    final midi = sortedNotes[index];
    final treble = midi >= 60;
    final y = treble
        ? _midiToTrebleY(midi, trebleTop, gap, preferFlats)
        : _midiToBassY(midi, bassTop, gap, preferFlats);
    final placedColumns = treble ? placedTrebleColumns : placedBassColumns;
    var column = 0;
    while ((placedColumns[column] ?? const <double>[]).any(
      (previousY) => (y - previousY).abs() < overlapThreshold,
    )) {
      column += 1;
    }
    placedColumns[column] = <double>[
      ...(placedColumns[column] ?? const <double>[]),
      y,
    ];
    regions.add(
      ScaleStaffHitRegion(
        midi: midi,
        degree: index,
        isLeftHand: !treble,
        center: Offset(noteStartX + column * noteColumnStep, y),
        radiusX: radiusX,
        radiusY: radiusY,
      ),
    );
  }
  return regions;
}

ScaleStaffHitRegion? staffNoteHitAt({
  required Offset position,
  required Size size,
  required Iterable<int> notes,
  required int keySignatureCount,
  required bool preferFlats,
}) {
  ScaleStaffHitRegion? best;
  var bestDistance = double.infinity;
  for (final region in buildStaffNoteHitRegions(
    size: size,
    notes: notes,
    keySignatureCount: keySignatureCount,
    preferFlats: preferFlats,
  )) {
    final distance = region.normalizedDistanceSquared(position);
    if (distance <= 1 && distance < bestDistance) {
      best = region;
      bestDistance = distance;
    }
  }
  return best;
}

double _midiToTrebleY(
  int midi,
  double top,
  double gap, [
  bool preferFlats = false,
]) {
  const bottomLineDiatonic = 30.0;
  return top +
      4 * gap -
      (_midiToDiatonic(midi, preferFlats) - bottomLineDiatonic) * gap / 2;
}

double _midiToBassY(
  int midi,
  double top,
  double gap, [
  bool preferFlats = false,
]) {
  const bottomLineDiatonic = 18.0;
  return top +
      4 * gap -
      (_midiToDiatonic(midi, preferFlats) - bottomLineDiatonic) * gap / 2;
}

double _midiToDiatonic(int midi, [bool preferFlats = false]) {
  const sharpPitchClassToDiatonic = <int>[0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6];
  const flatPitchClassToDiatonic = <int>[0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6];
  final pitchClass = ((midi % 12) + 12) % 12;
  final octave = (midi ~/ 12) - 1;
  final table = preferFlats
      ? flatPitchClassToDiatonic
      : sharpPitchClassToDiatonic;
  return (octave * 7 + table[pitchClass]).toDouble();
}
