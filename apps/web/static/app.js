const state = {
  mode: null,
  instrument: "piano",
  scalePlayMode: "piano",
  scaleMetronomeEnabled: false,
  guitarHandedness: "right",
  language: "es",
  accidental: "sharp",
  chordPatterns: [],
  scalePatterns: [],
  activeDetectionNotes: new Set(),
  activeMidiLiveNotes: new Set(),
  detectionResult: null,
  generatedChord: null,
  generatedScale: null,
  scaleCurrentNote: null,
  scaleInputRawNote: null,
  scaleGuitarStartNote: null,
  generationCurrentNote: null,
  generationPlayingNotes: new Set(),
  guitarChordCache: null,
  guitarVariations: [],
  guitarSelectedVariationIdx: null,
  guitarHitRegions: [],
  scaleLoop: {
    active: false,
    timer: null,
    index: 0,
    direction: 1,
  },
  scaleCurrentClearTimer: null,
  generationCurrentClearTimer: null,
  generationPlayClearTimer: null,
  metronomeRunning: false,
  metronomeTimer: null,
  metronomeAnimRaf: null,
  metronomeCtx: null,
  beatsPerBar: 4,
  clicksPerBeat: 1,
  metronomeBarAccentEnabled: true,
  metronomeTimerEnabled: false,
  metronomeTimerMinutes: 2,
  metronomeTimerSeconds: 0,
  metronomeTimerRemaining: 120,
  metronomeTimerLastTs: 0,
  currentBeat: -1,
  currentSubclick: 0,
  metronomeTickCount: 0,
  metronomeDirection: 1,
  metronomeMotionStartTs: 0,
  midi: {
    enabled: false,
    access: null,
    onMessage: null,
  },
  tuner: {
    running: false,
    stream: null,
    audioCtx: null,
    analyser: null,
    freqData: null,
    rangeMinHz: 20,
    rangeMaxHz: 500,
    inputGain: 100,
    currentStringIdx: null,
    currentCents: 0,
    currentFreq: 0,
    detectedMidi: null,
    buttonActiveUntil: {},
    referenceNote: null,
    tuningKey: "standard_e",
    raf: null,
  },
  staff: {
    braceImage: null,
    tunerStringRegions: [],
    scaleRegions: [],
    scaleHoverNote: null,
    scaleHoverDegree: null,
    scalePressedNote: null,
    scalePressedDegree: null,
    scaleSuppressNextClick: false,
  },
  heldChordVoices: new Map(),
  heldInputVoices: new Map(),
  inputDragActive: false,
  inputDragNote: null,
  inputDragInstrument: null,
  detectionShiftPressed: false,
  shiftPressed: false,
  detectionMouseChordNotes: new Set(),
  detectionMidiHeldNotes: new Set(),
  midiInputSoundEnabled: true,
  heldMidiInputVoices: new Map(),
};

const UI_TEXTS = {
  es: {
    mode_detection: "Detección de Acordes",
    mode_generation: "Generación de Acordes",
    mode_scales: "Escalas",
    mode_metronome: "Metrónomo",
    mode_tuner: "Afinador",
    staff: "Pentagrama",
    heading_detection: "Detección",
    heading_generation: "Generación de Acordes",
    heading_scales: "Escalas",
    heading_metronome: "Metrónomo",
    heading_tuner: "Afinador",
    hint_detection: "Pulsa notas en piano/guitarra para detectar acordes o usa un dispositivo MIDI.",
    clear: "Limpiar",
    label_chord: "Acorde:",
    label_notes: "Notas:",
    label_extras: "Sobrantes:",
    label_intervals: "Intervalos:",
    label_tonic: "Tónica",
    label_variant: "Variante",
    label_inversion: "Inversión",
    label_type: "Tipo",
    label_speed: "Velocidad",
    label_scale: "Escala:",
    label_note: "Nota:",
    label_cents: "Desviación:",
    label_freq: "Frecuencia:",
    label_bpm: "PPM",
    label_metronome_tempo: "Tempo",
    label_beats: "Pulsos por compás",
    label_subdivision: "Subdivisión",
    label_bar_accent: "Acento de compás",
    label_timer_enabled: "Temporizador",
    label_timer: "Tiempo",
    play: "Reproducir",
    stop: "Detener",
    metronome_mode: "Modo metrónomo",
    metro_start: "Iniciar metrónomo",
    metro_stop: "Detener metrónomo",
    tuner_start: "Iniciar afinador",
    tuner_stop: "Detener afinador",
    tuner_no_permission: "Sin permiso",
    tuner_cents_suffix: "cents",
    label_tuner_tuning: "Afinación",
    label_tuner_gain: "Ganancia de entrada",
    label_tuner_spectrum_range: "Rango del espectro",
    midi_off: "MIDI: Off",
    midi_on: "MIDI: On",
    midi_unsupported: "MIDI no soportado",
    midi_denied: "MIDI denegado",
    midi_requires_secure: "MIDI requiere HTTPS o localhost",
    midi_try_chrome: "MIDI: usa Chrome/Edge",
    midi_help_ready: "MIDI Web listo. Pulsa para activar/desactivar entradas MIDI.",
    midi_help_denied: "Permiso MIDI denegado. Revisa permisos del navegador y vuelve a intentar.",
    midi_input_sound_on: "Reproducir entrada MIDI",
    midi_input_sound_off: "Silenciar entrada MIDI",
    midi_startup_title: "Activar entrada MIDI",
    midi_startup_text: "Para usar un teclado/controlador MIDI en detección, activa la entrada MIDI.",
    midi_startup_enable: "Activar MIDI",
    midi_startup_close: "Ahora no",
    close: "Cerrar",
    midi_startup_safari_warning: "En Safari no es posible usar MIDI en esta web. Usa Chrome o Edge.",
    guitar_right: "Diestro",
    guitar_left: "Zurdo",
    inst_piano: "Piano",
    inst_guitar: "Guitarra",
    inversion_root: "Posición fundamental",
    inversion_suffix: "ª inversión",
    tempo_unit: "PPM",
    inversion_word: "inversión",
    donation_title: "Apoya MIDIChords",
    donation_text: "Este proyecto está pensado para mantenerse siempre gratis y sin publicidad. Tu ayuda permite cubrir costes de desarrollo, mantenimiento, infraestructura y tiempo de soporte para seguir mejorándolo.",
    donation_button: "Donar",
    detection_staff_shift_hint: "Mantén Shift pulsado para sostener notas",
    scale_staff_guitar_shift_hint: "Mantén Shift y pulsa una tónica para cambiar el inicio de la escala",
    staff_no_active_notes: "Sin notas activas",
  },
  en: {
    mode_detection: "Chord Detection",
    mode_generation: "Chord Generation",
    mode_scales: "Scales",
    mode_metronome: "Metronome",
    mode_tuner: "Tuner",
    staff: "Staff",
    heading_detection: "Detection",
    heading_generation: "Chord Generation",
    heading_scales: "Scales",
    heading_metronome: "Metronome",
    heading_tuner: "Tuner",
    hint_detection: "Press notes on piano/guitar to detect chords or use a MIDI device.",
    clear: "Clear",
    label_chord: "Chord:",
    label_notes: "Notes:",
    label_extras: "Extra notes:",
    label_intervals: "Intervals:",
    label_tonic: "Tonic",
    label_variant: "Variant",
    label_inversion: "Inversion",
    label_type: "Type",
    label_speed: "Speed",
    label_scale: "Scale:",
    label_note: "Note:",
    label_cents: "Cents:",
    label_freq: "Frequency:",
    label_bpm: "BPM",
    label_metronome_tempo: "Tempo",
    label_beats: "Beats per bar",
    label_subdivision: "Subdivision",
    label_bar_accent: "Bar accent",
    label_timer_enabled: "Timer",
    label_timer: "Time",
    play: "Play",
    stop: "Stop",
    metronome_mode: "Metronome mode",
    metro_start: "Start metronome",
    metro_stop: "Stop metronome",
    tuner_start: "Start tuner",
    tuner_stop: "Stop tuner",
    tuner_no_permission: "No permission",
    tuner_cents_suffix: "cents",
    label_tuner_tuning: "Tuning",
    label_tuner_gain: "Input gain",
    label_tuner_spectrum_range: "Spectrum range",
    midi_off: "MIDI: Off",
    midi_on: "MIDI: On",
    midi_unsupported: "MIDI unsupported",
    midi_denied: "MIDI denied",
    midi_requires_secure: "MIDI requires HTTPS or localhost",
    midi_try_chrome: "MIDI: use Chrome/Edge",
    midi_help_ready: "Web MIDI ready. Click to enable/disable MIDI inputs.",
    midi_help_denied: "MIDI permission denied. Check browser permissions and try again.",
    midi_input_sound_on: "Play MIDI input",
    midi_input_sound_off: "Mute MIDI input",
    midi_startup_title: "Enable MIDI input",
    midi_startup_text: "To use a MIDI keyboard/controller in detection, enable MIDI input.",
    midi_startup_enable: "Enable MIDI",
    midi_startup_close: "Not now",
    close: "Close",
    midi_startup_safari_warning: "MIDI is not available on this website in Safari. Use Chrome or Edge.",
    guitar_right: "Right-handed",
    guitar_left: "Left-handed",
    inst_piano: "Piano",
    inst_guitar: "Guitar",
    inversion_root: "Root position",
    inversion_suffix: " inversion",
    tempo_unit: "BPM",
    inversion_word: "inversion",
    donation_title: "Support MIDIChords",
    donation_text: "This project is designed to stay free forever and ad-free. Your support helps cover development, maintenance, infrastructure, and support time so we can keep improving it.",
    donation_button: "Donate",
    detection_staff_shift_hint: "Hold Shift to sustain notes",
    scale_staff_guitar_shift_hint: "Hold Shift and click a tonic to change the scale start note",
    staff_no_active_notes: "No active notes",
  },
};

const NOTE_LABELS = {
  es: {
    sharp: ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
    flat: ["Do", "Re♭", "Re", "Mi♭", "Mi", "Fa", "Sol♭", "Sol", "La♭", "La", "Si♭", "Si"],
  },
  en: {
    sharp: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    flat: ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"],
  },
};

const SHARP_KEY_SIGNATURES = ["F", "C", "G", "D", "A", "E", "B"];
const FLAT_KEY_SIGNATURES = ["B", "E", "A", "D", "G", "C", "F"];
const PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6];
const DONATE_URL = "https://buy.stripe.com/test_00w7sLcfn6Q3bvT3GL2cg00";
const TUNER_TUNINGS = [
  { key: "standard_e", es: "E estándar", en: "Standard E", notes: [40, 45, 50, 55, 59, 64] },
  { key: "drop_d", es: "Drop D", en: "Drop D", notes: [38, 45, 50, 55, 59, 64] },
  { key: "drop_c", es: "Drop C", en: "Drop C", notes: [36, 43, 48, 53, 57, 62] },
  { key: "half_step_down", es: "1/2 tono abajo", en: "Half-step down", notes: [39, 44, 49, 54, 58, 63] },
  { key: "whole_step_down", es: "1 tono abajo", en: "Whole-step down", notes: [38, 43, 48, 53, 57, 62] },
  { key: "open_g", es: "Open G", en: "Open G", notes: [38, 43, 50, 55, 59, 62] },
  { key: "open_d", es: "Open D", en: "Open D", notes: [38, 45, 50, 54, 57, 62] },
  { key: "dadgad", es: "DADGAD", en: "DADGAD", notes: [38, 45, 50, 55, 57, 62] },
];

function el(id) {
  return document.getElementById(id);
}

function noteNameFromPc(pc) {
  const preferFlat = !!getStaffContext().signature.preferFlats;
  return NOTE_LABELS[state.language][preferFlat ? "flat" : "sharp"][((pc % 12) + 12) % 12];
}

function noteNameFromPcStaff(pc, preferFlat) {
  return NOTE_LABELS[state.language][preferFlat ? "flat" : "sharp"][((pc % 12) + 12) % 12];
}

function tunerTuningDef() {
  return TUNER_TUNINGS.find((t) => t.key === state.tuner.tuningKey) || TUNER_TUNINGS[0];
}

function tunerTuningDisplayName(tuning) {
  const t = tuning || tunerTuningDef();
  return state.language === "es" ? t.es : t.en;
}

function tunerStringOrdinal(index6to1) {
  const n = 6 - Number(index6to1 || 0);
  return state.language === "es" ? `${n}ª` : `${n}th`;
}

function tempoUnitLabel() {
  return tr("tempo_unit");
}

function metronomePresetText(bpm) {
  const v = Math.max(1, Math.min(300, Number(bpm) || 120));
  const table = state.language === "es"
    ? [
        [24, "Larguísimo"],
        [45, "Grave"],
        [60, "Largo"],
        [76, "Lento"],
        [108, "Andante"],
        [120, "Moderato"],
        [156, "Allegro"],
        [176, "Vivace"],
        [200, "Presto"],
        [999, "Prestísimo"],
      ]
    : [
        [24, "Larghissimo"],
        [45, "Grave"],
        [60, "Largo"],
        [76, "Lento"],
        [108, "Andante"],
        [120, "Moderato"],
        [156, "Allegro"],
        [176, "Vivace"],
        [200, "Presto"],
        [999, "Prestissimo"],
      ];
  for (const [limit, label] of table) {
    if (v <= limit) return label;
  }
  return table[table.length - 1][1];
}

function refreshMetronomeTempoInfo() {
  const bpm = Math.max(1, Math.min(300, Number(el("bpm")?.value) || 120));
  const bpmNode = el("bpmValue");
  if (bpmNode) bpmNode.textContent = `${bpm} ${tr("label_bpm")}`;
  const presetNode = el("metroPresetValue");
  if (presetNode) presetNode.textContent = metronomePresetText(bpm);
}

function tr(key) {
  const lang = UI_TEXTS[state.language] || UI_TEXTS.es;
  return lang[key] || UI_TEXTS.es[key] || key;
}

function midiButtonTooltipForState(status = null) {
  const current = status || (state.midi.enabled ? "on" : "off");
  if (current === "secure_required") return tr("midi_requires_secure");
  if (current === "unsupported") return tr("midi_try_chrome");
  if (current === "denied") return tr("midi_help_denied");
  return tr("midi_help_ready");
}

function refreshMidiInputSoundToggleButton() {
  const btn = el("detectMidiSoundToggle");
  if (!btn) return;
  btn.textContent = state.midiInputSoundEnabled ? tr("midi_input_sound_on") : tr("midi_input_sound_off");
  btn.classList.toggle("active", !!state.midiInputSoundEnabled);
}

function refreshMidiToggleButtonState() {
  const btn = el("midiToggle");
  if (!btn) return;
  btn.classList.toggle("active", !!state.midi.enabled);
}

function isSafariBrowser() {
  const ua = String(navigator.userAgent || "");
  const hasSafari = /Safari\//.test(ua);
  const other = /(Chrome|CriOS|Edg|OPR|Firefox|FxiOS|SamsungBrowser|Android)/.test(ua);
  return hasSafari && !other;
}

function refreshMidiStartupModalContent() {
  const text = el("midiStartupText");
  const enableBtn = el("midiStartupEnableBtn");
  const closeBtn = el("midiStartupCloseBtn");
  if (!text || !enableBtn || !closeBtn) return;
  if (isSafariBrowser()) {
    text.textContent = tr("midi_startup_safari_warning");
    enableBtn.classList.add("hidden");
    closeBtn.textContent = tr("close");
  } else {
    text.textContent = tr("midi_startup_text");
    enableBtn.classList.remove("hidden");
    closeBtn.textContent = tr("midi_startup_close");
  }
}

function showMidiStartupModal() {
  const modal = el("midiStartupModal");
  if (!modal || state.midi.enabled) return;
  refreshMidiStartupModalContent();
  modal.classList.remove("hidden");
}

function hideMidiStartupModal() {
  const modal = el("midiStartupModal");
  if (!modal) return;
  modal.classList.add("hidden");
}

function refreshDetectionButtonsState() {
  const hasNotes = (state.activeDetectionNotes?.size || 0) > 0;
  const playBtn = el("detectPlay");
  const clearBtn = el("detectClear");
  if (playBtn) playBtn.disabled = !hasNotes;
  if (clearBtn) clearBtn.disabled = !hasNotes;
}

function applyTranslations() {
  const modeSelect = el("modeSelect");
  if (modeSelect) {
    const opt = (value, key) => {
      const o = modeSelect.querySelector(`option[value="${value}"]`);
      if (o) o.textContent = tr(key);
    };
    opt("detection", "mode_detection");
    opt("generation", "mode_generation");
    opt("scales", "mode_scales");
    opt("metronome", "mode_metronome");
    opt("tuner", "mode_tuner");
  }

  const setText = (id, key) => {
    const node = el(id);
    if (node) node.textContent = tr(key);
  };
  setText("staffHeader", "staff");
  setText("headingDetection", "heading_detection");
  setText("headingGeneration", "heading_generation");
  setText("headingScales", "heading_scales");
  setText("headingMetronome", "heading_metronome");
  setText("headingTuner", "heading_tuner");
  setText("detectionHint", "hint_detection");
  setText("detectClear", "clear");
  setText("labelDetectChord", "label_chord");
  setText("labelDetectNotes", "label_notes");
  setText("labelDetectExtras", "label_extras");
  setText("labelDetectIntervals", "label_intervals");
  setText("labelGenRoot", "label_tonic");
  setText("labelGenVariant", "label_variant");
  setText("labelGenInversion", "label_inversion");
  setText("labelGenChord", "label_chord");
  setText("labelGenNotes", "label_notes");
  setText("labelGenIntervals", "label_intervals");
  setText("labelScaleRoot", "label_tonic");
  setText("labelScaleType", "label_type");
  setText("labelScaleBpm", "label_speed");
  setText("labelScaleName", "label_scale");
  setText("labelScaleNotes", "label_notes");
  setText("labelScaleIntervals", "label_intervals");
  setText("labelMetronomeBpm", "label_metronome_tempo");
  setText("labelMetronomeBeats", "label_beats");
  setText("labelMetronomeSubdivision", "label_subdivision");
  setText("labelMetronomeBarAccent", "label_bar_accent");
  setText("labelMetronomeTimerEnabled", "label_timer_enabled");
  setText("labelMetronomeTimer", "label_timer");
  setText("labelTunerNote", "label_note");
  setText("labelTunerCents", "label_cents");
  setText("labelTunerFreq", "label_freq");
  setText("labelTunerTuning", "label_tuner_tuning");
  setText("labelTunerGain", "label_tuner_gain");
  setText("labelTunerSpectrumRange", "label_tuner_spectrum_range");
  setText("instPianoBtn", "inst_piano");
  setText("instGuitarBtn", "inst_guitar");
  setText("donationTitle", "donation_title");
  setText("donationText", "donation_text");
  setText("donateBtn", "donation_button");
  setText("midiStartupTitle", "midi_startup_title");
  setText("midiStartupText", "midi_startup_text");
  setText("midiStartupEnableBtn", "midi_startup_enable");
  setText("midiStartupCloseBtn", "midi_startup_close");
  refreshMidiStartupModalContent();
  const donateBtn = el("donateBtn");
  if (donateBtn) donateBtn.setAttribute("href", DONATE_URL);

  const right = el("guitarHandedness")?.querySelector('option[value="right"]');
  const left = el("guitarHandedness")?.querySelector('option[value="left"]');
  if (right) right.textContent = tr("guitar_right");
  if (left) left.textContent = tr("guitar_left");
  const handedness = el("guitarHandedness");
  if (handedness) handedness.setAttribute("title", `${tr("inst_guitar")} (${tr("guitar_right")}/${tr("guitar_left")})`);

  const detectPlay = el("detectPlay");
  const genPlay = el("genPlay");
  const scaleModeMetronome = el("scaleModeMetronome");
  if (detectPlay) {
    detectPlay.setAttribute("aria-label", tr("play"));
    detectPlay.setAttribute("title", tr("play"));
  }
  if (genPlay) {
    genPlay.setAttribute("aria-label", tr("play"));
    genPlay.setAttribute("title", tr("play"));
  }
  if (scaleModeMetronome) {
    scaleModeMetronome.setAttribute("aria-label", tr("metronome_mode"));
    scaleModeMetronome.setAttribute("title", tr("metronome_mode"));
  }
  const midiBtn = el("midiToggle");
  if (midiBtn) midiBtn.textContent = state.midi.enabled ? tr("midi_on") : tr("midi_off");
  if (midiBtn) midiBtn.setAttribute("title", midiButtonTooltipForState());
  refreshMidiToggleButtonState();
  refreshMidiInputSoundToggleButton();
  if (el("scaleBpm") && el("scaleBpmValue")) {
    el("scaleBpmValue").textContent = `${el("scaleBpm").value} ${tempoUnitLabel()}`;
  }
  refreshMetronomeTempoInfo();
  updateInversionMax();
  setScalePlayButtonState(!!state.scaleLoop.active);
  setMetronomeToggleButtonState(!!state.metronomeRunning);
  setTunerButtonState(!!state.tuner.running);
  const tunerSel = el("tunerTuning");
  if (tunerSel) {
    const prev = state.tuner.tuningKey;
    tunerSel.innerHTML = "";
    TUNER_TUNINGS.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.key;
      opt.textContent = tunerTuningDisplayName(t);
      tunerSel.appendChild(opt);
    });
    tunerSel.value = TUNER_TUNINGS.some((t) => t.key === prev) ? prev : TUNER_TUNINGS[0].key;
  }
  syncLeftPanelHeader();
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function activeModeSupportsInstrument() {
  return state.mode === "detection" || state.mode === "generation" || state.mode === "scales" || state.mode === "metronome";
}

