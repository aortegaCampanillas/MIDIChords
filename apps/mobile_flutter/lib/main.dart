import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/foundation.dart' show setEquals;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_audio_capture/flutter_audio_capture.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_midi_command/flutter_midi_command.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:wakelock_plus/wakelock_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'circle_of_fifths.dart';
import 'fingerings.dart';
import 'interval_data.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations(const <DeviceOrientation>[
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  runApp(const MidiChordsMobileApp());
}

const List<Map<String, dynamic>> _kChordPatternDefs = <Map<String, dynamic>>[
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

const Set<String> _kScaleBasicNames = <String>{
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

const List<Map<String, dynamic>> _kScalePatternDefs = <Map<String, dynamic>>[
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

const List<String> _kCommonChordSuffixOrder = <String>[
  '',
  'm',
  '7',
  'maj7',
  'm7',
  'sus4',
  'sus2',
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

const Map<String, String> _kChordSuffixNamesEs = <String, String>{
  '': 'Mayor',
  'm': 'Menor',
  '5': 'Quinta (power chord)',
  '-5': 'Mayor quinta disminuida',
  'dim': 'Disminuido',
  'aug': 'Aumentado',
  'sus2': 'Suspendido 2ª',
  'sus4': 'Suspendido 4ª',
  'sus2sus4': 'Suspendido 2ª y 4ª',
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

const Map<String, String> _kChordSuffixNamesEn = <String, String>{
  '': 'Major',
  'm': 'Minor',
  '5': 'Power chord',
  '-5': 'Major flat five',
  'dim': 'Diminished',
  'aug': 'Augmented',
  'sus2': 'Suspended 2nd',
  'sus4': 'Suspended 4th',
  'sus2sus4': 'Suspended 2nd and 4th',
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

const List<String> _kInversionNamesEs = <String>[
  '',
  'primera inversión',
  'segunda inversión',
  'tercera inversión',
];

const List<String> _kInversionNamesEn = <String>[
  '',
  'first inversion',
  'second inversion',
  'third inversion',
];

const Map<String, String> _kScaleNameEs = <String, String>{
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

const Map<int, String> _kGrandPianoSamples = <int, String>{
  48: 'samples/grand_piano/C3.mp3',
  52: 'samples/grand_piano/E3.mp3',
  55: 'samples/grand_piano/G3.mp3',
  60: 'samples/grand_piano/C4.mp3',
  64: 'samples/grand_piano/E4.mp3',
  67: 'samples/grand_piano/G4.mp3',
  72: 'samples/grand_piano/C5.mp3',
};

const Map<int, String> _kGuitarNylonSamples = <int, String>{
  40: 'samples/guitar_nylon/E2.mp3',
  45: 'samples/guitar_nylon/A2.mp3',
  50: 'samples/guitar_nylon/D3.mp3',
  52: 'samples/guitar_nylon/E3.mp3',
  55: 'samples/guitar_nylon/G3.mp3',
  59: 'samples/guitar_nylon/B3.mp3',
  64: 'samples/guitar_nylon/E4.mp3',
};
const String _kMetronomeSample = 'metronome.mp3';
const MethodChannel _kPlatformChannel = MethodChannel('midichords/platform');
const bool _kEnableMobileTuner = false;
const double _kTabletMinShortestSide = 600.0;
/// Teclado móvil: proporción web (`style.css` 124px / 36px).
const double _kPianoMinWhiteKeyWidth = 28.0;
const double _kPianoMaxWhiteKeyWidth = 36.0;
const double _kPianoWhiteKeyHeight = 124.0;
const double _kPianoKeyAspect =
    _kPianoWhiteKeyHeight / _kPianoMaxWhiteKeyWidth;
/// Teclas visibles en viewport cuando hay scroll (recorte lateral).
const double _kPianoTargetVisibleWhiteKeys = 9.5;
/// Piano estándar 88 teclas: A0 (21) … C8 (108), como escritorio/web.
const int _kPianoLowMidi = 21;
const int _kPianoHighMidi = 108;
const int _kPianoMiddleCMidi = 60;

class _PianoKeyMetrics {
  const _PianoKeyMetrics({
    required this.whiteW,
    required this.whiteH,
    required this.scrollable,
  });

  final double whiteW;
  final double whiteH;
  final bool scrollable;
}

_PianoKeyMetrics _computePianoKeyMetrics({
  required double viewportW,
  required double viewportH,
  required int whiteKeyCount,
}) {
  final availH = math.max(88.0, viewportH - 6.0);
  final n = whiteKeyCount.toDouble();

  // 1) Caben todas las teclas: rellenar ancho del panel (poco habitual con 88 teclas).
  var whiteW = (viewportW / n).clamp(_kPianoMinWhiteKeyWidth, _kPianoMaxWhiteKeyWidth);
  var whiteH = whiteW * _kPianoKeyAspect;
  if (whiteH <= availH && whiteW * n <= viewportW) {
    return _PianoKeyMetrics(whiteW: whiteW, whiteH: whiteH, scrollable: false);
  }

  // 2) Altura del panel manda; scroll horizontal si hace falta.
  whiteH = availH;
  whiteW = math.max(_kPianoMinWhiteKeyWidth, whiteH / _kPianoKeyAspect);
  var keyboardW = whiteW * n;
  if (keyboardW <= viewportW) {
    whiteW = viewportW / n;
    whiteH = math.min(availH, whiteW * _kPianoKeyAspect);
    return _PianoKeyMetrics(whiteW: whiteW, whiteH: whiteH, scrollable: false);
  }

  // 3) Scroll: priorizar altura y dejar ~media tecla cortada al borde.
  final targetW = (viewportW / _kPianoTargetVisibleWhiteKeys).clamp(0.0, _kPianoMaxWhiteKeyWidth);
  if (targetW > whiteW) {
    whiteW = targetW;
    whiteH = math.min(availH, whiteW * _kPianoKeyAspect);
    keyboardW = whiteW * n;
  }
  return _PianoKeyMetrics(
    whiteW: whiteW,
    whiteH: whiteH,
    scrollable: keyboardW > viewportW + 1,
  );
}

class _ChordAnalysis {
  const _ChordAnalysis(this.rootPc, this.pattern, this.bassPc);
  final int? rootPc;
  final Map<String, dynamic>? pattern;
  final int? bassPc;
}

class MidiChordsMobileApp extends StatelessWidget {
  const MidiChordsMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    const bg = Color(0xFF202834);
    const surface = Color(0xFF2F3A4B);
    const border = Color(0xFF56627A);
    const text = Color(0xFFE9EDF2);
    const muted = Color(0xFFA8B6C8);
    const accent = Color(0xFFF3BF2F);

    return MaterialApp(
      title: 'MIDI Piano & Guitar Chords',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: bg,
        colorScheme: const ColorScheme.dark(
          primary: accent,
          secondary: accent,
          surface: surface,
          onPrimary: Color(0xFF1A222D),
          onSurface: text,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF161E2A),
          foregroundColor: text,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF182535),
          labelStyle: const TextStyle(color: muted),
          hintStyle: const TextStyle(color: muted),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: border),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: border),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: accent, width: 1.5),
          ),
        ),
        cardTheme: CardThemeData(
          color: surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: border),
          ),
        ),
        useMaterial3: true,
      ),
      home: const _TabletOnlyGate(child: HomeScreen()),
    );
  }
}

class _TabletOnlyGate extends StatelessWidget {
  const _TabletOnlyGate({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final isTablet = media.size.shortestSide >= _kTabletMinShortestSide;
    if (isTablet) return child;
    return child;
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HelpStep {
  const _HelpStep({
    required this.id,
    required this.titleEs,
    required this.titleEn,
    required this.bodyEs,
    required this.bodyEn,
    this.side = _HelpCalloutSide.bottom,
    this.highlightPadding = 8,
  });

  final String id;
  final String titleEs;
  final String titleEn;
  final String bodyEs;
  final String bodyEn;
  final _HelpCalloutSide side;
  final double highlightPadding;
}

class _ResolvedHelpStep {
  const _ResolvedHelpStep({
    required this.step,
    required this.rect,
    required this.highlightRect,
  });

  final _HelpStep step;
  final Rect rect;
  final Rect highlightRect;
}

enum _HelpCalloutSide { top, right, bottom, left }

class _HelpOverlayPainter extends CustomPainter {
  const _HelpOverlayPainter({
    required this.targets,
    required this.activeRect,
    required this.dashPhase,
  });

  final List<Rect> targets;
  final Rect? activeRect;
  final double dashPhase;

  @override
  void paint(Canvas canvas, Size size) {
    final layerRect = Offset.zero & size;
    canvas.saveLayer(layerRect, Paint());
    canvas.drawRect(
      layerRect,
      Paint()..color = Colors.black.withValues(alpha: 0.34),
    );
    final dashedPaint = Paint()
      ..color = const Color(0xD9F3BF2F)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    for (final rect in targets) {
      final outline = RRect.fromRectAndRadius(rect, const Radius.circular(16));
      _drawDashedPath(
        canvas: canvas,
        path: Path()..addRRect(outline),
        paint: dashedPaint,
        dashLength: 12,
        gapLength: 8,
        dashOffset: dashPhase,
      );
    }
    if (activeRect != null) {
      final hole = RRect.fromRectAndRadius(activeRect!, const Radius.circular(16));
      canvas.drawRRect(hole, Paint()..blendMode = BlendMode.clear);
      _drawDashedPath(
        canvas: canvas,
        path: Path()..addRRect(hole),
        paint: Paint()
          ..color = const Color(0xFFF3BF2F)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3,
        dashLength: 14,
        gapLength: 7,
        dashOffset: dashPhase * 1.35,
      );
    }
    canvas.restore();
  }

  void _drawDashedPath({
    required Canvas canvas,
    required Path path,
    required Paint paint,
    required double dashLength,
    required double gapLength,
    required double dashOffset,
  }) {
    for (final metric in path.computeMetrics()) {
      final cycle = dashLength + gapLength;
      var distance = -dashOffset % cycle;
      while (distance < metric.length) {
        final start = distance.clamp(0.0, metric.length);
        final end = (distance + dashLength).clamp(0.0, metric.length);
        if (end > start) {
          canvas.drawPath(metric.extractPath(start, end), paint);
        }
        distance += cycle;
      }
    }
  }

  @override
  bool shouldRepaint(covariant _HelpOverlayPainter oldDelegate) {
    if (oldDelegate.activeRect != activeRect) return true;
    if (oldDelegate.dashPhase != dashPhase) return true;
    if (oldDelegate.targets.length != targets.length) return true;
    for (int i = 0; i < targets.length; i += 1) {
      if (oldDelegate.targets[i] != targets[i]) return true;
    }
    return false;
  }
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  static const Color _bgTop = Color(0xFF2A3442);
  static const Color _bgBottom = Color(0xFF202834);
  static const Color _panelA = Color(0xFF313C4C);
  static const Color _panelB = Color(0xFF273140);
  static const Color _surfaceDark = Color(0xFF182535);
  static const Color _border = Color(0xFF56627A);
  static const Color _text = Color(0xFFE9EDF2);
  static const Color _muted = Color(0xFFA8B6C8);
  static const Color _accent = Color(0xFFF3BF2F);

  bool _isCompactPhone(BuildContext context) =>
      MediaQuery.of(context).size.shortestSide < _kTabletMinShortestSide;

  /// Ancho aproximado de `actions` en AppBar; el `leading` usa el mismo valor para centrar el modo.

  double _compactResultHeight(BoxConstraints constraints, {double minHeight = 170}) {
    final available = constraints.maxHeight.isFinite ? constraints.maxHeight : 640.0;
    return math.max(minHeight, math.min(260.0, available * 0.38));
  }

  bool _isCompactLandscapePhoneForConstraints(BuildContext context, BoxConstraints constraints) =>
      _isCompactPhone(context) && constraints.maxWidth > constraints.maxHeight;
  final TextEditingController _detectionOutputController =
      TextEditingController(text: 'No results');
  final TextEditingController _chordOutputController = TextEditingController(
    text: 'No results',
  );
  final TextEditingController _scaleOutputController = TextEditingController(
    text: 'No results',
  );

  int _tabIndex = 0;
  bool _requestInFlight = false;
  String _instrumentView = 'piano';

  String _language = 'es';
  String _accidental = 'sharp';
  String _guitarHandedness = 'right';
  bool _showKeyNames = true;

  // Changelog state
  List<Map<String, dynamic>> _changelogEntries = <Map<String, dynamic>>[];
  String _lastSeenChangelogVersion = '';
  bool _changelogDontShow = false;

  List<Map<String, dynamic>> _chordPatterns = <Map<String, dynamic>>[];
  List<Map<String, dynamic>> _scalePatterns = <Map<String, dynamic>>[];

  int _chordRootPc = 0;
  String _chordSuffix = '';
  int _chordInversion = 0;
  int _chordMaxInversion = 0;
  int _chordGuitarVariant = 0;
  bool _generationPlayPressed = false;
  final Set<int> _generationInputStaffNotes = <int>{};
  /// MIDI de la última tecla tocada en piano (generación/círculo); coincide con web `generationCurrentNote`.
  int? _generationPianoHighlightMidi;
  Timer? _generationPianoHighlightTimer;
  final Set<int> _heldChordNativeNotes = <int>{};
  /// Limpia el resalte del acorde en pentagrama si no llega pointer-up (p. ej. iOS).
  Timer? _heldChordPlaybackEndTimer;
  final Map<int, AudioPlayer> _heldChordPlayers = <int, AudioPlayer>{};
  /// Invalida reproducciones async (p. ej. `Future.wait` de samples) si hubo `_stopHeldChord` entretanto.
  int _heldChordPlayToken = 0;
  final Map<int, AudioPlayer> _heldInputPlayers = <int, AudioPlayer>{};
  final Map<int, AudioPlayer> _heldMidiInputPlayers = <int, AudioPlayer>{};
  /// Notas actualmente sonando vía salida MIDI (sin AudioPlayer asociado).
  final Set<int> _midiOutHeldNotes = <int>{};
  final Map<String, String> _toneFileCache = <String, String>{};
  bool _samplePlaybackAvailable = true;
  bool _metronomeSampleAvailable = true;
  Map<String, List<Map<String, dynamic>>> _guitarChordCacheByKey =
      <String, List<Map<String, dynamic>>>{};
  bool _audioPlaybackAvailable = true;
  bool _midiInputSoundEnabled = true;
  final MidiCommand _midiCommand = MidiCommand();
  StreamSubscription<MidiPacket>? _midiDataSub;
  StreamSubscription<dynamic>? _midiSetupSub;
  final Map<String, MidiDevice> _midiConnectedDevices = <String, MidiDevice>{};
  final Set<int> _detectionMidiHeldNotes = <int>{};
  final Set<int> _detectionPlayHeldNotes = <int>{};
  final Set<int> _generationMidiHeldNotes = <int>{};  // MIDI notes held in chord generation mode
  bool _midiInputEnabled = false;
  String _midiError = '';
  /// Tras el último evento de nota MIDI en detección, mantenemos la pantalla activa este
  /// tiempo (iOS/Android no exponen “reiniciar el temporizador de reposo” como un toque).
  static const Duration _kMidiResetsIdleDuration = Duration(minutes: 3);
  Timer? _midiIdleExtensionTimer;
  String _soundOutput = 'audio';  // 'audio' or 'midi' - controls note playback routing

  int _scaleTonicPc = 0;
  String _scalePatternName = 'Ionian';
  String _scaleFilterMode = 'basic';  // 'basic' or 'all'
  int _scaleOctaves = 1;  // 1, 2, or 3
  String? _scaleFingeringHand;  // null, 'right', or 'left' for piano fingerings
  Map<int, int> _scaleFingeringsMap = <int, int>{};  // MIDI note -> finger number
  int _scaleBpm = 120;
  bool _scaleLoopRunning = false;
  bool _scaleMetronomeOnly = false;
  int _scaleLoopIndex = 0;
  int _scaleLoopDirection = 1;

  // Interval detection state
  List<int> _intervalNotes = <int>[];  // Last 2 notes for interval pair
  int? _intervalPlayingNote;
  int? _intervalPlayingIdx;
  bool _intervalMelodyPlaying = false;
  bool _intervalMelodyMode = false;   // false = play 2 notes, true = play reference melody
  Timer? _intervalMelodyPlaybackTimer;
  Timer? _scaleLoopTimer;
  int? _scaleCurrentNote;
  bool? _scaleCurrentIsLeft;
  int? _scaleInputRawNote;
  int? _scaleGuitarStartNote;
  final Set<int> _detectionSelectedNotes = <int>{};
  int _metroBpm = 120;
  int _metroVolume = 100;
  int _metroBeatsPerBar = 4;
  int _metroClicksPerBeat = 1;
  bool _metroBarAccent = true;
  bool _metroTimerEnabled = false;
  int _metroTimerMinutes = 2;
  int _metroTimerSeconds = 0;
  Duration _metroRemaining = Duration.zero;
  int _metroCurrentBeat = -1;
  int _metroSubdivisionIndex = 0;
  bool _metroRunning = false;
  Timer? _metroTimer;
  Timer? _metroAnimTimer;
  int _metroDirection = 1;
  int _metroTickCount = 0;
  DateTime _metroMotionStartAt = DateTime.fromMillisecondsSinceEpoch(0);
  FlutterAudioCapture? _audioCapture;
  bool _tunerRunning = false;
  String _tunerNote = '-';
  int _tunerCents = 0;
  double _tunerFreq = 0.0;
  String _tunerError = '';
  String _tunerTuning = 'standard_e';
  int? _tunerCurrentStringIdx;
  double _tunerInputGain = 1.0;
  int _tunerRangeMin = 20;
  int _tunerRangeMax = 500;
  double _tunerSmoothedFreq = 0.0;
  List<double> _tunerSpectrumBins = List<double>.filled(96, 0.0);
  final int _tunerSampleRate = 44100;
  DateTime _lastTunerUiUpdate = DateTime.fromMillisecondsSinceEpoch(0);
  Map<String, dynamic>? _detectionResultJson;
  Map<String, dynamic>? _generatedChordJson;
  Map<String, dynamic>? _generatedScaleJson;
  int _circleTonicPc = 0;
  String _circleKeyMode = 'major';
  int _circleChordRootPc = 0;
  bool _detectionPlayPressed = false;
  bool _inputDragActive = false;
  int? _dragPointer;
  int? _dragCurrentNote;
  Offset? _dragLastGlobalPos;
  DateTime _dragLastSwitchAt = DateTime.fromMillisecondsSinceEpoch(0);
  final ScrollController _pianoScrollController = ScrollController();
  bool _needsPianoScrollSync = false;
  final Set<int> _forbiddenFlashNotes = <int>{};
  final Map<int, Timer> _forbiddenFlashTimers = <int, Timer>{};
  final Map<String, GlobalKey> _helpAnchors = <String, GlobalKey>{};
  late final AnimationController _helpOverlayController;
  bool _helpActive = false;
  String? _helpSelectedId;

  List<int> _enabledModeIndexes() {
    return _kEnableMobileTuner
        ? const <int>[0, 1, 2, 3, 4, 5]
        : const <int>[0, 1, 2, 3, 4];
  }

  List<Map<String, dynamic>> _getFilteredScalePatterns() {
    final patterns = _scalePatterns.cast<Map<String, dynamic>>();
    if (_scaleFilterMode == 'basic') {
      return patterns
          .where((p) => _kScaleBasicNames.contains(p['name'] as String?))
          .toList();
    }
    return patterns;
  }

  List<int> _getScaleNotesForOctaves(List<int> noteMidi, int octaves) {
    if (noteMidi.isEmpty || octaves <= 1) {
      return noteMidi;
    }

    final result = <int>[...noteMidi];

    if (octaves >= 2) {
      // Add lower octave
      final lowerOctave = noteMidi
          .where((note) => note - 12 >= 0)
          .map((note) => note - 12)
          .toList();
      result.insertAll(0, lowerOctave);
    }

    if (octaves >= 3) {
      // Add upper octave
      final upperOctave = noteMidi.map((note) => note + 12).toList();
      result.addAll(upperOctave);
    }

    return result;
  }

  GlobalKey _helpAnchorKey(String id) =>
      _helpAnchors.putIfAbsent(id, () => GlobalKey(debugLabel: 'help_$id'));

  Widget _helpAnchor(String id, Widget child) {
    return KeyedSubtree(key: _helpAnchorKey(id), child: child);
  }

  List<_HelpStep> _helpStepsForCurrentMode() {
    final common = <_HelpStep>[
      _HelpStep(
        id: 'mode_select',
        titleEs: 'Selector de modo',
        titleEn: 'Mode selector',
        bodyEs:
            'Aqui cambias entre deteccion, generacion, circulo de quintas, escalas, metronomo y afinador.',
        bodyEn:
            'Switch between detection, generation, circle of fifths, scales, metronome, and tuner here.',
        highlightPadding: 4,
      ),
      _HelpStep(
        id: 'midi_toggle',
        titleEs: 'Entrada MIDI',
        titleEn: 'MIDI input',
        bodyEs:
            'Activa o desactiva la entrada de un teclado o controlador MIDI.',
        bodyEn:
            'Enable or disable input from a MIDI keyboard or controller.',
        highlightPadding: -3,
      ),
      _HelpStep(
        id: 'accidental',
        titleEs: 'Sostenidos o bemoles',
        titleEn: 'Sharps or flats',
        bodyEs:
            'Elige si prefieres nombres de notas con sostenidos (#) o bemoles (b).',
        bodyEn:
            'Choose whether note names should prefer sharps (#) or flats (b).',
        highlightPadding: -3,
      ),
      _HelpStep(
        id: 'settings',
        titleEs: 'Configuracion',
        titleEn: 'Settings',
        bodyEs:
            'Abre el panel de configuracion general, incluido el idioma de la interfaz.',
        bodyEn:
            'Open the general settings panel, including interface language.',
        side: _HelpCalloutSide.left,
        highlightPadding: -2,
      ),
    ];
    final modeSpecific = switch (_tabIndex) {
      0 => <_HelpStep>[
          _HelpStep(
            id: 'detection_staff',
            titleEs: 'Pentagrama de deteccion',
            titleEn: 'Detection staff',
            bodyEs:
                'Muestra las notas activas, las extras y el resultado detectado.',
            bodyEn:
                'Shows active notes, extras, and the detected result.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'detection_controls',
            titleEs: 'Panel de deteccion',
            titleEn: 'Detection panel',
            bodyEs:
                'Aqui se ve el resultado y los controles principales del modo deteccion.',
            bodyEn:
                'This panel contains the current result and main detection controls.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'detection_play_button',
            titleEs: 'Boton reproducir',
            titleEn: 'Play button',
            bodyEs:
                'Reproduce o mantiene sonando las notas detectadas mientras mantienes pulsado.',
            bodyEn:
                'Plays or sustains the detected notes while you keep it pressed.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'detection_clear_button',
            titleEs: 'Boton limpiar',
            titleEn: 'Clear button',
            bodyEs:
                'Borra las notas introducidas y recalcula la deteccion desde cero.',
            bodyEn:
                'Clears the entered notes and recalculates detection from scratch.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'detection_midi_sound_button',
            titleEs: 'Boton MIDI',
            titleEn: 'MIDI button',
            bodyEs:
                'Activa o silencia el sonido local al tocar notas desde MIDI o desde el piano en pantalla.',
            bodyEn:
                'Enables or mutes local sound when you play notes from MIDI or the on-screen piano.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'detection_result_chord',
            titleEs: 'Fila de acorde',
            titleEn: 'Chord row',
            bodyEs:
                'Muestra el acorde detectado actualmente.',
            bodyEn:
                'Shows the currently detected chord.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'detection_result_notes',
            titleEs: 'Fila de notas',
            titleEn: 'Notes row',
            bodyEs:
                'Muestra el listado de notas que participan en el resultado.',
            bodyEn:
                'Shows the list of notes that make up the result.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'detection_result_extras',
            titleEs: 'Fila de sobrantes',
            titleEn: 'Extras row',
            bodyEs:
                'Muestra las notas que no encajan en el acorde principal.',
            bodyEn:
                'Shows notes that do not fit the main chord.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'detection_result_intervals',
            titleEs: 'Fila de intervalos',
            titleEn: 'Intervals row',
            bodyEs:
                'Muestra la distancia entre las notas detectadas.',
            bodyEn:
                'Shows the spacing between detected notes.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'detection_instrument',
            titleEs: 'Piano interactivo',
            titleEn: 'Interactive piano',
            bodyEs:
                'Toca en el piano para introducir notas y reflejarlas en el pentagrama.',
            bodyEn:
                'Play the piano to enter notes and mirror them on the staff.',
            side: _HelpCalloutSide.top,
          ),
        ],
      1 => <_HelpStep>[
          _HelpStep(
            id: 'generation_staff',
            titleEs: 'Pentagrama del acorde',
            titleEn: 'Chord staff',
            bodyEs:
                'Muestra el acorde generado y resalta lo que estas reproduciendo.',
            bodyEn:
                'Shows the generated chord and highlights what is being played.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'generation_controls',
            titleEs: 'Panel de generacion',
            titleEn: 'Generation panel',
            bodyEs:
                'Configura tonica, tipo e inversion del acorde que quieres generar.',
            bodyEn:
                'Configure root, type, and inversion of the chord you want to generate.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'generation_play_button',
            titleEs: 'Boton reproducir',
            titleEn: 'Play button',
            bodyEs:
                'Reproduce o mantiene sonando el acorde generado mientras mantienes pulsado.',
            bodyEn:
                'Plays or sustains the generated chord while you keep it pressed.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_tonic',
            titleEs: 'Tonica',
            titleEn: 'Tonic',
            bodyEs:
                'Aqui eliges la nota base del acorde que quieres generar.',
            bodyEn:
                'Choose the root note of the chord you want to generate here.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_variant',
            titleEs: 'Variante',
            titleEn: 'Variant',
            bodyEs:
                'Define el tipo de acorde, como mayor, menor, disminuido o sus variaciones.',
            bodyEn:
                'Defines the chord type, such as major, minor, diminished, or its variations.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_inversion',
            titleEs: 'Inversion',
            titleEn: 'Inversion',
            bodyEs:
                'Cambia el orden de las notas del acorde manteniendo su misma funcion armonica.',
            bodyEn:
                'Changes the order of chord notes while keeping the same harmonic function.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_result_chord',
            titleEs: 'Resultado del acorde',
            titleEn: 'Chord result',
            bodyEs:
                'Muestra el nombre del acorde generado actualmente.',
            bodyEn:
                'Shows the currently generated chord name.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'generation_result_notes',
            titleEs: 'Notas del acorde',
            titleEn: 'Chord notes',
            bodyEs:
                'Muestra las notas que forman el acorde generado.',
            bodyEn:
                'Shows the notes that make up the generated chord.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'generation_result_intervals',
            titleEs: 'Intervalos del acorde',
            titleEn: 'Chord intervals',
            bodyEs:
                'Muestra la distancia entre las notas del acorde generado.',
            bodyEn:
                'Shows the spacing between the notes of the generated chord.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'generation_instrument_piano',
            titleEs: 'Boton Piano',
            titleEn: 'Piano button',
            bodyEs:
                'Cambia la vista y la reproduccion del acorde al piano.',
            bodyEn:
                'Switches the chord view and playback to piano.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_instrument_guitar',
            titleEs: 'Boton Guitarra',
            titleEn: 'Guitar button',
            bodyEs:
                'Cambia la vista y la reproduccion del acorde a la guitarra.',
            bodyEn:
                'Switches the chord view and playback to guitar.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_guitar_hand',
            titleEs: 'Mano de la guitarra',
            titleEn: 'Guitar handedness',
            bodyEs:
                'Ajusta la visualizacion para diestro o zurdo en la guitarra.',
            bodyEn:
                'Adjusts the guitar display for right- or left-handed view.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_guitar_variant',
            titleEs: 'Variantes de acorde',
            titleEn: 'Chord variations',
            bodyEs:
                'Permite recorrer distintas posiciones o variantes del mismo acorde en la guitarra.',
            bodyEn:
                'Lets you cycle through different positions or variants of the same chord on guitar.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'generation_instrument',
            titleEs: 'Piano o guitarra',
            titleEn: 'Piano or guitar',
            bodyEs:
                'Visualiza y prueba el acorde generado en el instrumento seleccionado.',
            bodyEn:
                'Visualize and try the generated chord on the selected instrument.',
            side: _HelpCalloutSide.top,
          ),
        ],
      2 => <_HelpStep>[
          _HelpStep(
            id: 'circle_staff',
            titleEs: 'Pentagrama',
            titleEn: 'Staff',
            bodyEs:
                'Muestra el acorde generado desde el circulo segun la tonalidad elegida.',
            bodyEn:
                'Shows the chord generated from the circle for the selected key.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'circle_canvas',
            titleEs: 'Circulo de quintas',
            titleEn: 'Circle of fifths',
            bodyEs:
                'Toca un sector para elegir un acorde diatonico. Manten pulsado: anillo exterior = tonica mayor; interior = modo menor relativo.',
            bodyEn:
                'Tap a sector to pick a diatonic chord. Long-press: outer ring = major tonic; inner = relative minor.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'circle_play',
            titleEs: 'Reproducir',
            titleEn: 'Play',
            bodyEs:
                'Mantén pulsado el botón de reproducción para oír el acorde en el instrumento.',
            bodyEn:
                'Hold the play button to hear the chord on the instrument.',
            side: _HelpCalloutSide.left,
          ),
        ],
      3 => <_HelpStep>[
          _HelpStep(
            id: 'scales_staff',
            titleEs: 'Pentagrama de escala',
            titleEn: 'Scale staff',
            bodyEs:
                'Muestra las notas de la escala y la nota actual durante la reproduccion.',
            bodyEn:
                'Shows scale notes and the current note during playback.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'scales_controls',
            titleEs: 'Panel de escalas',
            titleEn: 'Scales panel',
            bodyEs:
                'Configura tonica, tipo, velocidad y reproduccion de la escala.',
            bodyEn:
                'Configure tonic, type, speed, and playback of the scale.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'scales_tonic',
            titleEs: 'Tonica',
            titleEn: 'Tonic',
            bodyEs:
                'Aqui eliges la nota base de la escala.',
            bodyEn:
                'Choose the root note of the scale here.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_pattern',
            titleEs: 'Tipo de escala',
            titleEn: 'Scale type',
            bodyEs:
                'Selecciona el patron o modo de escala que quieres estudiar o reproducir.',
            bodyEn:
                'Select the scale pattern or mode you want to study or play.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_play_button',
            titleEs: 'Boton reproducir',
            titleEn: 'Play button',
            bodyEs:
                'Inicia o detiene la reproduccion automatica de la escala.',
            bodyEn:
                'Starts or stops automatic scale playback.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_metronome_only',
            titleEs: 'Modo metrico',
            titleEn: 'Metronome mode',
            bodyEs:
                'Activa un modo simplificado para practicar la escala con pulso y tempo.',
            bodyEn:
                'Enables a simplified mode to practice the scale with pulse and tempo.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_volume',
            titleEs: 'Volumen',
            titleEn: 'Volume',
            bodyEs:
                'Controla el volumen cuando el modo metrico de escalas esta activo.',
            bodyEn:
                'Controls volume when scale metronome mode is active.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_bpm',
            titleEs: 'Velocidad',
            titleEn: 'Speed',
            bodyEs:
                'Ajusta la velocidad de reproduccion de la escala en BPM.',
            bodyEn:
                'Adjusts scale playback speed in BPM.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_result_scale',
            titleEs: 'Resultado de la escala',
            titleEn: 'Scale result',
            bodyEs:
                'Muestra la escala seleccionada actualmente.',
            bodyEn:
                'Shows the currently selected scale.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'scales_result_notes',
            titleEs: 'Notas de la escala',
            titleEn: 'Scale notes',
            bodyEs:
                'Muestra las notas que forman la escala.',
            bodyEn:
                'Shows the notes that make up the scale.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'scales_result_intervals',
            titleEs: 'Intervalos de la escala',
            titleEn: 'Scale intervals',
            bodyEs:
                'Muestra la distancia entre las notas de la escala.',
            bodyEn:
                'Shows the spacing between the notes of the scale.',
            side: _HelpCalloutSide.left,
            highlightPadding: -2,
          ),
          _HelpStep(
            id: 'scales_instrument_piano',
            titleEs: 'Boton Piano',
            titleEn: 'Piano button',
            bodyEs:
                'Cambia la vista de la escala al piano.',
            bodyEn:
                'Switches the scale view to piano.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_instrument_guitar',
            titleEs: 'Boton Guitarra',
            titleEn: 'Guitar button',
            bodyEs:
                'Cambia la vista de la escala a la guitarra.',
            bodyEn:
                'Switches the scale view to guitar.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_guitar_hand',
            titleEs: 'Mano de la guitarra',
            titleEn: 'Guitar handedness',
            bodyEs:
                'Ajusta la visualizacion de la guitarra para diestro o zurdo.',
            bodyEn:
                'Adjusts the guitar display for right- or left-handed view.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_instrument',
            titleEs: 'Instrumento de escala',
            titleEn: 'Scale instrument',
            bodyEs:
                'Permite tocar y seguir visualmente la escala en piano o guitarra.',
            bodyEn:
                'Lets you play and visually follow the scale on piano or guitar.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'scales_octaves',
            titleEs: 'Número de octavas',
            titleEn: 'Number of octaves',
            bodyEs:
                'Muestra la escala en 1, 2 o 3 octavas sobre el teclado. Con 2 octavas se añade la octava inferior; con 3 también la superior.',
            bodyEn:
                'Displays the scale over 1, 2, or 3 octaves on the keyboard. With 2 octaves a lower octave is added; with 3 also an upper one.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'scales_fingering',
            titleEs: 'Digitación',
            titleEn: 'Fingering',
            bodyEs:
                'Selecciona la mano para ver la numeración de los dedos encima (subida) y debajo (bajada) del teclado. Los números en rojo/azul oscuro indican un cruce de dedos.',
            bodyEn:
                'Select a hand to see finger numbers above (ascending) and below (descending) the keyboard. Numbers in dark red/blue indicate a finger crossing.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
        ],
      4 => <_HelpStep>[
          _HelpStep(
            id: 'metronome_bead_row',
            titleEs: 'Bolas de pulso',
            titleEn: 'Beat balls',
            bodyEs:
                'Muestran los pulsos del compas y resaltan el pulso actual mientras corre el metronomo.',
            bodyEn:
                'They show the beats of the bar and highlight the current beat while the metronome runs.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_motion_axis',
            titleEs: 'Eje de movimiento',
            titleEn: 'Motion axis',
            bodyEs:
                'Marca el recorrido de la bola roja que acompasa visualmente el pulso.',
            bodyEn:
                'Marks the path of the red ball that visually follows the pulse.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_timer_display',
            titleEs: 'Zona del temporizador',
            titleEn: 'Timer area',
            bodyEs:
                'Aqui aparece la cuenta atras cuando activas el temporizador del metronomo.',
            bodyEn:
                'The countdown appears here when you enable the metronome timer.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_toggle_left',
            titleEs: 'Boton del metronomo',
            titleEn: 'Metronome button',
            bodyEs:
                'Inicia o detiene el metronomo directamente desde la vista principal.',
            bodyEn:
                'Starts or stops the metronome directly from the main view.',
            side: _HelpCalloutSide.top,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_controls',
            titleEs: 'Panel del metronomo',
            titleEn: 'Metronome panel',
            bodyEs:
                'Aqui ajustas tempo, compas, subdivision, acento y temporizador.',
            bodyEn:
                'Adjust tempo, meter, subdivision, accent, and timer here.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'metronome_volume',
            titleEs: 'Volumen',
            titleEn: 'Volume',
            bodyEs:
                'Controla el volumen general del metronomo.',
            bodyEn:
                'Controls the overall metronome volume.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_tempo',
            titleEs: 'Tempo',
            titleEn: 'Tempo',
            bodyEs:
                'Ajusta la velocidad del metronomo en BPM.',
            bodyEn:
                'Adjusts metronome speed in BPM.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_beats',
            titleEs: 'Pulsos por compas',
            titleEn: 'Beats per bar',
            bodyEs:
                'Define cuantas pulsaciones tiene cada compas.',
            bodyEn:
                'Defines how many beats there are in each bar.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_subdivision',
            titleEs: 'Subdivision',
            titleEn: 'Subdivision',
            bodyEs:
                'Elige cuantas subdivisiones sonaran dentro de cada pulso.',
            bodyEn:
                'Choose how many subdivisions sound within each beat.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_accent',
            titleEs: 'Acento',
            titleEn: 'Accent',
            bodyEs:
                'Activa o desactiva el acento del primer pulso de cada compas.',
            bodyEn:
                'Enables or disables the accent on the first beat of each bar.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_timer',
            titleEs: 'Temporizador',
            titleEn: 'Timer',
            bodyEs:
                'Permite limitar la duracion del metronomo con minutos y segundos.',
            bodyEn:
                'Lets you limit metronome duration with minutes and seconds.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'metronome_instrument',
            titleEs: 'Piano del metronomo',
            titleEn: 'Metronome piano',
            bodyEs:
                'Mientras corre el metronomo puedes seguir viendo y tocando notas en el piano.',
            bodyEn:
                'While the metronome runs you can still view and play notes on the piano.',
            side: _HelpCalloutSide.top,
          ),
        ],
      5 => <_HelpStep>[
          _HelpStep(
            id: 'tuner_staff',
            titleEs: 'Vista del afinador',
            titleEn: 'Tuner view',
            bodyEs:
                'Muestra afinacion, desviacion en cents y cuerda objetivo.',
            bodyEn:
                'Shows tuning, cents deviation, and target string.',
            side: _HelpCalloutSide.top,
          ),
          _HelpStep(
            id: 'tuner_controls',
            titleEs: 'Panel del afinador',
            titleEn: 'Tuner panel',
            bodyEs:
                'Configura la afinacion, la entrada y el rango del analisis.',
            bodyEn:
                'Configure tuning, input, and analysis range here.',
            side: _HelpCalloutSide.left,
          ),
          _HelpStep(
            id: 'tuner_toggle',
            titleEs: 'Boton del afinador',
            titleEn: 'Tuner button',
            bodyEs:
                'Inicia o detiene la escucha del microfono para afinar.',
            bodyEn:
                'Starts or stops microphone listening for tuning.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'tuner_tuning_select',
            titleEs: 'Afinacion',
            titleEn: 'Tuning',
            bodyEs:
                'Selecciona la afinacion objetivo del instrumento.',
            bodyEn:
                'Selects the target tuning of the instrument.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'tuner_gain',
            titleEs: 'Ganancia',
            titleEn: 'Gain',
            bodyEs:
                'Ajusta la sensibilidad de entrada del afinador.',
            bodyEn:
                'Adjusts the tuner input sensitivity.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'tuner_range',
            titleEs: 'Rango de frecuencia',
            titleEn: 'Frequency range',
            bodyEs:
                'Define el rango de frecuencias que el afinador analizara.',
            bodyEn:
                'Defines the frequency range the tuner will analyze.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
          _HelpStep(
            id: 'tuner_readout',
            titleEs: 'Lectura del afinador',
            titleEn: 'Tuner readout',
            bodyEs:
                'Muestra la nota detectada, la desviacion y la frecuencia actual.',
            bodyEn:
                'Shows the detected note, deviation, and current frequency.',
            side: _HelpCalloutSide.left,
            highlightPadding: 2,
          ),
        ],
      _ => const <_HelpStep>[],
    };
    return <_HelpStep>[...common, ...modeSpecific];
  }

  bool _helpAvailableForCurrentMode() => _helpStepsForCurrentMode().isNotEmpty;

  void _setHelpMode(bool enabled) {
    _helpActive = enabled && _helpAvailableForCurrentMode();
    _helpSelectedId = null;
    if (_helpActive) {
      _helpOverlayController.repeat();
    } else {
      _helpOverlayController.stop();
      _helpOverlayController.value = 0;
    }
  }

  void _toggleHelpMode() {
    setState(() {
      _setHelpMode(!_helpActive);
    });
  }

  Rect? _helpRectFor(BuildContext overlayContext, String id) {
    final key = _helpAnchors[id];
    if (key == null) return null;
    final targetContext = key.currentContext;
    if (targetContext == null) return null;
    final targetBox = targetContext.findRenderObject();
    final overlayBox = overlayContext.findRenderObject();
    if (targetBox is! RenderBox ||
        overlayBox is! RenderBox ||
        !targetBox.hasSize) {
      return null;
    }
    final offset = targetBox.localToGlobal(Offset.zero, ancestor: overlayBox);
    return offset & targetBox.size;
  }

  List<_ResolvedHelpStep> _resolvedHelpSteps(BuildContext overlayContext) {
    return _helpStepsForCurrentMode()
        .map((step) {
          final rect = _helpRectFor(overlayContext, step.id);
          if (rect == null || rect.width <= 0 || rect.height <= 0) {
            return null;
          }
          return _ResolvedHelpStep(
            step: step,
            rect: rect,
            highlightRect: rect.inflate(step.highlightPadding),
          );
        })
        .whereType<_ResolvedHelpStep>()
        .toList(growable: false);
  }

  _ResolvedHelpStep? _selectedHelpStep(List<_ResolvedHelpStep> resolved) {
    if (resolved.isEmpty) return null;
    if (_helpSelectedId == null) return null;
    for (final item in resolved) {
      if (item.step.id == _helpSelectedId) return item;
    }
    return null;
  }

  Rect _helpCalloutRect({
    required Rect target,
    required Size screenSize,
    required _HelpCalloutSide side,
    required EdgeInsets safePadding,
  }) {
    const margin = 16.0;
    const gap = 12.0;
    final width = math.min(screenSize.width - (margin * 2), 344.0);
    final largeScreen = screenSize.shortestSide >= 700.0;
    final height = math.min(
      math.max(
        screenSize.height * (largeScreen ? 0.255 : 0.225),
        largeScreen ? 232.0 : 196.0,
      ),
      largeScreen ? 300.0 : 248.0,
    );
    var left = target.left;
    var top = target.bottom + gap;
    switch (side) {
      case _HelpCalloutSide.top:
        left = target.center.dx - (width / 2);
        top = target.top - height - gap;
      case _HelpCalloutSide.right:
        left = target.right + gap;
        top = target.center.dy - (height / 2);
      case _HelpCalloutSide.bottom:
        left = target.center.dx - (width / 2);
        top = target.bottom + gap;
      case _HelpCalloutSide.left:
        left = target.left - width - gap;
        top = target.center.dy - (height / 2);
    }
    left = left.clamp(margin, screenSize.width - width - margin);
    top = top.clamp(
      safePadding.top + margin,
      screenSize.height - height - safePadding.bottom - margin,
    );
    return Rect.fromLTWH(left, top, width, height);
  }

  Rect _metronomeBeatRowRect(Size size) {
    final count = math.max(1, _metroBeatsPerBar);
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final spacing = count == 1 ? (right - left) : (right - left) / (count - 1);
    final baseR = (30 - (count * 0.75)).clamp(7.0, 24.0);
    final maxRBySpacing = (spacing * 0.42 - 2).clamp(6.0, 1000.0);
    final normalR = math.min(baseR, maxRBySpacing);
    final activeR = math.min(normalR + 2.0, maxRBySpacing + 1.5);
    return Rect.fromLTRB(
      left - activeR,
      yTop - activeR,
      right + activeR,
      yTop + activeR,
    );
  }

  Rect _metronomeMotionAxisRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    return Rect.fromLTRB(left - 12, axisY - 16, right + 12, axisY + 16);
  }

  Rect _metronomeTimerRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    final fontSize = math.min(44.0, size.height * 0.24);
    final centerY = axisY + ((size.height - axisY) * 0.5);
    final rectHeight = math.max(52.0, fontSize + 10.0);
    final rawTop = centerY - (rectHeight / 2);
    final minTop = axisY + 56.0;
    final maxTop = size.height - rectHeight - 16.0;
    // En algunos dispositivos/tamaños (Android 14) el rango puede invertirse
    // y `clamp` lanza ArgumentError si min > max.
    final top = maxTop >= minTop ? rawTop.clamp(minTop, maxTop) : math.max(0.0, math.min(rawTop, maxTop));
    final rectWidth = math.min(220.0, math.max(160.0, size.width * 0.26));
    final centerX = (left + right) / 2;
    return Rect.fromLTWH(centerX - (rectWidth / 2), top, rectWidth, rectHeight);
  }

  Rect _metronomeCenterButtonRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final axisRect = _metronomeMotionAxisRect(size);
    final timerRect = _metronomeTimerRect(size);
    final buttonHeight = 46.0;
    final buttonWidth = math.min(286.0, math.max(210.0, size.width * 0.34));
    final centerY = (axisRect.bottom + timerRect.top) / 2;
    final minTop = axisRect.bottom + 6.0;
    final maxTop = timerRect.top - buttonHeight - 6.0;
    final idealTop = centerY - (buttonHeight / 2);
    final top = maxTop >= minTop
        ? idealTop.clamp(minTop, maxTop)
        : math.max(axisRect.bottom + 2.0, idealTop);
    final leftPos = ((left + right) / 2) - (buttonWidth / 2);
    return Rect.fromLTWH(leftPos, top, buttonWidth, buttonHeight);
  }

  String _staffHelpIdForCurrentMode() => switch (_tabIndex) {
        0 => 'detection_staff',
        1 => 'generation_staff',
        2 => 'circle_staff',
        3 => 'scales_staff',
        4 => 'metronome_bead_row',
        5 => 'tuner_staff',
        _ => 'detection_staff',
      };

  String _ui(String es, String en) => _language == 'en' ? en : es;
  String _modeLabel(int index) {
    switch (index) {
      case 0:
        return _ui('Detección de Acordes', 'Chord Detection');
      case 1:
        return _ui('Generación de Acordes', 'Chord Generator');
      case 2:
        return _ui('Círculo de quintas', 'Circle of Fifths');
      case 3:
        return _ui('Escalas', 'Scales');
      case 4:
        return _ui('Metrónomo', 'Metronome');
      case 5:
        return _ui('Detección de Intervalos', 'Interval Detection');
      case 6:
        return _ui('Afinador', 'Tuner');
      default:
        return _ui('Detección de Acordes', 'Chord Detection');
    }
  }

  Future<void> _openSettingsPanel() async {
    String selectedLanguage = _language;
    bool selectedShowKeyNames = _showKeyNames;
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) => AlertDialog(
            backgroundColor: _panelA,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: _border),
            ),
            title: Text(
              _ui('Configuración', 'Settings'),
              style: const TextStyle(color: _text, fontWeight: FontWeight.w700),
            ),
            content: SizedBox(
              width: 420,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  DropdownButtonFormField<String>(
                    key: ValueKey<String>('settings_lang_$selectedLanguage'),
                    initialValue: selectedLanguage,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: InputDecoration(
                      labelText: _ui('Idioma', 'Language'),
                    ),
                    items: const <DropdownMenuItem<String>>[
                      DropdownMenuItem<String>(value: 'es', child: Text('Español')),
                      DropdownMenuItem<String>(value: 'en', child: Text('English')),
                    ],
                    onChanged: (value) {
                      if (value != null) setDialogState(() => selectedLanguage = value);
                    },
                  ),
                  const SizedBox(height: 4),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      _ui('Mostrar nombres en teclas', 'Show key names'),
                      style: const TextStyle(color: _text),
                    ),
                    value: selectedShowKeyNames,
                    activeColor: _accent,
                    onChanged: (v) => setDialogState(() => selectedShowKeyNames = v),
                  ),
                  const SizedBox(height: 8),
                  FutureBuilder<PackageInfo>(
                    future: PackageInfo.fromPlatform(),
                    builder: (context, snapshot) {
                      final versionText = snapshot.hasData
                          ? 'v${snapshot.data!.version} (${snapshot.data!.buildNumber})'
                          : '...';
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Text(
                            _ui('Versión de la app', 'App version'),
                            style: const TextStyle(fontWeight: FontWeight.w600, color: _muted),
                          ),
                          const SizedBox(height: 4),
                          Text(versionText,
                              style: const TextStyle(fontWeight: FontWeight.w800, color: _text)),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 8,
                            runSpacing: 4,
                            children: <Widget>[
                              TextButton.icon(
                                onPressed: () async {
                                  final uri = Uri.parse('https://freemidichords.com/');
                                  if (await canLaunchUrl(uri)) {
                                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                                  }
                                },
                                icon: const Icon(Icons.language, size: 18),
                                label: Text(_ui('Visitar la web', 'Visit website')),
                                style: TextButton.styleFrom(foregroundColor: _accent),
                              ),
                              TextButton.icon(
                                onPressed: () async {
                                  Navigator.of(dialogContext).pop();
                                  await _showChangelogDialog(fromSettings: true);
                                },
                                icon: const Icon(Icons.new_releases_outlined, size: 18),
                                label: Text(_ui('Novedades', "What's new")),
                                style: TextButton.styleFrom(foregroundColor: _accent),
                              ),
                            ],
                          ),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
            actions: <Widget>[
              TextButton(
                onPressed: () => Navigator.of(dialogContext).pop(),
                child: Text(_ui('Cancelar', 'Cancel')),
              ),
              FilledButton(
                onPressed: () async {
                  final langChanged = _language != selectedLanguage;
                  setState(() {
                    _language = selectedLanguage;
                    _showKeyNames = selectedShowKeyNames;
                  });
                  await _savePrefs();
                  if (langChanged) await _loadMeta();
                  if (dialogContext.mounted) Navigator.of(dialogContext).pop();
                },
                child: Text(_ui('Aplicar', 'Apply')),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  void initState() {
    super.initState();
    _helpOverlayController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );
    _initMidiInput();
    unawaited(_initPlatformAudioWorkarounds());
    unawaited(_loadPrefsAndStart());
  }

  Future<void> _loadPrefsAndStart() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _language = prefs.getString('language') ?? 'es';
      _showKeyNames = prefs.getBool('showKeyNames') ?? true;
      _lastSeenChangelogVersion = prefs.getString('lastSeenChangelogVersion') ?? '';
      _changelogDontShow = prefs.getBool('changelogDontShow') ?? false;
      _scaleOctaves = prefs.getInt('scaleOctaves') ?? 1;
      final finger = prefs.getString('scaleFingeringHand');
      _scaleFingeringHand = (finger == 'left' || finger == 'right') ? finger : null;
      final savedTab = prefs.getInt('tabIndex');
      if (savedTab != null && savedTab >= 0 && savedTab <= 6) {
        _tabIndex = savedTab;
      }
    });
    await _loadMeta();
    await _loadChangelog();
    if (mounted) _maybeShowChangelogPopup();
  }

  Future<void> _savePrefs() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('language', _language);
    await prefs.setBool('showKeyNames', _showKeyNames);
    await prefs.setString('lastSeenChangelogVersion', _lastSeenChangelogVersion);
    await prefs.setBool('changelogDontShow', _changelogDontShow);
    await prefs.setInt('scaleOctaves', _scaleOctaves);
    if (_scaleFingeringHand != null) {
      await prefs.setString('scaleFingeringHand', _scaleFingeringHand!);
    } else {
      await prefs.remove('scaleFingeringHand');
    }
    await prefs.setInt('tabIndex', _tabIndex);
  }

  Future<void> _loadChangelog() async {
    try {
      final raw = await rootBundle.loadString('assets/changelog.json');
      final list = (jsonDecode(raw) as List<dynamic>).cast<Map<String, dynamic>>();
      if (mounted) setState(() => _changelogEntries = list);
    } catch (_) {}
  }

  String get _latestChangelogVersion =>
      _changelogEntries.isNotEmpty ? (_changelogEntries.first['version'] as String? ?? '') : '';

  void _maybeShowChangelogPopup() {
    if (_changelogDontShow) return;
    final latest = _latestChangelogVersion;
    if (latest.isEmpty || latest == _lastSeenChangelogVersion) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) unawaited(_showChangelogDialog(fromSettings: false));
    });
  }

  Future<void> _showChangelogDialog({bool fromSettings = false}) async {
    bool dontShowAgain = _changelogDontShow;
    await showDialog<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setSt) {
          // Build version sections: [{version, date, items:[text,...]}]
          final sections = _changelogEntries.map((v) {
            final publishedItems = (v['items'] as List<dynamic>? ?? [])
                .cast<Map<String, dynamic>>()
                .where((it) => it['publish'] == true)
                .map((it) => (_language == 'en' ? it['en'] : it['es']) as String? ?? '')
                .where((t) => t.isNotEmpty)
                .toList();
            return (
              version: v['version'] as String? ?? '',
              date: v['date'] as String? ?? '',
              items: publishedItems,
            );
          }).where((s) => s.items.isNotEmpty).take(6).toList();

          return AlertDialog(
            backgroundColor: _panelA,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: _border),
            ),
            title: Text(
              _ui('Novedades', "What's new"),
              style: const TextStyle(color: _text, fontWeight: FontWeight.w700),
            ),
            content: SizedBox(
              width: 460,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxHeight: 380),
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: sections.map((s) => Padding(
                          padding: const EdgeInsets.only(bottom: 14),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Row(
                                children: <Widget>[
                                  Text(
                                    s.version,
                                    style: const TextStyle(
                                      color: _accent,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 13,
                                    ),
                                  ),
                                  if (s.date.isNotEmpty) ...<Widget>[
                                    const SizedBox(width: 8),
                                    Text(
                                      s.date,
                                      style: const TextStyle(color: _muted, fontSize: 11),
                                    ),
                                  ],
                                ],
                              ),
                              const SizedBox(height: 6),
                              ...s.items.map((text) => Padding(
                                padding: const EdgeInsets.only(bottom: 6),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: <Widget>[
                                    const Text('• ', style: TextStyle(color: _muted, fontWeight: FontWeight.bold)),
                                    Expanded(
                                      child: Text(text, style: const TextStyle(color: _text, height: 1.4, fontSize: 13)),
                                    ),
                                  ],
                                ),
                              )),
                            ],
                          ),
                        )).toList(),
                      ),
                    ),
                  ),
                  ...<Widget>[
                    const SizedBox(height: 12),
                    Row(
                      children: <Widget>[
                        Checkbox(
                          value: dontShowAgain,
                          activeColor: _accent,
                          onChanged: (v) => setSt(() => dontShowAgain = v ?? false),
                        ),
                        Expanded(
                          child: GestureDetector(
                            onTap: () => setSt(() => dontShowAgain = !dontShowAgain),
                            child: Text(
                              _ui('No volver a mostrar', "Don't show again"),
                              style: const TextStyle(color: _muted),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            actions: <Widget>[
              FilledButton(
                onPressed: () => Navigator.of(ctx).pop(),
                child: Text(_ui('Cerrar', 'Close')),
              ),
            ],
          );
        },
      ),
    );
    // Runs after dialog closes for ANY reason (button, back, tap outside)
    setState(() {
      _lastSeenChangelogVersion = _latestChangelogVersion;
      if (!fromSettings) _changelogDontShow = dontShowAgain;
    });
    await _savePrefs();
  }

  @override
  void dispose() {
    _heldChordPlaybackEndTimer?.cancel();
    _generationPianoHighlightTimer?.cancel();
    _metroTimer?.cancel();
    _metroAnimTimer?.cancel();
    _scaleLoopTimer?.cancel();
    _stopHeldChord();
    _stopHeldInputs();
    _stopHeldMidiInputs();
    unawaited(_disableMidiInput());
    _midiDataSub?.cancel();
    _midiSetupSub?.cancel();
    for (final t in _forbiddenFlashTimers.values) {
      t.cancel();
    }
    _forbiddenFlashTimers.clear();
    _audioCapture?.stop();
    _detectionOutputController.dispose();
    _chordOutputController.dispose();
    _scaleOutputController.dispose();
    _helpOverlayController.dispose();
    _pianoScrollController.dispose();
    _cancelMidiScreenActivityExtension();
    super.dispose();
  }

  int _positiveMod12(int value) {
    final m = value % 12;
    return m < 0 ? m + 12 : m;
  }

  bool get _preferFlat => _accidental == 'flat';

  Future<void> _initPlatformAudioWorkarounds() async {
    if (Platform.isAndroid) return;
    if (!Platform.isIOS) return;
    try {
      final isSimulator =
          await _kPlatformChannel.invokeMethod<bool>('isIosSimulator') ?? false;
      if (!isSimulator) return;
      _samplePlaybackAvailable = false;
      _metronomeSampleAvailable = false;
    } catch (_) {}
  }

  String _noteNameLocal(
    int midiNote, {
    required String language,
    required bool preferFlat,
    bool withOctave = true,
  }) {
    const sharpEs = <String>[
      'Do',
      'Do#',
      'Re',
      'Re#',
      'Mi',
      'Fa',
      'Fa#',
      'Sol',
      'Sol#',
      'La',
      'La#',
      'Si',
    ];
    const sharpEn = <String>[
      'C',
      'C#',
      'D',
      'D#',
      'E',
      'F',
      'F#',
      'G',
      'G#',
      'A',
      'A#',
      'B',
    ];
    const flatAliasesEs = <int, String>{
      1: 'Re♭',
      3: 'Mi♭',
      6: 'Sol♭',
      8: 'La♭',
      10: 'Si♭',
    };
    const flatAliasesEn = <int, String>{
      1: 'D♭',
      3: 'E♭',
      6: 'G♭',
      8: 'A♭',
      10: 'B♭',
    };
    final names = language == 'en' ? sharpEn : sharpEs;
    final flatAliases = language == 'en' ? flatAliasesEn : flatAliasesEs;
    final pc = _positiveMod12(midiNote);
    final name = preferFlat ? (flatAliases[pc] ?? names[pc]) : names[pc];
    if (!withOctave) {
      return name;
    }
    final octave = (midiNote ~/ 12) - 1;
    return '$name$octave';
  }

  int _tonicLetterIndex(int tonicPc, bool preferFlats) {
    const mapSharp = <int, int>{
      0: 0,
      1: 0,
      2: 1,
      3: 1,
      4: 2,
      5: 3,
      6: 3,
      7: 4,
      8: 4,
      9: 5,
      10: 5,
      11: 6,
    };
    const mapFlat = <int, int>{
      0: 0,
      1: 1,
      2: 1,
      3: 2,
      4: 2,
      5: 3,
      6: 4,
      7: 4,
      8: 5,
      9: 5,
      10: 6,
      11: 6,
    };
    final map = preferFlats ? mapFlat : mapSharp;
    return map[_positiveMod12(tonicPc)] ?? 0;
  }

  String? _applyAccidental(String base, int diff) {
    switch (diff) {
      case 0:
        return base;
      case 1:
        return '$base#';
      case -1:
        return '$base♭';
      case 2:
        return '$base##';
      case -2:
        return '$base♭♭';
      default:
        return null;
    }
  }

  String _spellByDegree({
    required int rootPc,
    required int targetPc,
    required int degree,
    required String language,
    required bool preferFlats,
    int? midiNote,
    bool withOctave = false,
  }) {
    const letterEs = <String>['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si'];
    const letterEn = <String>['C', 'D', 'E', 'F', 'G', 'A', 'B'];
    const basePcs = <int>[0, 2, 4, 5, 7, 9, 11];
    final letters = language == 'en' ? letterEn : letterEs;
    final tonicLetter = _tonicLetterIndex(rootPc, preferFlats);
    final letterIdx = (tonicLetter + degree) % 7;
    final naturalPc = basePcs[letterIdx];
    var diff = _positiveMod12(targetPc - naturalPc);
    if (diff > 6) {
      diff -= 12;
    }
    final spelled = _applyAccidental(letters[letterIdx], diff);
    if (spelled == null) {
      final fallback = midiNote ?? targetPc;
      return _noteNameLocal(
        fallback,
        language: language,
        preferFlat: preferFlats,
        withOctave: withOctave,
      );
    }
    if (!withOctave) {
      return spelled;
    }
    if (midiNote == null) {
      return spelled;
    }
    final octave = (midiNote ~/ 12) - 1;
    return '$spelled$octave';
  }

  int _chordIntervalDegree(int interval, String suffix) {
    final value = interval;
    if (value == 0 || value == 12) return 0;
    if (value == 1 || value == 2 || value == 13 || value == 14) return 1;
    if (value == 3 || value == 4 || value == 15) return 2;
    if (value == 5 || value == 17) return 3;
    if (value == 6 || value == 18) {
      if (suffix.contains('b5') || suffix.contains('dim')) return 4;
      return 3;
    }
    if (value == 7) return 4;
    if (value == 8) {
      if (suffix.contains('#5') || suffix.contains('aug')) return 4;
      return 5;
    }
    if (value == 9 || value == 21) return 5;
    if (value == 10 || value == 11) return 6;
    return math.max(0, math.min(6, value % 7));
  }

  /// Igual que `isMinorSuffix` / worker: `m…` pero no `maj…`.
  bool _isMinorChordSuffix(String suffix) {
    return suffix.startsWith('m') && !suffix.startsWith('maj');
  }

  /// Recuentos de #/♭ de armadura por tónica (misma tabla que la web).
  ({int? sharpCount, int? flatCount}) _keySignatureSharpFlatCounts(
    int tonicPc,
    bool isMinor,
  ) {
    final pc = _positiveMod12(tonicPc);
    final sharpMap = isMinor
        ? const <int, int>{
            4: 1,
            11: 2,
            6: 3,
            1: 4,
            8: 5,
            3: 6,
            10: 7,
          }
        : const <int, int>{
            7: 1,
            2: 2,
            9: 3,
            4: 4,
            11: 5,
            6: 6,
            1: 7,
          };
    final flatMap = isMinor
        ? const <int, int>{
            2: 1,
            7: 2,
            0: 3,
            5: 4,
            10: 5,
            3: 6,
          }
        : const <int, int>{
            5: 1,
            10: 2,
            3: 3,
            8: 4,
            1: 5,
            6: 6,
          };
    return (sharpCount: sharpMap[pc], flatCount: flatMap[pc]);
  }

  /// Misma regla que API/worker y `chordSymbolPreferFlat` en app.js: menos
  /// alteraciones; empate enarmónico → bemoles.
  bool _chordSymbolPreferFlat(int rootPc, bool isMinor) {
    final c = _keySignatureSharpFlatCounts(rootPc, isMinor);
    final sc = c.sharpCount;
    final fc = c.flatCount;
    if (sc == null && fc == null) {
      return false;
    }
    if (sc == null) {
      return true;
    }
    if (fc == null) {
      return false;
    }
    if (fc < sc) {
      return true;
    }
    if (sc < fc) {
      return false;
    }
    return true;
  }

  bool _scalePrefersMinor(String patternName) {
    const minorNames = <String>{
      'Aeolian',
      'Dorian',
      'Phrygian',
      'Locrian',
      'Super Locrian',
      'Half Diminished',
      'Minor Pentatonic',
      'Minor Blues',
    };
    return patternName.contains('Minor') || minorNames.contains(patternName);
  }

  /// `tiePreferFlat`: null → empate enarmónico a sostenidos; true/false fuerza.
  ({int count, bool preferFlats}) _keySignatureCountForTonic(
    int tonicPc,
    bool isMinor, {
    bool? tiePreferFlat,
  }) {
    final c = _keySignatureSharpFlatCounts(tonicPc, isMinor);
    final sc = c.sharpCount;
    final fc = c.flatCount;
    if (sc == null && fc == null) {
      return (count: 0, preferFlats: false);
    }
    if (sc == null) {
      return (count: fc!, preferFlats: true);
    }
    if (fc == null) {
      return (count: sc, preferFlats: false);
    }
    if (fc < sc) {
      return (count: fc, preferFlats: true);
    }
    if (sc < fc) {
      return (count: sc, preferFlats: false);
    }
    if (tiePreferFlat == true) {
      return (count: fc, preferFlats: true);
    }
    return (count: sc, preferFlats: false);
  }

  /// Si el usuario eligió ♭ y hay empate #/♭, armadura en bemoles (web).
  ({int count, bool preferFlats}) _applyFlatKeySigIfUiFlatAndTie(
    ({int count, bool preferFlats}) sig,
    int tonicPc,
    bool isMinor,
  ) {
    if (!_preferFlat) {
      return sig;
    }
    final c = _keySignatureSharpFlatCounts(tonicPc, isMinor);
    final sc = c.sharpCount;
    final fc = c.flatCount;
    if (sc != null && fc != null && sc == fc) {
      return (count: fc, preferFlats: true);
    }
    return sig;
  }

  /// Equivalente a `getStaffContext()` en `app.js` (armadura del pentagrama).
  ({int count, bool preferFlats}) _staffKeySignatureForCurrentTab() {
    if (_tabIndex == 5) return (count: 0, preferFlats: false);
    final tieFromSelect = _preferFlat;
    if (_tabIndex == 3 && _generatedScaleJson != null) {
      final name =
          (_generatedScaleJson!['pattern_name'] as String?) ?? 'Ionian';
      final isMinor = _scalePrefersMinor(name);
      final tonic = _positiveMod12(
        (_generatedScaleJson!['tonic_pc'] as num?)?.toInt() ?? 0,
      );
      var sig = _keySignatureCountForTonic(
        tonic,
        isMinor,
        tiePreferFlat: tieFromSelect,
      );
      sig = _applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
      return sig;
    }
    if (_tabIndex == 2) {
      // La tónica del anillo existe siempre; no depender de haber generado JSON.
      final isMinor = _circleKeyMode == 'minor';
      final tonic = _positiveMod12(_circleTonicPc);
      var sig = _keySignatureCountForTonic(
        tonic,
        isMinor,
        tiePreferFlat: tieFromSelect,
      );
      sig = _applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
      return sig;
    }
    if (_tabIndex == 1 && _generatedChordJson != null) {
      final suffix = (_generatedChordJson!['suffix'] as String?) ?? '';
      final isMinor = _isMinorChordSuffix(suffix);
      final tonic = _positiveMod12(
        (_generatedChordJson!['root_pc'] as num?)?.toInt() ?? 0,
      );
      var sig = _keySignatureCountForTonic(
        tonic,
        isMinor,
        tiePreferFlat: tieFromSelect,
      );
      sig = _applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
      return sig;
    }
    if (_tabIndex == 0 && _detectionResultJson != null) {
      final rpc = _detectionResultJson!['root_pc'];
      if (rpc is num && rpc.isFinite) {
        final tonic = _positiveMod12(rpc.toInt());
        final suffix =
            (_detectionResultJson!['suffix'] as String?) ?? '';
        final isMinor = _isMinorChordSuffix(suffix);
        final tieLikeChordName = _chordSymbolPreferFlat(tonic, isMinor);
        var sig = _keySignatureCountForTonic(
          tonic,
          isMinor,
          tiePreferFlat: tieLikeChordName,
        );
        sig = _applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
        return sig;
      }
    }
    return (count: 0, preferFlats: false);
  }

  List<int> _voicedIntervalsForInversion(List<int> intervals, int inversion) {
    if (intervals.isEmpty) {
      return <int>[];
    }
    final total = intervals.length;
    final inversionIdx = inversion.clamp(0, total - 1);
    final rotated = List<int>.generate(
      total,
      (i) => intervals[(inversionIdx + i) % total],
    );
    final voiced = <int>[];
    for (final raw in rotated) {
      var value = raw;
      if (voiced.isNotEmpty) {
        while (value <= voiced.last) {
          value += 12;
        }
      }
      voiced.add(value);
    }
    return voiced;
  }

  List<Map<String, dynamic>> _chordPatternsForUi() {
    final priority = <String, int>{
      for (int i = 0; i < _kCommonChordSuffixOrder.length; i += 1)
        _kCommonChordSuffixOrder[i]: i,
    };
    final sorted = _kChordPatternDefs
        .map(
          (p) => <String, dynamic>{
            'suffix': p['suffix'],
            'intervals': List<int>.from(
              p['intervals'] as List<dynamic>? ?? const <dynamic>[],
            ),
          },
        )
        .toList();
    sorted.sort((a, b) {
      final aSuffix = (a['suffix'] as String? ?? '');
      final bSuffix = (b['suffix'] as String? ?? '');
      final aIntervals =
          (a['intervals'] as List<dynamic>? ?? const <dynamic>[]).length;
      final bIntervals =
          (b['intervals'] as List<dynamic>? ?? const <dynamic>[]).length;
      final aPrio = priority[aSuffix] ?? _kCommonChordSuffixOrder.length;
      final bPrio = priority[bSuffix] ?? _kCommonChordSuffixOrder.length;
      if (aPrio != bPrio) return aPrio.compareTo(bPrio);
      if (aIntervals != bIntervals) return aIntervals.compareTo(bIntervals);
      return aSuffix.compareTo(bSuffix);
    });
    return sorted;
  }

  List<Map<String, dynamic>> _scalePatternsLocal(String language) {
    return _kScalePatternDefs
        .map((pattern) {
          final name = pattern['name'] as String? ?? 'Ionian';
          final localized = language == 'es'
              ? (_kScaleNameEs[name] ?? name)
              : name;
          return <String, dynamic>{
            'name': name,
            'localized_name': localized,
            'intervals': List<int>.from(
              pattern['intervals'] as List<dynamic>? ?? const <dynamic>[],
            ),
          };
        })
        .toList(growable: false);
  }

  _ChordAnalysis _analyzeChordNotes(Set<int> notes) {
    if (notes.isEmpty) {
      return const _ChordAnalysis(null, null, null);
    }
    final pcs = notes.map(_positiveMod12).toSet();
    final suffixPriority = <String, int>{
      for (int i = 0; i < _kCommonChordSuffixOrder.length; i += 1)
        _kCommonChordSuffixOrder[i]: i,
    };
    var bestScore = -999;
    var bestComplexity = -999;
    var bestPriority = _kCommonChordSuffixOrder.length;
    int? bestRoot;
    Map<String, dynamic>? bestPattern;
    for (int root = 0; root < 12; root += 1) {
      for (final pattern in _kChordPatternDefs) {
        final intervals =
            (pattern['intervals'] as List<dynamic>? ?? const <dynamic>[])
                .map((e) => e as int)
                .toList(growable: false);
        final template = intervals.map((i) => (root + i) % 12).toSet();
        final extra = pcs.difference(template).length;
        final missing = template.difference(pcs).length;
        int score;
        if (extra == 0 && missing == 0) {
          score = 100;
        } else if (missing == 0) {
          score = 70 - extra;
        } else if (extra == 0) {
          score = 40 - missing;
        } else {
          continue;
        }
        final complexity = -intervals.length;
        final suffix = pattern['suffix'] as String? ?? '';
        final priority =
            suffixPriority[suffix] ?? _kCommonChordSuffixOrder.length;
        final better = score > bestScore ||
            (score == bestScore && complexity > bestComplexity) ||
            (score == bestScore &&
                complexity == bestComplexity &&
                priority < bestPriority);
        if (better) {
          bestScore = score;
          bestComplexity = complexity;
          bestPriority = priority;
          bestRoot = root;
          bestPattern = pattern;
        }
      }
    }
    final bassPc = notes.reduce(math.min) % 12;
    return _ChordAnalysis(bestRoot, bestPattern, bassPc);
  }

  Map<String, dynamic> _generateChordLocal({
    required int rootPc,
    required String suffix,
    required int inversion,
    required String language,
    required bool preferFlat,
  }) {
    final selected = _kChordPatternDefs.firstWhere(
      (p) => (p['suffix'] as String? ?? '') == suffix,
      orElse: () => _kChordPatternDefs.first,
    );
    final intervals = List<int>.from(
      selected['intervals'] as List<dynamic>? ?? const <dynamic>[],
    );
    if (intervals.isEmpty) {
      return <String, dynamic>{
        'root_pc': _positiveMod12(rootPc),
        'suffix': selected['suffix'] as String? ?? '',
        'inversion': 0,
        'name': '-',
        'notes_midi': <int>[],
        'notes': <String>[],
      };
    }
    final safeInversion = inversion.clamp(0, intervals.length - 1);
    final rootMidi = 60 + _positiveMod12(rootPc);
    final voicedIntervals = _voicedIntervalsForInversion(
      intervals,
      safeInversion,
    );
    final notesMidi = voicedIntervals.map((i) => rootMidi + i).toList();
    final noteLabels = <String>[];
    final noteLabelsNoOct = <String>[];
    for (int i = 0; i < notesMidi.length; i += 1) {
      final interval = voicedIntervals[i];
      final midiNote = notesMidi[i];
      final degree = _chordIntervalDegree(interval, suffix);
      final pc = _positiveMod12(midiNote);
      noteLabels.add(
        _spellByDegree(
          rootPc: rootPc,
          targetPc: pc,
          degree: degree,
          language: language,
          preferFlats: preferFlat,
          midiNote: midiNote,
          withOctave: true,
        ),
      );
      noteLabelsNoOct.add(
        _spellByDegree(
          rootPc: rootPc,
          targetPc: pc,
          degree: degree,
          language: language,
          preferFlats: preferFlat,
          midiNote: midiNote,
          withOctave: false,
        ),
      );
    }
    final rootName = _spellByDegree(
      rootPc: rootPc,
      targetPc: _positiveMod12(rootPc),
      degree: 0,
      language: language,
      preferFlats: preferFlat,
      midiNote: rootPc,
      withOctave: false,
    );
    var chordName = '$rootName$suffix';
    if (safeInversion > 0 && noteLabelsNoOct.isNotEmpty) {
      chordName = '$chordName/${noteLabelsNoOct.first}';
    }
    return <String, dynamic>{
      'root_pc': _positiveMod12(rootPc),
      'suffix': suffix,
      'inversion': safeInversion,
      'name': chordName,
      'notes_midi': notesMidi,
      'notes': noteLabels,
      'notes_no_octave': noteLabelsNoOct,
      'intervals': voicedIntervals,
    };
  }

  Map<String, dynamic> _detectChordLocal({
    required List<int> notes,
    required String language,
    required bool preferFlat,
  }) {
    final midiNotes = notes.toSet().toList()..sort();
    if (midiNotes.isEmpty) {
      return <String, dynamic>{
        'name': '-',
        'extras_midi': <int>[],
        'notes_midi': <int>[],
        'notes': <String>[],
        'extras': <String>[],
      };
    }
    final pcs = midiNotes.map(_positiveMod12).toSet();
    if (pcs.length == 1) {
      final single = midiNotes.first;
      final namePf =
          _chordSymbolPreferFlat(_positiveMod12(single), false);
      return <String, dynamic>{
        'name': _noteNameLocal(
          single,
          language: language,
          preferFlat: namePf,
          withOctave: false,
        ),
        'notes_midi': midiNotes,
        'notes': midiNotes
            .map(
              (n) => _noteNameLocal(
                n,
                language: language,
                preferFlat: preferFlat,
                withOctave: true,
              ),
            )
            .toList(),
        'extras_midi': <int>[],
        'extras': <String>[],
      };
    }
    final analysis = _analyzeChordNotes(midiNotes.toSet());
    final root = analysis.rootPc;
    final pattern = analysis.pattern;
    final bassPc = analysis.bassPc;
    if (root == null || pattern == null) {
      return <String, dynamic>{
        'name': midiNotes
            .map(
              (n) => _noteNameLocal(
                n,
                language: language,
                preferFlat: preferFlat,
                withOctave: false,
              ),
            )
            .join(' + '),
        'notes_midi': midiNotes,
        'notes': midiNotes
            .map(
              (n) => _noteNameLocal(
                n,
                language: language,
                preferFlat: preferFlat,
                withOctave: true,
              ),
            )
            .toList(),
        'extras_midi': <int>[],
        'extras': <String>[],
      };
    }
    final suffix = pattern['suffix'] as String? ?? '';
    final intervals = List<int>.from(
      pattern['intervals'] as List<dynamic>? ?? const <dynamic>[],
    );
    final degreeByPc = <int, int>{};
    for (final interval in intervals) {
      final pc = _positiveMod12(root + interval);
      degreeByPc.putIfAbsent(pc, () => _chordIntervalDegree(interval, suffix));
    }
    final namePf = _chordSymbolPreferFlat(root, _isMinorChordSuffix(suffix));
    final rootName = _spellByDegree(
      rootPc: root,
      targetPc: root,
      degree: 0,
      language: language,
      preferFlats: namePf,
      midiNote: root,
      withOctave: false,
    );
    var chordName = '$rootName$suffix';
    String? resolvedBassName;
    if (bassPc != null && bassPc != root) {
      final bassDegree = degreeByPc[bassPc];
      resolvedBassName = bassDegree == null
          ? _noteNameLocal(
              bassPc,
              language: language,
              preferFlat: namePf,
              withOctave: false,
            )
          : _spellByDegree(
              rootPc: root,
              targetPc: bassPc,
              degree: bassDegree,
              language: language,
              preferFlats: namePf,
              midiNote: bassPc,
              withOctave: false,
            );
      chordName = '$chordName/$resolvedBassName';
    }
    final suffixNames =
        language == 'es' ? _kChordSuffixNamesEs : _kChordSuffixNamesEn;
    final inversionNames =
        language == 'es' ? _kInversionNamesEs : _kInversionNamesEn;
    final baseDesc = suffixNames[suffix];
    String? description;
    if (baseDesc != null) {
      if (bassPc != null && bassPc != root && resolvedBassName != null) {
        final bassInterval = (bassPc - root + 12) % 12;
        final invIndex = intervals.indexOf(bassInterval);
        if (invIndex > 0 && invIndex < inversionNames.length) {
          description = '$baseDesc, ${inversionNames[invIndex]}';
        } else {
          final bassWord = language == 'es' ? 'bajo en' : 'bass on';
          description = '$baseDesc, $bassWord $resolvedBassName';
        }
      } else {
        description = baseDesc;
      }
    }
    final expectedPcs = intervals.map((i) => _positiveMod12(root + i)).toSet();
    final extras = midiNotes
        .where((n) => !expectedPcs.contains(n % 12))
        .toList();
    // Panel de notas: #/♭ del usuario (`noteName`), no escritura por grado.
    final noteLabels = midiNotes
        .map(
          (n) => _noteNameLocal(
            n,
            language: language,
            preferFlat: preferFlat,
            withOctave: true,
          ),
        )
        .toList();
    return <String, dynamic>{
      'name': chordName,
      'notes_midi': midiNotes,
      'notes': noteLabels,
      'extras_midi': extras,
      'extras': extras
          .map(
            (n) => _noteNameLocal(
              n,
              language: language,
              preferFlat: preferFlat,
              withOctave: true,
            ),
          )
          .toList(),
      'root_pc': root,
      'suffix': suffix,
      if (description case final String d) 'description': d,
    };
  }

  Map<String, dynamic> _generateScaleLocal({
    required int tonicPc,
    required String patternName,
    required String language,
    required bool preferFlat,
  }) {
    final selected = _kScalePatternDefs.firstWhere(
      (p) => (p['name'] as String? ?? '') == patternName,
      orElse: () => _kScalePatternDefs.first,
    );
    final intervals = List<int>.from(
      selected['intervals'] as List<dynamic>? ?? const <dynamic>[],
    );
    final rootMidi = 60 + _positiveMod12(tonicPc);
    final notesMidi = intervals.map((i) => rootMidi + i).toList();
    final names = <String>[];
    for (int idx = 0; idx < notesMidi.length; idx += 1) {
      final midiNote = notesMidi[idx];
      names.add(
        _spellByDegree(
          rootPc: tonicPc,
          targetPc: _positiveMod12(midiNote),
          degree: idx,
          language: language,
          preferFlats: preferFlat,
          midiNote: midiNote,
          withOctave: true,
        ),
      );
    }
    final selectedName = selected['name'] as String? ?? patternName;
    final localized = language == 'es'
        ? (_kScaleNameEs[selectedName] ?? selectedName)
        : selectedName;
    return <String, dynamic>{
      'tonic_pc': _positiveMod12(tonicPc),
      'pattern_name': selectedName,
      'pattern_localized_name': localized,
      'notes_midi': notesMidi,
      'notes': names,
      'intervals': intervals,
    };
  }

  Future<void> _loadMeta() async {
    try {
      await _loadGuitarChordCache();
      final chordPatterns = _chordPatternsForUi();
      final scalePatterns = _scalePatternsLocal(_language);
      setState(() {
        _chordPatterns = chordPatterns;
        _scalePatterns = scalePatterns;
        if (_chordPatterns.isNotEmpty) {
          final current = _chordPatterns.where(
            (p) => (p['suffix'] as String? ?? '') == _chordSuffix,
          );
          if (current.isEmpty) {
            _chordSuffix = (_chordPatterns.first['suffix'] as String? ?? '');
          }
          _recomputeMaxInversion();
        }
        if (_scalePatterns.isNotEmpty) {
          final current = _scalePatterns.where(
            (p) => (p['name'] as String? ?? '') == _scalePatternName,
          );
          if (current.isEmpty) {
            _scalePatternName =
                (_scalePatterns.first['name'] as String? ?? 'Ionian');
          }
        }
      });
      if (_tabIndex == 0 && !_requestInFlight) {
        unawaited(_callDetect());
      } else if (_tabIndex == 1 && !_requestInFlight) {
        unawaited(_callGenerateChord());
      } else if (_tabIndex == 2 && !_requestInFlight) {
        unawaited(_callCircleGenerateChord());
      } else if (_tabIndex == 3 && !_requestInFlight) {
        unawaited(_callGenerateScale());
      }
    } catch (err) {
      _detectionOutputController.text = '${_ui('Error cargando meta', 'Error loading metadata')}: $err';
    }
  }

  Future<void> _loadGuitarChordCache() async {
    if (_guitarChordCacheByKey.isNotEmpty) return;
    try {
      final raw = await rootBundle.loadString('assets/guitar_chord_cache.json');
      final decoded = jsonDecode(raw);
      if (decoded is! Map) return;
      final byKey = decoded['by_app_key'];
      if (byKey is! Map) return;
      final parsed = <String, List<Map<String, dynamic>>>{};
      byKey.forEach((key, value) {
        if (key is! String || value is! List) return;
        final variations = value
            .whereType<Map>()
            .map(
              (item) => item.map(
                (k, v) => MapEntry<String, dynamic>(k.toString(), v),
              ),
            )
            .toList();
        parsed[key] = variations;
      });
      _guitarChordCacheByKey = parsed;
    } catch (_) {
      _guitarChordCacheByKey = <String, List<Map<String, dynamic>>>{};
    }
  }

  void _recomputeMaxInversion() {
    final match = _chordPatterns.firstWhere(
      (p) => (p['suffix'] as String? ?? '') == _chordSuffix,
      orElse: () => _chordPatterns.isNotEmpty
          ? _chordPatterns.first
          : <String, dynamic>{
              'intervals': <int>[0],
            },
    );
    final intervals =
        (match['intervals'] as List<dynamic>? ?? <dynamic>[0]).length;
    _chordMaxInversion = intervals > 0 ? intervals - 1 : 0;
    if (_chordInversion > _chordMaxInversion) {
      _chordInversion = _chordMaxInversion;
    }
  }

  List<int> _extractMidiList(
    Map<String, dynamic> json,
    List<String> preferredKeys,
  ) {
    for (final key in preferredKeys) {
      final raw = json[key];
      if (raw is List) {
        return raw
            .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
            .whereType<int>()
            .toList();
      }
    }
    return <int>[];
  }

  /// Igual que web `formatIntervalsFromMidi` y `music_theory.format_intervals`.
  String _intervalTextFromMidiList(List<int> notes) {
    final ordered = notes.map((n) => n).toSet().toList()..sort();
    if (ordered.isEmpty) return '-';
    final parts = <String>['0'];
    for (var i = 1; i < ordered.length; i++) {
      parts.add('+${ordered[i] - ordered[i - 1]}');
    }
    return parts.join(' ');
  }

  Set<int> get _activeDetectionNotes {
    if (_detectionPlayHeldNotes.isNotEmpty) return _detectionPlayHeldNotes;
    if (_detectionMidiHeldNotes.isNotEmpty) return _detectionMidiHeldNotes;
    return _detectionSelectedNotes;
  }

  void _cancelMidiScreenActivityExtension() {
    _midiIdleExtensionTimer?.cancel();
    _midiIdleExtensionTimer = null;
    unawaited(() async {
      try {
        await WakelockPlus.disable();
      } catch (_) {}
    }());
  }

  /// Cada nota MIDI (u off) renueva la ventana: equivale a “hubo interacción” para no
  /// entrar en reposo mientras sigues tocando (con pausas hasta [_kMidiResetsIdleDuration]).
  void _bumpMidiScreenActivityTimer() {
    if (!_midiInputEnabled || _tabIndex != 0) {
      return;
    }
    _midiIdleExtensionTimer?.cancel();
    unawaited(() async {
      try {
        await WakelockPlus.enable();
      } catch (_) {}
    }());
    _midiIdleExtensionTimer = Timer(_kMidiResetsIdleDuration, () {
      _midiIdleExtensionTimer = null;
      if (!mounted) {
        return;
      }
      unawaited(() async {
        try {
          await WakelockPlus.disable();
        } catch (_) {}
      }());
    });
  }

  void _initMidiInput() {
    _midiDataSub = _midiCommand.onMidiDataReceived?.listen(_onMidiPacket);
    _midiSetupSub = _midiCommand.onMidiSetupChanged?.listen((_) {
      if (_midiInputEnabled) {
        unawaited(_refreshMidiConnections());
      }
    });
  }

  void _onMidiPacket(MidiPacket packet) {
    if (!_midiInputEnabled) return;
    final bytes = packet.data;
    var hadNoteChannelMessage = false;
    for (var i = 0; i + 2 < bytes.length; i += 3) {
      final status = bytes[i] & 0xF0;
      final note = bytes[i + 1];
      final velocity = bytes[i + 2];
      final isNoteOn = status == 0x90 && velocity > 0;
      final isNoteOff = status == 0x80 || (status == 0x90 && velocity == 0);
      if (!isNoteOn && !isNoteOff) continue;
      hadNoteChannelMessage = true;

      // Track held notes for MIDI highlighting in generation mode (tabIndex 1 or 2)
      if (_tabIndex == 1 || _tabIndex == 2) {
        if (isNoteOn) {
          _generationMidiHeldNotes.add(note);
        } else {
          _generationMidiHeldNotes.remove(note);
        }
      }

      // Interval detection mode handling (tabIndex 5)
      if (_tabIndex == 5) {
        if (isNoteOn) {
          _addIntervalNote(note);
          if (_midiInputSoundEnabled) {
            unawaited(playNote(note, instrument: 'piano'));
          }
        }
        continue;
      }

      // Scale mode handling (tabIndex 3): show forbidden on non-scale MIDI notes
      if (_tabIndex == 3 && isNoteOn && _generatedScaleJson != null) {
        final scaleNotes = _scaleRhNotes();
        final scalePcs = scaleNotes.map((n) => n % 12).toSet();
        if (scalePcs.isNotEmpty && !scalePcs.contains(note % 12)) {
          _showForbiddenOnPiano(note);
        }
        continue;
      }

      // Detection mode handling (tabIndex 0)
      if (_tabIndex == 0) {
        if (isNoteOn) {
          if (_detectionMidiHeldNotes.isEmpty &&
              _detectionSelectedNotes.isNotEmpty) {
            _detectionSelectedNotes.clear();
            _stopHeldInputs();
          }
          _detectionMidiHeldNotes.add(note);
          if (_midiInputSoundEnabled) {
            unawaited(_startHeldMidiInputNote(note, instrument: 'piano'));
          }
        } else {
          _detectionMidiHeldNotes.remove(note);
          _releaseHeldMidiInputNote(note);
        }
      }
    }
    if (hadNoteChannelMessage) {
      _bumpMidiScreenActivityTimer();
    }
    if (mounted) setState(() {});
    if (_tabIndex == 0 && !_requestInFlight) {
      unawaited(_callDetect());
    }
  }

  Future<void> _refreshMidiConnections() async {
    try {
      final devices = await _midiCommand.devices;
      final available = (devices ?? <MidiDevice>[])
          .whereType<MidiDevice>()
          .toList();
      final availableIds = available.map((d) => d.id).toSet();

      for (final entry in _midiConnectedDevices.entries.toList()) {
        if (availableIds.contains(entry.key)) continue;
        try {
          _midiCommand.disconnectDevice(entry.value);
        } catch (_) {}
        _midiConnectedDevices.remove(entry.key);
      }

      for (final device in available) {
        if (_midiConnectedDevices.containsKey(device.id)) continue;
        try {
          _midiCommand.connectToDevice(device);
          _midiConnectedDevices[device.id] = device;
        } catch (_) {}
      }

      if (_midiInputEnabled) {
        _midiError = _midiConnectedDevices.isEmpty
            ? _ui(
                'No se encontró ningún dispositivo MIDI conectado.',
                'No connected MIDI device was found.',
              )
            : '';
      }
    } catch (_) {}
    if (mounted) setState(() {});
  }

  Future<void> _disableMidiInput() async {
    _midiInputEnabled = false;
    _midiError = '';
    for (final device in _midiConnectedDevices.values.toList()) {
      try {
        _midiCommand.disconnectDevice(device);
      } catch (_) {}
    }
    _midiConnectedDevices.clear();
    _detectionMidiHeldNotes.clear();
    _stopHeldMidiInputs();
    _cancelMidiScreenActivityExtension();
    if (mounted) setState(() {});
    if (_tabIndex == 0 && !_requestInFlight) {
      unawaited(_callDetect());
    }
  }

  Future<void> _toggleMidiInput() async {
    if (_midiInputEnabled) {
      await _disableMidiInput();
      return;
    }
    _midiInputEnabled = true;
    _midiError = '';
    if (mounted) setState(() {});
    await _refreshMidiConnections();
  }

  Set<int> _selectedChordGuitarNotes() {
    final variations = _chordGuitarVariations();
    if (variations.isNotEmpty) {
      final idx = _chordGuitarVariant.clamp(0, variations.length - 1);
      return _variationNotes(variations[idx]).toSet();
    }
    final fallback = _fallbackChordGuitarVoicings();
    if (fallback.isNotEmpty) {
      final idx = _chordGuitarVariant.clamp(0, fallback.length - 1);
      return fallback[idx].toSet();
    }
    return <int>{};
  }

  Set<int> _staffNotesForCurrentTab() {
    if (_tabIndex == 5) {
      if (_intervalMelodyMode) {
        return _getIntervalMelodyNotes().whereType<int>().toSet();
      }
      return _intervalNotes.toSet();
    }
    if (_tabIndex == 0) {
      if (_detectionResultJson != null) {
        final midi = _extractMidiList(_detectionResultJson!, <String>[
          'notes_midi',
        ]);
        if (midi.isNotEmpty) return midi.toSet();
      }
      return _activeDetectionNotes;
    }
    if ((_tabIndex == 1 || _tabIndex == 2) && _generatedChordJson != null) {
      final rh = _extractMidiList(_generatedChordJson!, <String>['notes_midi']);
      if (_instrumentView == 'guitar') {
        final selected = _selectedChordGuitarNotes();
        return selected.isNotEmpty ? selected : rh.toSet();
      }
      final lh = rh.map((n) => n - 12).where((n) => n >= 0);
      return <int>{...rh, ...lh};
    }
    if (_tabIndex == 3 && _generatedScaleJson != null) {
      final rh = _scaleRhNotes();
      final lh = _scaleLhNotes(rh);
      return <int>{...rh, ...lh};
    }
    return <int>{};
  }

  Set<int> _generationPlayingNotesForStaff() {
    if (_tabIndex != 1 && _tabIndex != 2) return <int>{};
    final rawNotes = <int>{
      ..._heldChordPlayers.keys,
      ..._heldChordNativeNotes,
    };
    // Piano y guitarra: mapear MIDI de reproducción al espacio del pentagrama actual
    // (la rama guitarra en crudo podía dejar un MIDI que, tras `guitarDisplayVoicing`,
    // coincidía con una nota del acorde aunque ya no hubiera reproducción coherente).
    final staffNotes = <int>{..._generationInputStaffNotes};
    for (final note in rawNotes) {
      final mapped = _generationStaffNoteForPitch(note, includeBass: true);
      if (mapped != null) {
        staffNotes.add(mapped);
      }
    }
    return staffNotes;
  }

  bool _isShiftPressed() {
    final keys = HardwareKeyboard.instance.logicalKeysPressed;
    return keys.contains(LogicalKeyboardKey.shiftLeft) ||
        keys.contains(LogicalKeyboardKey.shiftRight);
  }

  bool get _hasDetectionNotes => _activeDetectionNotes.isNotEmpty;

  Set<int> _staffExtrasForCurrentTab() {
    if (_tabIndex == 0 && _detectionResultJson != null) {
      return _extractMidiList(_detectionResultJson!, <String>[
        'extras_midi',
      ]).toSet();
    }
    return <int>{};
  }

  Set<int> _activeMidiForInstrument() {
    if (_tabIndex == 5) {
      if (_intervalMelodyMode) {
        return _getIntervalMelodyNotes().whereType<int>().toSet();
      }
      return _intervalNotes.toSet();
    }
    if (_tabIndex == 0) return _activeDetectionNotes;
    if ((_tabIndex == 1 || _tabIndex == 2) && _generatedChordJson != null) {
      final rh = _extractMidiList(_generatedChordJson!, <String>[
        'notes_midi',
      ]).toSet();
      if (_instrumentView == 'guitar') {
        final selected = _selectedChordGuitarNotes();
        return selected.isNotEmpty ? selected : rh;
      }
      final lh = rh.map((n) => n - 12).where((n) => n >= 0);
      return <int>{...rh, ...lh};
    }
    if (_tabIndex == 3 && _generatedScaleJson != null) {
      final rh = _scaleRhNotes();
      final notes = <int>{...rh};
      if (_scaleCurrentNote != null) notes.add(_scaleCurrentNote!);
      if (_instrumentView == 'piano' && _scaleInputRawNote != null) {
        notes.add(_scaleInputRawNote!);
      }
      return notes;
    }
    return <int>{};
  }

  int? _generationStaffNoteForPitch(int note, {required bool includeBass}) {
    if (_generatedChordJson == null) return null;
    if (_instrumentView == 'guitar') {
      final selected = _selectedChordGuitarNotes().toList()..sort();
      if (selected.isNotEmpty) {
        final display = selected.map((n) => n + 12).toList()..sort();
        display[0] -= 12;
        final exactIndex = selected.indexOf(note);
        if (exactIndex != -1 && exactIndex < display.length) {
          return display[exactIndex];
        }
        final pc = _positiveMod12(note);
        final samePc = <int>[];
        for (int i = 0; i < selected.length; i += 1) {
          if (_positiveMod12(selected[i]) == pc && i < display.length) {
            samePc.add(display[i]);
          }
        }
        if (samePc.isNotEmpty) {
          samePc.sort((a, b) => (a - (note + 12)).abs().compareTo((b - (note + 12)).abs()));
          return samePc.first;
        }
      }
    }
    final rh = _extractMidiList(_generatedChordJson!, <String>['notes_midi']);
    final lh = includeBass
        ? rh.map((n) => n - 12).where((n) => n >= 0)
        : const <int>[];
    final candidates = <int>{...rh, ...lh}.toList();
    if (candidates.isEmpty) return null;
    if (candidates.contains(note)) return note;
    final pc = _positiveMod12(note);
    final samePc = candidates.where((n) => _positiveMod12(n) == pc).toList();
    if (samePc.isNotEmpty) {
      samePc.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
      return samePc.first;
    }
    candidates.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
    return candidates.first;
  }

  int? _variationBassPc(Map<String, dynamic> variation) {
    final stringNotes = variation['string_notes'];
    if (stringNotes is List && stringNotes.length >= 6) {
      for (final note in stringNotes) {
        final n = note is num ? note.toInt() : int.tryParse('$note');
        if (n != null) return _positiveMod12(n);
      }
    }
    final fretsRaw = variation['frets'];
    if (fretsRaw is List && fretsRaw.length >= 6) {
      const tuning = <int>[40, 45, 50, 55, 59, 64]; // 6->1
      for (int i = 0; i < fretsRaw.length && i < tuning.length; i += 1) {
        final fret = fretsRaw[i] is num
            ? (fretsRaw[i] as num).toInt()
            : int.tryParse('${fretsRaw[i]}');
        if (fret != null && fret >= 0) {
          return _positiveMod12(tuning[i] + fret);
        }
      }
    }
    final notesRaw = variation['notes'];
    if (notesRaw is List && notesRaw.isNotEmpty) {
      final notes = notesRaw
          .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
          .whereType<int>()
          .toList();
      if (notes.isNotEmpty) {
        notes.sort();
        return _positiveMod12(notes.first);
      }
    }
    return null;
  }

  List<Map<String, dynamic>> _chordGuitarVariations() {
    if ((_tabIndex != 1 && _tabIndex != 2) || _generatedChordJson == null) {
      return const <Map<String, dynamic>>[];
    }
    final rootPc = (_generatedChordJson!['root_pc'] is num)
        ? (_generatedChordJson!['root_pc'] as num).toInt()
        : _chordRootPc;
    final suffix = _generatedChordJson!['suffix'] as String? ?? _chordSuffix;
    final key = '${_positiveMod12(rootPc)}|$suffix';
    var variations = List<Map<String, dynamic>>.from(
      _guitarChordCacheByKey[key] ?? const <Map<String, dynamic>>[],
    );
    final intervals =
        (_chordPatterns.firstWhere(
                      (p) => (p['suffix'] as String? ?? '') == suffix,
                      orElse: () => <String, dynamic>{
                        'intervals': const <int>[],
                      },
                    )['intervals']
                    as List<dynamic>? ??
                const <dynamic>[])
            .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
            .whereType<int>()
            .toList();
    if (intervals.isNotEmpty && variations.isNotEmpty) {
      final inversion = (_generatedChordJson!['inversion'] is num)
          ? (_generatedChordJson!['inversion'] as num).toInt()
          : _chordInversion;
      final inversionIdx = inversion.clamp(0, intervals.length - 1);
      final targetBassPc = _positiveMod12(rootPc + intervals[inversionIdx]);
      final filtered = variations
          .where((v) => _variationBassPc(v) == targetBassPc)
          .toList();
      if (filtered.isNotEmpty) {
        variations = filtered;
      }
    }
    return variations;
  }

  List<int> _variationNotes(Map<String, dynamic> variation) {
    final fromStrings =
        (variation['string_notes'] as List<dynamic>? ?? const <dynamic>[])
            .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
            .whereType<int>()
            .toList();
    if (fromStrings.isNotEmpty) return fromStrings;
    return (variation['notes'] as List<dynamic>? ?? const <dynamic>[])
        .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
        .whereType<int>()
        .toList();
  }

  List<List<int>> _fallbackChordGuitarVoicings() {
    if ((_tabIndex != 1 && _tabIndex != 2) || _generatedChordJson == null) {
      return const <List<int>>[];
    }
    final chordPcs = _extractMidiList(_generatedChordJson!, <String>[
      'notes_midi',
    ]).map((n) => _positiveMod12(n)).toSet();
    if (chordPcs.isEmpty) return const <List<int>>[];
    const tuning = <int>[40, 45, 50, 55, 59, 64];
    final out = <List<int>>[];
    final seen = <String>{};
    for (int windowStart = 0; windowStart <= 9; windowStart += 1) {
      final shape = <int>[];
      var valid = true;
      for (final open in tuning) {
        int? chosenFret;
        var bestDistance = 9999;
        for (int fret = 0; fret <= 12; fret += 1) {
          if (!chordPcs.contains(_positiveMod12(open + fret))) continue;
          if (fret < windowStart || fret > windowStart + 4) continue;
          final dist = (fret - (windowStart + 1)).abs();
          if (dist < bestDistance) {
            bestDistance = dist;
            chosenFret = fret;
          }
        }
        if (chosenFret == null) {
          valid = false;
          break;
        }
        shape.add(open + chosenFret);
      }
      if (!valid) continue;
      final key = shape.join(',');
      if (seen.add(key)) {
        out.add(shape);
      }
    }
    return out;
  }

  Set<int> _instrumentExtrasForCurrentTab() {
    if (_tabIndex == 0 && _detectionResultJson != null) {
      return _extractMidiList(_detectionResultJson!, <String>[
        'extras_midi',
      ]).toSet();
    }
    return <int>{};
  }

  List<int> _scaleBaseNotes() {
    if (_generatedScaleJson == null) return <int>[];
    final base = _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
    if (base.isEmpty) return <int>[];
    if (_tabIndex != 2 ||
        _instrumentView != 'guitar' ||
        _scaleGuitarStartNote == null) {
      return base;
    }
    final start = _scaleGuitarStartNote!;
    final first = base.first;
    if ((start % 12) != (first % 12)) {
      return base;
    }
    final delta = start - first;
    return base.map((n) => n + delta).toList();
  }

  List<int> _scaleRhNotes() {
    final base = _scaleBaseNotes();
    if (base.isEmpty || _scaleOctaves <= 1) return base;
    final result = <int>{...base};
    if (_scaleOctaves >= 2) {
      result.addAll(base.map((n) => n - 12).where((n) => n >= _kPianoLowMidi));
    }
    if (_scaleOctaves >= 3) {
      result.addAll(base.map((n) => n + 12).where((n) => n <= _kPianoHighMidi));
    }
    return result.toList()..sort();
  }

  List<int> _scaleLhNotes(List<int> rh) => rh
      .map((n) => n - 12)
      .where((n) => n >= 0 && (rh.isEmpty || n < rh.first))
      .toList();

  int? _scaleStaffNoteForPitch(int note, {bool includeBass = true}) {
    if (_generatedScaleJson == null) return null;
    final target = note;
    final rh = _scaleBaseNotes();
    final lh = includeBass ? _scaleLhNotes(rh) : <int>[];
    final candidates = includeBass ? <int>[...rh, ...lh] : <int>[...rh];
    if (candidates.contains(target)) return target;
    final pc = ((target % 12) + 12) % 12;
    final samePc = candidates.where((n) => ((n % 12) + 12) % 12 == pc).toList();
    if (samePc.isEmpty) return null;
    samePc.sort((a, b) => (a - target).abs().compareTo((b - target).abs()));
    return samePc.first;
  }

  MapEntry<int, bool>? _scaleStaffSelectionForPiano(int note) {
    if (_generatedScaleJson == null) return null;
    final rh = _scaleBaseNotes();
    final lh = _scaleLhNotes(rh);
    if (rh.contains(note)) return MapEntry<int, bool>(note, false);
    if (lh.contains(note)) return MapEntry<int, bool>(note, true);
    final pc = _positiveMod12(note);
    final rhByPc = rh.where((n) => _positiveMod12(n) == pc).toList();
    final lhByPc = lh.where((n) => _positiveMod12(n) == pc).toList();
    if (rhByPc.isEmpty && lhByPc.isEmpty) return null;
    if (rhByPc.isEmpty) {
      lhByPc.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
      return MapEntry<int, bool>(lhByPc.first, true);
    }
    if (lhByPc.isEmpty) {
      rhByPc.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
      return MapEntry<int, bool>(rhByPc.first, false);
    }
    rhByPc.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
    lhByPc.sort((a, b) => (a - note).abs().compareTo((b - note).abs()));
    final rhBest = rhByPc.first;
    final lhBest = lhByPc.first;
    if ((lhBest - note).abs() < (rhBest - note).abs()) {
      return MapEntry<int, bool>(lhBest, true);
    }
    return MapEntry<int, bool>(rhBest, false);
  }

  int _safeMidi(int midi) => midi.clamp(21, 108);

  double _midiFreq(int midi) => 440.0 * math.pow(2.0, (midi - 69) / 12.0);

  Uint8List _buildWavTone({
    required int midi,
    required double seconds,
    required String instrument,
    int sampleRate = 44100,
  }) {
    final totalSamples = math.max(1, (sampleRate * seconds).round());
    final dataSize = totalSamples * 2;
    final byteData = ByteData(44 + dataSize);
    final freq = _midiFreq(midi);

    void writeStr(int offset, String value) {
      for (int i = 0; i < value.length; i += 1) {
        byteData.setUint8(offset + i, value.codeUnitAt(i));
      }
    }

    writeStr(0, 'RIFF');
    byteData.setUint32(4, 36 + dataSize, Endian.little);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    byteData.setUint32(16, 16, Endian.little); // PCM chunk size
    byteData.setUint16(20, 1, Endian.little); // PCM
    byteData.setUint16(22, 1, Endian.little); // mono
    byteData.setUint32(24, sampleRate, Endian.little);
    byteData.setUint32(28, sampleRate * 2, Endian.little); // byte rate
    byteData.setUint16(32, 2, Endian.little); // block align
    byteData.setUint16(34, 16, Endian.little); // bits per sample
    writeStr(36, 'data');
    byteData.setUint32(40, dataSize, Endian.little);

    final pi2 = 2.0 * math.pi;
    final rng = math.Random((midi * 997) + instrument.hashCode);
    final isGuitar = instrument == 'guitar';
    final attack = isGuitar ? 0.0045 : 0.010;
    final decayBase = isGuitar ? 0.92 : 0.80;
    final maxAmp = isGuitar ? 0.54 : 0.50;
    final release = math.min(seconds * 0.18, isGuitar ? 0.040 : 0.028);
    for (int i = 0; i < totalSamples; i += 1) {
      final t = i / sampleRate;
      final decayFactor = math
          .pow(decayBase, t * (isGuitar ? 8.3 : 5.3))
          .toDouble();
      final fadeOut = release <= 0 || t < seconds - release
          ? 1.0
          : ((seconds - t) / release).clamp(0.0, 1.0);
      final env = (t < attack ? (t / attack) : decayFactor) * fadeOut;
      final fundamental = math.sin(pi2 * freq * t) * (isGuitar ? 0.84 : 0.92);
      final harmonic2 =
          math.sin(pi2 * freq * 2.0 * t) * (isGuitar ? 0.24 : 0.20);
      final harmonic3 =
          math.sin(pi2 * freq * 3.0 * t) * (isGuitar ? 0.15 : 0.12);
      final harmonic4 =
          math.sin(pi2 * freq * 4.0 * t) * (isGuitar ? 0.08 : 0.06);
      final harmonic5 =
          math.sin(pi2 * freq * 5.0 * t) * (isGuitar ? 0.03 : 0.045);
      final noise = (rng.nextDouble() * 2.0) - 1.0;
      final pick = isGuitar ? (noise * math.exp(-t * 48.0) * 0.26) : 0.0;
      final sample =
          (fundamental + harmonic2 + harmonic3 + harmonic4 + harmonic5 + pick) *
          env *
          maxAmp;
      final pcm = (sample * 32767.0).round().clamp(-32767, 32767);
      byteData.setInt16(44 + i * 2, pcm, Endian.little);
    }
    return byteData.buffer.asUint8List();
  }

  Uint8List _buildWavChord({
    required List<int> notes,
    required double seconds,
    required String instrument,
    int sampleRate = 44100,
  }) {
    final chordNotes = notes.map(_safeMidi).toSet().toList()..sort();
    if (chordNotes.isEmpty) {
      return _buildWavTone(
        midi: 60,
        seconds: seconds,
        instrument: instrument,
        sampleRate: sampleRate,
      );
    }
    final rendered = chordNotes
        .map(
          (midi) => _buildWavTone(
            midi: midi,
            seconds: seconds,
            instrument: instrument,
            sampleRate: sampleRate,
          ),
        )
        .toList();
    final totalSamples = math.max(1, (sampleRate * seconds).round());
    final dataSize = totalSamples * 2;
    final out = ByteData(44 + dataSize);

    for (int i = 0; i < 44; i += 1) {
      out.setUint8(i, rendered.first[i]);
    }

    final gain = 1.0 / math.max(1.0, math.sqrt(chordNotes.length.toDouble()));
    for (int i = 0; i < totalSamples; i += 1) {
      var mixed = 0.0;
      for (final wav in rendered) {
        final data = ByteData.sublistView(wav);
        mixed += data.getInt16(44 + (i * 2), Endian.little) * gain;
      }
      final pcm = mixed.round().clamp(-32767, 32767);
      out.setInt16(44 + (i * 2), pcm, Endian.little);
    }
    return out.buffer.asUint8List();
  }

  Future<String> _cachedWavFilePath({
    required String key,
    required Uint8List wavBytes,
  }) async {
    final cachedPath = _toneFileCache[key];
    if (cachedPath != null && await File(cachedPath).exists()) {
      return cachedPath;
    }
    final file = File('${Directory.systemTemp.path}/midichords_$key.wav');
    await file.writeAsBytes(wavBytes, flush: true);
    _toneFileCache[key] = file.path;
    return file.path;
  }

  String _toneCacheKey({
    required int midi,
    required String instrument,
    required double seconds,
  }) => '${_safeMidi(midi)}|$instrument|${(seconds * 1000).round()}';

  String _chordCacheKey({
    required List<int> notes,
    required String instrument,
    required double seconds,
  }) =>
      'chord_${notes.map(_safeMidi).join("_")}|$instrument|${(seconds * 1000).round()}';

  Future<void> _precacheTone({
    required int midi,
    required String instrument,
    required double seconds,
  }) async {
    final key = _toneCacheKey(
      midi: midi,
      instrument: instrument,
      seconds: seconds,
    );
    final wavBytes = _buildWavTone(
      midi: _safeMidi(midi),
      seconds: seconds,
      instrument: instrument,
    );
    await _cachedWavFilePath(key: key, wavBytes: wavBytes);
  }

  Future<void> _precacheChord({
    required List<int> notes,
    required String instrument,
    required double seconds,
  }) async {
    final chordNotes = notes.map(_safeMidi).toSet().toList()..sort();
    if (chordNotes.isEmpty) return;
    final key = _chordCacheKey(
      notes: chordNotes,
      instrument: instrument,
      seconds: seconds,
    );
    final wavBytes = _buildWavChord(
      notes: chordNotes,
      seconds: seconds,
      instrument: instrument,
    );
    await _cachedWavFilePath(key: key, wavBytes: wavBytes);
  }

  Uint8List _buildMetronomeClickWav({
    required int level,
    int sampleRate = 44100,
  }) {
    final freq = switch (level) {
      2 => 1700.0,
      1 => 1300.0,
      _ => 950.0,
    };
    final seconds = 0.045;
    final totalSamples = math.max(1, (sampleRate * seconds).round());
    final dataSize = totalSamples * 2;
    final byteData = ByteData(44 + dataSize);
    final rng = math.Random(1000 + (level * 97));

    void writeStr(int offset, String value) {
      for (int i = 0; i < value.length; i += 1) {
        byteData.setUint8(offset + i, value.codeUnitAt(i));
      }
    }

    writeStr(0, 'RIFF');
    byteData.setUint32(4, 36 + dataSize, Endian.little);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    byteData.setUint32(16, 16, Endian.little);
    byteData.setUint16(20, 1, Endian.little);
    byteData.setUint16(22, 1, Endian.little);
    byteData.setUint32(24, sampleRate, Endian.little);
    byteData.setUint32(28, sampleRate * 2, Endian.little);
    byteData.setUint16(32, 2, Endian.little);
    byteData.setUint16(34, 16, Endian.little);
    writeStr(36, 'data');
    byteData.setUint32(40, dataSize, Endian.little);

    final isAccent = level >= 1;
    final oscAmp = isAccent ? 0.34 : 0.24;
    final noiseAmp = isAccent ? 0.78 : 0.62;

    double triangleAt(double phase) {
      final wrapped = phase - phase.floorToDouble();
      return (4.0 * (wrapped - 0.5).abs()) - 1.0;
    }

    for (int i = 0; i < totalSamples; i += 1) {
      final t = i / sampleRate;
      final env = math.exp(-t * (isAccent ? 82.0 : 74.0));
      final tri = triangleAt(freq * t) * oscAmp;
      final noise = ((rng.nextDouble() * 2.0) - 1.0) * noiseAmp;
      final mixed = (tri + (noise * math.exp(-t * 115.0))) * env * 0.36;
      final pcm = (mixed * 32767.0).round().clamp(-32767, 32767);
      byteData.setInt16(44 + (i * 2), pcm, Endian.little);
    }
    return byteData.buffer.asUint8List();
  }

  Future<AudioPlayer?> _playTone({
    required int midi,
    required String instrument,
    double durationSeconds = 0.6,
    bool lowVolume = false,
    double volumeScale = 1.0,
  }) async {
    final gain = volumeScale.clamp(0.0, 1.0);
    if (gain <= 0.0) {
      return null;
    }
    if (Platform.isAndroid) {
      final targetVolume = ((lowVolume ? 0.68 : 1.0) * gain).clamp(0.0, 1.0);
      final ok = await _playAndroidSynthTone(
        midi: _safeMidi(midi),
        instrument: instrument,
        durationMs: (durationSeconds.clamp(0.1, 2.2) * 1000).round(),
        volume: targetVolume,
      );
      if (!ok && gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }
    if (Platform.isIOS) {
      final baseVolume = ((lowVolume ? 0.68 : 1.0) * gain).clamp(0.0, 1.0);
      // En iOS, el motor nativo puede saturar con algunos presets (especialmente piano).
      // Atenuamos un poco para evitar clipping percibido.
      final instrumentAttenuation = instrument == 'piano' ? 0.72 : 0.82;
      final targetVolume = (baseVolume * instrumentAttenuation).clamp(0.0, 1.0);
      final ok = await _playIosSynthTone(
        midi: _safeMidi(midi),
        instrument: instrument,
        durationMs: (durationSeconds.clamp(0.05, 2.2) * 1000).round(),
        volume: targetVolume,
      );
      if (!ok && gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }
    if (!_audioPlaybackAvailable) {
      if (gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }

    final targetVolume = ((lowVolume ? 0.68 : 1.0) * gain).clamp(0.0, 1.0);
    if (!Platform.isIOS) {
      try {
        final sampled = await _playSampleTone(
          midi: midi,
          instrument: instrument,
          volume: targetVolume,
          durationSeconds: durationSeconds,
        );
        if (sampled != null) {
          return sampled;
        }
      } catch (err) {
        debugPrint('Instrument sample playback unavailable: $err');
      }
    }
    final player = AudioPlayer();
    player.positionUpdater = null;
    try {
      await player.setPlayerMode(
        Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.setReleaseMode(ReleaseMode.release);
      if (Platform.isAndroid) {
        await player.setAudioContext(
          AudioContext(
            android: const AudioContextAndroid(
              contentType: AndroidContentType.sonification,
              usageType: AndroidUsageType.assistanceSonification,
              audioFocus: AndroidAudioFocus.none,
            ),
          ),
        );
      }
      final seconds = durationSeconds.clamp(0.12, 2.2);
      final wavBytes = _buildWavTone(
        midi: _safeMidi(midi),
        seconds: seconds,
        instrument: instrument,
      );
      if (Platform.isIOS) {
        final key = _toneCacheKey(
          midi: midi,
          instrument: instrument,
          seconds: seconds,
        );
        final filePath = await _cachedWavFilePath(key: key, wavBytes: wavBytes);
        await player.play(DeviceFileSource(filePath), volume: targetVolume);
      } else {
        await player.play(
          BytesSource(wavBytes, mimeType: 'audio/wav'),
          volume: targetVolume,
        );
      }
      _bindAutoDisposeOnComplete(player);
      return player;
    } catch (err) {
      _audioPlaybackAvailable = false;
      try {
        await player.dispose();
      } catch (_) {}
      debugPrint('Audio playback unavailable on this device/runtime: $err');
      SystemSound.play(SystemSoundType.click);
      return null;
    }
  }

  Future<AudioPlayer?> _playMetronomeClick({
    bool accent = false,
    bool bar = false,
    double volumeScale = 1.0,
  }) async {
    final gain = volumeScale.clamp(0.0, 1.0);
    if (gain <= 0.0) return null;
    final level = bar ? 2 : (accent ? 1 : 0);
    if (Platform.isAndroid) {
      final ok = await _playAndroidMetronomeClick(
        level: level,
        volume: gain.clamp(0.0, 1.0),
      );
      if (!ok && gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }
    if (Platform.isIOS) {
      try {
        final ok =
            await _kPlatformChannel.invokeMethod<bool>('playIosMetronomeClick', {
              'level': level,
              'volume': gain.clamp(0.0, 1.0),
            }) ??
            false;
        if (ok) {
          return null;
        }
      } catch (_) {}
    }
    if (!_audioPlaybackAvailable) {
      if (gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }
    final baseGain = switch (level) {
      2 => 1.24,
      1 => 0.96,
      _ => 0.68,
    };
    if (!Platform.isIOS && _metronomeSampleAvailable) {
      final samplePlayer = AudioPlayer();
      samplePlayer.positionUpdater = null;
      final baseRate = switch (level) {
        2 => 1.68,
        1 => 1.24,
        _ => 0.94,
      };
      try {
        await samplePlayer.setPlayerMode(
          Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
        );
        await samplePlayer.setReleaseMode(ReleaseMode.release);
        if ((baseRate - 1.0).abs() > 0.001) {
          await samplePlayer.setPlaybackRate(baseRate);
        }
        await samplePlayer.play(
          AssetSource(_kMetronomeSample),
          volume: (baseGain * gain).clamp(0.0, 1.0),
        );
        if (level > 0) {
          unawaited(_playMetronomeAccentTransient(level: level, gain: gain));
        }
        _bindAutoDisposeOnComplete(samplePlayer);
        return samplePlayer;
      } catch (err) {
        _metronomeSampleAvailable = false;
        try {
          await samplePlayer.dispose();
        } catch (_) {}
        debugPrint('Metronome sample playback unavailable: $err');
      }
    }
    final clickWav = _buildMetronomeClickWav(level: level);
    final player = AudioPlayer();
    player.positionUpdater = null;
    try {
      await player.setPlayerMode(
        Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.setReleaseMode(ReleaseMode.release);
      await player.play(
        BytesSource(clickWav, mimeType: 'audio/wav'),
        volume: (baseGain * gain).clamp(0.0, 1.0),
      );
      _bindAutoDisposeOnComplete(player);
      return player;
    } catch (err) {
      try {
        await player.dispose();
      } catch (_) {}
      debugPrint('Metronome synthesized click unavailable: $err');
    }
    if (gain > 0.02) {
      SystemSound.play(SystemSoundType.click);
    }
    return null;
  }

  Future<void> _playMetronomeAccentTransient({
    required int level,
    required double gain,
  }) async {
    if (level <= 0 || gain <= 0.0) return;
    if (Platform.isAndroid) {
      final overlay = level >= 2 ? 0.52 : 0.34;
      unawaited(
        _playAndroidMetronomeClick(
          level: level,
          volume: (overlay * gain).clamp(0.0, 1.0),
        ),
      );
      return;
    }
    final player = AudioPlayer();
    player.positionUpdater = null;
    try {
      await player.setPlayerMode(
        Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.setReleaseMode(ReleaseMode.release);
      await player.play(
        BytesSource(
          _buildMetronomeClickWav(level: level),
          mimeType: 'audio/wav',
        ),
        volume: ((level >= 2 ? 0.48 : 0.32) * gain).clamp(0.0, 1.0),
      );
      _bindAutoDisposeOnComplete(player);
    } catch (_) {
      try {
        await player.dispose();
      } catch (_) {}
    }
  }

  Future<AudioPlayer?> _playSampleTone({
    required int midi,
    required String instrument,
    required double volume,
    double durationSeconds = 0.6,
  }) async {
    if (Platform.isAndroid) {
      return null;
    }
    if (!_samplePlaybackAvailable) {
      return null;
    }
    final bank = instrument == 'guitar'
        ? _kGuitarNylonSamples
        : _kGrandPianoSamples;
    if (bank.isEmpty) {
      return null;
    }
    // Keep metronome click notes and out-of-range tones on synthesis fallback.
    final safe = _safeMidi(midi);
    if (instrument == 'piano' && (safe < 48 || safe > 84)) {
      return null;
    }
    if (instrument == 'guitar' && (safe < 40 || safe > 76)) {
      return null;
    }
    final sampleMidi = bank.keys.reduce(
      (a, b) => (a - safe).abs() <= (b - safe).abs() ? a : b,
    );
    final assetPath = bank[sampleMidi];
    if (assetPath == null) {
      return null;
    }
    final semitones = safe - sampleMidi;
    final targetRate = math.pow(2.0, semitones / 12.0).toDouble();
    final clampedRate = targetRate.clamp(0.5, 2.0);
    final player = AudioPlayer();
    player.positionUpdater = null;
    try {
      final useLowLatency = Platform.isAndroid;
      await player.setPlayerMode(
        useLowLatency ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.setReleaseMode(ReleaseMode.release);
      await player.setSource(AssetSource(assetPath));
      if ((clampedRate - 1.0).abs() > 0.001) {
        try {
          await player.setPlaybackRate(clampedRate);
        } catch (_) {
          // Keep sample playback even if transposition is unsupported.
        }
      }
      await player.setVolume(volume);
      if (Platform.isAndroid) {
        await player.setAudioContext(
          AudioContext(
            android: const AudioContextAndroid(
              contentType: AndroidContentType.music,
              usageType: AndroidUsageType.media,
              audioFocus: AndroidAudioFocus.none,
            ),
          ),
        );
        await player.resume();
        final ttlMs = ((durationSeconds.clamp(0.1, 2.2) * 1000) + 320)
            .round()
            .clamp(220, 3200);
        Timer(Duration(milliseconds: ttlMs), () {
          unawaited(_safeStopDispose(player));
        });
        return player;
      }
      await player.resume();
      if (useLowLatency) {
        final ttlMs = ((durationSeconds.clamp(0.1, 2.2) * 1000) + 320)
            .round()
            .clamp(220, 3200);
        Timer(Duration(milliseconds: ttlMs), () {
          unawaited(_safeStopDispose(player));
        });
      } else {
        _bindAutoDisposeOnComplete(player);
      }
      return player;
    } catch (err) {
      debugPrint('Instrument sample playback unavailable: $err');
      try {
        await player.dispose();
      } catch (_) {}
      return null;
    }
  }

  Future<bool> _playAndroidSynthTone({
    required int midi,
    required String instrument,
    required int durationMs,
    required double volume,
  }) async {
    try {
      return await _kPlatformChannel
              .invokeMethod<bool>('playAndroidSynthTone', <String, dynamic>{
                'midi': midi,
                'instrument': instrument,
                'durationMs': durationMs.clamp(80, 2600),
                'volume': volume.clamp(0.0, 1.0),
              }) ??
          false;
    } catch (err) {
      debugPrint('Android synth tone unavailable: $err');
      return false;
    }
  }

  Future<bool> _playAndroidSynthChord({
    required List<int> notes,
    required String instrument,
    required int durationMs,
    required double volume,
  }) async {
    if (notes.isEmpty) return false;
    try {
      return await _kPlatformChannel
              .invokeMethod<bool>('playAndroidSynthChord', <String, dynamic>{
                'notes': notes.map(_safeMidi).toList(growable: false),
                'instrument': instrument,
                'durationMs': durationMs.clamp(80, 2600),
                'volume': volume.clamp(0.0, 1.0),
              }) ??
          false;
    } catch (err) {
      debugPrint('Android synth chord unavailable: $err');
      return false;
    }
  }

  Future<bool> _playAndroidMetronomeClick({
    required int level,
    required double volume,
  }) async {
    try {
      return await _kPlatformChannel.invokeMethod<bool>(
            'playAndroidMetronomeClick',
            <String, dynamic>{
              'level': level.clamp(0, 2),
              'durationMs': 55,
              'volume': volume.clamp(0.0, 1.0),
            },
          ) ??
          false;
    } catch (err) {
      debugPrint('Android metronome click unavailable: $err');
      return false;
    }
  }

  Future<bool> _playIosSynthTone({
    required int midi,
    required String instrument,
    required int durationMs,
    required double volume,
  }) async {
    try {
      return await _kPlatformChannel
              .invokeMethod<bool>('playIosSynthTone', <String, dynamic>{
                'midi': midi,
                'instrument': instrument,
                'durationMs': durationMs.clamp(40, 2600),
                'volume': volume.clamp(0.0, 1.0),
              }) ??
          false;
    } catch (err) {
      debugPrint('iOS synth tone unavailable: $err');
      return false;
    }
  }

  Future<bool> _playIosSynthChord({
    required List<int> notes,
    required String instrument,
    required int durationMs,
    required double volume,
  }) async {
    if (notes.isEmpty) return false;
    try {
      return await _kPlatformChannel
              .invokeMethod<bool>('playIosSynthChord', <String, dynamic>{
                'notes': notes.map(_safeMidi).toList(growable: false),
                'instrument': instrument,
                'durationMs': durationMs.clamp(40, 2600),
                'volume': volume.clamp(0.0, 1.0),
              }) ??
          false;
    } catch (err) {
      debugPrint('iOS synth chord unavailable: $err');
      return false;
    }
  }

  Future<void> _stopIosSynth() async {
    try {
      await _kPlatformChannel.invokeMethod<bool>('stopIosSynth');
    } catch (err) {
      debugPrint('iOS synth stop unavailable: $err');
    }
  }

  void _bindAutoDisposeOnComplete(AudioPlayer player) {
    late StreamSubscription<void> completeSub;
    completeSub = player.onPlayerComplete.listen((_) {
      completeSub.cancel();
      unawaited(_safeStopDispose(player));
    });
  }

  Future<void> _safeStopDispose(AudioPlayer player) async {
    try {
      await player.dispose();
    } catch (_) {}
  }

  void _showForbiddenOnPiano(int midi) {
    final note = _safeMidi(midi);
    _forbiddenFlashTimers[note]?.cancel();
    _forbiddenFlashNotes.add(note);
    _forbiddenFlashTimers[note] = Timer(const Duration(milliseconds: 420), () {
      _forbiddenFlashNotes.remove(note);
      _forbiddenFlashTimers.remove(note);
      if (mounted) setState(() {});
    });
    if (mounted) setState(() {});
  }

  void _bumpGenerationPianoHighlight(int midi) {
    _generationPianoHighlightTimer?.cancel();
    setState(() => _generationPianoHighlightMidi = midi);
    _generationPianoHighlightTimer = Timer(const Duration(milliseconds: 720), () {
      if (!mounted) {
        return;
      }
      setState(() {
        _generationPianoHighlightMidi = null;
        _generationPianoHighlightTimer = null;
        if (_tabIndex == 1 || _tabIndex == 2) {
          _generationInputStaffNotes.clear();
        }
      });
    });
  }

  void _clearGenerationPianoHighlight() {
    _generationPianoHighlightTimer?.cancel();
    _generationPianoHighlightTimer = null;
    _generationPianoHighlightMidi = null;
  }

  Future<void> _handleInstrumentNote(int midi, {required bool pressed}) async {
    if (_tabIndex == 5) {
      if (!pressed) return;
      _addIntervalNote(midi);
      if (_midiInputSoundEnabled) {
        unawaited(playNote(midi, instrument: 'piano'));
      }
      return;
    }
    if (_tabIndex == 0) {
      if (!pressed) {
        return;
      }
      if (_detectionMidiHeldNotes.isNotEmpty) {
        _detectionMidiHeldNotes.clear();
        _stopHeldMidiInputs();
      }
      setState(() {
        if (_detectionSelectedNotes.contains(midi)) {
          _detectionSelectedNotes.remove(midi);
        } else {
          _detectionSelectedNotes.add(midi);
        }
      });
      if (!_requestInFlight) {
        unawaited(_callDetect());
      }
      if (_midiInputSoundEnabled) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        );
      }
      return;
    }
    if ((_tabIndex == 1 || _tabIndex == 2) && _generatedChordJson != null) {
      final chordNotes = _extractMidiList(_generatedChordJson!, <String>[
        'notes_midi',
      ]);
      final allowed = _instrumentView == 'guitar'
          ? chordNotes.map((n) => n % 12).toSet().contains(midi % 12)
          : <int>{
              ...chordNotes,
              ...chordNotes.map((n) => n - 12),
            }.contains(midi);
      if (!allowed) {
        _showForbiddenOnPiano(midi);
        _stopHeldChord();
        return;
      }
      final staffNote = _generationStaffNoteForPitch(
        midi,
        includeBass: _instrumentView != 'guitar',
      );
      if (staffNote != null) {
        _generationInputStaffNotes
          ..clear()
          ..add(staffNote);
      }
      if (_instrumentView == 'piano') {
        _bumpGenerationPianoHighlight(midi);
      } else if (staffNote != null) {
        setState(() {});
      }
      if (pressed) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        );
      } else if (_soundOutput == 'midi') {
        _sendMidiNoteOn(midi, 80);
        unawaited(
          Future<void>.delayed(
            Duration(
              milliseconds:
                  ((_instrumentView == 'guitar' ? 1.02 : 0.92) * 1000).round(),
            ),
          ).then((_) => _sendMidiNoteOff(midi)),
        );
      } else {
        await _playTone(
          midi: midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
          durationSeconds: _instrumentView == 'guitar' ? 1.02 : 0.92,
          lowVolume: true,
        );
      }
      return;
    }
    if (_tabIndex == 3 && _generatedScaleJson != null) {
      final scaleNotes = _scaleRhNotes();
      if (pressed &&
          _instrumentView == 'guitar' &&
          _isShiftPressed() &&
          scaleNotes.isNotEmpty) {
        final tonicPc = scaleNotes.first % 12;
        if ((midi % 12) == tonicPc) {
          setState(() {
            _scaleGuitarStartNote = midi;
            _scaleCurrentNote = null;
            _scaleCurrentIsLeft = null;
            _scaleInputRawNote = null;
          });
          if (_scaleLoopRunning) {
            _stopScaleLoop();
          }
          return;
        }
      }
      final allowed = scaleNotes.map((n) => n % 12).toSet().contains(midi % 12);
      if (!allowed) {
        _showForbiddenOnPiano(midi);
        return;
      }
      if (_instrumentView == 'piano') {
        final picked = _scaleStaffSelectionForPiano(midi);
        if (picked != null) {
          _scaleCurrentNote = picked.key;
          _scaleCurrentIsLeft = picked.value;
        } else {
          _scaleCurrentNote =
              _scaleStaffNoteForPitch(midi, includeBass: true) ?? midi;
          _scaleCurrentIsLeft = null;
        }
      } else {
        _scaleCurrentNote =
            _scaleStaffNoteForPitch(midi, includeBass: true) ?? midi;
        _scaleCurrentIsLeft = null;
      }
      _scaleInputRawNote = _instrumentView == 'piano' ? midi : null;
      setState(() {});
      if (pressed) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        );
      } else if (_soundOutput == 'midi') {
        _sendMidiNoteOn(midi, 80);
        unawaited(
          Future<void>.delayed(
            Duration(
              milliseconds:
                  ((_instrumentView == 'guitar' ? 0.95 : 0.85) * 1000).round(),
            ),
          ).then((_) => _sendMidiNoteOff(midi)),
        );
      } else {
        await _playTone(
          midi: midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
          durationSeconds: _instrumentView == 'guitar' ? 0.95 : 0.85,
          lowVolume: true,
        );
      }
    }
  }

  Future<void> _beginInputDrag(int midi, int pointer, Offset globalPos) async {
    _inputDragActive = true;
    _dragPointer = pointer;
    _dragCurrentNote = midi;
    _dragLastGlobalPos = globalPos;
    _dragLastSwitchAt = DateTime.now();
    await _handleInstrumentNote(midi, pressed: true);
  }

  Future<void> _updateInputDrag(int midi, int pointer, Offset globalPos) async {
    if (!_inputDragActive || _dragPointer != pointer) return;
    if (_tabIndex == 0) {
      return;
    }
    if (_dragCurrentNote == midi) return;
    final now = DateTime.now();
    final msSinceLast = now.difference(_dragLastSwitchAt).inMilliseconds;
    final lastPos = _dragLastGlobalPos;
    if (lastPos != null) {
      final dx = globalPos.dx - lastPos.dx;
      final dy = globalPos.dy - lastPos.dy;
      final distance = math.sqrt((dx * dx) + (dy * dy));
      // Avoid accidental note hops caused by tiny finger jitter.
      if (distance < 8.0 || msSinceLast < 28) {
        return;
      }
    }
    if (_dragCurrentNote != null) {
      _releaseHeldInputNote(_dragCurrentNote!);
      if (_tabIndex == 1 || _tabIndex == 2) {
        _generationInputStaffNotes.clear();
        _clearGenerationPianoHighlight();
      }
    }
    _dragCurrentNote = midi;
    _dragLastGlobalPos = globalPos;
    _dragLastSwitchAt = now;
    await _handleInstrumentNote(midi, pressed: true);
  }

  void _endInputDrag(int pointer) {
    if (!_inputDragActive || _dragPointer != pointer) return;
    _inputDragActive = false;
    _dragPointer = null;
    _dragCurrentNote = null;
    _dragLastGlobalPos = null;
    _stopHeldInputs();
    if (_tabIndex == 1 || _tabIndex == 2) {
      _generationInputStaffNotes.clear();
      _clearGenerationPianoHighlight();
    }
    if (_tabIndex == 3 && _scaleInputRawNote != null) {
      setState(() => _scaleInputRawNote = null);
    }
    if (mounted) {
      setState(() {});
    }
  }

  void _syncPianoScrollToMiddleC(
    double viewportW,
    double whiteW,
    List<int> whiteMidi,
  ) {
    if (!_needsPianoScrollSync) return;
    _needsPianoScrollSync = false;

    void attempt(int retriesLeft) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted || !_pianoScrollController.hasClients) return;
        final maxExt = _pianoScrollController.position.maxScrollExtent;
        if (maxExt <= 0) {
          // El layout puede tardar un frame extra en asentarse tras un
          // cambio de altura (p. ej. al activar/desactivar la digitación,
          // que añade/quita las tiras encima del piano). Reintentar evita
          // que el scroll se quede en 0 y desalinee las tiras del teclado.
          if (retriesLeft > 0) attempt(retriesLeft - 1);
          return;
        }
        final int anchorMidi;
        if (_tabIndex == 3 && _generatedScaleJson != null) {
          final rh = _scaleRhNotes();
          if (rh.isNotEmpty) {
            anchorMidi = (rh.first + rh.last) ~/ 2;
          } else {
            anchorMidi = _kPianoMiddleCMidi;
          }
        } else {
          anchorMidi = _kPianoMiddleCMidi;
        }
        final cIdx = whiteMidi.indexOf(anchorMidi);
        final wIdx = cIdx >= 0 ? cIdx : math.max(0, whiteMidi.indexWhere((m) => m >= anchorMidi));
        final keyCenterX = wIdx * whiteW + whiteW / 2;
        final target = (keyCenterX - viewportW / 2).clamp(0.0, maxExt);
        _pianoScrollController.jumpTo(target);
      });
    }

    attempt(5);
  }

  void _stopHeldChord() {
    _heldChordPlaybackEndTimer?.cancel();
    _heldChordPlaybackEndTimer = null;
    _heldChordPlayToken++;
    for (final midi in _heldChordNativeNotes) {
      _sendMidiNoteOff(midi);
    }
    // En iOS, el sintetizador nativo no expone note-off por nota.
    // Para evitar cortes bruscos al soltar, dejamos que la nota termine por duración.
    final uniquePlayers = _heldChordPlayers.values.toSet();
    for (final player in uniquePlayers) {
      unawaited(_safeStopDispose(player));
    }
    _heldChordPlayers.clear();
    _heldChordNativeNotes.clear();
    _detectionPlayHeldNotes.clear();
  }

  void _stopHeldInputs() {
    for (final midi in _midiOutHeldNotes) {
      _sendMidiNoteOff(midi);
    }
    _midiOutHeldNotes.clear();
    // En iOS, no parar el synth evita cortar el "release" de la nota.
    for (final entry in _heldInputPlayers.entries) {
      unawaited(_safeStopDispose(entry.value));
    }
    _heldInputPlayers.clear();
  }

  void _stopHeldMidiInputs() {
    // En iOS, no parar el synth evita cortar el "release" de la nota.
    for (final entry in _heldMidiInputPlayers.entries) {
      unawaited(_safeStopDispose(entry.value));
    }
    _heldMidiInputPlayers.clear();
  }

  void _scheduleHeldChordPlaybackAutoClear({required String instrument}) {
    _heldChordPlaybackEndTimer?.cancel();
    final ms =
        ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round() + 280;
    _heldChordPlaybackEndTimer = Timer(Duration(milliseconds: ms), () {
      _heldChordPlaybackEndTimer = null;
      if (!mounted) {
        return;
      }
      _stopHeldChord();
      setState(() {});
    });
  }

  Future<void> _startHeldChord(
    List<int> notes, {
    required String instrument,
  }) async {
    _stopHeldChord();
    final chordNotes = notes.map(_safeMidi).toSet().toList()..sort();
    _heldChordNativeNotes
      ..clear()
      ..addAll(chordNotes);
    _scheduleHeldChordPlaybackAutoClear(instrument: instrument);
    final playToken = _heldChordPlayToken;
    if (mounted) {
      setState(() {});
    }
    if (_soundOutput == 'midi') {
      for (final midi in chordNotes) {
        _sendMidiNoteOn(midi, 80);
      }
      return;
    }
    if (Platform.isAndroid && chordNotes.length > 1) {
      await _playAndroidSynthChord(
        notes: chordNotes,
        instrument: instrument,
        durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round(),
        volume: 0.92,
      );
      if (mounted) {
        _stopHeldChord();
        setState(() {});
      }
      return;
    }
    if (Platform.isIOS) {
      final volume = (0.92 * (instrument == 'piano' ? 0.72 : 0.82)).clamp(0.0, 1.0);
      if (chordNotes.length > 1) {
        await _playIosSynthChord(
          notes: chordNotes,
          instrument: instrument,
          durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000)
              .round(),
          volume: volume,
        );
      } else {
        await _playIosSynthTone(
          midi: chordNotes.first,
          instrument: instrument,
          durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000)
              .round(),
          volume: volume,
        );
      }
      if (mounted) {
        _stopHeldChord();
        setState(() {});
      }
      return;
    }
    final starts = notes.map((midi) async {
      final player = await _playTone(
        midi: midi,
        instrument: instrument,
        durationSeconds: instrument == 'guitar' ? 1.45 : 1.35,
      );
      return MapEntry<int, AudioPlayer?>(midi, player);
    }).toList();
    final started = await Future.wait(starts);
    if (!mounted || playToken != _heldChordPlayToken) {
      for (final entry in started) {
        final player = entry.value;
        if (player != null) {
          unawaited(_safeStopDispose(player));
        }
      }
      return;
    }
    for (final entry in started) {
      final player = entry.value;
      if (player != null) {
        _heldChordPlayers[entry.key] = player;
      }
    }
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _startHeldInputNote(
    int midi, {
    required String instrument,
  }) async {
    _releaseHeldInputNote(midi);
    if (_soundOutput == 'midi') {
      _sendMidiNoteOn(midi, 80);
      _midiOutHeldNotes.add(midi);
      return;
    }
    final durationSeconds = Platform.isIOS
        ? (instrument == 'guitar' ? 1.6 : 2.2)
        : (instrument == 'guitar' ? 1.05 : 0.95);
    final player = await _playTone(
      midi: midi,
      instrument: instrument,
      durationSeconds: durationSeconds,
    );
    if (player != null) {
      _heldInputPlayers[midi] = player;
    }
  }

  Future<void> _startHeldMidiInputNote(
    int midi, {
    required String instrument,
  }) async {
    _releaseHeldMidiInputNote(midi);
    final durationSeconds = Platform.isIOS
        ? (instrument == 'guitar' ? 1.6 : 2.2)
        : (instrument == 'guitar' ? 1.05 : 0.95);
    final player = await _playTone(
      midi: midi,
      instrument: instrument,
      durationSeconds: durationSeconds,
    );
    if (player != null) {
      _heldMidiInputPlayers[midi] = player;
    }
  }

  void _releaseHeldInputNote(int midi) {
    if (_midiOutHeldNotes.remove(midi)) {
      _sendMidiNoteOff(midi);
    }
    final player = _heldInputPlayers.remove(midi);
    if (player != null) {
      unawaited(_safeStopDispose(player));
    }
  }

  void _releaseHeldMidiInputNote(int midi) {
    final player = _heldMidiInputPlayers.remove(midi);
    if (player != null) {
      unawaited(_safeStopDispose(player));
    }
  }

  Future<void> _callDetect() async {
    if (_requestInFlight) {
      return;
    }
    setState(() => _requestInFlight = true);
    try {
      final notes = _activeDetectionNotes.toList()..sort();
      final json = _detectChordLocal(
        notes: notes,
        language: _language,
        preferFlat: _preferFlat,
      );
      _detectionResultJson = json;
      final detectedMidi = _extractMidiList(json, <String>['notes_midi']);
      _detectionOutputController.text =
          '${_ui('Acorde', 'Chord')}: ${json['name']}\n'
          '${_ui('Notas', 'Notes')}: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Sobrantes', 'Extras')}: ${(json['extras'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Intervalos', 'Intervals')}: ${_intervalTextFromMidiList(detectedMidi)}';
    } catch (err) {
      _detectionResultJson = null;
      _detectionOutputController.text = '${_ui('Error', 'Error')}: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  String _detectionResultValue(String key) {
    final json = _detectionResultJson;
    final fallback = _detectionOutputController.text.trim();
    if (json == null) {
      if (key == 'name' && fallback.isNotEmpty && fallback != 'No results') {
        return fallback;
      }
      return '-';
    }
    switch (key) {
      case 'name':
        return (json['name'] as String?)?.trim().isNotEmpty == true
            ? json['name'] as String
            : '-';
      case 'notes':
        final notes = (json['notes'] as List<dynamic>? ?? const <dynamic>[])
            .map((e) => e.toString())
            .where((e) => e.isNotEmpty)
            .toList(growable: false);
        return notes.isEmpty ? '-' : notes.join(' - ');
      case 'extras':
        final extras = (json['extras'] as List<dynamic>? ?? const <dynamic>[])
            .map((e) => e.toString())
            .where((e) => e.isNotEmpty)
            .toList(growable: false);
        return extras.isEmpty ? '-' : extras.join(' - ');
      case 'intervals':
        final detectedMidi = _extractMidiList(json, <String>['notes_midi']);
        final text = _intervalTextFromMidiList(detectedMidi).trim();
        return text.isEmpty ? '-' : text;
      case 'description':
        final desc = json['description'] as String?;
        return desc?.isNotEmpty == true ? desc! : '';
      default:
        return '-';
    }
  }

  Widget _detectionResultRow({
    required String helpId,
    required String labelEs,
    required String labelEn,
    required String value,
  }) {
    return _helpAnchor(
      helpId,
      Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: RichText(
          text: TextSpan(
            children: <InlineSpan>[
              TextSpan(
                text: '${_ui(labelEs, labelEn)}: ',
                style: const TextStyle(
                  color: _muted,
                  fontWeight: FontWeight.w800,
                  fontSize: 16,
                  height: 1.35,
                ),
              ),
              TextSpan(
                text: value,
                style: const TextStyle(
                  color: _text,
                  fontSize: 16,
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _chordResultValue(String key) {
    final json = _generatedChordJson;
    final fallback = _chordOutputController.text.trim();
    if (json == null) {
      if (key == 'name' && fallback.isNotEmpty && fallback != 'No results') {
        return fallback;
      }
      return '-';
    }
    switch (key) {
      case 'name':
        return (json['name'] as String?)?.trim().isNotEmpty == true
            ? json['name'] as String
            : '-';
      case 'notes':
        final notes = (json['notes'] as List<dynamic>? ?? const <dynamic>[])
            .map((e) => e.toString())
            .where((e) => e.isNotEmpty)
            .toList(growable: false);
        return notes.isEmpty ? '-' : notes.join(' - ');
      case 'intervals':
        final generatedMidi = _extractMidiList(json, <String>['notes_midi']);
        final text = _intervalTextFromMidiList(generatedMidi).trim();
        return text.isEmpty ? '-' : text;
      default:
        return '-';
    }
  }

  Widget _buildChordResultBlock() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF17273A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF73829A)),
      ),
      child: SingleChildScrollView(
        physics: const ClampingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            _detectionResultRow(
              helpId: 'generation_result_chord',
              labelEs: 'Acorde',
              labelEn: 'Chord',
              value: _chordResultValue('name'),
            ),
            _detectionResultRow(
              helpId: 'generation_result_notes',
              labelEs: 'Notas',
              labelEn: 'Notes',
              value: _chordResultValue('notes'),
            ),
            _detectionResultRow(
              helpId: 'generation_result_intervals',
              labelEs: 'Intervalos',
              labelEn: 'Intervals',
              value: _chordResultValue('intervals'),
            ),
          ],
        ),
      ),
    );
  }

  String _scaleResultValue(String key) {
    final json = _generatedScaleJson;
    final fallback = _scaleOutputController.text.trim();
    if (json == null) {
      if (key == 'name' && fallback.isNotEmpty && fallback != 'No results') {
        return fallback;
      }
      return '-';
    }
    switch (key) {
      case 'name':
        final name = (json['pattern_localized_name'] ?? json['pattern_name'])
            ?.toString()
            .trim();
        return (name?.isNotEmpty ?? false) ? name! : '-';
      case 'notes':
        final notes = (json['notes'] as List<dynamic>? ?? const <dynamic>[])
            .map((e) => e.toString())
            .where((e) => e.isNotEmpty)
            .toList(growable: false);
        return notes.isEmpty ? '-' : notes.join(' - ');
      case 'intervals':
        final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
        final text = _intervalTextFromMidiList(scaleMidi).trim();
        return text.isEmpty ? '-' : text;
      default:
        return '-';
    }
  }

  Widget _buildScaleResultBlock() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF17273A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF73829A)),
      ),
      child: SingleChildScrollView(
        physics: const ClampingScrollPhysics(),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            _detectionResultRow(
              helpId: 'scales_result_scale',
              labelEs: 'Escala',
              labelEn: 'Scale',
              value: _scaleResultValue('name'),
            ),
            _detectionResultRow(
              helpId: 'scales_result_notes',
              labelEs: 'Notas',
              labelEn: 'Notes',
              value: _scaleResultValue('notes'),
            ),
            _detectionResultRow(
              helpId: 'scales_result_intervals',
              labelEs: 'Intervalos',
              labelEn: 'Intervals',
              value: _scaleResultValue('intervals'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetectionResultBlock() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF17273A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF73829A)),
      ),
      child: SingleChildScrollView(
        physics: const ClampingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            _helpAnchor(
              'detection_result_chord',
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: RichText(
                  text: TextSpan(
                    children: <InlineSpan>[
                      TextSpan(
                        text: '${_ui('Acorde', 'Chord')}: ',
                        style: const TextStyle(
                          color: _muted,
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                          height: 1.35,
                        ),
                      ),
                      TextSpan(
                        text: _detectionResultValue('name'),
                        style: const TextStyle(
                          color: _text,
                          fontSize: 16,
                          height: 1.35,
                        ),
                      ),
                      if (_detectionResultValue('description').isNotEmpty)
                        TextSpan(
                          text: '  (${_detectionResultValue('description')})',
                          style: const TextStyle(
                            color: _muted,
                            fontSize: 13,
                            height: 1.35,
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
            _detectionResultRow(
              helpId: 'detection_result_notes',
              labelEs: 'Notas',
              labelEn: 'Notes',
              value: _detectionResultValue('notes'),
            ),
            _detectionResultRow(
              helpId: 'detection_result_extras',
              labelEs: 'Sobrantes',
              labelEn: 'Extras',
              value: _detectionResultValue('extras'),
            ),
            _detectionResultRow(
              helpId: 'detection_result_intervals',
              labelEs: 'Intervalos',
              labelEn: 'Intervals',
              value: _detectionResultValue('intervals'),
            ),
          ],
        ),
      ),
    );
  }

  /// Al cambiar tónica/variante o selección en el círculo: reproduce el acorde como el botón ▶.
  Future<void> _playChordPreviewFromSelection() async {
    if (_generatedChordJson == null) {
      return;
    }
    final List<int> notes;
    if (_instrumentView == 'guitar') {
      final g = _selectedChordGuitarNotes();
      notes = g.toList()..sort();
    } else {
      notes = List<int>.from(
        _extractMidiList(_generatedChordJson!, <String>['notes_midi']),
      );
    }
    if (notes.isEmpty) {
      return;
    }
    await _startHeldChord(
      notes,
      instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
    );
  }

  Future<void> _callGenerateChord() async {
    if (_requestInFlight) {
      return;
    }
    setState(() => _requestInFlight = true);
    try {
      final json = _generateChordLocal(
        rootPc: _chordRootPc,
        suffix: _chordSuffix,
        inversion: _chordInversion,
        language: _language,
        preferFlat: _preferFlat,
      );
      _generatedChordJson = json;
      _chordGuitarVariant = 0;
      _generationInputStaffNotes.clear();
      _clearGenerationPianoHighlight();
      final generatedMidi = _extractMidiList(json, <String>['notes_midi']);
      _chordOutputController.text =
          '${_ui('Acorde', 'Chord')}: ${json['name']}\n'
          '${_ui('Notas', 'Notes')}: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Intervalos', 'Intervals')}: ${_intervalTextFromMidiList(generatedMidi)}';
      if (Platform.isIOS && generatedMidi.isNotEmpty) {
        unawaited(
          _precacheChord(
            notes: generatedMidi,
            instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
            seconds: _instrumentView == 'guitar' ? 1.45 : 1.35,
          ),
        );
      }
      unawaited(_playChordPreviewFromSelection());
    } catch (err) {
      _generatedChordJson = null;
      _chordOutputController.text = '${_ui('Error', 'Error')}: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  int _circleMajorTonicPcForTheory() =>
      circleMajorTonicPcForTheory(_circleTonicPc, _circleKeyMode);

  /// [playPreview] solo true cuando el usuario elige tónica/acorde en el círculo (no al cambiar de modo).
  Future<void> _callCircleGenerateChord({bool playPreview = false}) async {
    if (_requestInFlight) {
      return;
    }
    setState(() => _requestInFlight = true);
    try {
      final tonicTheory = _circleMajorTonicPcForTheory();
      final rootPc = _positiveMod12(_circleChordRootPc);
      String suffix;
      if (_circleKeyMode == 'minor') {
        final mt = _positiveMod12(_circleTonicPc);
        suffix = diatonicTriadSuffixNaturalMinorKey(mt, rootPc).suffix;
      } else {
        suffix = diatonicTriadSuffixMajorKey(tonicTheory, rootPc).suffix;
      }
      setState(() {
        _chordRootPc = rootPc;
        _chordSuffix = suffix;
        _chordInversion = 0;
        _recomputeMaxInversion();
      });
      final json = _generateChordLocal(
        rootPc: rootPc,
        suffix: suffix,
        inversion: 0,
        language: _language,
        preferFlat: _preferFlat,
      );
      _generatedChordJson = json;
      _chordGuitarVariant = 0;
      _generationInputStaffNotes.clear();
      _clearGenerationPianoHighlight();
      final generatedMidi = _extractMidiList(json, <String>['notes_midi']);
      _chordOutputController.text =
          '${_ui('Acorde', 'Chord')}: ${json['name']}\n'
          '${_ui('Notas', 'Notes')}: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Intervalos', 'Intervals')}: ${_intervalTextFromMidiList(generatedMidi)}';
      if (Platform.isIOS && generatedMidi.isNotEmpty) {
        unawaited(
          _precacheChord(
            notes: generatedMidi,
            instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
            seconds: _instrumentView == 'guitar' ? 1.45 : 1.35,
          ),
        );
      }
      if (playPreview) {
        unawaited(_playChordPreviewFromSelection());
      }
    } catch (err) {
      _generatedChordJson = null;
      _chordOutputController.text = '${_ui('Error', 'Error')}: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  void _onCircleCanvasInteraction(Offset local, Size size, {required bool longPress}) {
    // Invertido respecto al gesto "shiftClick" original: mantener pulsado
    // cambia de tonalidad; una pulsación simple cambia de acorde dentro de
    // la tonalidad actual (más natural en móvil, donde no hay tecla Shift).
    final pc = CircleFifthsHit.chordRootPcFromClick(
      local,
      size,
      shiftClick: !longPress,
    );
    if (pc == null) return;
    final theory = _circleMajorTonicPcForTheory();
    if (!longPress) {
      if (!CircleFifthsHit.chordShiftClickIsDiatonic(
        theory,
        local,
        size,
        _circleKeyMode,
        _circleTonicPc,
      )) {
        return;
      }
      setState(() => _circleChordRootPc = pc);
    } else {
      final inner = CircleFifthsHit.clickInnerMinorBand(local, size);
      if (inner == null) return;
      setState(() {
        _circleKeyMode = inner ? 'minor' : 'major';
        _circleTonicPc = pc;
        _circleChordRootPc = pc;
      });
    }
    unawaited(_callCircleGenerateChord(playPreview: true));
  }

  Future<void> _callGenerateScale() async {
    if (_requestInFlight) {
      return;
    }
    setState(() => _requestInFlight = true);
    try {
      final json = _generateScaleLocal(
        tonicPc: _scaleTonicPc,
        patternName: _scalePatternName,
        language: _language,
        preferFlat: _preferFlat,
      );
      _generatedScaleJson = json;
      _needsPianoScrollSync = true;
      _updateScaleFingeringsMap();
      final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
      _scaleGuitarStartNote = scaleMidi.isNotEmpty ? scaleMidi.first : null;
      _scaleInputRawNote = null;
      _scaleCurrentNote = null;
      _scaleCurrentIsLeft = null;
      _scaleOutputController.text =
          '${_ui('Escala', 'Scale')}: ${json['pattern_localized_name'] ?? json['pattern_name']}\n'
          '${_ui('Notas', 'Notes')}: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Intervalos', 'Intervals')}: ${_intervalTextFromMidiList(scaleMidi)}';
      if (Platform.isIOS && scaleMidi.isNotEmpty) {
        final instrument = _instrumentView == 'guitar' ? 'guitar' : 'piano';
        final seconds = _instrumentView == 'guitar' ? 0.92 : 0.78;
        for (final midi in scaleMidi) {
          unawaited(
            _precacheTone(
              midi: midi,
              instrument: instrument,
              seconds: seconds,
            ),
          );
        }
      }
    } catch (err) {
      _generatedScaleJson = null;
      _scaleOutputController.text = '${_ui('Error', 'Error')}: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  int _scaleStepMs() {
    final bpm = _scaleBpm.clamp(1, 300);
    return math.max(60, (60000 / bpm).floor());
  }

  double _metronomeVolumeGain() => (_metroVolume.clamp(0, 100)) / 100.0;

  void _stopScaleLoop() {
    _scaleLoopTimer?.cancel();
    _scaleLoopTimer = null;
    _scaleLoopRunning = false;
    _scaleCurrentNote = null;
    _scaleCurrentIsLeft = null;
    _scaleInputRawNote = null;
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _stepScaleLoop() async {
    if (!_scaleLoopRunning) {
      return;
    }
    final notes = _scaleRhNotes();
    if (notes.isEmpty) {
      _stopScaleLoop();
      return;
    }
    final idx = _scaleLoopIndex.clamp(0, notes.length - 1);
    final note = notes[idx];
    _scaleCurrentNote = note;
    _scaleCurrentIsLeft = null;  // null lets both clefs match by note value
    _scaleInputRawNote = null;
    if (_scaleMetronomeOnly) {
      final accent = idx == 0 && _scaleLoopDirection > 0;
      unawaited(
        _playMetronomeClick(
          accent: accent,
          volumeScale: _metronomeVolumeGain(),
        ),
      );
      HapticFeedback.selectionClick();
    } else if (_soundOutput == 'midi') {
      _sendMidiNoteOn(note, 80);
      unawaited(
        Future<void>.delayed(
          Duration(
            milliseconds:
                ((_instrumentView == 'guitar' ? 0.92 : 0.78) * 1000).round(),
          ),
        ).then((_) => _sendMidiNoteOff(note)),
      );
    } else {
      await _playTone(
        midi: note,
        instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        durationSeconds: _instrumentView == 'guitar' ? 0.92 : 0.78,
        lowVolume: true,
      );
    }
    if (mounted) {
      setState(() {});
    }
    if (notes.length > 1) {
      if (_scaleLoopDirection > 0) {
        if (idx >= notes.length - 1) {
          _scaleLoopDirection = -1;
        } else {
          _scaleLoopIndex = idx + 1;
        }
      } else {
        if (idx <= 0) {
          _scaleLoopDirection = 1;
        } else {
          _scaleLoopIndex = idx - 1;
        }
      }
    }
    _scaleLoopTimer = Timer(
      Duration(milliseconds: _scaleStepMs()),
      _stepScaleLoop,
    );
  }

  void _toggleScaleLoop() {
    if (_scaleLoopRunning) {
      _stopScaleLoop();
      return;
    }
    final notes = _scaleRhNotes();
    if (notes.isEmpty) return;
    _scaleLoopRunning = true;
    _scaleLoopIndex = 0;
    _scaleLoopDirection = 1;
    _scaleInputRawNote = null;
    _stepScaleLoop();
  }

  Map<int, String> _scalePcNameMap() {
    if (_generatedScaleJson == null) return const <int, String>{};
    final rawNotes =
        (_generatedScaleJson!['notes'] as List<dynamic>? ?? <dynamic>[])
            .map((n) => n.toString())
            .toList();
    final midi = _scaleBaseNotes();
    if (rawNotes.isEmpty || midi.isEmpty) return const <int, String>{};
    final count = math.min(rawNotes.length, midi.length);
    final out = <int, String>{};
    for (int i = 0; i < count; i += 1) {
      final label = rawNotes[i]
          .replaceAll(RegExp(r'-?\d+'), '')
          .replaceAll(' ', '')
          .trim();
      if (label.isEmpty) continue;
      out[midi[i] % 12] = label;
    }
    return out;
  }

  String _pcLabel(int pc) {
    if (_tabIndex == 3) {
      final byScale = _scalePcNameMap();
      final scaleLabel = byScale[pc % 12];
      if (scaleLabel != null && scaleLabel.isNotEmpty) {
        return scaleLabel;
      }
    }
    const labelsSharpEs = <String>[
      'Do',
      'Do#',
      'Re',
      'Re#',
      'Mi',
      'Fa',
      'Fa#',
      'Sol',
      'Sol#',
      'La',
      'La#',
      'Si',
    ];
    const labelsFlatEs = <String>[
      'Do',
      'Re♭',
      'Re',
      'Mi♭',
      'Mi',
      'Fa',
      'Sol♭',
      'Sol',
      'La♭',
      'La',
      'Si♭',
      'Si',
    ];
    const labelsSharpEn = <String>[
      'C',
      'C#',
      'D',
      'D#',
      'E',
      'F',
      'F#',
      'G',
      'G#',
      'A',
      'A#',
      'B',
    ];
    const labelsFlatEn = <String>[
      'C',
      'D♭',
      'D',
      'E♭',
      'E',
      'F',
      'G♭',
      'G',
      'A♭',
      'A',
      'B♭',
      'B',
    ];
    final useFlat = _accidental == 'flat';
    if (_language == 'en') {
      return useFlat ? labelsFlatEn[pc % 12] : labelsSharpEn[pc % 12];
    }
    return useFlat ? labelsFlatEs[pc % 12] : labelsSharpEs[pc % 12];
  }

  /// Muchos tipos renderizan ♭ más pequeño que `#`; se escala la alteración para
  /// equiparar el aspecto en teclas y etiquetas.
  List<InlineSpan> _splitPitchClassLabelSpans(String label, TextStyle baseStyle) {
    final fz = baseStyle.fontSize ?? 14;
    final accFlatStyle = baseStyle.copyWith(
      fontSize: fz * 1.22,
      height: 1.0,
    );
    final accSharpStyle = baseStyle.copyWith(
      fontSize: fz * 1.06,
      height: 1.0,
    );
    if (label.endsWith('♭♭')) {
      return <InlineSpan>[
        TextSpan(text: label.substring(0, label.length - 2), style: baseStyle),
        TextSpan(text: '♭♭', style: accFlatStyle),
      ];
    }
    if (label.endsWith('♭')) {
      return <InlineSpan>[
        TextSpan(text: label.substring(0, label.length - 1), style: baseStyle),
        TextSpan(text: '♭', style: accFlatStyle),
      ];
    }
    if (label.endsWith('#')) {
      return <InlineSpan>[
        TextSpan(text: label.substring(0, label.length - 1), style: baseStyle),
        TextSpan(text: '#', style: accSharpStyle),
      ];
    }
    return <InlineSpan>[TextSpan(text: label, style: baseStyle)];
  }

  String _inversionLabel(int inversion, {bool compact = false}) {
    if (inversion == 0) {
      return compact ? 'Fundamental' : 'Posición fundamental';
    }
    return '$inversionª inversión';
  }

  void _metronomeTick() {
    if (!_metroRunning) {
      return;
    }
    final clicks = _metroClicksPerBeat.clamp(1, 6);
    final isPrimary = _metroSubdivisionIndex % clicks == 0;
    var isBarAccent = false;
    if (isPrimary) {
      if (_metroTickCount > 0) {
        _metroDirection *= -1;
      }
      _metroMotionStartAt = DateTime.now();
      final nextBeat = (_metroCurrentBeat + 1) % _metroBeatsPerBar;
      _metroCurrentBeat = nextBeat;
      isBarAccent = _metroBarAccent && nextBeat == 0;
    }

    // Fire audio first, then delay the visual update to align with actual sound output.
    // iOS audioplayers has ~26ms latency; Android has ~35ms. Visual trails audio otherwise.
    unawaited(
      _playMetronomeClick(
        accent: isPrimary,
        bar: isBarAccent,
        volumeScale: _metronomeVolumeGain(),
      ),
    );

    if (isPrimary) {
      if (isBarAccent) {
        HapticFeedback.mediumImpact();
      } else {
        HapticFeedback.selectionClick();
      }
    } else {
      HapticFeedback.selectionClick();
    }

    final visualDelayMs = Platform.isIOS ? 26 : 35;
    Future<void>.delayed(Duration(milliseconds: visualDelayMs), () {
      if (!mounted || !_metroRunning) return;
      setState(() {});
    });

    if (isPrimary) {
      _metroTickCount += 1;
    }
    _metroSubdivisionIndex += 1;
    if (_metroTimerEnabled) {
      final subMs = (60000 / (_metroBpm * clicks)).round().clamp(20, 2000);
      _metroRemaining -= Duration(milliseconds: subMs);
      if (_metroRemaining <= Duration.zero) {
        _stopMetronome();
        return;
      }
    }
  }

  void _startMetronomeAnimation() {
    _metroAnimTimer?.cancel();
    _metroAnimTimer = Timer.periodic(const Duration(milliseconds: 16), (_) {
      if (!mounted || !_metroRunning) {
        return;
      }
      if (_tabIndex == 4) {
        setState(() {});
      }
    });
  }

  double _metronomeMotionProgress() {
    if (!_metroRunning || _metroMotionStartAt.millisecondsSinceEpoch == 0) {
      return 0.0;
    }
    final beatSeconds = 60.0 / _metroBpm.clamp(1, 400);
    final elapsed =
        DateTime.now().difference(_metroMotionStartAt).inMilliseconds / 1000.0;
    return (elapsed / beatSeconds).clamp(0.0, 1.0);
  }

  List<int> _tunerOpenNotesForCurrentTuning() {
    switch (_tunerTuning) {
      case 'drop_d':
        return <int>[38, 45, 50, 55, 59, 64];
      case 'half_step_down':
        return <int>[39, 44, 49, 54, 58, 63];
      case 'standard_e':
      default:
        return <int>[40, 45, 50, 55, 59, 64];
    }
  }

  List<String> _tunerOpenLabelsForCurrentTuning() {
    return _tunerOpenNotesForCurrentTuning()
        .map((n) => _pcLabel(((n % 12) + 12) % 12))
        .toList(growable: false);
  }

  List<double> _tunerOpenFreqsForCurrentTuning() {
    return _tunerOpenNotesForCurrentTuning()
        .map((n) => _midiToFreq(n))
        .toList(growable: false);
  }

  double _midiToFreq(int midi) => 440.0 * math.pow(2.0, (midi - 69) / 12.0);

  List<Rect> _tunerCardRectsForSize(Size size) {
    final padX = 20.0;
    final cardGap = math.max(6.0, math.min(12.0, size.width * 0.012));
    final cardsH = math.max(68.0, math.min(114.0, size.height * 0.34));
    final cardW = (size.width - (padX * 2) - (cardGap * 5)) / 6;
    const cardsY = 16.0;
    return List<Rect>.generate(6, (i) {
      final x = padX + i * (cardW + cardGap);
      return Rect.fromLTWH(x, cardsY, cardW, cardsH);
    });
  }

  void _onTunerStaffTap(Offset localPosition, Size size) {
    final rects = _tunerCardRectsForSize(size);
    final idx = rects.indexWhere((r) => r.contains(localPosition));
    if (idx < 0) return;
    final notes = _tunerOpenNotesForCurrentTuning();
    if (idx >= notes.length) return;
    final targetMidi = notes[idx];
    setState(() {
      _tunerCurrentStringIdx = idx;
      _tunerNote = _pcLabel(((targetMidi % 12) + 12) % 12);
      _tunerCents = 0;
      _tunerFreq = _midiToFreq(targetMidi);
      _tunerSmoothedFreq = _tunerFreq;
    });
    unawaited(
      _playTone(
        midi: targetMidi,
        instrument: 'guitar',
        durationSeconds: 0.95,
        lowVolume: true,
      ),
    );
  }

  void _startMetronome() {
    _metroTimer?.cancel();
    _metroAnimTimer?.cancel();
    final totalSeconds = (_metroTimerMinutes * 60) + _metroTimerSeconds;
    setState(() {
      _metroRunning = true;
      _metroCurrentBeat = -1;
      _metroSubdivisionIndex = 0;
      _metroDirection = 1;
      _metroTickCount = 0;
      _metroMotionStartAt = DateTime.now();
      _metroRemaining = Duration(seconds: math.max(1, totalSeconds));
    });
    _startMetronomeAnimation();
    _metronomeTick();
    final clicks = _metroClicksPerBeat.clamp(1, 6);
    final intervalMs = (60000 / (_metroBpm * clicks)).round().clamp(20, 2000);
    _metroTimer = Timer.periodic(
      Duration(milliseconds: intervalMs),
      (_) => _metronomeTick(),
    );
  }

  void _stopMetronome() {
    _metroTimer?.cancel();
    _metroAnimTimer?.cancel();
    _metroTimer = null;
    _metroAnimTimer = null;
    setState(() {
      _metroRunning = false;
      _metroCurrentBeat = -1;
      _metroSubdivisionIndex = 0;
      _metroTickCount = 0;
    });
  }

  void _toggleMetronome() {
    if (_metroRunning) {
      _stopMetronome();
    } else {
      _startMetronome();
    }
  }

  double? _estimatePitch(List<double> input, int sampleRate) {
    if (input.length < 256) {
      return null;
    }
    final n = math.min(input.length, 4096);
    final data = List<double>.filled(n, 0.0);
    double mean = 0.0;
    for (int i = 0; i < n; i += 1) {
      mean += input[i];
    }
    mean /= n;
    double rms = 0.0;
    for (int i = 0; i < n; i += 1) {
      final v = input[i] - mean;
      data[i] = v;
      rms += v * v;
    }
    rms = math.sqrt(rms / n);
    if (rms < 0.008) {
      return null;
    }

    final minLag = (sampleRate / 1100).floor().clamp(8, n ~/ 2);
    final maxLag = (sampleRate / 55).floor().clamp(minLag + 1, n ~/ 2);
    int bestLag = -1;
    double bestCorr = 0.0;
    for (int lag = minLag; lag <= maxLag; lag += 1) {
      double corr = 0.0;
      for (int i = 0; i < n - lag; i += 1) {
        corr += data[i] * data[i + lag];
      }
      if (corr > bestCorr) {
        bestCorr = corr;
        bestLag = lag;
      }
    }
    if (bestLag <= 0 || bestCorr <= 0.0) {
      return null;
    }
    final freq = sampleRate / bestLag;
    if (freq < 50 || freq > 1300) {
      return null;
    }
    return freq;
  }

  List<double> _computeTunerSpectrum(
    List<double> samples,
    int sampleRate, {
    required double minHz,
    required double maxHz,
    int bins = 96,
  }) {
    if (samples.isEmpty || sampleRate <= 0 || bins <= 0) {
      return List<double>.filled(math.max(1, bins), 0.0);
    }
    final n = math.min(samples.length, 1024);
    if (n < 64) return List<double>.filled(bins, 0.0);
    final start = samples.length - n;
    final windowed = List<double>.filled(n, 0.0);
    for (int i = 0; i < n; i += 1) {
      final w = 0.5 - 0.5 * math.cos((2 * math.pi * i) / (n - 1));
      windowed[i] = samples[start + i] * w;
    }
    final fMin = minHz.clamp(1.0, sampleRate / 2 - 1);
    final fMax = maxHz.clamp(fMin + 1, sampleRate / 2 - 1);
    final logMin = math.log(fMin);
    final logMax = math.log(fMax);
    final out = List<double>.filled(bins, 0.0);
    double maxMag = 0.0;
    for (int b = 0; b < bins; b += 1) {
      final t = bins == 1 ? 0.0 : (b / (bins - 1));
      final freq = math.exp(logMin + (logMax - logMin) * t);
      final omega = 2 * math.pi * freq / sampleRate;
      double re = 0.0;
      double im = 0.0;
      for (int i = 0; i < n; i += 1) {
        final s = windowed[i];
        re += s * math.cos(omega * i);
        im -= s * math.sin(omega * i);
      }
      final mag = math.sqrt(re * re + im * im) / n;
      out[b] = mag;
      if (mag > maxMag) maxMag = mag;
    }
    if (maxMag <= 1e-9) return List<double>.filled(bins, 0.0);
    for (int i = 0; i < out.length; i += 1) {
      out[i] = (out[i] / maxMag).clamp(0.0, 1.0);
    }
    return out;
  }

  void _onTunerAudio(dynamic obj) {
    List<double> samples;
    if (obj is Float64List) {
      samples = obj.toList(growable: false);
    } else if (obj is Float32List) {
      samples = obj.map((v) => v.toDouble()).toList(growable: false);
    } else if (obj is List<dynamic>) {
      samples = obj.map((v) => (v as num).toDouble()).toList(growable: false);
    } else {
      return;
    }
    final scaled = samples
        .map((s) => (s * _tunerInputGain).clamp(-1.0, 1.0))
        .toList(growable: false);
    final effectiveSampleRate =
        (_audioCapture?.actualSampleRate?.round() ?? _tunerSampleRate).clamp(
          8000,
          96000,
        );
    final spectrum = _computeTunerSpectrum(
      scaled,
      effectiveSampleRate,
      minHz: _tunerRangeMin.toDouble(),
      maxHz: _tunerRangeMax.toDouble(),
    );
    if (_tunerSpectrumBins.length != spectrum.length) {
      _tunerSpectrumBins = List<double>.from(spectrum);
    } else {
      for (int i = 0; i < spectrum.length; i += 1) {
        final current = _tunerSpectrumBins[i];
        final incoming = spectrum[i];
        // Musical envelope: quick attack, slower decay.
        double next;
        if (incoming >= current) {
          next = current * 0.35 + incoming * 0.65;
        } else {
          final decayed = current * 0.93;
          next = math.max(incoming, decayed);
        }
        // Gentle compression and tiny floor removal for cleaner motion.
        final compressed = math.pow(next, 0.78).toDouble();
        _tunerSpectrumBins[i] = compressed < 0.012 ? 0.0 : compressed;
      }
    }

    final detected = _estimatePitch(scaled, effectiveSampleRate);
    int? bestIdx;
    int? rounded;
    double? bestCents;
    if (detected != null &&
        detected >= _tunerRangeMin &&
        detected <= _tunerRangeMax) {
      _tunerSmoothedFreq = _tunerSmoothedFreq <= 0.0
          ? detected
          : (_tunerSmoothedFreq * 0.72 + detected * 0.28);
      final midi = 69 + 12 * (math.log(_tunerSmoothedFreq / 440.0) / math.ln2);
      rounded = midi.round();
      final tuningNotes = _tunerOpenNotesForCurrentTuning();
      int localBestIdx = 0;
      double bestAbsCents = double.infinity;
      double localBestCents = 0.0;
      for (int i = 0; i < tuningNotes.length; i += 1) {
        final targetFreq = 440.0 * math.pow(2.0, (tuningNotes[i] - 69) / 12.0);
        final centsToString =
            1200.0 * (math.log(_tunerSmoothedFreq / targetFreq) / math.ln2);
        final absVal = centsToString.abs();
        if (absVal < bestAbsCents) {
          bestAbsCents = absVal;
          localBestIdx = i;
          localBestCents = centsToString;
        }
      }
      bestIdx = localBestIdx;
      bestCents = localBestCents;
    }

    final now = DateTime.now();
    if (now.difference(_lastTunerUiUpdate).inMilliseconds < 80) {
      return;
    }
    _lastTunerUiUpdate = now;
    if (!mounted || !_tunerRunning) {
      return;
    }
    setState(() {
      if (rounded != null && bestIdx != null && bestCents != null) {
        _tunerNote = _pcLabel(((rounded % 12) + 12) % 12);
        _tunerCurrentStringIdx = bestIdx;
        _tunerCents = bestCents.round().clamp(-50, 50);
        _tunerFreq = _tunerSmoothedFreq;
      }
    });
  }

  void _onTunerError(Object err) {
    if (!mounted) {
      return;
    }
    setState(() {
      _tunerError = '$err';
      _tunerRunning = false;
      _tunerCurrentStringIdx = null;
    });
  }

  Future<void> _startTuner() async {
    if (_tunerRunning) {
      return;
    }
    try {
      _audioCapture ??= FlutterAudioCapture();
      final initialized = await _audioCapture!.init();
      if (initialized != true) {
        throw Exception('No se pudo inicializar FlutterAudioCapture');
      }
      _tunerError = '';
      _tunerSmoothedFreq = 0.0;
      _tunerSpectrumBins = List<double>.filled(96, 0.0);
      await _audioCapture!.start(
        _onTunerAudio,
        _onTunerError,
        sampleRate: _tunerSampleRate,
        bufferSize: 3000,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _tunerRunning = true;
        _tunerCurrentStringIdx = null;
      });
    } catch (err) {
      if (!mounted) {
        return;
      }
      setState(() {
        _tunerError = '$err';
        _tunerRunning = false;
      });
    }
  }

  Future<void> _stopTuner() async {
    try {
      await _audioCapture?.stop();
    } catch (_) {}
    if (!mounted) {
      return;
    }
    setState(() {
      _tunerRunning = false;
      _tunerCurrentStringIdx = null;
      _tunerSpectrumBins = List<double>.filled(_tunerSpectrumBins.length, 0.0);
    });
  }

  Future<void> _toggleTuner() async {
    if (_tunerRunning) {
      await _stopTuner();
    } else {
      await _startTuner();
    }
  }

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final portrait = media.orientation == Orientation.portrait;
    final compactPhone = _isCompactPhone(context);
    final enabledModes = _enabledModeIndexes();
    final currentTab = enabledModes.contains(_tabIndex) ? _tabIndex : 0;
    if (currentTab != _tabIndex) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          setState(() {
            _tabIndex = currentTab;
            // Clean up held notes if exiting generation mode
            if (!(_tabIndex == 1 || _tabIndex == 2)) {
              _generationMidiHeldNotes.clear();
            }
          });
          if (currentTab != 0) {
            _cancelMidiScreenActivityExtension();
          }
        }
      });
    }
    final pages = <Widget>[
      _buildDetectionPage(),
      _buildChordGenerationPage(),
      _buildCircleOfFifthsPage(),
      _buildScaleGenerationPage(),
      _buildMetronomePage(),
      _buildIntervalDetectionPage(),
      _buildTunerPage(),
    ];

    return Stack(
      children: <Widget>[
        Scaffold(
      appBar: AppBar(
        toolbarHeight: compactPhone ? (portrait ? 60 : 64) : (portrait ? 64 : 74),
        automaticallyImplyLeading: false,
        leadingWidth: compactPhone ? 196.0 : 340.0,
        leading: Padding(
          padding: EdgeInsets.only(left: compactPhone ? 8.0 : 16.0),
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'MIDI Piano & Guitar Chords',
              style: TextStyle(
                fontSize: compactPhone
                    ? (portrait ? 15 : 18)
                    : (portrait ? 19 : 24),
                color: _text,
                fontWeight: FontWeight.w500,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ),
        // Sin centrar: así Flutter ajusta `title` al espacio libre real
        // entre `leading` y `actions` (que varía según si el botón "Salida
        // MIDI/Audio" está visible), en vez de tener que estimarlo a mano.
        centerTitle: false,
        titleSpacing: 8,
        title: LayoutBuilder(
          builder: (context, titleConstraints) {
            // Margen de seguridad extra para que el combo no quede pegado
            // a los botones vecinos de `actions`.
            final safetyMargin = compactPhone ? 16.0 : 20.0;
            final availableForTitle =
                math.max(80.0, titleConstraints.maxWidth - safetyMargin);
            final dropdownW = math.min(
              compactPhone
                  ? (portrait ? 260.0 : 300.0)
                  : (portrait ? 380.0 : 340.0),
              availableForTitle,
            );
            return SizedBox(
                width: dropdownW,
                child: _helpAnchor(
                  'mode_select',
                      DropdownButtonFormField<int>(
                        key: ValueKey<String>(
                          'mode_${currentTab}_${_kEnableMobileTuner ? 1 : 0}',
                        ),
                        initialValue: currentTab,
                        isExpanded: true,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: InputDecoration(
                          hintText: _ui('Modo', 'Mode'),
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: compactPhone ? 10 : 12,
                            vertical: compactPhone ? 6 : (portrait ? 8 : 10),
                          ),
                          isDense: true,
                        ),
                        items: enabledModes
                            .map(
                              (i) => DropdownMenuItem<int>(
                                value: i,
                                child: Text(
                                  _modeLabel(i),
                                  overflow: TextOverflow.ellipsis,
                                  maxLines: 1,
                                ),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value == null) return;
                          if (!_kEnableMobileTuner && value == 6) return;
                          setState(() {
                            _tabIndex = value;
                            _setHelpMode(false);
                            if (value == 0) {
                              _instrumentView = 'piano';
                            }
                            if (value == 3) _needsPianoScrollSync = true;
                          });
                          if (value != 3) {
                            _stopScaleLoop();
                          }
                          if (value != 4) {
                            _stopMetronome();
                          }
                          if (value != 6 && _tunerRunning) {
                            unawaited(_stopTuner());
                          }
                          _stopHeldChord();
                          _stopHeldInputs();
                          _stopHeldMidiInputs();
                          _generationInputStaffNotes.clear();
                          _clearGenerationPianoHighlight();
                          _detectionPlayPressed = false;
                          _generationPlayPressed = false;
                          if (value != 0) {
                            _detectionMidiHeldNotes.clear();
                          }
                          if (value == 0 && !_requestInFlight) {
                            unawaited(_callDetect());
                          } else if (value == 1 && !_requestInFlight) {
                            unawaited(_callGenerateChord());
                          } else if (value == 2 && !_requestInFlight) {
                            unawaited(_callCircleGenerateChord());
                          } else if (value == 3 && !_requestInFlight) {
                            unawaited(_callGenerateScale());
                          }
                          if (value != 0) {
                            _cancelMidiScreenActivityExtension();
                          }
                          _savePrefs();
                        },
                      ),
                    ),
            );
          },
        ),
        actions: <Widget>[
          _helpAnchor('midi_toggle', Padding(
            padding: EdgeInsets.only(right: compactPhone ? 6 : 8),
            child: OutlinedButton(
              onPressed: _toggleMidiInput,
              style: OutlinedButton.styleFrom(
                side: BorderSide(
                  color: _midiInputEnabled ? _accent : _border,
                  width: _midiInputEnabled ? 2 : 1,
                ),
                foregroundColor: _midiInputEnabled
                    ? const Color(0xFF1A222D)
                    : _text,
                backgroundColor: _midiInputEnabled ? _accent : _surfaceDark,
                padding: EdgeInsets.symmetric(
                  horizontal: compactPhone ? 10 : 14,
                  vertical: compactPhone ? 6 : 8,
                ),
              ),
              child: Text(_midiInputEnabled ? 'MIDI: On' : 'MIDI: Off'),
            ),
          )),
          if (_midiInputEnabled)
            _helpAnchor('sound_output', Padding(
              padding: EdgeInsets.only(right: compactPhone ? 6 : 8),
              child: OutlinedButton.icon(
                onPressed: () => setState(() {
                  _soundOutput = _soundOutput == 'audio' ? 'midi' : 'audio';
                }),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(
                    color: _soundOutput == 'midi' ? _accent : _border,
                    width: _soundOutput == 'midi' ? 2 : 1,
                  ),
                  foregroundColor: _soundOutput == 'midi'
                      ? const Color(0xFF1A222D)
                      : _text,
                  backgroundColor: _soundOutput == 'midi' ? _accent : _surfaceDark,
                  padding: EdgeInsets.symmetric(
                    horizontal: compactPhone ? 8 : 12,
                    vertical: compactPhone ? 6 : 8,
                  ),
                ),
                icon: Icon(
                  _soundOutput == 'midi' ? Icons.piano : Icons.volume_up,
                  size: 16,
                ),
                label: Text(_soundOutput == 'midi'
                    ? _ui('Salida MIDI', 'MIDI out')
                    : _ui('Audio', 'Audio')),
              ),
            )),
          _helpAnchor('accidental', Container(
            constraints: BoxConstraints(minWidth: compactPhone ? 64 : 76),
            margin: EdgeInsets.only(right: compactPhone ? 6 : 8),
            padding: EdgeInsets.symmetric(horizontal: compactPhone ? 6 : 8),
            decoration: BoxDecoration(
              color: _surfaceDark,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: _border),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _accidental,
                dropdownColor: _surfaceDark,
                style: const TextStyle(color: _text),
                iconEnabledColor: _muted,
                items: const <DropdownMenuItem<String>>[
                  DropdownMenuItem<String>(value: 'sharp', child: Text('#')),
                  DropdownMenuItem<String>(value: 'flat', child: Text('♭')),
                ],
                onChanged: (value) {
                  if (value == null) {
                    return;
                  }
                  setState(() => _accidental = value);
                  unawaited(_loadMeta());
                  if (_tabIndex == 0 && !_requestInFlight) {
                    unawaited(_callDetect());
                  } else if (_tabIndex == 1 &&
                      _generatedChordJson != null &&
                      !_requestInFlight) {
                    unawaited(_callGenerateChord());
                  } else if (_tabIndex == 2 &&
                      _generatedChordJson != null &&
                      !_requestInFlight) {
                    unawaited(_callCircleGenerateChord());
                  } else if (_tabIndex == 3 &&
                      _generatedScaleJson != null &&
                      !_requestInFlight) {
                    unawaited(_callGenerateScale());
                  }
                },
              ),
            ),
          )),
          _helpAnchor('help_toggle', IconButton(
            tooltip: _ui('Ayuda', 'Help'),
            onPressed: _toggleHelpMode,
            icon: Icon(
              _helpActive ? Icons.help_center : Icons.help_outline,
              color: _helpActive ? _accent : null,
            ),
          )),
          _helpAnchor('settings', IconButton(
            tooltip: 'Configuración',
            onPressed: _openSettingsPanel,
            icon: const Icon(Icons.settings),
          )),
          SizedBox(width: compactPhone ? 4 : 8),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: <Color>[_bgTop, _bgBottom],
          ),
        ),
        child: Column(children: <Widget>[
          if (_midiInputEnabled && _midiError.isNotEmpty)
            Container(
              width: double.infinity,
              color: const Color(0xFF3A1414),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                _midiError,
                style: const TextStyle(color: Colors.red),
                textAlign: TextAlign.center,
              ),
            ),
          Expanded(child: pages[currentTab]),
        ]),
      ),
    ),
        if (_helpActive) _buildHelpOverlay(),
      ],
    );
  }

  Widget _buildModeScaffold({
    required Widget controls,
    bool showInstrument = true,
    Widget? bottomPanel,
  }) {
    final staffNotes = _staffNotesForCurrentTab();
    final staffExtras = _staffExtrasForCurrentTab();
    final instrumentNotes = _activeMidiForInstrument();
    final staffPanel = _tabIndex == 4
        ? _buildStaffPanel(staffNotes, staffExtras)
        : _helpAnchor(
            _staffHelpIdForCurrentMode(),
            _buildStaffPanel(staffNotes, staffExtras),
          );
    final controlsPanel = _panel(child: controls);
    return Padding(
      padding: const EdgeInsets.all(12),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final wide = constraints.maxWidth >= 900;
          if (compactPhone) {
            final staffHeight = math.min(
              280.0,
              math.max(180.0, constraints.maxHeight * 0.28),
            );
            final compactLandscape = constraints.maxWidth > constraints.maxHeight;
            final compactTopHeight = compactLandscape
                ? (_tabIndex == 4
                      ? math.max(300.0, constraints.maxHeight * 0.58)
                      : math.max(240.0, constraints.maxHeight * 0.42))
                : staffHeight;
            return SingleChildScrollView(
              child: Column(
                children: <Widget>[
                  if (compactLandscape)
                    SizedBox(
                      height: compactTopHeight,
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Expanded(
                            flex: 11,
                            child: staffPanel,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            flex: 9,
                            child: controlsPanel,
                          ),
                        ],
                      ),
                    )
                  else ...<Widget>[
                    SizedBox(
                      height: staffHeight,
                      child: staffPanel,
                    ),
                    const SizedBox(height: 12),
                    controlsPanel,
                  ],
                  if (bottomPanel != null) ...<Widget>[
                    const SizedBox(height: 12),
                    bottomPanel,
                  ] else if (showInstrument) ...<Widget>[
                    const SizedBox(height: 12),
                    _buildInstrumentPanel(instrumentNotes),
                  ],
                ],
              ),
            );
          }
          final top = wide
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(
                      flex: 57,
                      child: staffPanel,
                    ),
                    const SizedBox(width: 12),
                    Expanded(flex: 43, child: controlsPanel),
                  ],
                )
              : Column(
                  children: <Widget>[
                    Expanded(
                      flex: 56,
                      child: staffPanel,
                    ),
                    const SizedBox(height: 12),
                    Expanded(flex: 44, child: controlsPanel),
                  ],
                );
          return Column(
            children: <Widget>[
              Expanded(child: top),
              if (bottomPanel != null) ...<Widget>[
                const SizedBox(height: 12),
                bottomPanel,
              ] else if (showInstrument) ...<Widget>[
                const SizedBox(height: 12),
                _buildInstrumentPanel(instrumentNotes),
              ],
            ],
          );
        },
      ),
    );
  }

  Widget _buildStaffPanel(Set<int> notes, Set<int> extras) {
    final title = switch (_tabIndex) {
      4 => _ui('Metrónomo', 'Metronome'),
      5 => _ui('Afinador', 'Tuner'),
      _ => _ui('Pentagrama', 'Staff'),
    };
    final guitarStaffMode =
        _instrumentView == 'guitar' &&
        (_tabIndex == 0 ||
            _tabIndex == 1 ||
            _tabIndex == 2 ||
            _tabIndex == 3);
    int staffMidi(int midi) => guitarStaffMode ? midi + 12 : midi;
    List<int> guitarDisplayVoicing(Iterable<int> source, {bool lowerBass = false}) {
      final mapped = source.map(staffMidi).toList()..sort();
      if (guitarStaffMode && lowerBass && mapped.isNotEmpty) {
        mapped[0] -= 12;
      }
      return mapped;
    }

    final lowerGuitarBass =
        (_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'guitar';
    final displayNotes = guitarDisplayVoicing(notes, lowerBass: lowerGuitarBass);
    final displayExtras = extras.map(staffMidi).toSet();
    final displayDetectionActiveNotes = _tabIndex == 0
        ? guitarDisplayVoicing(_activeDetectionNotes).toSet()
        : const <int>{};
    // Guitarra: las variantes pueden no coincidir con `notes_midi` del JSON;
    // el pentagrama usa `notes` (= `_staffNotesForCurrentTab`). Si `rhSet` se
    // arma solo con el JSON, una nota del acorde dibujada queda fuera de `rhSet`
    // y solo `generationPlayingNotes` la colorea (parece “nota en reproducción”).
    final displayGenerationRhNotes =
        ((_tabIndex == 1 || _tabIndex == 2) && _generatedChordJson != null)
        ? (_instrumentView == 'guitar'
              ? List<int>.from(displayNotes)
              : guitarDisplayVoicing(
                  _extractMidiList(_generatedChordJson!, <String>['notes_midi']),
                  lowerBass: lowerGuitarBass,
                ))
        : const <int>[];
    final displayGenerationLhNotes =
        ((_tabIndex == 1 || _tabIndex == 2) &&
            _instrumentView == 'piano' &&
            _generatedChordJson != null)
        ? _extractMidiList(_generatedChordJson!, <String>[
            'notes_midi',
          ]).map((n) => n - 12).where((n) => n >= 0).toList()
        : const <int>[];
    final bool generationPlaybackActive =
        (_tabIndex == 1 || _tabIndex == 2) &&
        (_generationPlayPressed ||
            _heldChordNativeNotes.isNotEmpty ||
            _heldChordPlayers.isNotEmpty ||
            _generationInputStaffNotes.isNotEmpty);
    final displayGenerationPlayingNotes = (_tabIndex == 1 || _tabIndex == 2)
        ? (generationPlaybackActive
              ? guitarDisplayVoicing(
                  _generationPlayingNotesForStaff(),
                  lowerBass: lowerGuitarBass,
                ).toSet()
              : <int>{})
        : const <int>{};
    final displayScaleRhNotes = _tabIndex == 3
        ? _scaleBaseNotes().map(staffMidi).toList()
        : const <int>[];
    final displayScaleLhNotes = (_tabIndex == 3 && _instrumentView == 'piano')
        ? _scaleLhNotes(_scaleBaseNotes())
        : const <int>[];
    final displayScaleCurrentNote = _tabIndex == 3 && _scaleCurrentNote != null
        ? staffMidi(_scaleCurrentNote!)
        : null;
    final staffKeySig = _staffKeySignatureForCurrentTab();
    final imelMode = _tabIndex == 5 && _intervalMelodyMode;
    final imelSemitones = _tabIndex == 5 ? _getIntervalSemitones() : null;
    final imelMelody = imelSemitones != null ? getIntervalMelody(imelSemitones) : null;
    final imelNotes = imelMode ? _getIntervalMelodyNotes() : const <int?>[];
    final imelDurations = imelMelody?.durations ?? const <String>[];
    final imelBeatsPerBar = imelMelody?.beatsPerBar ?? 4;
    final imelAnacrusis = imelMelody?.anacrusis ?? 0.0;
    return _panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            title,
            style: TextStyle(color: _muted, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          if (_tabIndex == 2) ...<Widget>[
            RichText(
              text: TextSpan(
                style: const TextStyle(color: _muted, fontSize: 14, height: 1.3),
                children: <TextSpan>[
                  TextSpan(text: '${_ui('Acorde', 'Chord')}: '),
                  TextSpan(
                    text: _chordResultValue('name'),
                    style: const TextStyle(
                      color: _text,
                      fontWeight: FontWeight.w800,
                      fontSize: 16,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
          ],
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF0F1621),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF3A4558)),
              ),
	              child: switch (_tabIndex) {
	                4 => LayoutBuilder(
	                  builder: (context, constraints) {
	                    final metronomeSize = Size(
	                      constraints.maxWidth,
	                      constraints.maxHeight,
	                    );
	                    return Stack(
	                      fit: StackFit.expand,
	                      children: <Widget>[
	                        CustomPaint(
	                          painter: _MiniMetronomePainter(
	                            beatsPerBar: _metroBeatsPerBar,
	                            clicksPerBeat: _metroClicksPerBeat,
	                            currentBeat: _metroCurrentBeat,
	                            running: _metroRunning,
	                            direction: _metroDirection,
	                            motionProgress: _metronomeMotionProgress(),
	                            timerEnabled: _metroTimerEnabled,
	                            timerRemaining: _metroRemaining,
	                          ),
	                          child: const SizedBox.expand(),
	                        ),
	                        Positioned.fromRect(
	                          rect: _metronomeBeatRowRect(metronomeSize),
	                          child: _helpAnchor(
	                            'metronome_bead_row',
	                            const SizedBox.expand(),
	                          ),
	                        ),
	                        Positioned.fromRect(
	                          rect: _metronomeMotionAxisRect(metronomeSize),
	                          child: _helpAnchor(
	                            'metronome_motion_axis',
	                            const SizedBox.expand(),
	                          ),
	                        ),
	                        Positioned.fromRect(
	                          rect: _metronomeTimerRect(metronomeSize),
	                          child: _helpAnchor(
	                            'metronome_timer_display',
	                            const SizedBox.expand(),
	                          ),
	                        ),
	                        Positioned.fromRect(
	                          rect: _metronomeCenterButtonRect(metronomeSize),
	                          child: IgnorePointer(
	                            ignoring: false,
	                            child: _helpAnchor(
	                              'metronome_toggle_left',
	                              FilledButton.icon(
	                                style: FilledButton.styleFrom(
	                                  backgroundColor: _metroRunning ? _accent : _surfaceDark,
	                                  foregroundColor: _metroRunning
	                                      ? const Color(0xFF1A222D)
	                                      : _text,
	                                  minimumSize: const Size(0, 46),
	                                  padding: const EdgeInsets.symmetric(
	                                    horizontal: 18,
	                                    vertical: 12,
	                                  ),
	                                  visualDensity: VisualDensity.compact,
	                                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
	                                  textStyle: const TextStyle(
	                                    fontSize: 18,
	                                    fontWeight: FontWeight.w700,
	                                  ),
	                                ),
	                                onPressed: _toggleMetronome,
	                                icon: Icon(
	                                  _metroRunning ? Icons.stop : Icons.play_arrow,
	                                  size: 22,
	                                ),
	                                label: Text(
	                                  _metroRunning
	                                      ? _ui('Detener', 'Stop')
	                                      : _ui('Iniciar', 'Start'),
	                                ),
	                              ),
	                            ),
	                          ),
	                        ),
	                      ],
	                    );
	                  },
	                ),
                5 => CustomPaint(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final panelSize = Size(
                        constraints.maxWidth,
                        constraints.maxHeight,
                      );
                      return GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTapDown: (details) =>
                            _onTunerStaffTap(details.localPosition, panelSize),
                        child: CustomPaint(
                          painter: _MiniTunerPainter(
                            noteLabel: _tunerNote,
                            cents: _tunerCents,
                            currentFreq: _tunerFreq,
                            currentStringIdx: _tunerCurrentStringIdx,
                            tuningLabels: _tunerOpenLabelsForCurrentTuning(),
                          ),
                          child: const SizedBox.expand(),
                        ),
                      );
                    },
                  ),
                ),
                _ => CustomPaint(
                  key: _tabIndex == 2
                      ? ValueKey<String>(
                          'circle_staff_${_circleTonicPc}_${_circleKeyMode}_${_circleChordRootPc}_${staffKeySig.count}_${staffKeySig.preferFlats}',
                        )
                      : null,
                  painter: _MiniStaffPainter(
                    notes: displayNotes,
                    extras: displayExtras,
                    detectionActiveNotes: displayDetectionActiveNotes,
                    generationRhNotes: displayGenerationRhNotes,
                    generationLhNotes: displayGenerationLhNotes,
                    generationPlayingNotes: displayGenerationPlayingNotes,
                    generationGuitarMode:
                        (_tabIndex == 1 || _tabIndex == 2) &&
                        _instrumentView == 'guitar',
                    scaleRhNotes: displayScaleRhNotes,
                    scaleLhNotes: displayScaleLhNotes,
                    scaleCurrentNote: displayScaleCurrentNote,
                    scaleCurrentIsLeft: _tabIndex == 3
                        ? _scaleCurrentIsLeft
                        : null,
                    scaleGuitarMode:
                        _tabIndex == 3 && _instrumentView == 'guitar',
                    keySignatureCount: staffKeySig.count,
                    keySignaturePreferFlats: staffKeySig.preferFlats,
                    intervalMelodyMode: imelMode,
                    intervalMelodyNotes: imelNotes,
                    intervalMelodyDurations: imelDurations,
                    intervalPlayingIdx: _tabIndex == 5 ? _intervalPlayingIdx : null,
                    intervalBeatsPerBar: imelBeatsPerBar,
                    intervalAnacrusis: imelAnacrusis,
                  ),
                  child: const SizedBox.expand(),
                ),
              },
            ),
          ),
          if (_tabIndex == 2) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              _ui(
                'Toca el anillo: elige un acorde diatónico (triada sobre un grado de la escala); no cambia la tónica. Mantén pulsado: fija la tónica y la tonalidad (mayor en el exterior, menor natural relativa en el interior; misma armadura).',
                'Tap: choose a diatonic chord—a triad on a scale degree (major, minor, or diminished); does not change the tonic. Long-press: sets the tonic and key (major on the outer ring, relative natural minor on the inner; same key signature).',
              ),
              style: const TextStyle(color: _muted, fontSize: 12, height: 1.35),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHelpOverlay() {
    return Positioned.fill(
      child: Material(
        color: Colors.transparent,
        child: LayoutBuilder(
          builder: (overlayContext, constraints) {
            final safePadding = MediaQuery.of(overlayContext).padding;
            final resolved = _resolvedHelpSteps(overlayContext);
            final helpToggleRect = _helpRectFor(overlayContext, 'help_toggle');
            if (resolved.isEmpty) {
              return Align(
                alignment: Alignment.topRight,
                child: Padding(
                  padding: EdgeInsets.only(
                    top: safePadding.top + 16,
                    right: 16,
                  ),
                  child: FilledButton.icon(
                    onPressed: _toggleHelpMode,
                    icon: const Icon(Icons.close),
                    label: Text(_ui('Cerrar ayuda', 'Close help')),
                  ),
                ),
              );
            }
            final selected = _selectedHelpStep(resolved);
            final activeRect = selected?.highlightRect;
            final helpTargets = resolved.map((r) => r.highlightRect).toList(growable: false);
            final helpPulse = 0.5 + (0.5 * math.sin(_helpOverlayController.value * math.pi * 2));
            final calloutRect = selected == null
                ? null
                : _helpCalloutRect(
                    target: activeRect!,
                    screenSize: constraints.biggest,
                    side: selected.step.side,
                    safePadding: safePadding,
                  );
            return Stack(
              children: <Widget>[
                Positioned.fill(
                  child: AnimatedBuilder(
                    animation: _helpOverlayController,
                    builder: (context, _) {
                      return CustomPaint(
                        painter: _HelpOverlayPainter(
                          targets: helpTargets,
                          activeRect: activeRect,
                          dashPhase: _helpOverlayController.value * 20,
                        ),
                      );
                    },
                  ),
                ),
                Align(
                  alignment: _tabIndex == 4
                      ? const Alignment(0, 0.36)
                      : const Alignment(0, 0.18),
                  child: IgnorePointer(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 520),
                      margin: const EdgeInsets.symmetric(horizontal: 24),
                      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                      decoration: BoxDecoration(
                        color: Color.lerp(
                          const Color(0x66182535),
                          const Color(0xCCF3BF2F),
                          helpPulse * 0.45,
                        ),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: Color.lerp(
                            const Color(0x33F3BF2F),
                            const Color(0xCCF3BF2F),
                            helpPulse,
                          )!,
                          width: 1.2 + (helpPulse * 0.8),
                        ),
                      ),
                      child: Text(
                        _ui(
                          'Modo ayuda activo. Toca la zona sobre la que quieres ayuda o pulsa ayuda otra vez para salir.',
                          'Help mode is active. Tap the area you want help with or tap help again to exit.',
                        ),
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          color: _text,
                          fontWeight: FontWeight.w700,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ),
                ),
                if (helpToggleRect != null)
                  Positioned.fromRect(
                    rect: helpToggleRect.inflate(4),
                    child: GestureDetector(
                      behavior: HitTestBehavior.translucent,
                      onTap: _toggleHelpMode,
                    ),
                  ),
                for (final item in resolved)
                  Positioned.fromRect(
                    rect: item.highlightRect,
                    child: MouseRegion(
                      cursor: SystemMouseCursors.help,
                      child: GestureDetector(
                        behavior: HitTestBehavior.translucent,
                        onTap: () => setState(() => _helpSelectedId = item.step.id),
                      ),
                    ),
                  ),
                if (selected != null && calloutRect != null)
                  Positioned.fromRect(
                    rect: calloutRect,
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        color: const Color(0xFF182535),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: _accent, width: 1.5),
                        boxShadow: const <BoxShadow>[
                          BoxShadow(
                            blurRadius: 20,
                            color: Color(0x55000000),
                            offset: Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
                        child: LayoutBuilder(
                          builder: (context, boxConstraints) {
                            final compactFooter = boxConstraints.maxWidth < 336;
                            return Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  _ui(selected.step.titleEs, selected.step.titleEn),
                                  style: const TextStyle(
                                    color: _text,
                                    fontSize: 18,
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Expanded(
                                  child: SingleChildScrollView(
                                    child: Text(
                                      _ui(selected.step.bodyEs, selected.step.bodyEn),
                                      style: const TextStyle(
                                        color: _text,
                                        height: 1.35,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 10),
                                if (compactFooter) ...<Widget>[
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: <Widget>[
                                      OutlinedButton(
                                        onPressed: () => setState(() => _helpSelectedId = null),
                                        child: Text(_ui('Ocultar', 'Hide')),
                                      ),
                                      FilledButton(
                                        onPressed: _toggleHelpMode,
                                        child: Text(_ui('Cerrar', 'Close')),
                                      ),
                                    ],
                                  ),
                                ] else
                                  Row(
                                    children: <Widget>[
                                      const Spacer(),
                                      Wrap(
                                        spacing: 8,
                                        runSpacing: 8,
                                        children: <Widget>[
                                          OutlinedButton(
                                            onPressed: () => setState(() => _helpSelectedId = null),
                                            child: Text(_ui('Ocultar', 'Hide')),
                                          ),
                                          FilledButton(
                                            onPressed: _toggleHelpMode,
                                            child: Text(_ui('Cerrar', 'Close')),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                              ],
                            );
                          },
                        ),
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildInstrumentPanel(Set<int> activeMidi) {
    final portrait = MediaQuery.of(context).orientation == Orientation.portrait;
    final compactPhone = _isCompactPhone(context);
    final metronomeFixedPiano = _tabIndex == 4;
    final showRightControls =
        _tabIndex == 1 || _tabIndex == 2 || _tabIndex == 3;
    final displayInstrumentView = metronomeFixedPiano ? 'piano' : _instrumentView;
    final pianoHelpId = _tabIndex == 3
        ? 'scales_instrument_piano'
        : 'generation_instrument_piano';
    final guitarHelpId = _tabIndex == 3
        ? 'scales_instrument_guitar'
        : 'generation_instrument_guitar';
    final handHelpId = _tabIndex == 3
        ? 'scales_guitar_hand'
        : 'generation_guitar_hand';
    final instrumentSurfaceHelpId = switch (_tabIndex) {
      0 => 'detection_instrument',
      1 => 'generation_instrument',
      2 => 'generation_instrument',
      3 => 'scales_instrument',
      4 => 'metronome_instrument',
      _ => 'generation_instrument',
    };
    final panelHeight = switch (_tabIndex) {
      4 => portrait ? 152.0 : 168.0,
      3 when _scaleMetronomeOnly => compactPhone ? (portrait ? 188.0 : 212.0) : (portrait ? 168.0 : 184.0),
      1 || 2 || 3 => compactPhone ? (portrait ? 204.0 : 232.0) : (portrait ? 188.0 : 220.0),
      _ => 220.0,
    };
    final chordVariations =
        ((_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'guitar')
        ? _chordGuitarVariations()
        : const <Map<String, dynamic>>[];
    final chordVoicings =
        ((_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'guitar')
        ? (chordVariations.isNotEmpty
              ? chordVariations.map(_variationNotes).toList()
              : _fallbackChordGuitarVoicings())
        : const <List<int>>[];
    final safeVariant = chordVoicings.isEmpty
        ? 0
        : _chordGuitarVariant.clamp(0, chordVoicings.length - 1);
    return _panel(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          SizedBox(
            height: panelHeight,
            child: compactPhone && showRightControls
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      Expanded(
                        child: _helpAnchor(
                          instrumentSurfaceHelpId,
                          displayInstrumentView == 'piano'
                              ? _buildPianoWithFingeringStrips(activeMidi)
                              : _buildGuitarStrip(
                                  activeMidi,
                                  chordVoicings: chordVoicings,
                                  chordVariations: chordVariations,
                                  chordVariant: safeVariant,
                                ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: <Widget>[
                          SizedBox(
                            width: 140,
                            child: _helpAnchor(
                              pianoHelpId,
                              _instToggle('piano', 'Piano'),
                            ),
                          ),
                          SizedBox(
                            width: 140,
                            child: _helpAnchor(
                              guitarHelpId,
                              _instToggle('guitar', 'Guitarra'),
                            ),
                          ),
                          if ((_tabIndex == 1 || _tabIndex == 2) &&
                              _instrumentView == 'guitar' &&
                              chordVoicings.length > 1) ...<Widget>[
                            _helpAnchor(
                              'generation_guitar_variant',
                              Row(
                                mainAxisSize: MainAxisSize.min,
                                children: <Widget>[
                                  OutlinedButton(
                                    onPressed: safeVariant > 0
                                        ? () => setState(
                                            () => _chordGuitarVariant = safeVariant - 1,
                                          )
                                        : null,
                                    child: const Icon(Icons.chevron_left),
                                  ),
                                  const SizedBox(width: 8),
                                  OutlinedButton(
                                    onPressed: safeVariant < chordVoicings.length - 1
                                        ? () => setState(
                                            () => _chordGuitarVariant = safeVariant + 1,
                                          )
                                        : null,
                                    child: const Icon(Icons.chevron_right),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          if (_instrumentView == 'guitar')
                            SizedBox(
                              width: 180,
                              child: _helpAnchor(
                                handHelpId,
                                DropdownButtonFormField<String>(
                                  key: ValueKey<String>('hand_$_guitarHandedness'),
                                  initialValue: _guitarHandedness,
                                  dropdownColor: _surfaceDark,
                                  style: const TextStyle(color: _text),
                                  decoration: const InputDecoration(
                                    isDense: true,
                                    labelText: 'Mano',
                                  ),
                                  items: const <DropdownMenuItem<String>>[
                                    DropdownMenuItem<String>(
                                      value: 'right',
                                      child: Text('Diestro'),
                                    ),
                                    DropdownMenuItem<String>(
                                      value: 'left',
                                      child: Text('Zurdo'),
                                    ),
                                  ],
                                  onChanged: (value) {
                                    if (value != null) {
                                      setState(() => _guitarHandedness = value);
                                    }
                                  },
                                ),
                              ),
                            ),
                        ],
                      ),
                    ],
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Expanded(
                        child: _helpAnchor(
                          instrumentSurfaceHelpId,
                          displayInstrumentView == 'piano'
                              ? _buildPianoWithFingeringStrips(activeMidi)
                              : _buildGuitarStrip(
                                  activeMidi,
                                  chordVoicings: chordVoicings,
                                  chordVariations: chordVariations,
                                  chordVariant: safeVariant,
                                ),
                        ),
                      ),
                      if (showRightControls) ...<Widget>[
                        const SizedBox(width: 10),
                        SizedBox(
                          width: 172,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: <Widget>[
                              _helpAnchor(
                                pianoHelpId,
                                _instToggle('piano', 'Piano'),
                              ),
                              const SizedBox(height: 8),
                              _helpAnchor(
                                guitarHelpId,
                                _instToggle('guitar', 'Guitarra'),
                              ),
                              if (_instrumentView == 'guitar') ...<Widget>[
                                const SizedBox(height: 8),
                                _helpAnchor(
                                  handHelpId,
                                  DropdownButtonFormField<String>(
                                    key: ValueKey<String>('hand_$_guitarHandedness'),
                                    initialValue: _guitarHandedness,
                                    dropdownColor: _surfaceDark,
                                    style: const TextStyle(color: _text),
                                    decoration: const InputDecoration(
                                      isDense: true,
                                      labelText: 'Mano',
                                    ),
                                    items: const <DropdownMenuItem<String>>[
                                      DropdownMenuItem<String>(
                                        value: 'right',
                                        child: Text('Diestro'),
                                      ),
                                      DropdownMenuItem<String>(
                                        value: 'left',
                                        child: Text('Zurdo'),
                                      ),
                                    ],
                                    onChanged: (value) {
                                      if (value != null) {
                                        setState(() => _guitarHandedness = value);
                                      }
                                    },
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
          ),
          if (!compactPhone &&
              (_tabIndex == 1 || _tabIndex == 2) &&
              _instrumentView == 'guitar') ...<Widget>[
            const SizedBox(height: 2),
            _helpAnchor(
              'generation_guitar_variant',
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  OutlinedButton(
                    onPressed: chordVoicings.length > 1 && safeVariant > 0
                        ? () => setState(
                            () => _chordGuitarVariant = safeVariant - 1,
                          )
                        : null,
                    child: const Icon(Icons.chevron_left),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    chordVoicings.isEmpty
                        ? 'Variante 0/0'
                        : 'Variante ${safeVariant + 1}/${chordVoicings.length}',
                    style: const TextStyle(
                      color: _muted,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton(
                    onPressed:
                        chordVoicings.length > 1 &&
                            safeVariant < chordVoicings.length - 1
                        ? () => setState(
                            () => _chordGuitarVariant = safeVariant + 1,
                          )
                        : null,
                    child: const Icon(Icons.chevron_right),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _instToggle(String key, String label) {
    final active = _instrumentView == key;
    final compactPhone = _isCompactPhone(context);
    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        minimumSize: compactPhone ? const Size(112, 42) : const Size(150, 56),
        padding: compactPhone
            ? const EdgeInsets.symmetric(horizontal: 12, vertical: 8)
            : const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
        backgroundColor: active ? _accent : _surfaceDark,
        side: BorderSide(color: active ? _accent : _border),
        foregroundColor: active ? const Color(0xFF1A222D) : _text,
      ),
      onPressed: () {
        setState(() {
          if (_instrumentView != key &&
              (_tabIndex == 1 || _tabIndex == 2)) {
            _generationInputStaffNotes.clear();
            _clearGenerationPianoHighlight();
            _stopHeldChord();
            _stopHeldInputs();
            _generationPlayPressed = false;
          }
          _instrumentView = key;
        });
      },
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Text(
          label,
          maxLines: 1,
          softWrap: false,
          overflow: TextOverflow.visible,
        ),
      ),
    );
  }

  /// Misma lógica que `RenderMixin._piano_fingering_for_count` (escritorio).
  List<int> _pianoFingeringRight(int count) {
    final n = math.max(1, count);
    switch (n) {
      case 1:
        return <int>[1];
      case 2:
        return <int>[1, 3];
      case 3:
        return <int>[1, 3, 5];
      case 4:
        return <int>[1, 2, 4, 5];
      case 5:
        return <int>[1, 2, 3, 4, 5];
      default:
        return List<int>.generate(n, (i) => math.min(5, i + 1));
    }
  }

  /// Mano izquierda: dedos de grave a agudo (p. ej. tríada Do 5-3-1).
  List<int> _pianoFingeringLeft(int count) {
    final n = math.max(1, count);
    switch (n) {
      case 1:
        return <int>[5];
      case 2:
        return <int>[5, 3];
      case 3:
        return <int>[5, 3, 1];
      case 4:
        return <int>[5, 3, 2, 1];
      case 5:
        return <int>[5, 4, 3, 2, 1];
      default:
        return List<int>.generate(n, (i) => math.max(1, 5 - i));
    }
  }

  Widget _buildPianoWithFingeringStrips(Set<int> activeMidi) {
    final showStrips = _tabIndex == 3 &&
        _instrumentView == 'piano' &&
        _scaleFingeringHand != null &&
        _scaleFingeringsMap.isNotEmpty;

    final sortedNotes = _scaleFingeringsMap.keys.toList()..sort();
    final fingers = sortedNotes.map((n) => _scaleFingeringsMap[n]!).toList();
    final ascCross = List<bool>.filled(fingers.length, false);
    final descCross = List<bool>.filled(fingers.length, false);
    for (int i = 1; i < fingers.length; i++) {
      if ((fingers[i] - fingers[i - 1]).abs() > 1) ascCross[i] = true;
    }
    for (int i = 0; i < fingers.length - 1; i++) {
      if ((fingers[i] - fingers[i + 1]).abs() > 1) descCross[i] = true;
    }

    // El `Column` con tiras (aunque ocultas con Opacity) se devuelve siempre
    // con la misma forma de árbol de widgets y las mismas dimensiones
    // (`stripH`/`gap` fijos); si `!showStrips` cambiara esas dimensiones, el
    // alto disponible del piano (`pianoViewH`) variaría entre modos y dejaría
    // hueco en blanco o desajustaría el tamaño de tecla. Y si en su lugar
    // devolviéramos directamente `_buildPianoStrip(...)` cuando `!showStrips`
    // (cambiando el tipo del widget raíz), Flutter destruiría y recrearía
    // todo el subárbol del piano — reseteando el ScrollController a offset 0.
    return LayoutBuilder(builder: (context, constraints) {
      const stripH = 22.0;
      const gap = 2.0;
      final viewportW = constraints.maxWidth;
      final pianoViewH = (constraints.maxHeight - 2 * (stripH + gap))
          .clamp(60.0, (_kPianoWhiteKeyHeight + 12).toDouble());

      final allWhite = List<int>.generate(
        _kPianoHighMidi - _kPianoLowMidi + 1,
        (i) => _kPianoLowMidi + i,
      ).where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12)).toList();

      final effectiveW = _computePianoKeyMetrics(
        viewportW: viewportW,
        viewportH: pianoViewH,
        whiteKeyCount: allWhite.length,
      ).whiteW;
      final double keyboardW = allWhite.length * effectiveW;
      final double badgeW = (effectiveW * 0.85).clamp(16.0, 22.0);

      List<Widget> buildBadges(bool ascending) {
        final badges = <Widget>[];
        for (int i = 0; i < sortedNotes.length; i++) {
          final midi = sortedNotes[i];
          final finger = fingers[i];
          final cross = ascending ? ascCross[i] : descCross[i];
          final bool isBlack =
              const <int>{1, 3, 6, 8, 10}.contains(midi % 12);
          final double x;
          if (isBlack) {
            final wIdx = allWhite.indexWhere((m) => m >= midi);
            x = (wIdx < 0 ? allWhite.length - 1 : wIdx) * effectiveW;
          } else {
            final wIdx = allWhite.indexOf(midi);
            x = wIdx < 0 ? 0 : wIdx * effectiveW;
          }
          final bool isActive = _scaleLoopRunning &&
              _scaleCurrentNote != null &&
              midi == _scaleCurrentNote &&
              (ascending ? _scaleLoopDirection > 0 : _scaleLoopDirection < 0);
          final Color bg = ascending
              ? (cross ? const Color(0xFFD42010) : const Color(0xFFE07818))
              : (cross ? const Color(0xFF3A3A8A) : const Color(0xFF4A6A8A));
          badges.add(
            Positioned(
              key: ValueKey<String>('${ascending ? 'a' : 'd'}-$midi-$i'),
              left: x + (effectiveW - badgeW) / 2,
              top: 1,
              child: Container(
                width: badgeW,
                height: 20,
                decoration: BoxDecoration(
                  color: isActive ? Colors.white : bg,
                  borderRadius: BorderRadius.circular(4),
                  border: isActive ? Border.all(color: bg, width: 2) : null,
                ),
                alignment: Alignment.center,
                child: Text(
                  '$finger',
                  style: TextStyle(
                    color: isActive ? bg : Colors.white,
                    fontWeight: FontWeight.w800,
                    fontSize: 11,
                  ),
                ),
              ),
            ),
          );
        }
        return badges;
      }

      Widget buildStrip(bool ascending) {
        final badgeStack = SizedBox(
          width: keyboardW,
          height: stripH,
          child: Stack(
            clipBehavior: Clip.none,
            children: buildBadges(ascending),
          ),
        );
        return SizedBox(
          width: viewportW,
          height: stripH,
          child: ClipRect(
            child: Opacity(
              opacity: showStrips ? 1.0 : 0.0,
              child: ListenableBuilder(
                listenable: _pianoScrollController,
                builder: (context, _) {
                  final offset = _pianoScrollController.hasClients
                      ? _pianoScrollController.offset
                      : 0.0;
                  return Transform.translate(
                    offset: Offset(-offset, 0),
                    child: badgeStack,
                  );
                },
              ),
            ),
          ),
        );
      }

      return Column(
        children: <Widget>[
          buildStrip(true),
          SizedBox(height: gap),
          Expanded(
            child: _buildPianoStrip(activeMidi, forcedWhiteW: effectiveW),
          ),
          SizedBox(height: gap),
          buildStrip(false),
        ],
      );
    });
  }


  Widget _buildPianoStrip(Set<int> activeMidi, {double? forcedWhiteW}) {
    final midiRange = List<int>.generate(
      _kPianoHighMidi - _kPianoLowMidi + 1,
      (i) => _kPianoLowMidi + i,
    );
    final whiteMidi = midiRange
        .where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12))
        .toList();
    final active = activeMidi.toSet();
    final extras = _instrumentExtrasForCurrentTab();
    final scaleRh = (_tabIndex == 3 ? _scaleRhNotes() : <int>[]).toSet();
    final chordGenPiano =
        (_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'piano';
    final chordRh = chordGenPiano && _generatedChordJson != null
        ? _extractMidiList(_generatedChordJson!, <String>['notes_midi'])
        : const <int>[];
    final chordLh = chordGenPiano
        ? chordRh
              .map((n) => n - 12)
              .where((n) => n >= _kPianoLowMidi)
              .toList()
        : const <int>[];
    final chordRhSet = chordRh.toSet();
    final chordLhSet = chordLh.toSet();
    final rhFinger = <int, int>{};
    final lhFinger = <int, int>{};
    if (chordRh.isNotEmpty) {
      final rhSorted = List<int>.from(chordRh)..sort();
      final rhTpl = _pianoFingeringRight(rhSorted.length);
      for (var i = 0; i < rhSorted.length; i += 1) {
        rhFinger[rhSorted[i]] = rhTpl[i];
      }
    }
    if (chordLh.isNotEmpty) {
      final lhSorted = List<int>.from(chordLh)..sort();
      final lhTpl = _pianoFingeringLeft(lhSorted.length);
      for (var i = 0; i < lhSorted.length; i += 1) {
        lhFinger[lhSorted[i]] = lhTpl[i];
      }
    }

    Widget marker({
      required double size,
      required Color color,
      required int digit,
      required double top,
      required double left,
    }) {
      return Positioned(
        left: left,
        top: top,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            border: Border.all(color: const Color(0xFFE9EDF2)),
          ),
          alignment: Alignment.center,
          child: Text(
            '$digit',
            style: TextStyle(
              color: const Color(0xFF11223A),
              fontWeight: FontWeight.w800,
              fontSize: size * 0.5,
            ),
          ),
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final viewportW = constraints.maxWidth;
        final viewportH = (constraints.maxHeight.isFinite
                ? constraints.maxHeight
                : _kPianoWhiteKeyHeight + 12)
            .clamp(0.0, _kPianoWhiteKeyHeight + 12);
        final metrics = _computePianoKeyMetrics(
          viewportW: viewportW,
          viewportH: viewportH,
          whiteKeyCount: whiteMidi.length,
        );
        final whiteW = forcedWhiteW ?? metrics.whiteW;
        final whiteH = forcedWhiteW != null
            ? (forcedWhiteW * _kPianoKeyAspect).clamp(0.0, viewportH)
            : metrics.whiteH;
        final blackW = whiteW * 0.64;
        final blackH = whiteH * 0.58;
        final keyboardW = whiteMidi.length * whiteW;
        final scrollable = forcedWhiteW != null
            ? (keyboardW > viewportW + 1)
            : metrics.scrollable;
        final whiteMarkerTop = whiteH * 0.63;
        final forbiddenTop = whiteH * 0.41;
        _syncPianoScrollToMiddleC(viewportW, whiteW, whiteMidi);

        double xForMidi(int midi) {
          final idx = whiteMidi.indexWhere((m) => m >= midi);
          final wIdx = idx < 0 ? whiteMidi.length - 1 : idx;
          return wIdx * whiteW;
        }

        return SizedBox(
          height: viewportH,
          width: viewportW,
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: const Color(0xFFE8ECF2),
              border: Border.all(color: const Color(0xFF3A4558)),
            ),
            child: Column(
              children: <Widget>[
                Expanded(
                  child: SingleChildScrollView(
                  controller: _pianoScrollController,
                  scrollDirection: Axis.horizontal,
                  physics: const BouncingScrollPhysics(
                    parent: AlwaysScrollableScrollPhysics(),
                  ),
                  child: SizedBox(
                    width: keyboardW,
                    height: whiteH,
                    child: Stack(
                      children: <Widget>[
                        Row(
                          children: whiteMidi.map((midi) {
                      final isActive = active.contains(midi);
                      final isExtra = extras.contains(midi);
                      final isScaleCurrent =
                          _tabIndex == 3 &&
                          _scaleCurrentNote != null &&
                          _scaleCurrentNote == midi;
                      final rh = rhFinger[midi];
                      final lh = lhFinger[midi];
                      final genKeyHi = chordGenPiano &&
                          _generatedChordJson != null &&
                          _generationPianoHighlightMidi == midi;
                      final inChordRh = chordRhSet.contains(midi);
                      final inChordLhOnly =
                          chordLhSet.contains(midi) && !chordRhSet.contains(midi);
                      return Listener(
                        behavior: HitTestBehavior.opaque,
                        onPointerDown: (event) => unawaited(
                          _beginInputDrag(midi, event.pointer, event.position),
                        ),
                        onPointerUp: (event) => _endInputDrag(event.pointer),
                        onPointerCancel: (event) =>
                            _endInputDrag(event.pointer),
                        child: Container(
                          width: whiteW,
                          height: whiteH,
                          decoration: BoxDecoration(
                            color: chordGenPiano && _generatedChordJson != null
                                ? (inChordRh
                                      ? (genKeyHi
                                            ? const Color(0xFF2878C8)
                                            : const Color(0xFF4DA3EA))
                                      : inChordLhOnly
                                          ? (genKeyHi
                                                ? const Color(0xFFCC5A00)
                                                : const Color(0xFFFF8A2B))
                                          : (isScaleCurrent
                                                ? const Color(0xFF4DA3EA)
                                                : (isExtra
                                                      ? const Color(
                                                          0xFFE04A4A,
                                                        )
                                                      : (isActive
                                                            ? const Color(
                                                                0xFFF3C64F,
                                                              )
                                                            : const Color(
                                                                0xFFF5F4EF,
                                                              )))))
                                : isScaleCurrent
                                    ? const Color(0xFF4DA3EA)
                                    : (isExtra
                                          ? const Color(0xFFE04A4A)
                                          : (scaleRh.contains(midi)
                                                ? const Color(0xFFF5F4EF)
                                                : (isActive
                                                      ? const Color(0xFFF3C64F)
                                                      : const Color(0xFFF5F4EF)))),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: genKeyHi
                                  ? const Color(0xFFF3BF2F)
                                  : chordGenPiano &&
                                          _generatedChordJson != null &&
                                          (inChordRh || inChordLhOnly)
                                      ? (inChordLhOnly
                                            ? const Color(0xFFC8772F)
                                            : const Color(0xFF2B6DA6))
                                      : const Color(0xFFAEB8C5),
                              width: genKeyHi ? 2.5 : 1,
                            ),
                          ),
                          child: Stack(
                            children: <Widget>[
                              if (_showKeyNames)
                                Align(
                                  alignment: Alignment.bottomCenter,
                                  child: Padding(
                                    padding: const EdgeInsets.only(bottom: 6),
                                    child: Text.rich(
                                      TextSpan(
                                        children: _splitPitchClassLabelSpans(
                                          _pcLabel(midi % 12),
                                          const TextStyle(
                                            color: Color(0xFF1A222D),
                                            fontWeight: FontWeight.w700,
                                            fontSize: 11,
                                          ),
                                        ),
                                      ),
                                      maxLines: 1,
                                      softWrap: false,
                                    ),
                                  ),
                                ),
                              if (_tabIndex == 3 && scaleRh.contains(midi))
                                Builder(builder: (context) {
                                  final isTonic = (midi % 12) == (_scaleTonicPc % 12);
                                  return Positioned(
                                    top: whiteMarkerTop,
                                    left: (whiteW - 22) / 2,
                                    child: Container(
                                      width: 22,
                                      height: 22,
                                      decoration: BoxDecoration(
                                        color: isTonic
                                            ? const Color(0xFF32D74B)
                                            : const Color(0xFFF6B60B),
                                        shape: BoxShape.circle,
                                        border: Border.all(
                                          color: isTonic
                                              ? const Color(0xFF1E8C38)
                                              : const Color(0xFF8D6B00),
                                          width: 1.5,
                                        ),
                                      ),
                                      alignment: Alignment.center,
                                      child: FittedBox(
                                        fit: BoxFit.scaleDown,
                                        child: Text(
                                          _pcLabel(midi % 12),
                                          style: const TextStyle(
                                            color: Color(0xFF101010),
                                            fontWeight: FontWeight.w700,
                                            fontSize: 9,
                                          ),
                                        ),
                                      ),
                                    ),
                                  );
                                }),
                              if (chordGenPiano && rh != null)
                                marker(
                                  size: 22,
                                  color: const Color(0xFF33C6FF),
                                  digit: rh,
                                  top: whiteMarkerTop,
                                  left: (whiteW - 22) / 2,
                                ),
                              if (chordGenPiano && rh == null && lh != null)
                                marker(
                                  size: 22,
                                  color: const Color(0xFFFF9E34),
                                  digit: lh,
                                  top: whiteMarkerTop,
                                  left: (whiteW - 22) / 2,
                                ),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  ...midiRange
                      .where(
                        (m) => const <int>{1, 3, 6, 8, 10}.contains(m % 12),
                      )
                      .map((midi) {
                        final isActive = active.contains(midi);
                        final isExtra = extras.contains(midi);
                        final isScaleCurrent =
                            _tabIndex == 3 &&
                            _scaleCurrentNote != null &&
                            _scaleCurrentNote == midi;
                        final rh = rhFinger[midi];
                        final lh = lhFinger[midi];
                        final genKeyHi = chordGenPiano &&
                            _generatedChordJson != null &&
                            _generationPianoHighlightMidi == midi;
                        final inChordRh = chordRhSet.contains(midi);
                        final inChordLhOnly =
                            chordLhSet.contains(midi) && !chordRhSet.contains(midi);
                        return Positioned(
                          left: xForMidi(midi) - (blackW / 2),
                          top: 0,
                          child: Listener(
                            behavior: HitTestBehavior.opaque,
                            onPointerDown: (event) => unawaited(
                              _beginInputDrag(
                                midi,
                                event.pointer,
                                event.position,
                              ),
                            ),
                            onPointerUp: (event) =>
                                _endInputDrag(event.pointer),
                            onPointerCancel: (event) =>
                                _endInputDrag(event.pointer),
                            child: Container(
                              width: blackW,
                              height: blackH,
                              decoration: BoxDecoration(
                                color: chordGenPiano && _generatedChordJson != null
                                    ? (inChordRh
                                          ? (genKeyHi
                                                ? const Color(0xFF005CA6)
                                                : const Color(0xFF0078D7))
                                          : inChordLhOnly
                                              ? (genKeyHi
                                                    ? const Color(0xFFCC5A00)
                                                    : const Color(0xFFFF8A2B))
                                              : (isScaleCurrent
                                                    ? const Color(0xFF0078D7)
                                                    : (isExtra
                                                          ? const Color(
                                                              0xFFB33434,
                                                            )
                                                          : (isActive
                                                                ? const Color(
                                                                    0xFFC37B00,
                                                                  )
                                                                : const Color(
                                                                    0xFF101822,
                                                                  )))))
                                    : isScaleCurrent
                                        ? const Color(0xFF0078D7)
                                        : (isExtra
                                              ? const Color(0xFFB33434)
                                              : (scaleRh.contains(midi)
                                                    ? const Color(0xFF101822)
                                                    : (isActive
                                                          ? const Color(0xFFC37B00)
                                                          : const Color(0xFF101822)))),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: genKeyHi
                                      ? const Color(0xFFF3BF2F)
                                      : chordGenPiano &&
                                              _generatedChordJson != null &&
                                              (inChordRh || inChordLhOnly)
                                          ? (inChordLhOnly
                                                ? const Color(0xFF7A3D00)
                                                : const Color(0xFF005CA6))
                                          : const Color(0xFF6F7F96),
                                  width: genKeyHi ? 2.5 : 1,
                                ),
                              ),
                              child: Stack(
                                children: <Widget>[
                                  if (_showKeyNames)
                                    Align(
                                      alignment: Alignment.bottomCenter,
                                      child: Padding(
                                        padding: const EdgeInsets.only(bottom: 4),
                                        child: SizedBox(
                                          width: blackW - 4,
                                          child: FittedBox(
                                            fit: BoxFit.scaleDown,
                                            child: Text.rich(
                                              TextSpan(
                                                children: _splitPitchClassLabelSpans(
                                                  _pcLabel(midi % 12),
                                                  const TextStyle(
                                                    color: Colors.white,
                                                    fontWeight: FontWeight.w700,
                                                    fontSize: 9,
                                                  ),
                                                ),
                                              ),
                                              maxLines: 1,
                                              softWrap: false,
                                            ),
                                          ),
                                        ),
                                    ),
                                  ),
                                  if (_tabIndex == 3 && scaleRh.contains(midi))
                                    Builder(builder: (context) {
                                      final isTonic = (midi % 12) == (_scaleTonicPc % 12);
                                      return Positioned(
                                        top: blackH * 0.5,
                                        left: (blackW - 18) / 2,
                                        child: Container(
                                          width: 18,
                                          height: 18,
                                          decoration: BoxDecoration(
                                            color: isTonic
                                                ? const Color(0xFF32D74B)
                                                : const Color(0xFFF6B60B),
                                            shape: BoxShape.circle,
                                            border: Border.all(
                                              color: isTonic
                                                  ? const Color(0xFF1E8C38)
                                                  : const Color(0xFF8D6B00),
                                              width: 1.5,
                                            ),
                                          ),
                                          alignment: Alignment.center,
                                          child: FittedBox(
                                            fit: BoxFit.scaleDown,
                                            child: Text(
                                              _pcLabel(midi % 12),
                                              style: const TextStyle(
                                                color: Color(0xFF101010),
                                                fontWeight: FontWeight.w700,
                                                fontSize: 8,
                                              ),
                                            ),
                                          ),
                                        ),
                                      );
                                    }),
                                  if (chordGenPiano && rh != null)
                                    marker(
                                      size: 18,
                                      color: const Color(0xFF33C6FF),
                                      digit: rh,
                                      top: 10,
                                      left: (blackW - 18) / 2,
                                    ),
                                  if (chordGenPiano && rh == null && lh != null)
                                    marker(
                                      size: 18,
                                      color: const Color(0xFFFF9E34),
                                      digit: lh,
                                      top: 10,
                                      left: (blackW - 18) / 2,
                                    ),
                                ],
                              ),
                            ),
                          ),
                        );
                      }),
                  ..._forbiddenFlashNotes.map((midi) {
                    return Positioned(
                      left: xForMidi(midi),
                      top: forbiddenTop,
                      child: const Text(
                        '⊘',
                        style: TextStyle(
                          color: Color(0xFFFF5A5A),
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    );
                  }),
                      ],
                    ),
                  ),
                ),
              ),
              if (scrollable)
                SizedBox(
                  height: 8,
                  child: RawScrollbar(
                    controller: _pianoScrollController,
                    thumbVisibility: true,
                    thickness: 5,
                    radius: const Radius.circular(3),
                    thumbColor: const Color(0xFF6B7A99),
                    child: const SizedBox.expand(),
                  ),
                ),
            ],
          ),
        ),
      );
      },
    );
  }

  Widget _buildGuitarStrip(
    Set<int> activeMidi, {
    List<List<int>> chordVoicings = const <List<int>>[],
    List<Map<String, dynamic>> chordVariations = const <Map<String, dynamic>>[],
    int chordVariant = 0,
  }) {
    final activePcs = activeMidi.map((n) => n % 12).toSet();
    final extraPcs = _instrumentExtrasForCurrentTab()
        .map((n) => n % 12)
        .toSet();
    final leftHanded = _guitarHandedness == 'left';
    const physicalTuning = <int>[40, 45, 50, 55, 59, 64]; // 6 -> 1
    final tuning = !leftHanded
        ? physicalTuning.reversed
              .toList() // 1 -> 6 (arriba -> abajo)
        : physicalTuning;
    const fretCount = 14;
    const fretW = 78.0;
    const openFretW = fretW / 2;
    const stringGap = 25.0;
    final detectionMode = _tabIndex == 0;
    final chordMode = _tabIndex == 1 || _tabIndex == 2;
    final selectedVariation = chordVariations.isEmpty
        ? null
        : chordVariations[chordVariant.clamp(0, chordVariations.length - 1)];
    final selectedVoicing = chordVoicings.isEmpty
        ? const <int>[]
        : chordVoicings[chordVariant.clamp(0, chordVoicings.length - 1)];
    final rawFrets =
        (selectedVariation?['frets'] as List<dynamic>? ?? const <dynamic>[])
            .map((v) => v is num ? v.toInt() : int.tryParse('$v'))
            .whereType<int>()
            .toList();
    final selectedFrets = !leftHanded
        ? rawFrets.reversed.toList()
        : rawFrets;
    final useFrets = selectedFrets.length >= 6;
    const openLeft = 40.0;
    final openRight = openLeft + openFretW;
    final boardWidth = (fretCount - 1) * fretW;
    final width = openRight + boardWidth;
    final boardLeft = leftHanded ? openLeft : openRight;
    final boardRight = leftHanded ? width - openFretW : width;
    final openAreaLeft = leftHanded ? width - openFretW : openLeft;
    final stringLabelLeft = leftHanded ? width + 4 : 0.0;

    double fretLineX(int fretIndex) {
      if (leftHanded) {
        return boardRight - (fretIndex * fretW);
      }
      return openRight + (fretIndex * fretW);
    }

    double noteCenterX(int fret) {
      if (fret == 0) {
        return leftHanded
            ? openAreaLeft + (openFretW * 0.5)
            : openLeft + (openFretW * 0.5);
      }
      if (leftHanded) {
        return boardRight - ((fret - 0.5) * fretW);
      }
      return openRight + ((fret - 0.5) * fretW);
    }

    return SizedBox(
      height: 186,
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF0F1621),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFF3A4558)),
        ),
        child: SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: SizedBox(
            width: width + 48,
            child: Stack(
              children: <Widget>[
                Positioned(
                  left: leftHanded ? openLeft : openLeft,
                  top: 6,
                  right: 0,
                  child: SizedBox(
                    width: width - openLeft,
                    child: Row(
                      children: <Widget>[
                        ...List<Widget>.generate(fretCount, (i) {
                          final fret = leftHanded ? fretCount - 1 - i : i;
                          return SizedBox(
                            width: fret == 0 ? openFretW : fretW,
                            child: Text(
                              '$fret',
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontSize: 10,
                                color: Color(0xFFC9D4E4),
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  left: openAreaLeft,
                  top: 20,
                  child: Container(
                    width: openFretW,
                    height: (6 * stringGap) + 16,
                    color: const Color(0xFFF4F5F7),
                  ),
                ),
                Positioned(
                  left: boardLeft,
                  top: 20,
                  child: Container(
                    width: boardWidth,
                    height: (6 * stringGap) + 16,
                    color: const Color(0xFF34363C),
                  ),
                ),
                ...List<Widget>.generate(6, (s) {
                  final y = 32.0 + (s * stringGap);
                  final open = tuning[s];
                  return Positioned(
                    left: stringLabelLeft,
                    top: y - 7,
                    child: SizedBox(
                      width: 36,
                      child: Text(
                        _pcLabel(open % 12),
                        textAlign: leftHanded ? TextAlign.left : TextAlign.right,
                        style: const TextStyle(
                          color: Color(0xFFE9EDF2),
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  );
                }),
                ...List<Widget>.generate(6, (s) {
                  final y = 32.0 + (s * stringGap);
                  return Positioned(
                    left: openLeft,
                    top: y,
                    child: Container(
                      width: width - openLeft,
                      height: 2,
                      color: const Color(0xFF8FA0B8),
                    ),
                  );
                }),
                ...List<Widget>.generate(fretCount, (f) {
                  return Positioned(
                    left: fretLineX(f),
                    top: 28,
                    child: Container(
                      width: f == 0 ? 4 : 2,
                      height: 6 * stringGap,
                      color: const Color(0xFFC0AE94),
                    ),
                  );
                }),
                ...List<int>.generate(6, (s) => s).expand((s) {
                  return List<Widget>.generate(fretCount, (f) {
                    final note = tuning[s] + f;
                    final y = 32.0 + (s * stringGap) - 10;
                    final x = noteCenterX(f) - 11;
                    final selectedFret = s < selectedFrets.length
                        ? selectedFrets[s]
                        : -999;
                    final active = chordMode
                        ? (useFrets
                              ? (selectedFret >= 0 && f == selectedFret)
                              : selectedVoicing.contains(note))
                        : activePcs.contains(note % 12);
                    final isExtra = extraPcs.contains(note % 12);
                    final showDot = detectionMode || active;
                    return Positioned(
                      left: x,
                      top: y,
                      child: Listener(
                        onPointerDown: showDot
                            ? (event) => unawaited(
                                _beginInputDrag(
                                  note,
                                  event.pointer,
                                  event.position,
                                ),
                              )
                            : null,
                        onPointerMove: showDot
                            ? (event) => unawaited(
                                _updateInputDrag(
                                  note,
                                  event.pointer,
                                  event.position,
                                ),
                              )
                            : null,
                        onPointerUp: showDot
                            ? (event) => _endInputDrag(event.pointer)
                            : null,
                        onPointerCancel: showDot
                            ? (event) => _endInputDrag(event.pointer)
                            : null,
                        child: Container(
                          width: 22,
                          height: 22,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: active
                                ? (isExtra
                                      ? const Color(0xFFE04A4A)
                                      : const Color(0xFFF3BF2F))
                                : (showDot
                                      ? const Color(0xFFE5E7EB)
                                      : Colors.transparent),
                            border: showDot
                                ? Border.all(
                                    color: active
                                        ? (isExtra
                                              ? const Color(0xFFB33434)
                                              : const Color(0xFFD29B20))
                                        : const Color(0xFFAAB1BC),
                                  )
                                : null,
                          ),
                          child: _forbiddenFlashNotes.contains(note)
                              ? const Text(
                                  '⊘',
                                  style: TextStyle(
                                    color: Color(0xFFFF5A5A),
                                    fontSize: 13,
                                    fontWeight: FontWeight.w800,
                                  ),
                                )
                              : (showDot
                                    ? Text(
                                        active
                                            ? _pcLabel(note % 12)
                                            : (detectionMode ? '•' : ''),
                                        style: TextStyle(
                                          color: active
                                              ? (isExtra
                                                    ? const Color(0xFFFCECEC)
                                                    : const Color(0xFF1A222D))
                                              : const Color(0xFF7D8797),
                                          fontSize: 10,
                                          fontWeight: FontWeight.w700,
                                        ),
                                      )
                                    : null),
                        ),
                      ),
                    );
                  });
                }),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildDetectionPage() {
    final hasNotes = _hasDetectionNotes;
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          final resultHeight = compactLandscape
              ? math.max(132.0, constraints.maxHeight - 116.0)
              : _compactResultHeight(constraints, minHeight: 140);
          final content = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
          Text(
            _ui('Detección de acordes', 'Chord detection'),
            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: <Widget>[
              _helpAnchor(
                'detection_play_button',
                _holdPlayButton(
                  enabled: hasNotes,
                  active: _detectionPlayPressed,
                  label: null,
                  onDown: () async {
                    final notes = _activeDetectionNotes.toList()..sort();
                    if (notes.isEmpty) return;
                    setState(() {
                      _detectionPlayPressed = true;
                      _detectionPlayHeldNotes
                        ..clear()
                        ..addAll(notes);
                    });
                    await _startHeldChord(notes, instrument: 'piano');
                  },
                  onUp: () {
                    _stopHeldChord();
                    if (mounted) {
                      setState(() {
                        _detectionPlayPressed = false;
                        _detectionPlayHeldNotes.clear();
                      });
                    }
                  },
                ),
              ),
              _helpAnchor(
                'detection_clear_button',
                OutlinedButton.icon(
                  onPressed: !hasNotes
                      ? null
                      : () {
                          setState(() => _detectionSelectedNotes.clear());
                          _detectionMidiHeldNotes.clear();
                          _stopHeldMidiInputs();
                          if (!_requestInFlight) {
                            unawaited(_callDetect());
                          }
                        },
                  icon: const Icon(Icons.clear_all),
                  label: Text(_ui('Limpiar', 'Clear')),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (compactPhone)
            SizedBox(
              height: resultHeight,
              child: _buildDetectionResultBlock(),
            )
          else
            Expanded(child: _buildDetectionResultBlock()),
        ],
          );
          if (!compactLandscape) {
            return content;
          }
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: content,
            ),
          );
        },
      ),
    );
  }

  Widget _buildChordGenerationPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          final resultHeight = compactLandscape
              ? math.max(84.0, constraints.maxHeight - 156.0)
              : _compactResultHeight(constraints);
          final compactGenerationLayout = compactPhone && constraints.maxWidth < 700;
          final content = Column(
        children: <Widget>[
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              _ui('Generación de acordes', 'Chord generation'),
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
            ),
          ),
          const SizedBox(height: 8),
          if (compactGenerationLayout)
            Column(
              children: <Widget>[
                Row(
                  children: <Widget>[
                    _helpAnchor(
                      'generation_play_button',
                      _holdPlayButton(
                      enabled:
                          _generatedChordJson != null &&
                          _extractMidiList(_generatedChordJson!, <String>[
                            'notes_midi',
                          ]).isNotEmpty,
                      active: _generationPlayPressed,
                      label: null,
                      onDown: () async {
                        final notes = <int>[
                          if (_generatedChordJson != null) ...(_instrumentView == 'guitar'
                              ? _selectedChordGuitarNotes()
                              : _extractMidiList(_generatedChordJson!, <String>[
                                  'notes_midi',
                                ])),
                        ]..sort();
                        if (notes.isEmpty) return;
                        setState(() => _generationPlayPressed = true);
                        await _startHeldChord(
                          notes,
                          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
                        );
                      },
                      onUp: () {
                        _stopHeldChord();
                        if (mounted) {
                          setState(() => _generationPlayPressed = false);
                        }
                      },
                    ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _helpAnchor(
                        'generation_tonic',
                        DropdownButtonFormField<int>(
                        key: ValueKey<int>(_chordRootPc),
                        initialValue: _chordRootPc,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: InputDecoration(labelText: _ui('Tónica', 'Tonic')),
                        items: List<DropdownMenuItem<int>>.generate(
                          12,
                          (index) => DropdownMenuItem<int>(
                            value: index,
                            child: Text(_pcLabel(index)),
                          ),
                        ),
                        onChanged: (value) {
                          if (value == null) {
                            return;
                          }
                          setState(() => _chordRootPc = value);
                          if (!_requestInFlight) {
                            unawaited(_callGenerateChord());
                          }
                        },
                      ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    Expanded(
                      flex: 2,
                      child: _helpAnchor(
                        'generation_variant',
                        DropdownButtonFormField<String>(
                        key: ValueKey<String>('suffix_$_chordSuffix'),
                        initialValue: _chordSuffix,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: InputDecoration(labelText: _ui('Variante', 'Variant')),
                        items: _chordPatterns
                            .map(
                              (p) => DropdownMenuItem<String>(
                                value: (p['suffix'] as String? ?? ''),
                                child: Text(
                                  (p['suffix'] as String? ?? '').isEmpty
                                      ? 'maj'
                                      : (p['suffix'] as String? ?? ''),
                                ),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value == null) {
                            return;
                          }
                          setState(() {
                            _chordSuffix = value;
                            _recomputeMaxInversion();
                          });
                          if (!_requestInFlight) {
                            unawaited(_callGenerateChord());
                          }
                        },
                      ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _helpAnchor(
                        'generation_inversion',
                        DropdownButtonFormField<int>(
                        key: ValueKey<String>(
                          'inv_$_chordInversion/$_chordMaxInversion',
                        ),
                        initialValue: _chordInversion.clamp(0, _chordMaxInversion),
                        isExpanded: true,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: InputDecoration(labelText: _ui('Inversión', 'Inversion')),
                        items: List<DropdownMenuItem<int>>.generate(
                          _chordMaxInversion + 1,
                          (i) => DropdownMenuItem<int>(
                            value: i,
                            child: Text(_inversionLabel(i)),
                          ),
                        ),
                        selectedItemBuilder: (context) => List<Widget>.generate(
                          _chordMaxInversion + 1,
                          (i) => Align(
                            alignment: Alignment.centerLeft,
                            child: Text(
                              _inversionLabel(i, compact: true),
                              overflow: TextOverflow.ellipsis,
                              maxLines: 1,
                            ),
                          ),
                        ),
                        onChanged: _instrumentView == 'guitar'
                            ? null
                            : (value) {
                                if (value == null) return;
                                setState(() => _chordInversion = value);
                                if (!_requestInFlight) {
                                  unawaited(_callGenerateChord());
                                }
                              },
                      ),
                      ),
                    ),
                  ],
                ),
              ],
            )
          else
            Row(
              children: <Widget>[
                Expanded(
                  child: _helpAnchor(
                    'generation_tonic',
                    DropdownButtonFormField<int>(
                    key: ValueKey<int>(_chordRootPc),
                    initialValue: _chordRootPc,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: InputDecoration(labelText: _ui('Tónica', 'Tonic')),
                    items: List<DropdownMenuItem<int>>.generate(
                      12,
                      (index) => DropdownMenuItem<int>(
                        value: index,
                        child: Text(_pcLabel(index)),
                      ),
                    ),
                    onChanged: (value) {
                      if (value == null) {
                        return;
                      }
                      setState(() => _chordRootPc = value);
                      if (!_requestInFlight) {
                        unawaited(_callGenerateChord());
                      }
                    },
                  ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  flex: 2,
                  child: _helpAnchor(
                    'generation_variant',
                    DropdownButtonFormField<String>(
                    key: ValueKey<String>('suffix_$_chordSuffix'),
                    initialValue: _chordSuffix,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: InputDecoration(labelText: _ui('Variante', 'Variant')),
                    items: _chordPatterns
                        .map(
                          (p) => DropdownMenuItem<String>(
                            value: (p['suffix'] as String? ?? ''),
                            child: Text(
                              (p['suffix'] as String? ?? '').isEmpty
                                  ? 'maj'
                                  : (p['suffix'] as String? ?? ''),
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (value) {
                      if (value == null) {
                        return;
                      }
                      setState(() {
                        _chordSuffix = value;
                        _recomputeMaxInversion();
                      });
                      if (!_requestInFlight) {
                        unawaited(_callGenerateChord());
                      }
                    },
                  ),
                  ),
                ),
              ],
            ),
          const SizedBox(height: 12),
          if (!compactGenerationLayout) ...<Widget>[
            Row(
              children: <Widget>[
                Expanded(
                  child: _helpAnchor(
                    'generation_inversion',
                    DropdownButtonFormField<int>(
                    key: ValueKey<String>(
                      'inv_$_chordInversion/$_chordMaxInversion',
                    ),
                    initialValue: _chordInversion.clamp(0, _chordMaxInversion),
                    isExpanded: true,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: InputDecoration(labelText: _ui('Inversión', 'Inversion')),
                    items: List<DropdownMenuItem<int>>.generate(
                      _chordMaxInversion + 1,
                      (i) => DropdownMenuItem<int>(
                        value: i,
                        child: Text(_inversionLabel(i)),
                      ),
                    ),
                    selectedItemBuilder: (context) => List<Widget>.generate(
                      _chordMaxInversion + 1,
                      (i) => Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          _inversionLabel(i, compact: true),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                      ),
                    ),
                    onChanged: _instrumentView == 'guitar'
                        ? null
                        : (value) {
                            if (value == null) return;
                            setState(() => _chordInversion = value);
                            if (!_requestInFlight) {
                              unawaited(_callGenerateChord());
                            }
                          },
                  ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerLeft,
              child: _helpAnchor(
                'generation_play_button',
                _holdPlayButton(
                enabled:
                    _generatedChordJson != null &&
                    _extractMidiList(_generatedChordJson!, <String>[
                      'notes_midi',
                    ]).isNotEmpty,
                active: _generationPlayPressed,
                label: null,
                onDown: () async {
                  final notes = <int>[
                    if (_generatedChordJson != null) ...(_instrumentView == 'guitar'
                        ? _selectedChordGuitarNotes()
                        : _extractMidiList(_generatedChordJson!, <String>[
                            'notes_midi',
                          ])),
                  ]..sort();
                  if (notes.isEmpty) return;
                  setState(() => _generationPlayPressed = true);
                  await _startHeldChord(
                    notes,
                    instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
                  );
                },
                onUp: () {
                  _stopHeldChord();
                  if (mounted) {
                    setState(() => _generationPlayPressed = false);
                  }
                },
              ),
              ),
            ),
          ],
          const SizedBox(height: 8),
          if (compactPhone)
            SizedBox(
              height: resultHeight,
              child: _buildChordResultBlock(),
            )
          else
            Expanded(child: _buildChordResultBlock()),
        ],
          );
          if (!compactLandscape) {
            return content;
          }
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: content,
            ),
          );
        },
      ),
    );
  }

  Widget _buildCircleOfFifthsPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final circleBox = math.min(
            520.0,
            math.max(
              200.0,
              math.min(constraints.maxWidth, constraints.maxHeight),
            ),
          );
          final media = MediaQuery.of(context);
          final dpr = media.devicePixelRatio;
          final circleStack = Stack(
            children: <Widget>[
              Positioned.fill(
                child: LayoutBuilder(
                  builder: (context, c) {
                    final sz = Size(c.maxWidth, c.maxHeight);
                    Offset? downLocal;
                    return GestureDetector(
                      onTapDown: (TapDownDetails d) =>
                          downLocal = d.localPosition,
                      onTap: () {
                        if (downLocal != null) {
                          _onCircleCanvasInteraction(
                            downLocal!,
                            sz,
                            longPress: false,
                          );
                        }
                      },
                      onLongPress: () {
                        if (downLocal != null) {
                          _onCircleCanvasInteraction(
                            downLocal!,
                            sz,
                            longPress: true,
                          );
                        }
                      },
                      child: CustomPaint(
                        painter: CircleOfFifthsPainter(
                          devicePixelRatio: dpr,
                          circleTonicPc: _circleTonicPc,
                          circleKeyMode: _circleKeyMode,
                          circleChordRootPc: _circleChordRootPc,
                          generatedChord: _generatedChordJson,
                          noteNameFromPc: _pcLabel,
                        ),
                        child: const SizedBox.expand(),
                      ),
                    );
                  },
                ),
              ),
              Positioned(
                top: 4,
                left: 4,
                child: _helpAnchor(
                  'circle_play',
                  _holdPlayButton(
                    enabled: _generatedChordJson != null &&
                        _extractMidiList(
                          _generatedChordJson!,
                          <String>['notes_midi'],
                        ).isNotEmpty,
                    active: _generationPlayPressed,
                    label: null,
                    onDown: () async {
                      final notes = <int>[
                        if (_generatedChordJson != null)
                          ...(_instrumentView == 'guitar'
                              ? _selectedChordGuitarNotes()
                              : _extractMidiList(
                                  _generatedChordJson!,
                                  <String>['notes_midi'],
                                )),
                      ]..sort();
                      if (notes.isEmpty) return;
                      setState(() => _generationPlayPressed = true);
                      await _startHeldChord(
                        notes,
                        instrument: _instrumentView == 'guitar'
                            ? 'guitar'
                            : 'piano',
                      );
                    },
                    onUp: () {
                      _stopHeldChord();
                      if (mounted) {
                        setState(() => _generationPlayPressed = false);
                      }
                    },
                  ),
                ),
              ),
            ],
          );
          final content = Center(
            child: _helpAnchor(
              'circle_canvas',
              SizedBox(
                width: circleBox,
                height: circleBox,
                child: circleStack,
              ),
            ),
          );
          if (compactPhone) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: content,
            );
          }
          return SizedBox(
            height: constraints.maxHeight,
            child: content,
          );
        },
      ),
    );
  }

  Widget _buildScaleGenerationPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          final metroLabelWidth = compact ? 96.0 : 110.0;
          final resultHeight = _scaleMetronomeOnly
              ? math.max(80.0, constraints.maxHeight - 310.0)
              : math.max(80.0, constraints.maxHeight - 270.0);
          final filteredPatterns = _getFilteredScalePatterns();
          // Ensure current pattern is valid for current filter
          final currentPatternValid = filteredPatterns.any(
            (p) => (p['name'] as String?) == _scalePatternName,
          );

          return Scrollbar(
            thumbVisibility: true,
            child: SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                const SizedBox(height: 8),
                // Row 1: Tonic selector
                _helpAnchor(
                  'scales_tonic',
                  DropdownButtonFormField<int>(
                    key: ValueKey<int>(100 + _scaleTonicPc),
                    initialValue: _scaleTonicPc,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: InputDecoration(labelText: _ui('Tónica', 'Tonic')),
                    items: List<DropdownMenuItem<int>>.generate(
                      12,
                      (index) => DropdownMenuItem<int>(
                        value: index,
                        child: Text(_pcLabel(index)),
                      ),
                    ),
                    onChanged: (value) {
                      if (value == null) return;
                      setState(() => _scaleTonicPc = value);
                      if (!_requestInFlight) unawaited(_callGenerateScale());
                    },
                  ),
                ),
                const SizedBox(height: 6),
                // Row 2: Scale type + Básicas/Todas toggle
                Row(
                  children: <Widget>[
                    Expanded(
                      child: _helpAnchor(
                        'scales_pattern',
                        DropdownButtonFormField<String>(
                          key: ValueKey<String>(
                            'scale_${_scalePatternName}_${_scaleFilterMode}',
                          ),
                          initialValue: currentPatternValid
                              ? _scalePatternName
                              : (filteredPatterns.isNotEmpty
                                  ? (filteredPatterns.first['name'] as String? ?? 'Ionian')
                                  : 'Ionian'),
                          isExpanded: true,
                          dropdownColor: _surfaceDark,
                          style: const TextStyle(color: _text),
                          decoration: InputDecoration(labelText: _ui('Tipo', 'Type')),
                          items: filteredPatterns
                              .map(
                                (p) => DropdownMenuItem<String>(
                                  value: (p['name'] as String? ?? 'Ionian'),
                                  child: Text(
                                    (p['localized_name'] as String? ??
                                        p['name'] as String? ??
                                        'Ionian'),
                                    overflow: TextOverflow.ellipsis,
                                    maxLines: 1,
                                  ),
                                ),
                              )
                              .toList(),
                          selectedItemBuilder: (context) => filteredPatterns
                              .map(
                                (p) => Align(
                                  alignment: Alignment.centerLeft,
                                  child: Text(
                                    (p['localized_name'] as String? ??
                                        p['name'] as String? ??
                                        'Ionian'),
                                    overflow: TextOverflow.ellipsis,
                                    maxLines: 1,
                                  ),
                                ),
                              )
                              .toList(),
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _scalePatternName = value);
                            if (!_requestInFlight) unawaited(_callGenerateScale());
                          },
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    _helpAnchor(
                      'scales_filter',
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          backgroundColor: _scaleFilterMode == 'basic'
                              ? _accent
                              : _surfaceDark,
                          foregroundColor: _scaleFilterMode == 'basic'
                              ? const Color(0xFF1A222D)
                              : _text,
                          side: BorderSide(
                            color: _scaleFilterMode == 'basic' ? _accent : _border,
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                        ),
                        onPressed: () {
                          setState(() {
                            _scaleFilterMode =
                                _scaleFilterMode == 'basic' ? 'all' : 'basic';
                          });
                        },
                        child: Text(
                          _scaleFilterMode == 'basic'
                              ? _ui('Básicas', 'Basic')
                              : _ui('Todas', 'All'),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                // Row 3: Play + Metro buttons (left) + Octaves selector (right)
                Row(
                  children: <Widget>[
                    _helpAnchor(
                      'scales_play_button',
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          backgroundColor: _scaleLoopRunning ? _accent : _surfaceDark,
                          foregroundColor: _scaleLoopRunning
                              ? const Color(0xFF1A222D)
                              : _text,
                          side: BorderSide(
                            color: _scaleLoopRunning ? _accent : _border,
                          ),
                          padding: const EdgeInsets.all(10),
                          minimumSize: const Size(40, 40),
                        ),
                        onPressed: _toggleScaleLoop,
                        child: Icon(
                          _scaleLoopRunning ? Icons.stop : Icons.play_arrow,
                          size: 20,
                        ),
                      ),
                    ),
                    const SizedBox(width: 6),
                    _helpAnchor(
                      'scales_metronome_only',
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          backgroundColor: _scaleMetronomeOnly ? _accent : _surfaceDark,
                          foregroundColor: _scaleMetronomeOnly
                              ? const Color(0xFF1A222D)
                              : _text,
                          side: BorderSide(
                            color: _scaleMetronomeOnly ? _accent : _border,
                          ),
                          padding: const EdgeInsets.all(10),
                          minimumSize: const Size(40, 40),
                        ),
                        onPressed: () =>
                            setState(() => _scaleMetronomeOnly = !_scaleMetronomeOnly),
                        child: const Text('⏱', style: TextStyle(fontSize: 16)),
                      ),
                    ),
                    const Spacer(),
                    // Octaves: 1 / 2 / 3 — only for piano
                    if (_instrumentView != 'guitar')
                    _helpAnchor(
                      'scales_octaves',
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          Text(
                            _ui('Octavas:', 'Octaves:'),
                            style: const TextStyle(color: _muted, fontSize: 12),
                          ),
                          const SizedBox(width: 4),
                          ...List<Widget>.generate(3, (i) {
                            final oct = i + 1;
                            final active = _scaleOctaves == oct;
                            return Padding(
                              padding: const EdgeInsets.only(left: 4),
                              child: SizedBox(
                                width: 32,
                                height: 32,
                                child: OutlinedButton(
                                  style: OutlinedButton.styleFrom(
                                    backgroundColor: active ? _accent : _surfaceDark,
                                    foregroundColor: active
                                        ? const Color(0xFF1A222D)
                                        : _text,
                                    side: BorderSide(
                                      color: active ? _accent : _border,
                                    ),
                                    padding: EdgeInsets.zero,
                                  ),
                                  onPressed: () {
                                    if (_scaleOctaves == oct) return;
                                    setState(() {
                                      _scaleOctaves = oct;
                                      _updateScaleFingeringsMap();
                                      _needsPianoScrollSync = true;
                                    });
                                    _savePrefs();
                                    if (_scaleLoopRunning) {
                                      _stopScaleLoop();
                                      unawaited(Future<void>.delayed(
                                        const Duration(milliseconds: 50),
                                        _toggleScaleLoop,
                                      ));
                                    }
                                  },
                                  child: Text('$oct', style: const TextStyle(fontSize: 13)),
                                ),
                              ),
                            );
                          }),
                        ],
                      ),
                    ),
                  ],
                ),
                if (_scaleMetronomeOnly) ...<Widget>[
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'scales_volume',
                    Row(
                      children: <Widget>[
                        SizedBox(
                          width: metroLabelWidth,
                          child: Text(
                            _ui('Volumen', 'Volume'),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(color: _muted),
                          ),
                        ),
                        Expanded(
                          child: Slider(
                            min: 0,
                            max: 100,
                            divisions: 100,
                            value: _metroVolume.toDouble(),
                            onChanged: (value) =>
                                setState(() => _metroVolume = value.round()),
                          ),
                        ),
                        SizedBox(
                          width: compact ? 72 : 80,
                          child: Text(
                            '$_metroVolume%',
                            textAlign: TextAlign.right,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 2),
                _helpAnchor(
                  'scales_bpm',
                  Row(
                    children: <Widget>[
                      SizedBox(
                        width: metroLabelWidth,
                        child: const Text('BPM', maxLines: 1, overflow: TextOverflow.ellipsis),
                      ),
                      Expanded(
                        child: Slider(
                          min: 1,
                          max: 300,
                          divisions: 299,
                          value: _scaleBpm.toDouble(),
                          onChanged: (value) =>
                              setState(() => _scaleBpm = value.round()),
                        ),
                      ),
                      SizedBox(
                        width: compact ? 92 : 100,
                        child: Text(
                          '$_scaleBpm BPM',
                          textAlign: TextAlign.right,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 6),
                ConstrainedBox(
                  constraints: BoxConstraints(maxHeight: resultHeight),
                  child: _buildScaleResultBlock(),
                ),
                if (_instrumentView != 'guitar') ...<Widget>[
                  const SizedBox(height: 10),
                  _helpAnchor('scales_fingering', _buildScaleFingeringRow()),
                ],
              ],
            ),
            ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildScaleFingeringRow() {
    const options = <(String, String, String)>[
      ('none',  'Sin digitación', 'No fingering'),
      ('left',  'Mano izquierda', 'Left hand'),
      ('right', 'Mano derecha',   'Right hand'),
    ];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: _surfaceDark,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _border),
      ),
      child: Row(
        children: <Widget>[
          Text(
            _ui('Digitación:', 'Fingering:'),
            style: const TextStyle(color: _muted, fontSize: 12),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Wrap(
              spacing: 8,
              runSpacing: 6,
              children: options.map(((String, String, String) opt) {
                final value = opt.$1;
                final label = _language == 'en' ? opt.$3 : opt.$2;
                final active = (_scaleFingeringHand ?? 'none') == value;
                return GestureDetector(
                  onTap: () {
                    final hand = value == 'none' ? null : value;
                    setState(() {
                      _scaleFingeringHand = hand;
                      _updateScaleFingeringsMap();
                      // Activar/desactivar las tiras cambia la altura
                      // disponible del piano y por tanto el ancho de tecla;
                      // hay que recentrar el scroll para que las tiras y
                      // las teclas queden alineadas de nuevo.
                      _needsPianoScrollSync = true;
                    });
                    _savePrefs();
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: active ? _accent : Colors.transparent,
                            border: Border.all(
                              color: active ? _accent : _muted,
                              width: active ? 2 : 1.5,
                            ),
                          ),
                          child: active
                              ? const Center(
                                  child: SizedBox(
                                    width: 8,
                                    height: 8,
                                    child: DecoratedBox(
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Color(0xFF1A222D),
                                      ),
                                    ),
                                  ),
                                )
                              : const SizedBox.shrink(),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(label, style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIntervalDetectionPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    _ui('Detección de Intervalos', 'Interval Detection'),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _surfaceDark,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: _border, width: 1),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        // Notes display
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: <Widget>[
                            Text(
                              _ui('Notas', 'Notes'),
                              style: const TextStyle(color: _muted, fontSize: 12),
                            ),
                            Text(
                              _intervalNotes.isEmpty
                                  ? '-'
                                  : (List<int>.from(_intervalNotes)..sort()).map(_midiNoteWithOctave).join(' – '),
                              style: const TextStyle(
                                color: _accent,
                                fontSize: 14,
                                fontFamily: 'Courier',
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Interval name
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: <Widget>[
                            Text(
                              _ui('Intervalo', 'Interval'),
                              style: const TextStyle(color: _muted, fontSize: 12),
                            ),
                            Text(
                              _intervalNotes.length >= 2 ? _getIntervalName() : '-',
                              style: const TextStyle(
                                color: _accent,
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Semitones
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: <Widget>[
                            Text(
                              _ui('Semitonos', 'Semitones'),
                              style: const TextStyle(color: _muted, fontSize: 12),
                            ),
                            Text(
                              _intervalNotes.length >= 2
                                  ? (_getIntervalSemitones()?.toString() ?? '-')
                                  : '-',
                              style: const TextStyle(
                                color: _accent,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Melody name — tappable toggle
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: <Widget>[
                            Text(
                              _ui('Ejemplo', 'Example'),
                              style: const TextStyle(color: _muted, fontSize: 12),
                            ),
                            GestureDetector(
                              onTap: _intervalNotes.length >= 2
                                  ? _toggleIntervalMelodyMode
                                  : null,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 3,
                                ),
                                decoration: BoxDecoration(
                                  color: _intervalMelodyMode
                                      ? const Color(0x26F3BF2F)
                                      : Colors.transparent,
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: _intervalMelodyMode ? _accent : _border,
                                  ),
                                ),
                                child: Text(
                                  _intervalNotes.length >= 2
                                      ? _getIntervalMelodyName()
                                      : '-',
                                  style: TextStyle(
                                    color: _intervalMelodyMode
                                        ? _accent
                                        : const Color(0xFFE9EDF2),
                                    fontSize: 13,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Buttons
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: <Widget>[
                      ElevatedButton.icon(
                        onPressed: _intervalNotes.length >= 2
                            ? () => _playIntervalMelody()
                            : null,
                        icon: const Icon(Icons.play_arrow),
                        label: Text(_ui('Reproducir', 'Play')),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _accent,
                          foregroundColor: Colors.black,
                          disabledBackgroundColor: _panelA,
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: _intervalNotes.length >= 2 && !_intervalMelodyMode
                            ? () => _playIntervalMelody(reversed: true)
                            : null,
                        icon: const Icon(Icons.play_arrow),
                        label: Text(_ui('Desc.', 'Rev.')),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _accent,
                          foregroundColor: Colors.black,
                          disabledBackgroundColor: _panelA,
                        ),
                      ),
                      OutlinedButton(
                        onPressed: _intervalNotes.isEmpty ? null : _clearIntervalNotes,
                        child: Text(_ui('Limpiar', 'Clear')),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _ui('Pulsa dos notas en el piano para detectar el intervalo',
                        'Press two notes on the piano to detect the interval'),
                    style: const TextStyle(color: _muted, fontSize: 12),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  String _midiNoteWithOctave(int midiNote) {
    final octave = (midiNote ~/ 12) - 1;
    return '${_pcLabel(midiNote % 12)}$octave';
  }

  Widget _buildMetronomePage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          final iphoneCompact = Platform.isIOS && _isCompactPhone(context);
          final sliderWidth = compact
              ? constraints.maxWidth - 24
              : constraints.maxWidth - 170;
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    _ui('Configuración de Metrónomo', 'Metronome settings'),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                  ),
                  const SizedBox(height: 6),
                  _helpAnchor(
                    'metronome_volume',
                    Wrap(
                    spacing: 12,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: <Widget>[
                      SizedBox(
                        width: compact ? constraints.maxWidth : 84,
                        child: Text(
                          _ui('Volumen', 'Volume'),
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            color: _muted,
                          ),
                        ),
                      ),
                      SizedBox(
                        width: sliderWidth,
                        child: Row(
                          children: <Widget>[
                            Expanded(
                              child: Slider(
                                min: 0,
                                max: 100,
                                divisions: 100,
                                value: _metroVolume.toDouble(),
                                onChanged: (value) {
                                  setState(() => _metroVolume = value.round());
                                },
                              ),
                            ),
                            SizedBox(
                              width: 72,
                              child: Text(
                                '$_metroVolume%',
                                textAlign: TextAlign.right,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_tempo',
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                  Text(
                    _ui('Tempo (BPM)', 'Tempo (BPM)'),
                    style: const TextStyle(fontWeight: FontWeight.w600, color: _muted),
                  ),
                  Row(
                    children: <Widget>[
                      IconButton(
                        onPressed: () {
                          setState(
                            () => _metroBpm = (_metroBpm - 1).clamp(40, 220),
                          );
                          if (_metroRunning) _startMetronome();
                        },
                        icon: const Icon(Icons.remove),
                      ),
                      Expanded(
                        child: Slider(
                          min: 40,
                          max: 220,
                          divisions: 180,
                          value: _metroBpm.toDouble(),
                          onChanged: (value) {
                            setState(() => _metroBpm = value.round());
                            if (_metroRunning) {
                              _startMetronome();
                            }
                          },
                        ),
                      ),
                      IconButton(
                        onPressed: () {
                          setState(
                            () => _metroBpm = (_metroBpm + 1).clamp(40, 220),
                          );
                          if (_metroRunning) _startMetronome();
                        },
                        icon: const Icon(Icons.add),
                      ),
                      SizedBox(
                        width: 72,
                        child: Text(
                          '$_metroBpm',
                          textAlign: TextAlign.right,
                        ),
                      ),
                    ],
                  ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_beats',
                    Wrap(
                    spacing: 10,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: <Widget>[
                      Text(_ui('Pulsos por compás:', 'Beats per bar:')),
                      if (!iphoneCompact)
                        IconButton(
                          onPressed: () {
                            setState(() {
                              _metroBeatsPerBar = (_metroBeatsPerBar - 1).clamp(
                                1,
                                16,
                              );
                              _metroCurrentBeat = -1;
                            });
                            if (_metroRunning) _startMetronome();
                          },
                          icon: const Icon(Icons.remove),
                        ),
                      SizedBox(
                        width: 72,
                        child: DropdownButton<int>(
                          isExpanded: true,
                          value: _metroBeatsPerBar,
                          items: List<DropdownMenuItem<int>>.generate(
                            16,
                            (i) => DropdownMenuItem<int>(
                              value: i + 1,
                              child: Text('${i + 1}'),
                            ),
                          ),
                          onChanged: (value) {
                            if (value == null) {
                              return;
                            }
                            setState(() {
                              _metroBeatsPerBar = value;
                              _metroCurrentBeat = -1;
                            });
                            if (_metroRunning) {
                              _startMetronome();
                            }
                          },
                        ),
                      ),
                      if (!iphoneCompact)
                        IconButton(
                          onPressed: () {
                            setState(() {
                              _metroBeatsPerBar = (_metroBeatsPerBar + 1).clamp(
                                1,
                                16,
                              );
                              _metroCurrentBeat = -1;
                            });
                            if (_metroRunning) _startMetronome();
                          },
                          icon: const Icon(Icons.add),
                        ),
                    ],
                  ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_subdivision',
                    Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: <Widget>[
                      Text(_ui('Subdivisión:', 'Subdivision:')),
                      const SizedBox(width: 10),
                      Expanded(
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: <Widget>[
                              ...<int>[1, 2, 3, 4, 6].map((n) {
                                final active = _metroClicksPerBeat == n;
                                return Padding(
                                  padding: const EdgeInsets.only(right: 8),
                                  child: ChoiceChip(
                                    selected: active,
                                    label: _metronomeSubdivisionFigure(
                                      n,
                                      active: active,
                                    ),
                                    labelPadding: const EdgeInsets.symmetric(
                                      horizontal: 4,
                                    ),
                                    visualDensity: VisualDensity.compact,
                                    materialTapTargetSize:
                                        MaterialTapTargetSize.shrinkWrap,
                                    onSelected: (_) {
                                      setState(() => _metroClicksPerBeat = n);
                                      if (_metroRunning) _startMetronome();
                                    },
                                  ),
                                );
                              }),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_accent',
                    Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Checkbox(
                        visualDensity: VisualDensity.compact,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        value: _metroBarAccent,
                        onChanged: (value) {
                          setState(() => _metroBarAccent = value ?? true);
                        },
                      ),
                      Flexible(child: Text(_ui('Acento de compás', 'Bar accent'))),
                    ],
                  ),
                  ),
                  _helpAnchor(
                    'metronome_timer',
                    Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: <Widget>[
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          Checkbox(
                            visualDensity: VisualDensity.compact,
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            value: _metroTimerEnabled,
                            onChanged: (value) {
                              setState(() => _metroTimerEnabled = value ?? false);
                            },
                          ),
                          Text(
                            _isCompactPhone(context)
                                ? _ui('Timer', 'Timer')
                                : _ui('Temporizador', 'Timer'),
                          ),
                        ],
                      ),
                      SizedBox(
                        width: 78,
                        child: DropdownButton<int>(
                          isExpanded: true,
                          value: _metroTimerMinutes.clamp(0, 99),
                          items: List<DropdownMenuItem<int>>.generate(
                            100,
                            (i) => DropdownMenuItem<int>(
                              value: i,
                              child: Text(i.toString().padLeft(2, '0')),
                            ),
                          ),
                          onChanged: (value) {
                            if (value != null) {
                              setState(() => _metroTimerMinutes = value);
                            }
                          },
                        ),
                      ),
                      const Text(':'),
                      SizedBox(
                        width: 78,
                        child: DropdownButton<int>(
                          isExpanded: true,
                          value: _metroTimerSeconds.clamp(0, 59),
                          items: List<DropdownMenuItem<int>>.generate(
                            60,
                            (i) => DropdownMenuItem<int>(
                              value: i,
                              child: Text(i.toString().padLeft(2, '0')),
                            ),
                          ),
                          onChanged: (value) {
                            if (value != null) {
                              setState(() => _metroTimerSeconds = value);
                            }
                          },
                        ),
                      ),
                    ],
                  ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _metronomeSubdivisionFigure(int clicks, {required bool active}) {
    final fg = active ? const Color(0xFF1A222D) : _text;
    if (clicks == 3 || clicks == 6) {
      final glyph = clicks == 3 ? '♪♪♪' : '♬♬';
      return Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.only(right: 2),
            child: Text(
              '$clicks',
              style: TextStyle(
                color: fg,
                fontSize: 10,
                fontWeight: FontWeight.w800,
                height: 1.0,
              ),
            ),
          ),
          Text(
            glyph,
            style: TextStyle(
              color: fg,
              fontSize: 14,
              fontWeight: FontWeight.w700,
              height: 1.0,
            ),
          ),
        ],
      );
    }
    final glyph = switch (clicks) {
      1 => '♩',
      2 => '♪♪',
      4 => '♬',
      _ => '$clicks',
    };
    return Text(
      glyph,
      style: TextStyle(
        color: fg,
        fontSize: 17,
        fontWeight: FontWeight.w700,
        height: 1.0,
      ),
    );
  }

  Widget _buildTunerPage() {
    final meter = (_tunerCents + 50) / 100.0;
    return _buildModeScaffold(
      showInstrument: false,
      bottomPanel: _buildTunerSpectrumPanel(),
      controls: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  _ui('Configuración de Afinador', 'Tuner settings'),
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                ),
                const SizedBox(height: 8),
                _helpAnchor(
                  'tuner_toggle',
                  FilledButton.icon(
                  onPressed: _toggleTuner,
                  icon: Icon(_tunerRunning ? Icons.stop : Icons.play_arrow),
                  label: Text(
                    _tunerRunning
                        ? _ui('Detener afinador', 'Stop tuner')
                        : _ui('Iniciar afinador', 'Start tuner'),
                  ),
                ),
                ),
                const SizedBox(height: 8),
                _helpAnchor(
                  'tuner_tuning_select',
                  Row(
                  children: <Widget>[
                    SizedBox(
                      width: 96,
                      child: Text(
                        _ui('Afinación', 'Tuning'),
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: _muted,
                        ),
                      ),
                    ),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        key: ValueKey<String>('tuner_tuning_$_tunerTuning'),
                        initialValue: _tunerTuning,
                        dropdownColor: _surfaceDark,
                        decoration: const InputDecoration(isDense: true),
                        items: <DropdownMenuItem<String>>[
                          DropdownMenuItem<String>(
                            value: 'standard_e',
                            child: Text(
                              _language == 'en' ? 'Standard E' : 'E estándar',
                            ),
                          ),
                          const DropdownMenuItem<String>(
                            value: 'drop_d',
                            child: Text('Drop D'),
                          ),
                          DropdownMenuItem<String>(
                            value: 'half_step_down',
                            child: Text(
                              _language == 'en'
                                  ? 'Half-step down'
                                  : '1/2 tono abajo',
                            ),
                          ),
                        ],
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _tunerTuning = value);
                          }
                        },
                      ),
                    ),
                  ],
                ),
                ),
                const SizedBox(height: 8),
                _helpAnchor(
                  'tuner_gain',
                  Row(
                  children: <Widget>[
                    SizedBox(
                      width: 96,
                      child: Text(
                        _ui('Ganancia', 'Gain'),
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: _muted,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(
                        () => _tunerInputGain = (_tunerInputGain - 0.01).clamp(
                          0.0,
                          2.0,
                        ),
                      ),
                      icon: const Icon(Icons.remove),
                    ),
                    Expanded(
                      child: Slider(
                        min: 0.0,
                        max: 2.0,
                        divisions: 200,
                        value: _tunerInputGain,
                        onChanged: (value) =>
                            setState(() => _tunerInputGain = value),
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(
                        () => _tunerInputGain = (_tunerInputGain + 0.01).clamp(
                          0.0,
                          2.0,
                        ),
                      ),
                      icon: const Icon(Icons.add),
                    ),
                    SizedBox(
                      width: 54,
                      child: Text('${(_tunerInputGain * 100).round()}%'),
                    ),
                  ],
                ),
                ),
                const SizedBox(height: 6),
                _helpAnchor(
                  'tuner_range',
                  Row(
                  children: <Widget>[
                    SizedBox(
                      width: 96,
                      child: Text(
                        _ui('Rango Hz', 'Hz range'),
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: _muted,
                        ),
                      ),
                    ),
                    SizedBox(
                      width: 74,
                      child: DropdownButton<int>(
                        value: _tunerRangeMin,
                        dropdownColor: _surfaceDark,
                        items: List<DropdownMenuItem<int>>.generate(
                          300,
                          (i) => DropdownMenuItem<int>(
                            value: i * 10,
                            child: Text('${i * 10}'),
                          ),
                        ),
                        onChanged: (value) {
                          if (value == null) return;
                          setState(() {
                            _tunerRangeMin = value.clamp(0, 2990);
                            if (_tunerRangeMax <= _tunerRangeMin) {
                              _tunerRangeMax = (_tunerRangeMin + 10).clamp(
                                10,
                                3000,
                              );
                            }
                          });
                        },
                      ),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 8),
                      child: Text('-'),
                    ),
                    SizedBox(
                      width: 74,
                      child: DropdownButton<int>(
                        value: _tunerRangeMax,
                        dropdownColor: _surfaceDark,
                        items: List<DropdownMenuItem<int>>.generate(
                          300,
                          (i) => DropdownMenuItem<int>(
                            value: (i + 1) * 10,
                            child: Text('${(i + 1) * 10}'),
                          ),
                        ),
                        onChanged: (value) {
                          if (value == null) return;
                          setState(() {
                            _tunerRangeMax = value.clamp(
                              _tunerRangeMin + 1,
                              3000,
                            );
                          });
                        },
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Text('Hz', style: TextStyle(color: _muted)),
                  ],
                ),
                ),
                const SizedBox(height: 12),
                _helpAnchor(
                  'tuner_readout',
                  Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: _surfaceDark,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _border),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text('Nota: $_tunerNote'),
                      const SizedBox(height: 4),
                      Text(
                        'Desviación: ${_tunerCents >= 0 ? '+' : ''}$_tunerCents cents',
                      ),
                      const SizedBox(height: 4),
                      Text('Frecuencia: ${_tunerFreq.toStringAsFixed(1)} Hz'),
                    ],
                  ),
                ),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 20,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                    color: const Color(0xFFCBD3DD),
                  ),
                  child: Stack(
                    children: <Widget>[
                      Positioned.fill(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 2),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              final knobX = (constraints.maxWidth - 16) * meter;
                              return Stack(
                                children: <Widget>[
                                  Positioned(
                                    left: knobX,
                                    top: 2,
                                    child: Container(
                                      width: 16,
                                      height: 16,
                                      decoration: const BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Colors.blue,
                                      ),
                                    ),
                                  ),
                                ],
                              );
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                if (_tunerError.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      'Error: $_tunerError',
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTunerSpectrumPanel() {
    return _panel(
      child: SizedBox(
        height: 220,
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF0B1018),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF2F3743)),
          ),
          child: CustomPaint(
            painter: _MiniTunerSpectrumPainter(
              rangeMinHz: _tunerRangeMin.toDouble(),
              rangeMaxHz: _tunerRangeMax.toDouble(),
              currentFreq: _tunerFreq,
              currentStringIdx: _tunerCurrentStringIdx,
              tuningLabels: _tunerOpenLabelsForCurrentTuning(),
              tuningFreqs: _tunerOpenFreqsForCurrentTuning(),
              spectrumBins: _tunerSpectrumBins,
            ),
            child: const SizedBox.expand(),
          ),
        ),
      ),
    );
  }

  Widget _panel({required Widget child}) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: <Color>[_panelA, _panelB],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _border),
      ),
      padding: const EdgeInsets.all(12),
      child: child,
    );
  }

  Widget _holdPlayButton({
    required bool enabled,
    required bool active,
    required Future<void> Function() onDown,
    required VoidCallback onUp,
    String? label,
  }) {
    final hasLabel = (label != null && label.trim().isNotEmpty);
    return Listener(
      onPointerDown: (_) {
        if (!enabled) return;
        unawaited(onDown());
      },
      onPointerUp: (_) {
        if (!enabled) return;
        onUp();
      },
      onPointerCancel: (_) {
        if (!enabled) return;
        onUp();
      },
      child: hasLabel
          ? FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: active ? _accent : _surfaceDark,
                foregroundColor: active ? const Color(0xFF1A222D) : _text,
              ),
              onPressed: enabled ? () {} : null,
              icon: const Icon(Icons.play_arrow),
              label: Text(label),
            )
          : FilledButton(
              style: FilledButton.styleFrom(
                minimumSize: const Size(46, 42),
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 10,
                ),
                backgroundColor: active ? _accent : _surfaceDark,
                foregroundColor: active ? const Color(0xFF1A222D) : _text,
              ),
              onPressed: enabled ? () {} : null,
              child: const Icon(Icons.play_arrow),
            ),
    );
  }

  /// Send a MIDI note_on (0x90) message to all connected MIDI devices.
  void _sendMidiNoteOn(int midiNote, int velocity) {
    try {
      _midiCommand.sendData(
        Uint8List.fromList(<int>[0x90, midiNote & 0x7F, velocity & 0x7F]),
      );
    } catch (_) {}
  }

  /// Send a MIDI note_off (0x80) message to all connected MIDI devices.
  void _sendMidiNoteOff(int midiNote) {
    try {
      _midiCommand.sendData(
        Uint8List.fromList(<int>[0x80, midiNote & 0x7F, 0]),
      );
    } catch (_) {}
  }

  /// Play a note via audio or MIDI output based on _soundOutput setting.
  Future<void> playNote(int midiNote, {int velocity = 80, String instrument = 'piano', double durationSeconds = 0.6}) async {
    if (_soundOutput == 'midi') {
      _sendMidiNoteOn(midiNote, velocity);
      return;
    }
    // Default: audio playback via synthesizer
    await _playTone(
      midi: midiNote,
      instrument: instrument,
      durationSeconds: durationSeconds,
    );
  }

  /// Stop a note via audio or MIDI output based on _soundOutput setting.
  Future<void> stopNote(int midiNote) async {
    if (_soundOutput == 'midi') {
      _sendMidiNoteOff(midiNote);
      return;
    }
    // Default: audio playback (note will naturally decay based on duration parameter)
    // No explicit stop needed for synthesized tones with fixed duration
  }

  /// Set scale fingering hand preference (none, right, left)
  void _setScaleFingeringHand(String? hand) {
    setState(() {
      _scaleFingeringHand = hand;
      _updateScaleFingeringsMap();
    });
  }

  /// Update fingerings map based on current scale and hand
  void _updateScaleFingeringsMap() {
    if (_scaleFingeringHand == null || _generatedScaleJson == null) {
      _scaleFingeringsMap = <int, int>{};
      return;
    }

    try {
      final midiNotes = _scaleRhNotes();
      const nameMap = <String, String>{
        'ionian': 'ionian_mode',
        'dorian': 'dorian_mode',
        'phrygian': 'phrygian_mode',
        'lydian': 'lydian_mode',
        'mixolydian': 'mixolydian_mode',
        'aeolian': 'aeolian_mode',
        'locrian': 'locrian_mode',
        'harmonic minor': 'harmonic_minor',
        'melodic minor': 'melodic_minor',
        'major pentatonic': 'major',
        'minor pentatonic': 'natural_minor',
      };
      final rawName = _scalePatternName.toLowerCase();
      final scaleType = nameMap[rawName] ?? rawName.replaceAll(' ', '_');

      final fingerings = getFingeringForScale(
        scaleType,
        _scaleTonicPc,
        _scaleFingeringHand!,
        count: midiNotes.length,
      );

      final result = <int, int>{};
      for (int i = 0; i < midiNotes.length && i < fingerings.length; i++) {
        result[midiNotes[i]] = fingerings[i];
      }
      _scaleFingeringsMap = result;
    } catch (e) {
      _scaleFingeringsMap = <int, int>{};
    }
  }

  /// Get finger number for a MIDI note in current scale
  int? getScaleFingering(int midiNote) => _scaleFingeringsMap[midiNote];

  /// Get fingerings to display on piano in scales tab
  Map<int, int> getDisplayScaleFingeringNotes() {
    if (_tabIndex != 3 || _scaleFingeringHand == null) {
      return <int, int>{};
    }
    return Map<int, int>.from(_scaleFingeringsMap);
  }

  /// Get MIDI notes held for highlighting in generation
  Set<int> getGenerationMidiHeldNotes() => Set<int>.from(_generationMidiHeldNotes);

  // Interval detection methods
  void _addIntervalNote(int midiNote) {
    setState(() {
      _intervalMelodyMode = false;
      _intervalNotes.add(midiNote);
      if (_intervalNotes.length > 2) {
        _intervalNotes.removeAt(0);
      }
    });
  }

  void _clearIntervalNotes() {
    setState(() {
      _intervalNotes.clear();
      _intervalMelodyMode = false;
      _intervalPlayingNote = null;
      _intervalPlayingIdx = null;
      _intervalMelodyPlaybackTimer?.cancel();
      _intervalMelodyPlaybackTimer = null;
    });
  }

  void _toggleIntervalMelodyMode() {
    final semitones = _getIntervalSemitones();
    if (semitones == null || _intervalNotes.length < 2) return;
    if (getIntervalMelody(semitones) == null) return;
    setState(() {
      _intervalMelodyMode = !_intervalMelodyMode;
      if (!_intervalMelodyMode) {
        _intervalPlayingNote = null;
        _intervalPlayingIdx = null;
      }
    });
  }

  int? _getIntervalSemitones() {
    if (_intervalNotes.length < 2) return null;
    final raw = (_intervalNotes[1] - _intervalNotes[0]).abs();
    final mod = raw % 12;
    return (mod == 0 && raw > 0) ? 12 : mod;
  }

  String _getIntervalName() {
    final semitones = _getIntervalSemitones();
    if (semitones == null) return "-";
    return getIntervalName(semitones, _language);
  }

  String _getIntervalMelodyName() {
    final semitones = _getIntervalSemitones();
    if (semitones == null) return "-";
    return getIntervalMelodyName(semitones, _language);
  }

  List<int?> _getIntervalMelodyNotes() {
    return getIntervalMelodyNotes(_intervalNotes);
  }

  void _playIntervalMelody({bool reversed = false}) {
    if (_intervalNotes.length < 2) return;
    _intervalMelodyPlaybackTimer?.cancel();
    if (_intervalMelodyMode) {
      // Melody mode: always play the reference song forward
      final notes = _getIntervalMelodyNotes();
      final semitones = _getIntervalSemitones();
      if (semitones == null) return;
      final melody = getIntervalMelody(semitones);
      if (melody == null) return;
      setState(() => _intervalMelodyPlaying = true);
      _playMelodySequence(notes, melody, 0);
    } else {
      // Normal mode: play the two interval notes (reversible)
      final ordered = reversed
          ? List<int>.from(_intervalNotes.reversed).cast<int?>()
          : List<int>.from(_intervalNotes).cast<int?>();
      const dummyMelody = IntervalMelody(
        nameEs: '', nameEn: '', beatsPerBar: 4,
        offsets: [0, 0], durations: ['q', 'q'],
      );
      setState(() => _intervalMelodyPlaying = true);
      _playMelodySequence(ordered, dummyMelody, 0);
    }
  }

  void _playMelodySequence(List<int?> notes, IntervalMelody melody, int index) {
    if (index >= notes.length) {
      setState(() {
        _intervalMelodyPlaying = false;
        _intervalPlayingNote = null;
        _intervalPlayingIdx = null;
      });
      return;
    }

    final note = notes[index];
    if (note != null) {
      unawaited(playNote(note, instrument: _instrumentView));
      setState(() {
        _intervalPlayingNote = note;
        _intervalPlayingIdx = index;
      });
    }

    final durations = melody.durations;
    final durationCode = index < durations.length ? durations[index] : "q";
    final durationMs = durationToMs(durationCode);

    _intervalMelodyPlaybackTimer = Timer(Duration(milliseconds: durationMs), () {
      _playMelodySequence(notes, melody, index + 1);
    });
  }

}

class _MiniStaffPainter extends CustomPainter {
  _MiniStaffPainter({
    required this.notes,
    required this.extras,
    this.detectionActiveNotes = const <int>{},
    this.generationRhNotes = const <int>[],
    this.generationLhNotes = const <int>[],
    this.generationPlayingNotes = const <int>{},
    this.generationGuitarMode = false,
    this.scaleRhNotes = const <int>[],
    this.scaleLhNotes = const <int>[],
    this.scaleCurrentNote,
    this.scaleCurrentIsLeft,
    this.scaleGuitarMode = false,
    this.keySignatureCount = 0,
    this.keySignaturePreferFlats = false,
    this.intervalMelodyMode = false,
    this.intervalMelodyNotes = const <int?>[],
    this.intervalMelodyDurations = const <String>[],
    this.intervalPlayingIdx,
    this.intervalBeatsPerBar = 4,
    this.intervalAnacrusis = 0.0,
  });

  /// Orden F# C# G# D# A# E# B# — mismos MIDI que `app.js`.
  static const List<double> _keySigTrebleSharpMidis = <double>[
    78,
    73,
    80,
    75,
    70,
    76,
    71,
  ];
  static const List<double> _keySigBassSharpMidis = <double>[
    54,
    49,
    56,
    51,
    46,
    52,
    47,
  ];
  static const List<double> _keySigTrebleFlatOffsets = <double>[
    2,
    0.5,
    2.5,
    1,
    3,
    1.5,
    3.5,
  ];
  static const List<double> _keySigBassFlatOffsets = <double>[
    3,
    1.5,
    3.5,
    2,
    4,
    2.5,
    4.5,
  ];

  final List<int> notes;
  final Set<int> extras;
  final Set<int> detectionActiveNotes;
  final List<int> generationRhNotes;
  final List<int> generationLhNotes;
  final Set<int> generationPlayingNotes;
  final bool generationGuitarMode;
  final List<int> scaleRhNotes;
  final List<int> scaleLhNotes;
  final int? scaleCurrentNote;
  final bool? scaleCurrentIsLeft;
  final bool scaleGuitarMode;
  final int keySignatureCount;
  final bool keySignaturePreferFlats;
  final bool intervalMelodyMode;
  final List<int?> intervalMelodyNotes;
  final List<String> intervalMelodyDurations;
  final int? intervalPlayingIdx;
  final int intervalBeatsPerBar;
  final double intervalAnacrusis;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0F1621);
    canvas.drawRect(Offset.zero & size, bg);

    final linePaint = Paint()
      ..color = const Color(0xFFCAD3E0)
      ..strokeWidth = 1.4;
    final noteOutline = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.8;

    final compactWidth = size.width < 520;
    final left = compactWidth ? 28.0 : 52.0;
    final right = size.width - 16;
    final gap = math.max(10.0, math.min(16.0, size.height / 24));
    final grandGap = math.max(64.0, gap * 6.2);
    final systemH = grandGap + (4 * gap);
    final trebleTop = (size.height - systemH) / 2;
    final bassTop = trebleTop + grandGap;
    final clefInset = compactWidth ? 6.0 : 12.0;
    final clefBassInset = compactWidth ? 8.0 : 14.0;
    var noteStartX = left + (compactWidth ? 72.0 : 110.0);
    final scaleStepX = compactWidth ? 24.0 : 32.0;
    final noteW = compactWidth ? 13.0 : 16.0;
    final noteH = compactWidth ? 10.0 : 12.0;
    final noteColumnStep = compactWidth ? noteW * 1.4 : noteW * 1.8;

    for (int i = 0; i < 5; i += 1) {
      final yT = trebleTop + i * gap;
      final yB = bassTop + i * gap;
      canvas.drawLine(Offset(left, yT), Offset(right, yT), linePaint);
      canvas.drawLine(Offset(left, yB), Offset(right, yB), linePaint);
    }
    canvas.drawLine(
      Offset(left, trebleTop),
      Offset(left, bassTop + 4 * gap),
      linePaint..strokeWidth = 1.6,
    );

    final clefStyle = TextStyle(
      color: const Color(0xFFE9EDF2),
      fontSize: gap * 3.5,
      fontWeight: FontWeight.w700,
    );
    final tpTreble = TextPainter(
      text: TextSpan(text: '𝄞', style: clefStyle),
      textDirection: TextDirection.ltr,
    )..layout();
    tpTreble.paint(canvas, Offset(left + clefInset, trebleTop + gap * 0.6));
    final tpBass = TextPainter(
      text: TextSpan(text: '𝄢', style: clefStyle),
      textDirection: TextDirection.ltr,
    )..layout();
    tpBass.paint(canvas, Offset(left + clefBassInset, bassTop + gap * 0.5));

    if (keySignatureCount > 0) {
      final sigStep = compactWidth ? 13.5 : 18.0;
      final keyX0 = left + (compactWidth ? 54.0 : 82.0);
      final accBase = math.max(15.0, gap * 1.55);
      final accStyleSharp = TextStyle(
        color: const Color(0xFFE9EDF2),
        fontSize: accBase,
      );
      final accStyleFlat = accStyleSharp.copyWith(fontSize: accBase * 1.14);
      var xKey = keyX0;
      final n = keySignatureCount.clamp(0, 7);
      for (int i = 0; i < n; i += 1) {
        final sym = keySignaturePreferFlats ? '♭' : '♯';
        final double yTreble;
        final double yBass;
        if (keySignaturePreferFlats) {
          yTreble = trebleTop + gap * _keySigTrebleFlatOffsets[i];
          yBass = bassTop + gap * _keySigBassFlatOffsets[i];
        } else {
          yTreble = _midiToTrebleY(_keySigTrebleSharpMidis[i], trebleTop, gap);
          yBass = _midiToBassY(_keySigBassSharpMidis[i], bassTop, gap);
        }
        final accStyle = keySignaturePreferFlats ? accStyleFlat : accStyleSharp;
        final tpAcc = TextPainter(
          text: TextSpan(text: sym, style: accStyle),
          textDirection: TextDirection.ltr,
        )..layout();
        final ox = xKey + sigStep / 2 - tpAcc.width / 2;
        final oyOff = tpAcc.height / 2;
        tpAcc.paint(canvas, Offset(ox, yTreble - oyOff));
        tpAcc.paint(canvas, Offset(ox, yBass - oyOff));
        xKey += sigStep;
      }
      noteStartX = xKey + (compactWidth ? 8.0 : 12.0);
    }

    if (intervalMelodyMode && intervalMelodyNotes.isNotEmpty) {
      _drawIntervalMelody(canvas, trebleTop, bassTop, gap, noteStartX, right, noteW, noteH);
    } else if (scaleRhNotes.isNotEmpty) {
      final pairCount = math.min(scaleRhNotes.length, scaleLhNotes.length);
      for (int degree = 0; degree < scaleRhNotes.length; degree += 1) {
        final x = noteStartX + (degree * scaleStepX);
        if (degree < pairCount) {
          final bassMidi = scaleLhNotes[degree];
          final yBass = _midiToBassY(bassMidi.toDouble(), bassTop, gap);
          final currentBass =
              scaleCurrentNote != null &&
              scaleCurrentNote == bassMidi &&
              (scaleCurrentIsLeft != false);
          noteOutline.color = currentBass
              ? const Color(0xFFFF8A2B)
              : const Color(0xFFE9EDF2);
          _drawLedgerLines(
            canvas,
            x: x,
            midi: bassMidi.toDouble(),
            top: bassTop,
            gap: gap,
            treble: false,
            color: noteOutline.color,
          );
          canvas.drawOval(
            Rect.fromCenter(center: Offset(x, yBass), width: noteW, height: noteH),
            noteOutline,
          );
        }
        final trebleMidi = scaleRhNotes[degree];
        final yTreble = _midiToTrebleY(trebleMidi.toDouble(), trebleTop, gap);
        final currentTreble =
            scaleCurrentNote != null &&
            scaleCurrentNote == trebleMidi &&
            (scaleCurrentIsLeft != true);
        noteOutline.color = currentTreble
            ? const Color(0xFF4DA3EA)
            : const Color(0xFFE9EDF2);
        _drawLedgerLines(
          canvas,
          x: x,
          midi: trebleMidi.toDouble(),
          top: trebleTop,
          gap: gap,
          treble: true,
          color: noteOutline.color,
        );
        canvas.drawOval(
          Rect.fromCenter(center: Offset(x, yTreble), width: noteW, height: noteH),
          noteOutline,
        );
      }
    } else {
      final list = notes.toList()..sort();
      final placedTrebleCols = <int, List<double>>{};
      final placedBassCols = <int, List<double>>{};
      final rhSet = generationRhNotes.toSet();
      final lhSet = generationLhNotes.toSet();
      final overlapThreshold = math.max(1.0, noteH - 1.0);
      for (int i = 0; i < list.length; i += 1) {
        final midi = list[i];
        final y = midi >= 60
            ? _midiToTrebleY(midi.toDouble(), trebleTop, gap)
            : _midiToBassY(midi.toDouble(), bassTop, gap);
        final placedCols = midi >= 60 ? placedTrebleCols : placedBassCols;
        var col = 0;
        while (true) {
          final ys = placedCols[col] ?? const <double>[];
          final overlaps = ys.any(
            (prevY) => (y - prevY).abs() < overlapThreshold,
          );
          if (!overlaps) break;
          col += 1;
        }
        final x = noteStartX + (col * noteColumnStep);
        final ys = List<double>.from(placedCols[col] ?? const <double>[])
          ..add(y);
        placedCols[col] = ys;
        Color? fillColor;
        noteOutline.strokeWidth = 1.8;
        if (detectionActiveNotes.contains(midi)) {
          fillColor = const Color(0xFF4DA3EA);
          noteOutline.color = const Color(0xFFE9EDF2);
        } else if (generationPlayingNotes.contains(midi)) {
          noteOutline.strokeWidth = 2.45;
          if (!generationGuitarMode &&
              lhSet.contains(midi) &&
              !rhSet.contains(midi)) {
            fillColor = const Color(0xFFFFA040);
            noteOutline.color = const Color(0xFFFFE0C2);
          } else {
            fillColor = const Color(0xFF5ECEFF);
            noteOutline.color = const Color(0xFFE9EDF2);
          }
        } else if (rhSet.contains(midi) || lhSet.contains(midi)) {
          // Mismo criterio que piano: contorno del acorde sin relleno en reposo.
          // En guitarra, si además rellenábamos todas las notas en rhSet, al
          // alinear rhSet con el pentagrama quedaban todas “marcadas”.
          fillColor = null;
          noteOutline.strokeWidth = 2.05;
          if (lhSet.contains(midi) && !rhSet.contains(midi)) {
            noteOutline.color = const Color(0xFFFF8A2B);
          } else {
            noteOutline.color = const Color(0xFF6FE0FF);
          }
        } else if (extras.contains(midi)) {
          fillColor = const Color(0xFFBF2F2F);
          noteOutline.color = const Color(0xFFF48F8F);
        } else {
          fillColor = null;
          noteOutline.color = const Color(0xFFE9EDF2);
        }
        final oval = Rect.fromCenter(
          center: Offset(x, y),
          width: noteW,
          height: noteH,
        );
        _drawLedgerLines(
          canvas,
          x: x,
          midi: midi.toDouble(),
          top: midi >= 60 ? trebleTop : bassTop,
          gap: gap,
          treble: midi >= 60,
          color: noteOutline.color,
        );
        if (fillColor != null) {
          canvas.drawOval(oval, Paint()..color = fillColor);
        }
        canvas.drawOval(oval, noteOutline);
      }
    }
  }

  double _midiToTrebleY(double midi, double top, double gap) {
    const bottomLineDiatonic = 30.0; // E4
    final d = _midiToDiatonic(midi);
    final baseY = top + 4 * gap;
    return baseY - ((d - bottomLineDiatonic) * (gap / 2));
  }

  double _midiToBassY(double midi, double top, double gap) {
    const bottomLineDiatonic = 18.0; // G2
    final d = _midiToDiatonic(midi);
    final baseY = top + 4 * gap;
    return baseY - ((d - bottomLineDiatonic) * (gap / 2));
  }

  double _midiToDiatonic(double midi) {
    const pcToLetter = <int>[0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6];
    final n = midi.round();
    final pc = ((n % 12) + 12) % 12;
    final octave = (n ~/ 12) - 1;
    return (octave * 7 + pcToLetter[pc]).toDouble();
  }

  void _drawLedgerLines(
    Canvas canvas, {
    required double x,
    required double midi,
    required double top,
    required double gap,
    required bool treble,
    required Color color,
  }) {
    final d = _midiToDiatonic(midi).round();
    final bottomLineD = treble ? 30 : 18;
    final topLineD = bottomLineD + 8;
    if (d >= bottomLineD && d <= topLineD) return;

    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.6
      ..strokeCap = StrokeCap.round;
    final lineLeft = x - 11.0;
    final lineRight = x + 11.0;
    if (d < bottomLineD) {
      for (int ld = bottomLineD - 2; ld >= d; ld -= 2) {
        final y = _staffYForDiatonic(
          diatonic: ld.toDouble(),
          bottomLineDiatonic: bottomLineD.toDouble(),
          top: top,
          gap: gap,
        );
        canvas.drawLine(Offset(lineLeft, y), Offset(lineRight, y), paint);
      }
      return;
    }
    for (int ld = topLineD + 2; ld <= d; ld += 2) {
      final y = _staffYForDiatonic(
        diatonic: ld.toDouble(),
        bottomLineDiatonic: bottomLineD.toDouble(),
        top: top,
        gap: gap,
      );
      canvas.drawLine(Offset(lineLeft, y), Offset(lineRight, y), paint);
    }
  }

  double _staffYForDiatonic({
    required double diatonic,
    required double bottomLineDiatonic,
    required double top,
    required double gap,
  }) {
    final baseY = top + 4 * gap;
    return baseY - ((diatonic - bottomLineDiatonic) * (gap / 2));
  }

  void _drawIntervalMelody(
    Canvas canvas,
    double trebleTop,
    double bassTop,
    double gap,
    double noteStartX,
    double right,
    double noteW,
    double noteH,
  ) {
    final n = intervalMelodyNotes.length;
    if (n == 0) return;

    const noteColor = Color(0xFFD7DDE7);
    const playColor = Color(0xFF4DA3EA);
    final stemLen = gap * 3.5;
    final dotR = math.max(1.5, gap * 0.18);

    // Time signature
    final tsFontSize = math.max(14.0, gap * 1.7);
    TextPainter makeTp(String text) => TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: const Color(0xFFFFFFFF),
          fontSize: tsFontSize,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    final tpNum = makeTp(intervalBeatsPerBar.toString());
    final tpDen = makeTp('4');
    final tsHW = math.max(tpNum.width, tpDen.width) / 2;
    final tsX = noteStartX + tsHW;
    tpNum.paint(canvas, Offset(tsX - tpNum.width / 2, trebleTop + gap * 0.3));
    tpDen.paint(canvas, Offset(tsX - tpDen.width / 2, trebleTop + gap * 2.3));
    tpNum.paint(canvas, Offset(tsX - tpNum.width / 2, bassTop + gap * 0.3));
    tpDen.paint(canvas, Offset(tsX - tpDen.width / 2, bassTop + gap * 2.3));
    final melLeft = tsX + tsHW + 10.0;

    // Tick durations
    const qt = 1000;
    int tickFor(String d) {
      final dotted = d.endsWith('.');
      final code = dotted ? d.substring(0, d.length - 1) : d;
      const tmap = <String, int>{
        'w': 4 * qt, 'h': 2 * qt, 'q': qt,
        'e': qt ~/ 2, 'et': qt ~/ 3, 's': qt ~/ 4,
      };
      var t = tmap[code] ?? qt;
      if (dotted) t = t * 3 ~/ 2;
      return t;
    }

    final ticks = List<int>.generate(n, (i) {
      final d = i < intervalMelodyDurations.length ? intervalMelodyDurations[i] : 'q';
      return tickFor(d);
    });
    final totalTicks = ticks.fold(0, (a, b) => a + b);
    if (totalTicks == 0) return;
    final availW = (right - 16.0) - melLeft;
    final xPos = List<double>.generate(n, (i) {
      final cum = ticks.sublist(0, i).fold(0, (a, b) => a + b);
      return melLeft + cum / totalTicks * availW;
    });

    // Bar lines
    final barTicks = intervalBeatsPerBar * qt;
    var barRun = -(intervalAnacrusis * qt).round();
    final blPaint = Paint()..color = const Color(0xFF5A6A7A)..strokeWidth = 1.0;
    for (int i = 0; i < n; i++) {
      final prev = barRun;
      barRun += ticks[i];
      if (i > 0 && (prev ~/ barTicks) < (barRun ~/ barTicks)) {
        final bx = (xPos[i - 1] + xPos[i]) / 2;
        canvas.drawLine(Offset(bx, trebleTop), Offset(bx, bassTop + 4 * gap), blPaint);
      }
    }

    // Beam groups
    final beamGroupOf = <int, int>{};
    final beamGroups = <List<int>>[];
    var tickPos = 0;
    var bgCurrent = <int>[];
    var bgBeat = 0;
    for (int i = 0; i < n; i++) {
      final dur = i < intervalMelodyDurations.length ? intervalMelodyDurations[i] : 'q';
      final durBase = dur.endsWith('.') ? dur.substring(0, dur.length - 1) : dur;
      final isSubQ = (durBase == 'e' || durBase == 'et' || durBase == 's') &&
          intervalMelodyNotes[i] != null;
      final beat = tickPos ~/ qt;
      if (isSubQ) {
        if (bgCurrent.isNotEmpty && beat != bgBeat) {
          if (bgCurrent.length > 1) {
            final gid = beamGroups.length;
            for (final g in bgCurrent) { beamGroupOf[g] = gid; }
            beamGroups.add(List<int>.from(bgCurrent));
          }
          bgCurrent = [];
        }
        if (bgCurrent.isEmpty) bgBeat = beat;
        bgCurrent.add(i);
      } else {
        if (bgCurrent.length > 1) {
          final gid = beamGroups.length;
          for (final g in bgCurrent) { beamGroupOf[g] = gid; }
          beamGroups.add(List<int>.from(bgCurrent));
        }
        bgCurrent = [];
      }
      tickPos += ticks[i];
    }
    if (bgCurrent.length > 1) {
      final gid = beamGroups.length;
      for (final g in bgCurrent) { beamGroupOf[g] = gid; }
      beamGroups.add(List<int>.from(bgCurrent));
    }

    // Draw notes and rests
    final stemData = <int, ({double x, double yEnd, bool stemUp, int flagCount})>{};
    for (int i = 0; i < n; i++) {
      final midiNull = intervalMelodyNotes[i];
      final dur = i < intervalMelodyDurations.length ? intervalMelodyDurations[i] : 'q';
      final durBase = dur.endsWith('.') ? dur.substring(0, dur.length - 1) : dur;
      final isDotted = dur.endsWith('.');
      final x = xPos[i];
      final flagCount = (durBase == 'e' || durBase == 'et') ? 1 : (durBase == 's' ? 2 : 0);
      final hasStem = durBase != 'w';
      final isHollow = durBase == 'w' || durBase == 'h';
      final col = intervalPlayingIdx == i ? playColor : noteColor;

      if (midiNull == null) {
        _drawRestSymbolMelody(canvas, x, trebleTop + 2 * gap, durBase, gap, noteColor, trebleTop);
      } else {
        final midi = midiNull;
        final isT = midi >= 60;
        final y = isT
            ? _midiToTrebleY(midi.toDouble(), trebleTop, gap)
            : _midiToBassY(midi.toDouble(), bassTop, gap);
        final staffTop = isT ? trebleTop : bassTop;
        _drawLedgerLines(canvas, x: x, midi: midi.toDouble(), top: staffTop, gap: gap, treble: isT, color: col);
        final nw = durBase == 'w' ? noteW * 1.25 : noteW;
        canvas.drawOval(
          Rect.fromCenter(center: Offset(x, y), width: nw, height: noteH),
          Paint()
            ..style = isHollow ? PaintingStyle.stroke : PaintingStyle.fill
            ..color = col
            ..strokeWidth = 2.0,
        );
        if (isDotted) {
          canvas.drawCircle(Offset(x + nw / 2 + dotR * 2.5, y), dotR, Paint()..color = col);
        }
        if (hasStem) {
          final stemMid = staffTop + 2 * gap;
          final stemUp = y > stemMid;
          final sx = stemUp ? x + nw / 2 - 1 : x - nw / 2 + 1;
          final syEnd = stemUp ? y - stemLen : y + stemLen;
          canvas.drawLine(Offset(sx, y), Offset(sx, syEnd),
              Paint()..color = col..strokeWidth = 1.8);
          if (flagCount > 0) {
            if (beamGroupOf.containsKey(i)) {
              stemData[i] = (x: sx, yEnd: syEnd, stemUp: stemUp, flagCount: flagCount);
            } else {
              _drawMelodyFlag(canvas, sx, syEnd, flagCount, stemUp, gap, col);
            }
          }
        }
      }
    }

    // Beams
    final beamW = math.max(2.5, gap * 0.25);
    for (final group in beamGroups) {
      final data = <({double x, double yEnd, bool stemUp, int flagCount})>[];
      for (final gi in group) {
        if (stemData.containsKey(gi)) data.add(stemData[gi]!);
      }
      if (data.length < 2) continue;
      final nPrim = data.map((d) => d.flagCount).reduce(math.min);
      for (int bar = 0; bar < nPrim; bar++) {
        final bOff = bar * gap * 0.3;
        final su = data.first.stemUp;
        final y0 = su ? data.first.yEnd + bOff : data.first.yEnd - bOff;
        final y1 = su ? data.last.yEnd + bOff : data.last.yEnd - bOff;
        canvas.drawLine(Offset(data.first.x, y0), Offset(data.last.x, y1),
            Paint()..color = noteColor..strokeWidth = beamW);
      }
      final grpLast = group.length - 1;
      for (int gi = 0; gi < group.length; gi++) {
        final idx = group[gi];
        if (!stemData.containsKey(idx)) continue;
        final d = stemData[idx]!;
        final extra = d.flagCount - nPrim;
        if (extra <= 0) continue;
        final stubDir = gi == grpLast ? -1.0 : 1.0;
        final stubW = math.max(gap * 1.2, 14.0);
        for (int be = 0; be < extra; be++) {
          final stubOff = (nPrim + be) * gap * 0.3;
          final sy = d.stemUp ? d.yEnd + stubOff : d.yEnd - stubOff;
          canvas.drawLine(Offset(d.x, sy), Offset(d.x + stubDir * stubW, sy),
              Paint()..color = noteColor..strokeWidth = beamW);
        }
      }
    }
  }

  void _drawMelodyFlag(
    Canvas canvas, double sx, double syEnd,
    int flagCount, bool stemUp, double gap, Color col,
  ) {
    final fw = gap * 0.52;
    final fh = gap * 1.75;
    final sign = stemUp ? 1.0 : -1.0;
    final paint = Paint()
      ..color = col
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    for (int fi = 0; fi < flagCount; fi++) {
      final fy0 = syEnd + sign * fi * gap * 0.55;
      final p0 = Offset(sx, fy0);
      final p1 = Offset(sx + fw * 0.9, fy0 + sign * fh * 0.07);
      final p2 = Offset(sx + fw, fy0 + sign * fh * 0.22);
      final p3 = Offset(sx + fw * 0.65, fy0 + sign * fh * 0.62);
      final p4 = Offset(sx + fw * 0.1, fy0 + sign * fh * 1.0);
      final m01 = Offset((p0.dx + p1.dx) / 2, (p0.dy + p1.dy) / 2);
      final m12 = Offset((p1.dx + p2.dx) / 2, (p1.dy + p2.dy) / 2);
      final m23 = Offset((p2.dx + p3.dx) / 2, (p2.dy + p3.dy) / 2);
      final m34 = Offset((p3.dx + p4.dx) / 2, (p3.dy + p4.dy) / 2);
      final path = Path()..moveTo(p0.dx, p0.dy);
      path.lineTo(m01.dx, m01.dy);
      path.quadraticBezierTo(p1.dx, p1.dy, m12.dx, m12.dy);
      path.quadraticBezierTo(p2.dx, p2.dy, m23.dx, m23.dy);
      path.quadraticBezierTo(p3.dx, p3.dy, m34.dx, m34.dy);
      path.quadraticBezierTo(p4.dx, p4.dy, p4.dx, p4.dy);
      canvas.drawPath(path, paint);
    }
  }

  void _drawRestSymbolMelody(
    Canvas canvas, double x, double cy,
    String dur, double gap, Color col, double trebleTop,
  ) {
    final paint = Paint()..color = col;
    if (dur == 'w') {
      final rw = gap * 1.3;
      canvas.drawRect(
        Rect.fromLTWH(x - rw / 2, trebleTop + gap, rw, gap * 0.48), paint,
      );
    } else if (dur == 'h') {
      final rw = gap * 1.3;
      final rh = gap * 0.48;
      canvas.drawRect(Rect.fromLTWH(x - rw / 2, cy - rh, rw, rh), paint);
    } else if (dur == 'q') {
      final lp = Paint()..color = col..strokeWidth = 1.8..style = PaintingStyle.stroke;
      final r = gap * 0.35;
      final y0 = cy - gap * 0.75;
      final pts = [
        Offset(x + r, y0), Offset(x - r * 0.4, y0 + gap * 0.5),
        Offset(x + r * 0.8, y0 + gap * 0.9), Offset(x, y0 + gap * 1.25),
        Offset(x - r * 0.5, y0 + gap * 1.55),
      ];
      for (int k = 0; k < pts.length - 1; k++) { canvas.drawLine(pts[k], pts[k + 1], lp); }
    } else if (dur == 'e' || dur == 'et') {
      final dr = math.max(3.5, gap * 0.43);
      final span = gap * 2.4;
      final xt = x + gap * 0.3;
      final yt = cy - span * 0.5;
      final xb = x - gap * 0.2;
      final yb = cy + span * 0.5;
      canvas.drawLine(Offset(xt, yt), Offset(xb, yb),
          Paint()..color = col..strokeWidth = 2.2);
      const t = 0.24;
      canvas.drawCircle(
        Offset(xt + (xb - xt) * t - dr * 0.65, yt + (yb - yt) * t), dr, paint,
      );
    } else if (dur == 's') {
      final dr = math.max(2.8, gap * 0.35);
      final span = gap * 3.0;
      final xt = x + gap * 0.3;
      final yt = cy - span * 0.5;
      final xb = x - gap * 0.2;
      final yb = cy + span * 0.5;
      canvas.drawLine(Offset(xt, yt), Offset(xb, yb),
          Paint()..color = col..strokeWidth = 2.2);
      for (final t in [0.18, 0.44]) {
        canvas.drawCircle(
          Offset(xt + (xb - xt) * t - dr * 0.65, yt + (yb - yt) * t), dr, paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _MiniStaffPainter oldDelegate) {
    if (oldDelegate.intervalMelodyMode != intervalMelodyMode) return true;
    if (oldDelegate.intervalPlayingIdx != intervalPlayingIdx) return true;
    if (oldDelegate.intervalMelodyNotes.length != intervalMelodyNotes.length) return true;
    if (oldDelegate.keySignatureCount != keySignatureCount) return true;
    if (oldDelegate.keySignaturePreferFlats != keySignaturePreferFlats) {
      return true;
    }
    if (oldDelegate.notes.length != notes.length) return true;
    if (oldDelegate.extras.length != extras.length) return true;
    if (oldDelegate.generationRhNotes.length != generationRhNotes.length) {
      return true;
    }
    if (oldDelegate.generationLhNotes.length != generationLhNotes.length) {
      return true;
    }
    if (!setEquals(
        oldDelegate.generationPlayingNotes, generationPlayingNotes)) {
      return true;
    }
    if (oldDelegate.generationGuitarMode != generationGuitarMode) return true;
    if (oldDelegate.scaleRhNotes.length != scaleRhNotes.length) return true;
    if (oldDelegate.scaleLhNotes.length != scaleLhNotes.length) return true;
    if (oldDelegate.scaleCurrentNote != scaleCurrentNote) return true;
    if (oldDelegate.scaleCurrentIsLeft != scaleCurrentIsLeft) return true;
    if (oldDelegate.scaleGuitarMode != scaleGuitarMode) return true;
    for (int i = 0; i < notes.length; i += 1) {
      if (oldDelegate.notes[i] != notes[i]) return true;
    }
    for (int i = 0; i < scaleRhNotes.length; i += 1) {
      if (oldDelegate.scaleRhNotes[i] != scaleRhNotes[i]) return true;
    }
    for (int i = 0; i < scaleLhNotes.length; i += 1) {
      if (oldDelegate.scaleLhNotes[i] != scaleLhNotes[i]) return true;
    }
    for (int i = 0; i < generationRhNotes.length; i += 1) {
      if (oldDelegate.generationRhNotes[i] != generationRhNotes[i]) return true;
    }
    for (int i = 0; i < generationLhNotes.length; i += 1) {
      if (oldDelegate.generationLhNotes[i] != generationLhNotes[i]) return true;
    }
    return false;
  }
}

class _MiniMetronomePainter extends CustomPainter {
  _MiniMetronomePainter({
    required this.beatsPerBar,
    required this.clicksPerBeat,
    required this.currentBeat,
    required this.running,
    required this.direction,
    required this.motionProgress,
    required this.timerEnabled,
    required this.timerRemaining,
  });

  final int beatsPerBar;
  final int clicksPerBeat;
  final int currentBeat;
  final bool running;
  final int direction;
  final double motionProgress;
  final bool timerEnabled;
  final Duration timerRemaining;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0F1621);
    canvas.drawRect(Offset.zero & size, bg);
    final count = math.max(1, beatsPerBar);
    final clicks = math.max(1, clicksPerBeat);
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    final spacing = count == 1 ? (right - left) : (right - left) / (count - 1);
    final xs = count == 1
        ? <double>[(left + right) * 0.5]
        : List<double>.generate(count, (i) => left + i * spacing);

    final rail = Paint()
      ..color = const Color(0xFF8F98A3)
      ..strokeWidth = 3;
    canvas.drawLine(Offset(left, axisY), Offset(right, axisY), rail);

    for (int k = 0; k <= clicks; k += 1) {
      final xTick = left + ((right - left) * (k / clicks));
      final isEnd = k == 0 || k == clicks;
      final tickH = isEnd ? 18.0 : 13.0;
      final tickPaint = Paint()
        ..color = isEnd ? const Color(0xFF9AA6B2) : const Color(0xFF747F8D)
        ..strokeWidth = isEnd ? 2.8 : 2.0;
      canvas.drawLine(
        Offset(xTick, axisY - (tickH / 2)),
        Offset(xTick, axisY + (tickH / 2)),
        tickPaint,
      );
    }

    final current = count > 0 ? ((currentBeat % count) + count) % count : 0;
    final baseR = (30 - (count * 0.75)).clamp(7.0, 24.0);
    final maxRBySpacing = (spacing * 0.42 - 2).clamp(6.0, 1000.0);
    final normalR = math.min(baseR, maxRBySpacing);
    final activeR = math.min(normalR + 2.0, maxRBySpacing + 1.5);
    for (int i = 0; i < xs.length; i += 1) {
      final x = xs[i];
      final active = running && i == current && currentBeat >= 0;
      final r = active ? activeR : normalR;
      canvas.drawCircle(
        Offset(x, yTop),
        r,
        Paint()
          ..color = active ? const Color(0xFFFFD24A) : const Color(0xFFC8A832),
      );
      canvas.drawCircle(
        Offset(x, yTop),
        r,
        Paint()
          ..color = active ? const Color(0xFFF3DA7A) : const Color(0xFF9F8427)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );
      final tp = TextPainter(
        text: TextSpan(
          text: '${i + 1}',
          style: TextStyle(
            color: const Color(0xFF1A1A1A),
            fontSize: (normalR * 0.82).clamp(8.0, 12.0),
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(x - (tp.width / 2), yTop - (tp.height / 2)));
    }

    final p = motionProgress.clamp(0.0, 1.0);
    final ballX = direction >= 0
        ? left + ((right - left) * p)
        : right - ((right - left) * p);
    final redBall = Paint()..color = const Color(0xFFFF4D4D);
    final redBallOutline = Paint()
      ..color = const Color(0xFFB61F1F)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;
    canvas.drawCircle(Offset(ballX, axisY), 11, redBall);
    canvas.drawCircle(Offset(ballX, axisY), 11, redBallOutline);

    if (timerEnabled) {
      final total = math.max(0, timerRemaining.inSeconds);
      final mm = (total ~/ 60).toString().padLeft(2, '0');
      final ss = (total % 60).toString().padLeft(2, '0');
      final tp = TextPainter(
        text: TextSpan(
          text: '$mm:$ss',
          style: TextStyle(
            color: const Color(0xFFFFB17A),
            fontSize: math.min(44.0, size.height * 0.24),
            fontWeight: FontWeight.w800,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      tp.paint(
        canvas,
        Offset(
          (size.width - tp.width) / 2,
          axisY + ((size.height - axisY) * 0.5) - (tp.height / 2),
        ),
      );
    } else if (!running) {
      final idle = TextPainter(
        text: const TextSpan(
          text: 'Pulsa Play para iniciar',
          style: TextStyle(
            color: Color(0xFF8090A8),
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      idle.paint(canvas, Offset((size.width - idle.width) / 2, axisY + 44));
    }
  }

  @override
  bool shouldRepaint(covariant _MiniMetronomePainter oldDelegate) {
    return oldDelegate.beatsPerBar != beatsPerBar ||
        oldDelegate.clicksPerBeat != clicksPerBeat ||
        oldDelegate.currentBeat != currentBeat ||
        oldDelegate.running != running ||
        oldDelegate.direction != direction ||
        oldDelegate.timerEnabled != timerEnabled ||
        oldDelegate.timerRemaining.inSeconds != timerRemaining.inSeconds ||
        (oldDelegate.motionProgress - motionProgress).abs() > 0.001;
  }
}

class _MiniTunerPainter extends CustomPainter {
  _MiniTunerPainter({
    required this.noteLabel,
    required this.cents,
    required this.currentFreq,
    required this.currentStringIdx,
    required this.tuningLabels,
  });

  final String noteLabel;
  final int cents;
  final double currentFreq;
  final int? currentStringIdx;
  final List<String> tuningLabels;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF000000);
    canvas.drawRect(Offset.zero & size, bg);

    final labels = tuningLabels.isEmpty
        ? const <String>['Mi', 'La', 'Re', 'Sol', 'Si', 'Mi']
        : tuningLabels;
    const ordinals = <String>['6', '5', '4', '3', '2', '1'];

    final padX = 20.0;
    final cardGap = math.max(6.0, math.min(12.0, size.width * 0.012));
    final cardsH = math.max(68.0, math.min(114.0, size.height * 0.34));
    final cardW = (size.width - (padX * 2) - (cardGap * 5)) / 6;
    final cardsY = 16.0;

    for (int i = 0; i < 6; i += 1) {
      final x = padX + i * (cardW + cardGap);
      final active = currentStringIdx == i;
      final fill = Paint()
        ..color = active ? const Color(0xFFF39C12) : const Color(0xFFD2D8DF);
      final rect = RRect.fromRectAndRadius(
        Rect.fromLTWH(x, cardsY, cardW, cardsH),
        Radius.circular(math.min(cardsH / 2, math.max(10, cardW * 0.26))),
      );
      canvas.drawRRect(rect, fill);

      final top = TextPainter(
        text: TextSpan(
          text: ordinals[i],
          style: TextStyle(
            color: active ? Colors.white : const Color(0xFF2B2E34),
            fontSize: 12,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: cardW - 4);
      top.paint(
        canvas,
        Offset(x + (cardW - top.width) / 2, cardsY + cardsH * 0.22),
      );

      final mid = TextPainter(
        text: TextSpan(
          text: labels[i % labels.length],
          style: TextStyle(
            color: active ? Colors.white : const Color(0xFF2B2E34),
            fontSize: 24,
            fontWeight: FontWeight.w800,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: cardW - 4);
      mid.paint(
        canvas,
        Offset(
          x + (cardW - mid.width) / 2,
          cardsY + cardsH * 0.54 - mid.height / 2,
        ),
      );
    }

    final liveText = currentFreq > 0.0
        ? '$noteLabel (${currentFreq.toStringAsFixed(1)} Hz)'
        : noteLabel;
    final live = TextPainter(
      text: TextSpan(
        text: liveText,
        style: const TextStyle(
          color: Color(0xFFFF9E34),
          fontSize: 30,
          fontWeight: FontWeight.w800,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: size.width - 24);
    live.paint(
      canvas,
      Offset((size.width - live.width) / 2, cardsY + cardsH + 18),
    );

    final meterTop = cardsY + cardsH + 68;
    final meterBottom = meterTop + 46;
    final meterLeft = 24.0;
    final meterRight = size.width - 24.0;
    final meterRect = RRect.fromRectAndRadius(
      Rect.fromLTRB(meterLeft, meterTop, meterRight, meterBottom),
      const Radius.circular(23),
    );
    canvas.drawRRect(meterRect, Paint()..color = const Color(0xFFC8C8CA));
    final centerX = (meterLeft + meterRight) / 2;
    canvas.drawLine(
      Offset(centerX, meterTop + 2),
      Offset(centerX, meterBottom - 2),
      Paint()
        ..color = const Color(0xFF16A05F)
        ..strokeWidth = 4,
    );
    final limited = cents.clamp(-50, 50).toDouble();
    final knobX = meterLeft + ((limited + 50) / 100) * (meterRight - meterLeft);
    canvas.drawCircle(
      Offset(knobX, (meterTop + meterBottom) / 2),
      12,
      Paint()..color = const Color(0xFFFF5A2F),
    );

    if (currentStringIdx != null) {
      final cText = TextPainter(
        text: TextSpan(
          text: '${cents >= 0 ? '+' : ''}$cents cents',
          style: const TextStyle(
            color: Color(0xFF9FB2C8),
            fontSize: 13,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: size.width - 24);
      cText.paint(
        canvas,
        Offset((size.width - cText.width) / 2, meterBottom + 10),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _MiniTunerPainter oldDelegate) {
    if (oldDelegate.noteLabel != noteLabel) return true;
    if (oldDelegate.cents != cents) return true;
    if ((oldDelegate.currentFreq - currentFreq).abs() > 0.01) return true;
    if (oldDelegate.currentStringIdx != currentStringIdx) return true;
    if (oldDelegate.tuningLabels.length != tuningLabels.length) return true;
    for (int i = 0; i < tuningLabels.length; i += 1) {
      if (oldDelegate.tuningLabels[i] != tuningLabels[i]) return true;
    }
    return false;
  }
}

class _MiniTunerSpectrumPainter extends CustomPainter {
  _MiniTunerSpectrumPainter({
    required this.rangeMinHz,
    required this.rangeMaxHz,
    required this.currentFreq,
    required this.currentStringIdx,
    required this.tuningLabels,
    required this.tuningFreqs,
    required this.spectrumBins,
  });

  final double rangeMinHz;
  final double rangeMaxHz;
  final double currentFreq;
  final int? currentStringIdx;
  final List<String> tuningLabels;
  final List<double> tuningFreqs;
  final List<double> spectrumBins;

  double _midiToFreq(int midi) => 440.0 * math.pow(2.0, (midi - 69) / 12.0);
  double _freqToMidi(double freq) =>
      69 + 12 * (math.log(freq / 440.0) / math.ln2);

  String _noteNameFromPc(int pc) {
    const names = <String>[
      'C',
      'C#',
      'D',
      'D#',
      'E',
      'F',
      'F#',
      'G',
      'G#',
      'A',
      'A#',
      'B',
    ];
    return names[((pc % 12) + 12) % 12];
  }

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Offset.zero & size,
      Paint()..color = const Color(0xFF0F1621),
    );
    final outer = RRect.fromRectAndRadius(
      Rect.fromLTWH(10, 10, size.width - 20, size.height - 20),
      const Radius.circular(10),
    );
    canvas.drawRRect(outer, Paint()..color = const Color(0xFF0B1018));
    canvas.drawRRect(
      outer,
      Paint()
        ..color = const Color(0xFF2F3743)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.2,
    );

    final x1 = 42.0;
    final y1 = 12.0;
    final x2 = math.max(x1 + 1.0, size.width - 14.0);
    final y2 = math.max(y1 + 1.0, size.height - 30.0);
    final frameRect = Rect.fromLTRB(x1, y1, x2, y2);
    canvas.drawRect(frameRect, Paint()..color = const Color(0xFF10131A));
    canvas.drawRect(
      frameRect,
      Paint()
        ..color = const Color(0xFF465062)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.0,
    );

    final fmin = math.max(1.0, rangeMinHz);
    final fmaxRaw = math.max(10.0, rangeMaxHz);
    final fmax = fmaxRaw <= fmin + 1 ? (fmin + 1) : fmaxRaw;
    final logMin = math.log(fmin) / math.ln10;
    final logMax = math.log(fmax) / math.ln10;
    final hzTicks = <int>[
      70,
      80,
      90,
      100,
      120,
      140,
      160,
      200,
      250,
      315,
      400,
      500,
      630,
      800,
      1000,
      1250,
      1400,
      1600,
      2000,
      2500,
      3000,
    ];
    final majorHz = <int>{100, 200, 400, 800, 1000};

    double fx(double hz) {
      final safe = hz.clamp(fmin, fmax);
      final logHz = math.log(safe) / math.ln10;
      final ratio = (logHz - logMin) / math.max(1e-6, (logMax - logMin));
      return x1 + ratio.clamp(0.0, 1.0) * (x2 - x1);
    }

    for (final hz in hzTicks) {
      final h = hz.toDouble();
      if (h < fmin || h > fmax) continue;
      final x = fx(h);
      final isMajor = majorHz.contains(hz);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = isMajor ? const Color(0xFF293140) : const Color(0xFF1F2531)
          ..strokeWidth = 1,
      );
      if (isMajor) {
        final tp = TextPainter(
          text: TextSpan(
            text: '$hz',
            style: const TextStyle(color: Color(0xFF8F98A8), fontSize: 8),
          ),
          textDirection: TextDirection.ltr,
        )..layout();
        tp.paint(canvas, Offset(x - (tp.width / 2), y2 + 4));
      }
    }

    const whitePcs = <int>{0, 2, 4, 5, 7, 9, 11};
    final minMidi = math.max(0, _freqToMidi(fmin).floor() - 1);
    final maxMidi = math.min(127, _freqToMidi(fmax).ceil() + 1);
    for (int midi = minMidi; midi <= maxMidi; midi += 1) {
      final hz = _midiToFreq(midi);
      if (hz < fmin || hz > fmax) continue;
      final x = fx(hz);
      final isNatural = whitePcs.contains(midi % 12);
      final lineColor = isNatural
          ? const Color(0xFFFF9F2A)
          : const Color(0xFF8A5F22);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = lineColor
          ..strokeWidth = 1.0,
      );
      final label = _noteNameFromPc(midi % 12);
      final tp = TextPainter(
        text: TextSpan(
          text: label,
          style: TextStyle(
            color: isNatural
                ? const Color(0xFFFFBF6C)
                : const Color(0xFFB58A4F),
            fontSize: 7,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: 14);
      final labelY = y1 + (midi.isEven ? 8 : 18);
      tp.paint(canvas, Offset(x - (tp.width / 2), labelY));
    }

    if (spectrumBins.isNotEmpty) {
      final innerW = x2 - x1;
      final innerH = y2 - y1 - 6;
      final bars = spectrumBins.length;
      final barW = math.max(1.2, innerW / math.max(40, bars * 1.35));
      for (int i = 0; i < bars; i += 1) {
        final v = spectrumBins[i].clamp(0.0, 1.0);
        if (v <= 0.005) continue;
        final x = x1 + (innerW * (i / math.max(1, bars - 1)));
        final h = v * innerH;
        canvas.drawRect(
          Rect.fromLTWH(x, y2 - h, barW, h),
          Paint()..color = const Color(0xFF49B5FF),
        );
      }
    }

    final n = math.min(tuningLabels.length, tuningFreqs.length);
    for (int i = 0; i < n; i += 1) {
      final hz = tuningFreqs[i];
      if (hz < fmin || hz > fmax) continue;
      final x = fx(hz);
      final active = currentStringIdx == i;
      final color = active ? const Color(0xFFFFBF6C) : const Color(0xFFB58A4F);
      canvas.drawLine(
        Offset(x, y1 + 2),
        Offset(x, y2 - 2),
        Paint()
          ..color = color
          ..strokeWidth = active ? 2.0 : 1.2,
      );
      final tp = TextPainter(
        text: TextSpan(
          text: tuningLabels[i],
          style: TextStyle(
            color: color,
            fontSize: 9,
            fontWeight: active ? FontWeight.w700 : FontWeight.w600,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: 22);
      tp.paint(canvas, Offset(x - (tp.width / 2), y1 + (i.isEven ? 8 : 18)));
    }

    if (currentFreq > 0.0 && currentFreq >= fmin && currentFreq <= fmax) {
      final x = fx(currentFreq);
      final markerColor = const Color(0xFF49B5FF);
      canvas.drawLine(
        Offset(x, y1),
        Offset(x, y2),
        Paint()
          ..color = markerColor
          ..strokeWidth = 2.2,
      );
      canvas.drawCircle(Offset(x, y1 + 8), 3.5, Paint()..color = markerColor);
      final tp = TextPainter(
        text: TextSpan(
          text: '${currentFreq.toStringAsFixed(1)} Hz',
          style: const TextStyle(
            color: Color(0xFF7CC8FF),
            fontSize: 10,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout(maxWidth: math.max(80.0, x2 - x1));
      final dx = (x - (tp.width / 2)).clamp(x1, x2 - tp.width);
      tp.paint(canvas, Offset(dx, y1 + 2));
    } else if (spectrumBins.isEmpty || spectrumBins.every((v) => v < 0.01)) {
      final tp = TextPainter(
        text: const TextSpan(
          text: '-',
          style: TextStyle(
            color: Color(0xFF8796AB),
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(
        canvas,
        Offset((x1 + x2 - tp.width) / 2, (y1 + y2 - tp.height) / 2),
      );
    }

    final hzLabel = TextPainter(
      text: const TextSpan(
        text: 'Hz',
        style: TextStyle(
          color: Color(0xFFA0A8B7),
          fontSize: 9,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    hzLabel.paint(
      canvas,
      Offset(((x1 + x2) / 2) - (hzLabel.width / 2), size.height - 16),
    );
  }

  @override
  bool shouldRepaint(covariant _MiniTunerSpectrumPainter oldDelegate) {
    if ((oldDelegate.rangeMinHz - rangeMinHz).abs() > 0.01) return true;
    if ((oldDelegate.rangeMaxHz - rangeMaxHz).abs() > 0.01) return true;
    if ((oldDelegate.currentFreq - currentFreq).abs() > 0.01) return true;
    if (oldDelegate.currentStringIdx != currentStringIdx) return true;
    if (oldDelegate.tuningLabels.length != tuningLabels.length) return true;
    if (oldDelegate.tuningFreqs.length != tuningFreqs.length) return true;
    if (oldDelegate.spectrumBins.length != spectrumBins.length) return true;
    for (int i = 0; i < tuningLabels.length; i += 1) {
      if (oldDelegate.tuningLabels[i] != tuningLabels[i]) return true;
    }
    for (int i = 0; i < tuningFreqs.length; i += 1) {
      if ((oldDelegate.tuningFreqs[i] - tuningFreqs[i]).abs() > 0.001) {
        return true;
      }
    }
    for (int i = 0; i < spectrumBins.length; i += 1) {
      if ((oldDelegate.spectrumBins[i] - spectrumBins[i]).abs() > 0.01) {
        return true;
      }
    }
    return false;
  }
}
