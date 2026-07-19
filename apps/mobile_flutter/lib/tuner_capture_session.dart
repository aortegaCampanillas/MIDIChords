import 'package:flutter_audio_capture/flutter_audio_capture.dart';

typedef TunerSamplesCallback = void Function(dynamic samples);
typedef TunerErrorCallback = void Function(Object error);

abstract interface class TunerCapturePort {
  double? get actualSampleRate;

  Future<bool> init();

  Future<void> start(
    TunerSamplesCallback onSamples,
    TunerErrorCallback onError, {
    required int sampleRate,
    required int bufferSize,
  });

  Future<void> stop();
}

final class FlutterTunerCapturePort implements TunerCapturePort {
  FlutterTunerCapturePort([FlutterAudioCapture? capture])
    : _capture = capture ?? FlutterAudioCapture();

  final FlutterAudioCapture _capture;

  @override
  double? get actualSampleRate => _capture.actualSampleRate;

  @override
  Future<bool> init() async => await _capture.init() == true;

  @override
  Future<void> start(
    TunerSamplesCallback onSamples,
    TunerErrorCallback onError, {
    required int sampleRate,
    required int bufferSize,
  }) => _capture.start(
    onSamples,
    onError,
    sampleRate: sampleRate,
    bufferSize: bufferSize,
  );

  @override
  Future<void> stop() => _capture.stop();
}

final class TunerCaptureSession {
  TunerCaptureSession({required TunerCapturePort Function() createPort})
    : _createPort = createPort;

  factory TunerCaptureSession.plugin() =>
      TunerCaptureSession(createPort: FlutterTunerCapturePort.new);

  final TunerCapturePort Function() _createPort;
  TunerCapturePort? _port;
  bool _started = false;

  double? get actualSampleRate => _port?.actualSampleRate;
  bool get isStarted => _started;

  Future<void> start(
    TunerSamplesCallback onSamples,
    TunerErrorCallback onError, {
    required int sampleRate,
    required int bufferSize,
  }) async {
    if (_started) return;
    final port = _port ??= _createPort();
    if (!await port.init()) {
      throw StateError('No se pudo inicializar la captura de audio');
    }
    try {
      await port.start(
        onSamples,
        onError,
        sampleRate: sampleRate,
        bufferSize: bufferSize,
      );
      _started = true;
    } catch (_) {
      await port.stop();
      rethrow;
    }
  }

  Future<void> stop() async {
    if (!_started) return;
    _started = false;
    await _port?.stop();
  }

  Future<void> dispose() async {
    await stop();
    _port = null;
  }
}