function activeModeSupportsStaff() {
  return state.mode === "detection" || state.mode === "generation" || state.mode === "scales" || state.mode === "metronome" || state.mode === "tuner";
}

function syncLeftPanelHeader() {
  const header = el("staffHeader");
  if (!header) return;
  if (state.mode === "metronome") header.textContent = tr("mode_metronome");
  else if (state.mode === "tuner") header.textContent = tr("mode_tuner");
  else header.textContent = tr("staff");
}

function renderScaleModeButtons() {
  const metroBtn = el("scaleModeMetronome");
  if (metroBtn) metroBtn.classList.toggle("active", !!state.scaleMetronomeEnabled);
}

function setScalePlayMode(mode) {
  if (!["piano", "guitar"].includes(mode)) mode = "piano";
  state.scalePlayMode = mode;
  renderScaleModeButtons();
  if (state.mode === "scales") setMode("scales");
}

function setMode(mode) {
  stopHeldChord();
  stopAllHeldInputNotes();
  stopAllHeldMidiInputNotes();
  endInputDrag();
  if (state.generationCurrentClearTimer != null) {
    clearTimeout(state.generationCurrentClearTimer);
    state.generationCurrentClearTimer = null;
  }
  state.generationCurrentNote = null;
  if (state.generationPlayClearTimer != null) {
    clearTimeout(state.generationPlayClearTimer);
    state.generationPlayClearTimer = null;
  }
  state.generationPlayingNotes.clear();
  if (state.mode === "scales" && mode !== "scales") stopScaleLoop();
  if (state.mode === "metronome" && mode !== "metronome" && state.metronomeRunning) toggleMetronome();
  if (state.mode === "tuner" && mode !== "tuner" && state.tuner.running) toggleTuner();
  state.mode = mode;
  refreshDetectionButtonsState();
  const modeScreen = el("modeScreen");
  if (modeScreen) {
    modeScreen.classList.remove("mode-detection", "mode-generation", "mode-scales", "mode-metronome", "mode-tuner");
    modeScreen.classList.add(`mode-${mode}`);
  }
  const modeSelect = el("modeSelect");
  if (modeSelect && modeSelect.value !== mode) modeSelect.value = mode;
  syncLeftPanelHeader();

  document.querySelectorAll(".mode-panel").forEach((p) => p.classList.add("hidden"));
  const panelMap = {
    detection: "panelDetection",
    generation: "panelGeneration",
    scales: "panelScales",
    metronome: "panelMetronome",
    tuner: "panelTuner",
  };
  el(panelMap[mode]).classList.remove("hidden");

  const supportsInstrument = activeModeSupportsInstrument();
  const supportsStaff = activeModeSupportsStaff();
  el("instrumentArea").classList.toggle("hidden", !supportsInstrument);
  el("instrumentArea").classList.toggle("with-inst-dock", mode === "generation" || mode === "scales");
  el("instrumentSwitch").classList.toggle("hidden", !supportsInstrument);
  el("staffArea").classList.toggle("hidden", !supportsStaff);
  const showInstrumentToggle = mode === "generation" || mode === "scales";
  document.querySelectorAll(".inst-btn").forEach((btn) => btn.classList.toggle("hidden", !showInstrumentToggle));
  el("guitarHandedness").classList.toggle("hidden", !showInstrumentToggle || state.instrument !== "guitar");
  const guitarVariationBar = el("guitarVariationBar");
  if (guitarVariationBar) guitarVariationBar.classList.toggle("hidden", !(mode === "generation" && state.instrument === "guitar"));
  const tunerSpectrumCanvas = el("tunerSpectrumCanvas");
  if (tunerSpectrumCanvas) tunerSpectrumCanvas.classList.toggle("hidden", mode !== "tuner");
  if (mode === "tuner") {
    el("instrumentArea").classList.remove("hidden");
    el("sharedPiano").classList.add("hidden");
    el("sharedGuitarCanvas").classList.add("hidden");
    if (guitarVariationBar) guitarVariationBar.classList.add("hidden");
  }

  if (mode === "detection") {
    setInstrument("piano");
  } else if (mode === "metronome") {
    setInstrument("piano");
  } else if (mode === "scales") {
    if (state.scalePlayMode === "guitar") setInstrument("guitar");
    else if (state.scalePlayMode === "piano") setInstrument("piano");
  }

  if (supportsInstrument) {
    setInstrument(state.instrument);
    renderInstrument();
    renderStaff();
  } else if (mode === "tuner") {
    renderStaff();
    renderTunerSpectrumPanel();
  } else if (supportsStaff) {
    renderStaff();
  } else if (mode === "metronome") {
    renderMetronomeDots();
  }
  refreshGenerationInversionControlState();
  renderScaleModeButtons();
}

function backToMenu() {
  setMode("detection");
}

function setInstrument(inst) {
  state.instrument = inst;
  if (state.mode === "scales" && (inst === "piano" || inst === "guitar")) {
    state.scalePlayMode = inst;
    renderScaleModeButtons();
  }
  if (state.mode === "tuner") {
    el("instrumentArea").classList.remove("guitar-active");
    el("sharedPiano").classList.add("hidden");
    el("sharedGuitarCanvas").classList.add("hidden");
    const tunerSpectrumCanvasOnly = el("tunerSpectrumCanvas");
    if (tunerSpectrumCanvasOnly) tunerSpectrumCanvasOnly.classList.remove("hidden");
    el("guitarHandedness").classList.add("hidden");
    const guitarVariationBarOnly = el("guitarVariationBar");
    if (guitarVariationBarOnly) guitarVariationBarOnly.classList.add("hidden");
    return;
  }
  document.querySelectorAll(".inst-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.inst === inst);
  });
  el("instrumentArea").classList.toggle("guitar-active", inst === "guitar");
  el("sharedPiano").classList.toggle("hidden", inst !== "piano");
  el("sharedGuitarCanvas").classList.toggle("hidden", inst !== "guitar");
  const tunerSpectrumCanvas = el("tunerSpectrumCanvas");
  if (tunerSpectrumCanvas) tunerSpectrumCanvas.classList.add("hidden");
  el("guitarHandedness").classList.toggle("hidden", inst !== "guitar");
  const guitarVariationBar = el("guitarVariationBar");
  if (guitarVariationBar) guitarVariationBar.classList.toggle("hidden", !(state.mode === "generation" && inst === "guitar"));
  if (state.mode === "generation" && inst === "guitar" && state.generatedChord && !state.guitarVariations.length) {
    loadGuitarVariations().then(() => {
      renderInstrument();
      renderStaff();
    }).catch(() => {});
  }
  refreshGenerationInversionControlState();
  renderGuitarVariationButtons();
}

function renderGuitarVariationButtons() {
  const bar = el("guitarVariationBar");
  if (!bar) return;
  bar.innerHTML = "";
  const show = state.mode === "generation" && state.instrument === "guitar" && state.guitarVariations.length > 0;
  bar.classList.toggle("hidden", !show);
  if (!show) return;
  state.guitarVariations.forEach((_variation, idx) => {
    const btn = document.createElement("button");
    btn.className = "guitar-var-btn";
    if (idx === state.guitarSelectedVariationIdx) btn.classList.add("active");
    btn.textContent = String(idx + 1);
    btn.addEventListener("click", () => {
      state.guitarSelectedVariationIdx = idx;
      renderGuitarVariationButtons();
      renderInstrument();
      renderStaff();
    });
    bar.appendChild(btn);
  });
}

function variationBassPc(variation) {
  const stringNotes = variation?.string_notes;
  if (Array.isArray(stringNotes) && stringNotes.length >= 6) {
    for (const note of stringNotes) {
      if (note != null) return Number(note) % 12;
    }
  }
  const frets = variation?.frets;
  if (Array.isArray(frets) && frets.length >= 6) {
    const tuning = [40, 45, 50, 55, 59, 64]; // 6->1
    for (let i = 0; i < frets.length; i += 1) {
      const fret = Number(frets[i]);
      if (Number.isFinite(fret) && fret >= 0) return (tuning[i] + fret) % 12;
    }
  }
  const notes = variation?.notes;
  if (Array.isArray(notes) && notes.length) {
    return Number(Math.min(...notes.map((n) => Number(n)))) % 12;
  }
  return null;
}

async function getVariationsFromClientCache(rootPc, suffix, inversion) {
  if (!state.guitarChordCache) {
    const cache = await fetchJson("/static/guitar_chord_cache.json");
    state.guitarChordCache = cache;
  }
  const byKey = state.guitarChordCache?.by_app_key;
  if (!byKey || typeof byKey !== "object") return [];
  const key = `${Number(rootPc) % 12}|${suffix || ""}`;
  let variations = Array.isArray(byKey[key]) ? [...byKey[key]] : [];
  const pattern = state.chordPatterns.find((p) => p.suffix === suffix);
  if (pattern && variations.length) {
    const intervals = Array.isArray(pattern.intervals) ? pattern.intervals : [];
    if (intervals.length) {
      const inversionIdx = Math.min(Math.max(0, Number(inversion) || 0), intervals.length - 1);
      const targetBassPc = (Number(rootPc) + Number(intervals[inversionIdx])) % 12;
      const filtered = variations.filter((v) => variationBassPc(v) === targetBassPc);
      if (filtered.length) variations = filtered;
    }
  }
  return variations;
}

