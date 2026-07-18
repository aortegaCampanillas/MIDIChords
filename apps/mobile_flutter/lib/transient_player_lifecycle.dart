import 'dart:async';

typedef PlayerDisposer<T extends Object> = Future<void> Function(T player);

final class TransientPlayerLifecycle<T extends Object> {
  TransientPlayerLifecycle({required PlayerDisposer<T> disposePlayer})
    : _disposePlayer = disposePlayer;

  final PlayerDisposer<T> _disposePlayer;
  final Map<T, StreamSubscription<void>> _completionSubscriptions =
      <T, StreamSubscription<void>>{};
  final Map<T, Future<void>> _disposing = <T, Future<void>>{};
  final Expando<bool> _disposed = Expando<bool>();

  int get trackedCount => _completionSubscriptions.length;

  void watch(T player, Stream<void> completion) {
    if (_disposing.containsKey(player) ||
        _completionSubscriptions.containsKey(player)) {
      return;
    }
    late StreamSubscription<void> subscription;
    subscription = completion.listen((_) {
      unawaited(dispose(player));
    });
    _completionSubscriptions[player] = subscription;
  }

  Future<void> dispose(T player) {
    if (_disposed[player] == true) return Future<void>.value();
    final pending = _disposing[player];
    if (pending != null) return pending;

    final operation = _disposeAndForget(player);
    _disposing[player] = operation;
    return operation;
  }

  Future<void> _disposeAndForget(T player) async {
    try {
      await _disposeOnce(player);
      _disposed[player] = true;
    } finally {
      _disposing.remove(player);
    }
  }

  Future<void> _disposeOnce(T player) async {
    final subscription = _completionSubscriptions.remove(player);
    await subscription?.cancel();
    try {
      await _disposePlayer(player);
    } catch (_) {
      // Audio cleanup must never interrupt input release or widget disposal.
    }
  }

  Future<void> disposeAll() async {
    final players = <T>{..._completionSubscriptions.keys, ..._disposing.keys};
    await Future.wait(players.map(dispose));
  }
}
