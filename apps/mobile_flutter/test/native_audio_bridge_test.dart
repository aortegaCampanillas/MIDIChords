import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/native_audio_bridge.dart';

final class _FakeNativeAudioPort implements NativeAudioPort {
  String? method;
  Map<String, Object>? arguments;
  bool? result = true;
  Object? error;

  @override
  Future<T?> invoke<T>(String method, Map<String, Object> arguments) async {
    this.method = method;
    this.arguments = arguments;
    if (error != null) throw error!;
    return result as T?;
  }
}

void main() {
  test('tone selects platform method and normalizes its arguments', () async {
    final port = _FakeNativeAudioPort();
    final bridge = NativeAudioBridge(port: port);

    expect(
      await bridge.playTone(
        platform: 'android',
        midi: 150,
        instrument: 'piano',
        durationMs: 20,
        volume: 2,
      ),
      isTrue,
    );
    expect(port.method, 'playAndroidSynthTone');
    expect(port.arguments, <String, Object>{
      'midi': 127,
      'instrument': 'piano',
      'durationMs': 80,
      'volume': 1.0,
    });
  });

  test('iOS chord uses its lower duration bound and clamps notes', () async {
    final port = _FakeNativeAudioPort();
    final bridge = NativeAudioBridge(port: port);

    expect(
      await bridge.playChord(
        platform: 'ios',
        notes: <int>[-2, 60, 140],
        instrument: 'guitar',
        durationMs: 10,
        volume: -1,
      ),
      isTrue,
    );
    expect(port.method, 'playIosSynthChord');
    expect(port.arguments, <String, Object>{
      'notes': <int>[0, 60, 127],
      'instrument': 'guitar',
      'durationMs': 40,
      'volume': 0.0,
    });
  });

  test('empty chord does not call the native port', () async {
    final port = _FakeNativeAudioPort();
    final bridge = NativeAudioBridge(port: port);

    expect(
      await bridge.playChord(
        platform: 'android',
        notes: const <int>[],
        instrument: 'piano',
        durationMs: 500,
        volume: 1,
      ),
      isFalse,
    );
    expect(port.method, isNull);
  });

  test('metronome keeps platform-specific arguments', () async {
    final port = _FakeNativeAudioPort();
    final bridge = NativeAudioBridge(port: port);

    await bridge.playMetronomeClick(
      platform: 'android',
      level: 4,
      volume: 0.5,
    );
    expect(port.method, 'playAndroidMetronomeClick');
    expect(port.arguments, <String, Object>{
      'level': 2,
      'durationMs': 55,
      'volume': 0.5,
    });

    await bridge.playMetronomeClick(
      platform: 'ios',
      level: -1,
      volume: 0.25,
    );
    expect(port.method, 'playIosMetronomeClick');
    expect(port.arguments, <String, Object>{'level': 0, 'volume': 0.25});
  });

  test('null results and native failures are reported as unavailable', () async {
    final port = _FakeNativeAudioPort()..result = null;
    final bridge = NativeAudioBridge(port: port);

    expect(
      await bridge.playTone(
        platform: 'ios',
        midi: 60,
        instrument: 'piano',
        durationMs: 500,
        volume: 1,
      ),
      isFalse,
    );

    port.error = StateError('channel unavailable');
    expect(
      await bridge.playMetronomeClick(
        platform: 'android',
        level: 1,
        volume: 1,
      ),
      isFalse,
    );
  });
}