async function loadGuitarVariations() {
  if (!state.generatedChord) {
    state.guitarVariations = [];
    state.guitarSelectedVariationIdx = null;
    renderGuitarVariationButtons();
    return;
  }
  try {
    const payload = {
      root_pc: Number(state.generatedChord.root_pc || 0),
      suffix: String(state.generatedChord.suffix || ""),
      inversion: Number(state.generatedChord.inversion || 0),
    };
    const out = await fetchJson("/api/generate/guitar-variations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.guitarVariations = Array.isArray(out.variations) ? out.variations : [];
    if (!state.guitarVariations.length) {
      state.guitarVariations = await getVariationsFromClientCache(payload.root_pc, payload.suffix, payload.inversion);
    }
    if (!state.guitarVariations.length) {
      state.guitarSelectedVariationIdx = null;
    } else if (state.guitarSelectedVariationIdx == null || state.guitarSelectedVariationIdx >= state.guitarVariations.length) {
      state.guitarSelectedVariationIdx = 0;
    }
  } catch (_err) {
    try {
      const payload = {
        root_pc: Number(state.generatedChord.root_pc || 0),
        suffix: String(state.generatedChord.suffix || ""),
        inversion: Number(state.generatedChord.inversion || 0),
      };
      state.guitarVariations = await getVariationsFromClientCache(payload.root_pc, payload.suffix, payload.inversion);
      state.guitarSelectedVariationIdx = state.guitarVariations.length ? 0 : null;
    } catch (_err2) {
      state.guitarVariations = [];
      state.guitarSelectedVariationIdx = null;
    }
  }
  renderGuitarVariationButtons();
}

function getActivePcsForMode() {
  if (state.mode === "generation" && state.generatedChord) {
    return new Set((state.generatedChord.notes_midi || []).map((n) => Number(n) % 12));
  }
  if (state.mode === "scales" && state.generatedScale) {
    return new Set((state.generatedScale.notes_midi || []).map((n) => Number(n) % 12));
  }
  if (state.mode === "detection") {
    return new Set(Array.from(state.activeDetectionNotes).map((n) => Number(n) % 12));
  }
  return new Set();
}

function getActiveMidiForMode() {
  if (state.mode === "generation" && state.generatedChord) {
    return new Set((state.generatedChord.notes_midi || []).map((n) => Number(n)));
  }
  if (state.mode === "scales" && state.generatedScale) {
    return new Set((state.generatedScale.notes_midi || []).map((n) => Number(n)));
  }
  if (state.mode === "detection") {
    return new Set(Array.from(state.activeDetectionNotes));
  }
  if (state.mode === "metronome") {
    return new Set(Array.from(state.activeMidiLiveNotes));
  }
  return new Set();
}

function getScaleBaseNotes() {
  if (!state.generatedScale || !Array.isArray(state.generatedScale.notes_midi)) return [];
  const base = Array.from(new Set(state.generatedScale.notes_midi.map((n) => Number(n))))
    .filter((n) => Number.isFinite(n))
    .sort((a, b) => a - b);
  const guitarScaleMode = state.mode === "scales" && getScalePlaybackInstrument() === "guitar";
  if (!guitarScaleMode || !base.length || state.scaleGuitarStartNote == null) return base;
  const start = Number(state.scaleGuitarStartNote);
  if (!Number.isFinite(start)) return base;
  const first = Number(base[0]);
  if ((((start % 12) + 12) % 12) !== (((first % 12) + 12) % 12)) return base;
  const delta = start - first;
  return base.map((n) => Number(n) + delta).filter((n) => Number.isFinite(n));
}

function setScaleGuitarStartNote(note) {
  const target = Number(note);
  if (!Number.isFinite(target) || !state.generatedScale || !Array.isArray(state.generatedScale.notes_midi)) return;
  const base = state.generatedScale.notes_midi.map((n) => Number(n)).filter((n) => Number.isFinite(n)).sort((a, b) => a - b);
  if (!base.length) return;
  const first = Number(base[0]);
  if ((((target % 12) + 12) % 12) !== (((first % 12) + 12) % 12)) return;
  state.scaleGuitarStartNote = target;
  if (state.scaleLoop.active) stopScaleLoop();
  state.scaleCurrentNote = null;
  state.scaleInputRawNote = null;
  renderInstrument();
  renderStaff();
}

function getScalePlaybackInstrument() {
  if (state.mode === "scales" && (state.instrument === "piano" || state.instrument === "guitar")) {
    if (state.scalePlayMode !== state.instrument) {
      state.scalePlayMode = state.instrument;
      renderScaleModeButtons();
    }
    return state.instrument;
  }
  return state.scalePlayMode === "guitar" ? "guitar" : "piano";
}

function getScaleRhLhDisplayNotes(includeBass = true) {
  const rh = getScaleBaseNotes();
  if (!includeBass) {
    return { rh, lh: [], display: [...rh] };
  }
  const firstRh = rh.length ? Number(rh[0]) : null;
  const lh = rh
    .map((n) => n - 12)
    .filter((n) => n >= 0 && (firstRh == null || n < firstRh));
  const display = [];
  const pairCount = Math.min(rh.length, lh.length);
  for (let i = 0; i < pairCount; i += 1) {
    display.push(lh[i], rh[i]);
  }
  for (let i = pairCount; i < rh.length; i += 1) display.push(rh[i]);
  return { rh, lh, display };
}

function mapScaleInputToDisplayMidi(note, options = {}) {
  const target = Number(note);
  if (!Number.isFinite(target)) return null;
  const includeBass = options.includeBass != null ? !!options.includeBass : (getScalePlaybackInstrument() === "piano");
  const { rh, lh } = getScaleRhLhDisplayNotes(includeBass);
  const candidates = includeBass ? [...rh, ...lh] : [...rh];
  if (!candidates.length) return null;
  if (candidates.includes(target)) return target;
  const targetPc = ((target % 12) + 12) % 12;
  const samePc = candidates.filter((n) => (((n % 12) + 12) % 12) === targetPc);
  if (!samePc.length) return null;
  return samePc.reduce((best, n) => (
    Math.abs(n - target) < Math.abs(best - target) ? n : best
  ), samePc[0]);
}

function getExtraMidiForMode() {
  if (state.mode === "detection" && state.detectionResult) {
    return new Set((state.detectionResult.extras_midi || []).map((n) => Number(n)));
  }
  return new Set();
}

function formatIntervalsFromMidi(notesMidi) {
  const ordered = Array.from(new Set((notesMidi || []).map((n) => Number(n)))).sort((a, b) => a - b);
  if (ordered.length === 0) return "-";
  const base = ordered[0];
  return ordered.map((n) => `+${n - base}`).join(" - ");
}

function pianoFingeringForCount(count, hand) {
  const n = Math.max(1, Number(count) || 1);
  if (hand === "right") {
    const templates = {
      1: [1],
      2: [1, 3],
      3: [1, 3, 5],
      4: [1, 2, 4, 5],
      5: [1, 2, 3, 4, 5],
    };
    if (templates[n]) return templates[n];
    return Array.from({ length: n }, (_, i) => Math.min(5, i + 1));
  }
  const templates = {
    1: [5],
    2: [5, 3],
    3: [5, 3, 1],
    4: [5, 3, 2, 1],
    5: [5, 4, 3, 2, 1],
  };
  if (templates[n]) return templates[n];
  return Array.from({ length: n }, (_, i) => Math.max(1, 5 - i));
}

function inversionLabel(inversion) {
  const inv = Number(inversion) || 0;
  if (inv === 0) {
    return tr("inversion_root");
  }
  if (state.language === "es") return `${inv}${tr("inversion_suffix")}`;
  const ordMap = { 1: "1st", 2: "2nd", 3: "3rd" };
  const ord = ordMap[inv] || `${inv}th`;
  return `${ord} ${tr("inversion_word")}`;
}

function renderInstrument() {
  if (state.mode === "tuner") {
    renderTunerSpectrumPanel();
    return;
  }
  if (!activeModeSupportsInstrument()) return;
  if (state.instrument === "guitar") renderGuitar();
  else renderPiano();
}

function renderPiano() {
  const container = el("sharedPiano");
  container.innerHTML = "";
  const low = 33;
  const high = 120;
  const blackPcs = new Set([1, 3, 6, 8, 10]);
  const activeMidi = getActiveMidiForMode();
  const activePcs = getActivePcsForMode();
  const extraMidi = getExtraMidiForMode();
  const tonicPc = state.mode === "scales" && state.generatedScale ? Number(state.generatedScale.tonic_pc) : null;
  const scaleCurrentPc = state.mode === "scales" && state.scaleCurrentNote != null
    ? ((Number(state.scaleCurrentNote) % 12) + 12) % 12
    : null;
  let scaleCurrentDisplayMidi = null;
  if (state.mode === "scales" && state.scaleCurrentNote != null) {
    scaleCurrentDisplayMidi = Number(state.scaleCurrentNote);
    while (scaleCurrentDisplayMidi < 60) scaleCurrentDisplayMidi += 12;
    while (scaleCurrentDisplayMidi > 72) scaleCurrentDisplayMidi -= 12;
  }
  const scaleCurrentExactMidi = state.mode === "scales" && state.scaleCurrentNote != null
    ? Number(state.scaleCurrentNote)
    : null;
  const scaleInputRawMidi = state.mode === "scales" && state.scaleInputRawNote != null
    ? Number(state.scaleInputRawNote)
    : null;
  const generationPianoMode = state.mode === "generation" && state.instrument === "piano" && state.generatedChord;
  const scalePianoMode = state.mode === "scales" && getScalePlaybackInstrument() === "piano";
  const rhNotes = generationPianoMode
    ? Array.from(new Set((state.generatedChord.notes_midi || []).map((n) => Number(n)))).sort((a, b) => a - b)
    : [];
  const lhNotes = generationPianoMode
    ? rhNotes.map((n) => n - 12).filter((n) => n >= low && n <= high)
    : [];
  const rhFingers = pianoFingeringForCount(rhNotes.length, "right");
  const lhFingers = pianoFingeringForCount(lhNotes.length, "left");
  const rhFingerByNote = new Map(rhNotes.map((n, i) => [n, rhFingers[Math.min(i, rhFingers.length - 1)]]));
  const lhFingerByNote = new Map(lhNotes.map((n, i) => [n, lhFingers[Math.min(i, lhFingers.length - 1)]]));
  const allActiveMidi = generationPianoMode ? new Set([...activeMidi, ...lhNotes]) : activeMidi;
  const scaleRhLh = scalePianoMode ? getScaleRhLhDisplayNotes() : { rh: [], lh: [], display: [] };
  const scaleRhSet = new Set(scaleRhLh.rh);
  const scaleLhSet = new Set(scaleRhLh.lh);
  const scaleDisplaySet = new Set(scaleRhLh.display.map((n) => Number(n)));
  const scaleRawOutsideDisplay = scalePianoMode
    && scaleInputRawMidi != null
    && !scaleDisplaySet.has(scaleInputRawMidi);
  const scaleCentralOnly = state.mode === "scales" && state.scaleLoop.active;
  const scaleCentralMin = 60; // C4
  const scaleCentralMax = 72; // C5

  for (let midi = low; midi <= high; midi += 1) {
    const pc = midi % 12;
    const black = blackPcs.has(pc);
    const scaleMarked = state.mode === "scales" && activePcs.has(pc);
    const scaleTonic = scaleMarked && tonicPc !== null && pc === tonicPc;
    const scaleCurrent = scaleMarked && (
      scaleCentralOnly
        ? (scaleCurrentDisplayMidi !== null && midi === scaleCurrentDisplayMidi)
        : (
          (scaleCurrentExactMidi !== null && midi === scaleCurrentExactMidi)
          || (scaleInputRawMidi == null && scaleCurrentDisplayMidi !== null && midi === scaleCurrentDisplayMidi)
        )
    );
    const key = document.createElement("button");
    key.className = `key ${black ? "black" : ""}`;
    if (generationPianoMode) {
      if (rhFingerByNote.has(midi)) key.classList.add("rh");
      if (lhFingerByNote.has(midi)) key.classList.add("lh");
    } else if (state.mode === "detection") {
      if (activeMidi.has(midi)) key.classList.add("active");
    } else if (scalePianoMode) {
      const mappedOnKey = scaleCurrentExactMidi !== null && midi === scaleCurrentExactMidi;
      const rawOnKey = scaleInputRawMidi !== null && midi === scaleInputRawMidi;
      if (mappedOnKey) {
        if (scaleLhSet.has(midi) && !scaleRhSet.has(midi)) key.classList.add("lh");
        else key.classList.add("rh");
      }
      if (rawOnKey && scaleRawOutsideDisplay) key.classList.add("active");
    } else if (state.mode !== "scales" && allActiveMidi.has(midi)) {
      key.classList.add("active");
    }
    if (extraMidi.has(midi)) key.classList.add("extra");
    if (state.mode === "scales" && scaleCurrent) {
      const keepYellow = !scalePianoMode || (scaleRawOutsideDisplay && scaleInputRawMidi === midi);
      if (keepYellow) key.classList.add("active");
    }
    if (state.mode !== "scales" && tonicPc !== null && pc === tonicPc) key.classList.add("tonic");
    key.dataset.midi = String(midi);
    key.innerHTML = `<span class="key-label">${noteNameFromPc(pc)}</span>`;

    if (generationPianoMode) {
      const rhFinger = rhFingerByNote.get(midi);
      const lhFinger = lhFingerByNote.get(midi);
      if (rhFinger != null) {
        const badge = document.createElement("div");
        badge.className = `finger-badge ${black ? "black-key" : "white-key"}`;
        badge.textContent = String(rhFinger);
        key.appendChild(badge);
      } else if (lhFinger != null) {
        const badge = document.createElement("div");
        badge.className = `finger-badge ${black ? "black-key" : "white-key"}`;
        badge.textContent = String(lhFinger);
        key.appendChild(badge);
      }
    } else if (state.mode === "scales" && scaleMarked) {
      const badge = document.createElement("span");
      badge.className = `scale-badge ${black ? "black-key" : "white-key"} ${scaleTonic ? "tonic" : ""} ${scaleCurrent ? "current" : ""}`;
      badge.textContent = noteNameFromPc(pc);
      key.appendChild(badge);
    }

    let suppressNextClick = false;
    const releasePressed = () => endInputDrag();
    const triggerKeyPress = () => handleInstrumentNote(midi);
    key.addEventListener("mousedown", (event) => {
      if (Number(event.button) !== 0) return;
      suppressNextClick = true;
      event.preventDefault();
      beginInputDrag(midi, "piano");
      const onReleaseDoc = () => releasePressed();
      document.addEventListener("mouseup", onReleaseDoc, { once: true });
      document.addEventListener("touchend", onReleaseDoc, { once: true, passive: true });
      document.addEventListener("touchcancel", onReleaseDoc, { once: true, passive: true });
    });
    key.addEventListener("touchstart", (event) => {
      suppressNextClick = true;
      event.preventDefault();
      beginInputDrag(midi, "piano");
      const onReleaseDoc = () => releasePressed();
      document.addEventListener("mouseup", onReleaseDoc, { once: true });
      document.addEventListener("touchend", onReleaseDoc, { once: true, passive: true });
      document.addEventListener("touchcancel", onReleaseDoc, { once: true, passive: true });
    }, { passive: false });
    key.addEventListener("mouseenter", (event) => {
      if (!state.inputDragActive) return;
      if ((Number(event.buttons) & 1) === 0) return;
      updateInputDrag(midi, "piano");
    });
    key.addEventListener("mouseup", releasePressed);
    key.addEventListener("touchend", releasePressed, { passive: true });
    key.addEventListener("touchcancel", releasePressed, { passive: true });
    key.addEventListener("click", (event) => {
      if (suppressNextClick) {
        suppressNextClick = false;
        event.preventDefault();
        return;
      }
      triggerKeyPress();
    });
    container.appendChild(key);
  }
}

function renderGuitar() {
  const canvas = el("sharedGuitarCanvas");
  const ctx = canvas.getContext("2d");
  const width = Math.max(980, canvas.clientWidth || canvas.width);
  const height = Math.max(220, canvas.clientHeight || canvas.height);
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;

  const rightTuning = [64, 59, 55, 50, 45, 40];
  const rightNames = ["E", "B", "G", "D", "A", "E"];
  const tuning = state.guitarHandedness === "left" ? [...rightTuning].reverse() : rightTuning;
  const stringNames = state.guitarHandedness === "left" ? [...rightNames].reverse() : rightNames;
  const frets = 14;
  const activeMidi = getActiveMidiForMode();
  const activePcs = getActivePcsForMode();
  const extraMidi = getExtraMidiForMode();
  const leftHanded = state.guitarHandedness === "left";
  const chordRootPc = state.generatedChord ? Number(state.generatedChord.root_pc) : null;
  const tonicPc = state.generatedScale ? Number(state.generatedScale.tonic_pc) : null;
  const drawnPcs = state.mode === "detection" ? null : activePcs;
  const generationVariationMode = state.mode === "generation" && state.instrument === "guitar" && state.guitarSelectedVariationIdx != null
    && state.guitarSelectedVariationIdx >= 0 && state.guitarSelectedVariationIdx < state.guitarVariations.length;
  const selectedVariation = generationVariationMode ? state.guitarVariations[state.guitarSelectedVariationIdx] : null;
  const variationFretsRaw = selectedVariation && Array.isArray(selectedVariation.frets) ? selectedVariation.frets.map((n) => Number(n)) : [];
  const variationFingersRaw = selectedVariation && Array.isArray(selectedVariation.fingers) ? selectedVariation.fingers.map((n) => Number(n)) : [];
  const displayFrets = leftHanded ? variationFretsRaw : [...variationFretsRaw].reverse();
  const displayFingers = leftHanded ? variationFingersRaw : [...variationFingersRaw].reverse();

  ctx.fillStyle = "#f9f9f7";
  ctx.fillRect(0, 0, width, height);

  const boardPad = 20;
  const nutMargin = 72;
  const stringBand = Math.max(116, Math.min(148, height * 0.56));
  const top = Math.round((height - stringBand) / 2);
  const bottom = Math.round(top + stringBand);
  const nutX = leftHanded ? width - nutMargin : nutMargin;
  const boardEdgeX = leftHanded ? boardPad : width - boardPad;
  const step = Math.abs(boardEdgeX - nutX) / frets;
  const dir = leftHanded ? -1 : 1;
  const openX = nutX - dir * (step * 0.5);
  const yGap = (bottom - top) / (tuning.length - 1);
  const fretCenterX = (fret) => (fret <= 0 ? (openX + nutX) / 2 : nutX + dir * (fret - 0.5) * step);

  ctx.fillStyle = "#34363c";
  ctx.strokeStyle = "#4a4f58";
  ctx.lineWidth = 1;
  ctx.fillRect(Math.min(nutX, boardEdgeX), top - 10, Math.abs(boardEdgeX - nutX), bottom - top + 20);
  ctx.strokeRect(Math.min(nutX, boardEdgeX), top - 10, Math.abs(boardEdgeX - nutX), bottom - top + 20);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(Math.min(openX, nutX), top - 10, Math.abs(nutX - openX), bottom - top + 20);
  ctx.strokeStyle = "#c8b79f";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(nutX, top - 10);
  ctx.lineTo(nutX, bottom + 10);
  ctx.stroke();

  for (let fret = 1; fret <= frets; fret += 1) {
    const x = nutX + dir * fret * step;
    ctx.strokeStyle = "#c8b79f";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, top - 10);
    ctx.lineTo(x, bottom + 10);
    ctx.stroke();
    ctx.strokeStyle = "#8f8576";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x + (dir > 0 ? 2 : -2), top - 10);
    ctx.lineTo(x + (dir > 0 ? 2 : -2), bottom + 10);
    ctx.stroke();
  }

  ctx.fillStyle = "#222";
  ctx.font = "bold 13px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (let fret = 0; fret < frets; fret += 1) {
    const x = fret <= 0 ? (openX + nutX) / 2 : nutX + dir * (fret - 0.5) * step;
    ctx.fillText(String(fret), x, 16);
  }
  ctx.textAlign = "start";
  ctx.textBaseline = "alphabetic";

  const barreSegments = [];
  const barreCovered = new Set();
  if (generationVariationMode && displayFrets.length >= 6 && displayFingers.length >= 6) {
    const soundedIdxs = [];
    for (let i = 0; i < displayFrets.length; i += 1) {
      if (Number(displayFrets[i]) >= 0) soundedIdxs.push(i);
    }
    const minSounded = soundedIdxs.length ? Math.min(...soundedIdxs) : 0;
    const maxSounded = soundedIdxs.length ? Math.max(...soundedIdxs) : 0;
    const uniqueFrets = Array.from(new Set(displayFrets.filter((f) => Number(f) > 0))).sort((a, b) => a - b);

    uniqueFrets.forEach((fretValue) => {
      const idxs = [];
      for (let i = 0; i < displayFrets.length; i += 1) {
        if (Number(displayFrets[i]) === Number(fretValue) && Number(displayFingers[i]) > 0) idxs.push(i);
      }
      if (idxs.length < 2) return;

      // Full barre: first and last sounding strings are covered at same fret.
      if (idxs[0] === minSounded && idxs[idxs.length - 1] === maxSounded) {
        const finger = Number(displayFingers[idxs[0]] || 1);
        const covered = new Set(idxs);
        barreSegments.push({ fret: Number(fretValue), finger, start: idxs[0], end: idxs[idxs.length - 1], covered });
        idxs.forEach((idx) => barreCovered.add(idx));
        return;
      }

      // Partial barre(s): contiguous runs with at least 2 strings.
      let runStart = idxs[0];
      let runPrev = idxs[0];
      for (let j = 1; j < idxs.length; j += 1) {
        const idx = idxs[j];
        if (idx === runPrev + 1) {
          runPrev = idx;
          continue;
        }
        if ((runPrev - runStart + 1) >= 2) {
          const finger = Number(displayFingers[runStart] || 1);
          const covered = new Set();
          for (let s = runStart; s <= runPrev; s += 1) covered.add(s);
          barreSegments.push({ fret: Number(fretValue), finger, start: runStart, end: runPrev, covered });
          for (let s = runStart; s <= runPrev; s += 1) barreCovered.add(s);
        }
        runStart = idx;
        runPrev = idx;
      }
      if ((runPrev - runStart + 1) >= 2) {
        const finger = Number(displayFingers[runStart] || 1);
        const covered = new Set();
        for (let s = runStart; s <= runPrev; s += 1) covered.add(s);
        barreSegments.push({ fret: Number(fretValue), finger, start: runStart, end: runPrev, covered });
        for (let s = runStart; s <= runPrev; s += 1) barreCovered.add(s);
      }
    });
  }

  state.guitarHitRegions = [];

  // Draw barre bars before individual finger circles.
  barreSegments.forEach((seg) => {
    const x = fretCenterX(seg.fret);
    const y1 = top + (seg.start * yGap);
    const y2 = top + (seg.end * yGap);
    const barW = Math.max(12, Math.min(18, yGap * 0.70));
    ctx.strokeStyle = "#f7b500";
    ctx.lineWidth = barW;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.stroke();
    ctx.lineCap = "butt";

    // On barres, draw one marker per sounding string, preserving tonic color.
    for (let stringIdx = seg.start; stringIdx <= seg.end; stringIdx += 1) {
      if (!seg.covered.has(stringIdx)) continue;
      const note = Number(tuning[stringIdx]) + Number(seg.fret);
      const pc = ((note % 12) + 12) % 12;
      const y = top + (stringIdx * yGap);
      const isRoot = chordRootPc !== null && pc === chordRootPc;
      ctx.fillStyle = isRoot ? "#b35f00" : "#f4a742";
      ctx.strokeStyle = "#2e2e2e";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(x, y, 10.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = isRoot ? "#ffffff" : "#1f1200";
      ctx.font = "bold 10px sans-serif";
      ctx.fillText(String(seg.finger > 0 ? seg.finger : 1), x - 3, y + 3);
    }
  });

  tuning.forEach((openNote, i) => {
    const y = top + i * yGap;
    ctx.strokeStyle = "#bdbdbd";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(Math.min(openX, boardEdgeX), y);
    ctx.lineTo(Math.max(openX, boardEdgeX), y);
    ctx.stroke();
    ctx.strokeStyle = "#8a8a8a";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(Math.min(openX, boardEdgeX), y + 1);
    ctx.lineTo(Math.max(openX, boardEdgeX), y + 1);
    ctx.stroke();
    ctx.fillStyle = "#111";
    ctx.font = "bold 11px sans-serif";
    ctx.textBaseline = "middle";
    if (leftHanded) {
      ctx.textAlign = "left";
      const rightEdge = Math.max(openX, boardEdgeX);
      ctx.fillText(stringNames[i], Math.min(width - 2, rightEdge + 10), y);
    } else {
      ctx.textAlign = "right";
      const leftEdge = Math.min(openX, boardEdgeX);
      ctx.fillText(stringNames[i], Math.max(2, leftEdge - 10), y);
    }
    ctx.textAlign = "start";

    for (let fret = 0; fret < frets; fret += 1) {
      if (generationVariationMode) {
        const selectedFret = Number(displayFrets[i]);
        if (!Number.isFinite(selectedFret) || selectedFret < 0 || selectedFret >= frets || fret !== selectedFret) continue;
        const note = openNote + fret;
        const pc = note % 12;
        const cx = fretCenterX(fret);
        const isRoot = chordRootPc !== null && pc === chordRootPc;
        const finger = Number(displayFingers[i] || 0);
        const coveredByBarre = fret > 0 && barreCovered.has(i);
        state.guitarHitRegions.push({ note, x: cx, y, r: 12, tonic: false });
        if (coveredByBarre) continue;
        ctx.fillStyle = isRoot ? "#b35f00" : "#f4a742";
        ctx.strokeStyle = "#f1c27d";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(cx, y, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = isRoot ? "#ffffff" : "#1f1200";
        ctx.font = "bold 10px sans-serif";
        ctx.fillText(String(finger > 0 ? finger : 1), cx - 3, y + 3);
        continue;
      }
      const note = openNote + fret;
      const pc = note % 12;
      const cx = fretCenterX(fret);
      const inSet = state.mode === "detection" ? activeMidi.has(note) : drawnPcs.has(pc);
      const detectionMode = state.mode === "detection";
      if (!detectionMode && !inSet) continue;
      const isExtra = extraMidi.has(note);
      const isRoot = (state.mode === "generation" && chordRootPc !== null && pc === chordRootPc)
        || (state.mode === "scales" && tonicPc !== null && pc === tonicPc);
      const isCurrentScale = state.mode === "scales"
        && state.scaleCurrentNote != null
        && Number(note) === Number(state.scaleCurrentNote);

      if (detectionMode && !inSet) {
        ctx.fillStyle = "#e5e7eb";
        ctx.strokeStyle = "#aab1bc";
      } else if (isCurrentScale) {
        ctx.fillStyle = "#2faeff";
        ctx.strokeStyle = "#4fd4ff";
      } else {
        ctx.fillStyle = isExtra ? "#f48f8f" : isRoot ? "#52d16f" : "#ffd46a";
        ctx.strokeStyle = isExtra ? "#a13737" : isRoot ? "#1e8c38" : "#c69928";
      }
      ctx.lineWidth = detectionMode && !inSet ? 1 : 1.2;
      ctx.beginPath();
      ctx.arc(cx, y, 11, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      if (inSet) {
        ctx.fillStyle = isCurrentScale ? "#f2f8ff" : "#121a26";
        ctx.font = "bold 10px sans-serif";
        const label = noteNameFromPc(pc);
        ctx.fillText(label, cx - (label.length * 2.8), y + 3);
      } else if (detectionMode) {
        ctx.fillStyle = "#8b93a0";
        ctx.font = "bold 10px sans-serif";
        ctx.fillText("•", cx - 2, y + 3);
      }

      if (detectionMode || inSet) {
        const isScaleTonic = state.mode === "scales" && tonicPc !== null && ((note % 12 + 12) % 12) === ((tonicPc % 12 + 12) % 12);
        state.guitarHitRegions.push({ note, x: cx, y, r: 12, tonic: isScaleTonic });
      }
    }
  });

  let suppressCanvasClick = false;
  const releaseCanvasPress = () => endInputDrag();
  const triggerGuitarPress = (event) => {
    const rect = canvas.getBoundingClientRect();
    const point = event.touches && event.touches.length ? event.touches[0] : event;
    const x = ((point.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((point.clientY - rect.top) / rect.height) * canvas.height;
    return state.guitarHitRegions.find((h) => ((x - h.x) ** 2) + ((y - h.y) ** 2) <= (h.r ** 2)) || null;
  };
  canvas.onmousedown = (event) => {
    if (Number(event.button) !== 0) return;
    suppressCanvasClick = true;
    event.preventDefault();
    const hit = triggerGuitarPress(event);
    if (hit && state.mode === "scales" && getScalePlaybackInstrument() === "guitar" && state.shiftPressed && hit.tonic) {
      setScaleGuitarStartNote(Number(hit.note));
    }
    if (hit) {
      beginInputDrag(Number(hit.note), "guitar");
      const onReleaseDoc = () => releaseCanvasPress();
      document.addEventListener("mouseup", onReleaseDoc, { once: true });
      document.addEventListener("touchend", onReleaseDoc, { once: true, passive: true });
      document.addEventListener("touchcancel", onReleaseDoc, { once: true, passive: true });
    }
  };
  canvas.ontouchstart = (event) => {
    suppressCanvasClick = true;
    event.preventDefault();
    const hit = triggerGuitarPress(event);
    if (hit) {
      beginInputDrag(Number(hit.note), "guitar");
      const onReleaseDoc = () => releaseCanvasPress();
      document.addEventListener("mouseup", onReleaseDoc, { once: true });
      document.addEventListener("touchend", onReleaseDoc, { once: true, passive: true });
      document.addEventListener("touchcancel", onReleaseDoc, { once: true, passive: true });
    }
  };
  canvas.onmousemove = (event) => {
    if (!state.inputDragActive) return;
    if ((Number(event.buttons) & 1) === 0) return;
    const hit = triggerGuitarPress(event);
    if (hit) updateInputDrag(Number(hit.note), "guitar");
  };
  canvas.ontouchmove = (event) => {
    if (!state.inputDragActive) return;
    event.preventDefault();
    const hit = triggerGuitarPress(event);
    if (hit) updateInputDrag(Number(hit.note), "guitar");
  };
  canvas.onmouseup = releaseCanvasPress;
  canvas.onmouseleave = releaseCanvasPress;
  canvas.ontouchend = releaseCanvasPress;
  canvas.ontouchcancel = releaseCanvasPress;
  canvas.onclick = (event) => {
    if (suppressCanvasClick) {
      suppressCanvasClick = false;
      event.preventDefault();
      return;
    }
    const hit = triggerGuitarPress(event);
    if (hit) handleInstrumentNote(Number(hit.note));
  };
}

function handleInstrumentNote(note, options = {}) {
  const pressed = !!options.pressed;
  const instrumentHint = options.instrumentHint || null;
  const released = !!options.released;
  if (state.mode === "detection") {
    if (pressed) {
      detectionManualPress(note, { instrumentHint });
    } else if (released) {
      detectionManualRelease(note);
    } else {
      playSingle(Number(note), instrumentHint || (state.instrument === "guitar" ? "guitar" : "piano"));
      return;
    }
    return;
  }
  if (state.mode === "generation" && state.generatedChord) {
    const setGenerationCurrent = (midi) => {
      if (state.generationCurrentClearTimer != null) {
        clearTimeout(state.generationCurrentClearTimer);
        state.generationCurrentClearTimer = null;
      }
      state.generationCurrentNote = Number(midi);
      renderStaff();
      state.generationCurrentClearTimer = setTimeout(() => {
        state.generationCurrentNote = null;
        state.generationCurrentClearTimer = null;
        if (state.mode === "generation") renderStaff();
      }, 720);
    };
    if (state.instrument === "piano") {
      const rh = (state.generatedChord.notes_midi || []).map((n) => Number(n));
      const lh = rh.map((n) => n - 12);
      const allowed = new Set([...rh, ...lh]);
      if (allowed.has(note)) {
        if (pressed) startHeldInputNote(note, "piano");
        else playSingleAt(note, null, 0.95, "piano");
        setGenerationCurrent(note);
      }
      return;
    }
    const pcs = new Set((state.generatedChord.notes_midi || []).map((n) => Number(n) % 12));
    if (pcs.has(note % 12)) {
      if (pressed) startHeldInputNote(note, "guitar");
      else playSingleAt(note, null, 1.05, "guitar");
      setGenerationCurrent(note);
    }
    return;
  }
  if (state.mode === "scales" && state.generatedScale) {
    const pcs = new Set((state.generatedScale.notes_midi || []).map((n) => Number(n) % 12));
    if (pcs.has(note % 12)) {
      const scaleInstrument = getScalePlaybackInstrument();
      if (pressed) startHeldInputNote(note, scaleInstrument);
      else playSingle(note, scaleInstrument);
      if (!state.scaleLoop.active) {
        if (state.scaleCurrentClearTimer != null) {
          clearTimeout(state.scaleCurrentClearTimer);
          state.scaleCurrentClearTimer = null;
        }
        const mapped = mapScaleInputToDisplayMidi(note, {
          includeBass: scaleInstrument === "guitar" ? true : undefined,
        });
        state.scaleCurrentNote = mapped == null ? Number(note) : Number(mapped);
        state.scaleInputRawNote = Number(note);
        renderInstrument();
        renderStaff();
        state.scaleCurrentClearTimer = setTimeout(() => {
          state.scaleCurrentNote = null;
          state.scaleInputRawNote = null;
          state.scaleCurrentClearTimer = null;
          if (state.mode === "scales") {
            renderInstrument();
            renderStaff();
          }
        }, 460);
      }
    }
    else showForbiddenOnPianoKey(note);
  }
}

function showForbiddenOnPianoKey(note) {
  if (state.instrument !== "piano") return;
  const key = document.querySelector(`#sharedPiano .key[data-midi="${Number(note)}"]`);
  if (!key) return;
  key.classList.remove("forbidden-flash");
  // Force reflow so repeated invalid taps retrigger the visual feedback.
  void key.offsetWidth;
  key.classList.add("forbidden-flash");
  setTimeout(() => key.classList.remove("forbidden-flash"), 420);
}

function refreshDetectionActiveNotes() {
  if (state.detectionMidiHeldNotes.size > 0) {
    state.activeDetectionNotes = new Set(state.detectionMidiHeldNotes);
  } else {
    state.activeDetectionNotes = new Set(state.detectionMouseChordNotes);
  }
  refreshDetectionButtonsState();
  renderInstrument();
  runDetection();
}

function detectionManualPress(note, options = {}) {
  const noteInt = Number(note);
  if (!Number.isFinite(noteInt)) return;
  const instrumentHint = options.instrumentHint || null;
  // Manual interaction takes control over the current chord selection.
  if (state.detectionMidiHeldNotes.size > 0) {
    state.detectionMidiHeldNotes.clear();
  }

  if (state.detectionShiftPressed) {
    if (state.detectionMouseChordNotes.has(noteInt)) {
      state.detectionMouseChordNotes.delete(noteInt);
      stopHeldInputNote(noteInt);
    } else {
      state.detectionMouseChordNotes.add(noteInt);
      startHeldInputNote(noteInt, instrumentHint || (state.instrument === "guitar" ? "guitar" : "piano"));
    }
  } else {
    stopAllHeldInputNotes();
    state.detectionMouseChordNotes.clear();
    state.detectionMouseChordNotes.add(noteInt);
    startHeldInputNote(noteInt, instrumentHint || (state.instrument === "guitar" ? "guitar" : "piano"));
  }
  refreshDetectionActiveNotes();
}

function detectionManualRelease(note) {
  const noteInt = Number(note);
  if (!Number.isFinite(noteInt)) return;
  // Keep chord selection latched; just stop the held preview voice.
  stopHeldInputNote(noteInt);
}

function keySignatureCountForTonic(tonicPc, isMinor) {
  const pc = ((Number(tonicPc) % 12) + 12) % 12;
  const sharpMap = isMinor
    ? { 4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7 }
    : { 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7 };
  const flatMap = isMinor
    ? { 2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6 }
    : { 5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6 };

  const sharpCount = sharpMap[pc];
  const flatCount = flatMap[pc];
  if (sharpCount == null && flatCount == null) return { count: 0, preferFlats: false };
  if (sharpCount == null) return { count: flatCount, preferFlats: true };
  if (flatCount == null) return { count: sharpCount, preferFlats: false };
  if (flatCount < sharpCount) return { count: flatCount, preferFlats: true };
  return { count: sharpCount, preferFlats: false };
}

function isMinorSuffix(suffix) {
  return String(suffix || "").startsWith("m") && !String(suffix || "").startsWith("maj");
}

function scalePrefersMinor(patternName) {
  const minorNames = new Set([
    "Aeolian",
    "Dorian",
    "Phrygian",
    "Locrian",
    "Super Locrian",
    "Half Diminished",
    "Minor Pentatonic",
    "Minor Blues",
  ]);
  return String(patternName || "").includes("Minor") || minorNames.has(String(patternName || ""));
}

function getStaffContext() {
  if (state.mode === "scales" && state.generatedScale) {
    const isMinor = scalePrefersMinor(state.generatedScale.pattern_name);
    const sig = keySignatureCountForTonic(state.generatedScale.tonic_pc, isMinor);
    return { signature: sig, tonicPc: Number(state.generatedScale.tonic_pc), isScale: true };
  }
  if (state.mode === "generation" && state.generatedChord) {
    const isMinor = isMinorSuffix(state.generatedChord.suffix);
    const sig = keySignatureCountForTonic(state.generatedChord.root_pc, isMinor);
    return { signature: sig, tonicPc: Number(state.generatedChord.root_pc), isScale: false };
  }
  if (state.mode === "detection" && state.detectionResult && Number.isInteger(state.detectionResult.root_pc)) {
    const isMinor = isMinorSuffix(state.detectionResult.suffix);
    const sig = keySignatureCountForTonic(state.detectionResult.root_pc, isMinor);
    return { signature: sig, tonicPc: Number(state.detectionResult.root_pc), isScale: false };
  }
  return { signature: { count: 0, preferFlats: false }, tonicPc: 0, isScale: false };
}

function drawStaffLines(ctx, xStart, xEnd, top, gap) {
  ctx.strokeStyle = "#cad3e0";
  ctx.lineWidth = 1.2;
  for (let i = 0; i < 5; i += 1) {
    const y = top + i * gap;
    ctx.beginPath();
    ctx.moveTo(xStart, y);
    ctx.lineTo(xEnd, y);
    ctx.stroke();
  }
}

function drawTrebleClef(ctx, x, y) {
  ctx.save();
  ctx.fillStyle = "#e9edf2";
  ctx.font = "82px 'Times New Roman', serif";
  ctx.textBaseline = "middle";
  ctx.fillText("𝄞", x, y);
  ctx.restore();
}

function drawBassClef(ctx, x, y) {
  ctx.save();
  ctx.fillStyle = "#e9edf2";
  ctx.font = "72px 'Times New Roman', serif";
  ctx.textBaseline = "middle";
  ctx.fillText("𝄢", x, y);
  ctx.restore();
}

function drawGrandBrace(ctx, x, trebleTop, bassTop, gap) {
  const top = trebleTop - 6;
  const bottom = bassTop + gap * 4 + 6;
  const img = state.staff.braceImage;
  if (img && img.complete && img.naturalWidth > 0 && img.naturalHeight > 0) {
    const targetH = Math.max(20, Math.floor(bottom - top + 1));
    const scale = targetH / img.naturalHeight;
    const drawW = Math.max(8, Math.round(img.naturalWidth * scale));
    const drawX = Math.round(x - drawW - 16);
    const drawY = Math.round((top + bottom - targetH) / 2);
    ctx.drawImage(img, drawX, drawY, drawW, targetH);
    return;
  }
  const mid = (top + bottom) / 2;
  ctx.strokeStyle = "#e9edf2";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x + 10, top);
  ctx.bezierCurveTo(x - 2, top + 20, x - 2, mid - 20, x + 10, mid);
  ctx.bezierCurveTo(x - 2, mid + 20, x - 2, bottom - 20, x + 10, bottom);
  ctx.stroke();
}

function initStaffAssets() {
  const brace = new Image();
  brace.onload = () => {
    state.staff.braceImage = brace;
    if (activeModeSupportsStaff()) renderStaff();
  };
  brace.onerror = () => {
    state.staff.braceImage = null;
  };
  brace.src = "/static/brace_left.png";
}

function signaturePositions(top, gap, bass = false) {
  if (bass) {
    return {
      sharp: [top + gap * 4, top + gap * 2.5, top + gap, top + gap * 3.5, top + gap * 2, top + gap * 4.5, top + gap * 3],
      flat: [top + gap * 3, top + gap * 4.5, top + gap * 2.5, top + gap, top + gap * 3.5, top + gap * 2, top + gap * 4],
    };
  }
  return {
    sharp: [top + gap * 3.5, top + gap * 2, top + gap * 4.5, top + gap * 3, top + gap * 1.5, top + gap * 4, top + gap * 2.5],
    flat: [top + gap * 2.5, top + gap * 4, top + gap * 2, top + gap * 3.5, top + gap * 1.5, top + gap * 3, top + gap],
  };
}

function drawKeySignatureOnStaff(ctx, x0, top, gap, sig, bass = false) {
  if (!sig || !sig.count) return x0;
  const positions = signaturePositions(top, gap, bass);
  const yList = sig.preferFlats ? positions.flat : positions.sharp;
  ctx.fillStyle = "#e9edf2";
  ctx.font = "24px serif";
  let x = x0;
  for (let i = 0; i < sig.count; i += 1) {
    ctx.fillText(sig.preferFlats ? "♭" : "♯", x, yList[i]);
    x += 18;
  }
  return x;
}

function drawGrandKeySignature(ctx, trebleTop, bassTop, gap, sig) {
  if (!sig || !sig.count) return 132;
  const xStart = 138;
  const xTrebleEnd = drawKeySignatureOnStaff(ctx, xStart, trebleTop, gap, sig, false);
  const xBassEnd = drawKeySignatureOnStaff(ctx, xStart, bassTop, gap, sig, true);
  return Math.max(xTrebleEnd, xBassEnd) + 10;
}

function midiToDiatonicIndex(midi) {
  const note = Number(midi);
  const pc = ((note % 12) + 12) % 12;
  const octave = Math.floor(note / 12) - 1;
  return (octave * 7) + PC_TO_DIATONIC_LETTER[pc];
}

function midiToTrebleY(midi, trebleTop, gap) {
  const trebleBottomLineDiatonic = (4 * 7) + 2; // E4
  const diatonicIdx = midiToDiatonicIndex(midi);
  const staffBaseY = trebleTop + (4 * gap);
  return staffBaseY - ((diatonicIdx - trebleBottomLineDiatonic) * (gap / 2));
}

function midiToBassY(midi, bassTop, gap) {
  const bassBottomLineDiatonic = (2 * 7) + 4; // G2
  const diatonicIdx = midiToDiatonicIndex(midi);
  const staffBaseY = bassTop + (4 * gap);
  return staffBaseY - ((diatonicIdx - bassBottomLineDiatonic) * (gap / 2));
}

function drawLedgerLines(ctx, x, y, staffTop, gap) {
  const staffBottom = staffTop + gap * 4;
  ctx.strokeStyle = "#cad3e0";
  ctx.lineWidth = 1;
  if (y < staffTop - 1) {
    for (let ly = staffTop - gap; ly >= y - 1; ly -= gap) {
      ctx.beginPath();
      ctx.moveTo(x - 13, ly);
      ctx.lineTo(x + 13, ly);
      ctx.stroke();
    }
  } else if (y > staffBottom + 1) {
    for (let ly = staffBottom + gap; ly <= y + 1; ly += gap) {
      ctx.beginPath();
      ctx.moveTo(x - 13, ly);
      ctx.lineTo(x + 13, ly);
      ctx.stroke();
    }
  }
}

function drawNote(ctx, x, y, staffTop, gap, extra = false, tonic = false, current = false, currentStroke = null) {
  const stroke = current ? (currentStroke || "#6fe0ff") : (extra ? "#ff9a9a" : "#d7dde7");
  const fill = current ? (currentStroke || "#6fe0ff") : "rgba(0,0,0,0)";
  ctx.beginPath();
  ctx.ellipse(x, y, 9, 6.5, -0.35, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 2;
  ctx.stroke();
  drawLedgerLines(ctx, x, y, staffTop, gap);
}

function drawMetronomeCanvas(ctx, width, height) {
  ctx.fillStyle = "#0f1621";
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, width, height);

  const beats = Math.max(1, Number(state.beatsPerBar) || 4);
  const left = 80;
  let right = width - 80;
  if (right <= left) right = left + 1;
  const yTop = Math.max(54, height * 0.33);
  const yBot = Math.min(height - 56, yTop + 84);

  let xs = [];
  let spacing = right - left;
  if (beats === 1) {
    xs = [(left + right) * 0.5];
  } else {
    spacing = (right - left) / (beats - 1);
    xs = Array.from({ length: beats }, (_v, i) => left + i * spacing);
  }

  const axisY = yBot + 18;
  ctx.strokeStyle = "#8f98a3";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(left, axisY);
  ctx.lineTo(right, axisY);
  ctx.stroke();

  const clicks = Math.max(1, Number(state.clicksPerBeat) || 1);
  for (let k = 0; k <= clicks; k += 1) {
    const xTick = left + (right - left) * (k / clicks);
    const isEnd = k === 0 || k === clicks;
    const tickH = isEnd ? 18 : 13;
    const tickW = isEnd ? 2.8 : 2;
    ctx.strokeStyle = isEnd ? "#9aa6b2" : "#747f8d";
    ctx.lineWidth = tickW;
    ctx.beginPath();
    ctx.moveTo(xTick, axisY - (tickH / 2));
    ctx.lineTo(xTick, axisY + (tickH / 2));
    ctx.stroke();
  }

  const current = ((Number(state.currentBeat) || 0) % beats + beats) % beats;
  const baseR = Math.max(7, Math.min(24, 30 - (beats * 0.75)));
  const maxRBySpacing = Math.max(6, (spacing * 0.42) - 2);
  const normalR = Math.min(baseR, maxRBySpacing);
  const activeR = Math.min(normalR + 2, maxRBySpacing + 1.5);
  for (let idx = 0; idx < xs.length; idx += 1) {
    const x = xs[idx];
    const active = !!state.metronomeRunning && idx === current;
    const r = active ? activeR : normalR;
    ctx.beginPath();
    ctx.arc(x, yTop, r, 0, Math.PI * 2);
    ctx.fillStyle = active ? "#ffd24a" : "#c8a832";
    ctx.fill();
    ctx.strokeStyle = active ? "#f3da7a" : "#9f8427";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "#1a1a1a";
    ctx.font = `bold ${Math.max(8, Math.min(12, Math.round(normalR * 0.82)))}px Helvetica`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(idx + 1), x, yTop);
  }

  let redX = xs[0] || left;
  if (state.metronomeRunning) {
    const bpm = Math.max(1, Math.min(300, Number(el("bpm").value) || 120));
    const pulseSec = 60 / bpm;
    const elapsed = Math.max(0, (performance.now() - state.metronomeMotionStartTs) / 1000);
    const t = Math.min(1, elapsed / Math.max(0.001, pulseSec));
    redX = state.metronomeDirection > 0
      ? (left + (right - left) * t)
      : (right - (right - left) * t);
  }
  const redR = 12;
  ctx.beginPath();
  ctx.arc(redX, axisY, redR, 0, Math.PI * 2);
  ctx.fillStyle = "#ff4333";
  ctx.fill();
  ctx.strokeStyle = "#ff8d81";
  ctx.lineWidth = 2;
  ctx.stroke();

  if (state.metronomeTimerEnabled) {
    const total = Math.max(0, Math.floor(state.metronomeTimerRemaining));
    const mm = Math.floor(total / 60);
    const ss = total % 60;
    ctx.fillStyle = "#ffb17a";
    ctx.font = "bold 56px Helvetica";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(`${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`, width / 2, axisY + ((height - axisY) * 0.5));
  }
}

function drawRoundedRect(ctx, x, y, w, h, r, fill, stroke = null, lineWidth = 1) {
  const rr = Math.max(0, Math.min(r, Math.min(w, h) / 2));
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lineWidth;
    ctx.stroke();
  }
}

function renderTunerSpectrumPanel() {
  const canvas = el("tunerSpectrumCanvas");
  if (!canvas || state.mode !== "tuner") return;
  const ctx = canvas.getContext("2d");
  const width = Math.max(680, canvas.clientWidth || canvas.width);
  const height = Math.max(220, canvas.clientHeight || canvas.height);
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;

  ctx.fillStyle = "#0f1621";
  ctx.fillRect(0, 0, width, height);
  drawRoundedRect(ctx, 10, 10, width - 20, height - 20, 10, "#0b1018", "#2f3743", 1.2);

  const bins = state.tuner.freqData;
  const audioCtx = state.tuner.audioCtx;
  if (!bins || !audioCtx) {
    ctx.fillStyle = "#8796ab";
    ctx.font = "bold 16px Helvetica";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("-", width / 2, height / 2);
    return;
  }

  const x1 = 42;
  const y1 = 12;
  const x2 = width - 14;
  const y2 = height - 30;
  const fmin = Math.max(0, Number(state.tuner.rangeMinHz) || 0);
  const fmaxRaw = Math.max(10, Number(state.tuner.rangeMaxHz) || 500);
  const fmax = fmaxRaw <= fmin + 1 ? (fmin + 1) : fmaxRaw;
  const fminLog = Math.max(1, fmin);
  const logMin = Math.log10(fminLog);
  const logMax = Math.log10(fmax);
  const nyq = (audioCtx.sampleRate || 44100) / 2;

  drawRoundedRect(ctx, x1, y1, x2 - x1, y2 - y1, 0, "#10131a", "#465062", 1);

  const fx = (freq) => {
    const safe = Math.max(fminLog, Math.min(fmax, Number(freq) || fminLog));
    const ratio = (Math.log10(safe) - logMin) / Math.max(1e-6, (logMax - logMin));
    return x1 + Math.max(0, Math.min(1, ratio)) * (x2 - x1);
  };

  const tickHz = [70, 80, 90, 100, 120, 140, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1400, 1600, 2000, 2500, 3000];
  const majorHz = new Set([100, 200, 400, 800, 1000]);
  tickHz.forEach((hz) => {
    if (hz < fmin || hz > fmax) return;
    const x = fx(hz);
    const isMajor = majorHz.has(hz);
    ctx.strokeStyle = isMajor ? "#293140" : "#1f2531";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.stroke();
    if (isMajor) {
      ctx.fillStyle = "#8f98a8";
      ctx.font = "8px Helvetica";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillText(String(hz), x, y2 + 4);
    }
  });

  const whitePcs = new Set([0, 2, 4, 5, 7, 9, 11]);
  const minMidi = Math.max(0, Math.floor(69 + 12 * Math.log2(Math.max(1e-9, fmin) / 440)) - 1);
  const maxMidi = Math.min(127, Math.ceil(69 + 12 * Math.log2(Math.max(1e-9, fmax) / 440)) + 1);
  for (let midi = minMidi; midi <= maxMidi; midi += 1) {
    const freq = midiToFreq(midi);
    if (freq < fmin || freq > fmax) continue;
    const x = fx(freq);
    const isNatural = whitePcs.has(midi % 12);
    ctx.strokeStyle = isNatural ? "#ff9f2a" : "#8a5f22";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.stroke();
    const labelY = y1 + ((midi % 2 === 0) ? 8 : 18);
    ctx.fillStyle = isNatural ? "#ffbf6c" : "#b58a4f";
    ctx.font = "bold 7px Helvetica";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(noteNameFromPc(midi % 12), x, labelY);
  }

  let bar = 0;
  const step = Math.max(1, Math.floor(bins.length / Math.max(80, Math.floor((x2 - x1) / 2))));
  for (let i = 0; i < bins.length; i += step) {
    const hz = (i / bins.length) * nyq;
    if (hz < fmin || hz > fmax) continue;
    const mag = bins[i] / 255;
    const x = fx(hz);
    const w = Math.max(1.3, ((x2 - x1) / 170));
    const h = mag * (y2 - y1 - 6);
    ctx.fillStyle = "#49b5ff";
    ctx.fillRect(x, y2 - h, w, h);
    bar += 1;
    if (bar > 260) break;
  }

  ctx.fillStyle = "#a0a8b7";
  ctx.font = "bold 9px Helvetica";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillText("Hz", (x1 + x2) / 2, height - 14);
}

function drawTunerCanvas(ctx, width, height) {
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, width, height);
  state.staff.tunerStringRegions = [];

  const tuning = tunerTuningDef();
  const notes = (tuning.notes || []).map((n) => Number(n));
  const now = performance.now() / 1000;

  const topMargin = 16;
  const bottomMargin = 14;
  const sectionGap = Math.max(10, height * 0.028);
  const usableH = Math.max(140, height - topMargin - bottomMargin);

  let cardsH = Math.min(122, Math.max(72, usableH * 0.36));
  let noteH = Math.min(72, Math.max(40, usableH * 0.18));
  const meterH = Math.min(62, Math.max(42, usableH * 0.20));
  const centsH = Math.min(30, Math.max(18, usableH * 0.10));
  let totalH = cardsH + noteH + meterH + centsH + (sectionGap * 3);
  let overflow = totalH - usableH;
  if (overflow > 0) {
    const reduceNote = Math.min(overflow * 0.55, Math.max(0, noteH - 34));
    noteH -= reduceNote;
    overflow -= reduceNote;
  }
  if (overflow > 0) {
    const reduceCards = Math.min(overflow, Math.max(0, cardsH - 64));
    cardsH -= reduceCards;
  }
  totalH = cardsH + noteH + meterH + centsH + (sectionGap * 3);
  const startY = Math.max(topMargin, (height - totalH) * 0.5);

  const padX = 20;
  const cardGap = Math.max(6, Math.min(12, width * 0.012));
  const cardW = Math.max(64, (width - (padX * 2) - (cardGap * 5)) / 6);
  const cardsY = startY;
  for (let idx = 0; idx < notes.length; idx += 1) {
    const note = notes[idx];
    const x1 = padX + idx * (cardW + cardGap);
    const x2 = x1 + cardW;
    const y1 = cardsY;
    const y2 = y1 + cardsH;
    const active = state.tuner.currentStringIdx === idx || (Number(state.tuner.buttonActiveUntil[idx] || 0) > now);
    const fill = active ? "#f39c12" : "#d2d8df";
    const textColor = active ? "#ffffff" : "#2b2e34";
    drawRoundedRect(ctx, x1, y1, x2 - x1, y2 - y1, Math.min((y2 - y1) / 2, Math.max(10, (x2 - x1) * 0.26)), fill);
    ctx.fillStyle = textColor;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = `bold ${Math.max(10, Math.min(13, Math.round(cardsH * 0.14)))}px Helvetica`;
    ctx.fillText(tunerStringOrdinal(idx), (x1 + x2) / 2, y1 + (cardsH * 0.28));
    ctx.font = `bold ${Math.max(17, Math.min(26, Math.round(cardsH * 0.29)))}px Helvetica`;
    ctx.fillText(noteNameFromPc(note % 12), (x1 + x2) / 2, y1 + (cardsH * 0.64));
    state.staff.tunerStringRegions.push({ idx, x1, y1, x2, y2 });
  }

  let liveNote = "-";
  const noteY = cardsY + cardsH + sectionGap + (noteH * 0.5);
  let liveSize = Math.max(24, Math.min(44, Math.round(noteH * 0.78)));
  if (state.tuner.detectedMidi != null) {
    liveNote = noteNameFromPc(((Number(state.tuner.detectedMidi) % 12) + 12) % 12);
    if (state.tuner.currentFreq > 0) {
      liveNote = `${liveNote} (${state.tuner.currentFreq.toFixed(1)} Hz)`;
      liveSize = Math.max(18, Math.min(30, Math.round(noteH * 0.55)));
    }
  }
  ctx.fillStyle = "#ff9e34";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = `bold ${liveSize}px Helvetica`;
  ctx.fillText(liveNote, width / 2, noteY);

  const meterX1 = 24;
  const meterX2 = width - 24;
  const meterY1 = noteY + (noteH * 0.5) + sectionGap;
  const meterY2 = meterY1 + meterH;
  drawRoundedRect(ctx, meterX1, meterY1, meterX2 - meterX1, meterY2 - meterY1, (meterY2 - meterY1) / 2, "#c8c8ca");
  const centerX = (meterX1 + meterX2) / 2;
  ctx.strokeStyle = "#16a05f";
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(centerX, meterY1 + 2);
  ctx.lineTo(centerX, meterY2 - 2);
  ctx.stroke();

  const cents = Math.max(-50, Math.min(50, Number(state.tuner.currentCents) || 0));
  const knobX = meterX1 + ((cents + 50) / 100) * (meterX2 - meterX1);
  const r = Math.min(14, (meterY2 - meterY1) * 0.36);
  ctx.beginPath();
  ctx.arc(knobX, (meterY1 + meterY2) / 2, r, 0, Math.PI * 2);
  ctx.fillStyle = "#ff5a2f";
  ctx.fill();

  if (state.tuner.currentStringIdx != null) {
    const centsY = Math.min(height - bottomMargin, meterY2 + sectionGap + (centsH * 0.45));
    ctx.fillStyle = "#9fb2c8";
    ctx.font = `bold ${Math.max(11, Math.min(15, Math.round(centsH * 0.6)))}px Helvetica`;
    ctx.fillText(`${cents >= 0 ? "+" : ""}${cents.toFixed(1)} ${tr("tuner_cents_suffix")}`, width / 2, centsY);
  }

}

