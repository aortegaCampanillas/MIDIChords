import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/piano_scroll_centering.dart';

void main() {
  test('centers the piano when entering detection and theory modes', () {
    expect(modeUsesCenteredTheoryPiano(0), isTrue);
    expect(modeUsesCenteredTheoryPiano(1), isTrue);
    expect(modeUsesCenteredTheoryPiano(3), isTrue);
    expect(modeUsesCenteredTheoryPiano(5), isTrue);
    expect(modeUsesCenteredTheoryPiano(8), isTrue);
    expect(modeUsesCenteredTheoryPiano(9), isTrue);
  });

  test('does not recenter unrelated modes', () {
    expect(modeUsesCenteredTheoryPiano(4), isFalse);
    expect(modeUsesCenteredTheoryPiano(6), isFalse);
    expect(modeUsesCenteredTheoryPiano(2), isFalse);
    expect(modeUsesCenteredTheoryPiano(7), isFalse);
  });

  test('remembers an independent scroll position for every theory mode', () {
    final memory = PianoScrollMemory();

    expect(memory.hasOffset(1), isFalse);
    memory.remember(0, 96.0);
    memory.remember(1, 128.5);
    memory.remember(2, 242.0);
    memory.remember(9, 314.0);

    expect(memory.offsetFor(0), 96.0);
    expect(memory.offsetFor(1), 128.5);
    expect(memory.offsetFor(2), 242.0);
    expect(memory.offsetFor(9), 314.0);
    expect(memory.hasOffset(3), isFalse);
  });

  test('ignores scroll positions from unrelated modes', () {
    final memory = PianoScrollMemory()..remember(4, 80);

    expect(memory.hasOffset(4), isFalse);
  });

  test('clears remembered positions when the piano viewport changes', () {
    final memory = PianoScrollMemory()
      ..remember(0, 80)
      ..remember(1, 160);

    memory.clear();

    expect(memory.hasOffset(0), isFalse);
    expect(memory.hasOffset(1), isFalse);
  });

  test('mode selection and piano toggle restore the saved position', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(source, contains('_rememberPianoScrollForMode(_tabIndex);'));
    expect(source, contains('_requestPianoScrollForMode(value);'));
    expect(source, contains('_requestPianoScrollForMode(_tabIndex);'));
  });

  test('startup centering retries until the piano scroll view is mounted', () {
    final source = File('lib/main.dart').readAsStringSync();
    final syncMethod = source
        .split('void _syncPianoScrollToMiddleC')
        .last
        .split('void _stopHeldChord')
        .first;

    expect(source, contains('_needsPianoScrollSync = true;'));
    expect(syncMethod, contains('if (!_pianoScrollController.hasClients)'));
    expect(syncMethod, contains('attempt(retriesLeft - 1, lastMaxExt);'));
    expect(syncMethod, contains('anchorMidi = _kPianoMiddleCMidi;'));
    expect(syncMethod, contains('(previousViewportW - viewportW).abs() > 1'));
    expect(syncMethod, contains('_pianoScrollMemory.clear();'));
    expect(syncMethod, contains('_pendingPianoScrollOffset = null;'));
  });

  test('restored startup mode schedules a fresh mandatory C4 centering', () {
    final source = File('lib/main.dart').readAsStringSync();
    final preferenceLoad = source
        .split('Future<void> _loadPrefsAndStart()')
        .last
        .split('Future<void> _savePrefs()')
        .first;
    final syncMethod = source
        .split('void _syncPianoScrollToMiddleC')
        .last
        .split('void _stopHeldChord')
        .first;

    expect(preferenceLoad, contains('_pendingPianoScrollOffset = null;'));
    expect(preferenceLoad, contains('_startupPianoCenterPending = true;'));
    expect(preferenceLoad, contains('_needsPianoScrollSync = true;'));
    expect(preferenceLoad, contains('_pianoScrollSyncGeneration += 1;'));
    expect(
      preferenceLoad.indexOf('await _loadChangelog();'),
      lessThan(preferenceLoad.indexOf('_startupPianoCenterPending = true;')),
    );
    expect(syncMethod, contains('!forceMiddleC && _tabIndex == 3'));
    expect(
      syncMethod,
      contains('syncGeneration != _pianoScrollSyncGeneration'),
    );
  });

  test('C key labels include the octave when note names are visible', () {
    final source = File('lib/main.dart').readAsStringSync();
    final labelHelper = source
        .split('String _pianoKeyLabel(int midi)')
        .last
        .split('String _pcLabelCanonical')
        .first;

    expect(labelHelper, contains("midi % 12 == 0"));
    expect(labelHelper, contains(r"'$label${midi ~/ 12 - 1}'"));
    expect(source, contains('_pianoKeyLabel(midi)'));
  });
}
