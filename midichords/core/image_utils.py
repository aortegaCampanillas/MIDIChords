from __future__ import annotations

from typing import Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap


def fit_photo_image(image: QPixmap, max_w: int, max_h: int) -> QPixmap:
    """Compat: conserva el nombre pero con QPixmap/QImage."""
    w = int(image.width())
    h = int(image.height())
    if w <= 0 or h <= 0:
        return image
    if w <= max_w and h <= max_h:
        return image

    scale = min(float(max_w) / float(w), float(max_h) / float(h))
    scale = max(0.0, scale)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return image.scaled(nw, nh, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


def pad_photo_image(image: QPixmap, pad_x: int = 4, pad_y: int = 4) -> QPixmap:
    w = int(image.width())
    h = int(image.height())
    out = QPixmap(w + pad_x * 2, h + pad_y * 2)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.drawPixmap(pad_x, pad_y, image)
    painter.end()
    return out


def recolor_dark_pixels(
    image: QPixmap,
    threshold: int = 56,
    target: tuple[int, int, int] = (255, 255, 255),
) -> QPixmap:
    target_color = QColor(int(target[0]), int(target[1]), int(target[2]))
    img = image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    w = img.width()
    h = img.height()

    dark_map = [[False for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for x in range(w):
            c = QColor(img.pixel(x, y))
            if c.alpha() == 0:
                dark_map[y][x] = False
                continue
            dark_map[y][x] = c.red() <= threshold and c.green() <= threshold and c.blue() <= threshold

    for y in range(h):
        for x in range(w):
            if not dark_map[y][x]:
                continue
            has_light_neighbor = False
            for ny in range(max(0, y - 1), min(h, y + 2)):
                for nx in range(max(0, x - 1), min(w, x + 2)):
                    if nx == x and ny == y:
                        continue
                    if not dark_map[ny][nx]:
                        has_light_neighbor = True
                        break
                if has_light_neighbor:
                    break
            if has_light_neighbor:
                # Mantener alpha original.
                old = QColor(img.pixel(x, y))
                out = QColor(target_color)
                out.setAlpha(old.alpha())
                img.setPixelColor(x, y, out)

    return QPixmap.fromImage(img)


def prepare_icon_for_dark_ui(
    image: QPixmap,
    bg: tuple[int, int, int] = (43, 47, 55),
    fg: tuple[int, int, int] = (246, 246, 246),
    light_threshold: int = 232,
) -> QPixmap:
    bg_color = QColor(int(bg[0]), int(bg[1]), int(bg[2]))
    fg_color = QColor(int(fg[0]), int(fg[1]), int(fg[2]))

    img = image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    w = img.width()
    h = img.height()

    for y in range(h):
        for x in range(w):
            c = QColor(img.pixel(x, y))
            if c.alpha() == 0:
                continue
            if c.red() >= light_threshold and c.green() >= light_threshold and c.blue() >= light_threshold:
                out = QColor(bg_color)
            else:
                out = QColor(fg_color)
            out.setAlpha(c.alpha())
            img.setPixelColor(x, y, out)

    return QPixmap.fromImage(img)