function getStaffNotes() {
  if (state.mode === "detection") return Array.from(state.activeDetectionNotes).sort((a, b) => a - b);
  if (state.mode === "generation" && state.generatedChord) {
    const rh = getGenerationBaseNotes();
    if (state.instrument === "guitar") {
      return Array.from(new Set(rh)).sort((a, b) => a - b);
    }
    const lh = rh.map((n) => n - 12).filter((n) => n >= 0);
    return Array.from(new Set([...rh, ...lh])).sort((a, b) => a - b);
  }
  if (state.mode === "scales" && state.generatedScale) {
    return getScaleRhLhDisplayNotes().display;
  }
  return [];
}

function getSelectedGuitarVariation() {
  if (!(state.mode === "generation" && state.instrument === "guitar")) return null;
  const idx = Number(state.guitarSelectedVariationIdx);
  if (!Number.isInteger(idx) || idx < 0 || idx >= state.guitarVariations.length) return null;
  return state.guitarVariations[idx] || null;
}

function getVariationNotes(variation) {
  if (!variation || typeof variation !== "object") return [];
  const fromStrings = Array.isArray(variation.string_notes)
    ? variation.string_notes.filter((n) => n != null).map((n) => Number(n)).filter((n) => Number.isFinite(n))
    : [];
  if (fromStrings.length) return Array.from(new Set(fromStrings)).sort((a, b) => a - b);
  const fromNotes = Array.isArray(variation.notes)
    ? variation.notes.map((n) => Number(n)).filter((n) => Number.isFinite(n))
    : [];
  if (fromNotes.length) return Array.from(new Set(fromNotes)).sort((a, b) => a - b);
  return [];
}

