import 'package:flutter/material.dart';

const Map<String, Map<String, String>> _groupLabels =
    <String, Map<String, String>>{
      'es': <String, String>{
        'chord_group_triads': 'Tríadas',
        'chord_group_sevenths': 'Séptimas',
        'chord_group_sixths': 'Sextas',
        'chord_group_add': 'Add (notas añadidas)',
        'chord_group_altered_dominants': 'Dominantes alterados',
        'chord_group_extensions': 'Extensiones',
        'chord_group_altered_extensions': 'Extensiones alteradas',
        'chord_group_other': 'Otras variantes',
      },
      'en': <String, String>{
        'chord_group_triads': 'Triads',
        'chord_group_sevenths': 'Sevenths',
        'chord_group_sixths': 'Sixths',
        'chord_group_add': 'Add chords',
        'chord_group_altered_dominants': 'Altered dominants',
        'chord_group_extensions': 'Extensions',
        'chord_group_altered_extensions': 'Altered extensions',
        'chord_group_other': 'Other variants',
      },
    };

List<DropdownMenuItem<String>> buildChordVariantDropdownItems({
  required Map<String, dynamic> catalog,
  required List<Map<String, dynamic>> patterns,
  required String language,
}) {
  final lang = language == 'en' ? 'en' : 'es';
  final bySuffix = <String, Map<String, dynamic>>{
    for (final pattern in patterns)
      (pattern['suffix'] as String? ?? ''): pattern,
  };
  final rendered = <String>{};
  final items = <DropdownMenuItem<String>>[];
  final groups = (catalog['groups'] as List<dynamic>? ?? const <dynamic>[])
      .whereType<Map>();
  var groupIndex = 0;
  for (final rawGroup in groups) {
    final group = rawGroup.map((key, value) => MapEntry(key.toString(), value));
    final suffixes = (group['suffixes'] as List<dynamic>? ?? const <dynamic>[])
        .map((value) => value.toString())
        .where(bySuffix.containsKey)
        .toList(growable: false);
    if (suffixes.isEmpty) continue;
    final labelKey = group['labelKey']?.toString() ?? '';
    items.add(
      DropdownMenuItem<String>(
        value: '__group__${groupIndex++}',
        enabled: false,
        child: Text(
          _groupLabels[lang]?[labelKey] ?? labelKey,
          style: const TextStyle(
            color: Color(0xFFF2BF2F),
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
    for (final suffix in suffixes) {
      rendered.add(suffix);
      items.add(
        DropdownMenuItem<String>(
          value: suffix,
          child: Padding(
            padding: const EdgeInsets.only(left: 12),
            child: Text(suffix.isEmpty ? 'maj' : suffix),
          ),
        ),
      );
    }
  }
  final remaining =
      bySuffix.keys.where((suffix) => !rendered.contains(suffix)).toList()
        ..sort();
  if (remaining.isNotEmpty) {
    items.add(
      DropdownMenuItem<String>(
        value: '__group__other',
        enabled: false,
        child: Text(
          _groupLabels[lang]?['chord_group_other'] ?? 'Other variants',
          style: const TextStyle(
            color: Color(0xFFF2BF2F),
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
    for (final suffix in remaining) {
      items.add(
        DropdownMenuItem<String>(
          value: suffix,
          child: Padding(
            padding: const EdgeInsets.only(left: 12),
            child: Text(suffix.isEmpty ? 'maj' : suffix),
          ),
        ),
      );
    }
  }
  return items;
}

String _naturalLanguageList(List<String> items, String language) {
  if (items.length <= 1) return items.isEmpty ? '' : items.first;
  final conjunction = language == 'en' ? ' and ' : ' y ';
  return '${items.sublist(0, items.length - 1).join(', ')}$conjunction${items.last}';
}

String _inversionHelp(
  Map<String, dynamic> catalog,
  String formula,
  int inversion,
  String language,
) {
  final lang = language == 'en' ? 'en' : 'es';
  final degrees = formula
      .split(' - ')
      .where((part) => part.isNotEmpty)
      .toList();
  if (degrees.isEmpty) return '';
  final safeInversion = inversion.clamp(0, degrees.length - 1);
  final inversionNames =
      ((catalog['inversion_names'] as Map?)?[lang] as List<dynamic>? ??
              const <dynamic>[])
          .map((value) => value.toString())
          .toList(growable: false);
  final inversionName = safeInversion < inversionNames.length
      ? inversionNames[safeInversion]
      : (lang == 'en'
            ? 'Inversion $safeInversion'
            : 'Inversión $safeInversion');
  if (safeInversion == 0) {
    return lang == 'en'
        ? "$inversionName: the root is in the bass and the remaining notes appear above it in formula order. This is the clearest reference position for recognizing the chord's structure."
        : '$inversionName: la fundamental está en el bajo y las demás notas aparecen por encima siguiendo el orden de la fórmula. Es la posición de referencia más clara para reconocer la estructura del acorde.';
  }
  final degreeNames =
      (((catalog['degree_names'] as Map?)?[lang] as Map?) ??
              const <dynamic, dynamic>{})
          .map((key, value) => MapEntry(key.toString(), value.toString()));
  final bassDegree =
      degreeNames[degrees[safeInversion]] ?? degrees[safeInversion];
  final movedDegrees = degrees
      .sublist(0, safeInversion)
      .map((degree) => degreeNames[degree] ?? degree)
      .toList(growable: false);
  final moved = _naturalLanguageList(movedDegrees, lang);
  if (lang == 'en') {
    final verb = movedDegrees.length == 1 ? 'moves' : 'move';
    return '$inversionName: $bassDegree is in the bass. $moved $verb up one octave; the chord keeps the same notes, but its bass support and voice leading into nearby chords change.';
  }
  final verb = movedDegrees.length == 1 ? 'se desplaza' : 'se desplazan';
  return '$inversionName: $bassDegree está en el bajo. $moved $verb una octava hacia arriba; el acorde conserva las mismas notas, pero cambia su apoyo grave y el enlace con los acordes cercanos.';
}

({String formula, String theory, String inversion}) chordVariantHelpContent({
  required Map<String, dynamic> catalog,
  required String suffix,
  required int inversion,
  required String language,
}) {
  final lang = language == 'en' ? 'en' : 'es';
  final theoryMap = (catalog['theory'] as Map?) ?? const <dynamic, dynamic>{};
  final rawEntry = theoryMap[suffix] as Map? ?? const <dynamic, dynamic>{};
  final entry = rawEntry.map((key, value) => MapEntry(key.toString(), value));
  final formula = entry['formula']?.toString() ?? '';
  final theory = entry[lang]?.toString() ?? '';
  String inversionText;
  final major =
      catalog['major_inversions'] as List<dynamic>? ?? const <dynamic>[];
  if (suffix.isEmpty && inversion >= 0 && inversion < major.length) {
    final values = major[inversion] as List<dynamic>;
    inversionText = values[lang == 'en' ? 1 : 0].toString();
  } else {
    inversionText = _inversionHelp(catalog, formula, inversion, lang);
  }
  return (formula: formula, theory: theory, inversion: inversionText);
}
