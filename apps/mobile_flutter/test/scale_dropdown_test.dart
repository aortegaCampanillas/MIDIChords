import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/scale_dropdown.dart';

void main() {
  test('scale dropdown renders disabled family headers', () {
    final items = buildScaleDropdownItems(
      language: 'es',
      patterns: <Map<String, dynamic>>[
        <String, dynamic>{'name': 'Chromatic', 'localized_name': 'Cromática'},
        <String, dynamic>{'name': 'Dorian', 'localized_name': 'Dórica'},
        <String, dynamic>{
          'name': 'Harmonic Minor',
          'localized_name': 'Menor armónica',
        },
      ],
    );
    final headers = items.where((item) => !item.enabled).toList();

    expect(headers, hasLength(3));
    expect((headers[0].child as Text).data, 'Modos griegos');
    expect((headers[1].child as Text).data, 'Escalas menores');
    expect((headers[2].child as Text).data, 'Simétricas y sintéticas');
    expect(
      items.where((item) => item.enabled).map((item) => item.value),
      <String>['Dorian', 'Harmonic Minor', 'Chromatic'],
    );
  });
}
