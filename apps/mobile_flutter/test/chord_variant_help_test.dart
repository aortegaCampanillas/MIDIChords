import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/chord_variant_help.dart';

void main() {
  final catalog =
      (jsonDecode(File('assets/chord_variant_theory.json').readAsStringSync())
          as Map<String, dynamic>);

  test('every chord variant and inversion has bilingual help', () {
    final theory = (catalog['theory'] as Map<String, dynamic>);
    expect(theory, hasLength(54));
    for (final entry in theory.entries) {
      final formula =
          (entry.value as Map<String, dynamic>)['formula'] as String;
      final inversions = formula.split(' - ').length;
      for (final language in <String>['es', 'en']) {
        for (var inversion = 0; inversion < inversions; inversion += 1) {
          final help = chordVariantHelpContent(
            catalog: catalog,
            suffix: entry.key,
            inversion: inversion,
            language: language,
          );
          expect(help.formula, isNotEmpty);
          expect(help.theory.length, greaterThan(40));
          expect(help.inversion.length, greaterThan(40));
        }
      }
    }
  });

  test('grouped dropdown keeps all variants selectable exactly once', () {
    final theory = (catalog['theory'] as Map<String, dynamic>);
    final patterns = theory.keys
        .map(
          (suffix) => <String, dynamic>{
            'suffix': suffix,
            'intervals': const <int>[],
          },
        )
        .toList();
    final items = buildChordVariantDropdownItems(
      catalog: catalog,
      patterns: patterns,
      language: 'es',
    );
    final selectable = items
        .where((item) => item.enabled)
        .map((item) => item.value)
        .toList();
    final headers = items.where((item) => !item.enabled).toList();

    expect(selectable, hasLength(54));
    expect(selectable.toSet(), hasLength(54));
    expect(headers, hasLength(7));
  });
}
