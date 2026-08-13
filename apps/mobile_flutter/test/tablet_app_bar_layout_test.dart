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
    expect(appBar, contains('fontSize: tabletPortrait ? 14 : null'));
    expect(appBar, contains('minWidth: tabletPortrait ? 54'));
    expect(appBar, contains('size: tabletPortrait ? 22 : null'));
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
  });
}
