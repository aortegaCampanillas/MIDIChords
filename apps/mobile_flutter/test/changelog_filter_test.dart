import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/changelog_filter.dart';

void main() {
  test('mobile changelog excludes entries for other platforms', () {
    expect(
      changelogItemTargetsMobile(<String, dynamic>{
        'platforms': <String>['desktop'],
      }),
      isFalse,
    );
    expect(
      changelogItemTargetsMobile(<String, dynamic>{
        'platforms': <String>['web', 'mobile'],
      }),
      isTrue,
    );
  });

  test('legacy entries without platforms remain visible', () {
    expect(changelogItemTargetsMobile(<String, dynamic>{}), isTrue);
    expect(
      changelogItemTargetsMobile(<String, dynamic>{'platforms': 'desktop'}),
      isFalse,
    );
  });
}
