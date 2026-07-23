import 'package:flutter/widgets.dart';

Rect visibleHelpRect({
  required Rect target,
  required Rect overlayBounds,
  Iterable<Rect> viewportBounds = const <Rect>[],
}) {
  var visible = target.intersect(overlayBounds);
  for (final viewport in viewportBounds) {
    visible = visible.intersect(viewport);
    if (visible.isEmpty) break;
  }
  return visible;
}
