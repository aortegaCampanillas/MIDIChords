import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'interval generation uses a semitone table and a wider controls panel',
    () {
      final pages = File('lib/main_pages.dart').readAsStringSync();
      final main = File('lib/main.dart').readAsStringSync();
      final intervalPage = pages
          .split('Widget _buildIntervalGenerationPage()')
          .last
          .split('Widget _intervalGenerationPlayButton(')
          .first;

      expect(pages, contains('Widget _buildIntervalGenerationTable('));
      expect(pages, contains('for (var semitones = 0; semitones <= 12;'));
      expect(pages, contains('for (final category in intervalGridCategories)'));
      expect(intervalPage, isNot(contains('ChoiceChip(')));
      expect(main, contains('flex: _tabIndex == 7 ? 42 : 57'));
      expect(main, contains('flex: _tabIndex == 7 ? 58 : 43'));
    },
  );
}
