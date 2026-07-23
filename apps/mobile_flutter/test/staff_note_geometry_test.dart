import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/staff_note_geometry.dart';

void main() {
  test('interval notes use distinct melodic columns', () {
    expect(intervalStaffNoteX(startX: 100, index: 0, compactWidth: false), 100);
    expect(intervalStaffNoteX(startX: 100, index: 1, compactWidth: false), 164);
    expect(intervalStaffNoteX(startX: 100, index: 1, compactWidth: true), 148);
  });

  test('negative indexes remain at the first column', () {
    expect(
      intervalStaffNoteX(startX: 100, index: -1, compactWidth: false),
      100,
    );
  });
}
