#!/usr/bin/env python3
"""
Gap report para changelog: muestra qué features están pendientes en cada plataforma.

Uso:
  python scripts/changelog_gap.py              # Resumen completo
  python scripts/changelog_gap.py --platforms  # Desglose por plataforma
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def load_changelog():
    """Carga el changelog.json desde apps/web/static/"""
    path = Path(__file__).parent.parent / "apps" / "web" / "static" / "changelog.json"
    with open(path) as f:
        return json.load(f)

def analyze_changelog():
    """Analiza qué features tienen gaps."""
    changelog = load_changelog()

    # Recolectar todos los ítems publicados
    items_by_platform = defaultdict(list)
    all_platforms = set()
    items_list = []

    for version in changelog:
        for item in version.get("items", []):
            if not item.get("publish", False):
                continue

            platforms = item.get("platforms", ["web"])  # Default a web si no está especificado
            all_platforms.update(platforms)

            # Guardar la información
            items_list.append({
                "version": version["version"],
                "date": item["date"],
                "es": item["es"],
                "platforms": set(platforms),
            })

            for platform in platforms:
                items_by_platform[platform].append(version["version"])

    return items_list, all_platforms, items_by_platform

def print_gap_report():
    """Imprime el reporte de gaps."""
    items_list, all_platforms, items_by_platform = analyze_changelog()

    all_platforms = sorted(all_platforms)

    print("\n" + "="*80)
    print("CHANGELOG GAP REPORT".center(80))
    print("="*80 + "\n")

    # Resumen general
    total_items = len(items_list)
    print(f"Total de features publicados: {total_items}\n")

    # Plataformas
    for platform in all_platforms:
        count = len(items_by_platform[platform])
        pct = (count / total_items * 100) if total_items > 0 else 0
        print(f"  {platform.ljust(10)} {count:2d} / {total_items} ({pct:5.1f}%)")

    print()

    # Features pendientes por plataforma
    gaps = defaultdict(list)
    for item in items_list:
        for platform in all_platforms:
            if platform not in item["platforms"]:
                gaps[platform].append(item)

    if gaps:
        print("-" * 80)
        print("PENDIENTE POR PLATAFORMA:\n")

        for platform in all_platforms:
            if gaps[platform]:
                print(f"\n{platform.upper()} — {len(gaps[platform])} feature(s) pendiente(s):")
                for item in gaps[platform]:
                    print(f"  ✗ {item['version']} ({item['date']})")
                    print(f"    {item['es']}\n")
    else:
        print("\n✓ Todas las plataformas están sincronizadas!\n")

    print("="*80 + "\n")

def print_platform_view(platform):
    """Imprime vista filtrada por plataforma."""
    items_list, all_platforms, _ = analyze_changelog()

    items_for_platform = [item for item in items_list if platform in item["platforms"]]

    print(f"\nFeatures en {platform.upper()}: {len(items_for_platform)}\n")

    for item in items_for_platform:
        print(f"  ✓ {item['version']} ({item['date']})")
        print(f"    {item['es']}\n")

if __name__ == "__main__":
    try:
        if "--platforms" in sys.argv:
            items_list, all_platforms, _ = analyze_changelog()
            for platform in sorted(all_platforms):
                print_platform_view(platform)
        else:
            print_gap_report()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Asegúrate de ejecutar desde la raíz del proyecto.")
        sys.exit(1)
