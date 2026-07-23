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
    expect(resolver, isNot(contains('overlayBox.debugNeedsLayout')));
    expect(resolver, isNot(contains('overlayBox.size')));
    expect(resolver, contains('_helpGlobalRectCache[id]'));
    expect(resolver, contains('viewportBox.debugNeedsLayout'));
  });

  test('scales exposes separate tonic, accidental, and type help anchors', () {
    final page = File('lib/main_pages.dart').readAsStringSync();
    final help = File('lib/main_help.dart').readAsStringSync();

    for (final id in <String>[
      'scales_tonic',
      'scales_accidental',
      'scales_pattern',
    ]) {
      expect(page, contains("'$id'"));
      expect(help, contains("id: '$id'"));
    }
  });

  test(
    'help anchors own a stable render box instead of their child layout',
    () {
      final help = File('lib/main_help.dart').readAsStringSync();
      final anchor = help
          .split('Widget _helpAnchor(')
          .last
          .split('List<_HelpStep>')
          .first;

      expect(anchor, contains('RepaintBoundary(key: _helpAnchorKey(id)'));
      expect(anchor, isNot(contains('KeyedSubtree')));
    },
  );

  test('dropdown help anchors use a fixed-height layout boundary', () {
    final help = File('lib/main_help.dart').readAsStringSync();
    final main = File('lib/main.dart').readAsStringSync();
    final pages = File('lib/main_pages.dart').readAsStringSync();

    expect(help, contains('Widget _helpFixedHeightAnchor('));
    expect(main, contains('_helpFixedHeightAnchor(helpId, child)'));
    expect(
      pages,
      contains(
        "_helpFixedHeightAnchor(\n                                'scales_pattern'",
      ),
    );
  });
}
