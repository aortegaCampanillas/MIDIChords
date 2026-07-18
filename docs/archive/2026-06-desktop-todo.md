# TODO Desktop (Python/Tkinter)

> Documento histórico de junio de 2026. No representa el estado actual de la
> aplicación Qt. Consultar [`../ROADMAP.md`](../ROADMAP.md).

## Current Status
- **Progress:** 9/11 features (81.8%)
- **Infrastructure:** ✅ Complete
- **UI Integration:** Partial (Piano fingerings, MIDI highlighting staff, Interval detection)

---

## Tier 0: New Feature - Interval Detection Mode ✅ (Completed)

### Interval Detection Mode ✅ 
**Status:** Core logic and UI panel complete

**What was implemented:**
- ✅ `interval_data.py` — INTERVAL_NAMES and INTERVAL_MELODIES tables (12 reference melodies)
- ✅ `interval_mixin.py` — Full detection logic:
  - `_add_interval_note()` — adds note, keeps last 2
  - `get_interval_semitones()` → calculates semitones
  - `get_interval_name()` → returns interval name
  - `get_interval_melody_notes()` → sequence for reference song
  - `get_interval_melody_name()` → song name
  - `play_interval_melody()` — plays reference melody (ascending/descending)
  - `_setup_interval_ui()` — creates panel widget
  - `_update_interval_display()` — updates display labels

- ✅ `ui_mixin.py` — Added "interval_detection" to available modes
- ✅ `input_detection_mixin.py` — Routes MIDI/keyboard input to interval mode
- ✅ `i18n.py` — All translations (ES/EN)

**How it works:**
1. Mode added to mode selector in UI
2. When "interval_detection" mode active:
   - MIDI/keyboard notes route to `_add_interval_note()`
   - Panel shows last 2 notes + interval info
   - Buttons: "Reproducir", "Reproducir descendente", "Limpiar"
3. Reference melodies play with correct timing via `play_interval_melody()`

**Effort:** ✅ Complete (4 hours across 8 commits)

---

## Tier 1: High Impact (2-3 hours total)

### 1. Piano Fingerings UI Rendering
**File:** `midichords/mixins/render_mixin.py`

**What's done:**
- State: `scale_fingering_hand` in `main_app.py` line 225
- Methods: `_set_scale_fingering()`, `_refresh_scale_fingering_buttons()` in scales_mixin.py
- Data: `get_scale_fingerings()` returns Map[midi_note → finger_number]

**What's left:**
- In `render_mixin.py` `_draw_piano_white_key()` method, add fingering number rendering:
  - Location: above key, centered horizontally
  - Color: gold (#f3bf2f)
  - Font: medium size (14-16pt)
  - Show only if `scale_fingering_hand` is not None
  - Skip if no fingering exists for that note
- Same for black keys: render inside the key, respecting black key geometry
- Reference: Desktop already has this at lines ~1435-1465 in render_mixin.py

**Effort:** 30-45 minutes

---

### 2. MIDI Highlighting: Staff Rendering
**File:** `midichords/mixins/render_mixin.py`

**What's done:**
- State: `generation_midi_held_notes` tracks held notes in generation mode
- Piano highlighting: gold color on white/black keys (lines ~1400-1430)

**What's left:**
- In `_draw_staff()` method, detect notes in `generation_midi_held_notes`
- Highlight staff note heads with gold fill color (#f3bf2f) and dark gold outline (#d4a017)
- Render BEFORE other active note states (priority: MIDI held > chord detection > scale)
- Reference: Desktop staff rendering around line ~600-700 in render_mixin.py

**Effort:** 30-45 minutes

---

## Tier 2: Optional Polish (1-2 hours)

### 3. Scale Octave Visual Feedback
**File:** `midichords/mixins/render_mixin.py`

**What's done:**
- State: `scale_octaves` stores 1, 2, or 3
- Logic: `_get_scale_notes_for_octaves()` expands notes

**What's left:**
- Render octave range indicator on piano (e.g., highlight border showing C1-C4 for 3 octaves)
- Show vertical line separators between octaves
- Color octave groups differently or add visual brackets

**Effort:** Optional, 30+ minutes

---

### 4. Fingering Mode Indicator
**File:** `midichords/mixins/ui_mixin.py`

**What's done:**
- Buttons for RH/LH/None selector in scales panel (lines 1207-1244)
- Button state tracking

**What's left:**
- Add tooltip or label explaining that fingerings are TomPlay standard reference
- Show warning if user selects mode but scale type doesn't have fingering data
- Persist preference across sessions: save to config_data

**Effort:** Optional, 15-30 minutes

---

## Implementation Order

1. **Start:** Piano Fingerings UI (highest ROI, straightforward)
2. **Then:** Staff MIDI Highlighting (visual parity with piano)
3. **Polish:** Octave feedback, Fingering indicators

---

## Testing Checklist

- [ ] Select a scale (e.g., C Major) → RH mode → verify finger numbers 1-2-3-1-2-3-4-5 on piano
- [ ] Hold notes on MIDI keyboard in generation mode → verify gold highlight on both piano and staff
- [ ] Switch scale types (e.g., to one with no fingering data) → no crash, graceful degradation
- [ ] Change octave count → fingering numbers scale/shift correctly
- [ ] Close and reopen app → fingering hand preference persists

---

## Files Involved

| File | Current State | TODO |
|------|---------------|------|
| `midichords/main_app.py` | ✅ states defined | 0 |
| `midichords/mixins/scales_mixin.py` | ✅ methods ready | 0 |
| `midichords/mixins/render_mixin.py` | 🔶 partial | rendering integration |
| `midichords/mixins/ui_mixin.py` | ✅ buttons ready | optional polish |

---

## Reference Code Locations

**Piano fingering data retrieval:**
```python
# scales_mixin.py lines ~450-480
self._scaleFingeringsMap = {}  # populated by _get_scale_fingerings()
fingering = self._scaleFingeringsMap.get(midi_note)  # returns int 1-5 or None
```

**MIDI held notes tracking:**
```python
# input_detection_mixin.py lines ~3000-3010
if _tabIndex in (1, 2):  # generation mode
    self.generation_midi_held_notes.add(note_int)
```

**Piano drawing context:**
```python
# render_mixin.py _draw_piano_white_key() method
# Variables available: key_x, key_y, key_bottom, key_height, note_pitch
```

---

## Notes

- Fingering numbers use the same font/color scheme as piano key labels (see lines ~1350-1370)
- MIDI highlighting gold color (#f3bf2f) matches web implementation
- All piano fingering data is already loaded via `getFingeringForScale()` from `tomplay_fingerings.py`
- No new dependencies required