function getGenerationBaseNotes() {
  if (!(state.mode === "generation" && state.generatedChord)) return [];
  const selectedVariation = getSelectedGuitarVariation();
  const variationNotes = getVariationNotes(selectedVariation);
  if (variationNotes.length) return variationNotes;
  return (state.generatedChord.notes_midi || [])
    .map((n) => Number(n))
    .filter((n) => Number.isFinite(n))
    .sort((a, b) => a - b);
}

function renderStaff() {
  if (!activeModeSupportsStaff()) return;
  const canvas = el("staffCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = Math.max(680, canvas.clientWidth || canvas.width);
  const height = Math.max(320, canvas.clientHeight || canvas.height);
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;

  if (state.mode === "metronome") {
    drawMetronomeCanvas(ctx, width, height);
    canvas.onclick = null;
    canvas.onmousemove = null;
    canvas.onmouseleave = null;
    canvas.onmousedown = null;
    canvas.onmouseup = null;
    return;
  }

  if (state.mode === "tuner") {
    drawTunerCanvas(ctx, width, height);
    canvas.onmousemove = null;
    canvas.onmouseleave = null;
    canvas.onmousedown = null;
    canvas.onmouseup = null;
    canvas.onclick = (event) => {
      const rect = canvas.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
      const y = ((event.clientY - rect.top) / rect.height) * canvas.height;
      const hit = (state.staff.tunerStringRegions || []).find((r) => x >= r.x1 && x <= r.x2 && y >= r.y1 && y <= r.y2);
      if (hit) playTunerString(hit.idx);
    };
    return;
  }

  ctx.fillStyle = "#0f1621";
  ctx.fillRect(0, 0, width, height);
  canvas.onclick = null;

  const marginX = 72;
  const rightX = width - 20;
  const gap = Math.max(14, Math.min(20, Math.round(height / 26)));
  const grandGap = Math.max(Math.round(gap * 6.8), 124);
  const systemHeight = grandGap + (4 * gap);
  const trebleTop = Math.round((height - systemHeight) / 2);
  const bassTop = trebleTop + grandGap;
  drawGrandBrace(ctx, marginX, trebleTop, bassTop, gap);
  drawStaffLines(ctx, marginX, rightX, trebleTop, gap);
  drawStaffLines(ctx, marginX, rightX, bassTop, gap);
  ctx.strokeStyle = "#cad3e0";
  ctx.lineWidth = 1.6;
  ctx.beginPath();
  ctx.moveTo(marginX, trebleTop);
  ctx.lineTo(marginX, bassTop + gap * 4);
  ctx.stroke();
  drawTrebleClef(ctx, 108, trebleTop + gap * 2.7);
  drawBassClef(ctx, 108, bassTop + gap * 2.25);

  const staffCtx = getStaffContext();
  const startX = drawGrandKeySignature(ctx, trebleTop, bassTop, gap, staffCtx.signature);

  const notes = getStaffNotes();
  const extras = getExtraMidiForMode();
  const tonicPc = staffCtx.tonicPc;
  const compactChordStaff = state.mode === "generation";
  const detectionStaff = state.mode === "detection";
  const scaleStaff = state.mode === "scales";
  state.staff.scaleRegions = [];
  if (detectionStaff && notes.length === 0) {
    ctx.fillStyle = "#cfcfcf";
    ctx.font = "italic 13px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "alphabetic";
    const emptyY = Math.min(height - 48, bassTop + (5.6 * gap));
    ctx.fillText(tr("staff_no_active_notes"), width / 2, emptyY);
  }
  if (detectionStaff) {
    ctx.fillStyle = "#8fa1b7";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText(tr("detection_staff_shift_hint"), width / 2, height - 10);
  }
  const scaleCurrentMidi = state.mode === "scales" ? state.scaleCurrentNote : null;
  let scaleCurrentDisplayMidi = scaleCurrentMidi;
  if (state.mode === "scales" && scaleCurrentDisplayMidi != null) {
    const current = Number(scaleCurrentDisplayMidi);
    const samePc = notes
      .map((n) => Number(n))
      .filter((n) => ((n % 12) + 12) % 12 === ((current % 12) + 12) % 12);
    if (samePc.length) {
      scaleCurrentDisplayMidi = samePc.reduce((best, n) => (
        Math.abs(n - current) < Math.abs(best - current) ? n : best
      ), samePc[0]);
    } else {
      scaleCurrentDisplayMidi = current;
    }
  }
  const generationCurrentMidi = state.mode === "generation" ? state.generationCurrentNote : null;
  const generationPlaying = state.mode === "generation" ? state.generationPlayingNotes : new Set();
  const generationPlayingDisplay = new Set(Array.from(generationPlaying).map((n) => Number(n)));
  const generationRhDisplayNotes = state.mode === "generation" && state.generatedChord
    ? new Set(getGenerationBaseNotes())
    : new Set();
  const generationLhDisplayNotes = state.mode === "generation" && state.generatedChord
    ? new Set((state.generatedChord.notes_midi || []).map((n) => Number(n) - 12).filter((n) => n >= 0))
    : new Set();
  let generationCurrentDisplayMidi = generationCurrentMidi;
  if (state.mode === "generation" && state.instrument === "piano" && generationCurrentDisplayMidi != null) {
    const staffSet = new Set(notes.map((n) => Number(n)));
    // Keyboard LH taps are an octave lower than the LH voice drawn in staff.
    if (!staffSet.has(Number(generationCurrentDisplayMidi)) && staffSet.has(Number(generationCurrentDisplayMidi) + 12)) {
      generationCurrentDisplayMidi = Number(generationCurrentDisplayMidi) + 12;
    }
  }
  if (state.mode === "generation" && state.instrument === "piano" && generationPlayingDisplay.size) {
    const staffSet = new Set(notes.map((n) => Number(n)));
    Array.from(generationPlayingDisplay).forEach((note) => {
      const lhNote = Number(note) - 12;
      if (staffSet.has(lhNote)) generationPlayingDisplay.add(lhNote);
    });
  }

  const xByLine = new Map();
  const placedTrebleCols = new Map();
  const placedBassCols = new Map();
  const scalePlaybackInstrument = scaleStaff ? getScalePlaybackInstrument() : null;
  const scaleRhLh = scaleStaff ? getScaleRhLhDisplayNotes() : { rh: [], lh: [], display: [] };
  const scaleRhSet = new Set(scaleRhLh.rh);
  const scaleLhSet = new Set(scaleRhLh.lh);
  const scaleStaffEntries = [];
  if (scaleStaff) {
    const pairCount = Math.min(scaleRhLh.rh.length, scaleRhLh.lh.length);
    for (let idx = 0; idx < pairCount; idx += 1) {
      const bass = Number(scaleRhLh.rh[idx]) - 12;
      if (scaleLhSet.has(bass)) scaleStaffEntries.push({ midi: bass, degree: idx });
      scaleStaffEntries.push({ midi: Number(scaleRhLh.rh[idx]), degree: idx });
    }
    for (let idx = pairCount; idx < scaleRhLh.rh.length; idx += 1) {
      scaleStaffEntries.push({ midi: Number(scaleRhLh.rh[idx]), degree: idx });
    }
  }
  const scaleLabels = scaleStaff && Array.isArray(state.generatedScale?.notes)
    ? state.generatedScale.notes.map((label) => String(label || "").replace(/\d+/g, ""))
    : [];
  const scaleHoveredNote = scaleStaff ? state.staff.scaleHoverNote : null;
  const scaleHoveredDegree = scaleStaff ? state.staff.scaleHoverDegree : null;
  const scalePressedNote = scaleStaff ? state.staff.scalePressedNote : null;
  const scalePressedDegree = scaleStaff ? state.staff.scalePressedDegree : null;
  let scaleCurrentDegree = null;
  if (scaleStaff && scaleCurrentDisplayMidi != null) {
    const currentEntry = scaleStaffEntries.find((entry) => Number(entry.midi) === Number(scaleCurrentDisplayMidi));
    if (currentEntry) scaleCurrentDegree = Number(currentEntry.degree);
  }
  notes.forEach((midi, idx) => {
    const useTreble = Number(midi) >= 60;
    const y = useTreble ? midiToTrebleY(midi, trebleTop, gap) : midiToBassY(midi, bassTop, gap);
    const staffTop = useTreble ? trebleTop : bassTop;
    const key = `${useTreble ? "T" : "B"}:${Math.round(y)}`;
    const used = xByLine.get(key) || 0;
    xByLine.set(key, used + 1);

    const col = Math.floor(idx / 7);
    const degreeIdx = scaleStaff && idx < scaleStaffEntries.length
      ? Number(scaleStaffEntries[idx].degree)
      : idx;
    const noteRx = Math.max(8, gap * 0.72);
    const overlapThreshold = Math.max(1, gap - 1);
    const detectionBaseX = startX + 62;
    let x;
    if (compactChordStaff) {
      const placedCols = useTreble ? placedTrebleCols : placedBassCols;
      let c = 0;
      while (true) {
        const ys = placedCols.get(c) || [];
        if (!ys.some((prevY) => Math.abs(y - prevY) < overlapThreshold)) break;
        c += 1;
      }
      const ys = placedCols.get(c) || [];
      ys.push(y);
      placedCols.set(c, ys);
      x = startX + 62 + (c * noteRx * 1.8);
    } else if (scaleStaff) {
      x = startX + 46 + degreeIdx * 44;
    } else if (detectionStaff) {
      const placedCols = useTreble ? placedTrebleCols : placedBassCols;
      let c = 0;
      while (true) {
        const ys = placedCols.get(c) || [];
        if (!ys.some((prevY) => Math.abs(y - prevY) < overlapThreshold)) break;
        c += 1;
      }
      const ys = placedCols.get(c) || [];
      ys.push(y);
      placedCols.set(c, ys);
      x = detectionBaseX + (c * noteRx * 1.8);
    } else {
      x = startX + 34 + col * 110 + (idx % 7) * 18 + used * 14;
    }
    const extra = extras.has(midi);
    const tonic = ((midi % 12) + 12) % 12 === tonicPc;
    const scaleNoteCurrent = scaleStaff && scaleCurrentDisplayMidi != null && Number(midi) === Number(scaleCurrentDisplayMidi);
    const scaleNoteHovered = scaleStaff && scaleHoveredNote != null && Number(midi) === Number(scaleHoveredNote);
    const scaleNotePressed = scaleStaff && scalePressedNote != null && Number(midi) === Number(scalePressedNote);
    const current = (scaleCurrentDisplayMidi != null && Number(midi) === Number(scaleCurrentDisplayMidi))
      || scaleNoteHovered
      || scaleNotePressed
      || (generationCurrentDisplayMidi != null && Number(midi) === Number(generationCurrentDisplayMidi))
      || (state.mode === "generation" && generationPlayingDisplay.has(Number(midi)));
    const currentStroke = current
      ? (
          ((state.mode === "generation"
            && state.instrument === "piano"
            && generationLhDisplayNotes.has(Number(midi))
            && !generationRhDisplayNotes.has(Number(midi)))
            || (scaleStaff && scalePlaybackInstrument === "piano" && scaleLhSet.has(Number(midi)) && !scaleRhSet.has(Number(midi))))
            ? "#ff8a3d"
            : "#6fe0ff"
        )
      : null;
    drawNote(ctx, x, y, staffTop, gap, extra, tonic, current, currentStroke);

    if (scaleStaff) {
      state.staff.scaleRegions.push({
        note: Number(midi),
        degree: Number(degreeIdx),
        x,
        y,
        rx: noteRx,
        ry: noteRx * 0.72,
        labelY: trebleTop - 16,
        labelHalfW: Number(midi) >= 60 ? Math.max(12, (scaleLabels[degreeIdx] || "").length * 4 + 8) : 0,
      });
    }

    if (!compactChordStaff && !detectionStaff) {
      const labelCurrent = scaleStaff
        ? (
            scaleNoteCurrent
            || scaleNotePressed
            || (scaleCurrentDegree != null && degreeIdx === Number(scaleCurrentDegree))
            || (scalePressedDegree != null && degreeIdx === Number(scalePressedDegree))
          )
        : current;
      const labelHovered = scaleStaff
        ? (scaleNoteHovered || (scaleHoveredDegree != null && degreeIdx === Number(scaleHoveredDegree)))
        : false;
      ctx.fillStyle = labelCurrent ? (currentStroke || "#6fe0ff") : (labelHovered ? "#7ed1ff" : "#b5c0cf");
      ctx.font = scaleStaff ? "bold 13px sans-serif" : "11px sans-serif";
      if (scaleStaff) {
        if (Number(midi) < 60) return;
        const label = degreeIdx >= 0 && degreeIdx < scaleLabels.length && scaleLabels[degreeIdx]
          ? scaleLabels[degreeIdx]
          : noteNameFromPcStaff(midi % 12, staffCtx.signature.preferFlats);
        ctx.textAlign = "center";
        ctx.fillText(label, x, trebleTop - 16);
        ctx.textAlign = "start";
      } else {
        const label = noteNameFromPcStaff(midi % 12, staffCtx.signature.preferFlats);
        ctx.fillText(label, x - 10, Math.min(height - 8, y + 18));
      }
    }
  });

  if (scaleStaff && scalePlaybackInstrument === "guitar") {
    ctx.fillStyle = "#8fa1b7";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText(tr("scale_staff_guitar_shift_hint"), width / 2, height - 10);
    ctx.textAlign = "start";
    ctx.textBaseline = "alphabetic";
  }

  if (scaleStaff) {
    const getScaleHit = (event) => {
      const rect = canvas.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
      const y = ((event.clientY - rect.top) / rect.height) * canvas.height;
      let best = null;
      let bestDist = Infinity;
      state.staff.scaleRegions.forEach((r) => {
        const nx = (x - r.x) / Math.max(1, r.rx + 4);
        const ny = (y - r.y) / Math.max(1, r.ry + 3);
        const inHead = ((nx * nx) + (ny * ny)) <= 1;
        const inLabel = Math.abs(x - r.x) <= (r.labelHalfW || 0) && Math.abs(y - r.labelY) <= 10;
        if (!inHead && !inLabel) return;
        const dist = Math.abs(x - r.x) + Math.abs(y - r.y);
        if (dist < bestDist) {
          bestDist = dist;
          best = r;
        }
      });
      return best;
    };
    canvas.onmousemove = (event) => {
      const hit = getScaleHit(event);
      const hoverNote = hit ? Number(hit.note) : null;
      const hoverDegree = hit ? Number(hit.degree) : null;
      if (
        state.staff.scalePressedNote != null
        && (Number(event.buttons) & 1) !== 0
        && hit
        && Number(hit.note) !== Number(state.staff.scalePressedNote)
      ) {
        state.staff.scalePressedNote = Number(hit.note);
        state.staff.scalePressedDegree = Number(hit.degree);
        handleInstrumentNote(Number(hit.note));
      }
      if (state.staff.scaleHoverNote !== hoverNote || state.staff.scaleHoverDegree !== hoverDegree) {
        state.staff.scaleHoverNote = hoverNote;
        state.staff.scaleHoverDegree = hoverDegree;
        renderStaff();
      }
      canvas.style.cursor = hit ? "pointer" : "";
    };
    canvas.onmouseleave = () => {
      if (state.staff.scaleHoverNote != null || state.staff.scaleHoverDegree != null) {
        state.staff.scaleHoverNote = null;
        state.staff.scaleHoverDegree = null;
        renderStaff();
      }
      state.staff.scalePressedNote = null;
      state.staff.scalePressedDegree = null;
      canvas.style.cursor = "";
    };
    canvas.onmousedown = (event) => {
      if (Number(event.button) !== 0) return;
      const hit = getScaleHit(event);
      if (!hit) return;
      state.staff.scaleSuppressNextClick = true;
      state.staff.scalePressedNote = Number(hit.note);
      state.staff.scalePressedDegree = Number(hit.degree);
      handleInstrumentNote(Number(hit.note));
      renderStaff();
    };
    canvas.onmouseup = () => {
      if (state.staff.scalePressedNote != null || state.staff.scalePressedDegree != null) {
        state.staff.scalePressedNote = null;
        state.staff.scalePressedDegree = null;
        renderStaff();
      }
    };
    canvas.onclick = (event) => {
      if (state.staff.scaleSuppressNextClick) {
        state.staff.scaleSuppressNextClick = false;
        event.preventDefault();
        return;
      }
      const hit = getScaleHit(event);
      if (!hit) return;
      handleInstrumentNote(Number(hit.note));
    };
  } else {
    state.staff.scaleHoverNote = null;
    state.staff.scaleHoverDegree = null;
    state.staff.scalePressedNote = null;
    state.staff.scalePressedDegree = null;
    state.staff.scaleSuppressNextClick = false;
    canvas.onmousemove = null;
    canvas.onmouseleave = null;
    canvas.onmousedown = null;
    canvas.onmouseup = null;
    canvas.style.cursor = "";
  }
}

async function loadMeta() {
  const data = await fetchJson(`/api/meta?language=${state.language}`);
  state.chordPatterns = data.chord_patterns || [];
  state.scalePatterns = data.scale_patterns || [];
  buildSelectors();
}

function buildSelectors() {
  const genRoot = el("genRoot");
  const scaleRoot = el("scaleRoot");
  const genVariant = el("genVariant");
  const scaleType = el("scaleType");
  const prevGenRoot = Number(genRoot.value || "0");
  const prevScaleRoot = Number(scaleRoot.value || "0");
  const prevVariant = genVariant.value || "";
  const prevScaleType = scaleType.value || "Ionian";

  genRoot.innerHTML = "";
  scaleRoot.innerHTML = "";
  for (let pc = 0; pc < 12; pc += 1) {
    const label = noteNameFromPc(pc);
    const o1 = document.createElement("option");
    o1.value = String(pc);
    o1.textContent = label;
    genRoot.appendChild(o1);
    const o2 = document.createElement("option");
    o2.value = String(pc);
    o2.textContent = label;
    scaleRoot.appendChild(o2);
  }
  genRoot.value = String(Math.max(0, Math.min(11, prevGenRoot)));
  scaleRoot.value = String(Math.max(0, Math.min(11, prevScaleRoot)));

  genVariant.innerHTML = "";
  state.chordPatterns.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.suffix;
    opt.textContent = p.suffix || "maj";
    genVariant.appendChild(opt);
  });
  if (state.chordPatterns.length > 0) {
    genVariant.value = state.chordPatterns.some((p) => p.suffix === prevVariant) ? prevVariant : state.chordPatterns[0].suffix;
  }

  scaleType.innerHTML = "";
  state.scalePatterns.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.name;
    opt.textContent = p.localized_name;
    scaleType.appendChild(opt);
  });
  if (state.scalePatterns.length > 0) {
    scaleType.value = state.scalePatterns.some((p) => p.name === prevScaleType) ? prevScaleType : state.scalePatterns[0].name;
  }
  updateInversionMax();
}

