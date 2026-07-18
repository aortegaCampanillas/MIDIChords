// Datos musicales declarativos de la implementación móvil.
// Mantener en paridad con midichords/core/music_theory.py y el Worker web.

const List<Map<String, dynamic>> chordPatternDefs = <Map<String, dynamic>>[
  <String, dynamic>{
    'suffix': '',
    'intervals': <int>[0, 4, 7],
  },
  <String, dynamic>{
    'suffix': '5',
    'intervals': <int>[0, 7],
  },
  <String, dynamic>{
    'suffix': '-5',
    'intervals': <int>[0, 4, 6],
  },
  <String, dynamic>{
    'suffix': 'm',
    'intervals': <int>[0, 3, 7],
  },
  <String, dynamic>{
    'suffix': 'dim',
    'intervals': <int>[0, 3, 6],
  },
  <String, dynamic>{
    'suffix': 'aug',
    'intervals': <int>[0, 4, 8],
  },
  <String, dynamic>{
    'suffix': 'sus2',
    'intervals': <int>[0, 2, 7],
  },
  <String, dynamic>{
    'suffix': 'sus4',
    'intervals': <int>[0, 5, 7],
  },
  <String, dynamic>{
    'suffix': 'sus2sus4',
    'intervals': <int>[0, 2, 5, 7],
  },
  <String, dynamic>{
    'suffix': 'add2',
    'intervals': <int>[0, 2, 4, 7],
  },
  <String, dynamic>{
    'suffix': 'add4',
    'intervals': <int>[0, 4, 5, 7],
  },
  <String, dynamic>{
    'suffix': 'add9',
    'intervals': <int>[0, 4, 7, 14],
  },
  <String, dynamic>{
    'suffix': 'madd9',
    'intervals': <int>[0, 3, 7, 14],
  },
  <String, dynamic>{
    'suffix': '6',
    'intervals': <int>[0, 4, 7, 9],
  },
  <String, dynamic>{
    'suffix': '6add9',
    'intervals': <int>[0, 4, 7, 9, 14],
  },
  <String, dynamic>{
    'suffix': 'm6',
    'intervals': <int>[0, 3, 7, 9],
  },
  <String, dynamic>{
    'suffix': 'm6add9',
    'intervals': <int>[0, 3, 7, 9, 14],
  },
  <String, dynamic>{
    'suffix': '7',
    'intervals': <int>[0, 4, 7, 10],
  },
  <String, dynamic>{
    'suffix': '7sus4',
    'intervals': <int>[0, 5, 7, 10],
  },
  <String, dynamic>{
    'suffix': '7#5',
    'intervals': <int>[0, 4, 8, 10],
  },
  <String, dynamic>{
    'suffix': '7b5',
    'intervals': <int>[0, 4, 6, 10],
  },
  <String, dynamic>{
    'suffix': '7#9',
    'intervals': <int>[0, 4, 7, 10, 15],
  },
  <String, dynamic>{
    'suffix': '7b9',
    'intervals': <int>[0, 4, 7, 10, 13],
  },
  <String, dynamic>{
    'suffix': '7(#5,#9)',
    'intervals': <int>[0, 4, 8, 10, 15],
  },
  <String, dynamic>{
    'suffix': '7(#5,b9)',
    'intervals': <int>[0, 4, 8, 10, 13],
  },
  <String, dynamic>{
    'suffix': '7(b5,#9)',
    'intervals': <int>[0, 4, 6, 10, 15],
  },
  <String, dynamic>{
    'suffix': '7(b5,b9)',
    'intervals': <int>[0, 4, 6, 10, 13],
  },
  <String, dynamic>{
    'suffix': '9',
    'intervals': <int>[0, 4, 7, 10, 14],
  },
  <String, dynamic>{
    'suffix': '9#5',
    'intervals': <int>[0, 4, 8, 10, 14],
  },
  <String, dynamic>{
    'suffix': '9b5',
    'intervals': <int>[0, 4, 6, 10, 14],
  },
  <String, dynamic>{
    'suffix': '11',
    'intervals': <int>[0, 4, 7, 10, 14, 17],
  },
  <String, dynamic>{
    'suffix': '11b9',
    'intervals': <int>[0, 4, 7, 10, 13, 17],
  },
  <String, dynamic>{
    'suffix': '13',
    'intervals': <int>[0, 4, 7, 10, 14, 21],
  },
  <String, dynamic>{
    'suffix': '13b9',
    'intervals': <int>[0, 4, 7, 10, 13, 21],
  },
  <String, dynamic>{
    'suffix': '13#11',
    'intervals': <int>[0, 4, 7, 10, 14, 18, 21],
  },
  <String, dynamic>{
    'suffix': 'maj7',
    'intervals': <int>[0, 4, 7, 11],
  },
  <String, dynamic>{
    'suffix': 'maj7#5',
    'intervals': <int>[0, 4, 8, 11],
  },
  <String, dynamic>{
    'suffix': 'maj7b5',
    'intervals': <int>[0, 4, 6, 11],
  },
  <String, dynamic>{
    'suffix': 'maj9',
    'intervals': <int>[0, 4, 7, 11, 14],
  },
  <String, dynamic>{
    'suffix': 'maj11',
    'intervals': <int>[0, 4, 7, 11, 14, 17],
  },
  <String, dynamic>{
    'suffix': 'maj13',
    'intervals': <int>[0, 4, 7, 11, 14, 21],
  },
  <String, dynamic>{
    'suffix': 'maj9#11',
    'intervals': <int>[0, 4, 7, 11, 14, 18],
  },
  <String, dynamic>{
    'suffix': 'maj13#11',
    'intervals': <int>[0, 4, 7, 11, 14, 18, 21],
  },
  <String, dynamic>{
    'suffix': 'm7',
    'intervals': <int>[0, 3, 7, 10],
  },
  <String, dynamic>{
    'suffix': 'm7#5',
    'intervals': <int>[0, 3, 8, 10],
  },
  <String, dynamic>{
    'suffix': 'm9',
    'intervals': <int>[0, 3, 7, 10, 14],
  },
  <String, dynamic>{
    'suffix': 'm11',
    'intervals': <int>[0, 3, 7, 10, 14, 17],
  },
  <String, dynamic>{
    'suffix': 'm13',
    'intervals': <int>[0, 3, 7, 10, 14, 21],
  },
  <String, dynamic>{
    'suffix': 'mMaj7',
    'intervals': <int>[0, 3, 7, 11],
  },
  <String, dynamic>{
    'suffix': 'mMaj9',
    'intervals': <int>[0, 3, 7, 11, 14],
  },
  <String, dynamic>{
    'suffix': 'dim7',
    'intervals': <int>[0, 3, 6, 9],
  },
  <String, dynamic>{
    'suffix': 'm7b5',
    'intervals': <int>[0, 3, 6, 10],
  },
];

