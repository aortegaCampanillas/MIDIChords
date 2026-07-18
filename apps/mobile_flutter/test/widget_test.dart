// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:midichords/main.dart';

void main() {
  testWidgets('App bootstrap smoke test', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 800));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    // Build our app and trigger a frame.
    await tester.pumpWidget(const MidiChordsMobileApp());
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('MIDI Piano & Guitar Chords'), findsOneWidget);
    expect(find.text('Detección de acordes'), findsOneWidget);
  });
}
