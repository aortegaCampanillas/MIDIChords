from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Iterable, Optional

from midichords.core.app_constants import ASSETS_DIR
from midichords.core.music_theory import (
    chord_construction_from_midi,
    chord_formula_from_root,
    root_position_voicing,
    rotate_degrees,
)

_INVERSION_LABEL_KEYS = {
    "es": ["", "primera inversión", "segunda inversión", "tercera inversión",
           "cuarta inversión", "quinta inversión", "sexta inversión"],
    "en": ["", "first inversion", "second inversion", "third inversion",
           "fourth inversion", "fifth inversion", "sixth inversion"],
}


_GROUP_LABELS = {
    "es": {
        "chord_group_triads": "Tríadas",
        "chord_group_sevenths": "Séptimas",
        "chord_group_sixths": "Sextas",
        "chord_group_add": "Add (notas añadidas)",
        "chord_group_altered_dominants": "Dominantes alterados",
        "chord_group_extensions": "Extensiones",
        "chord_group_altered_extensions": "Extensiones alteradas",
        "chord_group_other": "Otras variantes",
    },
    "en": {
        "chord_group_triads": "Triads",
        "chord_group_sevenths": "Sevenths",
        "chord_group_sixths": "Sixths",
        "chord_group_add": "Add chords",
        "chord_group_altered_dominants": "Altered dominants",
        "chord_group_extensions": "Extensions",
        "chord_group_altered_extensions": "Altered extensions",
        "chord_group_other": "Other variants",
    },
}


@lru_cache(maxsize=1)
def chord_help_catalog() -> dict[str, Any]:
    path = ASSETS_DIR / "chord_variant_theory.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def chord_variant_groups(
    language: str,
    available_suffixes: Iterable[str],
) -> list[tuple[str, list[str]]]:
    lang = "en" if language == "en" else "es"
    available = {str(suffix) for suffix in available_suffixes}
    rendered: set[str] = set()
    result: list[tuple[str, list[str]]] = []
    for group in chord_help_catalog().get("groups", []):
        suffixes = [str(s) for s in group.get("suffixes", []) if str(s) in available]
        if not suffixes:
            continue
        rendered.update(suffixes)
        label_key = str(group.get("labelKey", ""))
        result.append((_GROUP_LABELS[lang].get(label_key, label_key), suffixes))
    remaining = sorted(available - rendered)
    if remaining:
        result.append((_GROUP_LABELS[lang]["chord_group_other"], remaining))
    return result


def _natural_language_list(items: list[str], language: str) -> str:
    if len(items) <= 1:
        return items[0] if items else ""
    conjunction = " and " if language == "en" else " y "
    return f"{', '.join(items[:-1])}{conjunction}{items[-1]}"


def chord_inversion_help(formula: str, inversion: int, language: str) -> str:
    lang = "en" if language == "en" else "es"
    catalog = chord_help_catalog()
    degrees = [part for part in str(formula).split(" - ") if part]
    if not degrees:
        return ""
    safe_inversion = max(0, min(int(inversion), len(degrees) - 1))
    names = catalog["inversion_names"][lang]
    inversion_name = names[safe_inversion] if safe_inversion < len(names) else str(safe_inversion)
    if safe_inversion == 0:
        if lang == "en":
            return (
                f"{inversion_name}: the root is in the bass and the remaining notes appear above it in "
                "formula order. This is the clearest reference position for recognizing the chord's structure."
            )
        return (
            f"{inversion_name}: la fundamental está en el bajo y las demás notas aparecen por encima siguiendo "
            "el orden de la fórmula. Es la posición de referencia más clara para reconocer la estructura del acorde."
        )
    degree_names = catalog["degree_names"][lang]
    bass_degree = degree_names.get(degrees[safe_inversion], degrees[safe_inversion])
    moved_degrees = [degree_names.get(degree, degree) for degree in degrees[:safe_inversion]]
    moved = _natural_language_list(moved_degrees, lang)
    if lang == "en":
        verb = "moves" if len(moved_degrees) == 1 else "move"
        return (
            f"{inversion_name}: {bass_degree} is in the bass. {moved} {verb} up one octave; the chord keeps the "
            "same notes, but its bass support and voice leading into nearby chords change."
        )
    verb = "se desplaza" if len(moved_degrees) == 1 else "se desplazan"
    return (
        f"{inversion_name}: {bass_degree} está en el bajo. {moved} {verb} una octava hacia arriba; el acorde "
        "conserva las mismas notas, pero cambia su apoyo grave y el enlace con los acordes cercanos."
    )


def chord_variant_help(suffix: str, inversion: int, language: str) -> tuple[str, str, str]:
    lang = "en" if language == "en" else "es"
    catalog = chord_help_catalog()
    entry = catalog.get("theory", {}).get(str(suffix), {})
    formula = str(entry.get("formula", ""))
    theory = str(entry.get(lang, ""))
    if str(suffix) == "" and 0 <= int(inversion) < len(catalog.get("major_inversions", [])):
        inversion_text = str(catalog["major_inversions"][int(inversion)][1 if lang == "en" else 0])
    else:
        inversion_text = chord_inversion_help(formula, int(inversion), lang)
    return formula, theory, inversion_text


def _append_inversion_detail(base_value: str, inversion_index: int, inverted_value: str, language: str) -> str:
    if not inversion_index:
        return base_value
    lang = "en" if language == "en" else "es"
    names = _INVERSION_LABEL_KEYS[lang]
    label = names[inversion_index] if inversion_index < len(names) else (
        f"Inversion {inversion_index}" if lang == "en" else f"Inversión {inversion_index}"
    )
    return f"{base_value} ({label}: {inverted_value})"


def chord_formula_and_construction(
    root_pc: Optional[int],
    suffix: Optional[str],
    inversion: int,
    chord_midi: list[int],
    language: str,
) -> tuple[str, str]:
    """Fórmula y construcción de un acorde (con detalle de inversión entre
    paréntesis si aplica), para detección o generación. chord_midi debe ser el
    voicing ya ordenado tal como se toca/genera (refleja la inversión)."""
    if root_pc is None or not chord_midi:
        return "-", "-"
    catalog = chord_help_catalog()
    curated = catalog.get("theory", {}).get(str(suffix), {}).get("formula") if suffix is not None else None
    root_formula = str(curated) if curated else chord_formula_from_root(int(root_pc), chord_midi)
    inversion_index = int(inversion) or 0
    formula = _append_inversion_detail(
        root_formula, inversion_index, rotate_degrees(root_formula, inversion_index), language,
    )
    if inversion_index > 0:
        root_position_midi = root_position_voicing(int(root_pc), chord_midi)
        root_construction = chord_construction_from_midi(root_position_midi)
        inversion_construction = chord_construction_from_midi(chord_midi)
        construction = _append_inversion_detail(root_construction, inversion_index, inversion_construction, language)
    else:
        construction = chord_construction_from_midi(chord_midi)
    return formula, construction
