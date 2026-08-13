(function initHelpCallouts(global) {
"use strict";

const HELP_CALLOUTS_NOTE_DETECTION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#staffCanvas", textKey: "help_note_detection_staff", side: "top" },
  { selector: "#panelNoteDetection", textKey: "help_note_detection_panel", side: "left" },
  { selector: "#noteDetectPlay", textKey: "help_note_detection_play", side: "bottom" },
  { selector: "#noteDetectClear", textKey: "help_note_detection_clear", side: "bottom" },
  { selector: "#noteDetectDetailsToggle", textKey: "help_note_detection_toggle", side: "bottom" },
  { selector: "#noteDetectFieldNote", textKey: "help_note_detection_result", side: "left" },
  { selector: "#sharedPiano", textKey: "help_note_detection_instrument", side: "top" },
];

const HELP_CALLOUTS_DETECTION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_detection", side: "top" },
  { selector: "#panelDetection", textKey: "help_detection_panel", side: "left" },
  { selector: "#detectPlay", textKey: "help_detect_play", side: "bottom" },
  { selector: "#detectVariantHelp", textKey: "help_detect_variant_theory", side: "bottom" },
  { selector: "#detectClear", textKey: "help_detect_clear", side: "bottom" },
  { selector: "#detectDetailsToggle", textKey: "help_detect_details_toggle", side: "bottom" },
  { selector: "#detectFieldChord", textKey: "help_field_chord", side: "left" },
  { selector: "#detectFieldNotes", textKey: "help_field_notes", side: "left" },
  { selector: "#detectFieldExtras", textKey: "help_field_extras", side: "left" },
  { selector: "#detectFieldFormula", textKey: "help_field_formula", side: "left" },
  { selector: "#detectFieldConstruction", textKey: "help_field_construction", side: "left" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_detection", side: "top" },
];
const HELP_CALLOUTS_GENERATION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_generation", side: "top" },
  { selector: "#panelGeneration", textKey: "help_generation_panel", side: "left" },
  { selector: "#genRootRow", textKey: "help_gen_root", side: "left" },
  { selector: "#genVariant", textKey: "help_gen_variant", side: "left" },
  { selector: "#genInversion", textKey: "help_gen_inversion", side: "left" },
  { selector: ".generation-hand-row", textKey: "help_gen_hand", side: "left" },
  { selector: "#genPlay", textKey: "help_gen_play", side: "bottom" },
  { selector: "#genVariantHelp", textKey: "help_gen_variant_theory", side: "bottom" },
  { selector: "#genFieldChord", textKey: "help_gen_result_chord", side: "left" },
  { selector: "#genFieldNotes", textKey: "help_gen_result_notes", side: "left" },
  { selector: "#genFieldFormula", textKey: "help_gen_result_formula", side: "left" },
  { selector: "#genFieldConstruction", textKey: "help_gen_result_construction", side: "left" },
  { selector: "#guitarVariationBar", textKey: "help_guitar_variations_bar", side: "top" },
  { selector: "#guitarVariationBar .guitar-var-btn", textKey: "help_guitar_variation_btn", side: "top" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_generation", side: "top" },
];
const HELP_CALLOUTS_CIRCLE_FIFTHS = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_generation", side: "top" },
  { selector: "#circleFifthsCanvas", textKey: "help_circle_canvas", side: "left" },
  { selector: "#circlePlay", textKey: "help_circle_play", side: "bottom" },
  { selector: "#circleFieldChord", textKey: "help_circle_result_chord", side: "left" },
  { selector: "#guitarVariationBar", textKey: "help_guitar_variations_bar", side: "top" },
  { selector: "#guitarVariationBar .guitar-var-btn", textKey: "help_guitar_variation_btn", side: "top" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_generation", side: "top" },
];
const HELP_CALLOUTS_SCALES = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_scales", side: "top" },
  { selector: "#panelScales", textKey: "help_scales_panel", side: "left" },
  { selector: "#scaleRootRow", textKey: "help_scale_root", side: "left" },
  { selector: "#scaleType", textKey: "help_scale_type", side: "left" },
  { selector: "#scaleFilterToggle", textKey: "help_scale_filter", side: "left" },
  { selector: "#scalePlay", textKey: "help_scale_play", side: "bottom" },
  { selector: "#scaleModeMetronome", textKey: "help_scale_metronome_mode", side: "top" },
  { selector: ".scale-octaves-wrap", textKey: "help_scale_octaves", side: "top" },
  { selector: "#scaleBpm", textKey: "help_scale_bpm", side: "left" },
  { selector: "#scaleName", textKey: "help_scale_result_name", side: "left" },
  { selector: "#scaleNotes", textKey: "help_scale_result_notes", side: "left" },
  { selector: "#scaleFormula", textKey: "help_scale_result_formula", side: "left" },
  { selector: "#scalePattern", textKey: "help_scale_result_pattern", side: "left" },
  { selector: ".scale-fingering-row", textKey: "help_scale_fingering", side: "left" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_scales", side: "top" },
];
const HELP_CALLOUTS_METRONOME = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_metronome", side: "top" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_metronome", side: "top" },
  { selector: "#panelMetronome", textKey: "help_metronome_panel", side: "left" },
  { selector: "#metroToggle", textKey: "help_metro_start", side: "bottom" },
  { selector: "#metroVolume", textKey: "help_metro_volume", side: "left" },
  { selector: "#metroBpmMinus", textKey: "help_metro_bpm_minus", side: "left" },
  { selector: "#bpm", textKey: "help_metro_bpm", side: "left" },
  { selector: "#metroBpmPlus", textKey: "help_metro_bpm_plus", side: "left" },
  { selector: "#metroMeterMinus", textKey: "help_metro_meter_minus", side: "left" },
  { selector: "#metroMeter", textKey: "help_metro_meter", side: "left" },
  { selector: "#metroMeterPlus", textKey: "help_metro_meter_plus", side: "left" },
  { selector: "#metroRowSubdivision", textKey: "help_metro_subdivision", side: "top" },
  { selector: "#metroRowBarAccent", textKey: "help_metro_bar_accent", side: "left" },
  { selector: "#metroRowTimerEnabled", textKey: "help_metro_timer", side: "left" },
  { selector: "#metroRowTimer", textKey: "help_metro_timer_values", side: "left" },
  { selector: "#helpMetroYellowPoints", textKey: "help_metro_yellow_points", side: "top" },
  { selector: "#helpMetroScaleAxis", textKey: "help_metro_scale_axis", side: "top" },
  { selector: "#helpMetroRedBall", textKey: "help_metro_red_ball", side: "top" },
];

