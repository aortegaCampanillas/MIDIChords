import 'dart:convert';
import 'package:flutter/services.dart';

class ChangelogItem {
  final String version;
  final String versionDate;
  final String text;
  final List<String> platforms;

  ChangelogItem({
    required this.version,
    required this.versionDate,
    required this.text,
    required this.platforms,
  });
}

class ChangelogUtils {
  static Future<List<ChangelogItem>> loadChangelogForPlatform(
    String platform,
  ) async {
    try {
      final jsonString =
          await rootBundle.loadString('assets/changelog.json');
      final List<dynamic> jsonData = json.decode(jsonString);

      final List<ChangelogItem> items = [];

      for (final versionEntry in jsonData) {
        final version = versionEntry['version'] as String? ?? 'Unknown';
        final versionDate = versionEntry['date'] as String? ?? '';
        final itemsList = versionEntry['items'] as List<dynamic>? ?? [];

        for (final item in itemsList) {
          final publish = item['publish'] as bool? ?? false;
          if (!publish) continue;

          final platforms = (item['platforms'] as List<dynamic>? ?? ['web'])
              .map((p) => p.toString())
              .toList();

          if (!platforms.contains(platform)) continue;

          final text = item['es'] as String? ??
              item['en'] as String? ??
              'No description';

          items.add(
            ChangelogItem(
              version: version,
              versionDate: versionDate,
              text: text,
              platforms: platforms,
            ),
          );
        }
      }

      return items;
    } catch (e) {
      print('Error loading changelog: $e');
      return [];
    }
  }
}
