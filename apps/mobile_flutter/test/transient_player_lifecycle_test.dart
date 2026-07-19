import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/transient_player_lifecycle.dart';

final class _FakePlayer {
  _FakePlayer(this.name);

  final String name;
  final StreamController<void> completion = StreamController<void>();
  int disposeCalls = 0;
  bool failDispose = false;

  Future<void> dispose() async {
    disposeCalls += 1;
    if (failDispose) throw StateError('dispose $name');
  }
}

void main() {
  test('completion disposes a watched player exactly once', () async {
    final player = _FakePlayer('tone');
    final lifecycle = TransientPlayerLifecycle<_FakePlayer>(
      disposePlayer: (value) => value.dispose(),
    );

    lifecycle.watch(player, player.completion.stream);
    expect(lifecycle.trackedCount, 1);

    player.completion.add(null);
    await pumpEventQueue();
    await lifecycle.dispose(player);

    expect(player.disposeCalls, 1);
    expect(lifecycle.trackedCount, 0);
    await player.completion.close();
  });

  test('repeated watch and dispose do not duplicate ownership', () async {
    final player = _FakePlayer('sample');
    final lifecycle = TransientPlayerLifecycle<_FakePlayer>(
      disposePlayer: (value) => value.dispose(),
    );

    lifecycle.watch(player, player.completion.stream);
    lifecycle.watch(player, player.completion.stream);
    await Future.wait(<Future<void>>[
      lifecycle.dispose(player),
      lifecycle.dispose(player),
    ]);

    expect(player.disposeCalls, 1);
    await player.completion.close();
  });

  test('disposeAll closes every tracked player and absorbs failures', () async {
    final first = _FakePlayer('first')..failDispose = true;
    final second = _FakePlayer('second');
    final lifecycle = TransientPlayerLifecycle<_FakePlayer>(
      disposePlayer: (value) => value.dispose(),
    );
    lifecycle.watch(first, first.completion.stream);
    lifecycle.watch(second, second.completion.stream);

    await lifecycle.disposeAll();

    expect(first.disposeCalls, 1);
    expect(second.disposeCalls, 1);
    expect(lifecycle.trackedCount, 0);
    await first.completion.close();
    await second.completion.close();
  });
}
