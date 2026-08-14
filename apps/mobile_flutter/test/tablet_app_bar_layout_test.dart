import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('tablet portrait uses the compact main app bar layout', () {
    final source = File('lib/main.dart').readAsStringSync();
    final appBar = source
        .split('appBar: AppBar(')
        .last
        .split('body: Container(')
        .first;

    expect(
      source,
      contains('final tabletPortrait = !compactPhone && portrait;'),
    );
    expect(appBar, contains('(tabletPortrait ? 220.0 : 340.0)'));
    expect(appBar, contains('centerTitle: tabletPortrait'));
    expect(appBar, contains('(tabletPortrait ? 14 : 24)'));
    expect(appBar, contains('(tabletPortrait ? 220.0 : 340.0)'));
    expect(appBar, contains('tabletPortrait ? 14 : null'));
    expect(appBar, contains('tabletPortrait ? 54'));
    expect(appBar, contains('tabletPortrait ? 22 : null'));
    expect(appBar, contains('(portrait ? 60 : 50)'));
    expect(appBar, contains('(portrait ? 260.0 : 230.0)'));
    expect(appBar, contains('minWidth: compactLandscape'));
    expect(appBar, contains('? 44'));
    expect(
      'height: compactLandscape ? 34 : null'.allMatches(appBar),
      hasLength(2),
    );
    expect(appBar, contains('isDense: compactLandscape'));
  });

  test('tablet portrait gives more width to the piano and guitar', () {
    final source = File('lib/main.dart').readAsStringSync();
    final instrumentPanel = source
        .split('Widget _buildInstrumentPanel')
        .last
        .split('void _scrollGuitarToNut()')
        .first;

    expect('width: 64'.allMatches(instrumentPanel), hasLength(3));
    expect(instrumentPanel, contains('Size(52, 40)'));
    expect(instrumentPanel, contains('Icons.piano'));
    expect(instrumentPanel, contains("const Text('🎸'"));
    expect(instrumentPanel, contains('Icons.back_hand_outlined'));
    expect(instrumentPanel, contains('flipX: !rightHanded'));
    expect('Semantics('.allMatches(instrumentPanel), hasLength(2));
    expect('Tooltip('.allMatches(instrumentPanel), hasLength(2));
    expect(
      instrumentPanel,
      contains('compactPhone && portrait && showRightControls'),
    );
    expect(
      instrumentPanel,
      contains("_instrumentView == 'guitar' ? 132.0 : 104.0"),
    );
    expect(source, contains('compactChordGuitar ? 15.0 : 11.0'));
  });
}
