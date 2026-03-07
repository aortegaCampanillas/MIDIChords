import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_audio_capture/flutter_audio_capture.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_midi_command/flutter_midi_command.dart';

void main() {
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
      title: 'MIDIChords',
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
    return Scaffold(
      backgroundColor: const Color(0xFF202834),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF273140),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFF56627A)),
                ),
                child: const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    Icon(
                      Icons.tablet_mac_outlined,
                      color: Color(0xFFF3BF2F),
                      size: 44,
                    ),
                    SizedBox(height: 12),
                    Text(
                      'MIDIChords está disponible solo para tablets',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Color(0xFFE9EDF2),
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    SizedBox(height: 10),
                    Text(
                      'Abre la aplicación en un iPad o tablet Android para continuar.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Color(0xFFA8B6C8),
                        fontSize: 15,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const Color _bgTop = Color(0xFF2A3442);
  static const Color _bgBottom = Color(0xFF202834);
  static const Color _panelA = Color(0xFF313C4C);
  static const Color _panelB = Color(0xFF273140);
  static const Color _surfaceDark = Color(0xFF182535);
  static const Color _border = Color(0xFF56627A);
  static const Color _text = Color(0xFFE9EDF2);
  static const Color _muted = Color(0xFFA8B6C8);
  static const Color _accent = Color(0xFFF3BF2F);
  final TextEditingController _detectionOutputController =
      TextEditingController(text: 'Sin resultados');
  final TextEditingController _chordOutputController = TextEditingController(
    text: 'Sin resultados',
  );
  final TextEditingController _scaleOutputController = TextEditingController(
    text: 'Sin resultados',
  );

  int _tabIndex = 0;
  bool _requestInFlight = false;
  String _instrumentView = 'piano';

  String _language = 'es';
  String _accidental = 'sharp';
  String _guitarHandedness = 'right';

  List<Map<String, dynamic>> _chordPatterns = <Map<String, dynamic>>[];
  List<Map<String, dynamic>> _scalePatterns = <Map<String, dynamic>>[];

  int _chordRootPc = 0;
  String _chordSuffix = '';
  int _chordInversion = 0;
  int _chordMaxInversion = 0;
  int _chordGuitarVariant = 0;
  bool _generationPlayPressed = false;
  final Set<int> _generationInputStaffNotes = <int>{};
  final Map<int, AudioPlayer> _heldChordPlayers = <int, AudioPlayer>{};
  final Map<int, AudioPlayer> _heldInputPlayers = <int, AudioPlayer>{};
  final Map<int, AudioPlayer> _heldMidiInputPlayers = <int, AudioPlayer>{};
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
  bool _midiInputEnabled = false;

  int _scaleTonicPc = 0;
  String _scalePatternName = 'Ionian';
  int _scaleBpm = 120;
  bool _scaleLoopRunning = false;
  bool _scaleMetronomeOnly = false;
  int _scaleLoopIndex = 0;
  int _scaleLoopDirection = 1;
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
  bool _detectionPlayPressed = false;
  bool _inputDragActive = false;
  int? _dragPointer;
  int? _dragCurrentNote;
  Offset? _dragLastGlobalPos;
  DateTime _dragLastSwitchAt = DateTime.fromMillisecondsSinceEpoch(0);
  final Set<int> _forbiddenFlashNotes = <int>{};
  final Map<int, Timer> _forbiddenFlashTimers = <int, Timer>{};

  List<int> _enabledModeIndexes() {
    return _kEnableMobileTuner
        ? const <int>[0, 1, 2, 3, 4]
        : const <int>[0, 1, 2, 3];
  }

  String _modeLabel(int index) {
    switch (index) {
      case 0:
        return 'Detección de Acordes';
      case 1:
        return 'Generación de Acordes';
      case 2:
        return 'Escalas';
      case 3:
        return 'Metrónomo';
      case 4:
        return 'Afinador';
      default:
        return 'Detección de Acordes';
    }
  }

  Future<void> _openSettingsPanel() async {
    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return AlertDialog(
          backgroundColor: _panelA,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: _border),
          ),
          title: const Text(
            'Configuración',
            style: TextStyle(color: _text, fontWeight: FontWeight.w700),
          ),
          content: SizedBox(
            width: 420,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                DropdownButtonFormField<String>(
                  key: ValueKey<String>('settings_lang_$_language'),
                  initialValue: _language,
                  dropdownColor: _surfaceDark,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(labelText: 'Idioma'),
                  items: const <DropdownMenuItem<String>>[
                    DropdownMenuItem<String>(
                      value: 'es',
                      child: Text('Español'),
                    ),
                    DropdownMenuItem<String>(
                      value: 'en',
                      child: Text('English'),
                    ),
                  ],
                  onChanged: (value) async {
                    if (value == null) {
                      return;
                    }
                    setState(() => _language = value);
                    await _loadMeta();
                  },
                ),
              ],
            ),
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cerrar'),
            ),
          ],
        );
      },
    );
  }

  @override
  void initState() {
    super.initState();
    _initMidiInput();
    unawaited(_initPlatformAudioWorkarounds());
    _loadMeta();
  }

  @override
  void dispose() {
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
    var bestScore = -999;
    var bestComplexity = -999;
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
        if (score > bestScore ||
            (score == bestScore && complexity > bestComplexity)) {
          bestScore = score;
          bestComplexity = complexity;
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
      return <String, dynamic>{
        'name': _noteNameLocal(
          single,
          language: language,
          preferFlat: preferFlat,
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
    final rootName = _spellByDegree(
      rootPc: root,
      targetPc: root,
      degree: 0,
      language: language,
      preferFlats: preferFlat,
      midiNote: root,
      withOctave: false,
    );
    var chordName = '$rootName$suffix';
    if (bassPc != null && bassPc != root) {
      final bassDegree = degreeByPc[bassPc];
      final bassName = bassDegree == null
          ? _noteNameLocal(
              bassPc,
              language: language,
              preferFlat: preferFlat,
              withOctave: false,
            )
          : _spellByDegree(
              rootPc: root,
              targetPc: bassPc,
              degree: bassDegree,
              language: language,
              preferFlats: preferFlat,
              midiNote: bassPc,
              withOctave: false,
            );
      chordName = '$chordName/$bassName';
    }
    final expectedPcs = intervals.map((i) => _positiveMod12(root + i)).toSet();
    final extras = midiNotes
        .where((n) => !expectedPcs.contains(n % 12))
        .toList();
    final noteLabels = midiNotes.map((n) {
      final degree = degreeByPc[n % 12];
      if (degree == null) {
        return _noteNameLocal(
          n,
          language: language,
          preferFlat: preferFlat,
          withOctave: true,
        );
      }
      return _spellByDegree(
        rootPc: root,
        targetPc: n % 12,
        degree: degree,
        language: language,
        preferFlats: preferFlat,
        midiNote: n,
        withOctave: true,
      );
    }).toList();
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
      if (_tabIndex == 1 && !_requestInFlight) {
        unawaited(_callGenerateChord());
      } else if (_tabIndex == 2 && !_requestInFlight) {
        unawaited(_callGenerateScale());
      }
    } catch (err) {
      _detectionOutputController.text = 'Error cargando meta: $err';
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

  String _intervalTextFromMidiList(List<int> notes) {
    if (notes.isEmpty) return '-';
    final sorted = notes.toList()..sort();
    final root = sorted.first;
    return sorted.map((n) => '+${n - root}').join(' - ');
  }

  Set<int> get _activeDetectionNotes => _detectionMidiHeldNotes.isNotEmpty
      ? _detectionMidiHeldNotes
      : _detectionSelectedNotes;

  void _initMidiInput() {
    _midiDataSub = _midiCommand.onMidiDataReceived?.listen(_onMidiPacket);
    _midiSetupSub = _midiCommand.onMidiSetupChanged?.listen((_) {
      if (_midiInputEnabled) {
        unawaited(_refreshMidiConnections());
      }
    });
  }

  void _onMidiPacket(MidiPacket packet) {
    if (!_midiInputEnabled || _tabIndex != 0) return;
    final bytes = packet.data;
    for (var i = 0; i + 2 < bytes.length; i += 3) {
      final status = bytes[i] & 0xF0;
      final note = bytes[i + 1];
      final velocity = bytes[i + 2];
      final isNoteOn = status == 0x90 && velocity > 0;
      final isNoteOff = status == 0x80 || (status == 0x90 && velocity == 0);
      if (!isNoteOn && !isNoteOff) continue;
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
    if (mounted) setState(() {});
    if (!_requestInFlight) {
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
    } catch (_) {}
    if (mounted) setState(() {});
  }

  Future<void> _disableMidiInput() async {
    _midiInputEnabled = false;
    for (final device in _midiConnectedDevices.values.toList()) {
      try {
        _midiCommand.disconnectDevice(device);
      } catch (_) {}
    }
    _midiConnectedDevices.clear();
    _detectionMidiHeldNotes.clear();
    _stopHeldMidiInputs();
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
    if (_tabIndex == 0) {
      if (_detectionResultJson != null) {
        final midi = _extractMidiList(_detectionResultJson!, <String>[
          'notes_midi',
        ]);
        if (midi.isNotEmpty) return midi.toSet();
      }
      return _activeDetectionNotes;
    }
    if (_tabIndex == 1 && _generatedChordJson != null) {
      final rh = _extractMidiList(_generatedChordJson!, <String>['notes_midi']);
      if (_instrumentView == 'guitar') {
        final selected = _selectedChordGuitarNotes();
        return selected.isNotEmpty ? selected : rh.toSet();
      }
      final lh = rh.map((n) => n - 12).where((n) => n >= 0);
      return <int>{...rh, ...lh};
    }
    if (_tabIndex == 2 && _generatedScaleJson != null) {
      final rh = _scaleRhNotes();
      final lh = _scaleLhNotes(rh);
      return <int>{...rh, ...lh};
    }
    return <int>{};
  }

  Set<int> _generationPlayingNotesForStaff() {
    if (_tabIndex != 1) return <int>{};
    final rh = <int>{..._heldChordPlayers.keys, ..._generationInputStaffNotes};
    if (_instrumentView == 'guitar') return rh;
    final lh = rh.map((n) => n - 12).where((n) => n >= 0);
    return <int>{...rh, ...lh};
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
    if (_tabIndex == 0) return _activeDetectionNotes;
    if (_tabIndex == 1 && _generatedChordJson != null) {
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
    if (_tabIndex == 2 && _generatedScaleJson != null) {
      final rh = _scaleRhNotes();
      final lh = _scaleLhNotes(rh);
      final notes = <int>{...rh};
      notes.addAll(lh);
      if (_scaleCurrentNote != null) {
        notes.add(_scaleCurrentNote!);
      }
      if (_instrumentView == 'piano' && _scaleInputRawNote != null) {
        notes.add(_scaleInputRawNote!);
      }
      return notes;
    }
    return <int>{};
  }

  int? _generationStaffNoteForPitch(int note, {required bool includeBass}) {
    if (_generatedChordJson == null) return null;
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
    if (_tabIndex != 1 || _generatedChordJson == null) {
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
    if (_tabIndex != 1 || _generatedChordJson == null) {
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
    return _scaleBaseNotes();
  }

  List<int> _scaleLhNotes(List<int> rh) => rh
      .map((n) => n - 12)
      .where((n) => n >= 0 && (rh.isEmpty || n < rh.first))
      .toList();

  int? _scaleStaffNoteForPitch(int note, {bool includeBass = true}) {
    if (_generatedScaleJson == null) return null;
    final target = note;
    final rh = _scaleRhNotes();
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
    final rh = _scaleRhNotes();
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
    for (int i = 0; i < totalSamples; i += 1) {
      final t = i / sampleRate;
      final decayFactor = math
          .pow(decayBase, t * (isGuitar ? 8.3 : 5.3))
          .toDouble();
      final env = t < attack ? (t / attack) : decayFactor;
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
    if (!_audioPlaybackAvailable) {
      if (gain > 0.02) {
        SystemSound.play(SystemSoundType.click);
      }
      return null;
    }

    final targetVolume = ((lowVolume ? 0.68 : 1.0) * gain).clamp(0.0, 1.0);
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
    final player = AudioPlayer();
    player.positionUpdater = null;
    try {
      // audioplayers on Android cannot play BytesSource in lowLatency mode.
      await player.setPlayerMode(PlayerMode.mediaPlayer);
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
        final key =
            '${_safeMidi(midi)}|$instrument|${(seconds * 1000).round()}';
        final cachedPath = _toneFileCache[key];
        String filePath;
        if (cachedPath != null && await File(cachedPath).exists()) {
          filePath = cachedPath;
        } else {
          final file = File('${Directory.systemTemp.path}/midichords_$key.wav');
          await file.writeAsBytes(wavBytes, flush: true);
          filePath = file.path;
          _toneFileCache[key] = filePath;
        }
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
    if (_metronomeSampleAvailable) {
      final samplePlayer = AudioPlayer();
      samplePlayer.positionUpdater = null;
      final baseRate = switch (level) {
        2 => 1.68,
        1 => 1.24,
        _ => 0.94,
      };
      try {
        await samplePlayer.setPlayerMode(PlayerMode.mediaPlayer);
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
      await player.setPlayerMode(PlayerMode.mediaPlayer);
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
      await player.setPlayerMode(PlayerMode.mediaPlayer);
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
        await player.setSource(AssetSource(assetPath));
        if ((clampedRate - 1.0).abs() > 0.001) {
          try {
            await player.setPlaybackRate(clampedRate);
          } catch (_) {
            // Keep sample playback even if transposition is unsupported.
          }
        }
        await player.setVolume(volume);
        await player.resume();
        final ttlMs = ((durationSeconds.clamp(0.1, 2.2) * 1000) + 320)
            .round()
            .clamp(220, 3200);
        Timer(Duration(milliseconds: ttlMs), () {
          unawaited(_safeStopDispose(player));
        });
        return player;
      }
      await player.play(AssetSource(assetPath), volume: volume);
      if ((clampedRate - 1.0).abs() > 0.001) {
        try {
          await player.setPlaybackRate(clampedRate);
        } catch (_) {
          // Keep sample playback even if transposition is unsupported.
        }
      }
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

  Future<void> _handleInstrumentNote(int midi, {required bool pressed}) async {
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
    if (_tabIndex == 1 && _generatedChordJson != null) {
      final chordNotes = _extractMidiList(_generatedChordJson!, <String>[
        'notes_midi',
      ]);
      final allowed = _instrumentView == 'guitar'
          ? chordNotes.map((n) => n % 12).toSet().contains(midi % 12)
          : <int>{
              ...chordNotes,
              ...chordNotes.map((n) => n - 12),
            }.contains(midi);
      if (!allowed) return;
      final staffNote = _generationStaffNoteForPitch(
        midi,
        includeBass: _instrumentView != 'guitar',
      );
      if (staffNote != null) {
        _generationInputStaffNotes
          ..clear()
          ..add(staffNote);
        setState(() {});
      }
      if (pressed) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
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
    if (_tabIndex == 2 && _generatedScaleJson != null) {
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
      if (_tabIndex == 1) {
        _generationInputStaffNotes.clear();
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
    if (_tabIndex == 1) {
      _generationInputStaffNotes.clear();
    }
    if (_tabIndex == 2 && _scaleInputRawNote != null) {
      setState(() => _scaleInputRawNote = null);
    }
    if (mounted) {
      setState(() {});
    }
  }

  void _stopHeldChord() {
    for (final entry in _heldChordPlayers.entries) {
      unawaited(_safeStopDispose(entry.value));
    }
    _heldChordPlayers.clear();
  }

  void _stopHeldInputs() {
    for (final entry in _heldInputPlayers.entries) {
      unawaited(_safeStopDispose(entry.value));
    }
    _heldInputPlayers.clear();
  }

  void _stopHeldMidiInputs() {
    for (final entry in _heldMidiInputPlayers.entries) {
      unawaited(_safeStopDispose(entry.value));
    }
    _heldMidiInputPlayers.clear();
  }

  Future<void> _startHeldChord(
    List<int> notes, {
    required String instrument,
  }) async {
    _stopHeldChord();
    final chordNotes = notes.map(_safeMidi).toSet().toList()..sort();
    if (Platform.isAndroid && chordNotes.length > 1) {
      await _playAndroidSynthChord(
        notes: chordNotes,
        instrument: instrument,
        durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round(),
        volume: 0.92,
      );
      if (mounted) {
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
    final player = await _playTone(
      midi: midi,
      instrument: instrument,
      durationSeconds: instrument == 'guitar' ? 1.05 : 0.95,
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
    final player = await _playTone(
      midi: midi,
      instrument: instrument,
      durationSeconds: instrument == 'guitar' ? 1.05 : 0.95,
    );
    if (player != null) {
      _heldMidiInputPlayers[midi] = player;
    }
  }

  void _releaseHeldInputNote(int midi) {
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
          'Acorde: ${json['name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'Sobrantes: ${(json['extras'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'Intervalos: ${_intervalTextFromMidiList(detectedMidi)}';
    } catch (err) {
      _detectionOutputController.text = 'Error: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
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
      final generatedMidi = _extractMidiList(json, <String>['notes_midi']);
      _chordOutputController.text =
          'Acorde: ${json['name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'Intervalos: ${_intervalTextFromMidiList(generatedMidi)}';
    } catch (err) {
      _chordOutputController.text = 'Error: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
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
      final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
      _scaleGuitarStartNote = scaleMidi.isNotEmpty ? scaleMidi.first : null;
      _scaleInputRawNote = null;
      _scaleCurrentNote = null;
      _scaleCurrentIsLeft = null;
      _scaleOutputController.text =
          'Escala: ${json['pattern_localized_name'] ?? json['pattern_name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'Intervalos: ${_intervalTextFromMidiList(scaleMidi)}';
    } catch (err) {
      _scaleOutputController.text = 'Error: $err';
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

  void _stepScaleLoop() {
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
    _scaleCurrentIsLeft = false;
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
    } else {
      unawaited(
        _playTone(
          midi: note,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
          durationSeconds: _instrumentView == 'guitar' ? 0.92 : 0.78,
          lowVolume: true,
        ),
      );
    }
    setState(() {});
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
    final midi = _scaleRhNotes();
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
    if (_tabIndex == 2) {
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
    setState(() {});
  }

  void _startMetronomeAnimation() {
    _metroAnimTimer?.cancel();
    _metroAnimTimer = Timer.periodic(const Duration(milliseconds: 16), (_) {
      if (!mounted || !_metroRunning) {
        return;
      }
      if (_tabIndex == 3) {
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
    final enabledModes = _enabledModeIndexes();
    final currentTab = enabledModes.contains(_tabIndex) ? _tabIndex : 0;
    if (currentTab != _tabIndex) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          setState(() => _tabIndex = currentTab);
        }
      });
    }
    final pages = <Widget>[
      _buildDetectionPage(),
      _buildChordGenerationPage(),
      _buildScaleGenerationPage(),
      _buildMetronomePage(),
      _buildTunerPage(),
    ];

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 74,
        centerTitle: false,
        titleSpacing: 12,
        title: Row(
          children: <Widget>[
            const Text('MIDIChords'),
            const SizedBox(width: 12),
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 360),
                  child: DropdownButtonFormField<int>(
                    key: ValueKey<String>(
                      'mode_${currentTab}_${_kEnableMobileTuner ? 1 : 0}',
                    ),
                    initialValue: currentTab,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: const InputDecoration(
                      hintText: 'Modo',
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 10,
                      ),
                      isDense: true,
                    ),
                    items: enabledModes
                        .map(
                          (i) => DropdownMenuItem<int>(
                            value: i,
                            child: Text(_modeLabel(i)),
                          ),
                        )
                        .toList(),
                    onChanged: (value) {
                      if (value == null) return;
                      if (!_kEnableMobileTuner && value == 4) return;
                      setState(() {
                        _tabIndex = value;
                        if (value == 0) {
                          _instrumentView = 'piano';
                        }
                      });
                      if (value != 2) {
                        _stopScaleLoop();
                      }
                      if (value != 3) {
                        _stopMetronome();
                      }
                      if (value != 4 && _tunerRunning) {
                        unawaited(_stopTuner());
                      }
                      _stopHeldChord();
                      _stopHeldInputs();
                      _stopHeldMidiInputs();
                      _generationInputStaffNotes.clear();
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
                        unawaited(_callGenerateScale());
                      }
                    },
                  ),
                ),
              ),
            ),
          ],
        ),
        actions: <Widget>[
          Padding(
            padding: const EdgeInsets.only(right: 8),
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
              ),
              child: Text(_midiInputEnabled ? 'MIDI: On' : 'MIDI: Off'),
            ),
          ),
          Container(
            constraints: const BoxConstraints(minWidth: 76),
            margin: const EdgeInsets.only(right: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8),
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
                },
              ),
            ),
          ),
          IconButton(
            tooltip: 'Configuración',
            onPressed: _openSettingsPanel,
            icon: const Icon(Icons.settings),
          ),
          const SizedBox(width: 8),
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
        child: Column(children: <Widget>[Expanded(child: pages[currentTab])]),
      ),
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
    return Padding(
      padding: const EdgeInsets.all(12),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final wide = constraints.maxWidth >= 900;
          final top = wide
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(
                      flex: 57,
                      child: _buildStaffPanel(staffNotes, staffExtras),
                    ),
                    const SizedBox(width: 12),
                    Expanded(flex: 43, child: _panel(child: controls)),
                  ],
                )
              : Column(
                  children: <Widget>[
                    Expanded(
                      flex: 56,
                      child: _buildStaffPanel(staffNotes, staffExtras),
                    ),
                    const SizedBox(height: 12),
                    Expanded(flex: 44, child: _panel(child: controls)),
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
      3 => 'Metrónomo',
      4 => 'Afinador',
      _ => 'Pentagrama',
    };
    return _panel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            title,
            style: TextStyle(color: _muted, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF0F1621),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF3A4558)),
              ),
              child: switch (_tabIndex) {
                3 => CustomPaint(
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
                4 => CustomPaint(
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
                  painter: _MiniStaffPainter(
                    notes: notes.toList()..sort(),
                    extras: extras,
                    generationRhNotes:
                        (_tabIndex == 1 && _generatedChordJson != null)
                        ? _extractMidiList(_generatedChordJson!, <String>[
                            'notes_midi',
                          ])
                        : const <int>[],
                    generationLhNotes:
                        (_tabIndex == 1 &&
                            _instrumentView == 'piano' &&
                            _generatedChordJson != null)
                        ? _extractMidiList(_generatedChordJson!, <String>[
                            'notes_midi',
                          ]).map((n) => n - 12).where((n) => n >= 0).toList()
                        : const <int>[],
                    generationPlayingNotes: _tabIndex == 1
                        ? _generationPlayingNotesForStaff()
                        : const <int>{},
                    generationGuitarMode:
                        _tabIndex == 1 && _instrumentView == 'guitar',
                    scaleRhNotes: _tabIndex == 2
                        ? _scaleRhNotes()
                        : const <int>[],
                    scaleLhNotes: (_tabIndex == 2 && _instrumentView == 'piano')
                        ? _scaleLhNotes(_scaleRhNotes())
                        : const <int>[],
                    scaleCurrentNote: _tabIndex == 2 ? _scaleCurrentNote : null,
                    scaleCurrentIsLeft: _tabIndex == 2
                        ? _scaleCurrentIsLeft
                        : null,
                    scaleGuitarMode:
                        _tabIndex == 2 && _instrumentView == 'guitar',
                  ),
                  child: const SizedBox.expand(),
                ),
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstrumentPanel(Set<int> activeMidi) {
    final showRightControls = _tabIndex == 1 || _tabIndex == 2;
    final chordVariations = (_tabIndex == 1 && _instrumentView == 'guitar')
        ? _chordGuitarVariations()
        : const <Map<String, dynamic>>[];
    final chordVoicings = (_tabIndex == 1 && _instrumentView == 'guitar')
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
            height: 186,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Expanded(
                  child: _instrumentView == 'piano'
                      ? _buildPianoStrip(activeMidi)
                      : _buildGuitarStrip(
                          activeMidi,
                          chordVoicings: chordVoicings,
                          chordVariations: chordVariations,
                          chordVariant: safeVariant,
                        ),
                ),
                if (showRightControls) ...<Widget>[
                  const SizedBox(width: 10),
                  SizedBox(
                    width: 118,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: <Widget>[
                        _instToggle('piano', 'Piano'),
                        const SizedBox(height: 8),
                        _instToggle('guitar', 'Guitarra'),
                        if (_instrumentView == 'guitar') ...<Widget>[
                          const SizedBox(height: 8),
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
                        ],
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (_tabIndex == 1 && _instrumentView == 'guitar') ...<Widget>[
            const SizedBox(height: 8),
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
          ],
        ],
      ),
    );
  }

  Widget _instToggle(String key, String label) {
    final active = _instrumentView == key;
    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        backgroundColor: active ? _accent : _surfaceDark,
        side: BorderSide(color: active ? _accent : _border),
        foregroundColor: active ? const Color(0xFF1A222D) : _text,
      ),
      onPressed: () => setState(() => _instrumentView = key),
      child: Text(label),
    );
  }

  Widget _buildPianoStrip(Set<int> activeMidi) {
    final midiRange = List<int>.generate(37, (i) => 48 + i); // C3..C6
    final whiteMidi = midiRange
        .where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12))
        .toList();
    const whiteH = 130.0;
    final active = activeMidi.toSet();
    final extras = _instrumentExtrasForCurrentTab();
    final scaleRh = _tabIndex == 2 ? _scaleRhNotes().toSet() : <int>{};
    final scaleLh = (_tabIndex == 2 && _instrumentView == 'piano')
        ? _scaleLhNotes(_scaleRhNotes()).toSet()
        : <int>{};
    final chordGenPiano = _tabIndex == 1 && _instrumentView == 'piano';
    final chordRh = chordGenPiano && _generatedChordJson != null
        ? _extractMidiList(_generatedChordJson!, <String>['notes_midi'])
        : const <int>[];
    final chordLh = chordGenPiano
        ? chordRh.map((n) => n - 12).where((n) => n >= 0).toList()
        : const <int>[];
    final rhFinger = <int, int>{};
    final lhFinger = <int, int>{};
    for (int i = 0; i < chordRh.length; i += 1) {
      rhFinger[chordRh[i]] = math.min(5, i + 1);
    }
    for (int i = 0; i < chordLh.length; i += 1) {
      lhFinger[chordLh[i]] = math.max(1, 5 - i);
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

    return SizedBox(
      height: 140,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final viewportW = constraints.maxWidth;
          final whiteW = math.max(36.0, viewportW / whiteMidi.length);
          final blackW = whiteW * 0.6;
          final blackH = whiteH * 0.65;
          final keyboardW = whiteMidi.length * whiteW;

          double xForMidi(int midi) {
            final idx = whiteMidi.indexWhere((m) => m >= midi);
            final wIdx = idx < 0 ? whiteMidi.length - 1 : idx;
            return wIdx * whiteW;
          }

          return SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SizedBox(
              width: math.max(viewportW, keyboardW),
              child: Stack(
                children: <Widget>[
                  Row(
                    children: whiteMidi.map((midi) {
                      final isActive = active.contains(midi);
                      final isExtra = extras.contains(midi);
                      final isScaleCurrent =
                          _tabIndex == 2 &&
                          _scaleCurrentNote != null &&
                          _scaleCurrentNote == midi;
                      final currentIsLeft =
                          isScaleCurrent &&
                          _instrumentView == 'piano' &&
                          scaleLh.contains(midi) &&
                          !scaleRh.contains(midi);
                      final rh = rhFinger[midi];
                      final lh = lhFinger[midi];
                      return Listener(
                        onPointerDown: (event) => unawaited(
                          _beginInputDrag(midi, event.pointer, event.position),
                        ),
                        onPointerMove: (event) => unawaited(
                          _updateInputDrag(midi, event.pointer, event.position),
                        ),
                        onPointerUp: (event) => _endInputDrag(event.pointer),
                        onPointerCancel: (event) =>
                            _endInputDrag(event.pointer),
                        child: Container(
                          width: whiteW,
                          height: whiteH,
                          decoration: BoxDecoration(
                            color: isScaleCurrent
                                ? (currentIsLeft
                                      ? const Color(0xFFFF8A2B)
                                      : const Color(0xFF4DA3EA))
                                : (isExtra
                                      ? const Color(0xFFE04A4A)
                                      : (isActive
                                            ? const Color(0xFFF3C64F)
                                            : const Color(0xFFF5F4EF))),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: const Color(0xFFAEB8C5)),
                          ),
                          child: Stack(
                            children: <Widget>[
                              Align(
                                alignment: Alignment.bottomCenter,
                                child: Padding(
                                  padding: const EdgeInsets.only(bottom: 6),
                                  child: Text(
                                    _pcLabel(midi % 12),
                                    style: const TextStyle(
                                      color: Color(0xFF1A222D),
                                      fontWeight: FontWeight.w700,
                                      fontSize: 11,
                                    ),
                                  ),
                                ),
                              ),
                              if (chordGenPiano && rh != null)
                                marker(
                                  size: 22,
                                  color: const Color(0xFF33C6FF),
                                  digit: rh,
                                  top: 74,
                                  left: (whiteW - 22) / 2,
                                ),
                              if (chordGenPiano && rh == null && lh != null)
                                marker(
                                  size: 22,
                                  color: const Color(0xFFFF9E34),
                                  digit: lh,
                                  top: 74,
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
                            _tabIndex == 2 &&
                            _scaleCurrentNote != null &&
                            _scaleCurrentNote == midi;
                        final currentIsLeft =
                            isScaleCurrent &&
                            _instrumentView == 'piano' &&
                            scaleLh.contains(midi) &&
                            !scaleRh.contains(midi);
                        final rh = rhFinger[midi];
                        final lh = lhFinger[midi];
                        return Positioned(
                          left: xForMidi(midi) - (blackW / 2),
                          top: 0,
                          child: Listener(
                            onPointerDown: (event) => unawaited(
                              _beginInputDrag(
                                midi,
                                event.pointer,
                                event.position,
                              ),
                            ),
                            onPointerMove: (event) => unawaited(
                              _updateInputDrag(
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
                                color: isScaleCurrent
                                    ? (currentIsLeft
                                          ? const Color(0xFFB35F00)
                                          : const Color(0xFF0078D7))
                                    : (isExtra
                                          ? const Color(0xFFB33434)
                                          : (isActive
                                                ? const Color(0xFFC37B00)
                                                : const Color(0xFF101822))),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: const Color(0xFF6F7F96),
                                ),
                              ),
                              child: Stack(
                                children: <Widget>[
                                  Align(
                                    alignment: Alignment.bottomCenter,
                                    child: Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: SizedBox(
                                        width: blackW - 4,
                                        child: FittedBox(
                                          fit: BoxFit.scaleDown,
                                          child: Text(
                                            _pcLabel(midi % 12),
                                            maxLines: 1,
                                            softWrap: false,
                                            style: const TextStyle(
                                              color: Colors.white,
                                              fontWeight: FontWeight.w700,
                                              fontSize: 9,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
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
                      top: 48,
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
          );
        },
      ),
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
    const physicalTuning = <int>[40, 45, 50, 55, 59, 64]; // 6 -> 1
    final tuning = _guitarHandedness == 'right'
        ? physicalTuning.reversed
              .toList() // 1 -> 6 (arriba -> abajo)
        : physicalTuning;
    const fretCount = 14;
    const fretW = 78.0;
    const openFretW = fretW / 2;
    const stringGap = 25.0;
    final detectionMode = _tabIndex == 0;
    final chordMode = _tabIndex == 1;
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
    final selectedFrets = _guitarHandedness == 'right'
        ? rawFrets.reversed.toList()
        : rawFrets;
    final useFrets = selectedFrets.length >= 6;
    const openLeft = 40.0;
    final nutX = openLeft + openFretW;
    final boardWidth = (fretCount - 1) * fretW;
    final width = nutX + boardWidth;
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
                  left: openLeft,
                  top: 6,
                  right: 0,
                  child: SizedBox(
                    width: width - openLeft,
                    child: Row(
                      children: <Widget>[
                        SizedBox(
                          width: openFretW,
                          child: const Text(
                            '0',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 10,
                              color: Color(0xFFC9D4E4),
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        ...List<Widget>.generate(
                          fretCount - 1,
                          (i) => SizedBox(
                            width: fretW,
                            child: Text(
                              '${i + 1}',
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontSize: 10,
                                color: Color(0xFFC9D4E4),
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  left: openLeft,
                  top: 20,
                  child: Container(
                    width: openFretW,
                    height: (6 * stringGap) + 16,
                    color: const Color(0xFFF4F5F7),
                  ),
                ),
                Positioned(
                  left: nutX,
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
                    left: 0,
                    top: y - 7,
                    child: SizedBox(
                      width: 36,
                      child: Text(
                        _pcLabel(open % 12),
                        textAlign: TextAlign.right,
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
                    left: nutX + (f * fretW),
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
                    final x = (f == 0)
                        ? (openLeft + (openFretW * 0.5) - 11)
                        : (nutX + ((f - 0.5) * fretW) - 11);
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
    final midiSoundStyle = OutlinedButton.styleFrom(
      side: BorderSide(
        color: _midiInputSoundEnabled ? _accent : _border,
        width: _midiInputSoundEnabled ? 2 : 1,
      ),
      foregroundColor: _midiInputSoundEnabled ? const Color(0xFF1A222D) : _text,
      backgroundColor: _midiInputSoundEnabled ? _accent : null,
    );
    return _buildModeScaffold(
      controls: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Text(
            'Detección de acordes',
            style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
          ),
          const SizedBox(height: 4),
          const Text(
            'Pulsa notas en piano/guitarra para detectar acordes.',
            style: TextStyle(color: _muted),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: <Widget>[
              _holdPlayButton(
                enabled: hasNotes,
                active: _detectionPlayPressed,
                label: null,
                onDown: () async {
                  final notes = _activeDetectionNotes.toList()..sort();
                  if (notes.isEmpty) return;
                  setState(() => _detectionPlayPressed = true);
                  await _startHeldChord(notes, instrument: 'piano');
                },
                onUp: () {
                  _stopHeldChord();
                  if (mounted) {
                    setState(() => _detectionPlayPressed = false);
                  }
                },
              ),
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
                label: const Text('Limpiar'),
              ),
              OutlinedButton.icon(
                onPressed: () {
                  setState(() {
                    _midiInputSoundEnabled = !_midiInputSoundEnabled;
                    if (!_midiInputSoundEnabled) {
                      _stopHeldInputs();
                      _stopHeldMidiInputs();
                    }
                  });
                },
                icon: Icon(
                  _midiInputSoundEnabled ? Icons.volume_up : Icons.volume_off,
                ),
                label: Text(
                  _midiInputSoundEnabled
                      ? 'Reproducir entrada MIDI'
                      : 'Silenciar entrada MIDI',
                ),
                style: midiSoundStyle,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(child: _resultBlock(controller: _detectionOutputController)),
        ],
      ),
    );
  }

  Widget _buildChordGenerationPage() {
    return _buildModeScaffold(
      controls: Column(
        children: <Widget>[
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Generación de acordes',
              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: <Widget>[
              Expanded(
                child: DropdownButtonFormField<int>(
                  key: ValueKey<int>(_chordRootPc),
                  initialValue: _chordRootPc,
                  dropdownColor: _surfaceDark,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(labelText: 'Tónica'),
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
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: DropdownButtonFormField<String>(
                  key: ValueKey<String>('suffix_$_chordSuffix'),
                  initialValue: _chordSuffix,
                  dropdownColor: _surfaceDark,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(labelText: 'Variante'),
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
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: <Widget>[
              Expanded(
                child: DropdownButtonFormField<int>(
                  key: ValueKey<String>(
                    'inv_$_chordInversion/$_chordMaxInversion',
                  ),
                  initialValue: _chordInversion.clamp(0, _chordMaxInversion),
                  isExpanded: true,
                  dropdownColor: _surfaceDark,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(labelText: 'Inversión'),
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
            ],
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerLeft,
            child: _holdPlayButton(
              enabled:
                  _generatedChordJson != null &&
                  _extractMidiList(_generatedChordJson!, <String>[
                    'notes_midi',
                  ]).isNotEmpty,
              active: _generationPlayPressed,
              label: null,
              onDown: () async {
                final notes = _generatedChordJson == null
                    ? <int>[]
                    : _extractMidiList(_generatedChordJson!, <String>[
                        'notes_midi',
                      ]);
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
          const SizedBox(height: 8),
          Expanded(child: _resultBlock(controller: _chordOutputController)),
        ],
      ),
    );
  }

  Widget _buildScaleGenerationPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              children: <Widget>[
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Escalas',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    Expanded(
                      child: DropdownButtonFormField<int>(
                        key: ValueKey<int>(100 + _scaleTonicPc),
                        initialValue: _scaleTonicPc,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: const InputDecoration(labelText: 'Tónica'),
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
                          setState(() => _scaleTonicPc = value);
                          if (!_requestInFlight) {
                            unawaited(_callGenerateScale());
                          }
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 2,
                      child: DropdownButtonFormField<String>(
                        key: ValueKey<String>('scale_$_scalePatternName'),
                        initialValue: _scalePatternName,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: const InputDecoration(labelText: 'Escala'),
                        items: _scalePatterns
                            .map(
                              (p) => DropdownMenuItem<String>(
                                value: (p['name'] as String? ?? 'Ionian'),
                                child: Text(
                                  (p['localized_name'] as String? ??
                                      p['name'] as String? ??
                                      'Ionian'),
                                ),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value == null) {
                            return;
                          }
                          setState(() => _scalePatternName = value);
                          if (!_requestInFlight) {
                            unawaited(_callGenerateScale());
                          }
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: _scaleLoopRunning
                            ? _accent
                            : _surfaceDark,
                        foregroundColor: _scaleLoopRunning
                            ? const Color(0xFF1A222D)
                            : _text,
                      ),
                      onPressed: _toggleScaleLoop,
                      icon: Icon(
                        _scaleLoopRunning ? Icons.stop : Icons.play_arrow,
                      ),
                      label: Text(_scaleLoopRunning ? 'Stop' : 'Play'),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        backgroundColor: _scaleMetronomeOnly
                            ? _accent
                            : _surfaceDark,
                        foregroundColor: _scaleMetronomeOnly
                            ? const Color(0xFF1A222D)
                            : _text,
                        side: BorderSide(
                          color: _scaleMetronomeOnly ? _accent : _border,
                        ),
                      ),
                      onPressed: () {
                        setState(
                          () => _scaleMetronomeOnly = !_scaleMetronomeOnly,
                        );
                      },
                      child: const Text('⏱'),
                    ),
                  ],
                ),
                if (_scaleMetronomeOnly) ...<Widget>[
                  const SizedBox(height: 8),
                  Row(
                    children: <Widget>[
                      const SizedBox(
                        width: 74,
                        child: Text('Volumen', style: TextStyle(color: _muted)),
                      ),
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
                      SizedBox(width: 64, child: Text('$_metroVolume%')),
                    ],
                  ),
                ],
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    const Text('BPM'),
                    Expanded(
                      child: Slider(
                        min: 1,
                        max: 300,
                        divisions: 299,
                        value: _scaleBpm.toDouble(),
                        onChanged: (value) {
                          setState(() => _scaleBpm = value.round());
                        },
                      ),
                    ),
                    SizedBox(width: 64, child: Text('$_scaleBpm BPM')),
                  ],
                ),
                const SizedBox(height: 6),
                SizedBox(
                  height: 180,
                  child: _resultBlock(controller: _scaleOutputController),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMetronomePage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text(
                  'Configuración de Metrónomo',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                ),
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    const SizedBox(
                      width: 84,
                      child: Text(
                        'Volumen',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: _muted,
                        ),
                      ),
                    ),
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
                    SizedBox(width: 56, child: Text('$_metroVolume%')),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Tempo (BPM)',
                  style: TextStyle(fontWeight: FontWeight.w600, color: _muted),
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
                    SizedBox(width: 56, child: Text('$_metroBpm')),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    const Text('Pulsos por compás:'),
                    const SizedBox(width: 10),
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
                    DropdownButton<int>(
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
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    const Text('Subdivisión:'),
                    const SizedBox(width: 10),
                    Wrap(
                      spacing: 6,
                      children: <int>[1, 2, 3, 4, 6].map((n) {
                        final active = _metroClicksPerBeat == n;
                        return ChoiceChip(
                          selected: active,
                          label: _metronomeSubdivisionFigure(n, active: active),
                          onSelected: (_) {
                            setState(() => _metroClicksPerBeat = n);
                            if (_metroRunning) _startMetronome();
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    Checkbox(
                      visualDensity: VisualDensity.compact,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      value: _metroBarAccent,
                      onChanged: (value) {
                        setState(() => _metroBarAccent = value ?? true);
                      },
                    ),
                    const Text('Acento de compás'),
                  ],
                ),
                Row(
                  children: <Widget>[
                    Checkbox(
                      visualDensity: VisualDensity.compact,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      value: _metroTimerEnabled,
                      onChanged: (value) {
                        setState(() => _metroTimerEnabled = value ?? false);
                      },
                    ),
                    const Text('Temporizador'),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 72,
                      child: DropdownButton<int>(
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
                    const Text(' : '),
                    SizedBox(
                      width: 72,
                      child: DropdownButton<int>(
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
                const SizedBox(height: 12),
                FilledButton.icon(
                  style: FilledButton.styleFrom(
                    backgroundColor: _metroRunning ? _accent : _surfaceDark,
                    foregroundColor: _metroRunning
                        ? const Color(0xFF1A222D)
                        : _text,
                    minimumSize: const Size(0, 38),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 10,
                    ),
                    visualDensity: VisualDensity.compact,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  onPressed: _toggleMetronome,
                  icon: Icon(_metroRunning ? Icons.stop : Icons.play_arrow),
                  label: Text(
                    _metroRunning ? 'Detener metrónomo' : 'Iniciar metrónomo',
                  ),
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _metronomeSubdivisionFigure(int clicks, {required bool active}) {
    final fg = active ? const Color(0xFF1A222D) : _text;
    if (clicks == 3 || clicks == 6) {
      final glyph = clicks == 3 ? '♪♪♪' : '♬♬';
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Text(
            '3',
            style: TextStyle(
              color: fg,
              fontSize: 10,
              fontWeight: FontWeight.w800,
              height: 0.9,
            ),
          ),
          Text(
            glyph,
            style: TextStyle(
              color: fg,
              fontSize: 15,
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
                const Text(
                  'Configuración de Afinador',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                ),
                const SizedBox(height: 8),
                FilledButton.icon(
                  onPressed: _toggleTuner,
                  icon: Icon(_tunerRunning ? Icons.stop : Icons.play_arrow),
                  label: Text(
                    _tunerRunning ? 'Detener afinador' : 'Iniciar afinador',
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    const SizedBox(
                      width: 96,
                      child: Text(
                        'Afinación',
                        style: TextStyle(
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
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    const SizedBox(
                      width: 96,
                      child: Text(
                        'Ganancia',
                        style: TextStyle(
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
                const SizedBox(height: 6),
                Row(
                  children: <Widget>[
                    const SizedBox(
                      width: 96,
                      child: Text(
                        'Rango Hz',
                        style: TextStyle(
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
                const SizedBox(height: 12),
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

  Widget _resultBlock({required TextEditingController controller}) {
    return Container(
      width: double.infinity,
      height: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF17273A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF73829A)),
      ),
      child: ValueListenableBuilder<TextEditingValue>(
        valueListenable: controller,
        builder: (context, value, _) {
          return SingleChildScrollView(
            physics: const ClampingScrollPhysics(),
            child: SelectableText(
              value.text,
              style: const TextStyle(color: _text, fontSize: 16, height: 1.35),
            ),
          );
        },
      ),
    );
  }
}

class _MiniStaffPainter extends CustomPainter {
  _MiniStaffPainter({
    required this.notes,
    required this.extras,
    this.generationRhNotes = const <int>[],
    this.generationLhNotes = const <int>[],
    this.generationPlayingNotes = const <int>{},
    this.generationGuitarMode = false,
    this.scaleRhNotes = const <int>[],
    this.scaleLhNotes = const <int>[],
    this.scaleCurrentNote,
    this.scaleCurrentIsLeft,
    this.scaleGuitarMode = false,
  });

  final List<int> notes;
  final Set<int> extras;
  final List<int> generationRhNotes;
  final List<int> generationLhNotes;
  final Set<int> generationPlayingNotes;
  final bool generationGuitarMode;
  final List<int> scaleRhNotes;
  final List<int> scaleLhNotes;
  final int? scaleCurrentNote;
  final bool? scaleCurrentIsLeft;
  final bool scaleGuitarMode;

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

    final left = 52.0;
    final right = size.width - 16;
    final gap = math.max(10.0, math.min(16.0, size.height / 24));
    final grandGap = math.max(64.0, gap * 6.2);
    final systemH = grandGap + (4 * gap);
    final trebleTop = (size.height - systemH) / 2;
    final bassTop = trebleTop + grandGap;

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
    tpTreble.paint(canvas, Offset(left + 12, trebleTop + gap * 0.6));
    final tpBass = TextPainter(
      text: TextSpan(text: '𝄢', style: clefStyle),
      textDirection: TextDirection.ltr,
    )..layout();
    tpBass.paint(canvas, Offset(left + 14, bassTop + gap * 0.5));

    if (scaleRhNotes.isNotEmpty) {
      final pairCount = math.min(scaleRhNotes.length, scaleLhNotes.length);
      for (int degree = 0; degree < scaleRhNotes.length; degree += 1) {
        final x = left + 110 + (degree * 32.0);
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
            Rect.fromCenter(center: Offset(x, yBass), width: 16, height: 12),
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
          Rect.fromCenter(center: Offset(x, yTreble), width: 16, height: 12),
          noteOutline,
        );
      }
    } else {
      final list = notes.toList()..sort();
      final placedTrebleCols = <int, List<double>>{};
      final placedBassCols = <int, List<double>>{};
      final rhSet = generationRhNotes.toSet();
      final lhSet = generationLhNotes.toSet();
      const noteW = 16.0;
      const noteH = 12.0;
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
        final x = left + 110 + (col * noteW * 1.8);
        final ys = List<double>.from(placedCols[col] ?? const <double>[])
          ..add(y);
        placedCols[col] = ys;
        Color? fillColor;
        if (generationPlayingNotes.contains(midi)) {
          if (!generationGuitarMode &&
              lhSet.contains(midi) &&
              !rhSet.contains(midi)) {
            fillColor = const Color(0xFFFF8A2B);
            noteOutline.color = const Color(0xFFFFD2A7);
          } else {
            fillColor = const Color(0xFF4DA3EA);
            noteOutline.color = const Color(0xFFE9EDF2);
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

  @override
  bool shouldRepaint(covariant _MiniStaffPainter oldDelegate) {
    if (oldDelegate.notes.length != notes.length) return true;
    if (oldDelegate.extras.length != extras.length) return true;
    if (oldDelegate.generationRhNotes.length != generationRhNotes.length) {
      return true;
    }
    if (oldDelegate.generationLhNotes.length != generationLhNotes.length) {
      return true;
    }
    if (oldDelegate.generationPlayingNotes.length !=
        generationPlayingNotes.length) {
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
    for (final note in generationPlayingNotes) {
      if (!oldDelegate.generationPlayingNotes.contains(note)) return true;
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
