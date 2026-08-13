import 'package:shared_preferences/shared_preferences.dart';

final class AppPreferences {
  const AppPreferences({
    this.language = 'es',
    this.showKeyNames = true,
    this.lastSeenChangelogVersion = '',
    this.changelogDontShow = false,
    this.scaleOctaves = 1,
    this.scaleFingeringHand,
    this.tabIndex = 0,
  });

  final String language;
  final bool showKeyNames;
  final String lastSeenChangelogVersion;
  final bool changelogDontShow;
  final int scaleOctaves;
  final String? scaleFingeringHand;
  final int tabIndex;
}

abstract interface class PreferencesPort {
  String? getString(String key);
  bool? getBool(String key);
  int? getInt(String key);
  Future<void> setString(String key, String value);
  Future<void> setBool(String key, bool value);
  Future<void> setInt(String key, int value);
  Future<void> remove(String key);
}

final class SharedPreferencesPort implements PreferencesPort {
  SharedPreferencesPort(this._preferences);

  final SharedPreferences _preferences;

  static Future<SharedPreferencesPort> create() async =>
      SharedPreferencesPort(await SharedPreferences.getInstance());

  @override
  String? getString(String key) => _preferences.getString(key);
  @override
  bool? getBool(String key) => _preferences.getBool(key);
  @override
  int? getInt(String key) => _preferences.getInt(key);
  @override
  Future<void> setString(String key, String value) async {
    await _preferences.setString(key, value);
  }

  @override
  Future<void> setBool(String key, bool value) async {
    await _preferences.setBool(key, value);
  }

  @override
  Future<void> setInt(String key, int value) async {
    await _preferences.setInt(key, value);
  }

  @override
  Future<void> remove(String key) async {
    await _preferences.remove(key);
  }
}

final class AppPreferencesRepository {
  const AppPreferencesRepository(this._port);

  final PreferencesPort _port;

  AppPreferences load() {
    final fingering = _port.getString('scaleFingeringHand');
    final savedTab = _port.getInt('tabIndex');
    return AppPreferences(
      language: _port.getString('language') ?? 'es',
      showKeyNames: _port.getBool('showKeyNames') ?? true,
      lastSeenChangelogVersion:
          _port.getString('lastSeenChangelogVersion') ?? '',
      changelogDontShow: _port.getBool('changelogDontShow') ?? false,
      scaleOctaves: _port.getInt('scaleOctaves') ?? 1,
      scaleFingeringHand: fingering == 'left' || fingering == 'right'
          ? fingering
          : null,
      tabIndex: savedTab != null && savedTab >= 0 && savedTab <= 9
          ? savedTab
          : 0,
    );
  }

  Future<void> save(AppPreferences preferences) async {
    await _port.setString('language', preferences.language);
    await _port.setBool('showKeyNames', preferences.showKeyNames);
    await _port.setString(
      'lastSeenChangelogVersion',
      preferences.lastSeenChangelogVersion,
    );
    await _port.setBool('changelogDontShow', preferences.changelogDontShow);
    await _port.setInt('scaleOctaves', preferences.scaleOctaves);
    final fingering = preferences.scaleFingeringHand;
    if (fingering == null) {
      await _port.remove('scaleFingeringHand');
    } else {
      await _port.setString('scaleFingeringHand', fingering);
    }
    await _port.setInt('tabIndex', preferences.tabIndex);
  }
}
