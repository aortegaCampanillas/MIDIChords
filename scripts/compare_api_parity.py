from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

from midichords.core.music_service import (
    detect_chord,
    generate_chord,
    generate_scale,
    list_chord_patterns,
    list_scale_patterns,
)


BASE_URL = "https://freemidichords.com"


@dataclass
class Diff:
    endpoint: str
    case: str
    local: Any
    remote: Any


def http_json(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    url = f"{BASE_URL}{path}"
    last_exc: Exception | None = None
    for attempt in range(5):
        cmd = [
            "curl",
            "-sS",
            "-X",
            method,
            url,
            "-H",
            "accept: application/json, text/plain, */*",
            "-H",
            "user-agent: MIDIChordsParityCheck/1.0 (+https://freemidichords.com)",
        ]
        if payload is not None:
            cmd.extend(["-H", "content-type: application/json", "--data", json.dumps(payload)])
        try:
            out = subprocess.check_output(cmd, text=True)
            return json.loads(out)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(0.2 * (attempt + 1))
    raise RuntimeError(f"request failed after retries: {url}: {last_exc}")


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in sorted(value.items(), key=lambda kv: kv[0])}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def compare_case(diffs: list[Diff], endpoint: str, case: str, local: Any, remote: Any) -> None:
    if normalize(local) != normalize(remote):
        diffs.append(Diff(endpoint=endpoint, case=case, local=local, remote=remote))


def run() -> int:
    diffs: list[Diff] = []

    try:
        remote_health = http_json("/api/health")
    except Exception as exc:
        print(f"ERROR: no se pudo contactar API remota: {exc}", file=sys.stderr)
        return 2
    compare_case(diffs, "/api/health", "health", {"status": "ok"}, remote_health)

    for lang in ("es", "en"):
        local_meta = {
            "chord_patterns": list_chord_patterns(),
            "scale_patterns": list_scale_patterns(language=lang),
        }
        remote_meta = http_json(f"/api/meta?language={lang}")
        compare_case(diffs, "/api/meta", f"language={lang}", local_meta, remote_meta)

    detect_inputs = [
        {"notes": [], "language": "es", "accidental": "sharp"},
        {"notes": [60], "language": "es", "accidental": "sharp"},
        {"notes": [60, 64, 67], "language": "es", "accidental": "sharp"},
        {"notes": [60, 63, 67], "language": "es", "accidental": "sharp"},
        {"notes": [61, 65, 68], "language": "es", "accidental": "flat"},
        {"notes": [64, 67, 72], "language": "en", "accidental": "sharp"},
        {"notes": [60, 64, 67, 70], "language": "en", "accidental": "flat"},
        {"notes": [62, 65, 69, 72], "language": "es", "accidental": "sharp"},
    ]
    for idx, payload in enumerate(detect_inputs):
        local = detect_chord(
            notes=payload["notes"],
            language=payload["language"],
            prefer_flat=(payload["accidental"] == "flat"),
        )
        remote = http_json("/api/detect", method="POST", payload=payload)
        compare_case(diffs, "/api/detect", f"case#{idx}", local, remote)

    chord_patterns = list_chord_patterns()
    selected_suffixes = [p["suffix"] for p in chord_patterns[:20]]
    roots = [0, 1, 2, 5, 7, 10]
    langs = ("es", "en")
    accidentals = ("sharp", "flat")
    for suffix in selected_suffixes:
        for root in roots:
            for lang in langs:
                for acc in accidentals:
                    local_base = generate_chord(
                        root_pc=root,
                        suffix=suffix,
                        inversion=0,
                        language=lang,
                        prefer_flat=(acc == "flat"),
                    )
                    max_inv = max(0, len(local_base.get("intervals", [])) - 1)
                    for inv in (0, max_inv):
                        payload = {
                            "root_pc": root,
                            "suffix": suffix,
                            "inversion": inv,
                            "language": lang,
                            "accidental": acc,
                        }
                        local = generate_chord(
                            root_pc=root,
                            suffix=suffix,
                            inversion=inv,
                            language=lang,
                            prefer_flat=(acc == "flat"),
                        )
                        remote = http_json("/api/generate/chord", method="POST", payload=payload)
                        case = f"{suffix or 'maj'} root={root} inv={inv} {lang} {acc}"
                        compare_case(diffs, "/api/generate/chord", case, local, remote)

    scale_patterns = [p["name"] for p in list_scale_patterns(language="en")]
    selected_scales = scale_patterns[:30]
    for pattern_name in selected_scales:
        for tonic in (0, 1, 4, 7, 10):
            for lang in ("es", "en"):
                for acc in ("sharp", "flat"):
                    payload = {
                        "tonic_pc": tonic,
                        "pattern_name": pattern_name,
                        "language": lang,
                        "accidental": acc,
                    }
                    local = generate_scale(
                        tonic_pc=tonic,
                        pattern_name=pattern_name,
                        language=lang,
                        prefer_flat=(acc == "flat"),
                    )
                    remote = http_json("/api/generate/scale", method="POST", payload=payload)
                    case = f"{pattern_name} tonic={tonic} {lang} {acc}"
                    compare_case(diffs, "/api/generate/scale", case, local, remote)

    if not diffs:
        print("OK: paridad completa en casos probados.")
        return 0

    print(f"DIFFS: {len(diffs)}")
    for d in diffs[:25]:
        print(f"- {d.endpoint} [{d.case}]")
        print(f"  local : {json.dumps(d.local, ensure_ascii=False, sort_keys=True)}")
        print(f"  remote: {json.dumps(d.remote, ensure_ascii=False, sort_keys=True)}")
    if len(diffs) > 25:
        print(f"... {len(diffs) - 25} diferencias adicionales omitidas")
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