function updateInversionMax() {
  const suffix = el("genVariant").value;
  const pattern = state.chordPatterns.find((p) => p.suffix === suffix);
  const max = Math.max(0, ((pattern?.intervals || [0]).length - 1));
  const select = el("genInversion");
  const prev = Number(select.value || "0");
  select.innerHTML = "";
  for (let i = 0; i <= max; i += 1) {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = inversionLabel(i);
    select.appendChild(opt);
  }
  select.value = String(Math.min(max, Math.max(0, prev)));
  refreshGenerationInversionControlState();
}

function refreshGenerationInversionControlState() {
  const select = el("genInversion");
  if (!select) return;
  select.disabled = state.instrument === "guitar";
}

async function runDetection() {
  const payload = {
    notes: Array.from(state.activeDetectionNotes).sort((a, b) => a - b),
    language: state.language,
    accidental: state.accidental,
  };
  const out = await fetchJson("/api/detect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.detectionResult = out;
  el("detectChord").textContent = out.name || "-";
  el("detectNotes").textContent = (out.notes || []).join(" - ") || "-";
  el("detectExtras").textContent = (out.extras || []).join(" - ") || "-";
  el("detectIntervals").textContent = formatIntervalsFromMidi(out.notes_midi || []);
  renderInstrument();
  renderStaff();
}

async function runGenerateChord() {
  const payload = {
    root_pc: Number(el("genRoot").value),
    suffix: el("genVariant").value,
    inversion: Number(el("genInversion").value),
    language: state.language,
    accidental: state.accidental,
  };
  const out = await fetchJson("/api/generate/chord", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.generatedChord = out;
  el("genChordName").textContent = out.name || "-";
  el("genNotes").textContent = (out.notes || []).join(" - ") || "-";
  el("genIntervals").textContent = formatIntervalsFromMidi(out.notes_midi || []);
  await loadGuitarVariations();
  if (state.mode === "generation") {
    renderInstrument();
    renderStaff();
  }
}

async function runGenerateScale() {
  const restartLoop = state.scaleLoop.active;
  stopScaleLoop();
  const payload = {
    tonic_pc: Number(el("scaleRoot").value),
    pattern_name: el("scaleType").value,
    language: state.language,
    accidental: state.accidental,
  };
  const out = await fetchJson("/api/generate/scale", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.generatedScale = out;
  state.scaleGuitarStartNote = Array.isArray(out.notes_midi) && out.notes_midi.length ? Number(out.notes_midi[0]) : null;
  const tonic = noteNameFromPc(out.tonic_pc || 0);
  el("scaleName").textContent = `${tonic} ${out.pattern_localized_name || out.pattern_name || ""}`.trim();
  el("scaleNotes").textContent = (out.notes || []).join(" - ") || "-";
  el("scaleIntervals").textContent = formatIntervalsFromMidi(out.notes_midi || []);
  if (state.mode === "scales") {
    renderInstrument();
    renderStaff();
    if (restartLoop) toggleScaleLoop();
  }
}

function ensureAudioCtx() {
  if (!state.metronomeCtx) state.metronomeCtx = new AudioContext();
  return state.metronomeCtx;
}

function ensureNoiseBuffer(ctx) {
  if (state.audioNoiseBuffer && state.audioNoiseBuffer.sampleRate === ctx.sampleRate) {
    return state.audioNoiseBuffer;
  }
  const size = Math.max(2048, Math.floor(ctx.sampleRate * 0.09));
  const buf = ctx.createBuffer(1, size, ctx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < size; i += 1) data[i] = (Math.random() * 2) - 1;
  state.audioNoiseBuffer = buf;
  return buf;
}

function ensureAudioBus(ctx) {
  if (state.audioBus && state.audioBus.context === ctx) return state.audioBus;
  const comp = ctx.createDynamicsCompressor();
  comp.threshold.value = -22;
  comp.knee.value = 20;
  comp.ratio.value = 2.6;
  comp.attack.value = 0.003;
  comp.release.value = 0.18;
  const out = ctx.createGain();
  out.gain.value = 0.92;
  comp.connect(out);
  out.connect(ctx.destination);
  state.audioBus = comp;
  return state.audioBus;
}

function beep(freq = 1000, durationMs = 70, gain = 0.1) {
  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const dur = Math.max(0.02, Number(durationMs || 70) / 1000);
  const amp = Math.max(0.005, Number(gain) || 0.1);
  const isAccent = freq >= 1500;

  const noise = ctx.createBufferSource();
  noise.buffer = ensureNoiseBuffer(ctx);
  const hp = ctx.createBiquadFilter();
  hp.type = "highpass";
  hp.frequency.value = isAccent ? 1800 : 1300;
  const lp = ctx.createBiquadFilter();
  lp.type = "lowpass";
  lp.frequency.value = isAccent ? 7600 : 6200;
  const nGain = ctx.createGain();
  nGain.gain.setValueAtTime(0.0001, t);
  nGain.gain.exponentialRampToValueAtTime(amp * (isAccent ? 0.95 : 0.72), t + 0.002);
  nGain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  noise.connect(hp);
  hp.connect(lp);
  lp.connect(nGain);
  nGain.connect(ensureAudioBus(ctx));
  noise.start(t);
  noise.stop(t + dur + 0.01);

  const osc = ctx.createOscillator();
  const oGain = ctx.createGain();
  osc.type = "triangle";
  osc.frequency.value = Number(freq) || 1000;
  oGain.gain.setValueAtTime(0.0001, t);
  oGain.gain.exponentialRampToValueAtTime(amp * (isAccent ? 0.7 : 0.42), t + 0.0015);
  oGain.gain.exponentialRampToValueAtTime(0.0001, t + (dur * 0.82));
  osc.connect(oGain);
  oGain.connect(ensureAudioBus(ctx));
  osc.start(t);
  osc.stop(t + dur);
}

function playPianoAt(midi, startTime = null, durationSeconds = 0.46) {
  const ctx = ensureAudioCtx();
  const t = startTime == null ? ctx.currentTime : Number(startTime);
  const dur = Math.max(0.12, Number(durationSeconds) || 0.46);
  const freq = 440 * (2 ** ((Number(midi) - 69) / 12));
  const attack = Math.min(0.014, dur * 0.18);
  const decayPoint = t + Math.max(0.14, Math.min(0.32, dur * 0.44));
  const releaseEnd = t + dur + Math.max(0.48, dur * 0.95);
  const env = ctx.createGain();
  env.gain.setValueAtTime(0.0001, t);
  env.gain.linearRampToValueAtTime(0.16, t + attack);
  env.gain.exponentialRampToValueAtTime(0.078, decayPoint);
  env.gain.exponentialRampToValueAtTime(0.0001, releaseEnd);

  const filter = ctx.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.setValueAtTime(6200, t);
  filter.frequency.exponentialRampToValueAtTime(1900, t + Math.max(0.2, dur * 1.05));
  filter.Q.value = 0.6;

  env.connect(filter);
  filter.connect(ensureAudioBus(ctx));

  const partials = [
    { ratio: 1.0, gain: 0.78, type: "sine" },
    { ratio: 2.0, gain: 0.26, type: "triangle" },
    { ratio: 3.0, gain: 0.12, type: "triangle" },
  ];
  partials.forEach((p) => {
    const osc = ctx.createOscillator();
    const og = ctx.createGain();
    osc.type = p.type;
    osc.frequency.setValueAtTime(freq * p.ratio, t);
    og.gain.value = p.gain;
    osc.connect(og);
    og.connect(env);
    osc.start(t);
    osc.stop(releaseEnd + 0.08);
  });
}

function playGuitarAt(midi, startTime = null, durationSeconds = 0.9) {
  const ctx = ensureAudioCtx();
  const t = startTime == null ? ctx.currentTime : Number(startTime);
  const dur = Math.max(0.18, Number(durationSeconds) || 0.9);
  const freq = 440 * (2 ** ((Number(midi) - 69) / 12));

  const body = ctx.createBiquadFilter();
  body.type = "bandpass";
  body.frequency.value = Math.min(2800, Math.max(170, freq * 2.4));
  body.Q.value = 0.9;
  const low = ctx.createBiquadFilter();
  low.type = "lowpass";
  low.frequency.value = Math.min(4200, Math.max(900, freq * 5.2));

  const env = ctx.createGain();
  env.gain.setValueAtTime(0.0001, t);
  env.gain.exponentialRampToValueAtTime(0.17, t + 0.006);
  env.gain.exponentialRampToValueAtTime(0.0001, t + dur);

  body.connect(low);
  low.connect(env);
  env.connect(ensureAudioBus(ctx));

  const noise = ctx.createBufferSource();
  noise.buffer = ensureNoiseBuffer(ctx);
  const nGain = ctx.createGain();
  nGain.gain.setValueAtTime(0.0001, t);
  nGain.gain.exponentialRampToValueAtTime(0.42, t + 0.001);
  nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
  noise.connect(nGain);
  nGain.connect(body);
  noise.start(t);
  noise.stop(t + 0.05);

  const osc = ctx.createOscillator();
  const oGain = ctx.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(freq, t);
  oGain.gain.setValueAtTime(0.0001, t);
  oGain.gain.exponentialRampToValueAtTime(0.22, t + 0.005);
  oGain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  osc.connect(oGain);
  oGain.connect(body);
  osc.start(t);
  osc.stop(t + dur + 0.04);
}

function playSingleAt(midi, startTime = null, durationSeconds = 0.46, instrument = "piano") {
  if (instrument === "guitar") {
    playGuitarAt(midi, startTime, Math.max(0.24, Number(durationSeconds) || 0.46));
    return;
  }
  playPianoAt(midi, startTime, durationSeconds);
}

function playSingle(midi, instrument = null) {
  const inst = instrument || (state.instrument === "guitar" ? "guitar" : "piano");
  playSingleAt(midi, null, 0.46, inst);
}

function playNotesMidi(notes, stepMs = 120) {
  notes.forEach((midi, idx) => {
    setTimeout(() => playSingle(Number(midi)), idx * stepMs);
  });
}

function playChordMidi(notes, options = {}) {
  const ctx = ensureAudioCtx();
  const instrument = options.instrument === "guitar" ? "guitar" : "piano";
  const normalizedNotes = Array.from(new Set((notes || []).map((midi) => Number(midi))))
    .filter((midi) => Number.isFinite(midi));
  if (state.mode === "generation") {
    if (state.generationPlayClearTimer != null) {
      clearTimeout(state.generationPlayClearTimer);
      state.generationPlayClearTimer = null;
    }
    state.generationPlayingNotes = new Set(normalizedNotes);
    renderStaff();
  }
  const t = ctx.currentTime + 0.005;
  if (instrument === "guitar") {
    normalizedNotes.forEach((midi, idx) => playSingleAt(Number(midi), t + (idx * 0.018), 1.05, "guitar"));
  } else {
    normalizedNotes.forEach((midi) => playSingleAt(Number(midi), t, 1.25, "piano"));
  }
  if (state.mode === "generation" && normalizedNotes.length) {
    const clearMs = instrument === "guitar" ? 1250 : 980;
    state.generationPlayClearTimer = setTimeout(() => {
      state.generationPlayingNotes.clear();
      state.generationPlayClearTimer = null;
      if (state.mode === "generation") renderStaff();
    }, clearMs);
  }
}

function stopHeldChord() {
  if (state.generationPlayClearTimer != null) {
    clearTimeout(state.generationPlayClearTimer);
    state.generationPlayClearTimer = null;
  }
  if (state.generationPlayingNotes.size) {
    state.generationPlayingNotes.clear();
    if (state.mode === "generation") renderStaff();
  }
  if (!(state.heldChordVoices instanceof Map) || !state.heldChordVoices.size) return;
  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  state.heldChordVoices.forEach((voice) => {
    try {
      const gain = voice?.gain;
      if (gain?.gain) {
        const now = t;
        gain.gain.cancelScheduledValues(now);
        gain.gain.setValueAtTime(Math.max(0.0001, gain.gain.value || 0.001), now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.09);
      }
      (voice?.oscs || []).forEach((osc) => {
        try { osc.stop(t + 0.11); } catch (_e) {}
      });
      if (voice?.noise) {
        try { voice.noise.stop(t + 0.04); } catch (_e) {}
      }
    } catch (_e) {}
  });
  state.heldChordVoices.clear();
}

function stopHeldInputNote(midi) {
  if (!(state.heldInputVoices instanceof Map)) return;
  const note = Number(midi);
  const voice = state.heldInputVoices.get(note);
  if (!voice) return;
  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const instrument = voice.instrument === "guitar" ? "guitar" : "piano";
  const releaseSeconds = instrument === "guitar" ? 0.52 : 0.40;
  const oscTail = instrument === "guitar" ? 0.60 : 0.48;
  const noiseTail = instrument === "guitar" ? 0.14 : 0.10;
  try {
    if (voice.gain?.gain) {
      voice.gain.gain.cancelScheduledValues(t);
      voice.gain.gain.setValueAtTime(Math.max(0.0001, voice.gain.gain.value || 0.001), t);
      voice.gain.gain.exponentialRampToValueAtTime(0.0001, t + releaseSeconds);
    }
    (voice.oscs || []).forEach((osc) => {
      try { osc.stop(t + oscTail); } catch (_e) {}
    });
    if (voice.noise) {
      try { voice.noise.stop(t + noiseTail); } catch (_e) {}
    }
  } catch (_e) {}
  state.heldInputVoices.delete(note);
}

function stopAllHeldInputNotes() {
  if (!(state.heldInputVoices instanceof Map) || !state.heldInputVoices.size) return;
  Array.from(state.heldInputVoices.keys()).forEach((note) => stopHeldInputNote(note));
}

function startHeldMidiInputNote(midi, instrument = "piano") {
  const note = Number(midi);
  if (!Number.isFinite(note)) return;
  if (!(state.heldMidiInputVoices instanceof Map)) state.heldMidiInputVoices = new Map();
  if (state.heldMidiInputVoices.has(note)) return;

  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const freq = 440 * (2 ** ((note - 69) / 12));
  const bus = ensureAudioBus(ctx);
  const gain = ctx.createGain();
  const voice = { gain, oscs: [], noise: null, instrument };

  if (instrument === "guitar") {
    const body = ctx.createBiquadFilter();
    body.type = "bandpass";
    body.frequency.value = Math.min(2600, Math.max(170, freq * 2.2));
    body.Q.value = 0.9;
    const low = ctx.createBiquadFilter();
    low.type = "lowpass";
    low.frequency.value = Math.min(4300, Math.max(900, freq * 5.1));
    body.connect(low);
    low.connect(gain);

    const noise = ctx.createBufferSource();
    noise.buffer = ensureNoiseBuffer(ctx);
    const nGain = ctx.createGain();
    nGain.gain.setValueAtTime(0.0001, t);
    nGain.gain.exponentialRampToValueAtTime(0.38, t + 0.001);
    nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
    noise.connect(nGain);
    nGain.connect(body);
    noise.start(t);
    voice.noise = noise;

    const osc = ctx.createOscillator();
    const oGain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(freq, t);
    oGain.gain.value = 0.28;
    osc.connect(oGain);
    oGain.connect(body);
    osc.start(t);
    voice.oscs.push(osc);

    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.17, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.06, t + 0.22);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.10);
  } else {
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(5400, t);
    filter.frequency.exponentialRampToValueAtTime(2200, t + 0.22);
    filter.Q.value = 0.62;
    filter.connect(gain);

    const p1 = ctx.createOscillator();
    const p1g = ctx.createGain();
    p1.type = "sine";
    p1.frequency.setValueAtTime(freq, t);
    p1g.gain.value = 0.78;
    p1.connect(p1g);
    p1g.connect(filter);
    p1.start(t);

    const p2 = ctx.createOscillator();
    const p2g = ctx.createGain();
    p2.type = "triangle";
    p2.frequency.setValueAtTime(freq * 2, t);
    p2g.gain.value = 0.22;
    p2.connect(p2g);
    p2g.connect(filter);
    p2.start(t);

    voice.oscs.push(p1, p2);
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.linearRampToValueAtTime(0.16, t + 0.014);
    gain.gain.exponentialRampToValueAtTime(0.065, t + 0.24);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.25);
  }

  gain.connect(bus);
  state.heldMidiInputVoices.set(note, voice);
}

function stopHeldMidiInputNote(midi) {
  if (!(state.heldMidiInputVoices instanceof Map)) return;
  const note = Number(midi);
  const voice = state.heldMidiInputVoices.get(note);
  if (!voice) return;
  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const instrument = voice.instrument === "guitar" ? "guitar" : "piano";
  const releaseSeconds = instrument === "guitar" ? 0.52 : 0.40;
  const oscTail = instrument === "guitar" ? 0.60 : 0.48;
  const noiseTail = instrument === "guitar" ? 0.14 : 0.10;
  try {
    if (voice.gain?.gain) {
      voice.gain.gain.cancelScheduledValues(t);
      voice.gain.gain.setValueAtTime(Math.max(0.0001, voice.gain.gain.value || 0.001), t);
      voice.gain.gain.exponentialRampToValueAtTime(0.0001, t + releaseSeconds);
    }
    (voice.oscs || []).forEach((osc) => {
      try { osc.stop(t + oscTail); } catch (_e) {}
    });
    if (voice.noise) {
      try { voice.noise.stop(t + noiseTail); } catch (_e) {}
    }
  } catch (_e) {}
  state.heldMidiInputVoices.delete(note);
}

