import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('scales uses compact controls on phones', () {
    final pages = File('lib/main_pages.dart').readAsStringSync();
    final scalesPage = pages
        .split('Widget _buildScaleGenerationPage()')
        .last
        .split('Widget _buildScaleFingeringRow')
        .first;

    expect(
      scalesPage,
      contains('final compactPhone = _isCompactPhone(context);'),
    );
    expect(scalesPage, contains('helpAnchorHeight: compactPhone ? 36 : 48'));
    expect(scalesPage, contains('hideLabel: compactPhone'));
    expect(scalesPage, contains('minimumSize: Size.square'));
    expect(scalesPage, contains("? _ui('Oct.:', 'Oct.:')"));
    expect(scalesPage, contains('width: compactPhone ? 24 : 32'));
    expect(
      scalesPage,
      contains('_buildScaleResultBlock(compact: compactPhone)'),
    );
    expect(scalesPage, contains("'scales_settings'"));
    expect(scalesPage, contains('onPressed: _showScaleSettings'));
    expect(scalesPage, contains('if (!compactPhone)'));
    expect(pages, contains('void _showScaleSettings()'));
    expect(pages, contains("Text('BPM: \$_scaleBpm')"));
    expect(pages, contains('_buildScaleFingeringRow('));
    expect(pages, contains('MainAxisAlignment.spaceBetween'));
    expect(scalesPage, isNot(contains("if (_instrumentView != 'guitar')")));

    final main = File('lib/main.dart').readAsStringSync();
    expect(main, contains('_tabIndex == 3 ||'));
    expect(
      main,
      contains('_tabIndex == 1 || _tabIndex == 2 || _tabIndex == 7'),
    );
    expect(main, contains('scaleGuitarMode: false'));
    expect(main, contains('compactPhone ? (portrait ? 204.0 : 132.0) : 188.0'));
  });
}
