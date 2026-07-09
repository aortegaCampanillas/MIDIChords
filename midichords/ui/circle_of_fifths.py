"""
Círculo de quintas — dibujo y geometría alineados con `apps/web/static/app.js`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Optional

from PySide6.QtGui import QFont, QFontMetrics

import midichords.qt.tk_compat as tk

CIRCLE_FIFTHS_ORDER = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]


def _fit_font_size_for_slice(text: str, base_size: int, radius: float, min_size: int, font_family: str) -> int:
    """Encoge `base_size` si `text` no cabe en el ancho disponible del sector a ese
    radio (p. ej. "Sol#m" en el anillo menor, más estrecho que el mayor). Mide el
    ancho real con QFontMetrics (la etiqueta se dibuja en negrita, que es más ancha
    por carácter que el texto regular/cursiva de otros sitios de la UI — un
    estimador por número de caracteres calibrado en otro contexto no vale aquí)."""
    if not text or radius <= 0:
        return base_size
    half_angle = CIRCLE_SLICE_RAD / 2
    avail_width = 2 * radius * math.sin(half_angle) * 0.88
    font = QFont(font_family, base_size)
    font.setBold(True)
    est_width = QFontMetrics(font).horizontalAdvance(text)
    if est_width <= avail_width or est_width <= 0:
        return base_size
    size = max(min_size, int(math.floor(base_size * (avail_width / est_width))))
    # El escalado lineal es aproximado (hinting/redondeo de la fuente); afinar
    # bajando de 1 en 1 hasta que el ancho medido quepa de verdad.
    font.setPointSize(size)
    while size > min_size and QFontMetrics(font).horizontalAdvance(text) > avail_width:
        size -= 1
        font.setPointSize(size)
    return size


def _qt_canvas_polyline(canvas: tk.Canvas, flat: list[float], **kwargs: Any) -> None:
    """QtCanvas.create_line solo admite un segmento; Tk acepta muchos puntos en un create_line."""
    if len(flat) < 4:
        return
    kw = {k: v for k, v in kwargs.items() if k != "join"}
    for i in range(0, len(flat) - 2, 2):
        canvas.create_line(flat[i], flat[i + 1], flat[i + 2], flat[i + 3], **kw)

DIATONIC_DEGREE_SUFFIX = {0: "", 2: "m", 4: "m", 5: "", 7: "", 9: "m", 11: "dim"}

ROMAN_BY_DEGREE = {
    0: "I",
    2: "ii",
    4: "iii",
    5: "IV",
    7: "V",
    9: "vi",
    11: "vii°",
}

ROMAN_BY_MINOR_NATURAL_INTERVAL = {
    0: "i",
    2: "ii°",
    3: "\u266DIII",
    5: "iv",
    7: "v",
    8: "\u266DVI",
    10: "\u266DVII",
}

CIRCLE_DEGREE_FILL = {
    0: {"base": "#f0d5b8", "tonic": "#c9a06a"},
    2: "#ddd0e8",
    4: "#ddd0e8",
    5: "#f0d5b8",
    7: "#f0d5b8",
    9: "#ddd0e8",
    11: "#f5d4dc",
}

CIRCLE_DEGREE_TEXT = {
    0: "#1b5e20",
    2: "#0d47a1",
    4: "#b71c1c",
    5: "#1565c0",
    7: "#c62828",
    9: "#2e7d32",
    11: "#c62828",
}

CIRCLE_SLICE_RAD = (math.pi * 2) / 12


def _mod12(x: int) -> int:
    return int(x) % 12


def diatonic_triad_suffix_major_key(tonic_pc: int, root_pc: int) -> tuple[str, Optional[int]]:
    d = (root_pc - tonic_pc + 12) % 12
    if d in DIATONIC_DEGREE_SUFFIX:
        return DIATONIC_DEGREE_SUFFIX[d], d
    return "", None


def diatonic_triad_suffix_natural_minor_key(minor_tonic_pc: int, root_pc: int) -> tuple[str, Optional[int], str]:
    d = (root_pc - minor_tonic_pc + 12) % 12
    _map = {
        0: ("m", 0, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(0, "")),
        2: ("dim", 2, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(2, "")),
        3: ("", 3, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(3, "")),
        5: ("m", 5, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(5, "")),
        7: ("m", 7, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(7, "")),
        8: ("", 8, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(8, "")),
        10: ("", 10, ROMAN_BY_MINOR_NATURAL_INTERVAL.get(10, "")),
    }
    if d not in _map:
        return "", None, ""
    suf, iv, rom = _map[d]
    return suf, iv, rom


def chord_root_pc_for_major_scale_degree(tonic_pc: int, degree: int) -> int:
    inter = {0: 0, 2: 2, 4: 4, 5: 5, 7: 7, 9: 9, 11: 11}
    return _mod12(tonic_pc + inter.get(degree, 0))


def relative_minor_pc_from_major_pc(major_pc: int) -> int:
    return _mod12(int(major_pc) + 9)


def circle_slice_angles(i: int) -> tuple[float, float, float]:
    mid = (-math.pi / 2) + (i * CIRCLE_SLICE_RAD)
    half = CIRCLE_SLICE_RAD / 2
    return mid, mid - half, mid + half


def circle_slice_index_for_pitch_class(pc: int) -> int:
    p = _mod12(pc)
    for i in range(12):
        if CIRCLE_FIFTHS_ORDER[i] == p:
            return i
    return 0


def circle_fifths_radii_px(w: float, h: float) -> dict[str, float]:
    r_outer = min(w, h) * 0.46
    r_hole = r_outer * 0.18
    r_guide_sig_maj_ref = r_outer * 0.775
    band_sig = (r_outer - r_guide_sig_maj_ref) / 2
    r_sig_inner = r_outer - band_sig
    r_sig = (r_outer + r_sig_inner) / 2
    r_guide_maj_min = r_outer * 0.52
    return {
        "r_outer": r_outer,
        "r_hole": r_hole,
        "r_sig_inner": r_sig_inner,
        "r_sig": r_sig,
        "r_maj_name": r_outer * 0.72,
        "r_maj_roman": r_outer * 0.60,
        "r_min": r_outer * 0.38,
        "r_min_roman": r_outer * 0.292,
        "r_guide_sig_maj": r_sig_inner,
        "r_guide_maj_min": r_guide_maj_min,
    }


def circle_upper_band_is_diatonic_major_triad(degree: int) -> bool:
    return degree in (0, 5, 7)


def circle_lower_band_is_diatonic_minor_triad(minor_deg: int) -> bool:
    return minor_deg in (2, 4, 9)


def circle_minor_interval_to_major_degree_key(interval_d: int) -> int:
    m = {0: 0, 2: 11, 3: 4, 5: 5, 7: 7, 8: 9, 10: 9}
    return m.get(interval_d, 0)


def circle_diatonic_slice_fill(degree: int, pc: int, tonic_pc: int) -> str:
    if degree == 0:
        return CIRCLE_DEGREE_FILL[0]["tonic"] if pc == tonic_pc else CIRCLE_DEGREE_FILL[0]["base"]
    return str(CIRCLE_DEGREE_FILL[degree])


def circle_signature_label_for_slice_index(i: int) -> str:
    if i <= 6:
        return "0" if i == 0 else f"{i}♯"
    return f"{12 - i}♭"


def circle_major_tonic_pc_for_theory(circle_tonic_pc: int, circle_key_mode: str) -> int:
    t = _mod12(circle_tonic_pc)
    if circle_key_mode == "minor":
        return _mod12(t + 3)
    return t


def circle_slice_index_from_canvas(cx: float, cy: float, x: float, y: float) -> int:
    dx = x - cx
    dy = y - cy
    a = math.atan2(dy, dx)
    t = (a + math.pi / 2 + math.pi * 2) % (math.pi * 2)
    return int((t + CIRCLE_SLICE_RAD / 2) / CIRCLE_SLICE_RAD) % 12


def circle_fifths_click_inner_minor_band(
    canvas_w: float,
    canvas_h: float,
    cx: float,
    cy: float,
    x: float,
    y: float,
) -> Optional[bool]:
    dx = x - cx
    dy = y - cy
    dist = math.hypot(dx, dy)
    rad = circle_fifths_radii_px(canvas_w, canvas_h)
    r_outer = rad["r_outer"]
    r_hole = rad["r_hole"]
    r_guide_maj_min = rad["r_guide_maj_min"]
    if dist < r_hole * 1.02 or dist > r_outer * 1.02:
        return None
    return dist < r_guide_maj_min


def circle_chord_root_pc_from_click(
    canvas_w: float,
    canvas_h: float,
    cx: float,
    cy: float,
    x: float,
    y: float,
    shift_key: bool,
) -> Optional[int]:
    dx = x - cx
    dy = y - cy
    dist = math.hypot(dx, dy)
    rad = circle_fifths_radii_px(canvas_w, canvas_h)
    r_outer = rad["r_outer"]
    r_hole = rad["r_hole"]
    r_guide_maj_min = rad["r_guide_maj_min"]
    if dist < r_hole * 1.02 or dist > r_outer * 1.02:
        return None
    idx = circle_slice_index_from_canvas(cx, cy, x, y)
    major_pc = CIRCLE_FIFTHS_ORDER[idx]
    if not shift_key:
        if dist < r_guide_maj_min:
            return _mod12(major_pc + 9)
        return _mod12(major_pc)
    if dist < r_guide_maj_min:
        return _mod12(major_pc + 9)
    return _mod12(major_pc)


def circle_chord_shift_click_is_diatonic(
    tonic_pc: int,
    canvas_w: float,
    canvas_h: float,
    cx: float,
    cy: float,
    x: float,
    y: float,
    *,
    circle_key_mode: str,
    circle_tonic_pc: int,
) -> bool:
    dx = x - cx
    dy = y - cy
    dist = math.hypot(dx, dy)
    rad = circle_fifths_radii_px(canvas_w, canvas_h)
    r_outer = rad["r_outer"]
    r_hole = rad["r_hole"]
    r_guide_maj_min = rad["r_guide_maj_min"]
    if dist < r_hole * 1.02 or dist > r_outer * 1.02:
        return False
    idx = circle_slice_index_from_canvas(cx, cy, x, y)
    major_pc = CIRCLE_FIFTHS_ORDER[idx]
    inner_minor_band = dist < r_guide_maj_min
    if circle_key_mode == "minor":
        minor_tonic = _mod12(circle_tonic_pc)
        if not inner_minor_band:
            d_u = (major_pc - minor_tonic + 12) % 12
            return d_u in (3, 8, 10)
        root_minor = _mod12(major_pc + 9)
        _s, iv, _r = diatonic_triad_suffix_natural_minor_key(minor_tonic, root_minor)
        return iv is not None
    vii_root_pc = chord_root_pc_for_major_scale_degree(tonic_pc, 11)
    vii_label_slice_pc = _mod12(vii_root_pc + 3)
    if not inner_minor_band:
        _suf, deg = diatonic_triad_suffix_major_key(tonic_pc, major_pc)
        return deg is not None and circle_upper_band_is_diatonic_major_triad(deg)
    root_minor = _mod12(major_pc + 9)
    _suf_m, minor_deg = diatonic_triad_suffix_major_key(tonic_pc, root_minor)
    if minor_deg is not None and circle_lower_band_is_diatonic_minor_triad(minor_deg):
        return True
    if minor_deg == 11 and major_pc == vii_label_slice_pc:
        return True
    return False


@dataclass
class CircleDrawState:
    circle_tonic_pc: int
    circle_key_mode: str
    circle_chord_root_pc: int
    generated_chord: Optional[dict[str, Any]]


def circle_chord_highlight_geom(
    tonic_pc: int,
    chord_root_pc: int,
    generated_chord: Optional[dict[str, Any]],
    circle_key_mode: str,
    circle_tonic_pc: int,
) -> tuple[int, str]:
    root_from_state = _mod12(chord_root_pc)
    root_from_api = None
    if generated_chord and generated_chord.get("root_pc") is not None:
        root_from_api = _mod12(int(generated_chord["root_pc"]))
    root = root_from_api if root_from_api is not None else root_from_state
    suffix = ""
    if generated_chord and generated_chord.get("suffix") is not None:
        suffix = str(generated_chord.get("suffix") or "")
    if suffix in ("", "undefined"):
        if circle_key_mode == "minor":
            mt = _mod12(circle_tonic_pc)
            suf, _iv, _r = diatonic_triad_suffix_natural_minor_key(mt, root)
            suffix = suf or ""
        else:
            _suf, _deg = diatonic_triad_suffix_major_key(tonic_pc, root)
            suffix = _suf or ""
    if suffix == "m":
        rel_maj_pc = _mod12(root - 9)
        return circle_slice_index_for_pitch_class(rel_maj_pc), "minor"
    if suffix == "dim":
        rel_maj_pc = _mod12(root + 3)
        return circle_slice_index_for_pitch_class(rel_maj_pc), "minor"
    return circle_slice_index_for_pitch_class(root), "major"


def _annular_wedge_points(cx: float, cy: float, r_in: float, r_out: float, a0: float, a1: float, steps: int = 20) -> list[float]:
    pts: list[float] = []
    for i in range(steps + 1):
        t = i / steps
        a = a0 + (a1 - a0) * t
        pts.extend([cx + r_out * math.cos(a), cy + r_out * math.sin(a)])
    for i in range(steps + 1):
        t = i / steps
        a = a1 - (a1 - a0) * t
        pts.extend([cx + r_in * math.cos(a), cy + r_in * math.sin(a)])
    return pts


def _circle_path_arc_short_points(r: float, from_ang: float, to_ang: float) -> list[tuple[float, float]]:
    delta = math.atan2(math.sin(to_ang - from_ang), math.cos(to_ang - from_ang))
    n = max(8, min(64, int(math.ceil(48 * abs(delta) / (math.pi * 2)))))
    out: list[tuple[float, float]] = []
    for j in range(1, n + 1):
        t = j / n
        ang = from_ang + delta * t
        out.append((math.cos(ang) * r, math.sin(ang) * r))
    return out


def _stroke_circle_chord_selection_band(
    canvas: tk.Canvas,
    cx: float,
    cy: float,
    r_out: float,
    r_in: float,
    a0: float,
    a1: float,
    width: float,
    tag: str,
) -> None:
    pts: list[float] = []
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        a = a0 + (a1 - a0) * t
        pts.extend([cx + r_out * math.cos(a), cy + r_out * math.sin(a)])
    for i in range(steps + 1):
        t = i / steps
        a = a1 - (a1 - a0) * t
        pts.extend([cx + r_in * math.cos(a), cy + r_in * math.sin(a)])
    canvas.create_polygon(pts, outline="#f2bf2f", fill="", width=int(width), tags=tag)


def _stroke_diatonic_envelope(
    canvas: tk.Canvas,
    cx: float,
    cy: float,
    tonic_pc: int,
    r_sig_inner: float,
    r_guide_maj_min: float,
    r_hole: float,
    circle_key_mode: str,
    circle_tonic_pc: int,
    line_width: float,
    tag: str,
) -> None:
    r_list = [r_hole, r_guide_maj_min, r_sig_inner]
    cell = [[False, False] for _ in range(12)]
    minor_mode = circle_key_mode == "minor"
    minor_tonic = _mod12(circle_tonic_pc) if minor_mode else None

    if minor_mode and minor_tonic is not None:
        ii_dim_root = _mod12(minor_tonic + 2)
        ii_label_pc = _mod12(ii_dim_root + 3)
        for s in range(12):
            pc = CIRCLE_FIFTHS_ORDER[s]
            mpc_rel = relative_minor_pc_from_major_pc(pc)
            d_u = (pc - minor_tonic + 12) % 12
            if d_u in (3, 8, 10):
                cell[s][1] = True
            d_l = (mpc_rel - minor_tonic + 12) % 12
            if d_l in (0, 5, 7):
                cell[s][0] = True
            elif pc == ii_label_pc:
                cell[s][0] = True
    else:
        vii_root_pc = chord_root_pc_for_major_scale_degree(tonic_pc, 11)
        vii_label_slice_pc = _mod12(vii_root_pc + 3)
        for s in range(12):
            pc = CIRCLE_FIFTHS_ORDER[s]
            _suf, deg = diatonic_triad_suffix_major_key(tonic_pc, pc)
            mpc_rel = relative_minor_pc_from_major_pc(pc)
            _suf_m, minor_deg = diatonic_triad_suffix_major_key(tonic_pc, mpc_rel)
            if deg is not None and circle_upper_band_is_diatonic_major_triad(deg):
                cell[s][1] = True
            if minor_deg is not None and circle_lower_band_is_diatonic_minor_triad(minor_deg):
                cell[s][0] = True
            elif deg is not None and pc == vii_label_slice_pc:
                cell[s][0] = True

    def v_key(k: int, r_band: int) -> str:
        return f"{k}|{r_band}"

    def vertex_xy(key: str) -> tuple[float, float, float, float]:
        ks, rs = key.split("|")
        k = int(ks)
        r_band = int(rs)
        _mid, a0, _a1 = circle_slice_angles(k)
        rad = r_list[r_band]
        return math.cos(a0) * rad, math.sin(a0) * rad, a0, rad

    edge_set: set[str] = set()

    def toggle_edge(eid: str) -> None:
        if eid in edge_set:
            edge_set.remove(eid)
        else:
            edge_set.add(eid)

    for s in range(12):
        for b in range(2):
            if not cell[s][b]:
                continue
            ri, ro = b, b + 1
            toggle_edge(f"arc|{s}|{ro}")
            toggle_edge(f"arc|{s}|{ri}")
            toggle_edge(f"rad|{s}|{ri}|{ro}")
            toggle_edge(f"rad|{(s + 1) % 12}|{ri}|{ro}")

    adj: dict[str, list[str]] = {}
    seg_by_endpoints: dict[str, dict[str, Any]] = {}

    def add_adj(a: str, b: str) -> None:
        adj.setdefault(a, []).append(b)

    def undir_key(a: str, b: str) -> str:
        return f"{a}↔{b}" if a < b else f"{b}↔{a}"

    for eid in edge_set:
        parts = eid.split("|")
        typ = parts[0]
        if typ == "arc":
            s = int(parts[1])
            r_band = int(parts[2])
            k0 = v_key(s, r_band)
            k1 = v_key((s + 1) % 12, r_band)
            _mid, a0, a1 = circle_slice_angles(s)
            add_adj(k0, k1)
            add_adj(k1, k0)
            seg_by_endpoints[undir_key(k0, k1)] = {"kind": "arc", "r": r_list[r_band], "a0": a0, "a1": a1}
        else:
            k = int(parts[1])
            ri = int(parts[2])
            ro = int(parts[3])
            ka = v_key(k, ri)
            kb = v_key(k, ro)
            _mid, ang, _a1 = circle_slice_angles(k)
            add_adj(ka, kb)
            add_adj(kb, ka)
            seg_by_endpoints[undir_key(ka, kb)] = {"kind": "rad", "ang": ang, "r0": r_list[ri], "r1": r_list[ro]}

    if minor_mode and minor_tonic is not None:
        iv_major_pc = _mod12(minor_tonic + 8)
        iv_idx = circle_slice_index_for_pitch_class(iv_major_pc)
    else:
        iv_idx = circle_slice_index_for_pitch_class(chord_root_pc_for_major_scale_degree(tonic_pc, 5))

    start_key = v_key(iv_idx, 2)
    if start_key not in adj or not adj[start_key]:
        return

    first_neighbor = v_key((iv_idx + 1) % 12, 2)
    path = [start_key]
    cur = start_key
    prev: Optional[str] = None
    max_steps = len(edge_set) * 4 + 24
    for _step in range(max_steps):
        neigh = [n for n in adj.get(cur, []) if n != prev]
        if not neigh:
            break
        if prev is None:
            next_k = first_neighbor if first_neighbor in neigh else neigh[0]
        else:
            next_k = neigh[0]
        prev = cur
        cur = next_k
        path.append(cur)
        if cur == start_key:
            break

    flat: list[float] = []
    p0x, p0y, _, _ = vertex_xy(path[0])
    flat.extend([cx + p0x, cy + p0y])
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        seg = seg_by_endpoints.get(undir_key(a, b))
        if not seg:
            continue
        if seg["kind"] == "arc":
            va_x, va_y, va_ang, _ = vertex_xy(a)
            vb_x, vb_y, vb_ang, _ = vertex_xy(b)
            for px, py in _circle_path_arc_short_points(seg["r"], va_ang, vb_ang):
                flat.extend([cx + px, cy + py])
        else:
            vbx, vby, _, _ = vertex_xy(b)
            flat.extend([cx + vbx, cy + vby])

    if len(flat) >= 4:
        _qt_canvas_polyline(
            canvas,
            flat,
            fill="#0a0a0a",
            width=line_width,
            capstyle=tk.ROUND,
            tags=tag,
        )


def _draw_roman_maybe_flat(
    canvas: tk.Canvas,
    cx: float,
    cy: float,
    roman: str,
    font_family: str,
    fs_roman: int,
    fill: str,
    tag: str,
) -> None:
    if not roman:
        return
    flat_ch = "\u266D"
    if not roman.startswith(flat_ch):
        canvas.create_text(cx, cy, text=roman, fill=fill, font=(font_family, fs_roman), tags=tag)
        return
    body = roman[1:]
    sup_fs = max(7, int(round(fs_roman * 0.58)))
    rise = int(round(fs_roman * 0.4))
    # Centrar el grupo ♭ + espacio + numeral; hueco explícito para que no se solapen (antes: numeral en cx+8 fijo).
    gap = max(3, int(round(fs_roman * 0.14)))
    try:
        from midichords.qt.tkfont_compat import Font

        w_flat = Font(family=font_family, size=sup_fs).measure(flat_ch)
        w_body = Font(family=font_family, size=fs_roman).measure(body)
    except Exception:
        w_flat = max(1, int(round(sup_fs * 0.55)))
        w_body = max(1, int(round(fs_roman * 0.55 * len(body))))
    total = w_flat + gap + w_body
    x0 = cx - total / 2.0
    canvas.create_text(
        x0,
        cy - rise,
        text=flat_ch,
        fill=fill,
        font=(font_family, sup_fs),
        anchor="w",
        tags=tag,
    )
    canvas.create_text(
        x0 + w_flat + gap,
        cy,
        text=body,
        fill=fill,
        font=(font_family, fs_roman),
        anchor="w",
        tags=tag,
    )


def draw_circle_of_fifths(
    canvas: tk.Canvas,
    *,
    width: int,
    height: int,
    state: CircleDrawState,
    note_name_fn: Callable[[int], str],
    font_family: str,
    tag: str = "circle_fifths",
) -> None:
    canvas.delete(tag)
    w, h = float(width), float(height)
    cx, cy = w / 2, h / 2
    rad = circle_fifths_radii_px(w, h)
    r_outer = rad["r_outer"]
    r_hole = rad["r_hole"]
    r_sig_inner = rad["r_sig_inner"]
    r_sig = rad["r_sig"]
    r_maj_name = rad["r_maj_name"]
    r_maj_roman = rad["r_maj_roman"]
    r_min = rad["r_min"]
    r_min_roman = rad["r_min_roman"]
    r_guide_maj_min = rad["r_guide_maj_min"]
    r_guide_sig_maj = rad["r_guide_sig_maj"]

    tonic = circle_major_tonic_pc_for_theory(state.circle_tonic_pc, state.circle_key_mode)
    chord_root = _mod12(state.circle_chord_root_pc)
    vii_root_pc = chord_root_pc_for_major_scale_degree(tonic, 11)
    vii_label_slice_pc = _mod12(vii_root_pc + 3)
    minor_mode = state.circle_key_mode == "minor"
    minor_tonic = _mod12(state.circle_tonic_pc) if minor_mode else None
    rel_maj_from_minor = _mod12(minor_tonic + 3) if minor_tonic is not None else None
    ii_dim_root_minor = _mod12(minor_tonic + 2) if minor_tonic is not None else None
    ii_label_pc_minor = _mod12(ii_dim_root_minor + 3) if ii_dim_root_minor is not None else None

    # Anillo de armadura: tamaño similar; nombres de acordes un poco más pequeños para que quepan (p. ej. Re#m).
    fs_sig = max(10, min(24, int(round(0.026 * w))))
    _nm = 0.88
    fs_maj_base = max(12, min(28, int(round(0.036 * w * _nm))))
    fs_maj_r = max(11, min(25, int(round(0.03 * w * _nm))))
    fs_min_base = max(11, min(26, int(round(0.034 * w * _nm))))
    fs_min_r = max(10, min(23, int(round(0.028 * w * _nm))))

    canvas.create_rectangle(0, 0, w, h, fill="#1a2330", outline="", tags=tag)

    sig_ring_fill = "#ffffff"
    sig_ring_stroke = "#c8cdd7"
    gray_fill = "#3d4658"

    for i in range(12):
        pc = CIRCLE_FIFTHS_ORDER[i]
        _mid, a0, a1 = circle_slice_angles(i)
        mpc_rel = relative_minor_pc_from_major_pc(pc)
        upper_fill = gray_fill
        lower_fill = gray_fill
        if minor_mode and minor_tonic is not None and rel_maj_from_minor is not None:
            d_u = (pc - minor_tonic + 12) % 12
            if d_u in (3, 8, 10):
                mk = circle_minor_interval_to_major_degree_key(d_u)
                upper_fill = circle_diatonic_slice_fill(mk, pc, rel_maj_from_minor)
            d_l = (mpc_rel - minor_tonic + 12) % 12
            if d_l in (0, 5, 7):
                mk = circle_minor_interval_to_major_degree_key(d_l)
                lower_fill = (
                    circle_diatonic_slice_fill(0, pc, rel_maj_from_minor)
                    if d_l == 0
                    else circle_diatonic_slice_fill(mk, mpc_rel, tonic)
                )
            elif ii_label_pc_minor is not None and pc == ii_label_pc_minor and ii_dim_root_minor is not None:
                lower_fill = circle_diatonic_slice_fill(11, ii_dim_root_minor, tonic)
        else:
            _suf, deg = diatonic_triad_suffix_major_key(tonic, pc)
            _suf_m, minor_deg = diatonic_triad_suffix_major_key(tonic, mpc_rel)
            diatonic = deg is not None
            if diatonic and deg is not None and circle_upper_band_is_diatonic_major_triad(deg):
                upper_fill = circle_diatonic_slice_fill(deg, pc, tonic)
            if minor_deg is not None and circle_lower_band_is_diatonic_minor_triad(minor_deg):
                lower_fill = circle_diatonic_slice_fill(minor_deg, mpc_rel, tonic)
            elif diatonic and deg is not None and pc == vii_label_slice_pc:
                lower_fill = circle_diatonic_slice_fill(11, vii_root_pc, tonic)

        pts_sig = _annular_wedge_points(cx, cy, r_sig_inner, r_outer, a0, a1)
        canvas.create_polygon(pts_sig, fill=sig_ring_fill, outline=sig_ring_stroke, width=1, tags=tag)
        pts_up = _annular_wedge_points(cx, cy, r_guide_maj_min, r_sig_inner, a0, a1)
        canvas.create_polygon(pts_up, fill=upper_fill, outline="", tags=tag)
        pts_lo = _annular_wedge_points(cx, cy, r_hole, r_guide_maj_min, a0, a1)
        canvas.create_polygon(pts_lo, fill=lower_fill, outline="", tags=tag)

    for rg in (r_guide_sig_maj, r_guide_maj_min):
        canvas.create_oval(cx - rg, cy - rg, cx + rg, cy + rg, outline="#e2e8f247", width=1, tags=tag)
    canvas.create_oval(cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole, outline="#e2e8f266", width=1, tags=tag)

    for ri in range(12):
        _mid, _a0, a1 = circle_slice_angles(ri)
        ca, sa = math.cos(a1), math.sin(a1)
        canvas.create_line(
            cx + r_hole * ca,
            cy + r_hole * sa,
            cx + r_outer * ca,
            cy + r_outer * sa,
            fill="#ffffffe6",
            width=1,
            capstyle=tk.ROUND,
            tags=tag,
        )

    _stroke_diatonic_envelope(
        canvas,
        cx,
        cy,
        tonic,
        r_sig_inner,
        r_guide_maj_min,
        r_hole,
        state.circle_key_mode,
        state.circle_tonic_pc,
        max(4.0, 4.8),
        tag,
    )

    hl_idx, hl_band = circle_chord_highlight_geom(
        tonic,
        chord_root,
        state.generated_chord,
        state.circle_key_mode,
        state.circle_tonic_pc,
    )
    _mid, ha0, ha1 = circle_slice_angles(hl_idx)
    sel_inset = 3.2
    r_hi_out = r_sig_inner - sel_inset
    r_hi_in = r_guide_maj_min + sel_inset
    if hl_band == "minor":
        r_hi_out = r_guide_maj_min - sel_inset
        r_hi_in = r_hole + sel_inset
    _stroke_circle_chord_selection_band(canvas, cx, cy, r_hi_out, r_hi_in, ha0, ha1, max(2.5, 3.0), tag)

    def circle_minor_label(major_pc: int) -> str:
        mpc = relative_minor_pc_from_major_pc(major_pc)
        return f"{note_name_fn(mpc)}m"

    for i in range(12):
        pc = CIRCLE_FIFTHS_ORDER[i]
        mid, _a0, _a1 = circle_slice_angles(i)
        mpc_rel = relative_minor_pc_from_major_pc(pc)
        cos, sin = math.cos(mid), math.sin(mid)
        sig_label = circle_signature_label_for_slice_index(i)
        major_name = note_name_fn(pc)
        minor_name = circle_minor_label(pc)
        # Nombres largos (p. ej. "Sol#m") no caben en el anillo menor (más estrecho
        # que el mayor al mismo radio angular); encoger por etiqueta si hace falta.
        # fs_maj/fs_min quedan reasignados para esta vuelta; el resto del cuerpo del
        # bucle ya usa estas variables en cada `font=(...)`, así que no hace falta
        # tocar cada create_text por separado.
        fs_maj = _fit_font_size_for_slice(major_name, fs_maj_base, r_maj_name, 8, font_family)
        fs_min = _fit_font_size_for_slice(minor_name, fs_min_base, r_min, 8, font_family)
        canvas.create_text(
            cx + cos * r_sig,
            cy + sin * r_sig,
            text=sig_label,
            fill="#0d0d0d",
            font=(font_family, fs_sig, "bold"),
            tags=tag,
        )
        if minor_mode and minor_tonic is not None:
            d_u = (pc - minor_tonic + 12) % 12
            d_l = (mpc_rel - minor_tonic + 12) % 12
            has_upper = d_u in (3, 8, 10)
            has_lower = d_l in (0, 5, 7)
            is_ii_dim = ii_label_pc_minor is not None and pc == ii_label_pc_minor
            if has_upper:
                mk = circle_minor_interval_to_major_degree_key(d_u)
                fill_t = CIRCLE_DEGREE_TEXT.get(mk, "#a8b0bd")
                canvas.create_text(
                    cx + cos * r_maj_name,
                    cy + sin * r_maj_name,
                    text=major_name,
                    fill=fill_t,
                    font=(font_family, fs_maj, "bold"),
                    tags=tag,
                )
                rtxt = ROMAN_BY_MINOR_NATURAL_INTERVAL.get(d_u, "")
                _draw_roman_maybe_flat(
                    canvas,
                    cx + cos * r_maj_roman,
                    cy + sin * r_maj_roman,
                    rtxt,
                    font_family,
                    fs_maj_r,
                    fill_t,
                    tag,
                )
            else:
                canvas.create_text(
                    cx + cos * r_maj_name,
                    cy + sin * r_maj_name,
                    text=major_name,
                    fill="#a8b0bd",
                    font=(font_family, fs_maj, "bold"),
                    tags=tag,
                )
            if is_ii_dim and ii_dim_root_minor is not None:
                dim_lbl = f"{note_name_fn(ii_dim_root_minor)}°"
                fs_dim = _fit_font_size_for_slice(dim_lbl, fs_min_base, r_outer * 0.405, 8, font_family)
                canvas.create_text(
                    cx + cos * (r_outer * 0.405),
                    cy + sin * (r_outer * 0.405),
                    text=dim_lbl,
                    fill=CIRCLE_DEGREE_TEXT[11],
                    font=(font_family, fs_dim, "bold"),
                    tags=tag,
                )
                _draw_roman_maybe_flat(
                    canvas,
                    cx + cos * r_min_roman,
                    cy + sin * r_min_roman,
                    ROMAN_BY_MINOR_NATURAL_INTERVAL.get(2, ""),
                    font_family,
                    fs_min_r,
                    CIRCLE_DEGREE_TEXT[11],
                    tag,
                )
            elif has_lower:
                mk = circle_minor_interval_to_major_degree_key(d_l)
                fill_b = CIRCLE_DEGREE_TEXT.get(mk, "#8b95a3")
                canvas.create_text(
                    cx + cos * r_min,
                    cy + sin * r_min,
                    text=minor_name,
                    fill=fill_b,
                    font=(font_family, fs_min, "bold"),
                    tags=tag,
                )
                _draw_roman_maybe_flat(
                    canvas,
                    cx + cos * r_min_roman,
                    cy + sin * r_min_roman,
                    ROMAN_BY_MINOR_NATURAL_INTERVAL.get(d_l, ""),
                    font_family,
                    fs_min_r,
                    fill_b,
                    tag,
                )
            else:
                canvas.create_text(
                    cx + cos * r_min,
                    cy + sin * r_min,
                    text=minor_name,
                    fill="#8b95a3",
                    font=(font_family, fs_min, "bold"),
                    tags=tag,
                )
        else:
            _suf, deg = diatonic_triad_suffix_major_key(tonic, pc)
            diatonic = deg is not None
            _suf_m, minor_deg = diatonic_triad_suffix_major_key(tonic, mpc_rel)
            if diatonic:
                if deg is not None and circle_upper_band_is_diatonic_major_triad(deg):
                    fill_t = CIRCLE_DEGREE_TEXT.get(deg, "#a8b0bd")
                    canvas.create_text(
                        cx + cos * r_maj_name,
                        cy + sin * r_maj_name,
                        text=major_name,
                        fill=fill_t,
                        font=(font_family, fs_maj, "bold"),
                        tags=tag,
                    )
                    canvas.create_text(
                        cx + cos * r_maj_roman,
                        cy + sin * r_maj_roman,
                        text=ROMAN_BY_DEGREE.get(deg, ""),
                        fill=fill_t,
                        font=(font_family, fs_maj_r),
                        tags=tag,
                    )
                elif deg == 11:
                    canvas.create_text(
                        cx + cos * r_maj_name,
                        cy + sin * r_maj_name,
                        text=major_name,
                        fill="#a8b0bd",
                        font=(font_family, fs_maj, "bold"),
                        tags=tag,
                    )
                else:
                    canvas.create_text(
                        cx + cos * r_maj_name,
                        cy + sin * r_maj_name,
                        text=major_name,
                        fill="#a8b0bd",
                        font=(font_family, fs_maj, "bold"),
                        tags=tag,
                    )
                if minor_deg == 11:
                    sim_lbl = f"{note_name_fn(vii_root_pc)}m"
                    fs_sim = _fit_font_size_for_slice(sim_lbl, fs_min_base, r_outer * 0.405, 8, font_family)
                    canvas.create_text(
                        cx + cos * (r_outer * 0.405),
                        cy + sin * (r_outer * 0.405),
                        text=sim_lbl,
                        fill=CIRCLE_DEGREE_TEXT[11],
                        font=(font_family, fs_sim, "bold"),
                        tags=tag,
                    )
                    canvas.create_text(
                        cx + cos * r_min_roman,
                        cy + sin * r_min_roman,
                        text=ROMAN_BY_DEGREE.get(11, ""),
                        fill=CIRCLE_DEGREE_TEXT[11],
                        font=(font_family, fs_min_r),
                        tags=tag,
                    )
                elif minor_deg is not None and circle_lower_band_is_diatonic_minor_triad(minor_deg):
                    fill_b = CIRCLE_DEGREE_TEXT.get(minor_deg, "#8b95a3")
                    canvas.create_text(
                        cx + cos * r_min,
                        cy + sin * r_min,
                        text=minor_name,
                        fill=fill_b,
                        font=(font_family, fs_min, "bold"),
                        tags=tag,
                    )
                    canvas.create_text(
                        cx + cos * r_min_roman,
                        cy + sin * r_min_roman,
                        text=ROMAN_BY_DEGREE.get(minor_deg, ""),
                        fill=fill_b,
                        font=(font_family, fs_min_r),
                        tags=tag,
                    )
                else:
                    canvas.create_text(
                        cx + cos * r_min,
                        cy + sin * r_min,
                        text=minor_name,
                        fill="#8b95a3",
                        font=(font_family, fs_min, "bold"),
                        tags=tag,
                    )
            else:
                canvas.create_text(
                    cx + cos * r_maj_name,
                    cy + sin * r_maj_name,
                    text=major_name,
                    fill="#a8b0bd",
                    font=(font_family, fs_maj, "bold"),
                    tags=tag,
                )
                canvas.create_text(
                    cx + cos * r_min,
                    cy + sin * r_min,
                    text=minor_name,
                    fill="#8b95a3",
                    font=(font_family, fs_min, "bold"),
                    tags=tag,
                )
