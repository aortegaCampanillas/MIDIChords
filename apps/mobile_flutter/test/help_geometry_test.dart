import 'dart:io';
import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/help_geometry.dart';

void main() {
  test('clips help targets to the visible part of a scroll viewport', () {
    final visible = visibleHelpRect(
      target: const Rect.fromLTWH(20, 80, 300, 240),
      overlayBounds: const Rect.fromLTWH(0, 0, 800, 600),
      viewportBounds: const <Rect>[Rect.fromLTWH(10, 50, 400, 130)],
    );

    expect(visible, const Rect.fromLTWH(20, 80, 300, 100));
  });

  test('clips through nested horizontal and vertical viewports', () {
    final visible = visibleHelpRect(
      target: const Rect.fromLTWH(50, 50, 700, 300),
      overlayBounds: const Rect.fromLTWH(0, 0, 600, 400),
      viewportBounds: const <Rect>[
        Rect.fromLTWH(100, 0, 350, 400),
        Rect.fromLTWH(0, 100, 600, 120),
      ],
    );

    expect(visible, const Rect.fromLTWH(100, 100, 350, 120));
  });

  test('help geometry ignores render boxes that still need layout', () {
    final source = File('lib/main_help.dart').readAsStringSync();
    final resolver = source
        .split('Rect? _helpRectFor(')
        .last
        .split('List<_ResolvedHelpStep>')
        .first;

    expect(resolver, contains('targetBox.debugNeedsLayout'));
    expect(resolver, contains('overlayBox.debugNeedsLayout'));
    expect(resolver, contains('viewportBox.debugNeedsLayout'));
  });
}
