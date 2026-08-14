import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('interval practice compacts controls and hides the table on phones', () {
    final pages = File('lib/main_pages.dart').readAsStringSync();
    final practicePage = pages
        .split('Widget _buildIntervalPracticePage()')
        .last
        .split('void _showIntervalPracticeHelp()')
        .first;

    expect(
      practicePage,
      contains('final compactPhone = _isCompactPhone(context);'),
    );
    expect(practicePage, contains('minimumSize: const Size(0, 36)'));
    expect(practicePage, contains('minimumSize: const Size(36, 36)'));
    expect(practicePage, contains('compact: compactPhone'));
    expect(practicePage, contains('if (!compactPhone) ...<Widget>['));
    expect(practicePage, contains("'interval_practice_table'"));
    expect(
      pages,
      contains("compactPhone ? 'Responde pulsando la segunda nota"),
    );
    expect(
      pages,
      contains("compactPhone ? 'Answer by pressing the second note"),
    );
    expect(
      pages,
      contains('final whiteKeyHeight = compactPhone ? 96.0 : 112.0;'),
    );
    expect(
      pages,
      contains('final blackKeyHeight = compactPhone ? 58.0 : 68.0;'),
    );
  });
}
