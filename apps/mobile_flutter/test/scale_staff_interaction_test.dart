import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/scale_staff_interaction.dart';

void main() {
  test('finds treble and bass notes at their painted positions', () {
    const size = Size(800, 320);
    const right = <int>[60, 62, 64];
    const left = <int>[48, 50, 52];
    final regions = buildScaleStaffHitRegions(
      size: size,
      rightHandNotes: right,
      leftHandNotes: left,
      keySignatureCount: 0,
    );
    final treble = regions.firstWhere((region) => region.midi == 62);
    final bass = regions.firstWhere((region) => region.midi == 50);

    expect(
      scaleStaffHitAt(
        position: treble.center,
        size: size,
        rightHandNotes: right,
        leftHandNotes: left,
        keySignatureCount: 0,
      )?.midi,
      62,
    );
    expect(
      scaleStaffHitAt(
        position: bass.center,
        size: size,
        rightHandNotes: right,
        leftHandNotes: left,
        keySignatureCount: 0,
      )?.isLeftHand,
      isTrue,
    );
  });

  test('accounts for the key signature and ignores empty space', () {
    const size = Size(800, 320);
    final plain = buildScaleStaffHitRegions(
      size: size,
      rightHandNotes: const <int>[66],
      leftHandNotes: const <int>[],
      keySignatureCount: 0,
    ).single;
    final signed = buildScaleStaffHitRegions(
      size: size,
      rightHandNotes: const <int>[66],
      leftHandNotes: const <int>[],
      keySignatureCount: 3,
    ).single;

    expect(signed.center.dx, greaterThan(plain.center.dx));
    expect(signed.center.dx - plain.center.dx, greaterThan(50));
    expect(
      scaleStaffHitAt(
        position: Offset.zero,
        size: size,
        rightHandNotes: const <int>[66],
        leftHandNotes: const <int>[],
        keySignatureCount: 3,
      ),
      isNull,
    );
  });

  test('staff tap updates the selection and triggers scale playback', () {
    final source = File('lib/main.dart').readAsStringSync();
    final handler = source
        .split('void _playScaleStaffNote(ScaleStaffHitRegion hit)')
        .last
        .split('Future<void> _stepScaleLoop()')
        .first;

    expect(handler, contains('_scaleCurrentNote = hit.midi;'));
    expect(handler, contains('_scaleCurrentIsLeft = hit.isLeftHand;'));
    expect(
      handler,
      contains('_handleInstrumentNote(hit.midi, pressed: false)'),
    );
  });

  test('finds chord and detection notes using the generic staff layout', () {
    const size = Size(800, 320);
    const notes = <int>{48, 60, 64, 67};
    final regions = buildStaffNoteHitRegions(
      size: size,
      notes: notes,
      keySignatureCount: 3,
      preferFlats: true,
    );

    for (final region in regions) {
      expect(
        staffNoteHitAt(
          position: region.center,
          size: size,
          notes: notes,
          keySignatureCount: 3,
          preferFlats: true,
        )?.midi,
        region.midi,
      );
    }
  });

  test('grand staff separates boundary notes vertically, not horizontally', () {
    const size = Size(800, 320);
    final regions = buildStaffNoteHitRegions(
      size: size,
      notes: const <int>{59, 60},
      keySignatureCount: 0,
      preferFlats: true,
    );
    final bass = regions.firstWhere((region) => region.midi == 59);
    final treble = regions.firstWhere((region) => region.midi == 60);

    expect(bass.center.dx, treble.center.dx);
    expect((bass.center.dy - treble.center.dy).abs(), greaterThan(10));
  });

  test('finds both interval notes in their painted sequence columns', () {
    const size = Size(800, 320);
    const notes = <int>{60, 64};
    final regions = buildStaffNoteHitRegions(
      size: size,
      notes: notes,
      keySignatureCount: 0,
      preferFlats: false,
      intervalSequenceMode: true,
    );

    expect(regions, hasLength(2));
    expect(regions[1].center.dx - regions[0].center.dx, 64);
    for (final region in regions) {
      expect(
        staffNoteHitAt(
          position: region.center,
          size: size,
          notes: notes,
          keySignatureCount: 0,
          preferFlats: false,
          intervalSequenceMode: true,
        )?.midi,
        region.midi,
      );
    }
  });

  test('other note-based modes are connected to staff playback', () {
    final source = File('lib/main.dart').readAsStringSync();
    final tapBlock = source
        .split('onTapDown: (details) {')
        .last
        .split('child: CustomPaint(')
        .first;
    final handler = source
        .split('void _playGeneralStaffNote(int midi)')
        .last
        .split('Future<void> _stepScaleLoop()')
        .first;

    expect(
      tapBlock,
      contains(
        '0,\n                              1,\n                              2,\n                              5,\n                              7,\n                              9,',
      ),
    );
    expect(tapBlock, contains('staffNoteHitAt('));
    expect(
      tapBlock,
      contains('(_tabIndex == 7 && !_intervalGenHarmonic)'),
    );
    expect(
      tapBlock,
      contains('(_tabIndex == 9 && !_intervalPracticeHarmonic)'),
    );
    expect(handler, contains('if (_tabIndex == 0)'));
    expect(handler, contains('if (_tabIndex == 1 || _tabIndex == 2)'));
    expect(
      handler,
      contains('_tabIndex == 5 || _tabIndex == 7 || _tabIndex == 9'),
    );
  });

  test('generation staff selection highlights piano and guitar', () {
    final source = File('lib/main.dart').readAsStringSync();
    final instrumentHandler = source
        .split('Future<void> _handleInstrumentNote(')
        .last
        .split('Future<void> _beginInputDrag(')
        .first;
    final guitarBuilder = source
        .split('Widget _buildGuitarStrip(')
        .last
        .split('Widget _buildDetectionPage()')
        .first;

    expect(instrumentHandler, contains('_bumpGenerationNoteHighlight(midi);'));
    expect(guitarBuilder, contains('_generationNoteHighlightMidi == note'));
  });

  test('interval generation accepts matching notes in every octave', () {
    final source = File('lib/main.dart').readAsStringSync();
    final handler = source
        .split('Future<void> _handleInstrumentNote(')
        .last
        .split('Future<void> _beginInputDrag(')
        .first;

    expect(handler, contains('notes[index] % 12 == midi % 12'));
    expect(handler, contains('final aExact = notes[a] == midi;'));
    expect(handler, contains('(notes[a] - midi).abs()'));
  });

  test('interval input highlights its matching note on the regular staff', () {
    final painter = File('lib/main_painters.dart').readAsStringSync();
    final regularStaffNotes = painter
        .split('final list = notes.toList()..sort();')
        .last
        .split('if (intervalMelodyMode)')
        .first;

    expect(
      regularStaffNotes,
      contains('intervalSequenceMode && intervalPlayingIdx == i'),
    );
    expect(regularStaffNotes, contains('fillColor = const Color(0xFF4DA3EA)'));
  });
}
