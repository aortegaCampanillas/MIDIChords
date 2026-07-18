import 'package:flutter/material.dart';

import 'music_catalog.dart';

List<DropdownMenuItem<String>> buildScaleDropdownItems({
  required List<Map<String, dynamic>> patterns,
  required String language,
}) {
  final byName = <String, Map<String, dynamic>>{
    for (final pattern in patterns) pattern['name'] as String? ?? '': pattern,
  };
  const labels = <String, Map<String, String>>{
    'greek_modes': <String, String>{'es': 'Modos griegos', 'en': 'Greek modes'},
    'minor': <String, String>{'es': 'Escalas menores', 'en': 'Minor scales'},
    'altered_modes': <String, String>{
      'es': 'Modos alterados',
      'en': 'Altered modes',
    },
    'pentatonic_blues': <String, String>{
      'es': 'Pentatónicas y blues',
      'en': 'Pentatonic & blues',
    },
    'bebop': <String, String>{'es': 'Bebop', 'en': 'Bebop'},
    'symmetric_synthetic': <String, String>{
      'es': 'Simétricas y sintéticas',
      'en': 'Symmetric & synthetic',
    },
    'world': <String, String>{
      'es': 'Tradicionales del mundo',
      'en': 'World traditions',
    },
  };
  final lang = language == 'en' ? 'en' : 'es';
  final groups = scaleFamilyGroups.map((group) {
    final key = group['key']! as String;
    final names = group['names']! as List<String>;
    final groupPatterns = names
        .map((name) => byName[name])
        .whereType<Map<String, dynamic>>()
        .toList(growable: false);
    return (labels[key]![lang]!, groupPatterns);
  });
  final items = <DropdownMenuItem<String>>[];
  var groupIndex = 0;
  for (final (label, groupPatterns) in groups) {
    if (groupPatterns.isEmpty) continue;
    items.add(
      DropdownMenuItem<String>(
        value: '__scale_group__${groupIndex++}',
        enabled: false,
        child: Text(
          label,
          style: const TextStyle(
            color: Color(0xFFF2BF2F),
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
    for (final pattern in groupPatterns) {
      final name = pattern['name'] as String? ?? 'Ionian';
      final localized = pattern['localized_name'] as String? ?? name;
      items.add(
        DropdownMenuItem<String>(
          value: name,
          child: Padding(
            padding: const EdgeInsets.only(left: 12),
            child: Text(
              scaleDisplayName(name, localized),
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
          ),
        ),
      );
    }
  }
  return items;
}
