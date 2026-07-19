import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/audio_player_port.dart';

final class _FakePlayerPort implements AudioPlayerPort {
  final List<String> calls = <String>[];
  Object? modeError;
  int disposeCalls = 0;

  @override
  Stream<void> get onComplete => const Stream<void>.empty();

  @override
  Future<void> setPlayerMode(PlayerMode mode) async {
    calls.add('mode:$mode');
    if (modeError != null) throw modeError!;
  }

  @override
  Future<void> setReleaseMode(ReleaseMode mode) async {
    calls.add('release:$mode');
  }

  @override
  Future<void> setAudioContext(AudioContext context) async {
    calls.add('context');
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
  }

  @override
  Future<void> play(Source source, {double? volume}) async {}

  @override
  Future<void> resume() async {}

  @override
  Future<void> setPlaybackRate(double rate) async {}

  @override
  Future<void> setSource(Source source) async {}

  @override
  Future<void> setVolume(double volume) async {}
}

void main() {
  test(
    'factory configures mode, release, and optional context in order',
    () async {
      final port = _FakePlayerPort();
      final factory = AudioPlayerPortFactory(createPort: () => port);

      final result = await factory.create(
        mode: PlayerMode.lowLatency,
        context: AudioContext(),
      );

      expect(result, same(port));
      expect(port.calls, <String>[
        'mode:PlayerMode.lowLatency',
        'release:ReleaseMode.release',
        'context',
      ]);
    },
  );

  test('factory omits context when none is requested', () async {
    final port = _FakePlayerPort();
    final factory = AudioPlayerPortFactory(createPort: () => port);

    await factory.create(mode: PlayerMode.mediaPlayer);

    expect(port.calls, <String>[
      'mode:PlayerMode.mediaPlayer',
      'release:ReleaseMode.release',
    ]);
  });

  test('configuration failure disposes the partially created player', () async {
    final port = _FakePlayerPort()..modeError = StateError('mode');
    final factory = AudioPlayerPortFactory(createPort: () => port);

    await expectLater(
      factory.create(mode: PlayerMode.mediaPlayer),
      throwsStateError,
    );
    expect(port.disposeCalls, 1);
  });
}
