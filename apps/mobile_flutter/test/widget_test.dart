// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:midichords/main.dart';

void main() {
  testWidgets('chord detection fits an iPhone 17 landscape viewport', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
      'tabIndex': 0,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    tester.view.physicalSize = const Size(932, 430);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    expect(find.text('Detección de Acordes'), findsWidgets);
    expect(find.text('Construcción: -', findRichText: true), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('note detection fits an iPhone 17 landscape viewport', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
      'tabIndex': 8,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    tester.view.physicalSize = const Size(932, 430);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    expect(find.text('Detección de Notas'), findsOneWidget);
    expect(find.text('Nota: -', findRichText: true), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('chord generation fits an iPhone 17 landscape viewport', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
      'tabIndex': 1,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    tester.view.physicalSize = const Size(932, 430);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    expect(find.text('Generación de Acordes'), findsOneWidget);
    expect(find.byIcon(Icons.piano), findsWidgets);
    expect(tester.takeException(), isNull);

    await tester.tap(find.byIcon(Icons.piano).last);
    await tester.pump(const Duration(milliseconds: 200));
    expect(find.text('🎸'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('changelog fits an iPhone 17 landscape viewport', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    // Ignore unrelated compact-page layout before isolating the dialog.
    tester.takeException();
    await tester.tap(find.byIcon(Icons.settings));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Novedades'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Novedades'));
    await tester.pumpAndSettle();

    expect(find.text('Novedades'), findsOneWidget);
    expect(find.text('No volver a mostrar'), findsOneWidget);
    expect(find.text('Cerrar'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('App bootstrap smoke test', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    // Build our app and trigger a frame.
    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('MIDI Piano & Guitar Chords'), findsOneWidget);
    expect(find.text('Detección de Acordes'), findsWidgets);
  });

  testWidgets('help overlay resolves visible anchors after layout', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 100));
    await tester.tap(find.byIcon(Icons.help_outline));
    await tester.pump();

    expect(find.text('Cerrar ayuda'), findsNothing);
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint &&
            widget.painter.runtimeType.toString() == '_HelpOverlayPainter',
      ),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('chord detection can hide and restore didactic details', (
    WidgetTester tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 100));

    await tester.tap(find.text('Ocultar'));
    await tester.pump();
    expect(find.text('Mostrar'), findsOneWidget);

    await tester.tap(find.text('Mostrar'));
    await tester.pump();
    expect(find.text('Ocultar'), findsOneWidget);
  });

  testWidgets('interval detection can hide and restore didactic details', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{'tabIndex': 5});
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 200));

    await tester.tap(find.text('Ocultar'));
    await tester.pump();
    expect(find.text('Mostrar'), findsOneWidget);

    await tester.tap(find.text('Mostrar'));
    await tester.pump();
    expect(find.text('Ocultar'), findsOneWidget);
  });

  testWidgets('interval detection keeps actions visible on iPhone landscape', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
      'tabIndex': 5,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    tester.view.physicalSize = const Size(932, 430);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }

    expect(find.text('Reproducir'), findsOneWidget);
    expect(find.text('Desc.'), findsOneWidget);
    expect(find.text('Limpiar'), findsOneWidget);
    expect(find.text('Ocultar'), findsOneWidget);
    expect(find.text('Ejemplo:'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('interval practice renders a visible staff panel', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{'tabIndex': 9});
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 200));

    expect(find.text('Practicar Intervalos'), findsWidgets);
    expect(find.text('Pentagrama'), findsOneWidget);
    final staff = find.byWidgetPredicate(
      (widget) =>
          widget is CustomPaint &&
          widget.painter.runtimeType.toString() == '_MiniStaffPainter',
    );
    expect(staff, findsOneWidget);
    expect(tester.getSize(staff).height, greaterThan(100));
    await tester.pump(const Duration(milliseconds: 100));
  });

  testWidgets('interval practice filter fits an iPhone 17 landscape viewport', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{
      'changelogDontShow': true,
      'tabIndex': 9,
    });
    await tester.binding.setSurfaceSize(const Size(932, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 10; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    tester.takeException();

    await tester.ensureVisible(find.text('Filtrar'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Filtrar'));
    await tester.pumpAndSettle();

    expect(find.text('Filtrar intervalos'), findsOneWidget);
    expect(find.byType(SingleChildScrollView), findsWidgets);
    expect(tester.takeException(), isNull);
  });

  testWidgets('interval generation help resolves its scrollable table', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{'tabIndex': 7});
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 200));
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.text('Generación de Intervalos'), findsWidgets);
    // The compact tonic accidental dropdown has a pre-existing 6 px overflow
    // under the synthetic test font metrics. Clear it before exercising help.
    tester.takeException();

    await tester.tap(find.byIcon(Icons.help_outline));
    await tester.pump();

    expect(find.text('Cerrar ayuda'), findsNothing);
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint &&
            widget.painter.runtimeType.toString() == '_HelpOverlayPainter',
      ),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('scales help renders tonic, accidental, and type anchors', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues(<String, Object>{'tabIndex': 3});
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(const MidiChordsMobileApp());
    for (var attempt = 0; attempt < 6; attempt += 1) {
      await tester.pump(const Duration(milliseconds: 50));
    }
    tester.takeException();

    final anchorRects = <Rect>[];
    for (final id in <String>[
      'scales_tonic',
      'scales_accidental',
      'scales_pattern',
    ]) {
      final anchor = find.byWidgetPredicate(
        (widget) =>
            widget.key != null && widget.key.toString().contains('help_$id'),
      );
      expect(anchor, findsOneWidget);
      anchorRects.add(tester.getRect(anchor));
    }

    await tester.tap(find.byIcon(Icons.help_outline));
    await tester.pump();

    expect(find.text('Cerrar ayuda'), findsNothing);
    final overlayPaint = tester.widget<CustomPaint>(
      find.byWidgetPredicate(
        (widget) =>
            widget is CustomPaint &&
            widget.painter.runtimeType.toString() == '_HelpOverlayPainter',
      ),
    );
    final targets = ((overlayPaint.painter as dynamic).targets as List<Rect>);
    for (final anchorRect in anchorRects) {
      final expected = anchorRect.inflate(2);
      expect(
        targets.any(
          (target) =>
              (target.center - expected.center).distance < 2 &&
              (target.width - expected.width).abs() < 2 &&
              (target.height - expected.height).abs() < 2,
        ),
        isTrue,
        reason: 'expected $expected among $targets',
      );
    }
    expect(tester.takeException(), isNull);
  });
}
