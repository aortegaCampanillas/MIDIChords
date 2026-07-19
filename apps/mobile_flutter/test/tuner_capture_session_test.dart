import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/tuner_capture_session.dart';

final class _FakeCapturePort implements TunerCapturePort {
  bool initialized = true;
  int initCalls = 0;
  int startCalls = 0;
  int stopCalls = 0;
  int? requestedSampleRate;
  int? requestedBufferSize;
  TunerSamplesCallback? onSamples;
  TunerErrorCallback? onError;
  Object? startError;

  @override
  double? actualSampleRate = 48000;

  @override
  Future<bool> init() async {
    initCalls += 1;
    return initialized;
  }

  @override
  Future<void> start(
    TunerSamplesCallback onSamples,
    TunerErrorCallback onError, {
    required int sampleRate,
    required int bufferSize,
  }) async {
    startCalls += 1;
    if (startError != null) throw startError!;
    requestedSampleRate = sampleRate;
    requestedBufferSize = bufferSize;
    this.onSamples = onSamples;
    this.onError = onError;
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }
}

void main() {
  test(
    'start initializes once, forwards callbacks, and exposes sample rate',
    () async {
      final port = _FakeCapturePort();
      var samples = 0;
      Object? error;
      final session = TunerCaptureSession(createPort: () => port);

      await session.start(
        (_) => samples += 1,
        (value) => error = value,
        sampleRate: 44100,
        bufferSize: 3000,
      );
      await session.start((_) {}, (_) {}, sampleRate: 22050, bufferSize: 1000);
      port.onSamples?.call(<double>[0.1]);
      port.onError?.call(StateError('capture'));

      expect(session.isStarted, isTrue);
      expect(session.actualSampleRate, 48000);
      expect(port.initCalls, 1);
      expect(port.startCalls, 1);
      expect(port.requestedSampleRate, 44100);
      expect(port.requestedBufferSize, 3000);
      expect(samples, 1);
      expect(error, isA<StateError>());
    },
  );

  test(
    'failed initialization does not start or mark the session active',
    () async {
      final port = _FakeCapturePort()..initialized = false;
      final session = TunerCaptureSession(createPort: () => port);

      await expectLater(
        session.start((_) {}, (_) {}, sampleRate: 44100, bufferSize: 3000),
        throwsStateError,
      );
      expect(session.isStarted, isFalse);
      expect(port.startCalls, 0);
      expect(port.stopCalls, 0);
    },
  );

  test('stop and dispose are idempotent', () async {
    final port = _FakeCapturePort();
    final session = TunerCaptureSession(createPort: () => port);
    await session.start((_) {}, (_) {}, sampleRate: 44100, bufferSize: 3000);

    await session.stop();
    await session.stop();
    await session.dispose();

    expect(session.isStarted, isFalse);
    expect(session.actualSampleRate, isNull);
    expect(port.stopCalls, 1);
  });

  test('a failed native start is stopped and can be retried', () async {
    final port = _FakeCapturePort()..startError = StateError('native start');
    final session = TunerCaptureSession(createPort: () => port);

    await expectLater(
      session.start((_) {}, (_) {}, sampleRate: 44100, bufferSize: 3000),
      throwsStateError,
    );
    expect(session.isStarted, isFalse);
    expect(port.stopCalls, 1);

    port.startError = null;
    await session.start((_) {}, (_) {}, sampleRate: 44100, bufferSize: 3000);
    expect(session.isStarted, isTrue);
    expect(port.initCalls, 2);
    expect(port.startCalls, 2);
  });
}
