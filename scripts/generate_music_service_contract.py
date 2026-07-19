from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from midichords.core.music_service import detect_chord, generate_chord, generate_scale


OUTPUT_PATH = PROJECT_ROOT / "tests" / "fixtures" / "music_service_contract.json"

CASES: list[dict[str, Any]] = [
    {"id": "chord-major-root-es", "operation": "generate_chord", "input": {"root_pc": 0, "suffix": "", "inversion": 0, "language": "es", "prefer_flat": False}},
    {"id": "chord-minor-flat-en", "operation": "generate_chord", "input": {"root_pc": 10, "suffix": "m", "inversion": 0, "language": "en", "prefer_flat": True}},
    {"id": "chord-inversion-es", "operation": "generate_chord", "input": {"root_pc": 4, "suffix": "7", "inversion": 2, "language": "es", "prefer_flat": False}},
    {"id": "chord-added-tone-en", "operation": "generate_chord", "input": {"root_pc": 1, "suffix": "madd4", "inversion": 1, "language": "en", "prefer_flat": True}},
    {"id": "chord-extended-sharp", "operation": "generate_chord", "input": {"root_pc": 6, "suffix": "maj9#11", "inversion": 4, "language": "es", "prefer_flat": False}},
    {"id": "scale-ionian-es", "operation": "generate_scale", "input": {"tonic_pc": 0, "pattern_name": "Ionian", "language": "es", "prefer_flat": False}},
    {"id": "scale-dorian-flat-en", "operation": "generate_scale", "input": {"tonic_pc": 3, "pattern_name": "Dorian", "language": "en", "prefer_flat": True}},
    {"id": "scale-harmonic-minor", "operation": "generate_scale", "input": {"tonic_pc": 9, "pattern_name": "Harmonic Minor", "language": "es", "prefer_flat": False}},
    {"id": "scale-whole-tone-flat", "operation": "generate_scale", "input": {"tonic_pc": 6, "pattern_name": "Whole Tone", "language": "en", "prefer_flat": True}},
    {"id": "scale-world-pattern", "operation": "generate_scale", "input": {"tonic_pc": 1, "pattern_name": "Hirajoshi", "language": "es", "prefer_flat": True}},
    {"id": "detect-empty", "operation": "detect_chord", "input": {"notes": [], "language": "es", "prefer_flat": False}},
    {"id": "detect-single-flat", "operation": "detect_chord", "input": {"notes": [61], "language": "en", "prefer_flat": True}},
    {"id": "detect-major-root", "operation": "detect_chord", "input": {"notes": [60, 64, 67], "language": "es", "prefer_flat": False}},
    {"id": "detect-major-inversion", "operation": "detect_chord", "input": {"notes": [64, 67, 72], "language": "en", "prefer_flat": False}},
    {"id": "detect-dominant-flat", "operation": "detect_chord", "input": {"notes": [58, 62, 65, 68], "language": "es", "prefer_flat": True}},
    {"id": "detect-unmatched", "operation": "detect_chord", "input": {"notes": [60, 61, 66], "language": "en", "prefer_flat": False}},
]

EXPECTED_FIELDS = {
    "generate_chord": ("root_pc", "suffix", "inversion", "name", "notes_midi", "notes", "notes_no_octave", "intervals"),
    "generate_scale": ("tonic_pc", "pattern_name", "pattern_localized_name", "notes_midi", "notes", "intervals"),
    "detect_chord": ("name", "notes_midi", "notes", "extras_midi", "extras", "root_pc", "suffix"),
}


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    operation = case["operation"]
    values = case["input"]
    if operation == "generate_chord":
        result = generate_chord(**values)
    elif operation == "generate_scale":
        result = generate_scale(**values)
    else:
        result = detect_chord(**values)
    return {field: result[field] for field in EXPECTED_FIELDS[operation] if field in result}


def main() -> None:
    document = {
        "schema_version": 1,
        "canonical_implementation": "midichords.core.music_service",
        "cases": [{**case, "expected": evaluate(case)} for case in CASES],
    }
    OUTPUT_PATH.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(CASES)} cases in {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
