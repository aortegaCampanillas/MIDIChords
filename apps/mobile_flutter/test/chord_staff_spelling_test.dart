import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/widgets.dart';
import 'package:midichords/chord_staff_spelling.dart';
import 'package:midichords/scale_staff_interaction.dart';

void main() {
  test('C7 spells and positions its minor seventh as B flat', () {
    final preferences = chordStaffNotePreferFlats(
      chord: <String, dynamic>{
        'notes_midi': <int>[60, 64, 67, 70],
        'notes': <String>['Do4', 'Mi4', 'Sol4', 'Si♭4'],
      },
      displayToSourceNote: const <int, int>{60: 60, 64: 64, 67: 67, 70: 70},
    );

    expect(preferences[70], isTrue);
    final flat = buildStaffNoteHitRegions(
      size: const Size(800, 320),
      notes: const <int>[70],
      keySignatureCount: 0,
      preferFlats: false,
      notePreferFlats: preferences,
    ).single;
    final sharp = buildStaffNoteHitRegions(
      size: const Size(800, 320),
      notes: const <int>[70],
      keySignatureCount: 0,
      preferFlats: false,
    ).single;

    expect(flat.center.dy, isNot(sharp.center.dy));
  });
}