function stopAllHeldMidiInputNotes() {
  if (!(state.heldMidiInputVoices instanceof Map) || !state.heldMidiInputVoices.size) return;
  Array.from(state.heldMidiInputVoices.keys()).forEach((note) => stopHeldMidiInputNote(note));
}

function beginInputDrag(note, instrumentHint) {
  const midi = Number(note);
  if (!Number.isFinite(midi)) return;
  state.inputDragActive = true;
  state.inputDragInstrument = instrumentHint || null;
  if (state.inputDragNote != null && Number(state.inputDragNote) !== midi) {
    if (state.mode === "detection") {
      handleInstrumentNote(state.inputDragNote, {
        pressed: false,
        released: true,
        instrumentHint: state.inputDragInstrument,
      });
    } else {
      stopHeldInputNote(state.inputDragNote);
    }
  }
  state.inputDragNote = midi;
  handleInstrumentNote(midi, { pressed: true, instrumentHint });
}

function updateInputDrag(note, instrumentHint) {
  if (!state.inputDragActive) return;
  const midi = Number(note);
  if (!Number.isFinite(midi)) return;
  if (state.inputDragNote != null && Number(state.inputDragNote) === midi) return;
  if (state.inputDragNote != null) {
    if (state.mode === "detection") {
      handleInstrumentNote(state.inputDragNote, {
        pressed: false,
        released: true,
        instrumentHint: state.inputDragInstrument || instrumentHint || null,
      });
    } else {
      stopHeldInputNote(state.inputDragNote);
    }
  }
  state.inputDragNote = midi;
  state.inputDragInstrument = instrumentHint || state.inputDragInstrument || null;
  handleInstrumentNote(midi, { pressed: true, instrumentHint });
}

function endInputDrag() {
  if (state.inputDragNote != null) {
    if (state.mode === "detection") {
      handleInstrumentNote(state.inputDragNote, {
        pressed: false,
        released: true,
        instrumentHint: state.inputDragInstrument,
      });
    } else {
      stopHeldInputNote(state.inputDragNote);
    }
  }
  state.inputDragNote = null;
  state.inputDragInstrument = null;
  state.inputDragActive = false;
}

function startHeldInputNote(midi, instrument = "piano") {
  const note = Number(midi);
  if (!Number.isFinite(note)) return;
  if (!(state.heldInputVoices instanceof Map)) state.heldInputVoices = new Map();
  if (state.heldInputVoices.has(note)) return;

  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const freq = 440 * (2 ** ((note - 69) / 12));
  const bus = ensureAudioBus(ctx);
  const gain = ctx.createGain();
  const voice = { gain, oscs: [], noise: null, instrument };

  if (instrument === "guitar") {
    const body = ctx.createBiquadFilter();
    body.type = "bandpass";
    body.frequency.value = Math.min(2600, Math.max(170, freq * 2.2));
    body.Q.value = 0.9;
    const low = ctx.createBiquadFilter();
    low.type = "lowpass";
    low.frequency.value = Math.min(4300, Math.max(900, freq * 5.1));
    body.connect(low);
    low.connect(gain);

    const noise = ctx.createBufferSource();
    noise.buffer = ensureNoiseBuffer(ctx);
    const nGain = ctx.createGain();
    nGain.gain.setValueAtTime(0.0001, t);
    nGain.gain.exponentialRampToValueAtTime(0.38, t + 0.001);
    nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
    noise.connect(nGain);
    nGain.connect(body);
    noise.start(t);
    voice.noise = noise;

    const osc = ctx.createOscillator();
    const oGain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(freq, t);
    oGain.gain.value = 0.28;
    osc.connect(oGain);
    oGain.connect(body);
    osc.start(t);
    voice.oscs.push(osc);

    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.17, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.06, t + 0.22);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.10);
  } else {
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(5400, t);
    filter.frequency.exponentialRampToValueAtTime(2200, t + 0.22);
    filter.Q.value = 0.62;
    filter.connect(gain);

    const p1 = ctx.createOscillator();
    const p1g = ctx.createGain();
    p1.type = "sine";
    p1.frequency.setValueAtTime(freq, t);
    p1g.gain.value = 0.78;
    p1.connect(p1g);
    p1g.connect(filter);
    p1.start(t);

    const p2 = ctx.createOscillator();
    const p2g = ctx.createGain();
    p2.type = "triangle";
    p2.frequency.setValueAtTime(freq * 2, t);
    p2g.gain.value = 0.22;
    p2.connect(p2g);
    p2g.connect(filter);
    p2.start(t);

    voice.oscs.push(p1, p2);
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.linearRampToValueAtTime(0.16, t + 0.014);
    gain.gain.exponentialRampToValueAtTime(0.065, t + 0.24);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.25);
  }

  gain.connect(bus);
  state.heldInputVoices.set(note, voice);
}

function startHeldVoice(midi, instrument = "piano") {
  const note = Number(midi);
  if (!Number.isFinite(note)) return;
  if (!(state.heldChordVoices instanceof Map)) state.heldChordVoices = new Map();
  if (state.heldChordVoices.has(note)) return;

  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const freq = 440 * (2 ** ((note - 69) / 12));
  const gain = ctx.createGain();
  const bus = ensureAudioBus(ctx);
  const voice = { gain, oscs: [], noise: null };

  if (instrument === "guitar") {
    const body = ctx.createBiquadFilter();
    body.type = "bandpass";
    body.frequency.value = Math.min(2600, Math.max(170, freq * 2.1));
    body.Q.value = 0.9;
    const low = ctx.createBiquadFilter();
    low.type = "lowpass";
    low.frequency.value = Math.min(4200, Math.max(900, freq * 5.0));
    body.connect(low);
    low.connect(gain);

    const noise = ctx.createBufferSource();
    noise.buffer = ensureNoiseBuffer(ctx);
    const nGain = ctx.createGain();
    nGain.gain.setValueAtTime(0.0001, t);
    nGain.gain.exponentialRampToValueAtTime(0.33, t + 0.001);
    nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
    noise.connect(nGain);
    nGain.connect(body);
    noise.start(t);
    voice.noise = noise;

    const osc = ctx.createOscillator();
    const oGain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(freq, t);
    oGain.gain.value = 0.28;
    osc.connect(oGain);
    oGain.connect(body);
    osc.start(t);
    voice.oscs.push(osc);

    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.17, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.095, t + 0.13);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.65);
  } else {
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(5200, t);
    filter.frequency.exponentialRampToValueAtTime(2400, t + 0.25);
    filter.Q.value = 0.65;
    filter.connect(gain);

    const p1 = ctx.createOscillator();
    const p1g = ctx.createGain();
    p1.type = "sine";
    p1.frequency.setValueAtTime(freq, t);
    p1g.gain.value = 0.8;
    p1.connect(p1g);
    p1g.connect(filter);
    p1.start(t);

    const p2 = ctx.createOscillator();
    const p2g = ctx.createGain();
    p2.type = "triangle";
    p2.frequency.setValueAtTime(freq * 2, t);
    p2g.gain.value = 0.22;
    p2.connect(p2g);
    p2g.connect(filter);
    p2.start(t);

    voice.oscs.push(p1, p2);
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.linearRampToValueAtTime(0.15, t + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.085, t + 0.14);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.95);
  }

  gain.connect(bus);
  state.heldChordVoices.set(note, voice);
}

function startHeldChord(notes, instrument = "piano") {
  stopHeldChord();
  const normalizedNotes = Array.from(new Set((notes || []).map((midi) => Number(midi))))
    .filter((midi) => Number.isFinite(midi));
  normalizedNotes.forEach((midi) => startHeldVoice(midi, instrument));
  if (state.mode === "generation" && normalizedNotes.length) {
    state.generationPlayingNotes = new Set(normalizedNotes);
    renderStaff();
  }
}

function scaleStepMs() {
  const bpmInput = el("scaleBpm") || el("bpm");
  const raw = bpmInput ? Number(bpmInput.value) : 120;
  const bpm = Number.isFinite(raw) ? Math.max(1, Math.min(300, raw)) : 120;
  return Math.max(60, Math.floor(60000 / bpm));
}

function setScalePlayButtonState(active) {
  const btn = el("scalePlay");
  if (!btn) return;
  btn.classList.toggle("active", !!active);
  btn.classList.toggle("stop-mode", !!active);
  if (active) {
    btn.textContent = "";
    btn.setAttribute("aria-label", tr("stop"));
    btn.setAttribute("title", tr("stop"));
  } else {
    btn.textContent = "▶";
    btn.setAttribute("aria-label", tr("play"));
    btn.setAttribute("title", tr("play"));
  }
}

function setMetronomeToggleButtonState(active) {
  const btn = el("metroToggle");
  if (!btn) return;
  btn.classList.toggle("active", !!active);
  btn.classList.toggle("stop-mode", !!active);
  if (active) {
    btn.textContent = "";
    btn.setAttribute("aria-label", tr("stop"));
    btn.setAttribute("title", tr("stop"));
  } else {
    btn.textContent = "▶";
    btn.setAttribute("aria-label", tr("metro_start"));
    btn.setAttribute("title", tr("metro_start"));
  }
}

function clearScaleLoopTimer() {
  if (state.scaleLoop.timer != null) {
    clearTimeout(state.scaleLoop.timer);
    state.scaleLoop.timer = null;
  }
}

function stopScaleLoop() {
  state.scaleLoop.active = false;
  clearScaleLoopTimer();
  if (state.scaleCurrentClearTimer != null) {
    clearTimeout(state.scaleCurrentClearTimer);
    state.scaleCurrentClearTimer = null;
  }
  state.scaleCurrentNote = null;
  state.scaleInputRawNote = null;
  setScalePlayButtonState(false);
  if (state.mode === "scales") {
    renderInstrument();
    renderStaff();
  }
}

function stepScaleLoop() {
  if (!state.scaleLoop.active || !state.generatedScale || !Array.isArray(state.generatedScale.notes_midi)) {
    stopScaleLoop();
    return;
  }
  if (state.scaleCurrentClearTimer != null) {
    clearTimeout(state.scaleCurrentClearTimer);
    state.scaleCurrentClearTimer = null;
  }
  const notes = getScaleBaseNotes();
  if (!notes.length) {
    stopScaleLoop();
    return;
  }
  const idx = Math.max(0, Math.min(state.scaleLoop.index, notes.length - 1));
  const note = notes[idx];
  state.scaleCurrentNote = note;
  state.scaleInputRawNote = null;
  if (state.scaleMetronomeEnabled) {
    beep((idx === 0 && state.scaleLoop.direction > 0) ? 1600 : 1050, 55, 0.09);
  } else {
    const scaleInstrument = getScalePlaybackInstrument();
    const stepSeconds = Math.max(0.08, scaleStepMs() / 1000);
    const noteDur = scaleInstrument === "guitar"
      ? Math.max(0.62, Math.min(1.10, stepSeconds * 1.12))
      : Math.max(0.56, Math.min(1.00, stepSeconds * 1.02));
    playSingleAt(note, null, noteDur, scaleInstrument);
  }
  if (state.mode === "scales") {
    renderInstrument();
    renderStaff();
  }

  if (notes.length > 1) {
    if (state.scaleLoop.direction > 0) {
      if (idx >= notes.length - 1) {
        state.scaleLoop.direction = -1;
        state.scaleLoop.index = idx;
      } else {
        state.scaleLoop.index = idx + 1;
      }
    } else if (idx <= 0) {
      state.scaleLoop.direction = 1;
      state.scaleLoop.index = idx;
    } else {
      state.scaleLoop.index = idx - 1;
    }
  }
  state.scaleLoop.timer = setTimeout(stepScaleLoop, scaleStepMs());
}

function toggleScaleLoop() {
  if (!state.generatedScale || !state.generatedScale.notes_midi || !state.generatedScale.notes_midi.length) return;
  if (state.scaleLoop.active) {
    stopScaleLoop();
    return;
  }
  state.scaleLoop.active = true;
  state.scaleLoop.index = 0;
  state.scaleLoop.direction = 1;
  setScalePlayButtonState(true);
  stepScaleLoop();
}

function renderMetronomeDots() {
  const dots = el("metroDots");
  if (!dots) return;
  dots.innerHTML = "";
  for (let i = 0; i < state.beatsPerBar; i += 1) {
    const d = document.createElement("div");
    d.className = "dot";
    if (i === state.currentBeat) d.classList.add("active");
    if (i === 0) d.classList.add("accent");
    d.textContent = String(i + 1);
    dots.appendChild(d);
  }
}

function metronomeStepMs() {
  const bpm = Math.max(1, Math.min(300, Number(el("bpm").value) || 120));
  const clicks = Math.max(1, Math.min(16, Number(state.clicksPerBeat) || 1));
  return Math.max(10, Math.round((60000 / bpm) / clicks));
}

function updateMetronomeMotion() {
  const dot = el("metroMotionDot");
  const rail = el("metroMotion");
  if (!dot || !rail) return;
  const left = 12;
  const right = Math.max(left + 1, rail.clientWidth - 12);
  let x = left;
  if (state.metronomeRunning) {
    const pulseSec = 60 / Math.max(1, Math.min(300, Number(el("bpm").value) || 120));
    const elapsed = Math.max(0, (performance.now() - state.metronomeMotionStartTs) / 1000);
    const phase = Math.min(1, elapsed / Math.max(0.01, pulseSec));
    x = state.metronomeDirection > 0
      ? (left + (right - left) * phase)
      : (right - (right - left) * phase);
  } else {
    x = left;
  }
  dot.style.left = `${x}px`;
}

