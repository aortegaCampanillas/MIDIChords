import 'dart:convert';
import 'dart:async';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_audio_capture/flutter_audio_capture.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MidiChordsMobileApp());
}

class MidiChordsMobileApp extends StatelessWidget {
  const MidiChordsMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MIDIChords Tablet',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2D6A4F)),
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
  final TextEditingController _apiBaseController = TextEditingController(text: 'http://127.0.0.1:8000');
  final TextEditingController _detectNotesController = TextEditingController(text: '60,64,67');

  final TextEditingController _detectionOutputController = TextEditingController(text: 'Sin resultados');
  final TextEditingController _chordOutputController = TextEditingController(text: 'Sin resultados');
  final TextEditingController _scaleOutputController = TextEditingController(text: 'Sin resultados');

  int _tabIndex = 0;
  bool _loadingMeta = false;
  bool _requestInFlight = false;

  String _language = 'es';
  String _accidental = 'sharp';

  List<Map<String, dynamic>> _chordPatterns = <Map<String, dynamic>>[];
  List<Map<String, dynamic>> _scalePatterns = <Map<String, dynamic>>[];

  int _chordRootPc = 0;
  String _chordSuffix = '';
  int _chordInversion = 0;
  int _chordMaxInversion = 0;

  int _scaleTonicPc = 0;
  String _scalePatternName = 'Ionian';
  final Set<int> _detectionSelectedNotes = <int>{60, 64, 67};
  int _metroBpm = 120;
  int _metroBeatsPerBar = 4;
  int _metroCurrentBeat = -1;
  bool _metroRunning = false;
  Timer? _metroTimer;
  FlutterAudioCapture? _audioCapture;
  bool _tunerRunning = false;
  String _tunerNote = '-';
  int _tunerCents = 0;
  double _tunerFreq = 0.0;
  String _tunerError = '';
  double _tunerSmoothedFreq = 0.0;
  final int _tunerSampleRate = 44100;
  DateTime _lastTunerUiUpdate = DateTime.fromMillisecondsSinceEpoch(0);

  @override
  void initState() {
    super.initState();
    _loadMeta();
  }

  @override
  void dispose() {
    _metroTimer?.cancel();
    _audioCapture?.stop();
    _apiBaseController.dispose();
    _detectNotesController.dispose();
    _detectionOutputController.dispose();
    _chordOutputController.dispose();
    _scaleOutputController.dispose();
    super.dispose();
  }

  Uri _uri(String path) => Uri.parse('${_apiBaseController.text.trim()}$path');

