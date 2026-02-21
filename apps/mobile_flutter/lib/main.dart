import 'dart:convert';
import 'dart:async';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_audio_capture/flutter_audio_capture.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_midi_command/flutter_midi_command.dart';

void main() {
  runApp(const MidiChordsMobileApp());
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
      home: const HomeScreen(),
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

  static const String _defaultApiBase = String.fromEnvironment(
    'MIDICHORDS_API_BASE',
    defaultValue: 'http://127.0.0.1:8000',
  );

  final TextEditingController _apiBaseController = TextEditingController(
    text: _defaultApiBase,
  );
  final TextEditingController _detectionOutputController =
      TextEditingController(text: 'Sin resultados');
  final TextEditingController _chordOutputController = TextEditingController(
    text: 'Sin resultados',
  );
  final TextEditingController _scaleOutputController = TextEditingController(
    text: 'Sin resultados',
  );

  int _tabIndex = 0;
  bool _loadingMeta = false;
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
  bool _generationPlayPressed = false;
  final Map<int, AudioPlayer> _heldChordPlayers = <int, AudioPlayer>{};
  final Map<int, AudioPlayer> _heldInputPlayers = <int, AudioPlayer>{};
  final Map<int, AudioPlayer> _heldMidiInputPlayers = <int, AudioPlayer>{};
  final Map<String, String> _toneFileCache = <String, String>{};
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
  final Set<int> _detectionSelectedNotes = <int>{};
  int _metroBpm = 120;
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
  String _tunerTuning = 'standard';
  int? _tunerCurrentStringIdx;
  double _tunerInputGain = 1.0;
  int _tunerRangeMin = 20;
  int _tunerRangeMax = 500;
  double _tunerSmoothedFreq = 0.0;
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
                TextField(
                  controller: _apiBaseController,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(
                    labelText: 'Backend API base URL',
                  ),
                ),
                const SizedBox(height: 10),
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
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerLeft,
                  child: FilledButton.icon(
                    style: FilledButton.styleFrom(
                      backgroundColor: _accent,
                      foregroundColor: const Color(0xFF1A222D),
                    ),
                    onPressed: _loadingMeta ? null : _loadMeta,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Meta'),
                  ),
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
    _apiBaseController.dispose();
    _detectionOutputController.dispose();
    _chordOutputController.dispose();
    _scaleOutputController.dispose();
    super.dispose();
  }

  Uri _uri(String path) => Uri.parse('${_apiBaseController.text.trim()}$path');

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> payload,
  ) async {
    final resp = await http.post(
      _uri(path),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    if (resp.statusCode >= 400) {
      throw Exception('HTTP ${resp.statusCode}: ${resp.body}');
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  Future<void> _loadMeta() async {
    setState(() => _loadingMeta = true);
    try {
      final resp = await http.get(_uri('/api/meta?language=$_language'));
      if (resp.statusCode >= 400) {
        throw Exception('HTTP ${resp.statusCode}: ${resp.body}');
      }
      final json = jsonDecode(resp.body) as Map<String, dynamic>;
      final chordPatterns =
          (json['chord_patterns'] as List<dynamic>? ?? <dynamic>[])
              .whereType<Map<String, dynamic>>()
              .toList();
      final scalePatterns =
          (json['scale_patterns'] as List<dynamic>? ?? <dynamic>[])
              .whereType<Map<String, dynamic>>()
              .toList();
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
    } finally {
      if (mounted) {
        setState(() => _loadingMeta = false);
      }
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
      final rh = _extractMidiList(_generatedChordJson!, <String>[
        'notes_midi',
      ]);
      if (_instrumentView == 'guitar') {
        return rh.toSet();
      }
      final lh = rh.map((n) => n - 12).where((n) => n >= 0);
      return <int>{...rh, ...lh};
    }
    if (_tabIndex == 2 && _generatedScaleJson != null) {
      final rh = _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
      if (_instrumentView == 'guitar') {
        return rh.toSet();
      }
      final lh = rh.map((n) => n - 12).where((n) => n >= 0);
      return <int>{...rh, ...lh};
    }
    return <int>{};
  }

  Set<int> _generationPlayingNotesForStaff() {
    if (_tabIndex != 1) return <int>{};
    final rh = _heldChordPlayers.keys.toSet();
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
      return _extractMidiList(_generatedChordJson!, <String>[
        'notes_midi',
      ]).toSet();
    }
    if (_tabIndex == 2 && _generatedScaleJson != null) {
      final rh = _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
      final notes = <int>{...rh};
      if (_instrumentView == 'piano') {
        notes.addAll(rh.map((n) => n - 12).where((n) => n >= 0));
      }
      if (_scaleCurrentNote != null && _instrumentView == 'piano') {
        notes.add(_scaleCurrentNote!);
      }
      return notes;
    }
    return <int>{};
  }

  List<int> _scaleRhNotes() {
    if (_generatedScaleJson == null) return <int>[];
    return _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
  }

  List<int> _scaleLhNotes(List<int> rh) =>
      rh.map((n) => n - 12).where((n) => n >= 0).toList();

  int? _scaleStaffNoteForPitch(int note) {
    if (_generatedScaleJson == null) return null;
    final target = note;
    final rh = _scaleRhNotes();
    final lh = _instrumentView == 'piano' ? _scaleLhNotes(rh) : <int>[];
    final candidates = <int>[...rh, ...lh];
    if (candidates.contains(target)) return target;
    final pc = ((target % 12) + 12) % 12;
    final samePc = candidates.where((n) => ((n % 12) + 12) % 12 == pc).toList();
    if (samePc.isEmpty) return null;
    samePc.sort((a, b) => (a - target).abs().compareTo((b - target).abs()));
    return samePc.first;
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
    final attack = instrument == 'guitar' ? 0.006 : 0.009;
    final decayBase = instrument == 'guitar' ? 0.935 : 0.785;
    final maxAmp = instrument == 'guitar' ? 0.58 : 0.52;
    for (int i = 0; i < totalSamples; i += 1) {
      final t = i / sampleRate;
      final decayFactor = math
          .pow(decayBase, t * (instrument == 'guitar' ? 7.2 : 5.6))
          .toDouble();
      final env = t < attack ? (t / attack) : decayFactor;
      final fundamental = math.sin(pi2 * freq * t);
      final harmonic2 =
          math.sin(pi2 * freq * 2.0 * t) *
          (instrument == 'guitar' ? 0.20 : 0.14);
      final harmonic3 =
          math.sin(pi2 * freq * 3.0 * t) *
          (instrument == 'guitar' ? 0.10 : 0.06);
      final harmonic4 =
          math.sin(pi2 * freq * 4.0 * t) *
          (instrument == 'guitar' ? 0.04 : 0.025);
      final sample =
          (fundamental + harmonic2 + harmonic3 + harmonic4) * env * maxAmp;
      final pcm = (sample * 32767.0).round().clamp(-32767, 32767);
      byteData.setInt16(44 + i * 2, pcm, Endian.little);
    }
    return byteData.buffer.asUint8List();
  }

  Future<AudioPlayer?> _playTone({
    required int midi,
    required String instrument,
    double durationSeconds = 0.6,
    bool lowVolume = false,
  }) async {
    if (!_audioPlaybackAvailable) {
      SystemSound.play(SystemSoundType.click);
      return null;
    }
    final player = AudioPlayer();
    try {
      await player.setPlayerMode(PlayerMode.mediaPlayer);
      await player.setReleaseMode(ReleaseMode.stop);
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
        await player.play(
          DeviceFileSource(filePath),
          volume: lowVolume ? 0.68 : 1.0,
        );
      } else {
        await player.play(
          BytesSource(wavBytes, mimeType: 'audio/wav'),
          volume: lowVolume ? 0.68 : 1.0,
        );
      }
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

  Future<void> _safeStopDispose(AudioPlayer player) async {
    // On iOS simulator, stop/dispose can throw sporadic platform errors even
    // for already-finished players. Avoid hard lifecycle calls here.
    try {
      await player.setVolume(0.0);
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
      final shiftPressed = _isShiftPressed();
      setState(() {
        if (shiftPressed) {
          if (_detectionSelectedNotes.contains(midi)) {
            _detectionSelectedNotes.remove(midi);
          } else {
            _detectionSelectedNotes.add(midi);
          }
        } else {
          _detectionSelectedNotes.clear();
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
      final scaleNotes = _extractMidiList(_generatedScaleJson!, <String>[
        'notes_midi',
      ]);
      final allowed = scaleNotes.map((n) => n % 12).toSet().contains(midi % 12);
      if (!allowed) {
        _showForbiddenOnPiano(midi);
        return;
      }
      _scaleCurrentNote = _scaleStaffNoteForPitch(midi) ?? midi;
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
    for (final midi in notes) {
      final player = await _playTone(
        midi: midi,
        instrument: instrument,
        durationSeconds: instrument == 'guitar' ? 1.45 : 1.35,
      );
      if (player != null) {
        _heldChordPlayers[midi] = player;
      }
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
      final json = await _postJson('/api/detect', <String, dynamic>{
        'notes': notes,
        'language': _language,
        'accidental': _accidental,
      });
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
      final json = await _postJson('/api/generate/chord', <String, dynamic>{
        'root_pc': _chordRootPc,
        'suffix': _chordSuffix,
        'inversion': _chordInversion,
        'language': _language,
        'accidental': _accidental,
      });
      _generatedChordJson = json;
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
      final json = await _postJson('/api/generate/scale', <String, dynamic>{
        'tonic_pc': _scaleTonicPc,
        'pattern_name': _scalePatternName,
        'language': _language,
        'accidental': _accidental,
      });
      _generatedScaleJson = json;
      final scaleMidi = _extractMidiList(json, <String>['notes_midi']);
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

  void _stopScaleLoop() {
    _scaleLoopTimer?.cancel();
    _scaleLoopTimer = null;
    _scaleLoopRunning = false;
    _scaleCurrentNote = null;
    if (mounted) {
      setState(() {});
    }
  }

  void _stepScaleLoop() {
    if (!_scaleLoopRunning) {
      return;
    }
    final notes = _generatedScaleJson == null
        ? <int>[]
        : _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
    if (notes.isEmpty) {
      _stopScaleLoop();
      return;
    }
    final idx = _scaleLoopIndex.clamp(0, notes.length - 1);
    final note = notes[idx];
    _scaleCurrentNote = note;
    if (_scaleMetronomeOnly) {
      SystemSound.play(SystemSoundType.click);
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
    final notes = _generatedScaleJson == null
        ? <int>[]
        : _extractMidiList(_generatedScaleJson!, <String>['notes_midi']);
    if (notes.isEmpty) return;
    _scaleLoopRunning = true;
    _scaleLoopIndex = 0;
    _scaleLoopDirection = 1;
    _stepScaleLoop();
  }

  String _pcLabel(int pc) {
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

  void _metronomeTick() {
    if (!_metroRunning) {
      return;
    }
    final clicks = _metroClicksPerBeat.clamp(1, 6);
    final isPrimary = _metroSubdivisionIndex % clicks == 0;
    if (isPrimary) {
      if (_metroTickCount > 0) {
        _metroDirection *= -1;
      }
      _metroMotionStartAt = DateTime.now();
      final nextBeat = (_metroCurrentBeat + 1) % _metroBeatsPerBar;
      _metroCurrentBeat = nextBeat;
      if (_metroBarAccent && nextBeat == 0) {
        SystemSound.play(SystemSoundType.click);
        HapticFeedback.mediumImpact();
      } else {
        SystemSound.play(SystemSoundType.click);
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
      case 'half_step':
        return <int>[39, 44, 49, 54, 58, 63];
      case 'standard':
      default:
        return <int>[40, 45, 50, 55, 59, 64];
    }
  }

  List<String> _tunerOpenLabelsForCurrentTuning() {
    return _tunerOpenNotesForCurrentTuning()
        .map((n) => _pcLabel(((n % 12) + 12) % 12))
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
    final detected = _estimatePitch(scaled, _tunerSampleRate);
    if (detected == null) {
      return;
    }
    if (detected < _tunerRangeMin || detected > _tunerRangeMax) {
      return;
    }
    _tunerSmoothedFreq = _tunerSmoothedFreq <= 0.0
        ? detected
        : (_tunerSmoothedFreq * 0.72 + detected * 0.28);
    final now = DateTime.now();
    if (now.difference(_lastTunerUiUpdate).inMilliseconds < 80) {
      return;
    }
    _lastTunerUiUpdate = now;
    final midi = 69 + 12 * (math.log(_tunerSmoothedFreq / 440.0) / math.ln2);
    final rounded = midi.round();
    final tuningNotes = _tunerOpenNotesForCurrentTuning();
    int bestIdx = 0;
    double bestAbsCents = double.infinity;
    double bestCents = 0.0;
    for (int i = 0; i < tuningNotes.length; i += 1) {
      final targetFreq = 440.0 * math.pow(2.0, (tuningNotes[i] - 69) / 12.0);
      final centsToString =
          1200.0 * (math.log(_tunerSmoothedFreq / targetFreq) / math.ln2);
      final absVal = centsToString.abs();
      if (absVal < bestAbsCents) {
        bestAbsCents = absVal;
        bestIdx = i;
        bestCents = centsToString;
      }
    }
    final note = _pcLabel(((rounded % 12) + 12) % 12);
    if (!mounted || !_tunerRunning) {
      return;
    }
    setState(() {
      _tunerNote = note;
      _tunerCurrentStringIdx = bestIdx;
      _tunerCents = bestCents.round().clamp(-50, 50);
      _tunerFreq = _tunerSmoothedFreq;
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
      _tunerError = '';
      _tunerSmoothedFreq = 0.0;
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
    final pages = <Widget>[
      _buildDetectionPage(),
      _buildChordGenerationPage(),
      _buildScaleGenerationPage(),
      _buildMetronomePage(),
      _buildTunerPage(),
    ];

    return Scaffold(
      appBar: AppBar(
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
                    key: ValueKey<int>(_tabIndex),
                    initialValue: _tabIndex,
                    dropdownColor: _surfaceDark,
                    style: const TextStyle(color: _text),
                    decoration: const InputDecoration(
                      labelText: 'Modo',
                      isDense: true,
                    ),
                    items: List<DropdownMenuItem<int>>.generate(
                      5,
                      (int i) => DropdownMenuItem<int>(
                        value: i,
                        child: Text(_modeLabel(i)),
                      ),
                    ),
                    onChanged: (value) {
                      if (value == null) return;
                      setState(() => _tabIndex = value);
                      if (value != 2) {
                        _stopScaleLoop();
                      }
                      if (value != 3) {
                        _stopMetronome();
                      }
                      _stopHeldChord();
                      _stopHeldInputs();
                      _stopHeldMidiInputs();
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
        child: Column(children: <Widget>[Expanded(child: pages[_tabIndex])]),
      ),
    );
  }

  Widget _buildModeScaffold({
    required Widget controls,
    bool showInstrument = true,
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
              if (showInstrument) ...<Widget>[
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
                    currentBeat: _metroCurrentBeat,
                    running: _metroRunning,
                    direction: _metroDirection,
                    motionProgress: _metronomeMotionProgress(),
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
                    generationRhNotes: (_tabIndex == 1 && _generatedChordJson != null)
                        ? _extractMidiList(_generatedChordJson!, <String>['notes_midi'])
                        : const <int>[],
                    generationLhNotes: (_tabIndex == 1 && _instrumentView == 'piano' && _generatedChordJson != null)
                        ? _extractMidiList(_generatedChordJson!, <String>['notes_midi'])
                            .map((n) => n - 12)
                            .where((n) => n >= 0)
                            .toList()
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
    return _panel(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Expanded(
            child: _instrumentView == 'piano'
                ? _buildPianoStrip(activeMidi)
                : _buildGuitarStrip(activeMidi),
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
    final midiRange = List<int>.generate(31, (i) => 48 + i); // C3..F#5
    final whiteMidi = midiRange
        .where((m) => !const <int>{1, 3, 6, 8, 10}.contains(m % 12))
        .toList();
    const whiteW = 50.0;
    const blackW = 30.0;
    const whiteH = 130.0;
    const blackH = 84.0;
    final active = activeMidi.toSet();
    final scaleRh = _tabIndex == 2 ? _scaleRhNotes().toSet() : <int>{};
    final scaleLh = (_tabIndex == 2 && _instrumentView == 'piano')
        ? _scaleLhNotes(_scaleRhNotes()).toSet()
        : <int>{};

    double xForMidi(int midi) {
      final idx = whiteMidi.indexWhere((m) => m >= midi);
      final wIdx = idx < 0 ? whiteMidi.length - 1 : idx;
      return wIdx * whiteW;
    }

    return SizedBox(
      height: 140,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: SizedBox(
          width: whiteMidi.length * whiteW,
          child: Stack(
            children: <Widget>[
              Row(
                children: whiteMidi.map((midi) {
                  final isActive = active.contains(midi);
                  final isScaleCurrent =
                      _tabIndex == 2 &&
                      _scaleCurrentNote != null &&
                      _scaleCurrentNote == midi;
                  final currentIsLeft =
                      isScaleCurrent &&
                      _instrumentView == 'piano' &&
                      scaleLh.contains(midi) &&
                      !scaleRh.contains(midi);
                  return Listener(
                    onPointerDown: (event) => unawaited(
                      _beginInputDrag(midi, event.pointer, event.position),
                    ),
                    onPointerMove: (event) => unawaited(
                      _updateInputDrag(midi, event.pointer, event.position),
                    ),
                    onPointerUp: (event) => _endInputDrag(event.pointer),
                    onPointerCancel: (event) => _endInputDrag(event.pointer),
                    child: Container(
                      width: whiteW,
                      height: whiteH,
                      margin: EdgeInsets.zero,
                      decoration: BoxDecoration(
                        color: isScaleCurrent
                            ? (currentIsLeft
                                  ? const Color(0xFFFF8A2B)
                                  : const Color(0xFF4DA3EA))
                            : (isActive
                                  ? const Color(0xFFF3C64F)
                                  : const Color(0xFFF5F4EF)),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: const Color(0xFFAEB8C5)),
                      ),
                      alignment: Alignment.bottomCenter,
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
                  );
                }).toList(),
              ),
              ...midiRange
                  .where((m) => const <int>{1, 3, 6, 8, 10}.contains(m % 12))
                  .map((midi) {
                    final isActive = active.contains(midi);
                    final isScaleCurrent =
                        _tabIndex == 2 &&
                        _scaleCurrentNote != null &&
                        _scaleCurrentNote == midi;
                    final currentIsLeft =
                        isScaleCurrent &&
                        _instrumentView == 'piano' &&
                        scaleLh.contains(midi) &&
                        !scaleRh.contains(midi);
                    return Positioned(
                      left: xForMidi(midi) - (blackW / 2),
                      top: 0,
                      child: Listener(
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
                          width: blackW,
                          height: blackH,
                          decoration: BoxDecoration(
                            color: isScaleCurrent
                                ? (currentIsLeft
                                      ? const Color(0xFFB35F00)
                                      : const Color(0xFF0078D7))
                                : (isActive
                                      ? const Color(0xFFC37B00)
                                      : const Color(0xFF101822)),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: const Color(0xFF6F7F96)),
                          ),
                          alignment: Alignment.bottomCenter,
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Text(
                            _pcLabel(midi % 12),
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w700,
                              fontSize: 9,
                            ),
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
      ),
    );
  }

  Widget _buildGuitarStrip(Set<int> activeMidi) {
    final activePcs = activeMidi.map((n) => n % 12).toSet();
    final rightTuning = <int>[40, 45, 50, 55, 59, 64];
    final tuning = _guitarHandedness == 'left'
        ? rightTuning.reversed.toList()
        : rightTuning;
    const fretCount = 14;
    const fretW = 78.0;
    const stringGap = 25.0;
    final detectionMode = _tabIndex == 0;
    final width = (fretCount + 1) * fretW;
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
                  left: 40,
                  top: 6,
                  right: 0,
                  child: Row(
                    children: List<Widget>.generate(
                      fretCount + 1,
                      (i) => SizedBox(
                        width: fretW,
                        child: Text(
                          '$i',
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 10,
                            color: Color(0xFF1A222D),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
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
                    left: 40,
                    top: y,
                    child: Container(
                      width: width,
                      height: 2,
                      color: const Color(0xFF8FA0B8),
                    ),
                  );
                }),
                ...List<Widget>.generate(fretCount + 1, (f) {
                  return Positioned(
                    left: 40 + (f * fretW),
                    top: 28,
                    child: Container(
                      width: f == 0 ? 3 : 2,
                      height: 6 * stringGap,
                      color: const Color(0xFFC0AE94),
                    ),
                  );
                }),
                ...List<int>.generate(6, (s) => s).expand((s) {
                  return List<Widget>.generate(fretCount + 1, (f) {
                    final note = tuning[s] + f;
                    final y = 32.0 + (s * stringGap) - 10;
                    final x = 40 + (f * fretW) - 11;
                    final active = activePcs.contains(note % 12);
                    final showDot = detectionMode || active;
                    return Positioned(
                      left: x,
                      top: y,
                      child: Listener(
                        onPointerDown: (event) => unawaited(
                          _beginInputDrag(note, event.pointer, event.position),
                        ),
                        onPointerMove: (event) => unawaited(
                          _updateInputDrag(note, event.pointer, event.position),
                        ),
                        onPointerUp: (event) => _endInputDrag(event.pointer),
                        onPointerCancel: (event) =>
                            _endInputDrag(event.pointer),
                        child: Container(
                          width: 22,
                          height: 22,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: active
                                ? const Color(0xFFF3BF2F)
                                : (showDot
                                      ? const Color(0xFFE5E7EB)
                                      : Colors.transparent),
                            border: showDot
                                ? Border.all(
                                    color: active
                                        ? const Color(0xFFD29B20)
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
                                        active ? _pcLabel(note % 12) : '•',
                                        style: TextStyle(
                                          color: active
                                              ? const Color(0xFF1A222D)
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
              OutlinedButton.icon(
                onPressed: null,
                icon: const Icon(Icons.restore),
                label: const Text(''),
              ),
              _holdPlayButton(
                enabled: hasNotes,
                active: _detectionPlayPressed,
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
          const SizedBox(height: 8),
          Row(
            children: <Widget>[
              const SizedBox(
                width: 92,
                child: Text(
                  'Inversión',
                  style: TextStyle(fontWeight: FontWeight.w600, color: _muted),
                ),
              ),
              Expanded(
                child: DropdownButtonFormField<int>(
                  key: ValueKey<String>(
                    'inv_$_chordInversion/$_chordMaxInversion',
                  ),
                  initialValue: _chordInversion.clamp(0, _chordMaxInversion),
                  dropdownColor: _surfaceDark,
                  style: const TextStyle(color: _text),
                  decoration: const InputDecoration(isDense: true),
                  items: List<DropdownMenuItem<int>>.generate(
                    _chordMaxInversion + 1,
                    (i) => DropdownMenuItem<int>(
                      value: i,
                      child: Text(
                        i == 0 ? 'Posición fundamental' : '$iª inversión',
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
              const SizedBox(width: 8),
              _holdPlayButton(
                enabled:
                    _generatedChordJson != null &&
                    _extractMidiList(_generatedChordJson!, <String>[
                      'notes_midi',
                    ]).isNotEmpty,
                active: _generationPlayPressed,
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
            ],
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
                const SizedBox(height: 8),
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
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: _scaleLoopRunning ? _accent : null,
                        foregroundColor: _scaleLoopRunning
                            ? const Color(0xFF1A222D)
                            : null,
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
                            ? const Color(0xFF3B4659)
                            : null,
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
                const SizedBox(height: 8),
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
                const SizedBox(height: 8),
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
                  'Metrónomo',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
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
                          label: Text('$n'),
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
                  onPressed: _toggleMetronome,
                  icon: Icon(_metroRunning ? Icons.stop : Icons.play_arrow),
                  label: Text(
                    _metroRunning ? 'Detener metrónomo' : 'Iniciar metrónomo',
                  ),
                ),
                if (_metroTimerEnabled)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      '${_metroRemaining.inMinutes.remainder(60).toString().padLeft(2, '0')}:${_metroRemaining.inSeconds.remainder(60).toString().padLeft(2, '0')}',
                      style: const TextStyle(
                        color: _muted,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTunerPage() {
    final meter = (_tunerCents + 50) / 100.0;
    return _buildModeScaffold(
      showInstrument: false,
      controls: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const Text(
                  'Afinador',
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
                        items: const <DropdownMenuItem<String>>[
                          DropdownMenuItem<String>(
                            value: 'standard',
                            child: Text('E A D G B E'),
                          ),
                          DropdownMenuItem<String>(
                            value: 'drop_d',
                            child: Text('D A D G B E'),
                          ),
                          DropdownMenuItem<String>(
                            value: 'half_step',
                            child: Text('Eb Ab Db Gb Bb Eb'),
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
                const SizedBox(height: 8),
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
    String label = 'Play',
  }) {
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
      child: FilledButton.icon(
        style: FilledButton.styleFrom(
          backgroundColor: active ? _accent : null,
          foregroundColor: active ? const Color(0xFF1A222D) : null,
        ),
        onPressed: enabled ? () {} : null,
        icon: const Icon(Icons.play_arrow),
        label: Text(label),
      ),
    );
  }

  Widget _resultBlock({required TextEditingController controller}) {
    return Container(
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
        if (!scaleGuitarMode && degree < pairCount) {
          final bassMidi = scaleLhNotes[degree];
          final yBass = _midiToBassY(bassMidi.toDouble(), bassTop, gap);
          final currentBass =
              scaleCurrentNote != null && scaleCurrentNote == bassMidi;
          noteOutline.color = currentBass
              ? const Color(0xFFFF8A2B)
              : const Color(0xFFE9EDF2);
          canvas.drawOval(
            Rect.fromCenter(center: Offset(x, yBass), width: 16, height: 12),
            noteOutline,
          );
        }
        final trebleMidi = scaleRhNotes[degree];
        final yTreble = _midiToTrebleY(trebleMidi.toDouble(), trebleTop, gap);
        final currentTreble =
            scaleCurrentNote != null && scaleCurrentNote == trebleMidi;
        noteOutline.color = currentTreble
            ? const Color(0xFF4DA3EA)
            : const Color(0xFFE9EDF2);
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
          final overlaps = ys.any((prevY) => (y - prevY).abs() < overlapThreshold);
          if (!overlaps) break;
          col += 1;
        }
        final x = left + 110 + (col * noteW * 1.8);
        final ys = List<double>.from(placedCols[col] ?? const <double>[])..add(y);
        placedCols[col] = ys;
        Color? fillColor;
        if (generationPlayingNotes.contains(midi)) {
          if (!generationGuitarMode && lhSet.contains(midi) && !rhSet.contains(midi)) {
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

  @override
  bool shouldRepaint(covariant _MiniStaffPainter oldDelegate) {
    if (oldDelegate.notes.length != notes.length) return true;
    if (oldDelegate.extras.length != extras.length) return true;
    if (oldDelegate.generationRhNotes.length != generationRhNotes.length) return true;
    if (oldDelegate.generationLhNotes.length != generationLhNotes.length) return true;
    if (oldDelegate.generationPlayingNotes.length != generationPlayingNotes.length) return true;
    if (oldDelegate.generationGuitarMode != generationGuitarMode) return true;
    if (oldDelegate.scaleRhNotes.length != scaleRhNotes.length) return true;
    if (oldDelegate.scaleLhNotes.length != scaleLhNotes.length) return true;
    if (oldDelegate.scaleCurrentNote != scaleCurrentNote) return true;
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
    required this.currentBeat,
    required this.running,
    required this.direction,
    required this.motionProgress,
  });

  final int beatsPerBar;
  final int currentBeat;
  final bool running;
  final int direction;
  final double motionProgress;

  @override
  void paint(Canvas canvas, Size size) {
    final bg = Paint()..color = const Color(0xFF0F1621);
    canvas.drawRect(Offset.zero & size, bg);
    final title = TextPainter(
      text: const TextSpan(
        text: 'Tempo',
        style: TextStyle(
          color: Color(0xFFA8B6C8),
          fontSize: 13,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    title.paint(canvas, const Offset(14, 10));

    final count = math.max(1, beatsPerBar);
    final left = 34.0;
    final right = size.width - 34.0;
    final y = size.height * 0.54;
    final step = count == 1 ? 0.0 : (right - left) / (count - 1);

    final rail = Paint()
      ..color = const Color(0xFF8EA0B7)
      ..strokeWidth = 2;
    canvas.drawLine(Offset(left, y), Offset(right, y), rail);

    final markerPaint = Paint()..color = const Color(0xFF6F7F96);
    for (int i = 0; i < count; i += 1) {
      final x = count == 1 ? (left + right) / 2 : left + i * step;
      final active = running && i == currentBeat;
      canvas.drawCircle(Offset(x, y), active ? 7 : 5, markerPaint);
      final tp = TextPainter(
        text: TextSpan(
          text: '${i + 1}',
          style: TextStyle(
            color: active ? const Color(0xFFE9EDF2) : const Color(0xFF7E8FA9),
            fontSize: 11,
            fontWeight: FontWeight.w700,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(x - (tp.width / 2), y + 12));
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
    canvas.drawCircle(Offset(ballX, y), 11, redBall);
    canvas.drawCircle(Offset(ballX, y), 11, redBallOutline);

    final support = Paint()
      ..color = const Color(0xFF5E6E86)
      ..strokeWidth = 2;
    canvas.drawLine(
      Offset((left + right) / 2, y + 22),
      Offset((left + right) / 2, y + 44),
      support,
    );
    final base = Paint()..color = const Color(0xFF2F3A4B);
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH((left + right) / 2 - 34, y + 44, 68, 12),
        const Radius.circular(6),
      ),
      base,
    );
    final baseBorder = Paint()
      ..color = const Color(0xFF6A7A94)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH((left + right) / 2 - 34, y + 44, 68, 12),
        const Radius.circular(6),
      ),
      baseBorder,
    );

    if (!running) {
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
      idle.paint(canvas, Offset((size.width - idle.width) / 2, y + 66));
    }
  }

  @override
  bool shouldRepaint(covariant _MiniMetronomePainter oldDelegate) {
    return oldDelegate.beatsPerBar != beatsPerBar ||
        oldDelegate.currentBeat != currentBeat ||
        oldDelegate.running != running ||
        oldDelegate.direction != direction ||
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