const HELP_CALLOUTS_INTERVAL_DETECTION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#staffCanvas", textKey: "help_staff_interval", side: "top" },
  { selector: "#panelIntervalDetection", textKey: "help_interval_panel", side: "left" },
  { selector: "#intervalPlayReverse", textKey: "help_interval_play_reverse", side: "bottom" },
  { selector: "#intervalPlay", textKey: "help_interval_play", side: "bottom" },
  { selector: "#intervalClear", textKey: "help_interval_clear", side: "bottom" },
  { selector: "#intervalDetailsToggle", textKey: "help_interval_details_toggle", side: "bottom" },
  { selector: "#intervalFieldNotes", textKey: "help_interval_field_notes", side: "left" },
  { selector: "#intervalFieldName", textKey: "help_interval_field_name", side: "left" },
  { selector: "#intervalFieldAlt", textKey: "help_interval_field_alt", side: "left" },
  { selector: "#intervalFieldSemitones", textKey: "help_interval_field_semitones", side: "left" },
  { selector: "#intervalFieldRecuerda", textKey: "help_interval_field_recuerda", side: "left" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_interval", side: "top" },
];

const HELP_CALLOUTS_INTERVAL_GENERATION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#instrumentToggle", textKey: "help_instrument_toggle", side: "top" },
  { selector: "#guitarHandednessToggle", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_interval_generation", side: "top" },
  { selector: "#panelIntervalGeneration", textKey: "help_interval_gen_panel", side: "left" },
  { selector: "#intervalGenRootRow", textKey: "help_interval_gen_root", side: "left" },
  { selector: "#intervalGenPlaybackMode", textKey: "help_interval_gen_playback_mode", side: "bottom" },
  { selector: "#intervalGenPlayReverse", textKey: "help_interval_gen_play_reverse", side: "bottom" },
  { selector: "#intervalGenPlay", textKey: "help_interval_gen_play", side: "bottom" },
  { selector: "#intervalGenFieldNotes", textKey: "help_interval_gen_field_notes", side: "left" },
  { selector: "#intervalGenFieldName", textKey: "help_interval_gen_field_name", side: "left" },
  { selector: "#intervalGenFieldSemitones", textKey: "help_interval_field_semitones", side: "left" },
  { selector: "#intervalGenTableWrap", textKey: "help_interval_gen_table", side: "left" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_interval_generation", side: "top" },
];

const HELP_CALLOUTS_INTERVAL_PRACTICE = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#soundOutputToggle", textKey: "help_sound_output", side: "bottom" },
  { selector: "#staffCanvas", textKey: "help_interval_practice_staff", side: "top" },
  { selector: "#panelIntervalPractice", textKey: "help_interval_practice_panel", side: "left" },
  { selector: "#intervalPracticeStart", textKey: "help_interval_practice_start", side: "bottom" },
  { selector: "#intervalPracticeRepeat", textKey: "help_interval_practice_repeat", side: "bottom" },
  { selector: "#intervalPracticeNext", textKey: "help_interval_practice_next", side: "bottom" },
  { selector: "#intervalPracticeHelp", textKey: "help_interval_practice_process", side: "bottom" },
  { selector: "#intervalPracticeReview", textKey: "help_interval_practice_review", side: "bottom" },
  { selector: "#intervalPracticeOptions", textKey: "help_interval_practice_options", side: "left" },
  { selector: "#intervalPracticeRepetitionsRow", textKey: "help_interval_practice_repetitions", side: "left" },
  { selector: "#intervalPracticeFilter", textKey: "help_interval_practice_filter", side: "bottom" },
  { selector: "#intervalPracticePlaybackMode", textKey: "help_interval_practice_playback", side: "bottom" },
  { selector: "#intervalPracticeScoreField", textKey: "help_interval_practice_score", side: "left" },
  { selector: "#intervalPracticeNameField", textKey: "help_interval_practice_result", side: "left" },
  { selector: "#intervalPracticeTableWrap", textKey: "help_interval_practice_table", side: "left" },
  { selector: "#sharedPiano", textKey: "help_interval_practice_piano", side: "top" },
];

function helpCalloutsForMode(mode) {
  if (mode === "note_detection") return HELP_CALLOUTS_NOTE_DETECTION;
  if (mode === "detection") return HELP_CALLOUTS_DETECTION;
  if (mode === "interval_detection") return HELP_CALLOUTS_INTERVAL_DETECTION;
  if (mode === "interval_generation") return HELP_CALLOUTS_INTERVAL_GENERATION;
  if (mode === "interval_practice") return HELP_CALLOUTS_INTERVAL_PRACTICE;
  if (mode === "generation") return HELP_CALLOUTS_GENERATION;
  if (mode === "circle_fifths") return HELP_CALLOUTS_CIRCLE_FIFTHS;
  if (mode === "scales") return HELP_CALLOUTS_SCALES;
  if (mode === "metronome") return HELP_CALLOUTS_METRONOME;
  return [];
}

function isHelpAvailableForMode(mode) {
  return helpCalloutsForMode(mode).length > 0;
}


global.MidiChordsHelpCallouts = Object.freeze({
  helpCalloutsForMode,
  isHelpAvailableForMode,
});
})(globalThis);
