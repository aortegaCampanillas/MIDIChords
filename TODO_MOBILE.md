# TODO Mobile (Flutter/Dart)

## Current Status
- **Progress:** 9/11 features (81.8%)
- **Infrastructure:** ✅ Complete
- **UI Integration:** Partial (Audio/MIDI, Piano fingerings, MIDI highlighting rendering)

---

## Tier 1: Essential for Feature Completion (5-6 hours total)

### 1. Audio/MIDI Output Routing
**File:** `apps/mobile_flutter/lib/main.dart`

**What's done:**
- State: `_soundOutput = 'audio'` (line ~857)
- Wrapper methods: `playNote()`, `stopNote()` with audio/MIDI conditional logic (lines ~9197-9235)
- Infrastructure: state loads from persistent storage on startup

**What's left:**
- Replace ALL direct audio calls with `playNote()/stopNote()` wrapper:
  - Scale playback loop: `_playScaleLoop()` → call `playNote()` instead of `audio_engine.note_on()`
  - Chord generation playback: `_playChord()` → use wrapper
  - Detection mode playback: `_onPianoKeyDown()` → use wrapper
  - Staff playback: any audio engine calls
- Connect MIDI device output (if available):
  - When `_soundOutput == 'midi'`, invoke `_midiCommand.sendData()` with note_on/note_off messages
  - Handle case when no MIDI output connected (fallback to audio gracefully)
- Persist preference: save to `_prefs` on toggle

**Effort:** 2-3 hours

**Files to update:**
- `playNote()` call sites: ~15-20 locations
- MIDI output device selection: optional UI for choosing output port
- Error handling: show toast if MIDI device unavailable

---

### 2. Piano Fingerings: UI Display
**File:** `apps/mobile_flutter/lib/main.dart` → piano widget integration

**What's done:**
- State: `_scaleFingeringHand` stores 'right'/'left'/null (line ~864)
- Data: `_scaleFingeringsMap` = Map<int, int> of midi_note → finger_number (line ~865)
- Methods: `_setScaleFingeringHand()`, `_updateScaleFingeringsMap()`, `getScaleFingering()` (lines ~9238-9267)
- Helper: `getDisplayScaleFingeringNotes()` returns fingerings for rendering (NEW)

**What's left:**
- **Scales tab selector UI:** Add RH/LH/None buttons near scale tonic/type selectors
  - Location: scales panel, near octave buttons
  - Three buttons with state tracking (current hand highlighted)
  - Call `_setScaleFingeringHand(hand)` on tap
  - Color scheme: match octave button style

