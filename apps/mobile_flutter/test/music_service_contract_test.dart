import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/music_service.dart';

Map<String, dynamic> evaluateContractCase(
  String operation,
  Map<String, dynamic> input,
) {
  if (operation == 'generate_chord') {
    return generateChordLocal(
      rootPc: input['root_pc'] as int,
      suffix: input['suffix'] as String,
      inversion: input['inversion'] as int,
      language: input['language'] as String,
      preferFlat: input['prefer_flat'] as bool,
    );
  }
  if (operation == 'generate_scale') {
    return generateScaleLocal(
      tonicPc: input['tonic_pc'] as int,
      patternName: input['pattern_name'] as String,
      language: input['language'] as String,
      preferFlat: input['prefer_flat'] as bool,
    );
  }
  if (operation == 'detect_chord') {
    return detectChordLocal(
      notes: (input['notes'] as List<dynamic>).cast<int>(),
      language: input['language'] as String,
      preferFlat: input['prefer_flat'] as bool,
    );
  }
  throw StateError('Unknown contract operation: $operation');
}

void main() {
  final contractFile = File('../../tests/fixtures/music_service_contract.json');
  final contract =
      jsonDecode(contractFile.readAsStringSync()) as Map<String, dynamic>;
  final cases = (contract['cases'] as List<dynamic>)
      .cast<Map<String, dynamic>>();

  for (final contractCase in cases) {
    test('mobile music contract: ${contractCase['id']}', () {
      final expected = contractCase['expected'] as Map<String, dynamic>;
      final result = evaluateContractCase(
        contractCase['operation'] as String,
        contractCase['input'] as Map<String, dynamic>,
      );
      final actual = <String, dynamic>{
        for (final field in expected.keys) field: result[field],
      };
      expect(actual, expected);
    });
  }
}
