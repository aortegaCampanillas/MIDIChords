/// Piano scale fingerings (right and left hand) from TomPlay database.
/// Organized by scale type, with overrides by key to match awkward fingerings.
library;

import 'dart:math' as math;

const Map<String, Map<String, List<int>>> baseFingerings = {
  'major': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'natural_minor': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'harmonic_minor': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'melodic_minor': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'ionian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'dorian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'phrygian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'lydian_mode': {
    'right': [1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'mixolydian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'aeolian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [5, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1],
  },
  'locrian_mode': {
    'right': [1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 5],
    'left': [4, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1],
  },
  // Fuente: tomplay.com/es/tools/scales/piano (verificado en Do).
  'whole_tone': {
    'right': [1, 2, 1, 2, 3, 4, 1, 2, 1, 2, 3, 4, 5],
    'left': [3, 2, 1, 4, 3, 2, 3, 2, 1, 4, 3, 2, 1],
  },
  'minor_blues': {
    'right': [1, 2, 3, 4, 1, 3, 1, 2, 3, 4, 1, 3, 4],
    'left': [5, 4, 3, 2, 1, 2, 1, 4, 2, 3, 1, 2, 1],
  },
};

// Key = "scaleType_key_hand" for easy lookup
const Map<String, List<int>> fingeringOverrides = {
  'major_cs_right': [2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2],
  'major_cs_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_db_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'major_db_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_eb_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'major_eb_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_f_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'major_f_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_fs_right': [2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2],
  'major_fs_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'major_gb_right': [2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2],
  'major_gb_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'major_ab_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'major_ab_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_bb_right': [4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4],
  'major_bb_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'major_b_left': [4, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'natural_minor_cs_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'natural_minor_cs_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'natural_minor_db_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'natural_minor_db_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'natural_minor_eb_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'natural_minor_eb_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'natural_minor_f_right': [1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 4],
  'natural_minor_fs_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'natural_minor_fs_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'natural_minor_gb_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'natural_minor_gb_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'natural_minor_ab_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'natural_minor_ab_left': [3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3],
  'natural_minor_bb_right': [4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4],
  'natural_minor_bb_left': [2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2],
  'natural_minor_b_left': [4, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1],
  'harmonic_minor_cs_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'harmonic_minor_cs_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'harmonic_minor_db_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'harmonic_minor_db_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'harmonic_minor_eb_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'harmonic_minor_eb_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'harmonic_minor_f_right': [1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 4],
  'harmonic_minor_fs_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'harmonic_minor_fs_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'harmonic_minor_gb_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'harmonic_minor_gb_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'harmonic_minor_ab_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'harmonic_minor_ab_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'harmonic_minor_bb_right': [4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4],
  'harmonic_minor_bb_left': [2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2],
  'harmonic_minor_b_left': [4, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1],
  'melodic_minor_cs_right': [2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2],
  'melodic_minor_cs_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'melodic_minor_db_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'melodic_minor_db_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'melodic_minor_eb_right': [3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
  'melodic_minor_eb_left': [2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2],
  'melodic_minor_f_right': [1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 4],
  'melodic_minor_fs_right': [2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2],
  'melodic_minor_fs_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'melodic_minor_gb_right': [2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2],
  'melodic_minor_gb_left': [4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4],
  'melodic_minor_ab_right': [3, 4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
  'melodic_minor_ab_left': [3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1, 3],
  'melodic_minor_bb_right': [4, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 4],
  'melodic_minor_bb_left': [2, 1, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2],
  'melodic_minor_b_left': [4, 3, 2, 1, 4, 3, 2, 1, 3, 2, 1, 4, 3, 2, 1],
};

/// Get fingering for a scale. Returns right or left hand fingering pattern.
List<int> getFingeringForScale(
  String scaleType,
  int pcTonic,
  String hand, {
  int? count,
}) {
  scaleType = scaleType.toLowerCase();
  hand = hand.toLowerCase();
  String keyStr = _pcToKeyStr(pcTonic);
  String overrideKey = '${scaleType}_${keyStr}_$hand';

  List<int>? fingering;

  // Check overrides first (flat lookup)
  if (fingeringOverrides.containsKey(overrideKey)) {
    fingering = fingeringOverrides[overrideKey];
  }
  // Fall back to base fingerings
  else if (baseFingerings.containsKey(scaleType) &&
           baseFingerings[scaleType]!.containsKey(hand)) {
    fingering = baseFingerings[scaleType]![hand];
  }

  // Sin digitación documentada (ni en TomPlay ni verificada a mano) para
  // esta escala — usamos un ciclo genérico como aproximación razonable en
  // vez de dejarlo vacío. Añadir la escala a `baseFingerings` con datos
  // reales de Tomplay siempre tiene prioridad sobre este respaldo.
  final List<int> resolvedFingering =
      fingering ?? _genericScaleFingering(hand, count ?? 8);

  if (count == null) return List<int>.from(resolvedFingering);

  if (count <= 0) return [];
  if (count >= resolvedFingering.length) {
    final result = List<int>.from(resolvedFingering);
    if (count > resolvedFingering.length) {
      final patternBase = resolvedFingering.sublist(
        0,
        math.min(7, resolvedFingering.length),
      );
      for (int i = resolvedFingering.length; i < count; i++) {
        result.add(patternBase[i % patternBase.length]);
      }
    }
    return result;
  }

  return resolvedFingering.sublist(0, count);
}

/// Digitación algorítmica de respaldo para escalas sin patrón documentado.
/// Ciclo de mano derecha: 1-2-3-1-2-3-4 (7 notas); mano izquierda es el
/// espejo: 5-4-3-2-1-3-2-1.
List<int> _genericScaleFingering(String hand, int count) {
  final n = count <= 0 ? 8 : count;
  if (hand == 'left') {
    const cycle = <int>[5, 4, 3, 2, 1, 3, 2, 1];
    return List<int>.generate(n, (i) => cycle[i % cycle.length]);
  }
  const cycle = <int>[1, 2, 3, 1, 2, 3, 4];
  return List<int>.generate(n, (i) => cycle[i % cycle.length]);
}

String _pcToKeyStr(int pc) {
  const mapping = {
    0: 'c',
    1: 'cs',
    2: 'd',
    3: 'ds',
    4: 'e',
    5: 'f',
    6: 'fs',
    7: 'g',
    8: 'gs',
    9: 'a',
    10: 'as',
    11: 'b',
  };
  return mapping[(pc % 12)] ?? 'c';
}
