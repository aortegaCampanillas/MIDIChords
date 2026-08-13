bool changelogItemTargetsMobile(Map<String, dynamic> item) {
  final platforms = item['platforms'];
  if (platforms == null) return true;
  if (platforms is! List) return false;
  return platforms.any((platform) => platform == 'mobile');
}
