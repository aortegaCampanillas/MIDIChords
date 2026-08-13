import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/foundation.dart' show setEquals;
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show mapEquals;
import 'package:flutter/rendering.dart' show RenderAbstractViewport;
import 'package:flutter/services.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_midi_command/flutter_midi_command.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

import 'circle_of_fifths.dart';
import 'changelog_filter.dart';
import 'chord_staff_spelling.dart';
import 'app_preferences.dart';
import 'audio_player_port.dart';
import 'chord_variant_help.dart';
import 'fingerings.dart';
import 'help_geometry.dart';
import 'interval_data.dart';
import 'interval_practice.dart';
import 'interval_theory.dart' as interval_theory;
import 'key_signature_highlight.dart';
import 'music_catalog.dart';
import 'music_service.dart';
import 'midi_activity_guard.dart';
import 'midi_input_lifecycle.dart';
import 'midi_output_controller.dart';
import 'native_audio_bridge.dart';
import 'piano_layout.dart';
import 'piano_scroll_centering.dart';
import 'scale_guitar_marker.dart';
import 'scale_dropdown.dart';
import 'scale_staff_interaction.dart';
import 'sample_tone_plan.dart';
import 'staff_beam_geometry.dart';
import 'staff_note_geometry.dart';
import 'tuner_capture_session.dart';
import 'transient_player_lifecycle.dart';

part 'main_painters.dart';
part 'main_pages.dart';
part 'main_help.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations(const <DeviceOrientation>[
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  runApp(const MidiChordsMobileApp());
}

const String _kMetronomeSample = 'metronome.mp3';
const MethodChannel _kPlatformChannel = MethodChannel('midichords/platform');
const bool _kEnableMobileTuner = false;
const double _kTabletMinShortestSide = 600.0;

