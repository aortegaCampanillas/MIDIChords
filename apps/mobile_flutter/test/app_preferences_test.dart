import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/app_preferences.dart';

final class _MemoryPreferences implements PreferencesPort {
  _MemoryPreferences([Map<String, Object>? values])
    : values = <String, Object>{...?values};

  final Map<String, Object> values;

  @override
  bool? getBool(String key) => values[key] as bool?;
  @override
  int? getInt(String key) => values[key] as int?;
  @override
  String? getString(String key) => values[key] as String?;
  @override
  Future<void> remove(String key) async => values.remove(key);
  @override
  Future<void> setBool(String key, bool value) async => values[key] = value;
  @override
  Future<void> setInt(String key, int value) async => values[key] = value;
  @override
  Future<void> setString(String key, String value) async => values[key] = value;
}

void main() {
  test('load supplies defaults and rejects invalid bounded choices', () {
    final preferences = AppPreferencesRepository(
      _MemoryPreferences(<String, Object>{
        'scaleFingeringHand': 'middle',
        'tabIndex': 9,
      }),
    ).load();

    expect(preferences.language, 'es');
    expect(preferences.showKeyNames, isTrue);
    expect(preferences.scaleOctaves, 1);
    expect(preferences.scaleFingeringHand, isNull);
    expect(preferences.tabIndex, 0);
  });

  test('save persists the complete settings snapshot', () async {
    final port = _MemoryPreferences();
    final repository = AppPreferencesRepository(port);

    await repository.save(
      const AppPreferences(
        language: 'en',
        showKeyNames: false,
        lastSeenChangelogVersion: '1.2.3',
        changelogDontShow: true,
        scaleOctaves: 3,
        scaleFingeringHand: 'left',
        tabIndex: 4,
      ),
    );

    expect(port.values['language'], 'en');
    expect(port.values['showKeyNames'], isFalse);
    expect(port.values['lastSeenChangelogVersion'], '1.2.3');
    expect(port.values['changelogDontShow'], isTrue);
    expect(port.values['scaleOctaves'], 3);
    expect(port.values['scaleFingeringHand'], 'left');
    expect(port.values['tabIndex'], 4);
  });

  test('save removes an obsolete fingering selection', () async {
    final port = _MemoryPreferences(<String, Object>{
      'scaleFingeringHand': 'right',
    });

    await AppPreferencesRepository(
      port,
    ).save(const AppPreferences(scaleFingeringHand: null));

    expect(port.values, isNot(contains('scaleFingeringHand')));
  });
}
