import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('changelog list flexes inside short landscape dialogs', () {
    final source = File('lib/main.dart').readAsStringSync();
    final dialog = source.substring(
      source.indexOf('Future<void> _showChangelogDialog'),
      source.indexOf('Future<void> _loadChordTheoryCatalog'),
    );

    expect(dialog, contains('Flexible('));
    expect(dialog, contains('BoxConstraints(maxHeight: 380)'));
    expect(
      dialog,
      isNot(contains('MediaQuery.of(context).size.height - 260.0')),
    );
  });
}