  Future<Map<String, dynamic>> _postJson(String path, Map<String, dynamic> payload) async {
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
      final chordPatterns = (json['chord_patterns'] as List<dynamic>? ?? <dynamic>[])
          .whereType<Map<String, dynamic>>()
          .toList();
      final scalePatterns = (json['scale_patterns'] as List<dynamic>? ?? <dynamic>[])
          .whereType<Map<String, dynamic>>()
          .toList();
      setState(() {
        _chordPatterns = chordPatterns;
        _scalePatterns = scalePatterns;
        if (_chordPatterns.isNotEmpty) {
          final current = _chordPatterns.where((p) => (p['suffix'] as String? ?? '') == _chordSuffix);
          if (current.isEmpty) {
            _chordSuffix = (_chordPatterns.first['suffix'] as String? ?? '');
          }
          _recomputeMaxInversion();
        }
        if (_scalePatterns.isNotEmpty) {
          final current = _scalePatterns.where((p) => (p['name'] as String? ?? '') == _scalePatternName);
          if (current.isEmpty) {
            _scalePatternName = (_scalePatterns.first['name'] as String? ?? 'Ionian');
          }
        }
      });
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
      orElse: () => _chordPatterns.isNotEmpty ? _chordPatterns.first : <String, dynamic>{'intervals': <int>[0]},
    );
    final intervals = (match['intervals'] as List<dynamic>? ?? <dynamic>[0]).length;
    _chordMaxInversion = intervals > 0 ? intervals - 1 : 0;
    if (_chordInversion > _chordMaxInversion) {
      _chordInversion = _chordMaxInversion;
    }
  }

  Future<void> _callDetect() async {
    if (_requestInFlight) {
      return;
    }
    setState(() => _requestInFlight = true);
    try {
      final notes = _detectNotesController.text
          .split(',')
          .map((v) => v.trim())
          .where((v) => v.isNotEmpty)
          .map(int.parse)
          .toList();
      final json = await _postJson('/api/detect', <String, dynamic>{
        'notes': notes,
        'language': _language,
        'accidental': _accidental,
      });
      _detectionOutputController.text = 'Acorde: ${json['name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'Sobrantes: ${(json['extras'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}';
    } catch (err) {
      _detectionOutputController.text = 'Error: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  void _syncDetectTextFromSelection() {
    final ordered = _detectionSelectedNotes.toList()..sort();
    _detectNotesController.text = ordered.join(',');
  }

  void _syncSelectionFromDetectText() {
    final parsed = _detectNotesController.text
        .split(',')
        .map((v) => v.trim())
        .where((v) => v.isNotEmpty)
        .map(int.tryParse)
        .whereType<int>()
        .where((n) => n >= 21 && n <= 108)
        .toSet();
    setState(() {
      _detectionSelectedNotes
        ..clear()
        ..addAll(parsed);
    });
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
      _chordOutputController.text = 'Acorde: ${json['name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'MIDI: ${(json['notes_midi'] as List<dynamic>? ?? <dynamic>[]).join(', ')}';
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
      _scaleOutputController.text = 'Escala: ${json['pattern_localized_name'] ?? json['pattern_name']}\n'
          'Notas: ${(json['notes'] as List<dynamic>? ?? <dynamic>[]).join(' - ')}\n'
          'MIDI: ${(json['notes_midi'] as List<dynamic>? ?? <dynamic>[]).join(', ')}';
    } catch (err) {
      _scaleOutputController.text = 'Error: $err';
    } finally {
      if (mounted) {
        setState(() => _requestInFlight = false);
      }
    }
  }

  String _pcLabel(int pc) {
    const labelsSharpEs = <String>['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si'];
    const labelsFlatEs = <String>['Do', 'Re♭', 'Re', 'Mi♭', 'Mi', 'Fa', 'Sol♭', 'Sol', 'La♭', 'La', 'Si♭', 'Si'];
    const labelsSharpEn = <String>['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const labelsFlatEn = <String>['C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭', 'A', 'B♭', 'B'];
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
    final nextBeat = (_metroCurrentBeat + 1) % _metroBeatsPerBar;
    setState(() => _metroCurrentBeat = nextBeat);
    if (nextBeat == 0) {
      SystemSound.play(SystemSoundType.click);
      HapticFeedback.mediumImpact();
    } else {
      SystemSound.play(SystemSoundType.click);
      HapticFeedback.selectionClick();
    }
  }

  void _startMetronome() {
    _metroTimer?.cancel();
    setState(() {
      _metroRunning = true;
      _metroCurrentBeat = -1;
    });
    _metronomeTick();
    final intervalMs = (60000 / _metroBpm).round().clamp(120, 2000);
    _metroTimer = Timer.periodic(Duration(milliseconds: intervalMs), (_) => _metronomeTick());
  }

  void _stopMetronome() {
    _metroTimer?.cancel();
    _metroTimer = null;
    setState(() {
      _metroRunning = false;
      _metroCurrentBeat = -1;
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
    final detected = _estimatePitch(samples, _tunerSampleRate);
    if (detected == null) {
      return;
    }
    _tunerSmoothedFreq = _tunerSmoothedFreq <= 0.0 ? detected : (_tunerSmoothedFreq * 0.72 + detected * 0.28);
    final now = DateTime.now();
    if (now.difference(_lastTunerUiUpdate).inMilliseconds < 80) {
      return;
    }
    _lastTunerUiUpdate = now;
    final midi = 69 + 12 * (math.log(_tunerSmoothedFreq / 440.0) / math.ln2);
    final rounded = midi.round();
    final cents = ((midi - rounded) * 100).round();
    final note = _pcLabel(((rounded % 12) + 12) % 12);
    if (!mounted || !_tunerRunning) {
      return;
    }
    setState(() {
      _tunerNote = note;
      _tunerCents = cents.clamp(-50, 50);
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
      appBar: AppBar(title: const Text('MIDIChords Tablet')),
      body: Column(
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Column(
              children: <Widget>[
                TextField(
                  controller: _apiBaseController,
                  decoration: const InputDecoration(
                    labelText: 'Backend API base URL',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: <Widget>[
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        key: ValueKey<String>('lang_$_language'),
                        initialValue: _language,
                        decoration: const InputDecoration(labelText: 'Idioma', border: OutlineInputBorder()),
                        items: const <DropdownMenuItem<String>>[
                          DropdownMenuItem<String>(value: 'es', child: Text('Español')),
                          DropdownMenuItem<String>(value: 'en', child: Text('English')),
                        ],
                        onChanged: (value) async {
                          if (value == null) {
                            return;
                          }
                          setState(() => _language = value);
                          await _loadMeta();
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        key: ValueKey<String>('acc_$_accidental'),
                        initialValue: _accidental,
                        decoration: const InputDecoration(labelText: 'Alteración', border: OutlineInputBorder()),
                        items: const <DropdownMenuItem<String>>[
                          DropdownMenuItem<String>(value: 'sharp', child: Text('#')),
                          DropdownMenuItem<String>(value: 'flat', child: Text('♭')),
                        ],
                        onChanged: (value) {
                          if (value == null) {
                            return;
                          }
                          setState(() => _accidental = value);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.icon(
                      onPressed: _loadingMeta ? null : _loadMeta,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Meta'),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(child: pages[_tabIndex]),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tabIndex,
        onDestinationSelected: (index) => setState(() => _tabIndex = index),
        destinations: const <NavigationDestination>[
          NavigationDestination(icon: Icon(Icons.piano), label: 'Detección'),
          NavigationDestination(icon: Icon(Icons.library_music), label: 'Acordes'),
          NavigationDestination(icon: Icon(Icons.music_note), label: 'Escalas'),
          NavigationDestination(icon: Icon(Icons.timer), label: 'Metrónomo'),
          NavigationDestination(icon: Icon(Icons.graphic_eq), label: 'Afinador'),
        ],
      ),
    );
  }

  Widget _buildDetectionPage() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Text('Notas MIDI (coma separadas)', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          _buildDetectionKeyboard(),
          const SizedBox(height: 8),
          TextField(
            controller: _detectNotesController,
            decoration: const InputDecoration(border: OutlineInputBorder(), hintText: '60,64,67'),
            onChanged: (_) => _syncSelectionFromDetectText(),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: <Widget>[
              OutlinedButton.icon(
                onPressed: () {
                  setState(() => _detectionSelectedNotes.clear());
                  _syncDetectTextFromSelection();
                },
                icon: const Icon(Icons.clear_all),
                label: const Text('Limpiar'),
              ),
              OutlinedButton.icon(
                onPressed: () {
                  setState(() {
                    _detectionSelectedNotes
                      ..clear()
                      ..addAll(<int>{60, 64, 67});
                  });
                  _syncDetectTextFromSelection();
                },
                icon: const Icon(Icons.restore),
                label: const Text('C-E-G'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: _requestInFlight ? null : _callDetect,
            icon: const Icon(Icons.search),
            label: const Text('Detectar acorde'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: TextField(
              controller: _detectionOutputController,
              readOnly: true,
              maxLines: null,
              expands: true,
              decoration: const InputDecoration(border: OutlineInputBorder(), labelText: 'Resultado'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetectionKeyboard() {
    final midiRange = List<int>.generate(24, (i) => 48 + i); // C3..B4
    return SizedBox(
      height: 120,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: midiRange.map((midi) {
            final active = _detectionSelectedNotes.contains(midi);
            final isBlack = const <int>{1, 3, 6, 8, 10}.contains(midi % 12);
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: GestureDetector(
                onTap: () {
                  setState(() {
                    if (active) {
                      _detectionSelectedNotes.remove(midi);
                    } else {
                      _detectionSelectedNotes.add(midi);
                    }
                  });
                  _syncDetectTextFromSelection();
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 80),
                  width: isBlack ? 30 : 38,
                  height: isBlack ? 82 : 108,
                  decoration: BoxDecoration(
                    color: active
                        ? (isBlack ? Colors.orange.shade700 : Colors.orange.shade300)
                        : (isBlack ? Colors.black87 : Colors.white),
                    border: Border.all(color: Colors.grey.shade600),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        _pcLabel(midi % 12),
                        style: TextStyle(
                          fontSize: isBlack ? 9 : 10,
                          color: (active || !isBlack) ? Colors.black : Colors.white,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildChordGenerationPage() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: DropdownButtonFormField<int>(
                  key: ValueKey<int>(_chordRootPc),
                  initialValue: _chordRootPc,
                  decoration: const InputDecoration(labelText: 'Tónica', border: OutlineInputBorder()),
                  items: List<DropdownMenuItem<int>>.generate(
                    12,
                    (index) => DropdownMenuItem<int>(value: index, child: Text(_pcLabel(index))),
                  ),
                  onChanged: (value) {
                    if (value == null) {
                      return;
                    }
                    setState(() => _chordRootPc = value);
                  },
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: DropdownButtonFormField<String>(
                  key: ValueKey<String>('suffix_$_chordSuffix'),
                  initialValue: _chordSuffix,
                  decoration: const InputDecoration(labelText: 'Variante', border: OutlineInputBorder()),
                  items: _chordPatterns
                      .map(
                        (p) => DropdownMenuItem<String>(
                          value: (p['suffix'] as String? ?? ''),
                          child: Text((p['suffix'] as String? ?? '').isEmpty ? 'maj' : (p['suffix'] as String? ?? '')),
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
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: <Widget>[
              const Text('Inversión'),
              Expanded(
                child: Slider(
                  min: 0,
                  max: _chordMaxInversion.toDouble(),
                  divisions: _chordMaxInversion == 0 ? 1 : _chordMaxInversion,
                  value: _chordInversion.toDouble().clamp(0, _chordMaxInversion.toDouble()),
                  onChanged: (value) => setState(() => _chordInversion = value.round()),
                ),
              ),
              Text('$_chordInversion'),
            ],
          ),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              onPressed: _requestInFlight ? null : _callGenerateChord,
              icon: const Icon(Icons.auto_fix_high),
              label: const Text('Generar acorde'),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: TextField(
              controller: _chordOutputController,
              readOnly: true,
              maxLines: null,
              expands: true,
              decoration: const InputDecoration(border: OutlineInputBorder(), labelText: 'Resultado'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScaleGenerationPage() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: DropdownButtonFormField<int>(
                  key: ValueKey<int>(100 + _scaleTonicPc),
                  initialValue: _scaleTonicPc,
                  decoration: const InputDecoration(labelText: 'Tónica', border: OutlineInputBorder()),
                  items: List<DropdownMenuItem<int>>.generate(
                    12,
                    (index) => DropdownMenuItem<int>(value: index, child: Text(_pcLabel(index))),
                  ),
                  onChanged: (value) {
                    if (value == null) {
                      return;
                    }
                    setState(() => _scaleTonicPc = value);
                  },
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: DropdownButtonFormField<String>(
                  key: ValueKey<String>('scale_$_scalePatternName'),
                  initialValue: _scalePatternName,
                  decoration: const InputDecoration(labelText: 'Escala', border: OutlineInputBorder()),
                  items: _scalePatterns
                      .map(
                        (p) => DropdownMenuItem<String>(
                          value: (p['name'] as String? ?? 'Ionian'),
                          child: Text((p['localized_name'] as String? ?? p['name'] as String? ?? 'Ionian')),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value == null) {
                      return;
                    }
                    setState(() => _scalePatternName = value);
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              onPressed: _requestInFlight ? null : _callGenerateScale,
              icon: const Icon(Icons.auto_graph),
              label: const Text('Generar escala'),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: TextField(
              controller: _scaleOutputController,
              readOnly: true,
              maxLines: null,
              expands: true,
              decoration: const InputDecoration(border: OutlineInputBorder(), labelText: 'Resultado'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetronomePage() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Text('Tempo (BPM)', style: TextStyle(fontWeight: FontWeight.w600)),
          Row(
            children: <Widget>[
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
              SizedBox(width: 56, child: Text('$_metroBpm')),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: <Widget>[
              const Text('Pulsos por compás:'),
              const SizedBox(width: 10),
              DropdownButton<int>(
                value: _metroBeatsPerBar,
                items: const <DropdownMenuItem<int>>[
                  DropdownMenuItem<int>(value: 2, child: Text('2')),
                  DropdownMenuItem<int>(value: 3, child: Text('3')),
                  DropdownMenuItem<int>(value: 4, child: Text('4')),
                  DropdownMenuItem<int>(value: 5, child: Text('5')),
                  DropdownMenuItem<int>(value: 6, child: Text('6')),
                ],
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
            ],
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _toggleMetronome,
            icon: Icon(_metroRunning ? Icons.stop : Icons.play_arrow),
            label: Text(_metroRunning ? 'Detener metrónomo' : 'Iniciar metrónomo'),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: List<Widget>.generate(_metroBeatsPerBar, (index) {
              final active = index == _metroCurrentBeat;
              final isBarStart = index == 0;
              return AnimatedContainer(
                duration: const Duration(milliseconds: 80),
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: active
                      ? (isBarStart ? Colors.orange : Colors.blue)
                      : Colors.grey.shade300,
                  border: Border.all(
                    color: isBarStart ? Colors.deepOrange : Colors.grey.shade500,
                    width: isBarStart ? 2 : 1,
                  ),
                ),
                child: Center(
                  child: Text(
                    '${index + 1}',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: active ? Colors.white : Colors.black87,
                    ),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildTunerPage() {
    final meter = (_tunerCents + 50) / 100.0;
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          FilledButton.icon(
            onPressed: _toggleTuner,
            icon: Icon(_tunerRunning ? Icons.hearing_disabled : Icons.hearing),
            label: Text(_tunerRunning ? 'Detener afinador' : 'Iniciar afinador'),
          ),
          const SizedBox(height: 12),
          Row(
            children: <Widget>[
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        const Text('Nota detectada', style: TextStyle(fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        Text(
                          _tunerNote,
                          style: const TextStyle(fontSize: 42, fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 8),
                        Text('${_tunerFreq.toStringAsFixed(1)} Hz'),
                        Text('${_tunerCents >= 0 ? '+' : ''}$_tunerCents cents'),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 20,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10),
              color: Colors.grey.shade300,
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
            Text(
              'Error: $_tunerError',
              style: const TextStyle(color: Colors.red),
            ),
        ],
      ),
    );
  }

}