- **Piano rendering:** Show finger numbers on white/black keys
  - Location: in `_buildScalePianoWidget()` or custom painter
  - Display: small centered badge per key (1-5)
  - Color: gold text (#f3bf2f) on transparent background
  - Size: 12-14pt font
  - Show only if `_scaleFingeringHand` is not null and fingering exists
  - Reference geometry: white key area for white keys, black key interior for black keys

- **Chord fingerings (optional):** Display fingerings for generated chords
  - Data: use TomPlay chord fingering tables (similar to scales)
  - Display: same badge style on piano in generation mode

**Effort:** 2-3 hours

**Reference:** Desktop has complete example at `render_mixin.py` lines ~1435-1465

---

### 3. MIDI Highlighting: Piano & Staff Rendering
**File:** `apps/mobile_flutter/lib/main.dart` → piano/staff widgets

**What's done:**
- State: `_generationMidiHeldNotes` tracks held notes (line ~863)
- Tracking: MIDI packet handler populates set on note_on/note_off (lines ~3000-3010)
- Cleanup: held notes cleared on tab change (line ~5718)
- Helper: `getGenerationMidiHeldNotes()` returns set for rendering (NEW)

**What's left:**
- **Piano highlighting:** Render held notes in gold
  - Location: generation piano widget painter
  - Color: gold fill (#f3bf2f) with dark gold outline (#d4a017)
  - Shape: fill the key area (white or black)
  - Priority: render BEFORE chord/scale note highlights
  - Sync with piano key touch handling (held note = touched MIDI key)

- **Staff highlighting:** Show held notes on staff in real-time
  - Location: generation staff widget painter
  - Color: gold note head with dark outline
  - Priority: render BEFORE other active note markers
  - Only show if tabIndex == 1 or 2 (generation mode)

**Effort:** 1.5-2 hours

**Reference:** Desktop has complete implementation at `render_mixin.py` lines ~1400-1430 (piano) and ~600-700 (staff)

---

## Tier 2: Polish & Edge Cases (1-2 hours)

### 4. MIDI Message Sending Implementation
**File:** `apps/mobile_flutter/lib/main.dart` → `playNote()` / `stopNote()` MIDI branch

**What's done:**
- Methods have TODO stubs for MIDI message sending (lines ~9220-9235)
- `_midiCommand` object is available for sending data

**What's left:**
- Implement note_on message: `_midiCommand.sendData([0x90, midi_note, velocity])`
- Implement note_off message: `_midiCommand.sendData([0x80, midi_note, 0])`
- Handle velocity: use parameter passed to `playNote()` (default 80)
- Handle timing: note_off can be delayed (for sustain) or immediate
- Error handling: wrap in try-catch, log if MIDI send fails silently

**Effort:** 30-45 minutes

---

### 5. Fingering Mode Persistence
**File:** `apps/mobile_flutter/lib/main.dart`

**What's done:**
- State: `_scaleFingeringHand` exists
- Method: `_setScaleFingeringHand()` updates state

**What's left:**
- Save to `_prefs` (SharedPreferences) on change
- Load from `_prefs` on app startup
- Key: `'scale_fingering_hand'` → String ('right'/'left'/null)

**Effort:** 15-30 minutes

---

### 6. Scale Octave Selection UI (Optional)
**File:** `apps/mobile_flutter/lib/main.dart` → scales panel

**What's done:**
- State: `_scaleOctaves` stores count (1-3)
- Logic: octave expansion works correctly

**What's left:**
- Add three buttons (1, 2, 3 octaves) to scales tab
- Highlight current selection
- Call `_setScaleOctaves(count)` on tap
- Optional: show visual indicator of range on piano (C1-C4, etc.)

**Effort:** Optional, 30-45 minutes

---

## Implementation Order

1. **Start:** Audio/MIDI routing (core feature, enables sound output selection)
2. **Then:** Piano fingerings UI (high visual impact, straightforward)
3. **Then:** MIDI highlighting rendering (completes generation mode visual feedback)
4. **Polish:** MIDI message sending, persistence, octave selector

---

## Testing Checklist

- [ ] Audio/MIDI: Toggle audio/MIDI output → verify only one plays
- [ ] Audio/MIDI: If MIDI device unavailable → graceful fallback to audio
- [ ] Audio/MIDI: Close and reopen app → preference persisted
- [ ] Fingerings: Select scale → RH mode → finger numbers visible on piano
- [ ] Fingerings: Change scale type → fingerings update or disappear gracefully
- [ ] Fingerings: Close and reopen → RH/LH preference remembered
- [ ] MIDI highlight: Hold notes in generation mode → gold highlights appear on piano and staff
- [ ] MIDI highlight: Release notes → highlights disappear
- [ ] MIDI highlight: Switch to other tabs → highlights clear
- [ ] Overall: No crashes or memory leaks during repeated mode switching

---

## Files Involved

| File | Current State | TODO |
|------|---------------|------|
| `apps/mobile_flutter/lib/main.dart` | 🔶 infrastructure ready | routing + rendering integration |
| `apps/mobile_flutter/lib/fingerings.dart` | ✅ complete data | 0 |
| `apps/mobile_flutter/lib/circle_of_fifths.dart` | ✅ complete | 0 |

---

## Reference Code Locations

**Audio/MIDI routing:**
```dart
// main.dart line ~857
String _soundOutput = 'audio';

// lines ~9197-9235
void playNote(int midi, {int velocity = 80, Duration? duration}) {
  if (_soundOutput == 'midi' && _midiOutputConnected) {
    _midiCommand.sendData([0x90, midi, velocity]);
  } else {
    _playTone(midi, velocity: velocity);
  }
}
```

**Fingering data access:**
```dart
// main.dart line ~865
Map<int, int> _scaleFingeringsMap = {};

// line ~9267
int? getScaleFingering(int midiNote) => _scaleFingeringsMap[midiNote];
```

**MIDI held notes:**
```dart
// main.dart line ~863
Set<int> _generationMidiHeldNotes = <int>{};

// line ~3000-3010 (MIDI handler)
if (_tabIndex == 1 || _tabIndex == 2) {
  if (isNoteOn) {
    _generationMidiHeldNotes.add(note);
  } else if (isNoteOff) {
    _generationMidiHeldNotes.remove(note);
  }
}
```

---

## Notes

- Fingering numbers use gold color (#f3bf2f) matching desktop/web
- All fingering data is pre-loaded from `fingerings.dart`
- MIDI message format: status=0x90 (note on), 0x80 (note off), data=[note, velocity]
- Piano widget geometry differs from desktop; reference existing key rendering code for layout
- Test with actual MIDI device connected if possible; otherwise graceful degradation is acceptable

---

## Known Limitations

- MIDI output device selection UI not yet designed (optional; defaults to first available)
- Chord fingerings infrastructure exists but not fully documented (scale fingerings prioritized)
- Staff painter may need refactoring for MIDI highlighting layer priority

