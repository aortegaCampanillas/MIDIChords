#!/usr/bin/env python3
"""Report which changelog features are missing from each platform."""

import json
from pathlib import Path

# Locate changelog.json
PROJECT_ROOT = Path(__file__).parent.parent
CHANGELOG_PATH = PROJECT_ROOT / "assets" / "changelog.json"


def load_changelog():
    """Load and parse changelog.json."""
    if not CHANGELOG_PATH.exists():
        print(f"Error: changelog.json not found at {CHANGELOG_PATH}")
        return []
    with open(CHANGELOG_PATH) as f:
        data = json.load(f)
    return data


def main():
    versions = load_changelog()
    all_platforms = {"web", "desktop", "mobile"}

    # Collect all published features
    features = []
    for version_group in versions:
        for item in version_group.get("items", []):
            if not item.get("publish", False):
                continue
            platforms = set(item.get("platforms", ["web"]))
            features.append({
                "version": version_group.get("version", "unknown"),
                "date": item.get("date", "unknown"),
                "es": item.get("es", ""),
                "platforms": platforms,
            })

    if not features:
        print("No published features found.")
        return

    print(f"\n{'='*80}")
    print(f"MIDIChords Feature Parity Report")
    print(f"{'='*80}\n")

    # Summary counts
    counts = {p: 0 for p in all_platforms}
    for feat in features:
        for p in feat["platforms"]:
            counts[p] += 1

    total = len(features)
    print(f"Total published features: {total}\n")
    print(f"Implementation status:")
    for p in sorted(all_platforms):
        pct = (counts[p] / total * 100) if total > 0 else 0
        print(f"  {p:8} {counts[p]:2}/{total} ({pct:5.1f}%)")

    print(f"\n{'='*80}")
    print(f"Features by platform:")
    print(f"{'='*80}\n")

    # Show pending features per platform
    for target_platform in sorted(all_platforms):
        pending = [f for f in features if target_platform not in f["platforms"]]
        if not pending:
            print(f"✓ {target_platform}: All features implemented\n")
            continue

        print(f"⚠ {target_platform}: {len(pending)} features pending\n")
        for feat in pending:
            has = ", ".join(sorted(feat["platforms"])) if feat["platforms"] else "none"
            print(f"  [{feat['version']}] {feat['date']}")
            print(f"    {feat['es']}")
            print(f"    (implemented in: {has})\n")


if __name__ == "__main__":
    main()