const Set<String> scaleBasicNames = <String>{
  'Ionian',
  'Aeolian',
  'Harmonic Minor',
  'Melodic Minor',
  'Dorian',
  'Phrygian',
  'Lydian',
  'Mixolydian',
  'Locrian',
  'Major Pentatonic',
  'Minor Pentatonic',
  'Blues Pentatonic',
  'Minor Blues',
  'Chromatic',
  'Whole Tone (WT)',
};

const List<Map<String, dynamic>> scalePatternDefs = <Map<String, dynamic>>[
  <String, dynamic>{
    'name': 'Ionian',
    'intervals': <int>[0, 2, 4, 5, 7, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Dorian',
    'intervals': <int>[0, 2, 3, 5, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Phrygian',
    'intervals': <int>[0, 1, 3, 5, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Lydian',
    'intervals': <int>[0, 2, 4, 6, 7, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Mixolydian',
    'intervals': <int>[0, 2, 4, 5, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Aeolian',
    'intervals': <int>[0, 2, 3, 5, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Locrian',
    'intervals': <int>[0, 1, 3, 5, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Chromatic',
    'intervals': <int>[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
  },
  <String, dynamic>{
    'name': 'Locrian #2',
    'intervals': <int>[0, 2, 3, 5, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Harmonic Minor',
    'intervals': <int>[0, 2, 3, 5, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Melodic Minor',
    'intervals': <int>[0, 2, 3, 5, 7, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Major Pentatonic',
    'intervals': <int>[0, 2, 4, 7, 9, 12],
  },
  <String, dynamic>{
    'name': 'Minor Pentatonic',
    'intervals': <int>[0, 3, 5, 7, 10, 12],
  },
  <String, dynamic>{
    'name': 'Blues Pentatonic',
    'intervals': <int>[0, 3, 5, 7, 10, 12],
  },
  <String, dynamic>{
    'name': 'Neutral Pentatonic',
    'intervals': <int>[0, 2, 5, 7, 10, 12],
  },
  <String, dynamic>{
    'name': 'Bebop',
    'intervals': <int>[0, 2, 4, 5, 7, 9, 10, 11, 12],
  },
  <String, dynamic>{
    'name': 'Bebop Major',
    'intervals': <int>[0, 2, 4, 5, 7, 8, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Bebop Minor',
    'intervals': <int>[0, 2, 3, 4, 5, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Half Diminished',
    'intervals': <int>[0, 2, 3, 5, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Diminished',
    'intervals': <int>[0, 2, 3, 5, 6, 8, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Whole Tone (WT)',
    'intervals': <int>[0, 2, 4, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Diminished WT',
    'intervals': <int>[0, 1, 3, 4, 6, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Minor Blues',
    'intervals': <int>[0, 3, 5, 6, 7, 10, 12],
  },
  <String, dynamic>{
    'name': 'Super Locrian',
    'intervals': <int>[0, 1, 3, 4, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Romanian Minor',
    'intervals': <int>[0, 2, 3, 6, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Spanish Gypsy',
    'intervals': <int>[0, 1, 4, 5, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Eight Tone Spanish',
    'intervals': <int>[0, 1, 3, 4, 5, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Enigmatic',
    'intervals': <int>[0, 1, 4, 6, 8, 10, 11, 12],
  },
  <String, dynamic>{
    'name': 'Neapolitan Major',
    'intervals': <int>[0, 1, 3, 5, 7, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Neapolitan Minor',
    'intervals': <int>[0, 1, 3, 5, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Pelog',
    'intervals': <int>[0, 1, 3, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Prometheus',
    'intervals': <int>[0, 2, 4, 6, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Prometheus Neapolitan',
    'intervals': <int>[0, 1, 4, 6, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Six Tone Symmetric',
    'intervals': <int>[0, 1, 4, 5, 8, 9, 12],
  },
  <String, dynamic>{
    'name': 'Lydian Minor',
    'intervals': <int>[0, 2, 3, 6, 7, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Lydian Augmented',
    'intervals': <int>[0, 2, 4, 6, 8, 9, 11, 12],
  },
  <String, dynamic>{
    'name': 'Lydian Diminished',
    'intervals': <int>[0, 2, 3, 6, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Lydian Augmented #6',
    'intervals': <int>[0, 2, 4, 6, 8, 10, 11, 12],
  },
  <String, dynamic>{
    'name': 'Hungarian Major',
    'intervals': <int>[0, 3, 4, 6, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Hungarian Minor',
    'intervals': <int>[0, 2, 3, 6, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Ichikosucho',
    'intervals': <int>[0, 2, 4, 5, 6, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Persian',
    'intervals': <int>[0, 1, 4, 5, 6, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Flamenco',
    'intervals': <int>[0, 1, 4, 5, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Hawaiian',
    'intervals': <int>[0, 2, 3, 5, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Maqam',
    'intervals': <int>[0, 1, 4, 5, 7, 8, 10, 12],
  },
  <String, dynamic>{
    'name': 'Oriental',
    'intervals': <int>[0, 1, 4, 5, 6, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Iwato',
    'intervals': <int>[0, 1, 5, 6, 10, 12],
  },
  <String, dynamic>{
    'name': 'Raga Malakosh',
    'intervals': <int>[0, 3, 5, 7, 10, 12],
  },
  <String, dynamic>{
    'name': 'Balinese',
    'intervals': <int>[0, 1, 3, 7, 8, 12],
  },
  <String, dynamic>{
    'name': 'Kafi Raga',
    'intervals': <int>[0, 2, 3, 5, 7, 9, 10, 12],
  },
  <String, dynamic>{
    'name': 'Todi Raga',
    'intervals': <int>[0, 1, 3, 6, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'Purvi Raga',
    'intervals': <int>[0, 1, 4, 6, 7, 8, 11, 12],
  },
  <String, dynamic>{
    'name': 'In Sen',
    'intervals': <int>[0, 1, 5, 7, 10, 12],
  },
];

const List<String> commonChordSuffixOrder = <String>[
  '',
  'm',
  '7',
  'maj7',
  'm7',
  'add2',
  'add4',
  'sus2',
  'sus4',
  'dim',
  'aug',
  '5',
  '6',
  'm6',
  'add9',
  'madd9',
  '9',
  'maj9',
  'm9',
  '11',
  'm11',
  '13',
  'm13',
  'dim7',
  'm7b5',
];

const Map<String, String> chordSuffixNamesEs = <String, String>{
  '': 'Mayor',
  'm': 'Menor',
  '5': 'Quinta (power chord)',
  '-5': 'Mayor quinta disminuida',
  'dim': 'Disminuido',
  'aug': 'Aumentado',
  'sus2': 'Suspendido 2ª',
  'sus4': 'Suspendido 4ª',
  'sus2sus4': 'Suspendido 2ª y 4ª',
  'add2': 'Mayor con 2ª añadida',
  'add4': 'Mayor con 4ª añadida',
  'add9': 'Mayor con 9ª añadida',
  'madd9': 'Menor con 9ª añadida',
  '6': 'Mayor con 6ª',
  '6add9': 'Mayor con 6ª y 9ª',
  'm6': 'Menor con 6ª',
  'm6add9': 'Menor con 6ª y 9ª',
  '7': 'Mayor dominante (7ª menor)',
  '7sus4': 'Dominante suspendido 4ª',
  '7#5': 'Dominante aumentado',
  '7b5': 'Dominante quinta disminuida',
  '7#9': 'Dominante con 9ª aumentada',
  '7b9': 'Dominante con 9ª disminuida',
  '7(#5,#9)': 'Dominante aumentado con 9ª aumentada',
  '7(#5,b9)': 'Dominante aumentado con 9ª disminuida',
  '7(b5,#9)': 'Dominante quinta disminuida con 9ª aumentada',
  '7(b5,b9)': 'Dominante quinta disminuida con 9ª disminuida',
  '9': 'Dominante con 9ª',
  '9#5': 'Dominante aumentado con 9ª',
  '9b5': 'Dominante quinta disminuida con 9ª',
  '11': 'Dominante con 11ª',
  '11b9': 'Dominante con 11ª y 9ª disminuida',
  '13': 'Dominante con 13ª',
  '13b9': 'Dominante con 13ª y 9ª disminuida',
  '13#11': 'Dominante con 13ª y 11ª aumentada',
  'maj7': 'Mayor con 7ª mayor',
  'maj7#5': 'Mayor aumentado con 7ª mayor',
  'maj7b5': 'Mayor quinta disminuida con 7ª mayor',
  'maj9': 'Mayor con 9ª y 7ª mayor',
  'maj11': 'Mayor con 11ª y 7ª mayor',
  'maj13': 'Mayor con 13ª y 7ª mayor',
  'maj9#11': 'Mayor con 9ª, 11ª aumentada y 7ª mayor',
  'maj13#11': 'Mayor con 13ª, 11ª aumentada y 7ª mayor',
  'm7': 'Menor con 7ª menor',
  'm7#5': 'Menor aumentado con 7ª menor',
  'm9': 'Menor con 9ª y 7ª menor',
  'm11': 'Menor con 11ª y 7ª menor',
  'm13': 'Menor con 13ª y 7ª menor',
  'mMaj7': 'Menor con 7ª mayor',
  'mMaj9': 'Menor con 9ª y 7ª mayor',
  'dim7': 'Disminuido con 7ª disminuida',
  'm7b5': 'Semidisminuido (menor con quinta disminuida)',
};

const Map<String, String> chordSuffixNamesEn = <String, String>{
  '': 'Major',
  'm': 'Minor',
  '5': 'Power chord',
  '-5': 'Major flat five',
  'dim': 'Diminished',
  'aug': 'Augmented',
  'sus2': 'Suspended 2nd',
  'sus4': 'Suspended 4th',
  'sus2sus4': 'Suspended 2nd and 4th',
  'add2': 'Major add 2nd',
  'add4': 'Major add 4th',
  'add9': 'Major add 9th',
  'madd9': 'Minor add 9th',
  '6': 'Major 6th',
  '6add9': 'Major 6th add 9th',
  'm6': 'Minor 6th',
  'm6add9': 'Minor 6th add 9th',
  '7': 'Dominant 7th (major with minor 7th)',
  '7sus4': 'Dominant suspended 4th',
  '7#5': 'Augmented dominant',
  '7b5': 'Dominant flat five',
  '7#9': 'Dominant sharp 9th',
  '7b9': 'Dominant flat 9th',
  '7(#5,#9)': 'Augmented dominant sharp 9th',
  '7(#5,b9)': 'Augmented dominant flat 9th',
  '7(b5,#9)': 'Dominant flat five sharp 9th',
  '7(b5,b9)': 'Dominant flat five flat 9th',
  '9': 'Dominant 9th',
  '9#5': 'Augmented dominant 9th',
  '9b5': 'Dominant flat five 9th',
  '11': 'Dominant 11th',
  '11b9': 'Dominant 11th flat 9th',
  '13': 'Dominant 13th',
  '13b9': 'Dominant 13th flat 9th',
  '13#11': 'Dominant 13th sharp 11th',
  'maj7': 'Major 7th',
  'maj7#5': 'Augmented major 7th',
  'maj7b5': 'Major flat five major 7th',
  'maj9': 'Major 9th',
  'maj11': 'Major 11th',
  'maj13': 'Major 13th',
  'maj9#11': 'Major 9th sharp 11th',
  'maj13#11': 'Major 13th sharp 11th',
  'm7': 'Minor 7th',
  'm7#5': 'Augmented minor 7th',
  'm9': 'Minor 9th',
  'm11': 'Minor 11th',
  'm13': 'Minor 13th',
  'mMaj7': 'Minor major 7th',
  'mMaj9': 'Minor major 9th',
  'dim7': 'Diminished 7th',
  'm7b5': 'Half-diminished (minor flat five)',
};

const List<String> inversionNamesEs = <String>[
  '',
  'primera inversión',
  'segunda inversión',
  'tercera inversión',
];

const List<String> inversionNamesEn = <String>[
  '',
  'first inversion',
  'second inversion',
  'third inversion',
];

const Map<String, String> scaleNameEs = <String, String>{
  'Ionian': 'Jónica',
  'Dorian': 'Dórica',
  'Phrygian': 'Frigia',
  'Lydian': 'Lidia',
  'Mixolydian': 'Mixolidia',
  'Aeolian': 'Eólica',
  'Locrian': 'Locria',
  'Chromatic': 'Cromática',
  'Locrian #2': 'Locria #2',
  'Harmonic Minor': 'Menor armónica',
  'Melodic Minor': 'Menor melódica',
  'Major Pentatonic': 'Pentatónica mayor',
  'Minor Pentatonic': 'Pentatónica menor',
  'Blues Pentatonic': 'Pentatónica blues',
  'Neutral Pentatonic': 'Pentatónica neutral',
  'Bebop': 'Bebop',
  'Bebop Major': 'Bebop mayor',
  'Bebop Minor': 'Bebop menor',
  'Half Diminished': 'Semidisminuida',
  'Diminished': 'Disminuida',
  'Whole Tone (WT)': 'Tonos enteros (WT)',
  'Diminished WT': 'Disminuida WT',
  'Minor Blues': 'Blues menor',
  'Super Locrian': 'Superlocria',
  'Romanian Minor': 'Menor rumana',
  'Spanish Gypsy': 'Gitana española',
  'Eight Tone Spanish': 'Española de ocho tonos',
  'Enigmatic': 'Enigmática',
  'Neapolitan Major': 'Napolitana mayor',
  'Neapolitan Minor': 'Napolitana menor',
  'Prometheus': 'Prometeo',
  'Prometheus Neapolitan': 'Prometeo napolitana',
  'Six Tone Symmetric': 'Simétrica de seis tonos',
  'Lydian Minor': 'Lidia menor',
  'Lydian Augmented': 'Lidia aumentada',
  'Lydian Diminished': 'Lidia disminuida',
  'Lydian Augmented #6': 'Lidia aumentada #6',
  'Hungarian Major': 'Húngara mayor',
  'Hungarian Minor': 'Menor húngara',
  'Ichikosucho': 'Ichikosucho',
  'Pelog': 'Pelog',
  'Persian': 'Persa',
  'Flamenco': 'Flamenca',
  'Hawaiian': 'Hawaiana',
  'Maqam': 'Maqam',
  'Oriental': 'Oriental',
  'Iwato': 'Iwato',
  'Raga Malakosh': 'Raga Malakosh',
  'Balinese': 'Balinesa',
  'Kafi Raga': 'Raga Kafi',
  'Todi Raga': 'Raga Todi',
  'Purvi Raga': 'Raga Purvi',
  'In Sen': 'In Sen',
};
