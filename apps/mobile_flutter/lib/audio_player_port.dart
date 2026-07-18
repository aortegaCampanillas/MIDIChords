import 'dart:async';

import 'package:audioplayers/audioplayers.dart';

abstract interface class AudioPlayerPort {
  Stream<void> get onComplete;

  Future<void> setPlayerMode(PlayerMode mode);
  Future<void> setReleaseMode(ReleaseMode mode);
  Future<void> setAudioContext(AudioContext context);
  Future<void> setSource(Source source);
  Future<void> setPlaybackRate(double rate);
  Future<void> setVolume(double volume);
  Future<void> play(Source source, {double? volume});
  Future<void> resume();
  Future<void> dispose();
}

final class PluginAudioPlayerPort implements AudioPlayerPort {
  PluginAudioPlayerPort([AudioPlayer? player])
    : _player = player ?? AudioPlayer() {
    _player.positionUpdater = null;
  }

  final AudioPlayer _player;

  @override
  Stream<void> get onComplete => _player.onPlayerComplete;

  @override
  Future<void> setPlayerMode(PlayerMode mode) => _player.setPlayerMode(mode);

  @override
  Future<void> setReleaseMode(ReleaseMode mode) => _player.setReleaseMode(mode);

  @override
  Future<void> setAudioContext(AudioContext context) =>
      _player.setAudioContext(context);

  @override
  Future<void> setSource(Source source) => _player.setSource(source);

  @override
  Future<void> setPlaybackRate(double rate) => _player.setPlaybackRate(rate);

  @override
  Future<void> setVolume(double volume) => _player.setVolume(volume);

  @override
  Future<void> play(Source source, {double? volume}) =>
      _player.play(source, volume: volume);

  @override
  Future<void> resume() => _player.resume();

  @override
  Future<void> dispose() => _player.dispose();
}

final class AudioPlayerPortFactory {
  AudioPlayerPortFactory({required AudioPlayerPort Function() createPort})
    : _createPort = createPort;

  factory AudioPlayerPortFactory.plugin() =>
      AudioPlayerPortFactory(createPort: PluginAudioPlayerPort.new);

  final AudioPlayerPort Function() _createPort;

  Future<AudioPlayerPort> create({
    required PlayerMode mode,
    AudioContext? context,
  }) async {
    final player = _createPort();
    try {
      await player.setPlayerMode(mode);
      await player.setReleaseMode(ReleaseMode.release);
      if (context != null) await player.setAudioContext(context);
      return player;
    } catch (_) {
      try {
        await player.dispose();
      } catch (_) {}
      rethrow;
    }
  }
}