function renderMetronomeTimerDisplay() {
  const total = Math.max(0, Math.floor(state.metronomeTimerRemaining));
  const mm = Math.floor(total / 60);
  const ss = total % 60;
  const label = el("metroTimerDisplay");
  if (label) label.textContent = `${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
}

function stopMetronomeAnimation() {
  if (state.metronomeAnimRaf != null) {
    cancelAnimationFrame(state.metronomeAnimRaf);
    state.metronomeAnimRaf = null;
  }
}

function metronomeAnimLoop() {
  if (!state.metronomeRunning) {
    stopMetronomeAnimation();
    return;
  }
  if (state.metronomeTimerEnabled) {
    const now = performance.now();
    const elapsed = Math.max(0, (now - state.metronomeTimerLastTs) / 1000);
    state.metronomeTimerLastTs = now;
    state.metronomeTimerRemaining = Math.max(0, state.metronomeTimerRemaining - elapsed);
    renderMetronomeTimerDisplay();
    if (state.metronomeTimerRemaining <= 0) {
      toggleMetronome();
      return;
    }
  }
  updateMetronomeMotion();
  if (state.mode === "metronome") renderStaff();
  state.metronomeAnimRaf = requestAnimationFrame(metronomeAnimLoop);
}

function startMetronomeAnimation() {
  stopMetronomeAnimation();
  state.metronomeTimerLastTs = performance.now();
  state.metronomeAnimRaf = requestAnimationFrame(metronomeAnimLoop);
}

function renderMetronomeFigures() {
  document.querySelectorAll(".metro-figure").forEach((btn) => {
    btn.classList.toggle("active", Number(btn.dataset.clicks) === Number(state.clicksPerBeat));
  });
}

function metronomeTick() {
  if (!state.metronomeRunning) return;
  if (state.currentSubclick === 0) {
    if (state.metronomeTickCount > 0) {
      state.currentBeat = (state.currentBeat + 1) % Math.max(1, state.beatsPerBar);
      state.metronomeDirection *= -1;
    }
    state.metronomeMotionStartTs = performance.now();
  }

  const accent = state.currentSubclick === 0;
  const barAccent = accent && state.currentBeat === 0 && state.metronomeBarAccentEnabled;
  beep(barAccent ? 1700 : (accent ? 1300 : 950), 55, barAccent ? 0.12 : 0.09);

  renderMetronomeDots();
  updateMetronomeMotion();
  if (state.mode === "metronome") renderStaff();

  state.currentSubclick = (state.currentSubclick + 1) % Math.max(1, state.clicksPerBeat);
  state.metronomeTickCount += 1;
  state.metronomeTimer = setTimeout(metronomeTick, metronomeStepMs());
}

function syncMetronomeInputsToState() {
  state.beatsPerBar = Math.max(1, Math.min(16, Number(el("metroMeter").value) || 4));
  state.metronomeBarAccentEnabled = !!el("metroBarAccent").checked;
  state.metronomeTimerEnabled = !!el("metroTimerEnabled").checked;
  state.metronomeTimerMinutes = Math.max(0, Math.min(99, Number(el("metroTimerMinutes").value) || 0));
  state.metronomeTimerSeconds = Math.max(0, Math.min(59, Number(el("metroTimerSeconds").value) || 0));
}

function toggleMetronome() {
  if (state.metronomeRunning) {
    state.metronomeRunning = false;
    if (state.metronomeTimer != null) clearTimeout(state.metronomeTimer);
    state.metronomeTimer = null;
    state.currentBeat = -1;
    state.currentSubclick = 0;
    state.metronomeTickCount = 0;
    stopMetronomeAnimation();
    renderMetronomeDots();
    updateMetronomeMotion();
    setMetronomeToggleButtonState(false);
    return;
  }

  syncMetronomeInputsToState();
  state.metronomeRunning = true;
  state.currentBeat = 0;
  state.currentSubclick = 0;
  state.metronomeTickCount = 0;
  state.metronomeDirection = 1;
  state.metronomeMotionStartTs = performance.now();
  state.metronomeTimerRemaining = Math.max(0, (state.metronomeTimerMinutes * 60) + state.metronomeTimerSeconds);
  renderMetronomeDots();
  renderMetronomeTimerDisplay();
  metronomeTick();
  startMetronomeAnimation();
  setMetronomeToggleButtonState(true);
}

function autoCorrelate(buffer, sampleRate) {
  let bestOffset = -1;
  let bestCorrelation = 0;
  const size = buffer.length;
  for (let offset = 8; offset < 1200; offset += 1) {
    let corr = 0;
    for (let i = 0; i < size - offset; i += 1) corr += buffer[i] * buffer[i + offset];
    corr /= (size - offset);
    if (corr > bestCorrelation) {
      bestCorrelation = corr;
      bestOffset = offset;
    }
  }
  if (bestOffset === -1 || bestCorrelation < 0.01) return null;
  return sampleRate / bestOffset;
}

function freqToMidi(freq) {
  return 69 + 12 * Math.log2(freq / 440);
}

function midiToFreq(midi) {
  return 440 * (2 ** ((Number(midi) - 69) / 12));
}

function updateTunerNeedle(cents) {
  const needle = el("tunerNeedle");
  if (!needle) return;
  const clamped = Math.max(-50, Math.min(50, cents));
  const pct = ((clamped + 50) / 100) * 100;
  needle.style.left = `calc(${pct}% - 7px)`;
}

function setTunerButtonState(active) {
  const btn = el("tunerToggle");
  if (!btn) return;
  btn.classList.toggle("active", !!active);
  btn.classList.toggle("stop-mode", !!active);
  if (active) {
    btn.textContent = "";
    btn.setAttribute("aria-label", tr("stop"));
    btn.setAttribute("title", tr("stop"));
  } else {
    btn.textContent = "▶";
    btn.setAttribute("aria-label", tr("tuner_start"));
    btn.setAttribute("title", tr("tuner_start"));
  }
}

function updateTunerGainValue() {
  const out = el("tunerGainValue");
  if (out) out.textContent = `${Math.round(state.tuner.inputGain)}%`;
}

function clampTunerRange(minHz, maxHz) {
  let minVal = Math.max(0, Math.min(2990, Number(minHz) || 0));
  let maxVal = Math.max(10, Math.min(3000, Number(maxHz) || 500));
  if (maxVal <= minVal + 10) {
    if (maxVal < 3000) maxVal = Math.min(3000, minVal + 10);
    else minVal = Math.max(0, maxVal - 10);
  }
  state.tuner.rangeMinHz = Math.round(minVal);
  state.tuner.rangeMaxHz = Math.round(maxVal);
  if (el("tunerRangeMin")) el("tunerRangeMin").value = String(state.tuner.rangeMinHz);
  if (el("tunerRangeMax")) el("tunerRangeMax").value = String(state.tuner.rangeMaxHz);
}

function playTunerString(idx) {
  const tuning = tunerTuningDef();
  const notes = tuning.notes || [];
  const n = Number(notes[idx]);
  if (!Number.isFinite(n)) return;
  state.tuner.currentStringIdx = idx;
  state.tuner.currentCents = 0;
  state.tuner.currentFreq = midiToFreq(n);
  state.tuner.detectedMidi = n;
  state.tuner.buttonActiveUntil[idx] = (performance.now() / 1000) + 0.9;
  state.tuner.referenceNote = n;
  el("tunerNote").textContent = noteNameFromPc(n % 12);
  el("tunerCents").textContent = `+0.0 ${tr("tuner_cents_suffix")}`;
  el("tunerFreq").textContent = `${state.tuner.currentFreq.toFixed(1)} Hz`;
  playSingle(n);
  if (state.mode === "tuner") renderStaff();
}

function updateTunerDetection(freq) {
  const tuning = tunerTuningDef();
  const notes = (tuning.notes || []).map((n) => Number(n));
  if (!notes.length || !Number.isFinite(freq) || freq <= 0) return;

  if (state.tuner.currentFreq <= 0) state.tuner.currentFreq = freq;
  else state.tuner.currentFreq = (state.tuner.currentFreq * 0.82) + (freq * 0.18);

  let bestIdx = 0;
  let bestAbs = Number.POSITIVE_INFINITY;
  let bestCents = 0;
  for (let i = 0; i < notes.length; i += 1) {
    const target = midiToFreq(notes[i]);
    const cents = 1200 * Math.log2(Math.max(1e-9, freq) / target);
    const abs = Math.abs(cents);
    if (abs < bestAbs) {
      bestAbs = abs;
      bestIdx = i;
      bestCents = cents;
    }
  }

  state.tuner.currentStringIdx = bestIdx;
  state.tuner.currentCents = (state.tuner.currentCents * 0.78) + (bestCents * 0.22);
  state.tuner.buttonActiveUntil[bestIdx] = (performance.now() / 1000) + 0.20;
  const midi = Math.round(freqToMidi(freq));
  state.tuner.detectedMidi = Math.max(0, Math.min(127, midi));
}

async function toggleTuner() {
  if (state.tuner.running) {
    state.tuner.running = false;
    if (state.tuner.raf) cancelAnimationFrame(state.tuner.raf);
    if (state.tuner.stream) state.tuner.stream.getTracks().forEach((t) => t.stop());
    if (state.tuner.audioCtx) await state.tuner.audioCtx.close();
    state.tuner.stream = null;
    state.tuner.audioCtx = null;
    state.tuner.analyser = null;
    state.tuner.freqData = null;
    state.tuner.currentStringIdx = null;
    state.tuner.currentCents = 0;
    state.tuner.currentFreq = 0;
    state.tuner.detectedMidi = null;
    state.tuner.referenceNote = null;
    setTunerButtonState(false);
    el("tunerNote").textContent = "-";
    el("tunerCents").textContent = "-";
    el("tunerFreq").textContent = "-";
    if (state.mode === "tuner") renderStaff();
    if (state.mode === "tuner") renderTunerSpectrumPanel();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const audioCtx = new AudioContext();
    const src = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    src.connect(analyser);
    state.tuner.running = true;
    state.tuner.stream = stream;
    state.tuner.audioCtx = audioCtx;
    state.tuner.analyser = analyser;
    state.tuner.freqData = new Uint8Array(analyser.frequencyBinCount);
    setTunerButtonState(true);

    const data = new Float32Array(analyser.fftSize);
    const loop = () => {
      if (!state.tuner.running) return;
      analyser.getFloatTimeDomainData(data);
      const gain = Math.max(0, Number(state.tuner.inputGain) || 0) / 100;
      if (gain !== 1) {
        for (let i = 0; i < data.length; i += 1) data[i] *= gain;
      }
      const freq = autoCorrelate(data, audioCtx.sampleRate);
      if (freq && freq > 40 && freq < 2000) {
        if (freq >= state.tuner.rangeMinHz && freq <= state.tuner.rangeMaxHz) {
          updateTunerDetection(freq);
          const noteMidi = state.tuner.detectedMidi != null ? Number(state.tuner.detectedMidi) : Math.round(freqToMidi(freq));
          el("tunerNote").textContent = noteNameFromPc(((noteMidi % 12) + 12) % 12);
          el("tunerCents").textContent = `${state.tuner.currentCents >= 0 ? "+" : ""}${state.tuner.currentCents.toFixed(1)} ${tr("tuner_cents_suffix")}`;
          el("tunerFreq").textContent = `${state.tuner.currentFreq.toFixed(1)} Hz`;
        }
      }
      if (state.tuner.freqData) analyser.getByteFrequencyData(state.tuner.freqData);
      if (state.mode === "tuner") renderStaff();
      if (state.mode === "tuner") renderTunerSpectrumPanel();
      state.tuner.raf = requestAnimationFrame(loop);
    };
    loop();
  } catch (_err) {
    el("tunerNote").textContent = tr("tuner_no_permission");
    el("tunerCents").textContent = "-";
    setTunerButtonState(false);
    if (state.mode === "tuner") renderStaff();
  }
}

function handleMidiMessage(event) {
  if (!state.midi.enabled) return;
  const data = event.data || [];
  const status = data[0] & 0xf0;
  const note = Number(data[1]);
  const velocity = Number(data[2] || 0);
  const isNoteOn = status === 0x90 && velocity > 0;
  const isNoteOff = status === 0x80 || (status === 0x90 && velocity === 0);
  if (!isNoteOn && !isNoteOff) return;

  if (state.mode === "detection") {
    if (isNoteOn) {
      if (state.detectionMidiHeldNotes.size === 0 && state.detectionMouseChordNotes.size > 0) {
        state.detectionMouseChordNotes.clear();
      }
      state.detectionMidiHeldNotes.add(note);
      if (state.midiInputSoundEnabled) startHeldMidiInputNote(note, "piano");
    } else {
      state.detectionMidiHeldNotes.delete(note);
      stopHeldMidiInputNote(note);
    }
    refreshDetectionActiveNotes();
    return;
  }

  if (state.mode === "metronome") {
    if (isNoteOn) state.activeMidiLiveNotes.add(note);
    else state.activeMidiLiveNotes.delete(note);
    renderInstrument();
  }
}

async function toggleMidi() {
  const btn = el("midiToggle");
  if (state.midi.enabled) {
    state.midi.enabled = false;
    if (state.midi.access) {
      state.midi.access.inputs.forEach((input) => {
        input.onmidimessage = null;
      });
    }
    state.activeMidiLiveNotes.clear();
    stopAllHeldMidiInputNotes();
    state.detectionMidiHeldNotes.clear();
    if (state.mode === "detection") refreshDetectionActiveNotes();
    if (state.mode === "metronome") renderInstrument();
    btn.textContent = tr("midi_off");
    btn.setAttribute("title", midiButtonTooltipForState("off"));
    refreshMidiToggleButtonState();
    return;
  }

  if (!window.isSecureContext) {
    btn.textContent = tr("midi_requires_secure");
    btn.setAttribute("title", midiButtonTooltipForState("secure_required"));
    refreshMidiToggleButtonState();
    return;
  }

  if (!navigator.requestMIDIAccess) {
    btn.textContent = tr("midi_try_chrome");
    btn.setAttribute("title", midiButtonTooltipForState("unsupported"));
    refreshMidiToggleButtonState();
    return;
  }

  try {
    try {
      const ctx = ensureAudioCtx();
      if (ctx.state !== "running") {
        await ctx.resume();
      }
    } catch (_e) {
      // Audio resume may require user gesture; MIDI init should continue anyway.
    }
    if (!state.midi.access) state.midi.access = await navigator.requestMIDIAccess();
    state.midi.enabled = true;
    state.midi.access.inputs.forEach((input) => {
      input.onmidimessage = handleMidiMessage;
    });
    btn.textContent = tr("midi_on");
    btn.setAttribute("title", midiButtonTooltipForState("on"));
    refreshMidiToggleButtonState();
  } catch (_err) {
    btn.textContent = tr("midi_denied");
    btn.setAttribute("title", midiButtonTooltipForState("denied"));
    refreshMidiToggleButtonState();
  }
}

function bindEvents() {
  const bindImmediatePress = (button, action, options = {}) => {
    if (!button || typeof action !== "function") return;
    const highlightWhilePressed = !!options.highlightWhilePressed;
    const onPress = typeof options.onPress === "function" ? options.onPress : null;
    const onRelease = typeof options.onRelease === "function" ? options.onRelease : null;
    let suppressNextClick = false;
    let pointerPressed = false;

    const setPressedVisual = (pressed) => {
      if (!highlightWhilePressed) return;
      button.classList.toggle("active", !!pressed);
      if (pressed) button.classList.remove("stop-mode");
    };

    const onPointerStart = (event) => {
      if (button.disabled) return;
      if (event.type === "mousedown" && Number(event.button) !== 0) return;
      event.preventDefault();
      suppressNextClick = true;
      pointerPressed = true;
      setPressedVisual(true);
      if (onPress) onPress();
      else action();
    };

    const onPointerEnd = () => {
      if (!pointerPressed) return;
      pointerPressed = false;
      setPressedVisual(false);
      if (onRelease) onRelease();
    };

    button.addEventListener("mousedown", onPointerStart);
    button.addEventListener("touchstart", onPointerStart, { passive: false });
    document.addEventListener("mouseup", onPointerEnd);
    document.addEventListener("touchend", onPointerEnd, { passive: true });
    document.addEventListener("touchcancel", onPointerEnd, { passive: true });
    button.addEventListener("click", (event) => {
      if (button.disabled) {
        event.preventDefault();
        return;
      }
      if (suppressNextClick) {
        suppressNextClick = false;
        event.preventDefault();
        return;
      }
      if (onPress) {
        onPress();
        if (onRelease) setTimeout(() => onRelease(), 140);
      } else {
        action();
      }
      if (highlightWhilePressed) {
        setPressedVisual(true);
        setTimeout(() => setPressedVisual(false), 140);
      }
    });
  };

  const modeSelect = el("modeSelect");
  if (modeSelect) {
    modeSelect.addEventListener("change", (e) => setMode(e.target.value));
  }
  document.querySelectorAll(".inst-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      setInstrument(btn.dataset.inst);
      renderInstrument();
    });
  });

  el("midiToggle").addEventListener("click", toggleMidi);
  const midiStartupEnableBtn = el("midiStartupEnableBtn");
  if (midiStartupEnableBtn) {
    midiStartupEnableBtn.addEventListener("click", async () => {
      await toggleMidi();
      if (state.midi.enabled) hideMidiStartupModal();
    });
  }
  const midiStartupCloseBtn = el("midiStartupCloseBtn");
  if (midiStartupCloseBtn) {
    midiStartupCloseBtn.addEventListener("click", () => {
      hideMidiStartupModal();
    });
  }
  el("guitarHandedness").addEventListener("change", (e) => {
    state.guitarHandedness = e.target.value;
    if (state.instrument === "guitar") renderInstrument();
  });
  el("language").addEventListener("change", async (e) => {
    state.language = e.target.value;
    await loadMeta();
    applyTranslations();
    renderInstrument();
    if (state.mode === "detection") await runDetection();
    if (state.mode === "generation" && state.generatedChord) await runGenerateChord();
    if (state.mode === "scales" && state.generatedScale) await runGenerateScale();
    renderStaff();
  });

  el("accidental").addEventListener("change", async (e) => {
    state.accidental = e.target.value;
    await loadMeta();
    renderInstrument();
    if (state.mode === "detection") await runDetection();
    if (state.mode === "generation" && state.generatedChord) await runGenerateChord();
    if (state.mode === "scales" && state.generatedScale) await runGenerateScale();
    renderStaff();
  });

  el("detectClear").addEventListener("click", () => {
    stopHeldChord();
    stopAllHeldInputNotes();
    stopAllHeldMidiInputNotes();
    endInputDrag();
    state.detectionMouseChordNotes.clear();
    state.detectionMidiHeldNotes.clear();
    state.detectionShiftPressed = false;
    state.activeDetectionNotes.clear();
    refreshDetectionButtonsState();
    renderInstrument();
    runDetection();
  });
  const detectMidiSoundToggle = el("detectMidiSoundToggle");
  if (detectMidiSoundToggle) {
    detectMidiSoundToggle.addEventListener("click", async () => {
      state.midiInputSoundEnabled = !state.midiInputSoundEnabled;
      if (state.midiInputSoundEnabled) {
        try {
          const ctx = ensureAudioCtx();
          if (ctx.state !== "running") await ctx.resume();
        } catch (_e) {}
      }
      if (!state.midiInputSoundEnabled) stopAllHeldMidiInputNotes();
      refreshMidiInputSoundToggleButton();
    });
  }

  bindImmediatePress(el("detectPlay"), () => {
    playChordMidi(Array.from(state.activeDetectionNotes).sort((a, b) => a - b), { instrument: "piano" });
  }, {
    highlightWhilePressed: true,
    onPress: () => {
      const notes = Array.from(state.activeDetectionNotes).sort((a, b) => a - b);
      if (!notes.length) return;
      startHeldChord(notes, "piano");
    },
    onRelease: () => {
      stopHeldChord();
    },
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Shift") return;
    if (event.repeat) return;
    state.shiftPressed = true;
    if (state.mode !== "detection") return;
    state.detectionShiftPressed = true;
  });
  document.addEventListener("keyup", (event) => {
    if (event.key !== "Shift") return;
    state.shiftPressed = false;
    if (state.mode !== "detection") return;
    state.detectionShiftPressed = false;
  });
  window.addEventListener("blur", () => {
    state.shiftPressed = false;
    state.detectionShiftPressed = false;
  });

  el("genRoot").addEventListener("change", runGenerateChord);
  el("genVariant").addEventListener("change", () => {
    updateInversionMax();
    runGenerateChord();
  });
  el("genInversion").addEventListener("change", () => {
    runGenerateChord();
  });
  bindImmediatePress(el("genPlay"), () => {
    if (!state.generatedChord) return;
    const notes = getGenerationBaseNotes();
    if (!notes.length) return;
    playChordMidi(notes, { instrument: state.instrument === "guitar" ? "guitar" : "piano" });
  }, {
    highlightWhilePressed: true,
    onPress: () => {
      if (!state.generatedChord) return;
      const notes = getGenerationBaseNotes();
      if (!notes.length) return;
      startHeldChord(notes, state.instrument === "guitar" ? "guitar" : "piano");
    },
    onRelease: () => {
      stopHeldChord();
    },
  });

  const scaleModeMetronome = el("scaleModeMetronome");
  if (scaleModeMetronome) {
    scaleModeMetronome.addEventListener("click", () => {
      state.scaleMetronomeEnabled = !state.scaleMetronomeEnabled;
      renderScaleModeButtons();
      // Metronome mode only changes sound source; playback starts/stops with Play/Stop.
    });
  }
  el("scaleRoot").addEventListener("change", runGenerateScale);
  el("scaleType").addEventListener("change", runGenerateScale);
  el("scaleBpm").addEventListener("input", (e) => {
    const v = String(e.target.value || "120");
    el("scaleBpmValue").textContent = `${v} ${tempoUnitLabel()}`;
    const metroBpm = el("bpm");
    if (metroBpm) metroBpm.value = v;
    refreshMetronomeTempoInfo();
  });
  bindImmediatePress(el("scalePlay"), () => {
    toggleScaleLoop();
  });

  const syncMeterDisplay = () => {
    const meter = Math.max(1, Math.min(16, Number(el("metroMeter").value) || 4));
    el("metroMeterValue").textContent = String(meter);
    state.beatsPerBar = meter;
    if (!state.metronomeRunning) renderMetronomeDots();
  };
  syncMeterDisplay();

  el("bpm").addEventListener("input", (e) => {
    const v = String(e.target.value || "120");
    refreshMetronomeTempoInfo();
    if (el("scaleBpm")) {
      el("scaleBpm").value = v;
      el("scaleBpmValue").textContent = `${v} ${tempoUnitLabel()}`;
    }
  });

  el("metroBpmMinus").addEventListener("click", () => {
    const bpm = Math.max(1, Math.min(300, Number(el("bpm").value) || 120) - 1);
    el("bpm").value = String(bpm);
    el("bpm").dispatchEvent(new Event("input"));
  });
  el("metroBpmPlus").addEventListener("click", () => {
    const bpm = Math.max(1, Math.min(300, Number(el("bpm").value) || 120) + 1);
    el("bpm").value = String(bpm);
    el("bpm").dispatchEvent(new Event("input"));
  });

  el("metroMeter").addEventListener("input", syncMeterDisplay);
  el("metroMeterMinus").addEventListener("click", () => {
    const meter = Math.max(1, Math.min(16, Number(el("metroMeter").value) || 4) - 1);
    el("metroMeter").value = String(meter);
    syncMeterDisplay();
  });
  el("metroMeterPlus").addEventListener("click", () => {
    const meter = Math.max(1, Math.min(16, Number(el("metroMeter").value) || 4) + 1);
    el("metroMeter").value = String(meter);
    syncMeterDisplay();
  });

  document.querySelectorAll(".metro-figure").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.clicksPerBeat = Math.max(1, Math.min(16, Number(btn.dataset.clicks) || 1));
      renderMetronomeFigures();
      renderMetronomeDots();
      if (state.mode === "metronome") renderStaff();
    });
  });
  renderMetronomeFigures();

  el("metroBarAccent").addEventListener("change", (e) => {
    state.metronomeBarAccentEnabled = !!e.target.checked;
    if (state.mode === "metronome") renderStaff();
  });
  el("metroTimerEnabled").addEventListener("change", (e) => {
    state.metronomeTimerEnabled = !!e.target.checked;
    if (!state.metronomeRunning) {
      state.metronomeTimerRemaining = (Number(el("metroTimerMinutes").value) * 60) + Number(el("metroTimerSeconds").value);
      renderMetronomeTimerDisplay();
    }
    if (state.mode === "metronome") renderStaff();
  });
  const syncTimerInputs = () => {
    el("metroTimerMinutes").value = String(Math.max(0, Math.min(99, Number(el("metroTimerMinutes").value) || 0)));
    el("metroTimerSeconds").value = String(Math.max(0, Math.min(59, Number(el("metroTimerSeconds").value) || 0)));
    if (!state.metronomeRunning) {
      state.metronomeTimerRemaining = (Number(el("metroTimerMinutes").value) * 60) + Number(el("metroTimerSeconds").value);
      renderMetronomeTimerDisplay();
    }
    if (state.mode === "metronome") renderStaff();
  };
  el("metroTimerMinutes").addEventListener("change", syncTimerInputs);
  el("metroTimerSeconds").addEventListener("change", syncTimerInputs);
  syncTimerInputs();

  const tunerTuning = el("tunerTuning");
  if (tunerTuning) {
    tunerTuning.addEventListener("change", (e) => {
      const key = String(e.target.value || "standard_e");
      state.tuner.tuningKey = TUNER_TUNINGS.some((t) => t.key === key) ? key : "standard_e";
      state.tuner.currentStringIdx = null;
      state.tuner.detectedMidi = null;
      state.tuner.currentCents = 0;
      if (state.mode === "tuner") renderStaff();
    });
  }
  const syncTunerGain = () => {
    state.tuner.inputGain = Math.max(0, Math.min(200, Number(el("tunerGain").value) || 100));
    el("tunerGain").value = String(state.tuner.inputGain);
    updateTunerGainValue();
  };
  el("tunerGain").addEventListener("input", syncTunerGain);
  el("tunerGainMinus").addEventListener("click", () => {
    el("tunerGain").value = String(Math.max(0, Math.min(200, Number(el("tunerGain").value) - 1)));
    syncTunerGain();
  });
  el("tunerGainPlus").addEventListener("click", () => {
    el("tunerGain").value = String(Math.max(0, Math.min(200, Number(el("tunerGain").value) + 1)));
    syncTunerGain();
  });
  syncTunerGain();

  const syncTunerRange = () => {
    clampTunerRange(el("tunerRangeMin").value, el("tunerRangeMax").value);
    if (state.mode === "tuner") renderStaff();
  };
  el("tunerRangeMin").addEventListener("change", syncTunerRange);
  el("tunerRangeMax").addEventListener("change", syncTunerRange);
  syncTunerRange();

  window.addEventListener("resize", () => {
    if (activeModeSupportsStaff()) renderStaff();
    if (state.mode === "tuner") renderTunerSpectrumPanel();
  });
  window.addEventListener("blur", () => {
    stopHeldChord();
    stopAllHeldInputNotes();
  });

  el("metroToggle").addEventListener("click", toggleMetronome);
  el("tunerToggle").addEventListener("click", toggleTuner);
}

async function main() {
  initStaffAssets();
  bindEvents();
  applyTranslations();
  syncLeftPanelHeader();
  if (el("scaleBpm") && el("bpm")) {
    el("scaleBpm").value = el("bpm").value;
    el("scaleBpmValue").textContent = `${el("scaleBpm").value} ${tempoUnitLabel()}`;
  }
  refreshMetronomeTempoInfo();
  if (el("metroMotionDot")) updateMetronomeMotion();
  renderMetronomeTimerDisplay();
  await loadMeta();
  applyTranslations();
  await runGenerateChord();
  await runGenerateScale();
  await runDetection();
  refreshDetectionButtonsState();
  setMode("detection");
  showMidiStartupModal();
  renderMetronomeDots();
  renderStaff();
}

main();
