from __future__ import annotations

import tkinter as tk


def fit_photo_image(image: tk.PhotoImage, max_w: int, max_h: int) -> tk.PhotoImage:
    w = image.width()
    h = image.height()
    if w <= 0 or h <= 0:
        return image
    if w <= max_w and h <= max_h:
        return image

    best_zoom = 1
    best_sub = 1
    best_diff = float("inf")

    for zoom in range(1, 5):
        for sub in range(1, 20):
            nw = max(1, (w * zoom) // sub)
            nh = max(1, (h * zoom) // sub)
            if nw > max_w or nh > max_h:
                continue
            diff = (max_w - nw) + (max_h - nh)
            if diff < best_diff:
                best_diff = diff
                best_zoom = zoom
                best_sub = sub

    if best_zoom == 1 and best_sub == 1:
        return image.subsample(max(1, (w + max_w - 1) // max_w), max(1, (h + max_h - 1) // max_h))

    fitted = image.zoom(best_zoom, best_zoom)
    if best_sub > 1:
        fitted = fitted.subsample(best_sub, best_sub)
    return fitted


def pad_photo_image(image: tk.PhotoImage, pad_x: int = 4, pad_y: int = 4) -> tk.PhotoImage:
    w = image.width()
    h = image.height()
    out = tk.PhotoImage(width=w + pad_x * 2, height=h + pad_y * 2)
    out.tk.call(str(out), "copy", str(image), "-to", pad_x, pad_y)
    return out


def recolor_dark_pixels(image: tk.PhotoImage, threshold: int = 56, target: tuple[int, int, int] = (255, 255, 255)) -> None:
    target_hex = f"#{target[0]:02x}{target[1]:02x}{target[2]:02x}"
    w = image.width()
    h = image.height()
    dark_map = [[False for _ in range(w)] for _ in range(h)]

    for y in range(h):
        for x in range(w):
            rgb = image.get(x, y)
            if isinstance(rgb, tuple) and len(rgb) >= 3:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            elif isinstance(rgb, str) and rgb.startswith("#") and len(rgb) == 7:
                r = int(rgb[1:3], 16)
                g = int(rgb[3:5], 16)
                b = int(rgb[5:7], 16)
            else:
                continue
            dark_map[y][x] = r <= threshold and g <= threshold and b <= threshold

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
                image.put(target_hex, (x, y))


def prepare_icon_for_dark_ui(
    image: tk.PhotoImage,
    bg: tuple[int, int, int] = (43, 47, 55),
    fg: tuple[int, int, int] = (246, 246, 246),
    light_threshold: int = 232,
) -> None:
    bg_hex = f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}"
    fg_hex = f"#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"
    w = image.width()
    h = image.height()
    for y in range(h):
        for x in range(w):
            rgb = image.get(x, y)
            if isinstance(rgb, tuple) and len(rgb) >= 3:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            elif isinstance(rgb, str) and rgb.startswith("#") and len(rgb) == 7:
                r = int(rgb[1:3], 16)
                g = int(rgb[3:5], 16)
                b = int(rgb[5:7], 16)
            else:
                continue
            if r >= light_threshold and g >= light_threshold and b >= light_threshold:
                image.put(bg_hex, (x, y))
            else:
                image.put(fg_hex, (x, y))