/// Piano estándar 88 teclas: A0 (21) … C8 (108), como escritorio/web.
const int _kPianoLowMidi = 21;
const int _kPianoHighMidi = 108;
const int _kPianoMiddleCMidi = 60;

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
      debugShowCheckedModeBanner: false,
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
      final hole = RRect.fromRectAndRadius(
        activeRect!,
        const Radius.circular(16),
      );
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

  double _compactResultHeight(
    BoxConstraints constraints, {
    double minHeight = 170,
  }) {
    final available = constraints.maxHeight.isFinite
        ? constraints.maxHeight
        : 640.0;
    return math.max(minHeight, math.min(260.0, available * 0.38));
  }

  bool _isCompactLandscapePhoneForConstraints(
    BuildContext context,
    BoxConstraints constraints,
  ) => _isCompactPhone(context) && constraints.maxWidth > constraints.maxHeight;
  final TextEditingController _detectionOutputController =
      TextEditingController(text: 'No results');
  final TextEditingController _chordOutputController = TextEditingController(
    text: 'No results',
  );
  final TextEditingController _scaleOutputController = TextEditingController(
    text: 'No results',
  );

  int _tabIndex = 0;
  int? _noteDetectionNote;
  bool _noteDetectionDetailsVisible = true;
  bool _noteDetectionPlayPressed = false;
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
  Map<String, dynamic> _chordTheoryCatalog = <String, dynamic>{};
  List<Map<String, dynamic>> _scalePatterns = <Map<String, dynamic>>[];

  int _chordRootPc = 0;
  // Letra natural + alteración elegidas explícitamente en el combo de tónica
  // (varias combinaciones dan el mismo pc, p. ej. Re♭ y Do#: se guarda la
  // elección real del usuario en vez de recalcular una enarmonía "canónica").
  int _chordRootLetterPc = 0;
  String _chordRootAccidental = 'natural';
  String _chordSuffix = '';
  int _chordInversion = 0;
  int _chordMaxInversion = 0;
  int _chordGuitarVariant = 0;
  bool _generationPlayPressed = false;
  final Set<int> _generationInputStaffNotes = <int>{};

  /// MIDI de la última tecla tocada en piano (generación/círculo); coincide con web `generationCurrentNote`.
  int? _generationNoteHighlightMidi;
  Timer? _generationNoteHighlightTimer;
  final Set<int> _heldChordNativeNotes = <int>{};

  /// Limpia el resalte del acorde en pentagrama si no llega pointer-up (p. ej. iOS).
  Timer? _heldChordPlaybackEndTimer;
  final Map<int, AudioPlayerPort> _heldChordPlayers = <int, AudioPlayerPort>{};

  /// Invalida reproducciones async (p. ej. `Future.wait` de samples) si hubo `_stopHeldChord` entretanto.
  int _heldChordPlayToken = 0;
  final Map<int, AudioPlayerPort> _heldInputPlayers = <int, AudioPlayerPort>{};
  final Map<int, AudioPlayerPort> _heldMidiInputPlayers =
      <int, AudioPlayerPort>{};

  /// Notas actualmente sonando vía salida MIDI (sin AudioPlayer asociado).
  final Set<int> _midiOutHeldNotes = <int>{};
  final Map<String, String> _toneFileCache = <String, String>{};
  bool _samplePlaybackAvailable = true;
  bool _metronomeSampleAvailable = true;
  Map<String, List<Map<String, dynamic>>> _guitarChordCacheByKey =
      <String, List<Map<String, dynamic>>>{};
  bool _audioPlaybackAvailable = true;
  final NativeAudioBridge _nativeAudioBridge = NativeAudioBridge.plugin();
  final AudioPlayerPortFactory _audioPlayerFactory =
      AudioPlayerPortFactory.plugin();
  late final TransientPlayerLifecycle<AudioPlayerPort> _audioPlayerLifecycle =
      TransientPlayerLifecycle<AudioPlayerPort>(
        disposePlayer: (player) => player.dispose(),
      );
  final bool _midiInputSoundEnabled = true;
  final MidiCommand _midiCommand = MidiCommand();
  late final MidiOutputController _midiOutputController;
  MidiInputLifecycle? _midiInputLifecycle;
  final Map<String, MidiDevice> _midiConnectedDevices = <String, MidiDevice>{};
  final Set<int> _detectionMidiHeldNotes = <int>{};
  final Set<int> _detectionPlayHeldNotes = <int>{};
  final Set<int> _generationMidiHeldNotes = <int>{};
  final Set<int> _scaleMidiHeldNotes = <int>{};
  bool _midiInputEnabled = false;
  String _midiError = '';

  /// Tras el último evento de nota MIDI en detección, mantenemos la pantalla activa este
  /// tiempo (iOS/Android no exponen “reiniciar el temporizador de reposo” como un toque).
  static const Duration _kMidiResetsIdleDuration = Duration(minutes: 3);
  final MidiActivityGuard _midiActivityGuard = MidiActivityGuard(
    wakeLock: const PluginWakeLockPort(),
    idleDuration: _kMidiResetsIdleDuration,
  );
  String _soundOutput =
      'audio'; // 'audio' or 'midi' - controls note playback routing

  int _scaleTonicPc = 0;
  int _scaleTonicLetterPc = 0;
  String _scaleTonicAccidental = 'natural';
  String _scalePatternName = 'Ionian';
  String _scaleFilterMode = 'basic'; // 'basic' or 'all'
  int _scaleOctaves = 1; // 1, 2, or 3
  String? _scaleFingeringHand; // null, 'right', or 'left' for piano fingerings
  Map<int, int> _scaleFingeringsMap =
      <int, int>{}; // MIDI note -> finger number
  int _scaleBpm = 120;
  bool _scaleLoopRunning = false;
  bool _scaleMetronomeOnly = false;
  int _scaleLoopIndex = 0;
  int _scaleLoopDirection = 1;

  // Interval detection state
  final List<int> _intervalNotes = <int>[]; // Last 2 notes for interval pair
  int? _intervalPlayingIdx;
  bool _intervalMelodyMode =
      false; // false = play 2 notes, true = play reference melody
  bool _intervalDetailsVisible = true;
  Timer? _intervalMelodyPlaybackTimer;
  int _intervalGenRootPc = 0;
  int _intervalGenRootLetterPc = 0;
  String _intervalGenRootAccidental = 'natural';
  int _intervalGenSemitones = 7;
  String _intervalGenCategoryKey = 'perfect';
  String _intervalGenLabel = '5J';
  int? _intervalGenPlayingIdx;
  bool? _intervalGenLastPlayReversed;
  bool _intervalGenHarmonic = false;
  Timer? _intervalGenInputHighlightTimer;
  Timer? _intervalGenPlaybackTimer;
  final IntervalPracticeDeck _intervalPracticeDeck = IntervalPracticeDeck();
  bool _intervalPracticeStarted = false;
  bool _intervalPracticeRunning = false;
  bool _intervalPracticeRandomTonic = false;
  bool _intervalPracticeAscendingOnly = true;
  bool _intervalPracticeHarmonic = false;
  int _intervalPracticeRepetitions = 10;
  int _intervalPracticeCorrect = 0;
  int _intervalPracticeTotal = 0;
  int _intervalPracticeRoot = 60;
  int _intervalPracticeSemitones = 0;
  int _intervalPracticeDirection = 1;
  int? _intervalPracticeAnswerNote;
  bool? _intervalPracticeAnswerCorrect;
  final Set<int> _intervalPracticeAllowedSemitones = <int>{
    for (var semitones = 0; semitones <= 12; semitones += 1) semitones,
  };
  final List<Map<String, Object>> _intervalPracticeHistory =
      <Map<String, Object>>[];
  int? _intervalPracticeReviewIndex;
  final Set<int> _intervalPracticePlayingNotes = <int>{};
  int? _intervalPracticePlayingNote;
  Timer? _intervalPracticePlaybackTimer;
  Timer? _intervalPracticeReviewTimer;
  int _intervalPracticePlaybackGeneration = 0;
  Timer? _scaleLoopTimer;
  Timer? _scaleStaffHighlightTimer;
  int? _scaleCurrentNote;
  bool? _scaleCurrentIsLeft;
  int? _scaleInputRawNote;
  int? _scaleGuitarStartNote;
  final Set<int> _detectionSelectedNotes = <int>{};
  final Set<int> _metronomeHeldNotes = <int>{};
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
  late final TunerCaptureSession _tunerCaptureSession =
      TunerCaptureSession.plugin();
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
  bool _detectionDetailsVisible = true;
  bool _inputDragActive = false;
  int? _dragPointer;
  int? _dragCurrentNote;
  Offset? _dragLastGlobalPos;
  DateTime _dragLastSwitchAt = DateTime.fromMillisecondsSinceEpoch(0);
  final ScrollController _pianoScrollController = ScrollController();
  final ScrollController _scaleControlsScrollController = ScrollController();
  final PianoScrollMemory _pianoScrollMemory = PianoScrollMemory();
  bool _needsPianoScrollSync = false;
  double? _pendingPianoScrollOffset;
  bool _startupPianoCenterPending = true;
  int _pianoScrollSyncGeneration = 0;
  final Set<int> _forbiddenFlashNotes = <int>{};
  final Map<int, Timer> _forbiddenFlashTimers = <int, Timer>{};
  final Map<String, GlobalKey> _helpAnchors = <String, GlobalKey>{};
  final Map<String, Rect> _helpGlobalRectCache = <String, Rect>{};
  late final AnimationController _helpOverlayController;
  bool _helpActive = false;
  bool _helpBannerVisible = true;
  Timer? _helpBannerTimer;
  String? _helpSelectedId;

  List<int> _enabledModeIndexes() {
    return _kEnableMobileTuner
        ? const <int>[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        : const <int>[0, 1, 2, 3, 4, 5, 7, 8, 9];
  }

  /// Same display order as the web mode selector.
  static const List<int> _kWebModeOrder = <int>[8, 0, 1, 5, 7, 9, 2, 3, 4, 6];

  List<int> _orderedEnabledModes(List<int> enabledModes) {
    final enabledSet = enabledModes.toSet();
    return _kWebModeOrder.where(enabledSet.contains).toList();
  }

  List<Map<String, dynamic>> _getFilteredScalePatterns() {
    final patterns = _scalePatterns.cast<Map<String, dynamic>>();
    if (_scaleFilterMode == 'basic') {
      return patterns
          .where((p) => scaleBasicNames.contains(p['name'] as String?))
          .toList();
    }
    return patterns;
  }

  String _ui(String es, String en) => _language == 'en' ? en : es;

  Widget _buildChordVariantTheoryButton({
    String helpId = 'generation_variant_theory',
    String? suffix,
    int? inversion,
    bool enabled = true,
  }) {
    final selectedSuffix = suffix ?? _chordSuffix;
    final selectedInversion = inversion ?? _chordInversion;
    return _helpAnchor(
      helpId,
      Tooltip(
        message: _ui('Ayuda de la variante', 'Variant help'),
        child: SizedBox(
          width: 40,
          height: 40,
          child: OutlinedButton(
            onPressed: enabled
                ? () => unawaited(
                    _showChordVariantHelpDialog(
                      suffix: selectedSuffix,
                      inversion: selectedInversion,
                    ),
                  )
                : null,
            style: OutlinedButton.styleFrom(
              padding: EdgeInsets.zero,
              foregroundColor: const Color(0xFFF2BF2F),
              side: const BorderSide(color: _border),
              shape: const CircleBorder(),
            ),
            child: const Text(
              '?',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _showChordVariantHelpDialog({
    required String suffix,
    required int inversion,
  }) async {
    if (_chordTheoryCatalog.isEmpty) {
      await _loadChordTheoryCatalog();
    }
    if (!mounted) return;
    final help = chordVariantHelpContent(
      catalog: _chordTheoryCatalog,
      suffix: suffix,
      inversion: inversion,
      language: _language,
    );
    final names = _language == 'en' ? chordSuffixNamesEn : chordSuffixNamesEs;
    final variant = names[suffix] ?? (suffix.isEmpty ? 'maj' : suffix);
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: _panelA,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: _border),
        ),
        title: Text(
          '${_ui('Teoría', 'Theory')}: $variant',
          style: const TextStyle(color: _text, fontWeight: FontWeight.w800),
        ),
        content: ConstrainedBox(
          constraints: BoxConstraints(
            maxWidth: 620,
            maxHeight: math.max(
              180.0,
              MediaQuery.of(dialogContext).size.height - 190,
            ),
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                DecoratedBox(
                  decoration: BoxDecoration(
                    color: _surfaceDark,
                    border: Border.all(color: _border),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 7,
                    ),
                    child: Text(
                      '${_ui('Fórmula', 'Formula')}: ${help.formula}',
                      style: const TextStyle(
                        color: Color(0xFFF2BF2F),
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  help.theory,
                  style: const TextStyle(color: _text, height: 1.45),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 14),
                  child: Divider(color: _border, height: 1),
                ),
                Text(
                  help.inversion,
                  style: const TextStyle(color: _text, height: 1.45),
                ),
              ],
            ),
          ),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: Text(_ui('Cerrar', 'Close')),
          ),
        ],
      ),
    );
  }

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
      case 7:
        return _ui('Generación de Intervalos', 'Interval Generation');
      case 8:
        return _ui('Detección de Notas', 'Note Detection');
      case 9:
        return _ui('Practicar Intervalos', 'Interval Practice');
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
              child: ConstrainedBox(
                // Misma reserva fija que en el diálogo de Novedades: título +
                // padding + acciones no caben en pantallas bajas (landscape
                // de iPhone) si el contenido no tiene un alto máximo propio.
                constraints: BoxConstraints(
                  maxHeight: math.max(
                    160.0,
                    math.min(420.0, MediaQuery.of(context).size.height - 220.0),
                  ),
                ),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      DropdownButtonFormField<String>(
                        key: ValueKey<String>(
                          'settings_lang_$selectedLanguage',
                        ),
                        initialValue: selectedLanguage,
                        dropdownColor: _surfaceDark,
                        style: const TextStyle(color: _text),
                        decoration: InputDecoration(
                          labelText: _ui('Idioma', 'Language'),
                        ),
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
                        onChanged: (value) {
                          if (value != null) {
                            setDialogState(() => selectedLanguage = value);
                          }
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
                        activeThumbColor: _accent,
                        onChanged: (v) =>
                            setDialogState(() => selectedShowKeyNames = v),
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
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  color: _muted,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                versionText,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w800,
                                  color: _text,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Wrap(
                                spacing: 8,
                                runSpacing: 4,
                                children: <Widget>[
                                  TextButton.icon(
                                    onPressed: () async {
                                      final uri = Uri.parse(
                                        'https://freemidichords.com/',
                                      );
                                      if (await canLaunchUrl(uri)) {
                                        await launchUrl(
                                          uri,
                                          mode: LaunchMode.externalApplication,
                                        );
                                      }
                                    },
                                    icon: const Icon(Icons.language, size: 18),
                                    label: Text(
                                      _ui('Visitar la web', 'Visit website'),
                                    ),
                                    style: TextButton.styleFrom(
                                      foregroundColor: _accent,
                                    ),
                                  ),
                                  TextButton.icon(
                                    onPressed: () async {
                                      Navigator.of(dialogContext).pop();
                                      await _showChangelogDialog(
                                        fromSettings: true,
                                      );
                                    },
                                    icon: const Icon(
                                      Icons.new_releases_outlined,
                                      size: 18,
                                    ),
                                    label: Text(_ui('Novedades', "What's new")),
                                    style: TextButton.styleFrom(
                                      foregroundColor: _accent,
                                    ),
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
    _midiOutputController = MidiOutputController(
      MidiCommandOutputPort(_midiCommand),
    );
    _helpOverlayController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );
    _needsPianoScrollSync = true;
    _initMidiInput();
    unawaited(_initPlatformAudioWorkarounds());
    unawaited(_loadPrefsAndStart());
  }

  Future<void> _loadPrefsAndStart() async {
    final repository = AppPreferencesRepository(
      await SharedPreferencesPort.create(),
    );
    final prefs = repository.load();
    setState(() {
      _language = prefs.language;
      _showKeyNames = prefs.showKeyNames;
      _lastSeenChangelogVersion = prefs.lastSeenChangelogVersion;
      _changelogDontShow = prefs.changelogDontShow;
      _scaleOctaves = prefs.scaleOctaves;
      _scaleFingeringHand = prefs.scaleFingeringHand;
      _tabIndex = prefs.tabIndex;
    });
    await _loadMeta();
    await _loadChangelog();
    if (!mounted) return;
    setState(() {
      // La carga de datos puede regenerar escalas o acordes y programar su
      // propio scroll. El centrado inicial debe ser la última operación para
      // que ninguna reconstrucción posterior sustituya C4 por otra ancla.
      _pendingPianoScrollOffset = null;
      _startupPianoCenterPending = true;
      _needsPianoScrollSync = true;
      _pianoScrollSyncGeneration += 1;
    });
    _maybeShowChangelogPopup();
  }

  Future<void> _savePrefs() async {
    final repository = AppPreferencesRepository(
      await SharedPreferencesPort.create(),
    );
    await repository.save(
      AppPreferences(
        language: _language,
        showKeyNames: _showKeyNames,
        lastSeenChangelogVersion: _lastSeenChangelogVersion,
        changelogDontShow: _changelogDontShow,
        scaleOctaves: _scaleOctaves,
        scaleFingeringHand: _scaleFingeringHand,
        tabIndex: _tabIndex,
      ),
    );
  }

  Future<void> _loadChangelog() async {
    try {
      final raw = await rootBundle.loadString('assets/changelog.json');
      final list = (jsonDecode(raw) as List<dynamic>)
          .cast<Map<String, dynamic>>();
      if (mounted) setState(() => _changelogEntries = list);
    } catch (_) {}
  }

  String get _latestChangelogVersion => _changelogEntries.isNotEmpty
      ? (_changelogEntries.first['version'] as String? ?? '')
      : '';

  void _maybeShowChangelogPopup() {
    // Mientras el usuario no marque "No volver a mostrar", el diálogo
    // reaparece en cada arranque de la app (no solo la primera vez que se
    // publica la versión) — es la única forma de que quede claro que sigue
    // sin haberlo confirmado.
    if (_changelogDontShow) return;
    final latest = _latestChangelogVersion;
    if (latest.isEmpty) return;
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
          final sections = _changelogEntries
              .map((v) {
                final publishedItems = (v['items'] as List<dynamic>? ?? [])
                    .cast<Map<String, dynamic>>()
                    .where(
                      (it) =>
                          it['publish'] == true &&
                          changelogItemTargetsMobile(it),
                    )
                    .map(
                      (it) =>
                          (_language == 'en' ? it['en'] : it['es'])
                              as String? ??
                          '',
                    )
                    .where((t) => t.isNotEmpty)
                    .toList();
                return (
                  version: v['version'] as String? ?? '',
                  date: v['date'] as String? ?? '',
                  items: publishedItems,
                );
              })
              .where((s) => s.items.isNotEmpty)
              .take(6)
              .toList();

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
                    // Deja sitio para el título del diálogo, el checkbox
                    // "No volver a mostrar" y los botones de acción, que
                    // viven fuera de este ConstrainedBox pero comparten el
                    // mismo alto disponible dentro del AlertDialog. Restamos
                    // una reserva fija (título + padding + checkbox +
                    // acciones) del alto de pantalla en vez de un simple
                    // porcentaje, para que quepa también en landscape de
                    // iPhone (pantallas de ~400-430pt de alto).
                    constraints: BoxConstraints(
                      maxHeight: math.max(
                        120.0,
                        math.min(
                          380.0,
                          MediaQuery.of(context).size.height - 260.0,
                        ),
                      ),
                    ),
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: sections
                            .map(
                              (s) => Padding(
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
                                            style: const TextStyle(
                                              color: _muted,
                                              fontSize: 11,
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    ...s.items.map(
                                      (text) => Padding(
                                        padding: const EdgeInsets.only(
                                          bottom: 6,
                                        ),
                                        child: Row(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: <Widget>[
                                            const Text(
                                              '• ',
                                              style: TextStyle(
                                                color: _muted,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            Expanded(
                                              child: Text(
                                                text,
                                                style: const TextStyle(
                                                  color: _text,
                                                  height: 1.4,
                                                  fontSize: 13,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            )
                            .toList(),
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
                          onChanged: (v) =>
                              setSt(() => dontShowAgain = v ?? false),
                        ),
                        Expanded(
                          child: GestureDetector(
                            onTap: () =>
                                setSt(() => dontShowAgain = !dontShowAgain),
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
    // Runs after dialog closes for ANY reason (button, back, tap outside).
    // El checkbox "No volver a mostrar" siempre se persiste tal cual lo deja
    // el usuario (tanto al marcarlo como al desmarcarlo), incluso abriendo
    // el diálogo desde Configuración. Solo actualizamos "última versión
    // vista" cuando el diálogo apareció automáticamente (no desde
    // Configuración) y el usuario marcó el check — si no lo marca, debe
    // volver a aparecer solo en el próximo arranque, no en cada apertura.
    setState(() {
      _changelogDontShow = dontShowAgain;
      if (!fromSettings && dontShowAgain) {
        _lastSeenChangelogVersion = _latestChangelogVersion;
      }
    });
    await _savePrefs();
  }

  @override
  void dispose() {
    _heldChordPlaybackEndTimer?.cancel();
    _generationNoteHighlightTimer?.cancel();
    _metroTimer?.cancel();
    _metroAnimTimer?.cancel();
    _scaleLoopTimer?.cancel();
    _scaleStaffHighlightTimer?.cancel();
    _intervalMelodyPlaybackTimer?.cancel();
    _intervalGenPlaybackTimer?.cancel();
    _intervalGenInputHighlightTimer?.cancel();
    _intervalPracticePlaybackTimer?.cancel();
    _intervalPracticeReviewTimer?.cancel();
    _helpBannerTimer?.cancel();
    _stopHeldChord();
    _stopHeldInputs();
    _stopHeldMidiInputs();
    unawaited(_audioPlayerLifecycle.disposeAll());
    unawaited(_disableMidiInput(notify: false));
    unawaited(_midiInputLifecycle?.dispose());
    for (final t in _forbiddenFlashTimers.values) {
      t.cancel();
    }
    _forbiddenFlashTimers.clear();
    unawaited(_tunerCaptureSession.dispose());
    _detectionOutputController.dispose();
    _chordOutputController.dispose();
    _scaleOutputController.dispose();
    _helpOverlayController.dispose();
    _pianoScrollController.dispose();
    _scaleControlsScrollController.dispose();
    _midiActivityGuard.dispose();
    super.dispose();
  }

  int _positiveMod12(int value) => positiveMod12(value);

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

  bool _isMinorChordSuffix(String suffix) => isMinorChordSuffix(suffix);

  ({int? sharpCount, int? flatCount}) _keySignatureSharpFlatCounts(
    int tonicPc,
    bool isMinor,
  ) => keySignatureSharpFlatCounts(tonicPc, isMinor);

  bool _chordSymbolPreferFlat(int rootPc, bool isMinor) =>
      chordSymbolPreferFlat(rootPc, isMinor);

  bool _scalePrefersMinor(String patternName) => scalePrefersMinor(patternName);

  /// Semitonos que hay que SUMAR a la tónica del modo para llegar a su mayor
  /// relativo real (comparte exactamente las mismas notas). Verificado nota
  /// a nota: Do Dórico = Sib Mayor (+10), Do Frigio = Lab Mayor (+8), Do
  /// Locrio = Reb Mayor (+1), Do Eolio = Mib Mayor (+3, ya era el
  /// comportamiento previo/correcto), Fa Lidio = Do Mayor (+7), Sol
  /// Mixolidio = Do Mayor (+5). Ionian/Mayor no necesita entrada (offset
  /// 0). Sin esto, cada modo "no jónico" heredaba o bien la armadura del
  /// menor natural (los de sabor menor) o la de su propia tónica como si
  /// fuera Mayor normal (los de sabor mayor: Lidio, Mixolidio), ambas
  /// incorrectas salvo casualidad.
  static const Map<String, int> _modeRelativeMajorOffset = <String, int>{
    'Dorian': 10,
    'Phrygian': 8,
    'Locrian': 1,
    'Aeolian': 3,
    'Lydian': 7,
    'Mixolydian': 5,
    'Minor': 3,
    'Natural Minor': 3,
    'Minor Pentatonic': 3,
    'Minor Blues': 3,
  };

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
    if (_tabIndex == 5 || _tabIndex == 8) {
      return (count: 0, preferFlats: _preferFlat);
    }
    final tieFromSelect = _preferFlat;
    if (_tabIndex == 3 && _generatedScaleJson != null) {
      final name =
          (_generatedScaleJson!['pattern_name'] as String?) ?? 'Ionian';
      final isMinor = _scalePrefersMinor(name);
      final tonic = _positiveMod12(
        (_generatedScaleJson!['tonic_pc'] as num?)?.toInt() ?? 0,
      );
      final offset = _modeRelativeMajorOffset[name];
      if (offset != null) {
        final relativeMajorPc = _positiveMod12(tonic + offset);
        return _keySignatureCountForTonic(
          relativeMajorPc,
          false,
          tiePreferFlat: tieFromSelect,
        );
      }
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
        final suffix = (_detectionResultJson!['suffix'] as String?) ?? '';
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

  Future<void> _loadMeta() async {
    try {
      await _loadGuitarChordCache();
      await _loadChordTheoryCatalog();
      final chordPatterns = chordPatternsForUi();
      final scalePatterns = scalePatternsLocal(_language);
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
      _detectionOutputController.text =
          '${_ui('Error cargando meta', 'Error loading metadata')}: $err';
    }
  }

  Future<void> _loadChordTheoryCatalog() async {
    if (_chordTheoryCatalog.isNotEmpty) return;
    final raw = await rootBundle.loadString('assets/chord_variant_theory.json');
    final decoded = jsonDecode(raw);
    if (decoded is Map) {
      _chordTheoryCatalog = decoded.map(
        (key, value) => MapEntry<String, dynamic>(key.toString(), value),
      );
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
    _midiActivityGuard.cancel();
  }

  /// Cada nota MIDI (u off) renueva la ventana: equivale a “hubo interacción” para no
  /// entrar en reposo mientras sigues tocando (con pausas hasta [_kMidiResetsIdleDuration]).
  void _bumpMidiScreenActivityTimer() {
    if (!_midiInputEnabled || _tabIndex != 0) {
      return;
    }
    _midiActivityGuard.bump();
  }

  void _initMidiInput() {
    _midiInputLifecycle = MidiInputLifecycle.fromCommand(
      command: _midiCommand,
      onMidiBytes: _onMidiBytes,
      onSetupChanged: () {
        if (_midiInputEnabled) {
          unawaited(_refreshMidiConnections());
        }
      },
    )..start();
  }

  void _onMidiBytes(List<int> bytes) {
    if (!_midiInputEnabled) return;
    var hadNoteChannelMessage = false;
    for (var i = 0; i + 2 < bytes.length; i += 3) {
      final status = bytes[i] & 0xF0;
      final note = bytes[i + 1];
      final velocity = bytes[i + 2];
      final isNoteOn = status == 0x90 && velocity > 0;
      final isNoteOff = status == 0x80 || (status == 0x90 && velocity == 0);
      if (!isNoteOn && !isNoteOff) continue;
      hadNoteChannelMessage = true;

      if (_tabIndex == 8) {
        if (isNoteOn) {
          setState(() => _noteDetectionNote = note);
          if (_midiInputSoundEnabled) {
            unawaited(_startHeldMidiInputNote(note, instrument: 'piano'));
          }
        } else {
          _releaseHeldMidiInputNote(note);
        }
        continue;
      }

      // Generation / Circle of fifths mode handling (tabIndex 1 or 2): mismo
      // resaltado/aviso de nota prohibida que con dedo/ratón, sin reenviar
      // por MIDI-out la nota que ya llega de un teclado MIDI externo.
      if (_tabIndex == 1 || _tabIndex == 2) {
        unawaited(
          _handleInstrumentNote(note, pressed: isNoteOn, fromMidi: true),
        );
        continue;
      }

      // Interval detection mode handling (tabIndex 5)
      if (_tabIndex == 5) {
        if (isNoteOn) {
          _addIntervalNote(note);
          if (_midiInputSoundEnabled) {
            unawaited(_startHeldMidiInputNote(note, instrument: 'piano'));
          }
        }
        continue;
      }

      if (_tabIndex == 7) {
        if (isNoteOn) {
          unawaited(_handleInstrumentNote(note, pressed: true, fromMidi: true));
        }
        continue;
      }

      if (_tabIndex == 9) {
        unawaited(
          _handleInstrumentNote(note, pressed: isNoteOn, fromMidi: true),
        );
        continue;
      }

      // Metronome mode handling (tabIndex 4): el piano sigue siendo
      // interactivo mientras suena el metrónomo, igual que con ratón/touch.
      if (_tabIndex == 4) {
        if (isNoteOn) {
          setState(() => _metronomeHeldNotes.add(note));
          if (_midiInputSoundEnabled) {
            unawaited(_startHeldMidiInputNote(note, instrument: 'piano'));
          }
        } else {
          setState(() => _metronomeHeldNotes.remove(note));
          _releaseHeldMidiInputNote(note);
        }
        continue;
      }

      // Scale mode handling (tabIndex 3): mismo resaltado/aviso de nota
      // prohibida que con dedo/ratón, sin reenviar por MIDI-out.
      if (_tabIndex == 3 && _generatedScaleJson != null) {
        unawaited(
          _handleInstrumentNote(note, pressed: isNoteOn, fromMidi: true),
        );
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

  Future<void> _disableMidiInput({bool notify = true}) async {
    _midiInputEnabled = false;
    _midiError = '';
    // El botón "Salida MIDI/Audio" solo es visible con MIDI activado; si se
    // queda en 'midi' al desactivar el toggle, la app se queda sin sonido
    // (no hay dispositivo MIDI ni tampoco vuelve a sonar por el altavoz).
    _soundOutput = 'audio';
    for (final device in _midiConnectedDevices.values.toList()) {
      try {
        _midiCommand.disconnectDevice(device);
      } catch (_) {}
    }
    _midiConnectedDevices.clear();
    _midiOutputController.resetProgram();
    _detectionMidiHeldNotes.clear();
    _generationMidiHeldNotes.clear();
    _scaleMidiHeldNotes.clear();
    _stopHeldMidiInputs();
    _cancelMidiScreenActivityExtension();
    if (notify && mounted) setState(() {});
    if (notify && _tabIndex == 0 && !_requestInFlight) {
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

  void _selectChordGuitarVariant(int variant) {
    if (variant == _chordGuitarVariant) return;
    setState(() => _chordGuitarVariant = variant);
    unawaited(_playChordPreviewFromSelection());
  }

  Set<int> _staffNotesForCurrentTab() {
    if (_tabIndex == 8) {
      return _noteDetectionNote == null ? <int>{} : <int>{_noteDetectionNote!};
    }
    if (_tabIndex == 7) return _intervalGenerationNotes().toSet();
    if (_tabIndex == 9) return _intervalPracticeDisplayNotes().toSet();
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
    final rawNotes = <int>{..._heldChordPlayers.keys, ..._heldChordNativeNotes};
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
    if (_tabIndex == 8) {
      return _noteDetectionNote == null ? <int>{} : <int>{_noteDetectionNote!};
    }
    if (_tabIndex == 7) return _intervalGenerationNotes().toSet();
    if (_tabIndex == 9) return _intervalPracticeDisplayNotes().toSet();
    if (_tabIndex == 5) {
      if (_intervalMelodyMode) {
        return _getIntervalMelodyNotes().whereType<int>().toSet();
      }
      return _intervalNotes.toSet();
    }
    if (_tabIndex == 0) return _activeDetectionNotes;
    if (_tabIndex == 4) return _metronomeHeldNotes;
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
      final notes = <int>{...rh, ..._scaleMidiHeldNotes};
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
      // Devolvemos la nota real del voicing seleccionado tal cual: la
      // transposición para que se lea en el registro habitual de guitarra
      // (+12) ya la aplica _buildStaffPanel (vía staffMidi/guitarDisplayVoicing)
      // de forma uniforme a todas las notas del pentagrama; aplicarla aquí
      // también duplicaba el desplazamiento y descolocaba las notas.
      final selected = _selectedChordGuitarNotes();
      if (selected.contains(note)) return note;
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
    // En guitarra el selector de octavas no aplica: el diapasón/pentagrama
    // siempre muestran una sola octava, independientemente de lo elegido
    // para piano.
    if (base.isEmpty || _scaleOctaves <= 1 || _instrumentView == 'guitar') {
      return base;
    }
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

  Future<AudioPlayerPort?> _playTone({
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
      final ok = await _nativeAudioBridge.playTone(
        platform: 'android',
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
      final ok = await _nativeAudioBridge.playTone(
        platform: 'ios',
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
    AudioPlayerPort? player;
    try {
      player = await _audioPlayerFactory.create(
        mode: Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
        context: Platform.isAndroid
            ? AudioContext(
                android: const AudioContextAndroid(
                  contentType: AndroidContentType.sonification,
                  usageType: AndroidUsageType.assistanceSonification,
                  audioFocus: AndroidAudioFocus.none,
                ),
              )
            : null,
      );
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
      _audioPlayerLifecycle.watch(player, player.onComplete);
      return player;
    } catch (err) {
      _audioPlaybackAvailable = false;
      try {
        await player?.dispose();
      } catch (_) {}
      debugPrint('Audio playback unavailable on this device/runtime: $err');
      SystemSound.play(SystemSoundType.click);
      return null;
    }
  }

  Future<AudioPlayerPort?> _playMetronomeClick({
    bool accent = false,
    bool bar = false,
    double volumeScale = 1.0,
  }) async {
    final gain = volumeScale.clamp(0.0, 1.0);
    if (gain <= 0.0) return null;
    final level = bar ? 2 : (accent ? 1 : 0);
    if (Platform.isAndroid) {
      final ok = await _nativeAudioBridge.playMetronomeClick(
        platform: 'android',
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
        final ok = await _nativeAudioBridge.playMetronomeClick(
          platform: 'ios',
          level: level,
          volume: gain,
        );
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
      AudioPlayerPort? samplePlayer;
      final baseRate = switch (level) {
        2 => 1.68,
        1 => 1.24,
        _ => 0.94,
      };
      try {
        samplePlayer = await _audioPlayerFactory.create(
          mode: Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
        );
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
        _audioPlayerLifecycle.watch(samplePlayer, samplePlayer.onComplete);
        return samplePlayer;
      } catch (err) {
        _metronomeSampleAvailable = false;
        try {
          await samplePlayer?.dispose();
        } catch (_) {}
        debugPrint('Metronome sample playback unavailable: $err');
      }
    }
    final clickWav = _buildMetronomeClickWav(level: level);
    AudioPlayerPort? player;
    try {
      player = await _audioPlayerFactory.create(
        mode: Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.play(
        BytesSource(clickWav, mimeType: 'audio/wav'),
        volume: (baseGain * gain).clamp(0.0, 1.0),
      );
      _audioPlayerLifecycle.watch(player, player.onComplete);
      return player;
    } catch (err) {
      try {
        await player?.dispose();
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
        _nativeAudioBridge.playMetronomeClick(
          platform: 'android',
          level: level,
          volume: (overlay * gain).clamp(0.0, 1.0),
        ),
      );
      return;
    }
    AudioPlayerPort? player;
    try {
      player = await _audioPlayerFactory.create(
        mode: Platform.isIOS ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
      );
      await player.play(
        BytesSource(
          _buildMetronomeClickWav(level: level),
          mimeType: 'audio/wav',
        ),
        volume: ((level >= 2 ? 0.48 : 0.32) * gain).clamp(0.0, 1.0),
      );
      _audioPlayerLifecycle.watch(player, player.onComplete);
    } catch (_) {
      try {
        await player?.dispose();
      } catch (_) {}
    }
  }

  Future<AudioPlayerPort?> _playSampleTone({
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
    final plan = planSampleTone(midi: midi, instrument: instrument);
    if (plan == null) return null;
    AudioPlayerPort? player;
    try {
      final useLowLatency = Platform.isAndroid;
      player = await _audioPlayerFactory.create(
        mode: useLowLatency ? PlayerMode.lowLatency : PlayerMode.mediaPlayer,
        context: Platform.isAndroid
            ? AudioContext(
                android: const AudioContextAndroid(
                  contentType: AndroidContentType.music,
                  usageType: AndroidUsageType.media,
                  audioFocus: AndroidAudioFocus.none,
                ),
              )
            : null,
      );
      final activePlayer = player;
      await activePlayer.setSource(AssetSource(plan.assetPath));
      if ((plan.playbackRate - 1.0).abs() > 0.001) {
        try {
          await activePlayer.setPlaybackRate(plan.playbackRate);
        } catch (_) {
          // Keep sample playback even if transposition is unsupported.
        }
      }
      await activePlayer.setVolume(volume);
      if (Platform.isAndroid) {
        await activePlayer.resume();
        final ttlMs = ((durationSeconds.clamp(0.1, 2.2) * 1000) + 320)
            .round()
            .clamp(220, 3200);
        Timer(Duration(milliseconds: ttlMs), () {
          unawaited(_safeStopDispose(activePlayer));
        });
        return activePlayer;
      }
      await activePlayer.resume();
      if (useLowLatency) {
        final ttlMs = ((durationSeconds.clamp(0.1, 2.2) * 1000) + 320)
            .round()
            .clamp(220, 3200);
        Timer(Duration(milliseconds: ttlMs), () {
          unawaited(_safeStopDispose(activePlayer));
        });
      } else {
        _audioPlayerLifecycle.watch(activePlayer, activePlayer.onComplete);
      }
      return activePlayer;
    } catch (err) {
      debugPrint('Instrument sample playback unavailable: $err');
      try {
        await player?.dispose();
      } catch (_) {}
      return null;
    }
  }

  Future<void> _safeStopDispose(AudioPlayerPort player) =>
      _audioPlayerLifecycle.dispose(player);

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

  void _bumpGenerationNoteHighlight(int midi) {
    _generationNoteHighlightTimer?.cancel();
    setState(() => _generationNoteHighlightMidi = midi);
    _generationNoteHighlightTimer = Timer(
      const Duration(milliseconds: 720),
      () {
        if (!mounted) {
          return;
        }
        setState(() {
          _generationNoteHighlightMidi = null;
          _generationNoteHighlightTimer = null;
          if (_tabIndex == 1 || _tabIndex == 2) {
            _generationInputStaffNotes.clear();
          }
        });
      },
    );
  }

  void _clearGenerationNoteHighlight() {
    _generationNoteHighlightTimer?.cancel();
    _generationNoteHighlightTimer = null;
    _generationNoteHighlightMidi = null;
  }

  Future<void> _handleInstrumentNote(
    int midi, {
    required bool pressed,
    bool fromMidi = false,
  }) async {
    if (_tabIndex == 9) {
      if (!pressed) return;
      if (!_intervalPracticeStarted) return;
      if (_intervalPracticeAnswerCorrect == null) {
        _answerIntervalPractice(note: midi);
        return;
      }
      final permitted = _intervalPracticeDisplayNotes().toSet();
      if (!permitted.contains(midi)) {
        _showForbiddenOnPiano(midi);
        return;
      }
      if (!fromMidi || _midiInputSoundEnabled) {
        await playNote(midi, instrument: 'piano');
      }
      _intervalGenInputHighlightTimer?.cancel();
      setState(() {
        _intervalPracticePlayingNote = midi;
        _intervalPracticePlayingNotes
          ..clear()
          ..add(midi);
      });
      _intervalGenInputHighlightTimer = Timer(
        const Duration(milliseconds: 600),
        () {
          if (!mounted) return;
          setState(() {
            _intervalPracticePlayingNote = null;
            _intervalPracticePlayingNotes.clear();
            _intervalGenInputHighlightTimer = null;
          });
        },
      );
      return;
    }
    if (_tabIndex == 8) {
      if (pressed) {
        setState(() => _noteDetectionNote = midi);
        if (!fromMidi || _midiInputSoundEnabled) {
          await playNote(midi, instrument: 'piano');
        }
      } else if (!fromMidi) {
        await stopNote(midi);
      }
      return;
    }
    if (_tabIndex == 7) {
      if (fromMidi && !pressed) return;
      final notes = _intervalGenerationNotes();
      final matchingIndexes =
          <int>[
            for (var index = 0; index < notes.length; index++)
              if (notes[index] % 12 == midi % 12) index,
          ]..sort((a, b) {
            final aExact = notes[a] == midi;
            final bExact = notes[b] == midi;
            if (aExact != bExact) return aExact ? -1 : 1;
            return (notes[a] - midi).abs().compareTo((notes[b] - midi).abs());
          });
      final matchedIndex = matchingIndexes.isEmpty ? -1 : matchingIndexes.first;
      if (matchedIndex < 0) {
        _showForbiddenOnPiano(midi);
        return;
      }
      if (!fromMidi || _midiInputSoundEnabled) {
        await playNote(midi, instrument: _instrumentView);
      }
      _intervalGenInputHighlightTimer?.cancel();
      setState(() => _intervalGenPlayingIdx = matchedIndex);
      _intervalGenInputHighlightTimer = Timer(
        const Duration(milliseconds: 720),
        () {
          if (!mounted) return;
          setState(() {
            _intervalGenPlayingIdx = null;
            _intervalGenInputHighlightTimer = null;
          });
        },
      );
      return;
    }
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
      if (fromMidi) {
        // Con MIDI puede haber varias notas sostenidas a la vez (acorde real
        // en el teclado externo): se acumulan en el pentagrama y en el
        // teclado en vez de usar el highlight de una sola nota pensado para
        // el toque con dedo/ratón (que solo tiene un puntero activo a la
        // vez). Al soltar una nota, solo se retira esa, no todo el Set.
        setState(() {
          if (pressed) {
            _generationMidiHeldNotes.add(midi);
            if (staffNote != null) _generationInputStaffNotes.add(staffNote);
          } else {
            _generationMidiHeldNotes.remove(midi);
            if (staffNote != null) {
              _generationInputStaffNotes.remove(staffNote);
            }
          }
        });
      } else {
        if (staffNote != null) {
          _generationInputStaffNotes
            ..clear()
            ..add(staffNote);
        }
        _bumpGenerationNoteHighlight(midi);
      }
      if (fromMidi) {
        if (pressed) {
          await _startHeldMidiInputNote(
            midi,
            instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
          );
        } else {
          _releaseHeldMidiInputNote(midi);
        }
      } else if (pressed) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        );
      } else if (_soundOutput == 'midi') {
        _sendMidiNoteOn(midi, 80);
        unawaited(
          Future<void>.delayed(
            Duration(
              milliseconds: ((_instrumentView == 'guitar' ? 1.02 : 0.92) * 1000)
                  .round(),
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
      if (pressed) {
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
      }
      if (fromMidi) {
        // Igual que en Generación: con MIDI puede haber varias notas
        // sostenidas a la vez, así que se acumulan en un Set en vez de la
        // única "nota actual" que usa el resto de la pantalla de Escalas.
        if (pressed) {
          _scaleMidiHeldNotes.add(midi);
        } else {
          _scaleMidiHeldNotes.remove(midi);
          final releasedCurrent =
              _scaleCurrentNote != null &&
              _positiveMod12(_scaleCurrentNote!) == _positiveMod12(midi);
          if (_scaleMidiHeldNotes.isEmpty) {
            _scaleCurrentNote = null;
            _scaleCurrentIsLeft = null;
            _scaleInputRawNote = null;
          } else if (releasedCurrent) {
            final remaining = _scaleMidiHeldNotes.last;
            _scaleCurrentNote =
                _scaleStaffNoteForPitch(remaining, includeBass: true) ??
                remaining;
            _scaleCurrentIsLeft = null;
          }
        }
      }
      setState(() {});
      if (fromMidi) {
        if (pressed) {
          await _startHeldMidiInputNote(
            midi,
            instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
          );
        } else {
          _releaseHeldMidiInputNote(midi);
        }
      } else if (pressed) {
        await _startHeldInputNote(
          midi,
          instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        );
      } else if (_soundOutput == 'midi') {
        _sendMidiNoteOn(midi, 80);
        unawaited(
          Future<void>.delayed(
            Duration(
              milliseconds: ((_instrumentView == 'guitar' ? 0.95 : 0.85) * 1000)
                  .round(),
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
      return;
    }
    if (_tabIndex == 4) {
      // El piano sigue siendo interactivo mientras corre el metrónomo (ver
      // texto de ayuda: "puedes seguir viendo y tocando notas en el piano").
      // El resaltado usa un Set propio actualizado de forma síncrona en vez
      // de _heldInputPlayers (que _startHeldInputNote solo rellena tras el
      // `await _playTone`, con retraso variable en Android) para que la
      // tecla se marque al instante, no cuando el audio termine de cargar.
      if (pressed) {
        setState(() => _metronomeHeldNotes.add(midi));
        await _startHeldInputNote(midi, instrument: 'piano');
      } else {
        setState(() => _metronomeHeldNotes.remove(midi));
        if (_soundOutput == 'midi') {
          _sendMidiNoteOn(midi, 80);
          unawaited(
            Future<void>.delayed(
              const Duration(milliseconds: 850),
            ).then((_) => _sendMidiNoteOff(midi)),
          );
        } else {
          await _playTone(
            midi: midi,
            instrument: 'piano',
            durationSeconds: 0.85,
            lowVolume: true,
          );
        }
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
        _clearGenerationNoteHighlight();
      }
      if (_tabIndex == 4) {
        setState(() => _metronomeHeldNotes.remove(_dragCurrentNote));
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
      _clearGenerationNoteHighlight();
    }
    if (_tabIndex == 3 && !_scaleLoopRunning) {
      _scaleCurrentNote = null;
      _scaleCurrentIsLeft = null;
      _scaleInputRawNote = null;
    }
    if (_tabIndex == 4) {
      _metronomeHeldNotes.clear();
    }
    if (mounted) {
      setState(() {});
    }
  }

  void _rememberPianoScrollForMode(int tabIndex) {
    if (_instrumentView != 'piano' || !_pianoScrollController.hasClients) {
      return;
    }
    _pianoScrollMemory.remember(tabIndex, _pianoScrollController.offset);
  }

  void _requestPianoScrollForMode(int tabIndex) {
    if (!modeUsesCenteredTheoryPiano(tabIndex)) return;
    _pendingPianoScrollOffset = _pianoScrollMemory.offsetFor(tabIndex);
    _needsPianoScrollSync = true;
  }

  void _syncPianoScrollToMiddleC(
    double viewportW,
    double whiteW,
    List<int> whiteMidi,
  ) {
    if (!_needsPianoScrollSync) return;
    _needsPianoScrollSync = false;
    final requestedOffset = _pendingPianoScrollOffset;
    _pendingPianoScrollOffset = null;
    final forceMiddleC = _startupPianoCenterPending;
    final syncGeneration = ++_pianoScrollSyncGeneration;

    void attempt(int retriesLeft, double lastMaxExt) {
      WidgetsBinding.instance.addPostFrameCallback((_) async {
        if (!mounted || syncGeneration != _pianoScrollSyncGeneration) return;
        if (!_pianoScrollController.hasClients) {
          if (retriesLeft > 0) {
            await Future<void>.delayed(const Duration(milliseconds: 32));
            attempt(retriesLeft - 1, lastMaxExt);
          }
          return;
        }
        final maxExt = _pianoScrollController.position.maxScrollExtent;
        // El layout puede tardar varios frames en asentarse tras un cambio
        // de altura (p. ej. al activar/desactivar la digitación, que añade
        // o quita las tiras encima del piano) o simplemente en el primer
        // frame tras abrir la app. Reintentamos no solo cuando maxExt es 0,
        // sino también mientras siga cambiando de un intento a otro: un
        // valor positivo pero todavía provisional produce un centrado
        // desviado (el clamp corta el scroll antes de llegar al centro
        // real una vez el layout termina de crecer).
        if (maxExt <= 0 || (retriesLeft > 0 && maxExt != lastMaxExt)) {
          if (retriesLeft > 0) {
            await Future<void>.delayed(const Duration(milliseconds: 32));
            attempt(retriesLeft - 1, maxExt);
          }
          return;
        }
        final int anchorMidi;
        if (!forceMiddleC && _tabIndex == 3 && _generatedScaleJson != null) {
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
        final wIdx = cIdx >= 0
            ? cIdx
            : math.max(0, whiteMidi.indexWhere((m) => m >= anchorMidi));
        final keyCenterX = wIdx * whiteW + whiteW / 2;
        final centeredTarget = keyCenterX - viewportW / 2;
        final target = (requestedOffset ?? centeredTarget).clamp(0.0, maxExt);
        _pianoScrollController.jumpTo(target);
        if (forceMiddleC) {
          _startupPianoCenterPending = false;
        }
      });
    }

    attempt(8, -1.0);
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
    final ms = ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round() + 280;
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
      // No paramos aquí el resaltado: playChord en nativo devuelve el
      // control casi al instante (solo agenda el audio), muy antes de que
      // termine de sonar, así que parar aquí borraría el resaltado nada
      // más empezar. El temporizador de _scheduleHeldChordPlaybackAutoClear
      // ya se encarga de limpiarlo cuando el acorde termina de sonar.
      unawaited(
        _nativeAudioBridge.playChord(
          platform: 'android',
          notes: chordNotes,
          instrument: instrument,
          durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round(),
          volume: 0.92,
        ),
      );
      return;
    }
    if (Platform.isIOS) {
      final volume = (0.92 * (instrument == 'piano' ? 0.72 : 0.82)).clamp(
        0.0,
        1.0,
      );
      // Igual que en Android: no paramos el resaltado aquí, el temporizador
      // de _scheduleHeldChordPlaybackAutoClear ya lo hace cuando el acorde
      // termina de sonar de verdad.
      if (chordNotes.length > 1) {
        unawaited(
          _nativeAudioBridge.playChord(
            platform: 'ios',
            notes: chordNotes,
            instrument: instrument,
            durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round(),
            volume: volume,
          ),
        );
      } else {
        unawaited(
          _nativeAudioBridge.playTone(
            platform: 'ios',
            midi: chordNotes.first,
            instrument: instrument,
            durationMs: ((instrument == 'guitar' ? 1.45 : 1.35) * 1000).round(),
            volume: volume,
          ),
        );
      }
      return;
    }
    final starts = notes.map((midi) async {
      final player = await _playTone(
        midi: midi,
        instrument: instrument,
        durationSeconds: instrument == 'guitar' ? 1.45 : 1.35,
      );
      return MapEntry<int, AudioPlayerPort?>(midi, player);
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
    // Con salida MIDI seleccionada no reproducimos audio local para una
    // nota que ya llega de un teclado MIDI externo — ni tampoco la
    // reenviamos por MIDI-out, para no producir un eco de la misma nota.
    if (_soundOutput == 'midi') return;
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
      final json = detectChordLocal(
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
      case 'formula':
      case 'construction':
        final extrasMidi = _extractMidiList(json, <String>[
          'extras_midi',
        ]).toSet();
        final chordOnlyMidi = _extractMidiList(json, <String>[
          'notes_midi',
        ]).where((n) => !extrasMidi.contains(n)).toList();
        final result = interval_theory.chordFormulaAndConstruction(
          catalog: _chordTheoryCatalog,
          rootPc: json['root_pc'] as int?,
          suffix: json['suffix'] as String?,
          inversion: (json['inversion'] as int?) ?? 0,
          chordMidi: chordOnlyMidi,
          language: _language,
        );
        return key == 'formula' ? result.formula : result.construction;
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
      case 'formula':
      case 'construction':
        final generatedMidi = _extractMidiList(json, <String>['notes_midi']);
        final result = interval_theory.chordFormulaAndConstruction(
          catalog: _chordTheoryCatalog,
          rootPc: json['root_pc'] as int?,
          suffix: json['suffix'] as String?,
          inversion: (json['inversion'] as int?) ?? 0,
          chordMidi: generatedMidi,
          language: _language,
        );
        return key == 'formula' ? result.formula : result.construction;
      case 'description':
        final desc = json['description'] as String?;
        return desc?.isNotEmpty == true ? desc! : '';
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
            _helpAnchor(
              'generation_result_chord',
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
                        text: _chordResultValue('name'),
                        style: const TextStyle(
                          color: _text,
                          fontSize: 16,
                          height: 1.35,
                        ),
                      ),
                      if (_chordResultValue('description').isNotEmpty)
                        TextSpan(
                          text: '  (${_chordResultValue('description')})',
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
              helpId: 'generation_result_notes',
              labelEs: 'Notas',
              labelEn: 'Notes',
              value: _chordResultValue('notes'),
            ),
            _detectionResultRow(
              helpId: 'generation_result_formula',
              labelEs: 'Fórmula',
              labelEn: 'Formula',
              value: _chordResultValue('formula'),
            ),
            _detectionResultRow(
              helpId: 'generation_result_construction',
              labelEs: 'Construcción',
              labelEn: 'Construction',
              value: _chordResultValue('construction'),
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
        final patternName = json['pattern_name']?.toString().trim() ?? '';
        final localizedName =
            json['pattern_localized_name']?.toString().trim() ?? patternName;
        return localizedName.isEmpty
            ? '-'
            : scaleDisplayName(patternName, localizedName);
      case 'notes':
        final notes = (json['notes'] as List<dynamic>? ?? const <dynamic>[])
            .map((e) => e.toString())
            .where((e) => e.isNotEmpty)
            .toList(growable: false);
        return notes.isEmpty ? '-' : notes.join(' - ');
      case 'formula':
        final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
        return interval_theory.scaleFormulaFromMidi(scaleMidi);
      case 'pattern':
        final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
        return interval_theory.scalePatternFromMidi(scaleMidi);
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
              helpId: 'scales_result_formula',
              labelEs: 'Fórmula',
              labelEn: 'Formula',
              value: _scaleResultValue('formula'),
            ),
            _detectionResultRow(
              helpId: 'scales_result_pattern',
              labelEs: 'Patrón',
              labelEn: 'Pattern',
              value: _scaleResultValue('pattern'),
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
              helpId: 'detection_result_formula',
              labelEs: 'Fórmula',
              labelEn: 'Formula',
              value: _detectionResultValue('formula'),
            ),
            _detectionResultRow(
              helpId: 'detection_result_construction',
              labelEs: 'Construcción',
              labelEn: 'Construction',
              value: _detectionResultValue('construction'),
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
      final json = generateChordLocal(
        rootPc: _chordRootPc,
        suffix: _chordSuffix,
        inversion: _chordInversion,
        language: _language,
        preferFlat: _preferFlat,
        tonicLetterPc: _chordRootLetterPc,
      );
      _generatedChordJson = json;
      _chordGuitarVariant = 0;
      _generationInputStaffNotes.clear();
      _clearGenerationNoteHighlight();
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
      final json = generateChordLocal(
        rootPc: rootPc,
        suffix: suffix,
        inversion: 0,
        language: _language,
        preferFlat: _preferFlat,
      );
      _generatedChordJson = json;
      _chordGuitarVariant = 0;
      _generationInputStaffNotes.clear();
      _clearGenerationNoteHighlight();
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

  void _onCircleCanvasInteraction(
    Offset local,
    Size size, {
    required bool longPress,
  }) {
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
      final json = generateScaleLocal(
        tonicPc: _scaleTonicPc,
        patternName: _scalePatternName,
        language: _language,
        preferFlat: _preferFlat,
        tonicLetterPc: _scaleTonicLetterPc,
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
          '${_ui('Escala', 'Scale')}: ${scaleDisplayName(json['pattern_name']?.toString() ?? '', json['pattern_localized_name']?.toString() ?? json['pattern_name']?.toString() ?? '')}\n'
          '${_ui('Notas', 'Notes')}: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          '${_ui('Intervalos', 'Intervals')}: ${_intervalTextFromMidiList(scaleMidi)}';
      if (Platform.isIOS && scaleMidi.isNotEmpty) {
        final instrument = _instrumentView == 'guitar' ? 'guitar' : 'piano';
        final seconds = _instrumentView == 'guitar' ? 0.92 : 0.78;
        for (final midi in scaleMidi) {
          unawaited(
            _precacheTone(midi: midi, instrument: instrument, seconds: seconds),
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

  void _playScaleStaffNote(ScaleStaffHitRegion hit) {
    if (_tabIndex != 3 || _generatedScaleJson == null) return;
    if (_scaleLoopRunning) {
      _stopScaleLoop();
    }
    _scaleStaffHighlightTimer?.cancel();
    setState(() {
      _scaleCurrentNote = hit.midi;
      _scaleCurrentIsLeft = hit.isLeftHand;
      _scaleInputRawNote = null;
    });
    unawaited(_handleInstrumentNote(hit.midi, pressed: false));
    _scaleStaffHighlightTimer = Timer(const Duration(milliseconds: 720), () {
      _scaleStaffHighlightTimer = null;
      if (!mounted || _scaleLoopRunning || _scaleCurrentNote != hit.midi) {
        return;
      }
      setState(() {
        _scaleCurrentNote = null;
        _scaleCurrentIsLeft = null;
        _scaleInputRawNote = null;
      });
    });
  }

  void _playStaffPreviewNote(int midi) {
    if (_soundOutput == 'midi') {
      _sendMidiNoteOn(midi, 80);
      unawaited(
        Future<void>.delayed(
          const Duration(milliseconds: 720),
        ).then((_) => _sendMidiNoteOff(midi)),
      );
      return;
    }
    unawaited(
      _playTone(
        midi: midi,
        instrument: _instrumentView == 'guitar' ? 'guitar' : 'piano',
        durationSeconds: _instrumentView == 'guitar' ? 0.95 : 0.85,
        lowVolume: true,
      ),
    );
  }

  void _playGeneralStaffNote(int midi) {
    if (_tabIndex == 0) {
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
        _playStaffPreviewNote(midi);
      }
      return;
    }
    if (_tabIndex == 1 || _tabIndex == 2) {
      unawaited(_handleInstrumentNote(midi, pressed: false));
      return;
    }
    if (_tabIndex == 5 || _tabIndex == 7 || _tabIndex == 9) {
      if (_tabIndex == 7) {
        unawaited(_handleInstrumentNote(midi, pressed: false));
      } else if (_tabIndex == 9) {
        unawaited(_handleInstrumentNote(midi, pressed: true));
      } else {
        _playStaffPreviewNote(midi);
      }
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
    _scaleCurrentIsLeft = null; // null lets both clefs match by note value
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
            milliseconds: ((_instrumentView == 'guitar' ? 0.92 : 0.78) * 1000)
                .round(),
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

  int _activeScaleKeySignatureIndex(({int count, bool preferFlats}) signature) {
    if (_tabIndex != 3 || _scaleCurrentNote == null) return -1;
    final currentNote = _scaleCurrentNote!;
    final label = _scalePcNameMap()[_positiveMod12(currentNote)];
    return keySignatureIndexForScaleNote(
      label: label,
      midi: currentNote,
      signatureCount: signature.count,
      preferFlats: signature.preferFlats,
    );
  }

  int _activeChordKeySignatureIndex(
    ({int count, bool preferFlats}) signature,
    Iterable<int> activeNotes,
  ) {
    if (_tabIndex != 1 && _tabIndex != 2) return -1;
    for (final midi in activeNotes) {
      final index = keySignatureIndexForMidi(
        midi: midi,
        signatureCount: signature.count,
        preferFlats: signature.preferFlats,
      );
      if (index >= 0) return index;
    }
    return -1;
  }

  /// pc de cada letra natural (Do..Si) para el combo de tónica dividido en
  /// nota + alteración, y qué alteraciones son reales para cada una (sin
  /// enarmonías inventadas como Fb/Cb/E#/B#, que no existen en _pcLabelCanonical).
  static const List<int> _kRootLetterPcs = <int>[0, 2, 4, 5, 7, 9, 11];
  static const Map<int, List<String>> _kRootLetterAccidentals =
      <int, List<String>>{
        0: <String>['natural', 'sharp'],
        2: <String>['flat', 'natural', 'sharp'],
        4: <String>['flat', 'natural'],
        5: <String>['natural', 'sharp'],
        7: <String>['flat', 'natural', 'sharp'],
        9: <String>['flat', 'natural', 'sharp'],
        11: <String>['flat', 'natural'],
      };
  static const Map<String, String> _kAccidentalSymbols = <String, String>{
    'natural': '♮',
    'sharp': '♯',
    'flat': '♭',
  };

  static int _rootPcFromLetterAccidental(int letterPc, String accidental) {
    final offset = accidental == 'sharp' ? 1 : (accidental == 'flat' ? -1 : 0);
    return ((letterPc + offset) % 12 + 12) % 12;
  }

  /// Deriva (pc de letra natural, alteración) desde un pc final (0-11).
  static (int, String) _letterAndAccidentalFromPc(int pc) {
    final targetPc = ((pc % 12) + 12) % 12;
    for (final letterPc in _kRootLetterPcs) {
      for (final accidental in _kRootLetterAccidentals[letterPc]!) {
        if (_rootPcFromLetterAccidental(letterPc, accidental) == targetPc) {
          return (letterPc, accidental);
        }
      }
    }
    return (0, 'natural');
  }

  String _pcLabel(int pc) {
    if (_tabIndex == 3) {
      final byScale = _scalePcNameMap();
      final scaleLabel = byScale[pc % 12];
      if (scaleLabel != null && scaleLabel.isNotEmpty) {
        return scaleLabel;
      }
    }
    return _pcLabelCanonical(pc);
  }

  String _pianoKeyLabel(int midi) {
    final label = _pcLabel(midi % 12);
    return midi % 12 == 0 ? '$label${midi ~/ 12 - 1}' : label;
  }

  /// Nombre de nota neutro (Do, Do#, Re...), sin la ortografía diatónica de
  /// la escala actual — para selectores que deben listar las 12 tónicas
  /// posibles siempre igual (p. ej. no debe aparecer "Si#" en vez de "Do"
  /// solo porque la última escala generada lo deletreaba así).
  String _pcLabelCanonical(int pc) {
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

  /// Combo de tónica dividido en nota natural + alteración: sustituye al
  /// dropdown único de 12 semitonos. [rootPc] es el pc actual (0-11) y
  /// [onPc] recibe el nuevo pc combinando letra+alteración elegidas.
  /// [savedLetterPc]/[savedAccidental] son el estado explícito guardado por el
  /// caller (p. ej. _chordRootLetterPc/_chordRootAccidental). Si ya no
  /// coinciden con [rootPc] (cambiado desde otro sitio, como el Círculo de
  /// quintas), se deriva una combinación por defecto — pero mientras
  /// coincidan, se respeta la elección real del usuario en vez de recalcular
  /// una enarmonía "canónica" (evita que Si♭ se muestre como La# solo porque
  /// La va antes que Si en el orden de letras).
  Widget _buildTonicLetterAccidentalDropdowns({
    required int rootPc,
    required int savedLetterPc,
    required String savedAccidental,
    required void Function(int pc, int letterPc, String accidental) onPc,
    Key? letterKey,
    Key? accidentalKeyPrefix,
    String? letterHelpId,
    String? accidentalHelpId,
    double helpAnchorHeight = 56,
  }) {
    int letterPc;
    String accidental;
    if (_rootPcFromLetterAccidental(savedLetterPc, savedAccidental) == rootPc) {
      letterPc = savedLetterPc;
      accidental = savedAccidental;
    } else {
      (letterPc, accidental) = _letterAndAccidentalFromPc(rootPc);
    }
    final accidentals = _kRootLetterAccidentals[letterPc]!;
    final safeAccidental = accidentals.contains(accidental)
        ? accidental
        : 'natural';
    Widget withHelp(String? helpId, Widget child) => helpId == null
        ? child
        : helpAnchorHeight == 56
        ? _helpFixedHeightAnchor(helpId, child)
        : _helpFixedHeightAnchor(helpId, child, height: helpAnchorHeight);

    return Row(
      children: <Widget>[
        Expanded(
          flex: 3,
          child: withHelp(
            letterHelpId,
            DropdownButtonFormField<int>(
              key: letterKey ?? ValueKey<int>(letterPc),
              initialValue: letterPc,
              isExpanded: true,
              dropdownColor: _surfaceDark,
              style: const TextStyle(color: _text),
              decoration: InputDecoration(
                labelText: _ui('Tónica', 'Tonic'),
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 12,
                ),
              ),
              items: _kRootLetterPcs
                  .map(
                    (pc) => DropdownMenuItem<int>(
                      value: pc,
                      child: Text(_pcLabelCanonical(pc)),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                if (value == null) return;
                final newAccidentals = _kRootLetterAccidentals[value]!;
                final keepAccidental = newAccidentals.contains(safeAccidental)
                    ? safeAccidental
                    : 'natural';
                onPc(
                  _rootPcFromLetterAccidental(value, keepAccidental),
                  value,
                  keepAccidental,
                );
              },
            ),
          ),
        ),
        const SizedBox(width: 6),
        SizedBox(
          width: 64,
          child: withHelp(
            accidentalHelpId,
            DropdownButtonFormField<String>(
              key:
                  accidentalKeyPrefix ??
                  ValueKey<String>('acc-$letterPc-$safeAccidental'),
              initialValue: safeAccidental,
              isExpanded: true,
              dropdownColor: _surfaceDark,
              style: const TextStyle(color: _text),
              decoration: const InputDecoration(
                labelText: '',
                isDense: true,
                contentPadding: EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 12,
                ),
              ),
              items: accidentals
                  .map(
                    (a) => DropdownMenuItem<String>(
                      value: a,
                      child: Text(_kAccidentalSymbols[a]!),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                if (value == null) return;
                onPc(
                  _rootPcFromLetterAccidental(letterPc, value),
                  letterPc,
                  value,
                );
              },
            ),
          ),
        ),
      ],
    );
  }

  /// Muchos tipos renderizan ♭ más pequeño que `#`; se escala la alteración para
  /// equiparar el aspecto en teclas y etiquetas.
  List<InlineSpan> _splitPitchClassLabelSpans(
    String label,
    TextStyle baseStyle,
  ) {
    final fz = baseStyle.fontSize ?? 14;
    final accFlatStyle = baseStyle.copyWith(fontSize: fz * 1.22, height: 1.0);
    final accSharpStyle = baseStyle.copyWith(fontSize: fz * 1.06, height: 1.0);
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
      return compact
          ? _ui('Fundamental', 'Root')
          : _ui('Posición fundamental', 'Root position');
    }
    final names = _language == 'en' ? inversionNamesEn : inversionNamesEs;
    if (inversion < names.length) {
      final name = names[inversion];
      return _language == 'en'
          ? '${name[0].toUpperCase()}${name.substring(1)}'
          : name;
    }
    return _ui('$inversionª inversión', 'Inversion $inversion');
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
        (_tunerCaptureSession.actualSampleRate?.round() ?? _tunerSampleRate)
            .clamp(8000, 96000);
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
      _tunerError = '';
      _tunerSmoothedFreq = 0.0;
      _tunerSpectrumBins = List<double>.filled(96, 0.0);
      await _tunerCaptureSession.start(
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
      await _tunerCaptureSession.stop();
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
      _buildIntervalGenerationPage(),
      _buildNoteDetectionPage(),
      _buildIntervalPracticePage(),
    ];

    return Stack(
      children: <Widget>[
        Scaffold(
          appBar: AppBar(
            toolbarHeight: compactPhone
                ? (portrait ? 60 : 64)
                : (portrait ? 64 : 74),
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
                final availableForTitle = math.max(
                  80.0,
                  titleConstraints.maxWidth - safetyMargin,
                );
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
                      items: _orderedEnabledModes(enabledModes)
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
                        _rememberPianoScrollForMode(_tabIndex);
                        setState(() {
                          _tabIndex = value;
                          _setHelpMode(false);
                          if (value == 0 ||
                              value == 5 ||
                              value == 7 ||
                              value == 8 ||
                              value == 9) {
                            _instrumentView = 'piano';
                          }
                          _requestPianoScrollForMode(value);
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
                        _clearGenerationNoteHighlight();
                        _intervalGenPlaybackTimer?.cancel();
                        _intervalGenPlayingIdx = null;
                        _cancelIntervalPracticePlayback();
                        _detectionPlayPressed = false;
                        _generationPlayPressed = false;
                        if (value != 0) {
                          _detectionMidiHeldNotes.clear();
                        }
                        if (value != 1 && value != 2) {
                          _generationMidiHeldNotes.clear();
                        }
                        if (value != 3) {
                          _scaleMidiHeldNotes.clear();
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
              _helpAnchor(
                'midi_toggle',
                Padding(
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
                      backgroundColor: _midiInputEnabled
                          ? _accent
                          : _surfaceDark,
                      padding: EdgeInsets.symmetric(
                        horizontal: compactPhone ? 10 : 14,
                        vertical: compactPhone ? 6 : 8,
                      ),
                    ),
                    child: Text(_midiInputEnabled ? 'MIDI: On' : 'MIDI: Off'),
                  ),
                ),
              ),
              if (_midiInputEnabled)
                _helpAnchor(
                  'sound_output',
                  Padding(
                    padding: EdgeInsets.only(right: compactPhone ? 6 : 8),
                    child: OutlinedButton.icon(
                      onPressed: () => setState(() {
                        _soundOutput = _soundOutput == 'audio'
                            ? 'midi'
                            : 'audio';
                      }),
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(
                          color: _soundOutput == 'midi' ? _accent : _border,
                          width: _soundOutput == 'midi' ? 2 : 1,
                        ),
                        foregroundColor: _soundOutput == 'midi'
                            ? const Color(0xFF1A222D)
                            : _text,
                        backgroundColor: _soundOutput == 'midi'
                            ? _accent
                            : _surfaceDark,
                        padding: EdgeInsets.symmetric(
                          horizontal: compactPhone ? 8 : 12,
                          vertical: compactPhone ? 6 : 8,
                        ),
                      ),
                      icon: Icon(
                        _soundOutput == 'midi' ? Icons.piano : Icons.volume_up,
                        size: 16,
                      ),
                      label: Text(
                        _soundOutput == 'midi'
                            ? _ui('Salida MIDI', 'MIDI out')
                            : _ui('Audio', 'Audio'),
                      ),
                    ),
                  ),
                ),
              _helpAnchor(
                'accidental',
                Container(
                  constraints: BoxConstraints(minWidth: compactPhone ? 64 : 76),
                  margin: EdgeInsets.only(right: compactPhone ? 6 : 8),
                  padding: EdgeInsets.symmetric(
                    horizontal: compactPhone ? 6 : 8,
                  ),
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
                        DropdownMenuItem<String>(
                          value: 'sharp',
                          child: Text('#'),
                        ),
                        DropdownMenuItem<String>(
                          value: 'flat',
                          child: Text('♭'),
                        ),
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
                ),
              ),
              _helpAnchor(
                'help_toggle',
                IconButton(
                  tooltip: _ui('Ayuda', 'Help'),
                  onPressed: _toggleHelpMode,
                  icon: Icon(
                    _helpActive ? Icons.help_center : Icons.help_outline,
                    color: _helpActive ? _accent : null,
                  ),
                ),
              ),
              _helpAnchor(
                'settings',
                IconButton(
                  tooltip: _ui('Configuración', 'Settings'),
                  onPressed: _openSettingsPanel,
                  icon: const Icon(Icons.settings),
                ),
              ),
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
            // SafeArea solo abajo: en Android con navegación por gestos, el
            // contenido final de cada pantalla (p.ej. el selector de variante
            // de acorde) quedaba tapado por la barra de gestos del sistema.
            child: SafeArea(
              top: false,
              child: Column(
                children: <Widget>[
                  if (_midiInputEnabled && _midiError.isNotEmpty)
                    Container(
                      width: double.infinity,
                      color: const Color(0xFF3A1414),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      child: Text(
                        _midiError,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  Expanded(child: pages[currentTab]),
                ],
              ),
            ),
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
            final compactLandscape =
                constraints.maxWidth > constraints.maxHeight;
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
                            flex: _tabIndex == 7 || _tabIndex == 9 ? 8 : 11,
                            child: staffPanel,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            flex: _tabIndex == 7 || _tabIndex == 9 ? 12 : 9,
                            child: controlsPanel,
                          ),
                        ],
                      ),
                    )
                  else ...<Widget>[
                    SizedBox(height: staffHeight, child: staffPanel),
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
                      flex: _tabIndex == 7 || _tabIndex == 9 ? 42 : 57,
                      child: staffPanel,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: _tabIndex == 7 || _tabIndex == 9 ? 58 : 43,
                      child: controlsPanel,
                    ),
                  ],
                )
              : Column(
                  children: <Widget>[
                    Expanded(flex: 56, child: staffPanel),
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
      6 => _ui('Afinador', 'Tuner'),
      _ => _ui('Pentagrama', 'Staff'),
    };
    final guitarStaffMode =
        _instrumentView == 'guitar' &&
        (_tabIndex == 0 || _tabIndex == 1 || _tabIndex == 2);
    int staffMidi(int midi) => guitarStaffMode ? midi + 12 : midi;
    List<int> guitarDisplayVoicing(
      Iterable<int> source, {
      bool lowerBass = false,
    }) {
      final mapped = source.map(staffMidi).toList();
      if (_tabIndex != 9) {
        mapped.sort();
      }
      if (guitarStaffMode && lowerBass && mapped.isNotEmpty) {
        mapped[0] -= 12;
      }
      return mapped;
    }

    final lowerGuitarBass =
        (_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'guitar';
    final displayNotes = guitarDisplayVoicing(
      notes,
      lowerBass: lowerGuitarBass,
    );
    final sourceNotes = notes.toList();
    if (_tabIndex != 9) {
      sourceNotes.sort();
    }
    final displayToSourceNote = <int, int>{};
    for (
      var index = 0;
      index < sourceNotes.length && index < displayNotes.length;
      index += 1
    ) {
      displayToSourceNote[displayNotes[index]] = sourceNotes[index];
    }
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
                  _extractMidiList(_generatedChordJson!, <String>[
                    'notes_midi',
                  ]),
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
    final chordForStaff = _tabIndex == 0
        ? _detectionResultJson
        : ((_tabIndex == 1 || _tabIndex == 2) ? _generatedChordJson : null);
    final notePreferFlats = chordStaffNotePreferFlats(
      chord: chordForStaff,
      displayToSourceNote: displayToSourceNote,
      additionalDisplayNotes: displayGenerationLhNotes,
    );
    final bool generationPlaybackActive =
        (_tabIndex == 1 || _tabIndex == 2) &&
        (_generationPlayPressed ||
            _heldChordNativeNotes.isNotEmpty ||
            _heldChordPlayers.isNotEmpty ||
            _generationInputStaffNotes.isNotEmpty);
    final displayGenerationPlayingNotes = (_tabIndex == 1 || _tabIndex == 2)
        ? (generationPlaybackActive
              // No usamos lowerBass tal cual (que baja el índice [0] del
              // propio conjunto resaltado): con una sola nota tocada con el
              // dedo, ese conjunto tiene un solo elemento y "el más grave"
              // sería siempre esa nota suelta, desplazándola mal. En su
              // lugar, comparamos contra la nota que SÍ se bajó una octava
              // en el voicing completo (displayNotes) y aplicamos el mismo
              // desplazamiento solo si es esa nota concreta la que suena.
              ? guitarDisplayVoicing(_generationPlayingNotesForStaff()).map((
                  n,
                ) {
                  if (lowerGuitarBass &&
                      displayNotes.isNotEmpty &&
                      n == displayNotes[0] + 12) {
                    return n - 12;
                  }
                  return n;
                }).toSet()
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
    final activeKeySigIndex = _tabIndex == 3
        ? _activeScaleKeySignatureIndex(staffKeySig)
        : _activeChordKeySignatureIndex(
            staffKeySig,
            displayGenerationPlayingNotes,
          );
    final imelMode = _tabIndex == 5 && _intervalMelodyMode;
    final imelSemitones = _tabIndex == 5 ? _getIntervalSemitones() : null;
    final imelMelody = imelSemitones != null
        ? getIntervalMelody(imelSemitones)
        : null;
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
                style: const TextStyle(
                  color: _muted,
                  fontSize: 14,
                  height: 1.3,
                ),
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
                            idleLabel: _ui(
                              'Pulsa Play para iniciar',
                              'Press Play to start',
                            ),
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
                                  backgroundColor: _metroRunning
                                      ? _accent
                                      : _surfaceDark,
                                  foregroundColor: _metroRunning
                                      ? const Color(0xFF1A222D)
                                      : _text,
                                  minimumSize: const Size(0, 46),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 18,
                                    vertical: 12,
                                  ),
                                  visualDensity: VisualDensity.compact,
                                  tapTargetSize:
                                      MaterialTapTargetSize.shrinkWrap,
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
                6 => CustomPaint(
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
                _ => LayoutBuilder(
                  builder: (context, constraints) {
                    final panelSize = Size(
                      constraints.maxWidth,
                      constraints.maxHeight,
                    );
                    return GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTapDown: (details) {
                        if (_tabIndex == 3) {
                          final hit = scaleStaffHitAt(
                            position: details.localPosition,
                            size: panelSize,
                            rightHandNotes: displayScaleRhNotes,
                            leftHandNotes: displayScaleLhNotes,
                            keySignatureCount: staffKeySig.count,
                          );
                          if (hit != null) {
                            _playScaleStaffNote(hit);
                          }
                          return;
                        }
                        if (!const <int>{
                              0,
                              1,
                              2,
                              5,
                              7,
                              9,
                            }.contains(_tabIndex) ||
                            imelMode) {
                          return;
                        }
                        final hit = staffNoteHitAt(
                          position: details.localPosition,
                          size: panelSize,
                          notes: displayNotes,
                          keySignatureCount: staffKeySig.count,
                          preferFlats: staffKeySig.preferFlats,
                          notePreferFlats: notePreferFlats,
                          intervalSequenceMode:
                              _tabIndex == 5 ||
                              _tabIndex == 7 ||
                              _tabIndex == 9,
                        );
                        if (hit != null) {
                          _playGeneralStaffNote(
                            displayToSourceNote[hit.midi] ?? hit.midi,
                          );
                        }
                      },
                      child: CustomPaint(
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
                          notePreferFlats: notePreferFlats,
                          activeKeySignatureIndex: activeKeySigIndex,
                          intervalMelodyMode: imelMode,
                          intervalMelodyNotes: imelNotes,
                          intervalMelodyDurations: imelDurations,
                          intervalPlayingIdx: _tabIndex == 5
                              ? _intervalPlayingIdx
                              : (_tabIndex == 7
                                    ? _intervalGenPlayingIdx
                                    : (_tabIndex == 9 &&
                                              _intervalPracticePlayingNote !=
                                                  null
                                          ? displayNotes.indexOf(
                                              _intervalPracticePlayingNote!,
                                            )
                                          : null)),
                          intervalPlayingNotes: _tabIndex == 9
                              ? _intervalPracticePlayingNotes
                              : const <int>{},
                          intervalSequenceMode:
                              _tabIndex == 5 ||
                              _tabIndex == 7 ||
                              _tabIndex == 9,
                          intervalQuestion:
                              _tabIndex == 9 &&
                              _intervalPracticeStarted &&
                              _intervalPracticeAnswerCorrect == null,
                          intervalCorrectNote:
                              _tabIndex == 9 &&
                                  _intervalPracticeAnswerCorrect != null
                              ? _intervalPracticeQuestionNotes().last
                              : null,
                          intervalWrongNote:
                              _tabIndex == 9 &&
                                  _intervalPracticeAnswerCorrect == false
                              ? _intervalPracticeAnswerNote
                              : null,
                          intervalBeatsPerBar: imelBeatsPerBar,
                          intervalAnacrusis: imelAnacrusis,
                        ),
                        child: const SizedBox.expand(),
                      ),
                    );
                  },
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
            final overlayBounds = Offset.zero & constraints.biggest;
            final resolved = _resolvedHelpSteps(
              overlayContext,
              overlayBounds: overlayBounds,
            );
            final helpToggleRect = _helpRectFor(
              overlayContext,
              'help_toggle',
              overlayBounds: overlayBounds,
            );
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
            final helpTargets = resolved
                .map((r) => r.highlightRect)
                .toList(growable: false);
            final helpPulse =
                0.5 +
                (0.5 * math.sin(_helpOverlayController.value * math.pi * 2));
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
                    child: AnimatedOpacity(
                      opacity: _helpBannerVisible ? 1.0 : 0.0,
                      duration: const Duration(milliseconds: 600),
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 520),
                        margin: const EdgeInsets.symmetric(horizontal: 24),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 18,
                          vertical: 12,
                        ),
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
                        onTap: () {
                          _helpBannerTimer?.cancel();
                          setState(() {
                            _helpSelectedId = item.step.id;
                            _helpBannerVisible = false;
                          });
                        },
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
                                  _ui(
                                    selected.step.titleEs,
                                    selected.step.titleEn,
                                  ),
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
                                      _ui(
                                        selected.step.bodyEs,
                                        selected.step.bodyEn,
                                      ),
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
                                        onPressed: () => setState(
                                          () => _helpSelectedId = null,
                                        ),
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
                                            onPressed: () => setState(
                                              () => _helpSelectedId = null,
                                            ),
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
    final metronomeFixedPiano =
        _tabIndex == 4 || _tabIndex == 5 || _tabIndex == 8 || _tabIndex == 9;
    final showRightControls =
        _tabIndex == 1 || _tabIndex == 2 || _tabIndex == 3 || _tabIndex == 7;
    final displayInstrumentView = metronomeFixedPiano
        ? 'piano'
        : _instrumentView;
    final pianoHelpId = switch (_tabIndex) {
      8 => 'note_detection_piano',
      9 => 'interval_practice_piano',
      3 => 'scales_instrument_piano',
      2 => 'circle_instrument_piano_btn',
      7 => 'interval_generation_instrument_piano',
      _ => 'generation_instrument_piano',
    };
    final guitarHelpId = switch (_tabIndex) {
      3 => 'scales_instrument_guitar',
      2 => 'circle_instrument_guitar_btn',
      7 => 'interval_generation_instrument_guitar',
      _ => 'generation_instrument_guitar',
    };
    final handHelpId = switch (_tabIndex) {
      3 => 'scales_guitar_hand',
      2 => 'circle_guitar_hand',
      7 => 'interval_generation_guitar_hand',
      _ => 'generation_guitar_hand',
    };
    final guitarVariantHelpId = _tabIndex == 2
        ? 'circle_guitar_variant'
        : 'generation_guitar_variant';
    final instrumentSurfaceHelpId = switch (_tabIndex) {
      0 => 'detection_instrument',
      1 => 'generation_instrument',
      2 => 'circle_instrument',
      3 => 'scales_instrument',
      4 => 'metronome_instrument',
      5 => 'interval_detection_instrument',
      7 => 'interval_generation_instrument',
      9 => 'interval_practice_piano',
      _ => 'generation_instrument',
    };
    final panelHeight = switch (_tabIndex) {
      4 => portrait ? 152.0 : 168.0,
      7 => compactPhone ? 220.0 : (_instrumentView == 'guitar' ? 188.0 : 148.0),
      9 => compactPhone ? 168.0 : 156.0,
      3 when _scaleMetronomeOnly =>
        compactPhone ? (portrait ? 188.0 : 212.0) : (portrait ? 168.0 : 184.0),
      3 => compactPhone ? (portrait ? 204.0 : 232.0) : 188.0,
      1 || 2 =>
        compactPhone ? (portrait ? 204.0 : 232.0) : (portrait ? 188.0 : 220.0),
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
                              _instToggle('guitar', _ui('Guitarra', 'Guitar')),
                            ),
                          ),
                          if ((_tabIndex == 1 || _tabIndex == 2) &&
                              _instrumentView == 'guitar' &&
                              chordVoicings.length > 1) ...<Widget>[
                            _helpAnchor(
                              guitarVariantHelpId,
                              Row(
                                mainAxisSize: MainAxisSize.min,
                                children: <Widget>[
                                  OutlinedButton(
                                    onPressed: safeVariant > 0
                                        ? () => _selectChordGuitarVariant(
                                            safeVariant - 1,
                                          )
                                        : null,
                                    child: const Icon(Icons.chevron_left),
                                  ),
                                  const SizedBox(width: 8),
                                  OutlinedButton(
                                    onPressed:
                                        safeVariant < chordVoicings.length - 1
                                        ? () => _selectChordGuitarVariant(
                                            safeVariant + 1,
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
                                  key: ValueKey<String>(
                                    'hand_$_guitarHandedness',
                                  ),
                                  initialValue: _guitarHandedness,
                                  dropdownColor: _surfaceDark,
                                  style: const TextStyle(color: _text),
                                  decoration: InputDecoration(
                                    isDense: true,
                                    labelText: _ui('Mano', 'Hand'),
                                  ),
                                  items: <DropdownMenuItem<String>>[
                                    DropdownMenuItem<String>(
                                      value: 'right',
                                      child: Text(
                                        _ui('Diestro', 'Right-handed'),
                                      ),
                                    ),
                                    DropdownMenuItem<String>(
                                      value: 'left',
                                      child: Text(_ui('Zurdo', 'Left-handed')),
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
                                _instToggle(
                                  'guitar',
                                  _ui('Guitarra', 'Guitar'),
                                ),
                              ),
                              if (_instrumentView == 'guitar') ...<Widget>[
                                const SizedBox(height: 8),
                                _helpAnchor(
                                  handHelpId,
                                  DropdownButtonFormField<String>(
                                    key: ValueKey<String>(
                                      'hand_$_guitarHandedness',
                                    ),
                                    initialValue: _guitarHandedness,
                                    dropdownColor: _surfaceDark,
                                    style: const TextStyle(color: _text),
                                    decoration: InputDecoration(
                                      isDense: true,
                                      labelText: _ui('Mano', 'Hand'),
                                    ),
                                    items: <DropdownMenuItem<String>>[
                                      DropdownMenuItem<String>(
                                        value: 'right',
                                        child: Text(
                                          _ui('Diestro', 'Right-handed'),
                                        ),
                                      ),
                                      DropdownMenuItem<String>(
                                        value: 'left',
                                        child: Text(
                                          _ui('Zurdo', 'Left-handed'),
                                        ),
                                      ),
                                    ],
                                    onChanged: (value) {
                                      if (value != null) {
                                        setState(
                                          () => _guitarHandedness = value,
                                        );
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
              guitarVariantHelpId,
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  OutlinedButton(
                    onPressed: chordVoicings.length > 1 && safeVariant > 0
                        ? () => _selectChordGuitarVariant(safeVariant - 1)
                        : null,
                    child: const Icon(Icons.chevron_left),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    chordVoicings.isEmpty
                        ? _ui('Variante 0/0', 'Variant 0/0')
                        : _ui(
                            'Variante ${safeVariant + 1}/${chordVoicings.length}',
                            'Variant ${safeVariant + 1}/${chordVoicings.length}',
                          ),
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
                        ? () => _selectChordGuitarVariant(safeVariant + 1)
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
        final instrumentChanging = _instrumentView != key;
        if (instrumentChanging && _instrumentView == 'piano') {
          _rememberPianoScrollForMode(_tabIndex);
        }
        setState(() {
          if (instrumentChanging && (_tabIndex == 1 || _tabIndex == 2)) {
            _generationInputStaffNotes.clear();
            _clearGenerationNoteHighlight();
            _stopHeldChord();
            _stopHeldInputs();
            _generationPlayPressed = false;
          }
          _instrumentView = key;
          if (instrumentChanging && key == 'piano') {
            _requestPianoScrollForMode(_tabIndex);
          }
          if (_tabIndex == 3) {
            // _scaleRhNotes() fuerza 1 octava en guitarra; al volver a
            // piano hay que recalcular la digitación con las octavas
            // realmente seleccionadas, si no se queda con solo 1 octava.
            _updateScaleFingeringsMap();
          }
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
    // Las tiras de digitación pertenecen exclusivamente a Escalas. El resto
    // de modos aprovecha toda la altura disponible para el teclado.
    if (_tabIndex != 3) {
      return _buildPianoStrip(activeMidi);
    }
    final showStrips =
        _tabIndex == 3 &&
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
    return LayoutBuilder(
      builder: (context, constraints) {
        const stripH = 22.0;
        const gap = 2.0;
        final viewportW = constraints.maxWidth;
        final pianoViewH = (constraints.maxHeight - 2 * (stripH + gap)).clamp(
          60.0,
          (pianoWhiteKeyHeight + 12).toDouble(),
        );

        final allWhite = List<int>.generate(
          _kPianoHighMidi - _kPianoLowMidi + 1,
          (i) => _kPianoLowMidi + i,
        ).where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12)).toList();

        final effectiveW = computePianoKeyMetrics(
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
            final bool isBlack = const <int>{
              1,
              3,
              6,
              8,
              10,
            }.contains(midi % 12);
            final double x;
            if (isBlack) {
              final wIdx = allWhite.indexWhere((m) => m >= midi);
              x = (wIdx < 0 ? allWhite.length - 1 : wIdx) * effectiveW;
            } else {
              final wIdx = allWhite.indexOf(midi);
              x = wIdx < 0 ? 0 : wIdx * effectiveW;
            }
            final bool isActive =
                _scaleLoopRunning &&
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
      },
    );
  }

  Widget _intervalPianoMarker({
    required int midi,
    required int? rootMidi,
    required double size,
    required double top,
    required double left,
  }) {
    final isRoot = midi == rootMidi;
    final practiceWrong =
        _tabIndex == 9 &&
        _intervalPracticeAnswerCorrect == false &&
        midi == _intervalPracticeAnswerNote;
    final practiceCorrect =
        _tabIndex == 9 &&
        _intervalPracticeAnswerCorrect != null &&
        midi == _intervalPracticeQuestionNotes().last;
    final fill = practiceWrong
        ? const Color(0xFFE35D67)
        : (practiceCorrect || isRoot
              ? const Color(0xFF32D74B)
              : const Color(0xFFF6B60B));
    final outline = practiceWrong
        ? const Color(0xFF9E2E38)
        : (practiceCorrect || isRoot
              ? const Color(0xFF1E8C38)
              : const Color(0xFF8D6B00));
    return Positioned(
      top: top,
      left: left,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: fill,
          shape: BoxShape.circle,
          border: Border.all(color: outline, width: 1.5),
        ),
        alignment: Alignment.center,
        child: FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            _pcLabel(midi % 12),
            style: TextStyle(
              color: const Color(0xFF101010),
              fontWeight: FontWeight.w700,
              fontSize: size * 0.4,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPianoStrip(Set<int> activeMidi, {double? forcedWhiteW}) {
    final midiRange = List<int>.generate(
      _kPianoHighMidi - _kPianoLowMidi + 1,
      (i) => _kPianoLowMidi + i,
    );
    final whiteMidi = midiRange
        .where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12))
        .toList();
    final active = _tabIndex == 5 || _tabIndex == 7 || _tabIndex == 9
        ? <int>{}
        : activeMidi.toSet();
    final extras = _instrumentExtrasForCurrentTab();
    final scaleRh = (_tabIndex == 3 ? _scaleRhNotes() : <int>[]).toSet();
    final intervalNotes = _tabIndex == 5
        ? List<int>.from(_intervalNotes)
        : (_tabIndex == 7
              ? _intervalGenerationNotes()
              : (_tabIndex == 9
                    ? _intervalPracticeDisplayNotes()
                    : const <int>[]));
    final intervalNoteSet = intervalNotes.toSet();
    final intervalRootMidi = intervalNotes.isEmpty ? null : intervalNotes.first;
    final intervalPlayingIdx = _tabIndex == 5
        ? _intervalPlayingIdx
        : (_tabIndex == 7
              ? _intervalGenPlayingIdx
              : (_tabIndex == 9 && _intervalPracticePlayingNote != null
                    ? intervalNotes.indexOf(_intervalPracticePlayingNote!)
                    : null));
    final intervalCurrentMidi =
        intervalPlayingIdx != null &&
            intervalPlayingIdx >= 0 &&
            intervalPlayingIdx < intervalNotes.length
        ? intervalNotes[intervalPlayingIdx]
        : null;
    final intervalCurrentNotes = _tabIndex == 9
        ? _intervalPracticePlayingNotes
        : <int>{?intervalCurrentMidi};
    final chordGenPiano =
        (_tabIndex == 1 || _tabIndex == 2) && _instrumentView == 'piano';
    final chordRh = chordGenPiano && _generatedChordJson != null
        ? _extractMidiList(_generatedChordJson!, <String>['notes_midi'])
        : const <int>[];
    final chordLh = chordGenPiano
        ? chordRh.map((n) => n - 12).where((n) => n >= _kPianoLowMidi).toList()
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
        final viewportH =
            (constraints.maxHeight.isFinite
                    ? constraints.maxHeight
                    : pianoWhiteKeyHeight + 12)
                .clamp(0.0, pianoWhiteKeyHeight + 12);
        final metrics = computePianoKeyMetrics(
          viewportW: viewportW,
          viewportH: viewportH,
          whiteKeyCount: whiteMidi.length,
        );
        final whiteW = forcedWhiteW ?? metrics.whiteW;
        final whiteH = forcedWhiteW != null
            ? (forcedWhiteW * pianoKeyAspect).clamp(0.0, viewportH)
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
                              final isIntervalCurrent = intervalCurrentNotes
                                  .contains(midi);
                              final isExtra = extras.contains(midi);
                              final isScaleCurrent =
                                  _tabIndex == 3 &&
                                  ((_scaleCurrentNote != null &&
                                          _scaleCurrentNote == midi) ||
                                      _scaleMidiHeldNotes.contains(midi));
                              final rh = rhFinger[midi];
                              final lh = lhFinger[midi];
                              final genKeyHi =
                                  chordGenPiano &&
                                  _generatedChordJson != null &&
                                  (_generationNoteHighlightMidi == midi ||
                                      _generationMidiHeldNotes.contains(midi) ||
                                      _heldChordNativeNotes.contains(midi));
                              final inChordRh = chordRhSet.contains(midi);
                              final inChordLhOnly =
                                  chordLhSet.contains(midi) &&
                                  !chordRhSet.contains(midi);
                              return Listener(
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
                                  width: whiteW,
                                  height: whiteH,
                                  decoration: BoxDecoration(
                                    color: isIntervalCurrent
                                        ? const Color(0xFF4DA3EA)
                                        : chordGenPiano &&
                                              _generatedChordJson != null
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
                                                          ? const Color(
                                                              0xFFF3C64F,
                                                            )
                                                          : const Color(
                                                              0xFFF5F4EF,
                                                            )))),
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
                                      if (_showKeyNames &&
                                          !(_tabIndex == 8 &&
                                              !_noteDetectionDetailsVisible))
                                        Align(
                                          alignment: Alignment.bottomCenter,
                                          child: Padding(
                                            padding: const EdgeInsets.only(
                                              bottom: 6,
                                            ),
                                            child: Text.rich(
                                              TextSpan(
                                                children:
                                                    _splitPitchClassLabelSpans(
                                                      _pianoKeyLabel(midi),
                                                      const TextStyle(
                                                        color: Color(
                                                          0xFF1A222D,
                                                        ),
                                                        fontWeight:
                                                            FontWeight.w700,
                                                        fontSize: 11,
                                                      ),
                                                    ),
                                              ),
                                              maxLines: 1,
                                              softWrap: false,
                                            ),
                                          ),
                                        ),
                                      if (_tabIndex == 3 &&
                                          scaleRh.contains(midi))
                                        Builder(
                                          builder: (context) {
                                            final isTonic =
                                                (midi % 12) ==
                                                (_scaleTonicPc % 12);
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
                                                        ? const Color(
                                                            0xFF1E8C38,
                                                          )
                                                        : const Color(
                                                            0xFF8D6B00,
                                                          ),
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
                                                      fontWeight:
                                                          FontWeight.w700,
                                                      fontSize: 9,
                                                    ),
                                                  ),
                                                ),
                                              ),
                                            );
                                          },
                                        ),
                                      if (intervalNoteSet.contains(midi))
                                        _intervalPianoMarker(
                                          midi: midi,
                                          rootMidi: intervalRootMidi,
                                          size: 22,
                                          top: whiteMarkerTop,
                                          left: (whiteW - 22) / 2,
                                        ),
                                      if (chordGenPiano && rh != null)
                                        marker(
                                          size: 22,
                                          color: const Color(0xFF33C6FF),
                                          digit: rh,
                                          top: whiteMarkerTop,
                                          left: (whiteW - 22) / 2,
                                        ),
                                      if (chordGenPiano &&
                                          rh == null &&
                                          lh != null)
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
                                (m) => const <int>{
                                  1,
                                  3,
                                  6,
                                  8,
                                  10,
                                }.contains(m % 12),
                              )
                              .map((midi) {
                                final isActive = active.contains(midi);
                                final isIntervalCurrent = intervalCurrentNotes
                                    .contains(midi);
                                final isExtra = extras.contains(midi);
                                final isScaleCurrent =
                                    _tabIndex == 3 &&
                                    _scaleCurrentNote != null &&
                                    _scaleCurrentNote == midi;
                                final rh = rhFinger[midi];
                                final lh = lhFinger[midi];
                                final genKeyHi =
                                    chordGenPiano &&
                                    _generatedChordJson != null &&
                                    (_generationNoteHighlightMidi == midi ||
                                        _generationMidiHeldNotes.contains(
                                          midi,
                                        ) ||
                                        _heldChordNativeNotes.contains(midi));
                                final inChordRh = chordRhSet.contains(midi);
                                final inChordLhOnly =
                                    chordLhSet.contains(midi) &&
                                    !chordRhSet.contains(midi);
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
                                        color: isIntervalCurrent
                                            ? const Color(0xFF0078D7)
                                            : chordGenPiano &&
                                                  _generatedChordJson != null
                                            ? (inChordRh
                                                  ? (genKeyHi
                                                        ? const Color(
                                                            0xFF005CA6,
                                                          )
                                                        : const Color(
                                                            0xFF0078D7,
                                                          ))
                                                  : inChordLhOnly
                                                  ? (genKeyHi
                                                        ? const Color(
                                                            0xFFCC5A00,
                                                          )
                                                        : const Color(
                                                            0xFFFF8A2B,
                                                          ))
                                                  : (isScaleCurrent
                                                        ? const Color(
                                                            0xFF0078D7,
                                                          )
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
                                                        ? const Color(
                                                            0xFF101822,
                                                          )
                                                        : (isActive
                                                              ? const Color(
                                                                  0xFFC37B00,
                                                                )
                                                              : const Color(
                                                                  0xFF101822,
                                                                )))),
                                        borderRadius: BorderRadius.circular(6),
                                        border: Border.all(
                                          color: genKeyHi
                                              ? const Color(0xFFF3BF2F)
                                              : chordGenPiano &&
                                                    _generatedChordJson !=
                                                        null &&
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
                                          if (_showKeyNames &&
                                              !(_tabIndex == 8 &&
                                                  !_noteDetectionDetailsVisible))
                                            Align(
                                              alignment: Alignment.bottomCenter,
                                              child: Padding(
                                                padding: const EdgeInsets.only(
                                                  bottom: 4,
                                                ),
                                                child: SizedBox(
                                                  width: blackW - 4,
                                                  child: FittedBox(
                                                    fit: BoxFit.scaleDown,
                                                    child: Text.rich(
                                                      TextSpan(
                                                        children:
                                                            _splitPitchClassLabelSpans(
                                                              _pianoKeyLabel(
                                                                midi,
                                                              ),
                                                              const TextStyle(
                                                                color: Colors
                                                                    .white,
                                                                fontWeight:
                                                                    FontWeight
                                                                        .w700,
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
                                          if (_tabIndex == 3 &&
                                              scaleRh.contains(midi))
                                            Builder(
                                              builder: (context) {
                                                final isTonic =
                                                    (midi % 12) ==
                                                    (_scaleTonicPc % 12);
                                                return Positioned(
                                                  top: blackH * 0.5,
                                                  left: (blackW - 18) / 2,
                                                  child: Container(
                                                    width: 18,
                                                    height: 18,
                                                    decoration: BoxDecoration(
                                                      color: isTonic
                                                          ? const Color(
                                                              0xFF32D74B,
                                                            )
                                                          : const Color(
                                                              0xFFF6B60B,
                                                            ),
                                                      shape: BoxShape.circle,
                                                      border: Border.all(
                                                        color: isTonic
                                                            ? const Color(
                                                                0xFF1E8C38,
                                                              )
                                                            : const Color(
                                                                0xFF8D6B00,
                                                              ),
                                                        width: 1.5,
                                                      ),
                                                    ),
                                                    alignment: Alignment.center,
                                                    child: FittedBox(
                                                      fit: BoxFit.scaleDown,
                                                      child: Text(
                                                        _pcLabel(midi % 12),
                                                        style: const TextStyle(
                                                          color: Color(
                                                            0xFF101010,
                                                          ),
                                                          fontWeight:
                                                              FontWeight.w700,
                                                          fontSize: 8,
                                                        ),
                                                      ),
                                                    ),
                                                  ),
                                                );
                                              },
                                            ),
                                          if (intervalNoteSet.contains(midi))
                                            _intervalPianoMarker(
                                              midi: midi,
                                              rootMidi: intervalRootMidi,
                                              size: 18,
                                              top: blackH * 0.5,
                                              left: (blackW - 18) / 2,
                                            ),
                                          if (chordGenPiano && rh != null)
                                            marker(
                                              size: 18,
                                              color: const Color(0xFF33C6FF),
                                              digit: rh,
                                              top: 10,
                                              left: (blackW - 18) / 2,
                                            ),
                                          if (chordGenPiano &&
                                              rh == null &&
                                              lh != null)
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
                            final isBlack = const <int>{
                              1,
                              3,
                              6,
                              8,
                              10,
                            }.contains(midi % 12);
                            final keyCenterX = isBlack
                                ? xForMidi(midi)
                                : xForMidi(midi) + whiteW / 2;
                            const indicatorSize = 22.0;
                            return Positioned(
                              left: keyCenterX - indicatorSize / 2,
                              top: forbiddenTop,
                              child: const SizedBox(
                                width: indicatorSize,
                                height: indicatorSize,
                                child: Center(
                                  child: Text(
                                    '⊘',
                                    style: TextStyle(
                                      color: Color(0xFFFF5A5A),
                                      fontSize: 18,
                                      fontWeight: FontWeight.w800,
                                      height: 1,
                                    ),
                                  ),
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
    final scaleMode = _tabIndex == 3;
    final intervalGenerationMode = _tabIndex == 7;
    final intervalGenerationNotes = intervalGenerationMode
        ? _intervalGenerationNotes()
        : const <int>[];
    final intervalGenerationRootPc = intervalGenerationNotes.isEmpty
        ? null
        : intervalGenerationNotes.first % 12;
    final intervalGenerationCurrentPc =
        intervalGenerationMode &&
            _intervalGenPlayingIdx != null &&
            _intervalGenPlayingIdx! >= 0 &&
            _intervalGenPlayingIdx! < intervalGenerationNotes.length
        ? intervalGenerationNotes[_intervalGenPlayingIdx!] % 12
        : null;
    final scaleTonicPc = _positiveMod12(
      (_generatedScaleJson?['tonic_pc'] as num?)?.toInt() ?? _scaleTonicPc,
    );
    final scaleCurrentNotes = <int>{..._scaleMidiHeldNotes, ?_scaleCurrentNote};
    final extraPcs = _instrumentExtrasForCurrentTab()
        .map((n) => n % 12)
        .toSet();
    final leftHanded = _guitarHandedness == 'left';
    const physicalTuning = <int>[40, 45, 50, 55, 59, 64]; // 6 -> 1
    final tuning = !leftHanded
        ? physicalTuning.reversed
              .toList() // 1 -> 6 (arriba -> abajo)
        : physicalTuning;
    const fretCount = 16; // cuerda al aire (0) + trastes 1..15
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
    final selectedFrets = !leftHanded ? rawFrets.reversed.toList() : rawFrets;
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
                        textAlign: leftHanded
                            ? TextAlign.left
                            : TextAlign.right,
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
                    final isPlaying =
                        active &&
                        (chordMode
                            ? (_heldChordNativeNotes.contains(note) ||
                                  _generationNoteHighlightMidi == note)
                            : ((_tabIndex == 3 &&
                                      ((_scaleCurrentNote != null &&
                                              _scaleCurrentNote == note) ||
                                          _scaleMidiHeldNotes.contains(
                                            note,
                                          ))) ||
                                  (intervalGenerationMode &&
                                      note % 12 ==
                                          intervalGenerationCurrentPc)));
                    final isIntervalRoot =
                        intervalGenerationMode &&
                        note % 12 == intervalGenerationRootPc;
                    final scaleMarker = scaleMode && active
                        ? scaleGuitarMarkerStyle(
                            note: note,
                            tonicPitchClass: scaleTonicPc,
                            currentNotes: scaleCurrentNotes,
                            selectedStartNote: _scaleGuitarStartNote,
                          )
                        : null;
                    final scaleMarkerColor = switch (scaleMarker) {
                      ScaleGuitarMarkerStyle.current => const Color(0xFF2FA8FF),
                      ScaleGuitarMarkerStyle.selectedStart => const Color(
                        0xFFFF9800,
                      ),
                      ScaleGuitarMarkerStyle.tonic => const Color(0xFFF6B60B),
                      ScaleGuitarMarkerStyle.degree => const Color(0xFFFFFFFF),
                      null => null,
                    };
                    final scaleMarkerBorder = switch (scaleMarker) {
                      ScaleGuitarMarkerStyle.current => const Color(0xFF0F5F99),
                      ScaleGuitarMarkerStyle.selectedStart => const Color(
                        0xFF8A4F10,
                      ),
                      ScaleGuitarMarkerStyle.tonic => const Color(0xFFB38B00),
                      ScaleGuitarMarkerStyle.degree => const Color(0xFF2F3137),
                      null => null,
                    };
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
                            color:
                                scaleMarkerColor ??
                                (active
                                    ? (isExtra
                                          ? const Color(0xFFE04A4A)
                                          : (isPlaying
                                                ? const Color(0xFF2FA8FF)
                                                : (isIntervalRoot
                                                      ? const Color(0xFF22C55E)
                                                      : const Color(
                                                          0xFFF3BF2F,
                                                        ))))
                                    : (showDot
                                          ? const Color(0xFFE5E7EB)
                                          : Colors.transparent)),
                            border: showDot
                                ? Border.all(
                                    color:
                                        scaleMarkerBorder ??
                                        (active
                                            ? (isExtra
                                                  ? const Color(0xFFB33434)
                                                  : (isPlaying
                                                        ? const Color(
                                                            0xFF0F5F99,
                                                          )
                                                        : (isIntervalRoot
                                                              ? const Color(
                                                                  0xFF1E8C38,
                                                                )
                                                              : const Color(
                                                                  0xFFD29B20,
                                                                ))))
                                            : const Color(0xFFAAB1BC)),
                                    width: isPlaying ? 2.5 : 1.0,
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
                                    ? Padding(
                                        padding: const EdgeInsets.all(2),
                                        child: FittedBox(
                                          fit: BoxFit.scaleDown,
                                          child: Text(
                                            active
                                                ? _pcLabel(note % 12)
                                                : (detectionMode ? '•' : ''),
                                            maxLines: 1,
                                            softWrap: false,
                                            style: TextStyle(
                                              color: active
                                                  ? (isExtra
                                                        ? const Color(
                                                            0xFFFCECEC,
                                                          )
                                                        : const Color(
                                                            0xFF0F0F0F,
                                                          ))
                                                  : const Color(0xFF7D8797),
                                              fontSize: 10,
                                              fontWeight: FontWeight.w700,
                                            ),
                                          ),
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

  void _updateState(VoidCallback update) => setState(update);

  // General MIDI: 0 = Acoustic Grand Piano, 25 = Steel String Guitar. Sin un
  // Program Change el dispositivo receptor se queda con el timbre por
  // defecto (normalmente piano) aunque la app esté mostrando la guitarra.
  static const int _kMidiOutProgramPiano = 0;
  static const int _kMidiOutProgramGuitar = 25;

  /// Send a MIDI note_on (0x90) message to all connected MIDI devices.
  /// Envía primero un Program Change si el instrumento visible ha cambiado
  /// (piano/guitarra), para que el dispositivo receptor use el timbre
  /// correcto en vez de quedarse con el que tuviera por defecto.
  void _sendMidiNoteOn(int midiNote, int velocity) {
    _midiOutputController.noteOn(
      note: midiNote,
      velocity: velocity,
      program: _instrumentView == 'guitar'
          ? _kMidiOutProgramGuitar
          : _kMidiOutProgramPiano,
    );
  }

  /// Send a MIDI note_off (0x80) message to all connected MIDI devices.
  void _sendMidiNoteOff(int midiNote) {
    _midiOutputController.noteOff(midiNote);
  }

  /// Play a note via audio or MIDI output based on _soundOutput setting.
  Future<void> playNote(
    int midiNote, {
    int velocity = 80,
    String instrument = 'piano',
    double durationSeconds = 0.6,
  }) async {
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
        'whole tone (wt)': 'whole_tone',
        'minor blues': 'minor_blues',
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

  // Interval detection methods
  List<int> _intervalPracticeQuestionNotes() => <int>[
    _intervalPracticeRoot,
    _intervalPracticeRoot +
        _intervalPracticeDirection * _intervalPracticeSemitones,
  ];

  List<int> _intervalPracticeDisplayNotes() {
    if (!_intervalPracticeStarted) return const <int>[];
    final notes = _intervalPracticeQuestionNotes();
    if (_intervalPracticeAnswerCorrect == null) return <int>[notes.first];
    if (_intervalPracticeAnswerCorrect!) return notes;
    return <int>[notes.first, _intervalPracticeAnswerNote!, notes.last];
  }

  void _cancelIntervalPracticePlayback() {
    _intervalPracticePlaybackGeneration += 1;
    _intervalPracticePlaybackTimer?.cancel();
    _intervalPracticePlaybackTimer = null;
    _intervalPracticeReviewTimer?.cancel();
    _intervalPracticeReviewTimer = null;
    _intervalGenInputHighlightTimer?.cancel();
    _intervalGenInputHighlightTimer = null;
    _intervalPracticePlayingNotes.clear();
    _intervalPracticePlayingNote = null;
  }

  void _playIntervalPracticeNotes(List<int> notes, {bool hideSecond = false}) {
    _cancelIntervalPracticePlayback();
    final generation = _intervalPracticePlaybackGeneration;
    if (_intervalPracticeHarmonic) {
      setState(() {
        _intervalPracticePlayingNotes
          ..clear()
          ..addAll(hideSecond ? <int>[notes.first] : notes);
        _intervalPracticePlayingNote = hideSecond ? notes.first : null;
      });
      for (final note in notes) {
        unawaited(playNote(note, instrument: 'piano'));
      }
      _intervalPracticePlaybackTimer = Timer(
        const Duration(milliseconds: 600),
        () {
          if (!mounted || generation != _intervalPracticePlaybackGeneration) {
            return;
          }
          setState(() {
            _intervalPracticePlayingNotes.clear();
            _intervalPracticePlayingNote = null;
          });
        },
      );
      return;
    }

    void playAt(int index) {
      if (!mounted || generation != _intervalPracticePlaybackGeneration) return;
      if (index >= notes.length) {
        setState(() {
          _intervalPracticePlayingNotes.clear();
          _intervalPracticePlayingNote = null;
        });
        return;
      }
      setState(() {
        _intervalPracticePlayingNotes
          ..clear()
          ..addAll(
            hideSecond && index > 0 ? const <int>[] : <int>[notes[index]],
          );
        _intervalPracticePlayingNote = hideSecond && index > 0
            ? null
            : notes[index];
      });
      unawaited(playNote(notes[index], instrument: 'piano'));
      _intervalPracticePlaybackTimer = Timer(
        const Duration(milliseconds: 600),
        () => playAt(index + 1),
      );
    }

    playAt(0);
  }

  void _playIntervalPracticeQuestion() {
    if (!_intervalPracticeStarted) return;
    _playIntervalPracticeNotes(
      _intervalPracticeQuestionNotes(),
      hideSecond: _intervalPracticeAnswerCorrect == null,
    );
  }

  void _nextIntervalPracticeQuestion() {
    if (!_intervalPracticeRunning ||
        _intervalPracticeTotal >= _intervalPracticeRepetitions) {
      return;
    }
    final choice = _intervalPracticeDeck.draw(
      allowedSemitones: _intervalPracticeAllowedSemitones,
      randomTonic: _intervalPracticeRandomTonic,
      ascendingOnly: _intervalPracticeAscendingOnly,
    );
    if (choice == null) return;
    _cancelIntervalPracticePlayback();
    setState(() {
      _intervalPracticeStarted = true;
      _intervalPracticeRoot = choice.root;
      _intervalPracticeSemitones = choice.semitones;
      _intervalPracticeDirection = choice.direction;
      _intervalPracticeAnswerNote = null;
      _intervalPracticeAnswerCorrect = null;
      _intervalPracticeReviewIndex = null;
    });
    _playIntervalPracticeQuestion();
  }

  void _toggleIntervalPractice() {
    if (_intervalPracticeRunning) {
      _stopIntervalPractice();
      return;
    }
    _intervalPracticeDeck.reset();
    setState(() {
      _intervalPracticeRunning = true;
      _intervalPracticeStarted = true;
      _intervalPracticeCorrect = 0;
      _intervalPracticeTotal = 0;
      _intervalPracticeHistory.clear();
      _intervalPracticeReviewIndex = null;
      _intervalPracticeAnswerNote = null;
      _intervalPracticeAnswerCorrect = null;
    });
    _nextIntervalPracticeQuestion();
  }

  void _stopIntervalPractice() {
    _cancelIntervalPracticePlayback();
    setState(() {
      _intervalPracticeRunning = false;
      if (_intervalPracticeHistory.isNotEmpty) {
        _intervalPracticeReviewIndex = _intervalPracticeHistory.length - 1;
        _loadIntervalPracticeHistory(_intervalPracticeReviewIndex!);
      }
    });
  }

  void _answerIntervalPractice({int? note, int? semitones}) {
    if (!_intervalPracticeRunning || _intervalPracticeAnswerCorrect != null) {
      return;
    }
    final question = _intervalPracticeQuestionNotes();
    final guessedNote =
        note ??
        (_intervalPracticeRoot + _intervalPracticeDirection * (semitones ?? 0));
    final guessedSemitones = semitones ?? (guessedNote - question.first).abs();
    final correct = note != null
        ? guessedNote == question.last
        : guessedSemitones == _intervalPracticeSemitones;
    setState(() {
      _intervalPracticeAnswerNote = guessedNote;
      _intervalPracticeAnswerCorrect = correct;
      _intervalPracticeTotal += 1;
      if (correct) _intervalPracticeCorrect += 1;
      _intervalPracticeHistory.add(<String, Object>{
        'root': _intervalPracticeRoot,
        'semitones': _intervalPracticeSemitones,
        'direction': _intervalPracticeDirection,
        'answerNote': guessedNote,
        'correct': correct,
        'scoreCorrect': _intervalPracticeCorrect,
        'scoreTotal': _intervalPracticeTotal,
      });
      if (_intervalPracticeTotal >= _intervalPracticeRepetitions) {
        _intervalPracticeRunning = false;
        _intervalPracticeReviewIndex = _intervalPracticeHistory.length - 1;
      }
    });
    _playIntervalPracticeNotes(<int>[question.first, guessedNote]);
  }

  void _loadIntervalPracticeHistory(int index) {
    final entry = _intervalPracticeHistory[index];
    _intervalPracticeRoot = entry['root']! as int;
    _intervalPracticeSemitones = entry['semitones']! as int;
    _intervalPracticeDirection = entry['direction']! as int;
    _intervalPracticeAnswerNote = entry['answerNote']! as int;
    _intervalPracticeAnswerCorrect = entry['correct']! as bool;
    _intervalPracticeCorrect = entry['scoreCorrect']! as int;
    _intervalPracticeTotal = entry['scoreTotal']! as int;
  }

  void _reviewIntervalPractice(int delta) {
    if (_intervalPracticeHistory.isEmpty) return;
    final current =
        _intervalPracticeReviewIndex ?? _intervalPracticeHistory.length - 1;
    final next = (current + delta).clamp(
      0,
      _intervalPracticeHistory.length - 1,
    );
    setState(() {
      _intervalPracticeReviewIndex = next;
      _loadIntervalPracticeHistory(next);
    });
  }

  void _replayIntervalPracticeResult() {
    if (_intervalPracticeAnswerCorrect == null) {
      _playIntervalPracticeQuestion();
      return;
    }
    final question = _intervalPracticeQuestionNotes();
    _playIntervalPracticeNotes(question);
    if (!_intervalPracticeAnswerCorrect!) {
      final generation = _intervalPracticePlaybackGeneration;
      _intervalPracticeReviewTimer = Timer(
        const Duration(milliseconds: 1150),
        () {
          if (!mounted || generation != _intervalPracticePlaybackGeneration) {
            return;
          }
          _playIntervalPracticeNotes(<int>[
            question.first,
            _intervalPracticeAnswerNote!,
          ]);
        },
      );
    }
  }

  List<int> _intervalGenerationNotes() =>
      generateIntervalNotes(_intervalGenRootPc, _intervalGenSemitones);

  void _selectGeneratedInterval(
    IntervalGridCategory category,
    IntervalGridCell cell,
  ) {
    _intervalGenPlaybackTimer?.cancel();
    setState(() {
      _intervalGenCategoryKey = category.key;
      _intervalGenSemitones = cell.semitones;
      _intervalGenLabel = cell.label;
      _intervalGenPlayingIdx = null;
    });
    _playGeneratedInterval();
  }

  void _playGeneratedInterval({bool reversed = false}) {
    _intervalGenPlaybackTimer?.cancel();
    final notes = _intervalGenerationNotes();
    if (_intervalGenHarmonic) {
      setState(() => _intervalGenPlayingIdx = null);
      for (final note in notes) {
        unawaited(playNote(note, instrument: _instrumentView));
      }
      return;
    }
    final ordered = reversed ? notes.reversed.toList() : notes;
    void playAt(int index) {
      if (!mounted || index >= ordered.length) {
        if (mounted) setState(() => _intervalGenPlayingIdx = null);
        return;
      }
      final originalIndex = notes.indexOf(ordered[index]);
      setState(() => _intervalGenPlayingIdx = originalIndex);
      unawaited(playNote(ordered[index], instrument: _instrumentView));
      _intervalGenPlaybackTimer = Timer(
        const Duration(milliseconds: 500),
        () => playAt(index + 1),
      );
    }

    playAt(0);
  }

  void _playGeneratedIntervalFromButton({required bool reversed}) {
    if (_intervalGenHarmonic && reversed) return;
    setState(() => _intervalGenLastPlayReversed = reversed);
    _playGeneratedInterval(reversed: reversed);
  }

  void _toggleIntervalGenerationPlaybackMode() {
    _intervalGenPlaybackTimer?.cancel();
    setState(() {
      _intervalGenHarmonic = !_intervalGenHarmonic;
      _intervalGenLastPlayReversed = _intervalGenHarmonic ? false : null;
      _intervalGenPlayingIdx = null;
    });
    _playGeneratedInterval();
  }

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

  String _getIntervalAltNames() {
    final semitones = _getIntervalSemitones();
    if (semitones == null) return "-";
    return getIntervalAltNames(semitones, _language);
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
      _playMelodySequence(notes, melody, 0);
    } else {
      // Normal mode: play the two interval notes (reversible)
      final ordered = reversed
          ? List<int>.from(_intervalNotes.reversed).cast<int?>()
          : List<int>.from(_intervalNotes).cast<int?>();
      const dummyMelody = IntervalMelody(
        nameEs: '',
        nameEn: '',
        beatsPerBar: 4,
        offsets: [0, 0],
        durations: ['q', 'q'],
      );
      _playMelodySequence(
        ordered,
        dummyMelody,
        0,
        displayIndices: reversed ? const <int>[1, 0] : null,
      );
    }
  }

  void _playMelodySequence(
    List<int?> notes,
    IntervalMelody melody,
    int index, {
    List<int>? displayIndices,
  }) {
    if (index >= notes.length) {
      setState(() {
        _intervalPlayingIdx = null;
      });
      return;
    }

    final note = notes[index];
    if (note != null) {
      unawaited(playNote(note, instrument: _instrumentView));
      setState(() {
        _intervalPlayingIdx = displayIndices?[index] ?? index;
      });
    }

    final durations = melody.durations;
    final durationCode = index < durations.length ? durations[index] : "q";
    final durationMs = durationToMs(durationCode);

    _intervalMelodyPlaybackTimer = Timer(
      Duration(milliseconds: durationMs),
      () {
        _playMelodySequence(
          notes,
          melody,
          index + 1,
          displayIndices: displayIndices,
        );
      },
    );
  }
}
