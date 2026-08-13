import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

abstract interface class NativeAudioPort {
  Future<T?> invoke<T>(String method, Map<String, Object> arguments);
}

final class MethodChannelNativeAudioPort implements NativeAudioPort {
  const MethodChannelNativeAudioPort(this._channel);

  final MethodChannel _channel;

  @override
  Future<T?> invoke<T>(String method, Map<String, Object> arguments) =>
      _channel.invokeMethod<T>(method, arguments);
}

final class NativeAudioBridge {
  NativeAudioBridge({required NativeAudioPort port}) : _port = port;

  factory NativeAudioBridge.plugin() => NativeAudioBridge(
    port: const MethodChannelNativeAudioPort(
      MethodChannel('midichords/platform'),
    ),
  );

  final NativeAudioPort _port;

  Future<bool> playTone({
    required String platform,
    required int midi,
    required String instrument,
    required int durationMs,
    required double volume,
  }) => _invoke('play${_platformPrefix(platform)}SynthTone', <String, Object>{
    'midi': midi.clamp(0, 127),
    'instrument': instrument,
    'durationMs': durationMs.clamp(platform == 'ios' ? 40 : 80, 2600),
    'volume': volume.clamp(0.0, 1.0),
  });

  Future<bool> playChord({
    required String platform,
    required List<int> notes,
    required String instrument,
    required int durationMs,
    required double volume,
  }) {
    if (notes.isEmpty) return Future<bool>.value(false);
    return _invoke('play${_platformPrefix(platform)}SynthChord', <
      String,
      Object
    >{
      'notes': notes.map((note) => note.clamp(0, 127)).toList(growable: false),
      'instrument': instrument,
      'durationMs': durationMs.clamp(platform == 'ios' ? 40 : 80, 2600),
      'volume': volume.clamp(0.0, 1.0),
    });
  }

  Future<bool> playMetronomeClick({
    required String platform,
    required int level,
    required double volume,
  }) => _invoke(
    'play${_platformPrefix(platform)}MetronomeClick',
    <String, Object>{
      'level': level.clamp(0, 2),
      if (platform == 'android') 'durationMs': 55,
      'volume': volume.clamp(0.0, 1.0),
    },
  );

  Future<bool> _invoke(String method, Map<String, Object> arguments) async {
    try {
      return await _port.invoke<bool>(method, arguments) ?? false;
    } catch (error) {
      debugPrint('Native audio unavailable ($method): $error');
      return false;
    }
  }

  static String _platformPrefix(String platform) => switch (platform) {
    'android' => 'Android',
    'ios' => 'Ios',
    _ => throw ArgumentError.value(platform, 'platform'),
  };
}
