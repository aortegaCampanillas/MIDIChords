from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from midichords.core.guitar_chord_cache import get_cached_variations, load_guitar_chord_cache
from midichords.core.music_service import (
    detect_chord,
    generate_chord,
    generate_scale,
    list_chord_patterns,
    list_scale_patterns,
)
from midichords.core.music_theory import CHORD_PATTERNS


Language = Literal["es", "en"]
Accidental = Literal["sharp", "flat"]


class DetectionRequest(BaseModel):
    notes: list[int] = Field(default_factory=list)
    language: Language = "es"
    accidental: Accidental = "sharp"


class ChordGenerateRequest(BaseModel):
    root_pc: int = 0
    suffix: str = ""
    inversion: int = 0
    language: Language = "es"
    accidental: Accidental = "sharp"


class ScaleGenerateRequest(BaseModel):
    tonic_pc: int = 0
    pattern_name: str = "Ionian"
    language: Language = "es"
    accidental: Accidental = "sharp"


class GuitarVariationsRequest(BaseModel):
    root_pc: int = 0
    suffix: str = ""
    inversion: int = 0


HERE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(HERE / "templates"))
GUITAR_CACHE = load_guitar_chord_cache()

app = FastAPI(title="MIDIChords", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")


@app.get("/api/health")
def api_health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/meta")
def api_meta(language: Language = "es") -> dict:
    return {
        "chord_patterns": list_chord_patterns(),
        "scale_patterns": list_scale_patterns(language=language),
    }


@app.post("/api/detect")
def api_detect(payload: DetectionRequest) -> dict:
    prefer_flat = payload.accidental == "flat"
    return detect_chord(
        notes=payload.notes,
        language=payload.language,
        prefer_flat=prefer_flat,
    )


@app.post("/api/generate/chord")
def api_generate_chord(payload: ChordGenerateRequest) -> dict:
    prefer_flat = payload.accidental == "flat"
    return generate_chord(
        root_pc=payload.root_pc,
        suffix=payload.suffix,
        inversion=payload.inversion,
        language=payload.language,
        prefer_flat=prefer_flat,
    )


@app.post("/api/generate/scale")
def api_generate_scale(payload: ScaleGenerateRequest) -> dict:
    prefer_flat = payload.accidental == "flat"
    return generate_scale(
        tonic_pc=payload.tonic_pc,
        pattern_name=payload.pattern_name,
        language=payload.language,
        prefer_flat=prefer_flat,
    )


def _variation_bass_pc(variation: dict) -> int | None:
    string_notes = variation.get("string_notes")
    if isinstance(string_notes, list) and len(string_notes) >= 6:
        for note in string_notes:
            if note is not None:
                return int(note) % 12
    frets = variation.get("frets")
    if isinstance(frets, list) and len(frets) >= 6:
        tuning = [40, 45, 50, 55, 59, 64]  # 6->1
        for i, fret in enumerate(frets):
            if isinstance(fret, int) and fret >= 0:
                return (tuning[i] + fret) % 12
    notes = variation.get("notes")
    if isinstance(notes, list) and notes:
        return int(min(int(n) for n in notes)) % 12
    return None


@app.post("/api/generate/guitar-variations")
def api_generate_guitar_variations(payload: GuitarVariationsRequest) -> dict:
    root_pc = int(payload.root_pc) % 12
    suffix = str(payload.suffix)
    inversion = int(payload.inversion)
    variations = list(get_cached_variations(GUITAR_CACHE, root_pc, suffix))
    pattern = next((p for p in CHORD_PATTERNS if p.suffix == suffix), None)
    if pattern is not None and variations:
        intervals = list(pattern.intervals)
        if intervals:
            inversion_idx = min(max(0, inversion), max(0, len(intervals) - 1))
            target_bass_pc = (root_pc + int(intervals[inversion_idx])) % 12
            filtered = [v for v in variations if _variation_bass_pc(v) == target_bass_pc]
            if filtered:
                variations = filtered
    return {"variations": variations}
