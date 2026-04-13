// Feature flag: keep tuner code but hide/disable it by default.
const TUNER_FEATURE_ENABLED = false;

/** Respaldo si `/api/meta` no devuelve `app_version` (debe coincidir con `APP_VERSION` en el worker). */
const WEB_APP_VERSION_FALLBACK = "1.0.2";

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
  appVersion: WEB_APP_VERSION_FALLBACK,
  activeDetectionNotes: new Set(),
  activeMidiLiveNotes: new Set(),
  detectionResult: null,
  generatedChord: null,
  circleTonicPc: 0,
  /** "major": circleTonicPc es la tónica mayor; "minor": es la fundamental menor (relativa mayor = +3 semitonos). */
  circleKeyMode: "major",
  circleChordRootPc: 0,
  circleFifthsResizeScheduled: false,
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
  metronomeVolume: 100,
  currentBeat: -1,
  metronomeDisplayBeat: -1,
  currentSubclick: 0,
  metronomeTickCount: 0,
  metronomeDirection: 1,
  metronomeMotionStartTs: 0,
  metronomeVisualDelayTimer: null,
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
    inputDeviceId: "",
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
    metronomeRegions: {},
  },
  heldChordVoices: new Map(),
  heldInputVoices: new Map(),
  inputDragActive: false,
  inputDragNote: null,
  inputDragInstrument: null,
  guitarSuppressNextClick: false,
  guitarSuppressNextClickTimer: null,
  detectionShiftPressed: false,
  shiftPressed: false,
  help: {
    active: false,
    bindings: [],
    activeTarget: null,
    activeItem: null,
  },
  detectionMouseChordNotes: new Set(),
  detectionMidiHeldNotes: new Set(),
  intervalNotes: [],
  intervalMelodyActive: false,
  intervalPlayingNote: null,
  intervalPlayingIdx: null,
  intervalPlayGeneration: 0,
  midiInputSoundEnabled: true,
  /** Screen Wake Lock (detección + MIDI); renovar con cada nota. */
  midiScreenWakeLock: null,
  midiScreenWakeLockTimer: null,
  midiScreenWakeLockWanted: false,
  heldMidiInputVoices: new Map(),
  audioSampleCache: {},
  audioSampleLoadPromise: null,
};

const UI_TEXTS = {
  es: {
    mode_detection: "Detección de Acordes",
    mode_interval_detection: "Detección de Intervalos",
    mode_generation: "Generación de Acordes",
    mode_circle_fifths: "Círculo de quintas",
    mode_scales: "Escalas",
    mode_metronome: "Metrónomo",
    mode_tuner: "Afinador",
    staff: "Pentagrama",
    heading_detection: "Detección",
    heading_interval_detection: "Intervalos",
    heading_generation: "Generación de Acordes",
    heading_circle_fifths: "Círculo de quintas",
    heading_scales: "Escalas",
    heading_metronome: "Metrónomo",
    heading_tuner: "Afinador",
    heading_metronome_settings: "Configuración de Metrónomo",
    heading_tuner_settings: "Configuración de Afinador",
    hint_detection: "Pulsa notas en piano/guitarra para detectar acordes o usa un dispositivo MIDI.",
    hint_interval_detection: "Pulsa dos notas (ratón, teclado o MIDI) para detectar el intervalo.",
    interval_play_reverse: "Reproducir descendente",
    label_interval_notes: "Notas:",
    label_interval_name: "Intervalo:",
    label_interval_semitones: "Semitonos:",
    help_staff_interval: "Pentagrama de intervalos: muestra las dos últimas notas pulsadas.",
    help_interval_panel: "Panel de intervalos: controles y resultado del intervalo actual.",
    help_interval_play: "Reproduce las dos notas del intervalo de forma melódica.",
    help_interval_clear: "Limpia las notas activas para comenzar de nuevo.",
    help_interval_field_notes: "Notas: las dos últimas notas pulsadas.",
    help_interval_field_name: "Nombre del intervalo detectado.",
    help_interval_field_semitones: "Número de semitonos entre las dos notas.",
    help_interval_field_recuerda: "Canción mnemotécnica: pulsa el nombre para activar la melodía de referencia en el pentagrama y reproducirla.",
    help_instrument_surface_interval: "Teclado interactivo: pulsa notas para detectar intervalos (también vía MIDI). Cada pulsación añade la nota al par; la más antigua se descarta automáticamente.",
    label_interval_recuerda: "Ejemplo:",
    help_interval_play_reverse: "Reproduce el intervalo de forma descendente (nota alta → nota baja).",
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
    label_metronome_volume: "Volumen",
    label_beats: "Pulsos",
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
    label_tuner_input: "Entrada",
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
    donation_title: "Apoya MIDI Piano & Guitar Chords",
    donation_text: "Este proyecto está pensado para mantenerse siempre gratis y sin publicidad. Tu ayuda permite cubrir costes de desarrollo, mantenimiento, infraestructura y tiempo de soporte para seguir mejorándolo.",
    donation_button: "Donar",
    feedback_panel_title: "Comentarios",
    feedback_panel_text: "Puedes enviarnos comentarios sobre la página y sugerencias de mejora para seguir evolucionando la herramienta.",
    feedback_open: "Enviar comentarios",
    feedback_modal_title: "Enviar comentarios",
    feedback_help: "Envíanos sugerencias o errores que hayas detectado.",
    feedback_name: "Nombre",
    feedback_email: "Email",
    feedback_message: "Comentario",
    downloads_panel_title: "Descargas",
    downloads_panel_text: "Descarga la app para PC y móvil, o abre las tiendas oficiales.",
    downloads_open: "Ver descargas",
    downloads_modal_title: "Descargas",
    downloads_modal_intro: "Elige tu plataforma para descargar la app.",
    downloads_pc_title: "PC/Mac",
    downloads_mobile_title: "Móvil",
    downloads_windows_store: "Windows (Microsoft Store)",
    downloads_macos_dmg: "macOS (App Store)",
    downloads_linux_deb: "Linux (.deb) (GitHub Releases)",
    downloads_ios_appstore: "iOS (App Store)",
    downloads_android_googleplay: "Android (Google Play)",
    feedback_send: "Enviar comentario",
    feedback_sending: "Enviando...",
    feedback_ok: "Gracias. Comentario enviado.",
    feedback_error: "No se pudo enviar. Inténtalo de nuevo.",
    help_button: "Ayuda",
    help_close_hint: "Pulsa Ayuda de nuevo para cerrar",
    help_mode_select: "Aquí cambias entre detección, generación, escalas y utilidades.",
    help_language: "Selecciona el idioma de la interfaz.",
    help_accidental: "Elige si prefieres nombres de notas con sostenidos (#) o bemoles (♭).",
    help_midi_toggle: "Activa o desactiva la entrada de un teclado/controlador MIDI.",
    help_inst_piano_btn: "Cambia el instrumento visual e interactivo a teclado.",
    help_inst_guitar_btn: "Cambia el instrumento visual e interactivo a guitarra.",
    help_guitar_handedness: "Ajusta la orientación de la guitarra (diestro/zurdo).",
    help_staff_detection: "Pentagrama de detección: muestra las notas activas y el acorde detectado.",
    help_staff_generation: "Pentagrama de generación: muestra el acorde generado y resalta la nota que pulses.",
    help_staff_scales: "Pentagrama de escalas: muestra las notas y la nota actual. Al tocar en teclado/guitarra se refleja aquí, y al pulsar notas del pentagrama también se reproducen.",
    help_staff_metronome: "Vista del metrónomo: muestra el pulso y el estado de reproducción.",
    help_detection_panel: "Panel de detección: controles y resultado del acorde actual.",
    help_detect_play: "Reproduce las notas activas del acorde detectado.",
    help_detect_clear: "Limpia todas las notas activas para comenzar de nuevo.",
    help_detect_midi_sound: "Activa o silencia el sonido de la entrada MIDI al tocar.",
    help_detect_result: "Resultado de la detección: nombre, notas, sobrantes e intervalos.",
    help_instrument_surface_detection: "Teclado/guitarra interactivos: pulsa para detectar acordes (también vía MIDI). Puedes mantener notas con Shift; lo que toques se refleja en el pentagrama y viceversa.",
    help_field_chord: "Acorde: nombre detectado con la mejor coincidencia.",
    help_field_notes: "Notas: notas que forman el acorde detectado.",
    help_field_extras: "Sobrantes: notas activas que no encajan en el acorde.",
    help_field_intervals: "Intervalos: distancias entre notas respecto a la tónica.",
    help_generation_panel: "Panel de generación: elige tónica, variante e inversión para construir acordes.",
    help_instrument_surface_generation: "Teclado/guitarra del acorde generado: al pulsar una nota se resalta en el pentagrama, y al pulsar una nota del pentagrama se marca en el instrumento con su octava. En piano se muestran mano derecha (arriba) y mano izquierda (una octava abajo); los números en teclas son digitaciones sugeridas de dedos.",
    help_gen_root: "Tónica del acorde a generar.",
    help_gen_variant: "Tipo o color del acorde (mayor, menor, 7, etc.).",
    help_gen_inversion: "Reordena las notas del acorde sin cambiar su calidad.",
    help_gen_play: "Reproduce el acorde generado.",
    help_gen_result_chord: "Nombre del acorde generado.",
    help_gen_result_notes: "Notas que forman el acorde generado.",
    help_gen_result_intervals: "Intervalos del acorde respecto a su tónica.",
    circle_hint: "Clic: fija la tónica y la tonalidad (mayor en el anillo exterior, menor natural relativa en el interior; misma armadura). Mayús+clic: elige un acorde diatónico, es decir, una triada sobre un grado de esa escala (mayor, menor o disminuida); no cambia la tónica.",
    help_circle_staff_footer: "Bajo el pentagrama: ayuda (clic / Mayús) para el círculo. Reproducir: botón ▶ sobre el círculo (arriba a la izquierda).",
    help_circle_panel: "Círculo de tónicas: elige la tonalidad con el ratón; con Mayús, un acorde diatónico.",
    help_circle_canvas: "Círculo de tónicas (en quintas): cada sector es una tónica posible. Clic con el ratón para fijar la tonalidad (mayor en el anillo exterior, menor relativa en el interior). Con Mayús pulsado, clic para elegir un acorde diatónico de esa tonalidad (triada en un grado de la escala) sin cambiar la tónica.",
    help_circle_play: "Reproduce el acorde seleccionado.",
    help_circle_result_chord: "Nombre del acorde según la tonalidad elegida.",
    help_guitar_variations_bar: "Barra de variaciones de guitarra: aquí aparecen posiciones alternativas del mismo acorde.",
    help_guitar_variation_btn: "Cada botón selecciona una digitación/posición distinta del acorde en guitarra.",
    help_scales_panel: "Panel de escalas: configura tónica, tipo y reproducción.",
    help_instrument_surface_scales: "Teclado/guitarra de escala: puedes tocar notas de la escala y verlas en el pentagrama; el pentagrama y el instrumento se mantienen sincronizados al tocar en cualquiera de los dos.",
    help_scale_root: "Tónica de la escala.",
    help_scale_type: "Tipo de escala (mayor, menor, modos, etc.).",
    help_scale_play: "Reproduce la escala actual.",
    help_scale_metronome_mode: "Activa reproducción de escala con pulsos de metrónomo.",
    help_scale_bpm: "Velocidad de reproducción de la escala.",
    help_scale_result_name: "Nombre completo de la escala seleccionada.",
    help_scale_result_notes: "Notas de la escala.",
    help_scale_result_intervals: "Intervalos de la escala respecto a la tónica.",
    help_metronome_panel: "Panel de metrónomo: tempo, compás, subdivisión y temporizador.",
    help_instrument_surface_metronome: "Piano del metrónomo: muestra las notas que entran por MIDI (si están habilitadas) y permite ver qué tocas mientras el metrónomo corre.",
    help_metro_start: "Inicia o detiene el metrónomo.",
    help_metro_volume: "Volumen del clic del metrónomo.",
    help_metro_bpm: "Tempo en pulsos por minuto.",
    help_metro_bpm_minus: "Disminuye el tempo (BPM) en 1.",
    help_metro_bpm_plus: "Aumenta el tempo (BPM) en 1.",
    help_metro_meter: "Número de pulsos por compás.",
    help_metro_meter_minus: "Disminuye los pulsos por compás en 1.",
    help_metro_meter_plus: "Aumenta los pulsos por compás en 1.",
    help_metro_subdivision: "Subdivide cada pulso en 1, 2, 3, 4 o 6 clics.",
    help_metro_bar_accent: "Activa acento en el primer pulso de cada compás.",
    help_metro_timer: "Activa un temporizador de parada automática.",
    help_metro_timer_values: "Duración del temporizador (minutos y segundos).",
    help_metro_yellow_points: "Puntos amarillos: representan los pulsos del compás actual.",
    help_metro_scale_axis: "Escala/eje del metrónomo: marca el recorrido y la subdivisión del pulso.",
    help_metro_red_ball: "Bola roja: indica la posición instantánea del pulso en movimiento.",
    detection_staff_shift_hint: "Mantén Shift pulsado para sostener notas",
    scale_staff_guitar_shift_hint: "Mantén Shift y pulsa una tónica para cambiar el inicio de la escala",
    staff_no_active_notes: "Sin notas activas",
  },
  en: {
    mode_detection: "Chord Detection",
    mode_interval_detection: "Interval Detection",
    mode_generation: "Chord Generation",
    mode_circle_fifths: "Circle of Fifths",
    mode_scales: "Scales",
    mode_metronome: "Metronome",
    mode_tuner: "Tuner",
    staff: "Staff",
    heading_detection: "Detection",
    heading_interval_detection: "Intervals",
    heading_generation: "Chord Generation",
    heading_circle_fifths: "Circle of Fifths",
    heading_scales: "Scales",
    heading_metronome: "Metronome",
    heading_tuner: "Tuner",
    heading_metronome_settings: "Metronome Settings",
    heading_tuner_settings: "Tuner Settings",
    hint_detection: "Press notes on piano/guitar to detect chords or use a MIDI device.",
    hint_interval_detection: "Press two notes (mouse, keyboard or MIDI) to detect the interval.",
    interval_play_reverse: "Play descending",
    label_interval_notes: "Notes:",
    label_interval_name: "Interval:",
    label_interval_semitones: "Semitones:",
    help_staff_interval: "Interval staff: shows the two latest pressed notes.",
    help_interval_panel: "Interval panel: controls and current interval output.",
    help_interval_play: "Play the two interval notes melodically.",
    help_interval_clear: "Clear active notes and start over.",
    help_interval_field_notes: "Notes: the two latest pressed notes.",
    help_interval_field_name: "Name of the detected interval.",
    help_interval_field_semitones: "Number of semitones between the two notes.",
    help_interval_field_recuerda: "Mnemonic song: tap the name to activate the reference melody on the staff and play it.",
    help_instrument_surface_interval: "Interactive keyboard: press notes to detect intervals (also via MIDI). Each press adds a note to the pair; the oldest is automatically discarded.",
    label_interval_recuerda: "Example:",
    help_interval_play_reverse: "Play the interval descending (high note → low note).",
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
    label_metronome_volume: "Volume",
    label_beats: "Beats",
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
    label_tuner_input: "Input",
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
    donation_title: "Support MIDI Piano & Guitar Chords",
    donation_text: "This project is designed to stay free forever and ad-free. Your support helps cover development, maintenance, infrastructure, and support time so we can keep improving it.",
    donation_button: "Donate",
    feedback_panel_title: "Feedback",
    feedback_panel_text: "You can send comments about the website and suggestions for improvements to keep evolving the tool.",
    feedback_open: "Send feedback",
    feedback_modal_title: "Send feedback",
    feedback_help: "Send us suggestions or report issues you found.",
    feedback_name: "Name",
    feedback_email: "Email",
    feedback_message: "Comment",
    downloads_panel_title: "Downloads",
    downloads_panel_text: "Download the app for PC and mobile, or open the official stores.",
    downloads_open: "View downloads",
    downloads_modal_title: "Downloads",
    downloads_modal_intro: "Choose your platform to download the app.",
    downloads_pc_title: "PC/Mac",
    downloads_mobile_title: "Mobile",
    downloads_windows_store: "Windows (Microsoft Store)",
    downloads_macos_dmg: "macOS (App Store)",
    downloads_linux_deb: "Linux (.deb) (GitHub Releases)",
    downloads_ios_appstore: "iOS (App Store)",
    downloads_android_googleplay: "Android (Google Play)",
    feedback_send: "Send feedback",
    feedback_sending: "Sending...",
    feedback_ok: "Thanks. Feedback sent.",
    feedback_error: "Could not send. Please try again.",
    help_button: "Help",
    help_close_hint: "Click Help again to close",
    help_mode_select: "Switch between detection, generation, scales, and utility tools here.",
    help_language: "Choose the interface language.",
    help_accidental: "Set whether note names prefer sharps (#) or flats (♭).",
    help_midi_toggle: "Enable or disable MIDI keyboard/controller input.",
    help_inst_piano_btn: "Switch the interactive instrument to piano.",
    help_inst_guitar_btn: "Switch the interactive instrument to guitar.",
    help_guitar_handedness: "Set guitar orientation (right-handed/left-handed).",
    help_staff_detection: "Detection staff: shows active notes and the detected chord.",
    help_staff_generation: "Generation staff: shows the generated chord and highlights the note you press.",
    help_staff_scales: "Scale staff: shows scale notes and the current note. Playing notes on keyboard/guitar is reflected here, and clicking staff notes also triggers playback.",
    help_staff_metronome: "Metronome view: shows pulse and playback state.",
    help_detection_panel: "Detection panel: controls and current chord output.",
    help_detect_play: "Play the currently active detected notes.",
    help_detect_clear: "Clear all active notes and start over.",
    help_detect_midi_sound: "Enable or mute MIDI input sound while playing.",
    help_detect_result: "Detection output: chord name, notes, extras, and intervals.",
    help_instrument_surface_detection: "Interactive keyboard/guitar: press notes to detect chords (also via MIDI). Hold Shift to sustain notes; instrument and staff stay in sync both ways.",
    help_field_chord: "Chord: detected chord name with the best match.",
    help_field_notes: "Notes: notes that belong to the detected chord.",
    help_field_extras: "Extra notes: active notes that do not fit the chord.",
    help_field_intervals: "Intervals: note distances relative to the tonic.",
    help_generation_panel: "Generation panel: choose tonic, chord quality, and inversion.",
    help_instrument_surface_generation: "Generated-chord keyboard/guitar: pressing a note highlights it on the staff, and pressing a staff note highlights it on the instrument at the same octave. In piano mode, right hand notes (upper register) and left hand notes (one octave below) are shown; numbers on keys are suggested fingerings.",
    help_gen_root: "Root note of the chord to generate.",
    help_gen_variant: "Chord quality/type (major, minor, 7th, etc.).",
    help_gen_inversion: "Reorders chord notes without changing chord quality.",
    help_gen_play: "Play the generated chord.",
    help_gen_result_chord: "Generated chord name.",
    help_gen_result_notes: "Notes that form the generated chord.",
    help_gen_result_intervals: "Chord intervals relative to its tonic.",
    circle_hint: "Click: sets the tonic and key (major on the outer ring, relative natural minor on the inner; same key signature). Shift+click: choose a diatonic chord—a triad on a scale degree (major, minor, or diminished); does not change the tonic.",
    help_circle_staff_footer: "Below the staff: hint (click / Shift) for the circle. Play: ▶ button on the circle (top left).",
    help_circle_panel: "Circle of tonics: choose the key with the mouse; with Shift, a diatonic chord.",
    help_circle_canvas: "Circle of tonics (by fifths): each sector is a possible tonic. Click to set the key (major on the outer ring, relative natural minor on the inner). Hold Shift and click to pick a diatonic chord in that key (a triad on a scale degree) without changing the tonic.",
    help_circle_play: "Play the selected chord.",
    help_circle_result_chord: "Chord name in the chosen key context.",
    help_guitar_variations_bar: "Guitar variations bar: alternative positions for the same chord appear here.",
    help_guitar_variation_btn: "Each button selects a different guitar fingering/position for the chord.",
    help_scales_panel: "Scales panel: set tonic, scale type, and playback.",
    help_instrument_surface_scales: "Scale keyboard/guitar: play scale notes and see them on the staff; staff and instrument stay synced when you interact with either one.",
    help_scale_root: "Scale tonic.",
    help_scale_type: "Scale type (major, minor, modes, etc.).",
    help_scale_play: "Play the current scale.",
    help_scale_metronome_mode: "Enable scale playback synced with metronome pulses.",
    help_scale_bpm: "Scale playback speed.",
    help_scale_result_name: "Full selected scale name.",
    help_scale_result_notes: "Scale notes.",
    help_scale_result_intervals: "Scale intervals relative to tonic.",
    help_metronome_panel: "Metronome panel: tempo, meter, subdivision, and timer.",
    help_instrument_surface_metronome: "Metronome piano: displays incoming MIDI notes (when enabled) so you can monitor what you play while the metronome runs.",
    help_metro_start: "Start or stop the metronome.",
    help_metro_volume: "Metronome click volume.",
    help_metro_bpm: "Tempo in beats per minute.",
    help_metro_bpm_minus: "Decrease tempo (BPM) by 1.",
    help_metro_bpm_plus: "Increase tempo (BPM) by 1.",
    help_metro_meter: "Beats per bar.",
    help_metro_meter_minus: "Decrease beats per bar by 1.",
    help_metro_meter_plus: "Increase beats per bar by 1.",
    help_metro_subdivision: "Subdivide each beat into 1, 2, 3, 4, or 6 clicks.",
    help_metro_bar_accent: "Enable accent on the first beat of each bar.",
    help_metro_timer: "Enable auto-stop timer.",
    help_metro_timer_values: "Timer duration (minutes and seconds).",
    help_metro_yellow_points: "Yellow points: represent beats in the current bar.",
    help_metro_scale_axis: "Metronome scale/axis: shows pulse travel and subdivision.",
    help_metro_red_ball: "Red ball: shows current pulse position in motion.",
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
const PC_TO_DIATONIC_LETTER = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]; // convención sostenidos
const PC_TO_DIATONIC_FLAT   = [0, 1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6]; // convención bemoles

const PIANO_SAMPLE_URLS = {
  48: "/static/samples/grand_piano/C3.mp3",
  52: "/static/samples/grand_piano/E3.mp3",
  55: "/static/samples/grand_piano/G3.mp3",
  60: "/static/samples/grand_piano/C4.mp3",
  64: "/static/samples/grand_piano/E4.mp3",
  67: "/static/samples/grand_piano/G4.mp3",
  72: "/static/samples/grand_piano/C5.mp3",
};

const GUITAR_SAMPLE_URLS = {
  40: "/static/samples/guitar_nylon/E2.mp3",
  45: "/static/samples/guitar_nylon/A2.mp3",
  50: "/static/samples/guitar_nylon/D3.mp3",
  52: "/static/samples/guitar_nylon/E3.mp3",
  55: "/static/samples/guitar_nylon/G3.mp3",
  59: "/static/samples/guitar_nylon/B3.mp3",
  64: "/static/samples/guitar_nylon/E4.mp3",
};

const METRONOME_SAMPLE_URL = "/static/metronome.mp3";
const DONATE_URL = "https://buy.stripe.com/eVqdR9fs19MVcIgeVH8g000";
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

const HELP_CALLOUTS_DETECTION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#instPianoBtn", textKey: "help_inst_piano_btn", side: "top" },
  { selector: "#instGuitarBtn", textKey: "help_inst_guitar_btn", side: "top" },
  { selector: "#guitarHandedness", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_detection", side: "top" },
  { selector: "#panelDetection", textKey: "help_detection_panel", side: "left" },
  { selector: "#detectPlay", textKey: "help_detect_play", side: "bottom" },
  { selector: "#detectClear", textKey: "help_detect_clear", side: "bottom" },
  { selector: "#detectMidiSoundToggle", textKey: "help_detect_midi_sound", side: "top" },
  { selector: "#detectFieldChord", textKey: "help_field_chord", side: "left" },
  { selector: "#detectFieldNotes", textKey: "help_field_notes", side: "left" },
  { selector: "#detectFieldExtras", textKey: "help_field_extras", side: "left" },
  { selector: "#detectFieldIntervals", textKey: "help_field_intervals", side: "left" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_detection", side: "top" },
];
const HELP_CALLOUTS_GENERATION = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#instPianoBtn", textKey: "help_inst_piano_btn", side: "top" },
  { selector: "#instGuitarBtn", textKey: "help_inst_guitar_btn", side: "top" },
  { selector: "#guitarHandedness", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_generation", side: "top" },
  { selector: "#panelGeneration", textKey: "help_generation_panel", side: "left" },
  { selector: "#genRoot", textKey: "help_gen_root", side: "left" },
  { selector: "#genVariant", textKey: "help_gen_variant", side: "left" },
  { selector: "#genInversion", textKey: "help_gen_inversion", side: "left" },
  { selector: "#genPlay", textKey: "help_gen_play", side: "bottom" },
  { selector: "#genFieldChord", textKey: "help_gen_result_chord", side: "left" },
  { selector: "#genFieldNotes", textKey: "help_gen_result_notes", side: "left" },
  { selector: "#genFieldIntervals", textKey: "help_gen_result_intervals", side: "left" },
  { selector: "#guitarVariationBar", textKey: "help_guitar_variations_bar", side: "top" },
  { selector: "#guitarVariationBar .guitar-var-btn", textKey: "help_guitar_variation_btn", side: "top" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_generation", side: "top" },
];
const HELP_CALLOUTS_CIRCLE_FIFTHS = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#instPianoBtn", textKey: "help_inst_piano_btn", side: "top" },
  { selector: "#instGuitarBtn", textKey: "help_inst_guitar_btn", side: "top" },
  { selector: "#guitarHandedness", textKey: "help_guitar_handedness", side: "top" },
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
  { selector: "#instPianoBtn", textKey: "help_inst_piano_btn", side: "top" },
  { selector: "#instGuitarBtn", textKey: "help_inst_guitar_btn", side: "top" },
  { selector: "#guitarHandedness", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_scales", side: "top" },
  { selector: "#panelScales", textKey: "help_scales_panel", side: "left" },
  { selector: "#scaleRoot", textKey: "help_scale_root", side: "left" },
  { selector: "#scaleType", textKey: "help_scale_type", side: "left" },
  { selector: "#scalePlay", textKey: "help_scale_play", side: "bottom" },
  { selector: "#scaleModeMetronome", textKey: "help_scale_metronome_mode", side: "top" },
  { selector: "#scaleBpm", textKey: "help_scale_bpm", side: "left" },
  { selector: "#scaleName", textKey: "help_scale_result_name", side: "left" },
  { selector: "#scaleNotes", textKey: "help_scale_result_notes", side: "left" },
  { selector: "#scaleIntervals", textKey: "help_scale_result_intervals", side: "left" },
  { selector: "#instrumentArea", textKey: "help_instrument_surface_scales", side: "top" },
];
const HELP_CALLOUTS_METRONOME = [
  { selector: "#modeSelect", textKey: "help_mode_select", side: "bottom" },
  { selector: "#language", textKey: "help_language", side: "bottom" },
  { selector: "#accidental", textKey: "help_accidental", side: "bottom" },
  { selector: "#midiToggle", textKey: "help_midi_toggle", side: "bottom" },
  { selector: "#instPianoBtn", textKey: "help_inst_piano_btn", side: "top" },
  { selector: "#instGuitarBtn", textKey: "help_inst_guitar_btn", side: "top" },
  { selector: "#guitarHandedness", textKey: "help_guitar_handedness", side: "top" },
  { selector: "#staffCanvas", textKey: "help_staff_metronome", side: "top" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_metronome", side: "top" },
  { selector: "#panelMetronome", textKey: "help_metronome_panel", side: "left" },
  { selector: "#metroToggle", textKey: "help_metro_start", side: "bottom" },
  { selector: "#metroMidiSoundToggle", textKey: "help_detect_midi_sound", side: "top" },
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
  { selector: "#staffCanvas", textKey: "help_staff_interval", side: "top" },
  { selector: "#panelIntervalDetection", textKey: "help_interval_panel", side: "left" },
  { selector: "#intervalPlayReverse", textKey: "help_interval_play_reverse", side: "bottom" },
  { selector: "#intervalPlay", textKey: "help_interval_play", side: "bottom" },
  { selector: "#intervalClear", textKey: "help_interval_clear", side: "bottom" },
  { selector: "#intervalMidiSoundToggle", textKey: "help_detect_midi_sound", side: "top" },
  { selector: "#intervalFieldNotes", textKey: "help_interval_field_notes", side: "left" },
  { selector: "#intervalFieldName", textKey: "help_interval_field_name", side: "left" },
  { selector: "#intervalFieldSemitones", textKey: "help_interval_field_semitones", side: "left" },
  { selector: "#intervalFieldRecuerda", textKey: "help_interval_field_recuerda", side: "left" },
  { selector: "#sharedPiano", textKey: "help_instrument_surface_interval", side: "top" },
];

function helpCalloutsForMode(mode) {
  if (mode === "detection") return HELP_CALLOUTS_DETECTION;
  if (mode === "interval_detection") return HELP_CALLOUTS_INTERVAL_DETECTION;
  if (mode === "generation") return HELP_CALLOUTS_GENERATION;
  if (mode === "circle_fifths") return HELP_CALLOUTS_CIRCLE_FIFTHS;
  if (mode === "scales") return HELP_CALLOUTS_SCALES;
  if (mode === "metronome") return HELP_CALLOUTS_METRONOME;
  return [];
}

function isHelpAvailableForMode(mode) {
  return helpCalloutsForMode(mode).length > 0;
}

function el(id) {
  return document.getElementById(id);
}

function isChordGenerationLikeMode() {
  return state.mode === "generation" || state.mode === "circle_fifths";
}

/** #/♭: leer el <select> visible primero (state puede desincronizarse si no hubo evento change). */
function accidentalPreferFlatFromUi() {
  const node = el("accidental");
  if (node && node.value === "flat") return true;
  return state.accidental === "flat";
}

function currentAccidentalValue() {
  const node = el("accidental");
  if (node && (node.value === "flat" || node.value === "sharp")) return node.value;
  return state.accidental;
}

function noteNameFromPc(pc) {
  const preferFlat = accidentalPreferFlatFromUi();
  return NOTE_LABELS[state.language][preferFlat ? "flat" : "sharp"][((pc % 12) + 12) % 12];
}

/** Etiqueta del teclado: base + alteración sin hueco tipográfico entre ambos. */
function pianoKeyLabelHtml(pc) {
  const label = noteNameFromPc(pc);
  if (label.endsWith("#")) {
    const base = label.slice(0, -1);
    return `<span class="key-label"><span class="key-note-base">${base}</span><span class="key-accidental">#</span></span>`;
  }
  if (label.endsWith("♭")) {
    const base = label.slice(0, -1);
    return `<span class="key-label"><span class="key-note-base">${base}</span><span class="key-accidental">♭</span></span>`;
  }
  return `<span class="key-label">${label}</span>`;
}

function noteNameFromPcStaff(pc, preferFlat) {
  return NOTE_LABELS[state.language][preferFlat ? "flat" : "sharp"][((pc % 12) + 12) % 12];
}

/** Sentido horario desde arriba (Do), avanzando de quinta en quinta. */
const CIRCLE_FIFTHS_ORDER = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5];

const DIATONIC_DEGREE_SUFFIX = {
  0: "",
  2: "m",
  4: "m",
  5: "",
  7: "",
  9: "m",
  11: "dim",
};

const ROMAN_BY_DEGREE = {
  0: "I",
  2: "ii",
  4: "iii",
  5: "IV",
  7: "V",
  9: "vi",
  11: "vii°",
};

/**
 * Fondos diatónicos (referencia visual): mayor = melocotón claro; tónica I = beige/marrón más oscuro;
 * menor = lavanda claro; vii° = rosa pálido (como en la maqueta del círculo).
 */
const CIRCLE_DEGREE_FILL = {
  0: { base: "#f0d5b8", tonic: "#c9a06a" },
  2: "#ddd0e8",
  4: "#ddd0e8",
  5: "#f0d5b8",
  7: "#f0d5b8",
  9: "#ddd0e8",
  11: "#f5d4dc",
};

/** Texto diatónico: I/vi verde; IV/ii azul; V/iii/vii° rojo (legible sobre fondos claros). */
const CIRCLE_DEGREE_TEXT = {
  0: "#1b5e20",
  2: "#0d47a1",
  4: "#b71c1c",
  5: "#1565c0",
  7: "#c62828",
  9: "#2e7d32",
  11: "#c62828",
};

function diatonicTriadSuffixMajorKey(tonicPc, rootPc) {
  const d = (rootPc - tonicPc + 12) % 12;
  if (Object.prototype.hasOwnProperty.call(DIATONIC_DEGREE_SUFFIX, d)) {
    return { suffix: DIATONIC_DEGREE_SUFFIX[d], degree: d };
  }
  return { suffix: "", degree: null };
}

/**
 * Triadas diatónicas en tonalidad menor natural (intervalos desde la tónica menor).
 * III/VI/VII como ♭ respecto a la mayor paralela (p. ej. en Lam: Do = ♭III).
 */
const ROMAN_BY_MINOR_NATURAL_INTERVAL = {
  0: "i",
  2: "ii°",
  3: "\u266DIII",
  5: "iv",
  7: "v",
  8: "\u266DVI",
  10: "\u266DVII",
};

/** En canvas, dibuja numerales con el bem (\u266D) en superíndice respecto al número romano. */
function fillTextRomanMaybeFlatSuperscript(ctx, roman, x, y, fsRoman) {
  const ff = `"Avenir Next", "Segoe UI", sans-serif`;
  const flat = "\u266D";
  if (!roman) return;
  if (roman.charAt(0) !== flat) {
    ctx.font = `${fsRoman}px ${ff}`;
    ctx.fillText(roman, x, y);
    return;
  }
  const body = roman.slice(1);
  const supFs = Math.max(7, Math.round(fsRoman * 0.58));
  const rise = Math.round(fsRoman * 0.4);
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";
  ctx.font = `${supFs}px ${ff}`;
  const wFlat = ctx.measureText(flat).width;
  ctx.font = `${fsRoman}px ${ff}`;
  const wBody = ctx.measureText(body).width;
  const gap = Math.max(2, Math.round(fsRoman * 0.14));
  const total = wFlat + gap + wBody;
  let drawX = x - total / 2;
  ctx.font = `${supFs}px ${ff}`;
  ctx.fillText(flat, drawX, y - rise);
  drawX += wFlat + gap;
  ctx.font = `${fsRoman}px ${ff}`;
  ctx.fillText(body, drawX, y);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
}

function diatonicTriadSuffixNaturalMinorKey(minorTonicPc, rootPc) {
  const d = (rootPc - minorTonicPc + 12) % 12;
  const MAP = {
    0: { suffix: "m" },
    2: { suffix: "dim" },
    3: { suffix: "" },
    5: { suffix: "m" },
    7: { suffix: "m" },
    8: { suffix: "" },
    10: { suffix: "" },
  };
  if (!Object.prototype.hasOwnProperty.call(MAP, d)) {
    return { suffix: "", interval: null, roman: "" };
  }
  return {
    suffix: MAP[d].suffix,
    interval: d,
    roman: ROMAN_BY_MINOR_NATURAL_INTERVAL[d] || "",
  };
}

/**
 * Mapea intervalo menor natural → clave de grado mayor para CIRCLE_DEGREE_TEXT / rellenos.
 * VII comparte lavanda con III/VI (no el rosa de vii°); ii° usa el rosa de grado 11.
 */
function circleMinorIntervalToMajorDegreeKey(intervalD) {
  const map = { 0: 0, 2: 11, 3: 4, 5: 5, 7: 7, 8: 9, 10: 9 };
  return map[intervalD] !== undefined ? map[intervalD] : 0;
}

function circleDiatonicSliceFill(degree, pc, tonicPc) {
  if (degree === 0) {
    return pc === tonicPc ? CIRCLE_DEGREE_FILL[0].tonic : CIRCLE_DEGREE_FILL[0].base;
  }
  return CIRCLE_DEGREE_FILL[degree];
}

/** En el anillo mayor del sector solo la triada mayor I, IV o V es la función diatónica (no Re mayor = ii ni Si mayor = vii°). */
function circleUpperBandIsDiatonicMajorTriad(degree) {
  return degree === 0 || degree === 5 || degree === 7;
}

/** El anillo inferior muestra la menor relativa; ii/iii/vi coinciden con Rem/Mim/Lam en los sectores correctos. */
function circleLowerBandIsDiatonicMinorTriad(minorDeg) {
  return minorDeg === 2 || minorDeg === 4 || minorDeg === 9;
}

/** Índice 0..11 en orden de quintas (C arriba): 0–6 → #, 7–11 → ♭. */
function circleSignatureLabelForSliceIndex(i) {
  if (i <= 6) {
    const n = i;
    if (n === 0) return "0";
    return `${n}♯`;
  }
  const fb = 12 - i;
  return `${fb}♭`;
}

/** Menor relativa de una mayor (ej. Do → La). */
function relativeMinorPcFromMajorPc(majorPc) {
  return (Number(majorPc) + 9 + 12) % 12;
}

function circleMinorLabel(majorPc) {
  const mpc = relativeMinorPcFromMajorPc(majorPc);
  return `${noteNameFromPc(mpc)}m`;
}

function circleFifthsRadiiPx(w, h) {
  const rOuter = Math.min(w, h) * 0.46;
  const rHole = rOuter * 0.18;
  /** Anillo de ♯/♭: mitad del ancho que tenía la franja exterior respecto a la guía antigua (0.775·R). */
  const rGuideSigMajRef = rOuter * 0.775;
  const bandSig = (rOuter - rGuideSigMajRef) / 2;
  const rSigInner = rOuter - bandSig;
  const rSig = (rOuter + rSigInner) / 2;
  /** Frontera mayor/menor: más cerca del centro → anillo mayor más estrecho y anillo menor más ancho (menos solape de textos). */
  const rGuideMajMin = rOuter * 0.52;
  return {
    rOuter,
    rHole,
    rSigInner,
    rSig,
    rMajName: rOuter * 0.72,
    rMajRoman: rOuter * 0.60,
    rMin: rOuter * 0.38,
    /** Romano bajo el nombre menor; más hacia el centro del anillo menor que el agujero. */
    rMinRoman: rOuter * 0.292,
    /** Líneas entre anillo de armadura / mayor / menor. */
    rGuideSigMaj: rSigInner,
    rGuideMajMin,
  };
}

function circleSliceIndexForPitchClass(pc) {
  const p = ((pc % 12) + 12) % 12;
  for (let i = 0; i < 12; i += 1) {
    if (CIRCLE_FIFTHS_ORDER[i] === p) return i;
  }
  return 0;
}

/** Raíz del acorde diatónico en tonalidad mayor (I, ii, iii, IV, V, vi, vii°). */
function chordRootPcForMajorScaleDegree(tonicPc, degree) {
  const inter = { 0: 0, 2: 2, 4: 4, 5: 5, 7: 7, 9: 9, 11: 11 };
  return (((tonicPc + inter[degree]) % 12) + 12) % 12;
}

/**
 * Arco entre dos ángulos en r: elige tramo corto o largo según preferNorth (−sin) o sur (+sin).
 * Usado para el arco superior IV–I–V (pasar por el norte, por encima de Do).
 */
function circlePathArc(ctx, r, aFrom, aTo, preferNorth) {
  let d = aTo - aFrom;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const shortSweep = d > Math.PI ? Math.PI * 2 - d : d;
  const longSweep = Math.PI * 2 - shortSweep;
  const midShort = aFrom + shortSweep / 2;
  const midLong = aFrom + longSweep / 2;
  const scoreNorth = (a) => -Math.sin(a);
  const scoreSouth = (a) => Math.sin(a);
  const score = preferNorth ? scoreNorth : scoreSouth;
  const sweep = score(midLong) > score(midShort) ? longSweep : shortSweep;
  const steps = 40;
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = aFrom + sweep * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/**
 * Arco en rHole entre dos ángulos: tramo por la parte inferior (Mi, Si, Fa#…),
 * coherente con ii–iii–vi en el anillo interior.
 */
function circlePathArcHoleBottom(ctx, r, aFrom, aTo) {
  let d = aTo - aFrom;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const shortSweep = d > Math.PI ? Math.PI * 2 - d : d;
  const longSweep = Math.PI * 2 - shortSweep;
  function avgSin(sweep) {
    let s = 0;
    for (let k = 0; k <= 16; k += 1) {
      const t = k / 16;
      const ang = aFrom + sweep * t;
      s += Math.sin(ang);
    }
    return s / 17;
  }
  const sweep = avgSin(longSweep) > avgSin(shortSweep) ? longSweep : shortSweep;
  const steps = 40;
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = aFrom + sweep * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/** Arco en r constante de ang0 a ang1 (recorrido corto positivo, hasta 2π). */
function circlePathArcSpan(ctx, r, ang0, ang1) {
  let d = ang1 - ang0;
  while (d <= 0) d += Math.PI * 2;
  while (d > Math.PI * 2) d -= Math.PI * 2;
  const steps = Math.max(8, Math.min(64, Math.ceil(48 * d / (Math.PI * 2))));
  for (let i = 1; i <= steps; i += 1) {
    const t = i / steps;
    const ang = ang0 + d * t;
    ctx.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
  }
}

/**
 * Perímetro de la unión de celdas diatónicas en la grilla (3 radios × 12 sectores):
 * solo aristas de celda (arcos en rHole, rGuideMajMin, rSigInner y radiales en límites de sector).
 * Diferencia simétrica de aristas → borde de la unión (mínimo en el sentido de perímetro de polígono ortogonal).
 * Esquina superior izquierda del IV = vértice (radial del a0 del IV, banda rSigInner).
 */
function strokeCircleDiatonicEnvelope(ctx, tonicPc, rSigInner, rGuideMajMin, rHole, dpr) {
  const R = [rHole, rGuideMajMin, rSigInner];
  /** Celda [slice][banda]: 0 = rHole–rGuide, 1 = rGuide–rSig. */
  const cell = [];
  for (let s = 0; s < 12; s += 1) {
    cell[s] = [false, false];
  }
  const minorMode = state.circleKeyMode === "minor";
  const minorTonic = minorMode ? ((state.circleTonicPc % 12) + 12) % 12 : null;
  if (minorMode) {
    const iiDimRoot = (minorTonic + 2 + 12) % 12;
    const iiLabelPc = (iiDimRoot + 3 + 12) % 12;
    for (let s = 0; s < 12; s += 1) {
      const pc = CIRCLE_FIFTHS_ORDER[s];
      const mpcRel = relativeMinorPcFromMajorPc(pc);
      const dU = (pc - minorTonic + 12) % 12;
      if ([3, 8, 10].includes(dU)) {
        cell[s][1] = true;
      }
      const dL = (mpcRel - minorTonic + 12) % 12;
      if ([0, 5, 7].includes(dL)) {
        cell[s][0] = true;
      } else if (pc === iiLabelPc) {
        cell[s][0] = true;
      }
    }
  } else {
    const viiRootPc = chordRootPcForMajorScaleDegree(tonicPc, 11);
    const viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
    for (let s = 0; s < 12; s += 1) {
      const pc = CIRCLE_FIFTHS_ORDER[s];
      const { degree } = diatonicTriadSuffixMajorKey(tonicPc, pc);
      const mpcRel = relativeMinorPcFromMajorPc(pc);
      const minorDeg = diatonicTriadSuffixMajorKey(tonicPc, mpcRel).degree;
      if (degree != null && circleUpperBandIsDiatonicMajorTriad(degree)) {
        cell[s][1] = true;
      }
      if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
        cell[s][0] = true;
      } else if (degree != null && pc === viiLabelSlicePc) {
        cell[s][0] = true;
      }
    }
  }

  /** Vértice: radial k ∈ [0,11] (ángulo = a0(k)), banda r ∈ {0,1,2} → R[r]. */
  function vKey(k, rBand) {
    return `${k}|${rBand}`;
  }
  function parseVKey(key) {
    const [ks, rs] = key.split("|");
    return { k: Number(ks), rBand: Number(rs) };
  }
  function vertexXY(key) {
    const { k, rBand } = parseVKey(key);
    const ang = circleSliceAngles(k).a0;
    const rad = R[rBand];
    return { x: Math.cos(ang) * rad, y: Math.sin(ang) * rad, ang, rad };
  }

  const edgeSet = new Set();
  function toggleEdge(id) {
    if (edgeSet.has(id)) edgeSet.delete(id);
    else edgeSet.add(id);
  }

  for (let s = 0; s < 12; s += 1) {
    for (let b = 0; b < 2; b += 1) {
      if (!cell[s][b]) continue;
      const ri = b;
      const ro = b + 1;
      /* Arco en sector s: (s, ro)–((s+1)%12, ro) y (s, ri)–((s+1)%12, ri). */
      toggleEdge(`arc|${s}|${ro}`);
      toggleEdge(`arc|${s}|${ri}`);
      /* Radial izq. sector s: (s, ri)–(s, ro); der.: ((s+1)%12, ri)–((s+1)%12, ro). */
      toggleEdge(`rad|${s}|${ri}|${ro}`);
      toggleEdge(`rad|${(s + 1) % 12}|${ri}|${ro}`);
    }
  }

  const adj = new Map();
  function addAdj(a, b) {
    if (!adj.has(a)) adj.set(a, []);
    adj.get(a).push(b);
  }
  const segByEndpoints = new Map();
  function undirKey(a, b) {
    return a < b ? `${a}↔${b}` : `${b}↔${a}`;
  }

  for (const eid of edgeSet) {
    const [type, ...rest] = eid.split("|");
    if (type === "arc") {
      const s = Number(rest[0]);
      const rBand = Number(rest[1]);
      const k0 = vKey(s, rBand);
      const k1 = vKey((s + 1) % 12, rBand);
      const a0 = circleSliceAngles(s).a0;
      const a1 = circleSliceAngles(s).a1;
      addAdj(k0, k1);
      addAdj(k1, k0);
      segByEndpoints.set(undirKey(k0, k1), { kind: "arc", r: R[rBand], a0, a1 });
    } else {
      const k = Number(rest[0]);
      const ri = Number(rest[1]);
      const ro = Number(rest[2]);
      const ka = vKey(k, ri);
      const kb = vKey(k, ro);
      const ang = circleSliceAngles(k).a0;
      addAdj(ka, kb);
      addAdj(kb, ka);
      segByEndpoints.set(undirKey(ka, kb), { kind: "rad", ang, r0: R[ri], r1: R[ro] });
    }
  }

  let ivIdx;
  if (minorMode) {
    const mt = minorTonic;
    const ivMajorPc = (mt + 8 + 12) % 12;
    ivIdx = circleSliceIndexForPitchClass(ivMajorPc);
  } else {
    ivIdx = circleSliceIndexForPitchClass(chordRootPcForMajorScaleDegree(tonicPc, 5));
  }
  const startKey = vKey(ivIdx, 2);
  if (!adj.has(startKey) || (adj.get(startKey) || []).length === 0) return;

  /** Primer paso: arco exterior IV→V (vértice (ivIdx+1, 2) = esquina superior derecha del IV). */
  const firstNeighbor = vKey((ivIdx + 1) % 12, 2);

  /** Arco más corto entre dos ángulos en radio r (misma convención que el resto del canvas). */
  function circlePathArcShort(ctx2, r, fromAng, toAng) {
    let delta = Math.atan2(Math.sin(toAng - fromAng), Math.cos(toAng - fromAng));
    const steps = Math.max(8, Math.min(64, Math.ceil(48 * Math.abs(delta) / (Math.PI * 2))));
    for (let j = 1; j <= steps; j += 1) {
      const t = j / steps;
      const ang = fromAng + delta * t;
      ctx2.lineTo(Math.cos(ang) * r, Math.sin(ang) * r);
    }
  }

  const path = [startKey];
  let cur = startKey;
  let prev = null;
  const maxSteps = edgeSet.size * 4 + 24;
  for (let step = 0; step < maxSteps; step += 1) {
    const neigh = (adj.get(cur) || []).filter((n) => n !== prev);
    if (neigh.length === 0) break;
    let next;
    if (prev === null) {
      next = neigh.includes(firstNeighbor) ? firstNeighbor : neigh[0];
    } else {
      next = neigh[0];
    }
    prev = cur;
    cur = next;
    path.push(cur);
    if (cur === startKey) break;
  }

  ctx.beginPath();
  const p0 = vertexXY(path[0]);
  ctx.moveTo(p0.x, p0.y);
  for (let i = 0; i < path.length - 1; i += 1) {
    const a = path[i];
    const b = path[i + 1];
    const seg = segByEndpoints.get(undirKey(a, b));
    if (!seg) continue;
    if (seg.kind === "arc") {
      const va = vertexXY(a);
      const vb = vertexXY(b);
      circlePathArcShort(ctx, seg.r, va.ang, vb.ang);
    } else {
      const vb = vertexXY(b);
      ctx.lineTo(vb.x, vb.y);
    }
  }
  ctx.closePath();
  ctx.strokeStyle = "#0a0a0a";
  ctx.lineWidth = Math.max(4, 4.8 * dpr);
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.stroke();
}

/**
 * Resaltado del acorde: banda superior (mayor + romanos mayores) o inferior (menor + romanos menores).
 * Lam (vi) vive en el sector de su mayor relativa (p. ej. Do), no en el sector La.
 */
function circleChordHighlightGeom(tonicPc, chordRootPc, generatedChord) {
  const rootFromState = ((chordRootPc % 12) + 12) % 12;
  const rootFromApi = generatedChord != null && generatedChord.root_pc != null
    ? (((Number(generatedChord.root_pc) % 12) + 12) % 12)
    : null;
  const root = rootFromApi != null ? rootFromApi : rootFromState;
  let suffix = "";
  if (generatedChord && generatedChord.suffix != null && generatedChord.suffix !== undefined) {
    suffix = String(generatedChord.suffix);
  }
  if (suffix === "" || suffix === "undefined") {
    if (state.circleKeyMode === "minor") {
      const mt = ((state.circleTonicPc % 12) + 12) % 12;
      suffix = diatonicTriadSuffixNaturalMinorKey(mt, root).suffix || "";
    } else {
      suffix = diatonicTriadSuffixMajorKey(tonicPc, root).suffix || "";
    }
  }
  if (suffix === "m") {
    const relMajPc = (root - 9 + 12) % 12;
    return {
      sliceIdx: circleSliceIndexForPitchClass(relMajPc),
      band: "minor",
    };
  }
  if (suffix === "dim") {
    const relMajPc = (root + 3 + 12) % 12;
    return {
      sliceIdx: circleSliceIndexForPitchClass(relMajPc),
      band: "minor",
    };
  }
  return {
    sliceIdx: circleSliceIndexForPitchClass(root),
    band: "major",
  };
}

/** Trapecio circular: solo contorno amarillo (sin relleno). */
function strokeCircleChordSelectionBand(ctx, rOut, rIn, a0, a1, dpr) {
  ctx.beginPath();
  ctx.moveTo(rOut * Math.cos(a0), rOut * Math.sin(a0));
  ctx.lineTo(rIn * Math.cos(a0), rIn * Math.sin(a0));
  ctx.arc(0, 0, rIn, a0, a1, false);
  ctx.lineTo(rOut * Math.cos(a1), rOut * Math.sin(a1));
  ctx.arc(0, 0, rOut, a1, a0, true);
  ctx.closePath();
  ctx.strokeStyle = "#f2bf2f";
  ctx.lineWidth = Math.max(2.5, 3 * dpr);
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.stroke();
}

const CIRCLE_SLICE_RAD = (Math.PI * 2) / 12;

/** Do (índice 0) con eje en el norte (−90°); cada sector centrado en −90° + i·30°. */
function circleSliceAngles(i) {
  const mid = (-Math.PI / 2) + (i * CIRCLE_SLICE_RAD);
  const half = CIRCLE_SLICE_RAD / 2;
  return { mid, a0: mid - half, a1: mid + half };
}

function circleSliceIndexFromCanvas(cx, cy, x, y) {
  const dx = x - cx;
  const dy = y - cy;
  const a = Math.atan2(dy, dx);
  const t = (a + Math.PI / 2 + Math.PI * 2) % (Math.PI * 2);
  return Math.floor((t + CIRCLE_SLICE_RAD / 2) / CIRCLE_SLICE_RAD) % 12;
}

function pitchClassFromCircleClick(cx, cy, x, y) {
  const idx = circleSliceIndexFromCanvas(cx, cy, x, y);
  return CIRCLE_FIFTHS_ORDER[idx];
}

/**
 * Clic: fija tónica/tonalidad según anillo (mayor exterior / menor relativa interior).
 * Mayús+clic: raíz del acorde diatónico en la misma regla de anillo.
 */
function circleChordRootPcFromClick(canvasW, canvasH, cx, cy, x, y, shiftKey) {
  const dx = x - cx;
  const dy = y - cy;
  const dist = Math.sqrt((dx * dx) + (dy * dy));
  const { rOuter, rHole, rGuideMajMin } = circleFifthsRadiiPx(canvasW, canvasH);
  if (dist < rHole * 1.02 || dist > rOuter * 1.02) return null;
  const idx = circleSliceIndexFromCanvas(cx, cy, x, y);
  const majorPc = CIRCLE_FIFTHS_ORDER[idx];
  if (!shiftKey) {
    if (dist < rGuideMajMin) {
      return ((majorPc + 9) % 12 + 12) % 12;
    }
    return ((majorPc % 12) + 12) % 12;
  }
  if (dist < rGuideMajMin) {
    return ((majorPc + 9) % 12 + 12) % 12;
  }
  return ((majorPc % 12) + 12) % 12;
}

/**
 * Mayús+clic: solo triadas diatónicas según banda y sector (mayor: I–IV–V / ii–iii–vi–vii°; menor natural: grados relativos).
 */
function circleChordShiftClickIsDiatonic(tonicPc, canvasW, canvasH, cx, cy, x, y) {
  const dx = x - cx;
  const dy = y - cy;
  const dist = Math.sqrt((dx * dx) + (dy * dy));
  const { rOuter, rHole, rGuideMajMin } = circleFifthsRadiiPx(canvasW, canvasH);
  if (dist < rHole * 1.02 || dist > rOuter * 1.02) return false;
  const idx = circleSliceIndexFromCanvas(cx, cy, x, y);
  const majorPc = CIRCLE_FIFTHS_ORDER[idx];
  const innerMinorBand = dist < rGuideMajMin;
  if (state.circleKeyMode === "minor") {
    const minorTonic = ((state.circleTonicPc % 12) + 12) % 12;
    if (!innerMinorBand) {
      const dU = (majorPc - minorTonic + 12) % 12;
      return [3, 8, 10].includes(dU);
    }
    const rootMinor = (majorPc + 9 + 12) % 12;
    return diatonicTriadSuffixNaturalMinorKey(minorTonic, rootMinor).interval != null;
  }
  const viiRootPc = chordRootPcForMajorScaleDegree(tonicPc, 11);
  const viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
  if (!innerMinorBand) {
    const { degree } = diatonicTriadSuffixMajorKey(tonicPc, majorPc);
    return degree != null && circleUpperBandIsDiatonicMajorTriad(degree);
  }
  const rootMinor = (majorPc + 9 + 12) % 12;
  const { degree: minorDeg } = diatonicTriadSuffixMajorKey(tonicPc, rootMinor);
  if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) return true;
  if (minorDeg === 11 && majorPc === viiLabelSlicePc) return true;
  return false;
}

/** Tónica de la tonalidad mayor usada en análisis diatónico (numeración, colores, API). Si el usuario eligió modo menor, es la relativa mayor. */
function circleMajorTonicPcForTheory() {
  const t = ((state.circleTonicPc % 12) + 12) % 12;
  if (state.circleKeyMode === "minor") {
    return (t + 3 + 12) % 12;
  }
  return t;
}

/** null = fuera del anillo; true = banda menor; false = banda mayor. */
function circleFifthsClickInnerMinorBand(canvasW, canvasH, cx, cy, x, y) {
  const dx = x - cx;
  const dy = y - cy;
  const dist = Math.sqrt((dx * dx) + (dy * dy));
  const { rOuter, rHole, rGuideMajMin } = circleFifthsRadiiPx(canvasW, canvasH);
  if (dist < rHole * 1.02 || dist > rOuter * 1.02) return null;
  return dist < rGuideMajMin;
}

function scheduleCircleFifthsLayout() {
  if (state.circleFifthsResizeScheduled) return;
  state.circleFifthsResizeScheduled = true;
  requestAnimationFrame(() => {
    state.circleFifthsResizeScheduled = false;
    if (state.mode === "circle_fifths") renderCircleFifths();
  });
}

function renderCircleFifths() {
  const canvas = el("circleFifthsCanvas");
  if (!canvas || state.mode !== "circle_fifths") return;
  const ctx = canvas.getContext("2d");
  const wrap = canvas.parentElement;
  const box = Math.min(520, Math.max(260, wrap?.clientWidth || canvas.clientWidth || 300));
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const size = Math.floor(box * dpr);
  if (canvas.width !== size || canvas.height !== size) {
    canvas.width = size;
    canvas.height = size;
  }
  canvas.style.width = `${box}px`;
  canvas.style.height = `${box}px`;
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const {
    rOuter, rHole, rSigInner, rSig, rMajName, rMajRoman, rMin, rMinRoman, rGuideSigMaj, rGuideMajMin,
  } = circleFifthsRadiiPx(w, h);
  const tonic = circleMajorTonicPcForTheory();
  const chordRoot = ((state.circleChordRootPc % 12) + 12) % 12;
  const viiRootPc = chordRootPcForMajorScaleDegree(tonic, 11);
  const viiLabelSlicePc = (viiRootPc + 3 + 12) % 12;
  const minorMode = state.circleKeyMode === "minor";
  const minorTonic = minorMode ? ((state.circleTonicPc % 12) + 12) % 12 : null;
  const relMajFromMinor = minorMode ? (minorTonic + 3 + 12) % 12 : null;
  const iiDimRootMinor = minorMode ? (minorTonic + 2 + 12) % 12 : null;
  const iiLabelPcMinor = minorMode ? (iiDimRootMinor + 3 + 12) % 12 : null;
  const fsSig = Math.max(10, Math.min(24, Math.round(0.026 * w)));
  const fsMaj = Math.max(14, Math.min(32, Math.round(0.036 * w)));
  const fsMajR = Math.max(12, Math.min(28, Math.round(0.03 * w)));
  const fsMin = Math.max(13, Math.min(30, Math.round(0.034 * w)));
  const fsMinR = Math.max(11, Math.min(26, Math.round(0.028 * w)));
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = "#1a2330";
  ctx.fillRect(0, 0, w, h);
  ctx.translate(cx, cy);
  const sigRingFill = "#ffffff";
  const sigRingStroke = "rgba(200, 205, 215, 0.65)";
  for (let i = 0; i < 12; i += 1) {
    const pc = CIRCLE_FIFTHS_ORDER[i];
    const { a0, a1 } = circleSliceAngles(i);
    const mpcRel = relativeMinorPcFromMajorPc(pc);
    const grayFill = "#3d4658";
    let upperFill = grayFill;
    let lowerFill = grayFill;
    if (minorMode) {
      const dU = (pc - minorTonic + 12) % 12;
      if ([3, 8, 10].includes(dU)) {
        const mk = circleMinorIntervalToMajorDegreeKey(dU);
        upperFill = circleDiatonicSliceFill(mk, pc, relMajFromMinor);
      }
      const dL = (mpcRel - minorTonic + 12) % 12;
      if ([0, 5, 7].includes(dL)) {
        const mk = circleMinorIntervalToMajorDegreeKey(dL);
        lowerFill = dL === 0
          ? circleDiatonicSliceFill(0, pc, relMajFromMinor)
          : circleDiatonicSliceFill(mk, mpcRel, tonic);
      } else if (pc === iiLabelPcMinor) {
        lowerFill = circleDiatonicSliceFill(11, iiDimRootMinor, tonic);
      }
    } else {
      const { degree } = diatonicTriadSuffixMajorKey(tonic, pc);
      const minorDeg = diatonicTriadSuffixMajorKey(tonic, mpcRel).degree;
      const diatonic = degree != null;
      if (diatonic && circleUpperBandIsDiatonicMajorTriad(degree)) {
        upperFill = circleDiatonicSliceFill(degree, pc, tonic);
      }
      if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
        lowerFill = circleDiatonicSliceFill(minorDeg, mpcRel, tonic);
      } else if (diatonic && pc === viiLabelSlicePc) {
        lowerFill = circleDiatonicSliceFill(11, viiRootPc, tonic);
      }
    }
    ctx.beginPath();
    ctx.arc(0, 0, rOuter, a0, a1);
    ctx.arc(0, 0, rSigInner, a1, a0, true);
    ctx.closePath();
    ctx.fillStyle = sigRingFill;
    ctx.fill();
    ctx.strokeStyle = sigRingStroke;
    ctx.lineWidth = Math.max(1, 1.05 * dpr);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, rSigInner, a0, a1);
    ctx.arc(0, 0, rGuideMajMin, a1, a0, true);
    ctx.closePath();
    ctx.fillStyle = upperFill;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, rGuideMajMin, a0, a1);
    ctx.arc(0, 0, rHole, a1, a0, true);
    ctx.closePath();
    ctx.fillStyle = lowerFill;
    ctx.fill();
  }
  ctx.strokeStyle = "rgba(226, 232, 242, 0.28)";
  ctx.lineWidth = Math.max(1, 1.15 * dpr);
  [rGuideSigMaj, rGuideMajMin].forEach((rg) => {
    ctx.beginPath();
    ctx.arc(0, 0, rg, 0, Math.PI * 2);
    ctx.stroke();
  });
  ctx.strokeStyle = "rgba(226, 232, 242, 0.4)";
  ctx.lineWidth = Math.max(1, 1.05 * dpr);
  ctx.beginPath();
  ctx.arc(0, 0, rHole, 0, Math.PI * 2);
  ctx.stroke();
  /** Radios blancos en los límites entre los 12 sectores (separan acordes). */
  ctx.strokeStyle = "rgba(255, 255, 255, 0.9)";
  ctx.lineWidth = Math.max(1.2, 1.35 * dpr);
  ctx.lineCap = "round";
  for (let ri = 0; ri < 12; ri += 1) {
    const { a1 } = circleSliceAngles(ri);
    const ca = Math.cos(a1);
    const sa = Math.sin(a1);
    ctx.beginPath();
    ctx.moveTo(rHole * ca, rHole * sa);
    ctx.lineTo(rOuter * ca, rOuter * sa);
    ctx.stroke();
  }
  strokeCircleDiatonicEnvelope(ctx, tonic, rSigInner, rGuideMajMin, rHole, dpr);
  const hl = circleChordHighlightGeom(tonic, chordRoot, state.generatedChord);
  const { a0: ha0, a1: ha1 } = circleSliceAngles(hl.sliceIdx);
  const selInset = Math.max(2.5, 3.2 * dpr);
  let rHiOut = rSigInner - selInset;
  let rHiIn = rGuideMajMin + selInset;
  if (hl.band === "minor") {
    rHiOut = rGuideMajMin - selInset;
    rHiIn = rHole + selInset;
  }
  strokeCircleChordSelectionBand(ctx, rHiOut, rHiIn, ha0, ha1, dpr);
  for (let i = 0; i < 12; i += 1) {
    const pc = CIRCLE_FIFTHS_ORDER[i];
    const { mid } = circleSliceAngles(i);
    const mpcRel = relativeMinorPcFromMajorPc(pc);
    const cos = Math.cos(mid);
    const sin = Math.sin(mid);
    const sigLabel = circleSignatureLabelForSliceIndex(i);
    const majorName = noteNameFromPc(pc);
    const minorName = circleMinorLabel(pc);
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#0d0d0d";
    ctx.font = `bold ${fsSig}px "Avenir Next", "Segoe UI", sans-serif`;
    ctx.fillText(sigLabel, cos * rSig, sin * rSig);
    if (minorMode) {
      const dU = (pc - minorTonic + 12) % 12;
      const dL = (mpcRel - minorTonic + 12) % 12;
      const hasUpperDiat = [3, 8, 10].includes(dU);
      const hasLowerDiat = [0, 5, 7].includes(dL);
      const isIiDimSector = pc === iiLabelPcMinor;
      if (hasUpperDiat) {
        const mk = circleMinorIntervalToMajorDegreeKey(dU);
        ctx.fillStyle = CIRCLE_DEGREE_TEXT[mk];
        ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillText(majorName, cos * rMajName, sin * rMajName);
        fillTextRomanMaybeFlatSuperscript(
          ctx,
          ROMAN_BY_MINOR_NATURAL_INTERVAL[dU] || "",
          cos * rMajRoman,
          sin * rMajRoman,
          fsMajR,
        );
      } else {
        ctx.fillStyle = "#a8b0bd";
        ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillText(majorName, cos * rMajName, sin * rMajName);
      }
      if (isIiDimSector) {
        const rSimVii = rOuter * 0.405;
        const dimChordLabel = `${noteNameFromPc(iiDimRootMinor)}°`;
        ctx.fillStyle = CIRCLE_DEGREE_TEXT[11];
        ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillText(dimChordLabel, cos * rSimVii, sin * rSimVii);
        fillTextRomanMaybeFlatSuperscript(
          ctx,
          ROMAN_BY_MINOR_NATURAL_INTERVAL[2] || "",
          cos * rMinRoman,
          sin * rMinRoman,
          fsMinR,
        );
      } else if (hasLowerDiat) {
        const mk = circleMinorIntervalToMajorDegreeKey(dL);
        ctx.fillStyle = CIRCLE_DEGREE_TEXT[mk];
        ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillText(minorName, cos * rMin, sin * rMin);
        fillTextRomanMaybeFlatSuperscript(
          ctx,
          ROMAN_BY_MINOR_NATURAL_INTERVAL[dL] || "",
          cos * rMinRoman,
          sin * rMinRoman,
          fsMinR,
        );
      } else {
        ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillStyle = "#8b95a3";
        ctx.fillText(minorName, cos * rMin, sin * rMin);
      }
    } else {
      const { degree } = diatonicTriadSuffixMajorKey(tonic, pc);
      const diatonic = degree != null;
      const minorDeg = diatonicTriadSuffixMajorKey(tonic, mpcRel).degree;
      if (diatonic) {
        if (circleUpperBandIsDiatonicMajorTriad(degree)) {
          ctx.fillStyle = CIRCLE_DEGREE_TEXT[degree];
          ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(majorName, cos * rMajName, sin * rMajName);
          ctx.font = `${fsMajR}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(ROMAN_BY_DEGREE[degree] || "", cos * rMajRoman, sin * rMajRoman);
        } else if (degree === 11) {
          ctx.fillStyle = "#a8b0bd";
          ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(majorName, cos * rMajName, sin * rMajName);
          /* vii° va en el anillo inferior junto a Sim, no bajo el nombre mayor Si. */
        } else {
          ctx.fillStyle = "#a8b0bd";
          ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(majorName, cos * rMajName, sin * rMajName);
        }
        if (minorDeg === 11) {
          const simLabel = `${noteNameFromPc(viiRootPc)}m`;
          const rSimVii = rOuter * 0.405;
          ctx.fillStyle = CIRCLE_DEGREE_TEXT[11];
          ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(simLabel, cos * rSimVii, sin * rSimVii);
          ctx.font = `${fsMinR}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(ROMAN_BY_DEGREE[11] || "", cos * rMinRoman, sin * rMinRoman);
        } else if (minorDeg != null && circleLowerBandIsDiatonicMinorTriad(minorDeg)) {
          ctx.fillStyle = CIRCLE_DEGREE_TEXT[minorDeg];
          ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(minorName, cos * rMin, sin * rMin);
          ctx.font = `${fsMinR}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillText(ROMAN_BY_DEGREE[minorDeg] || "", cos * rMinRoman, sin * rMinRoman);
        } else {
          ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
          ctx.fillStyle = "#8b95a3";
          ctx.fillText(minorName, cos * rMin, sin * rMin);
        }
      } else {
        ctx.fillStyle = "#a8b0bd";
        ctx.font = `bold ${fsMaj}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillText(majorName, cos * rMajName, sin * rMajName);
        ctx.font = `bold ${fsMin}px "Avenir Next", "Segoe UI", sans-serif`;
        ctx.fillStyle = "#8b95a3";
        ctx.fillText(minorName, cos * rMin, sin * rMin);
      }
    }
  }
  ctx.setTransform(1, 0, 0, 1, 0, 0);
}

function bindCircleFifthsCanvas() {
  const canvas = el("circleFifthsCanvas");
  if (!canvas || canvas.dataset.circleBound === "1") return;
  canvas.dataset.circleBound = "1";
  canvas.addEventListener("click", async (event) => {
    if (state.mode !== "circle_fifths") return;
    const rect = canvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((event.clientY - rect.top) / rect.height) * canvas.height;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const pc = circleChordRootPcFromClick(canvas.width, canvas.height, cx, cy, x, y, event.shiftKey);
    if (pc == null) return;
    if (event.shiftKey) {
      if (!circleChordShiftClickIsDiatonic(circleMajorTonicPcForTheory(), canvas.width, canvas.height, cx, cy, x, y)) return;
      state.circleChordRootPc = pc;
    } else {
      const band = circleFifthsClickInnerMinorBand(canvas.width, canvas.height, cx, cy, x, y);
      state.circleKeyMode = band ? "minor" : "major";
      state.circleTonicPc = pc;
      state.circleChordRootPc = pc;
    }
    try {
      await runGenerateChordCircle(true);
    } catch (_err) {}
  });
  const wrap = canvas.parentElement;
  if (wrap && typeof ResizeObserver !== "undefined") {
    const ro = new ResizeObserver(() => scheduleCircleFifthsLayout());
    ro.observe(wrap);
  }
}

/** @param {boolean} [playChordAfter] — si es true, reproduce el acorde (solo tras clic en el círculo). */
async function runGenerateChordCircle(playChordAfter = false) {
  const rootPc = ((state.circleChordRootPc % 12) + 12) % 12;
  const tonicPc = circleMajorTonicPcForTheory();
  let suffix;
  if (state.circleKeyMode === "minor") {
    const mt = ((state.circleTonicPc % 12) + 12) % 12;
    suffix = diatonicTriadSuffixNaturalMinorKey(mt, rootPc).suffix || "";
  } else {
    suffix = diatonicTriadSuffixMajorKey(tonicPc, rootPc).suffix || "";
  }
  const payload = {
    root_pc: rootPc,
    suffix,
    inversion: 0,
    language: state.language,
    accidental: currentAccidentalValue(),
  };
  const out = await fetchJson("/api/generate/chord", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.generatedChord = out;
  const nameEl = el("circleChordName");
  if (nameEl) nameEl.textContent = out.name || "-";
  await loadGuitarVariations();
  if (state.mode === "circle_fifths") {
    renderInstrument();
    renderStaff();
    renderCircleFifths();
    if (playChordAfter) {
      const notes = getGenerationBaseNotes();
      if (notes.length) {
        playChordMidi(notes, { instrument: state.instrument === "guitar" ? "guitar" : "piano" });
      }
    }
  }
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

function refreshMetronomeVolumeInfo() {
  const mainSlider = el("metroVolume");
  const scaleSlider = el("scaleMetroVolume");
  const active = document.activeElement;
  const preferredValue = active === scaleSlider
    ? Number(scaleSlider?.value)
    : (active === mainSlider ? Number(mainSlider?.value) : Number(mainSlider?.value) || Number(scaleSlider?.value));
  const vol = Math.max(
    0,
    Math.min(
      100,
      preferredValue || Number(state.metronomeVolume) || 100,
    ),
  );
  state.metronomeVolume = vol;
  if (mainSlider && Number(mainSlider.value) !== vol) mainSlider.value = String(vol);
  if (scaleSlider && Number(scaleSlider.value) !== vol) scaleSlider.value = String(vol);
  const text = `${Math.round(vol)}%`;
  const node = el("metroVolumeValue");
  if (node) node.textContent = text;
  const scaleNode = el("scaleMetroVolumeValue");
  if (scaleNode) scaleNode.textContent = text;
}

function metronomeVolumeGain() {
  const vol = Math.max(0, Math.min(100, Number(state.metronomeVolume) || 100));
  return (vol / 100) * 3;
}

function tr(key) {
  const lang = UI_TEXTS[state.language] || UI_TEXTS.es;
  return lang[key] || UI_TEXTS.es[key] || key;
}

const SEO_META = {
  es: {
    title: "MIDI Piano & Guitar Chords — Acordes, escalas, metrónomo y MIDI gratis",
    description:
      "Herramienta online gratuita: detecta y genera acordes en piano y guitarra, círculo de quintas interactivo, escalas, metrónomo y afinador. Usa teclado MIDI o ratón. Sin instalación en el navegador.",
  },
  en: {
    title: "MIDI Piano & Guitar Chords — Chords, scales, metronome & free MIDI tool",
    description:
      "Free online tool: detect and generate piano and guitar chords, interactive circle of fifths, scales, metronome and tuner. Use a MIDI keyboard or mouse. Runs in your browser, no install.",
  },
};

function setMetaContent(selector, content) {
  const node = document.querySelector(selector);
  if (node) node.setAttribute("content", content);
}

function applySeoMeta() {
  const m = SEO_META[state.language] || SEO_META.es;
  document.title = m.title;
  document.documentElement.lang = state.language;
  setMetaContent('meta[name="description"]', m.description);
  setMetaContent('meta[property="og:title"]', m.title);
  setMetaContent('meta[property="og:description"]', m.description);
  setMetaContent('meta[name="twitter:title"]', m.title);
  setMetaContent('meta[name="twitter:description"]', m.description);
  const ogLoc = document.querySelector('meta[property="og:locale"]');
  if (ogLoc) ogLoc.setAttribute("content", state.language === "es" ? "es_ES" : "en_US");
}

function midiButtonTooltipForState(status = null) {
  const current = status || (state.midi.enabled ? "on" : "off");
  if (current === "secure_required") return tr("midi_requires_secure");
  if (current === "unsupported") return tr("midi_try_chrome");
  if (current === "denied") return tr("midi_help_denied");
  return tr("midi_help_ready");
}

function refreshMidiInputSoundToggleButton() {
  const label = state.midiInputSoundEnabled ? tr("midi_input_sound_on") : tr("midi_input_sound_off");
  ["detectMidiSoundToggle", "intervalMidiSoundToggle", "metroMidiSoundToggle"].forEach((id) => {
    const btn = el(id);
    if (!btn) return;
    btn.textContent = label;
    btn.classList.toggle("active", !!state.midiInputSoundEnabled);
  });
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

function showFeedbackModal() {
  const modal = el("feedbackModal");
  if (!modal) return;
  modal.classList.remove("hidden");
}

function hideFeedbackModal() {
  const modal = el("feedbackModal");
  if (!modal) return;
  modal.classList.add("hidden");
}

function showDownloadsModal() {
  const modal = el("downloadsModal");
  if (!modal) return;
  modal.classList.remove("hidden");
}

function hideDownloadsModal() {
  const modal = el("downloadsModal");
  if (!modal) return;
  modal.classList.add("hidden");
}

function refreshHelpButtonState() {
  const helpBtn = el("helpToggle");
  if (!helpBtn) return;
  const available = isHelpAvailableForMode(state.mode);
  helpBtn.disabled = !available;
  helpBtn.classList.toggle("active", !!state.help.active);
  helpBtn.classList.toggle("help-blink", !!state.help.active);
  helpBtn.textContent = tr("help_button");
  helpBtn.setAttribute("title", tr("help_button"));
}

function placeHelpCallout(node, targetRect, side) {
  const margin = 12;
  const gap = 10;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const width = node.offsetWidth;
  const height = node.offsetHeight;
  let x = targetRect.left;
  let y = targetRect.top;
  if (side === "top") {
    x = targetRect.left + (targetRect.width - width) / 2;
    y = targetRect.top - height - gap;
  } else if (side === "bottom") {
    x = targetRect.left + (targetRect.width - width) / 2;
    y = targetRect.bottom + gap;
  } else if (side === "left") {
    x = targetRect.left - width - gap;
    y = targetRect.top + (targetRect.height - height) / 2;
  } else {
    x = targetRect.right + gap;
    y = targetRect.top + (targetRect.height - height) / 2;
  }
  x = Math.max(margin, Math.min(vw - width - margin, x));
  y = Math.max(margin, Math.min(vh - height - margin, y));
  node.style.left = `${Math.round(x)}px`;
  node.style.top = `${Math.round(y)}px`;
}

function ensureHelpOverlayChildren() {
  const overlay = el("helpOverlay");
  if (!overlay) return null;
  let highlight = overlay.querySelector(".help-highlight");
  if (!highlight) {
    highlight = document.createElement("div");
    highlight.className = "help-highlight hidden";
    overlay.appendChild(highlight);
  }
  let callout = overlay.querySelector(".help-callout");
  if (!callout) {
    callout = document.createElement("div");
    callout.className = "help-callout hidden";
    overlay.appendChild(callout);
  }
  let closeTip = overlay.querySelector(".help-close-tip");
  if (!closeTip) {
    closeTip = document.createElement("div");
    closeTip.className = "help-close-tip";
    overlay.appendChild(closeTip);
  }
  closeTip.textContent = tr("help_close_hint");
  return { overlay, highlight, callout, closeTip };
}

function removeMetronomeHelpHotspots() {
  document.querySelectorAll(".help-metro-hotspot").forEach((node) => node.remove());
}

function syncMetronomeHelpHotspots() {
  removeMetronomeHelpHotspots();
  if (!(state.help.active && state.mode === "metronome")) return;
  const canvas = el("staffCanvas");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const cw = Math.max(1, Number(canvas.width) || 1);
  const ch = Math.max(1, Number(canvas.height) || 1);
  const sx = rect.width / cw;
  const sy = rect.height / ch;
  const regions = state.staff.metronomeRegions || {};
  const defs = [
    ["helpMetroYellowPoints", regions.yellowPoints],
    ["helpMetroScaleAxis", regions.scaleAxis],
    ["helpMetroRedBall", regions.redBall],
  ];
  defs.forEach(([id, r]) => {
    if (!r || !Number.isFinite(r.x) || !Number.isFinite(r.y) || !Number.isFinite(r.w) || !Number.isFinite(r.h) || r.w <= 0 || r.h <= 0) return;
    const node = document.createElement("div");
    node.id = String(id);
    node.className = "help-metro-hotspot";
    node.style.left = `${Math.round(rect.left + (Number(r.x) * sx))}px`;
    node.style.top = `${Math.round(rect.top + (Number(r.y) * sy))}px`;
    node.style.width = `${Math.round(Number(r.w) * sx)}px`;
    node.style.height = `${Math.round(Number(r.h) * sy)}px`;
    document.body.appendChild(node);
  });
}

function positionHelpCloseTip(closeTip) {
  const helpBtn = el("helpToggle");
  if (!closeTip || !helpBtn) return;
  const rect = helpBtn.getBoundingClientRect();
  const gap = 8;
  closeTip.style.left = `${Math.round(rect.right)}px`;
  closeTip.style.top = `${Math.round(rect.bottom + gap)}px`;
  closeTip.style.bottom = "auto";
  closeTip.style.transform = "translateX(-100%)";
}

function clearHelpFocus() {
  const ui = ensureHelpOverlayChildren();
  if (!ui) return;
  ui.highlight.classList.add("hidden");
  ui.callout.classList.add("hidden");
  if (state.help.activeTarget) {
    state.help.activeTarget.classList.remove("help-target-active");
  }
  state.help.activeTarget = null;
  state.help.activeItem = null;
}

function showHelpForTarget(target, item) {
  const ui = ensureHelpOverlayChildren();
  if (!ui) return;
  const rect = target.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) {
    clearHelpFocus();
    return;
  }
  if (state.help.activeTarget && state.help.activeTarget !== target) {
    state.help.activeTarget.classList.remove("help-target-active");
  }
  state.help.activeTarget = target;
  state.help.activeItem = item;
  target.classList.add("help-target-active");

  const pad = 4;
  ui.highlight.classList.remove("hidden");
  ui.highlight.style.left = `${Math.round(rect.left - pad)}px`;
  ui.highlight.style.top = `${Math.round(rect.top - pad)}px`;
  ui.highlight.style.width = `${Math.round(rect.width + (pad * 2))}px`;
  ui.highlight.style.height = `${Math.round(rect.height + (pad * 2))}px`;

  ui.callout.className = `help-callout help-${item.side || "top"}`;
  ui.callout.textContent = tr(item.textKey);
  ui.callout.classList.remove("hidden");
  placeHelpCallout(ui.callout, rect, item.side || "top");
}

function clearHelpBindings() {
  state.help.bindings.forEach(({ target, onEnter, onLeave }) => {
    target.removeEventListener("mouseenter", onEnter);
    target.removeEventListener("focus", onEnter);
    target.removeEventListener("mouseleave", onLeave);
    target.removeEventListener("blur", onLeave);
    target.classList.remove("help-target", "help-target-active");
  });
  state.help.bindings = [];
}

function findHelpBindingForTarget(target) {
  if (!target) return null;
  return state.help.bindings.find((b) => b.target === target) || null;
}

function enableHelpMode() {
  const ui = ensureHelpOverlayChildren();
  if (!ui) return;
  ui.overlay.classList.remove("hidden");
  document.body.classList.add("help-active");
  clearHelpBindings();
  helpCalloutsForMode(state.mode).forEach((item) => {
    const target = document.querySelector(item.selector);
    if (!target) return;
    const onEnter = () => showHelpForTarget(target, item);
    const onLeave = (ev) => {
      const next = ev && ev.relatedTarget instanceof Element
        ? ev.relatedTarget.closest(".help-target")
        : null;
      if (next && next !== target) {
        const binding = findHelpBindingForTarget(next);
        if (binding) {
          showHelpForTarget(binding.target, binding.item);
          return;
        }
      }
      if (state.help.activeTarget === target) clearHelpFocus();
    };
    target.classList.add("help-target");
    target.addEventListener("mouseenter", onEnter);
    target.addEventListener("focus", onEnter);
    target.addEventListener("mouseleave", onLeave);
    target.addEventListener("blur", onLeave);
    state.help.bindings.push({ target, item, onEnter, onLeave });
  });
}

function disableHelpMode() {
  const ui = ensureHelpOverlayChildren();
  clearHelpBindings();
  clearHelpFocus();
  removeMetronomeHelpHotspots();
  document.body.classList.remove("help-active");
  if (ui) {
    ui.closeTip.classList.add("hidden");
    ui.overlay.classList.add("hidden");
  }
}

function refreshHelpOverlay() {
  if (!state.help.active) {
    disableHelpMode();
    return;
  }
  syncMetronomeHelpHotspots();
  enableHelpMode();
  const ui = ensureHelpOverlayChildren();
  if (ui) {
    ui.closeTip.classList.remove("hidden");
    positionHelpCloseTip(ui.closeTip);
  }
  if (state.help.activeTarget && state.help.activeItem) {
    showHelpForTarget(state.help.activeTarget, state.help.activeItem);
  }
}

function setHelpActive(active) {
  state.help.active = !!active && isHelpAvailableForMode(state.mode);
  refreshHelpButtonState();
  refreshHelpOverlay();
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
    opt("interval_detection", "mode_interval_detection");
    opt("generation", "mode_generation");
    opt("circle_fifths", "mode_circle_fifths");
    opt("scales", "mode_scales");
    opt("metronome", "mode_metronome");
    opt("tuner", "mode_tuner");
    const tunerOption = modeSelect.querySelector('option[value="tuner"]');
    if (tunerOption) tunerOption.hidden = !TUNER_FEATURE_ENABLED;
  }

  const setText = (id, key) => {
    const node = el(id);
    if (node) node.textContent = tr(key);
  };
  setText("staffHeader", "staff");
  setText("headingDetection", "heading_detection");
  setText("headingIntervalDetection", "heading_interval_detection");
  setText("intervalDetectionHint", "hint_interval_detection");
  setText("intervalClear", "clear");
  setText("labelIntervalNotes", "label_interval_notes");
  setText("labelIntervalName", "label_interval_name");
  setText("labelIntervalSemitones", "label_interval_semitones");
  setText("labelIntervalRecuerda", "label_interval_recuerda");
  setText("headingGeneration", "heading_generation");
  setText("headingScales", "heading_scales");
  setText("headingMetronome", "heading_metronome_settings");
  setText("headingTuner", "heading_tuner_settings");
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
  setText("labelCircleChord", "label_chord");
  setText("labelScaleRoot", "label_tonic");
  setText("labelScaleType", "label_type");
  setText("labelScaleMetronomeVolume", "label_metronome_volume");
  setText("labelScaleBpm", "label_speed");
  setText("labelScaleName", "label_scale");
  setText("labelScaleNotes", "label_notes");
  setText("labelScaleIntervals", "label_intervals");
  setText("labelMetronomeBpm", "label_metronome_tempo");
  setText("labelMetronomeVolume", "label_metronome_volume");
  setText("labelMetronomeBeats", "label_beats");
  setText("labelMetronomeSubdivision", "label_subdivision");
  setText("labelMetronomeBarAccent", "label_bar_accent");
  setText("labelMetronomeTimerEnabled", "label_timer_enabled");
  setText("labelMetronomeTimer", "label_timer");
  setText("labelTunerNote", "label_note");
  setText("labelTunerCents", "label_cents");
  setText("labelTunerFreq", "label_freq");
  setText("labelTunerTuning", "label_tuner_tuning");
  setText("labelTunerInput", "label_tuner_input");
  setText("labelTunerGain", "label_tuner_gain");
  setText("labelTunerSpectrumRange", "label_tuner_spectrum_range");
  setText("instPianoBtn", "inst_piano");
  setText("instGuitarBtn", "inst_guitar");
  setText("donationTitle", "donation_title");
  setText("donationText", "donation_text");
  setText("donateBtn", "donation_button");
  setText("feedbackPanelTitle", "feedback_panel_title");
  setText("feedbackPanelText", "feedback_panel_text");
  setText("feedbackOpenBtn", "feedback_open");
  setText("feedbackModalTitle", "feedback_modal_title");
  setText("feedbackHelp", "feedback_help");
  setText("feedbackNameLabel", "feedback_name");
  setText("feedbackEmailLabel", "feedback_email");
  setText("feedbackMessageLabel", "feedback_message");
  setText("feedbackSubmit", "feedback_send");
  setText("feedbackCloseBtn", "close");
  setText("downloadsPanelTitle", "downloads_panel_title");
  setText("downloadsPanelText", "downloads_panel_text");
  setText("downloadsOpenBtn", "downloads_open");
  setText("downloadsModalTitle", "downloads_modal_title");
  setText("downloadsModalIntro", "downloads_modal_intro");
  setText("downloadsPcTitle", "downloads_pc_title");
  setText("downloadsMobileTitle", "downloads_mobile_title");
  setText("downloadWindowsLink", "downloads_windows_store");
  setText("downloadMacosLink", "downloads_macos_dmg");
  setText("downloadLinuxDebLink", "downloads_linux_deb");
  setText("downloadIosLink", "downloads_ios_appstore");
  setText("downloadAndroidLink", "downloads_android_googleplay");
  setText("downloadsCloseBtn", "close");
  setText("helpToggle", "help_button");
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
  const intervalPlay = el("intervalPlay");
  const intervalPlayReverse = el("intervalPlayReverse");
  const genPlay = el("genPlay");
  const scaleModeMetronome = el("scaleModeMetronome");
  if (detectPlay) {
    detectPlay.setAttribute("aria-label", tr("play"));
    detectPlay.setAttribute("title", tr("play"));
  }
  if (intervalPlay) {
    intervalPlay.setAttribute("aria-label", tr("play"));
    intervalPlay.setAttribute("title", tr("play"));
  }
  if (intervalPlayReverse) {
    intervalPlayReverse.setAttribute("aria-label", tr("interval_play_reverse"));
    intervalPlayReverse.setAttribute("title", tr("interval_play_reverse"));
  }
  if (genPlay) {
    genPlay.setAttribute("aria-label", tr("play"));
    genPlay.setAttribute("title", tr("play"));
  }
  const circlePlay = el("circlePlay");
  if (circlePlay) {
    circlePlay.setAttribute("aria-label", tr("play"));
    circlePlay.setAttribute("title", tr("play"));
  }
  if (scaleModeMetronome) {
    scaleModeMetronome.setAttribute("aria-label", tr("metronome_mode"));
    scaleModeMetronome.setAttribute("title", tr("metronome_mode"));
  }
  const midiBtn = el("midiToggle");
  if (midiBtn) midiBtn.textContent = state.midi.enabled ? tr("midi_on") : tr("midi_off");
  if (midiBtn) midiBtn.setAttribute("title", midiButtonTooltipForState());
  refreshMidiToggleButtonState();
  refreshHelpButtonState();
  refreshMidiInputSoundToggleButton();
  if (el("scaleBpm") && el("scaleBpmValue")) {
    el("scaleBpmValue").textContent = `${el("scaleBpm").value} ${tempoUnitLabel()}`;
  }
  refreshMetronomeTempoInfo();
  refreshMetronomeVolumeInfo();
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
  if (TUNER_FEATURE_ENABLED) {
    void refreshTunerInputs();
  }
  syncLeftPanelHeader();
  const circleHint = el("circleFifthsHint");
  if (circleHint) circleHint.textContent = tr("circle_hint");
  if (state.mode === "circle_fifths") scheduleCircleFifthsLayout();
  if (state.help.active) refreshHelpOverlay();
}

async function submitFeedbackForm(event) {
  event.preventDefault();
  const form = el("feedbackForm");
  const submitBtn = el("feedbackSubmit");
  const status = el("feedbackStatus");
  if (!form || !submitBtn || !status) return;

  const name = String(el("feedbackName")?.value || "").trim();
  const email = String(el("feedbackEmail")?.value || "").trim();
  const message = String(el("feedbackMessage")?.value || "").trim();
  if (!name || !email || !message) {
    status.textContent = tr("feedback_error");
    return;
  }

  submitBtn.disabled = true;
  status.textContent = tr("feedback_sending");
  try {
    const out = await fetchJson("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        email,
        message,
        mode: state.mode || "web",
        language: state.language,
        page_url: window.location.href,
      }),
    });
    if (!out?.sent) {
      throw new Error(out?.reason || "feedback_not_sent");
    }
    form.reset();
    status.textContent = tr("feedback_ok");
  } catch (_err) {
    status.textContent = tr("feedback_error");
  } finally {
    submitBtn.disabled = false;
  }
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function activeModeSupportsInstrument() {
  return state.mode === "detection" || state.mode === "interval_detection" || state.mode === "generation" || state.mode === "circle_fifths" || state.mode === "scales" || state.mode === "metronome";
}

function activeModeSupportsStaff() {
  return state.mode === "detection"
    || state.mode === "interval_detection"
    || state.mode === "generation"
    || state.mode === "circle_fifths"
    || state.mode === "scales"
    || state.mode === "metronome"
    || (TUNER_FEATURE_ENABLED && state.mode === "tuner");
}

function syncLeftPanelHeader() {
  const header = el("staffHeader");
  if (!header) return;
  if (state.mode === "metronome") header.textContent = tr("mode_metronome");
  else if (TUNER_FEATURE_ENABLED && state.mode === "tuner") header.textContent = tr("mode_tuner");
  else header.textContent = tr("staff");
}

function renderScaleModeButtons() {
  const metroBtn = el("scaleModeMetronome");
  if (metroBtn) metroBtn.classList.toggle("active", !!state.scaleMetronomeEnabled);
  const metroVolWrap = el("scaleMetronomeVolumeWrap");
  if (metroVolWrap) metroVolWrap.classList.toggle("hidden", !state.scaleMetronomeEnabled);
}

function setScalePlayMode(mode) {
  if (!["piano", "guitar"].includes(mode)) mode = "piano";
  state.scalePlayMode = mode;
  renderScaleModeButtons();
  if (state.mode === "scales") setMode("scales");
}

function setMode(mode) {
  if (!TUNER_FEATURE_ENABLED && mode === "tuner") {
    mode = "detection";
  }
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
  if (TUNER_FEATURE_ENABLED && state.mode === "tuner" && mode !== "tuner" && state.tuner.running) toggleTuner();
  state.mode = mode;
  if (mode !== "detection" && mode !== "interval_detection") {
    resetMidiScreenWakeLockFully();
  }
  if (state.help.active && !isHelpAvailableForMode(state.mode)) state.help.active = false;
  refreshDetectionButtonsState();
  refreshHelpButtonState();
  const modeScreen = el("modeScreen");
  if (modeScreen) {
    modeScreen.classList.remove("mode-detection", "mode-interval_detection", "mode-generation", "mode-circle_fifths", "mode-scales", "mode-metronome", "mode-tuner");
    modeScreen.classList.add(`mode-${mode}`);
  }
  const modeSelect = el("modeSelect");
  if (modeSelect && modeSelect.value !== mode) modeSelect.value = mode;
  syncLeftPanelHeader();

  document.querySelectorAll(".mode-panel").forEach((p) => p.classList.add("hidden"));
  const panelMap = {
    detection: "panelDetection",
    interval_detection: "panelIntervalDetection",
    generation: "panelGeneration",
    circle_fifths: "panelCircleFifths",
    scales: "panelScales",
    metronome: "panelMetronome",
    tuner: "panelTuner",
  };
  const panelId = panelMap[mode];
  if (panelId && el(panelId)) {
    el(panelId).classList.remove("hidden");
  }

  const supportsInstrument = activeModeSupportsInstrument();
  const supportsStaff = activeModeSupportsStaff();
  el("instrumentArea").classList.toggle("hidden", !supportsInstrument);
  el("instrumentArea").classList.toggle("with-inst-dock", mode === "generation" || mode === "circle_fifths" || mode === "scales");
  el("instrumentSwitch").classList.toggle("hidden", !supportsInstrument);
  el("staffArea").classList.toggle("hidden", !supportsStaff);
  const circleStaffFooter = el("circleFifthsStaffFooter");
  const circleChordOverStaff = el("circleChordOverStaff");
  const circleLeftVisible = mode === "circle_fifths";
  if (circleStaffFooter) {
    if (circleLeftVisible) {
      circleStaffFooter.removeAttribute("hidden");
      circleStaffFooter.setAttribute("aria-hidden", "false");
    } else {
      circleStaffFooter.setAttribute("hidden", "");
      circleStaffFooter.setAttribute("aria-hidden", "true");
    }
  }
  if (circleChordOverStaff) {
    if (circleLeftVisible) {
      circleChordOverStaff.removeAttribute("hidden");
      circleChordOverStaff.setAttribute("aria-hidden", "false");
    } else {
      circleChordOverStaff.setAttribute("hidden", "");
      circleChordOverStaff.setAttribute("aria-hidden", "true");
    }
  }
  const showInstrumentToggle = mode === "generation" || mode === "circle_fifths" || mode === "scales";
  document.querySelectorAll(".inst-btn").forEach((btn) => btn.classList.toggle("hidden", !showInstrumentToggle));
  el("guitarHandedness").classList.toggle("hidden", !showInstrumentToggle || state.instrument !== "guitar");
  const guitarVariationBar = el("guitarVariationBar");
  if (guitarVariationBar) guitarVariationBar.classList.toggle("hidden", !((mode === "generation" || mode === "circle_fifths") && state.instrument === "guitar"));
  const tunerSpectrumCanvas = el("tunerSpectrumCanvas");
  if (tunerSpectrumCanvas) tunerSpectrumCanvas.classList.toggle("hidden", mode !== "tuner" || !TUNER_FEATURE_ENABLED);
  if (TUNER_FEATURE_ENABLED && mode === "tuner") {
    el("instrumentArea").classList.remove("hidden");
    el("sharedPiano").classList.add("hidden");
    el("sharedGuitarCanvas").classList.add("hidden");
    if (guitarVariationBar) guitarVariationBar.classList.add("hidden");
  }

  if (mode === "detection" || mode === "interval_detection") {
    setInstrument("piano");
  } else if (mode === "metronome") {
    setInstrument("piano");
  } else if (mode === "scales") {
    if (state.scalePlayMode === "guitar") setInstrument("guitar");
    else if (state.scalePlayMode === "piano") setInstrument("piano");
  } else if (mode === "circle_fifths") {
    bindCircleFifthsCanvas();
    void runGenerateChordCircle().catch(() => {});
    scheduleCircleFifthsLayout();
  }

  if (supportsInstrument) {
    setInstrument(state.instrument);
    renderInstrument();
    renderStaff();
  } else if (TUNER_FEATURE_ENABLED && mode === "tuner") {
    renderStaff();
    renderTunerSpectrumPanel();
  } else if (supportsStaff) {
    renderStaff();
  } else if (mode === "metronome") {
    renderMetronomeDots();
  }
  refreshGenerationInversionControlState();
  renderScaleModeButtons();
  refreshHelpOverlay();
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
  if (TUNER_FEATURE_ENABLED && state.mode === "tuner") {
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
  if (guitarVariationBar) guitarVariationBar.classList.toggle("hidden", !((state.mode === "generation" || state.mode === "circle_fifths") && inst === "guitar"));
  if ((state.mode === "generation" || state.mode === "circle_fifths") && inst === "guitar" && state.generatedChord && !state.guitarVariations.length) {
    loadGuitarVariations().then(() => {
      renderInstrument();
      renderStaff();
    }).catch(() => {});
  }
  refreshGenerationInversionControlState();
  renderGuitarVariationButtons();
  // Sin esto, al alternar piano/guitarra el pentagrama seguía con el dibujo anterior
  // hasta pulsar una nota (que ya llamaba a renderStaff).
  if (activeModeSupportsInstrument()) {
    renderInstrument();
    if (activeModeSupportsStaff()) {
      renderStaff();
    }
  }
}

function renderGuitarVariationButtons() {
  const bar = el("guitarVariationBar");
  if (!bar) return;
  bar.innerHTML = "";
  const show = isChordGenerationLikeMode() && state.instrument === "guitar" && state.guitarVariations.length > 0;
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
  if (isChordGenerationLikeMode() && state.generatedChord) {
    return new Set((state.generatedChord.notes_midi || []).map((n) => Number(n) % 12));
  }
  if (state.mode === "scales" && state.generatedScale) {
    return new Set((state.generatedScale.notes_midi || []).map((n) => Number(n) % 12));
  }
  if (state.mode === "detection") {
    return new Set(Array.from(state.activeDetectionNotes).map((n) => Number(n) % 12));
  }
  if (state.mode === "interval_detection") {
    if (state.intervalPlayingNote != null) return new Set([Number(state.intervalPlayingNote) % 12]);
    return new Set(state.intervalNotes.map((n) => Number(n) % 12));
  }
  return new Set();
}

function getActiveMidiForMode() {
  if (isChordGenerationLikeMode() && state.generatedChord) {
    return new Set((state.generatedChord.notes_midi || []).map((n) => Number(n)));
  }
  if (state.mode === "scales" && state.generatedScale) {
    return new Set((state.generatedScale.notes_midi || []).map((n) => Number(n)));
  }
  if (state.mode === "detection") {
    return new Set(Array.from(state.activeDetectionNotes));
  }
  if (state.mode === "interval_detection") {
    if (state.intervalPlayingNote != null) return new Set([Number(state.intervalPlayingNote)]);
    return new Set(state.intervalNotes.map((n) => Number(n)));
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

const INTERVAL_NAMES = {
  es: {
    0: "Unísono justo", 1: "Segunda menor", 2: "Segunda mayor",
    3: "Tercera menor", 4: "Tercera mayor", 5: "Cuarta justa",
    6: "Cuarta aum. / Quinta dim.", 7: "Quinta justa",
    8: "Sexta menor", 9: "Sexta mayor", 10: "Séptima menor",
    11: "Séptima mayor", 12: "Octava justa",
  },
  en: {
    0: "Perfect Unison", 1: "Minor Second", 2: "Major Second",
    3: "Minor Third", 4: "Major Third", 5: "Perfect Fourth",
    6: "Aug. Fourth / Dim. Fifth", 7: "Perfect Fifth",
    8: "Minor Sixth", 9: "Major Sixth", 10: "Minor Seventh",
    11: "Major Seventh", 12: "Perfect Octave",
  },
};

// durations: "w"=redonda  "h"=blanca  "q"=negra  "e"=corchea  "s"=semicorchea
//            Añadir "." para puntillo. null=silencio
// jumpAt: índice donde ocurre el intervalo (por defecto 0 = salto entre notas 0 y 1)
const INTERVAL_MELODIES = {
  1:  { name_es: "Tiburón (Jaws)",             name_en: "Jaws Theme",
        beatsPerBar: 4,
        offsets:   [0, 1, null, 0, 1, null, 0, 1, 0, 1, 3, 5],
        durations: ["h","e","q", "q","q","e", "e","e","e","e","q","h"] },

  2:  { name_es: "Cumpleaños feliz",            name_en: "Happy Birthday",
        beatsPerBar: 3, anacrusis: 1,
        jumpAt: 1,
        beams: [[0, 1]],
        offsets:   [0, 0, 2, 0, 5, 4],
        durations: ["e.","s","q","q","q","h"] },

  3:  { name_es: "Smoke on the Water",          name_en: "Smoke on the Water",
        beatsPerBar: 4,
        offsets:   [0, 3, 5, null, 0, 3, 6, 5, null, 0, 3, 5, 3, 0],
        durations: ["q","q","q.","e","q","q","e","q","e","q","q","q","q","h"] },

  4:  { name_es: "Oh! Susanna",                 name_en: "Oh! Susanna",
        beatsPerBar: 4,
        offsets:   [0, 4, 7, 7, 9, 7, 4, 0, 4, 2, 2],
        durations: ["q","q","q","e","e","q","q","q","q","q","h"] },

  5:  { name_es: "Aquí el que no corre vuela",  name_en: "Here Comes the Bride",
        beatsPerBar: 4,
        offsets:   [0, 5, 5, 4, 5, 7, 5, 4, 0],
        durations: ["q","h.","q","q","h","q","q","q","h"] },

  6:  { name_es: "María (West Side Story)",     name_en: "Maria (West Side Story)",
        beatsPerBar: 3,
        offsets:   [0, 6, 7, null, 0, 6, 7],
        durations: ["h","q","h.","q","h","q","h."] },

  7:  { name_es: "Star Wars",                   name_en: "Star Wars",
        beatsPerBar: 4,
        offsets:   [0, 7, 7, 7, 3, 10, 7],
        durations: ["q","e","e","q.","e","e","h"] },

  8:  { name_es: "El sueño imposible",          name_en: "The Impossible Dream",
        beatsPerBar: 3,
        offsets:   [0, 8, 7, 5, 4, 5, 7, 8],
        durations: ["q","h","q.","e","q","q","q.","h"] },

  9:  { name_es: "My Way",                      name_en: "My Way",
        beatsPerBar: 4,
        offsets:   [0, 9, 7, 5, 7, 9, 12],
        durations: ["q","h.","q","q","q","q","h"] },

  10: { name_es: "Somewhere (West Side Story)", name_en: "Somewhere (West Side Story)",
        beatsPerBar: 4,
        offsets:   [0, 10, 9, 7, 9, 7, 3, 7],
        durations: ["h","h","q","q","q.","e","q","h"] },

  11: { name_es: "Take On Me",                  name_en: "Take On Me",
        beatsPerBar: 4,
        offsets:   [0, 11, 12, 9, 7, 9, 11],
        durations: ["e","e","q","e","e","q","h"] },

  12: { name_es: "Somewhere Over the Rainbow",  name_en: "Somewhere Over the Rainbow",
        beatsPerBar: 4,
        offsets:   [0, 12, 11, 9, 8, 6, 9],
        durations: ["h","h","q.","e","q","q","h"] },
};

function getIntervalName(semitones) {
  const lang = state.language in INTERVAL_NAMES ? state.language : "es";
  return INTERVAL_NAMES[lang][semitones] || "-";
}

function getIntervalSemitones() {
  const n = state.intervalNotes;
  if (n.length < 2) return null;
  const raw = Math.abs(n[1] - n[0]);
  const mod = raw % 12;
  return (mod === 0 && raw > 0) ? 12 : mod;
}

function getIntervalMelodyNotes() {
  if (state.intervalNotes.length < 2) return [...state.intervalNotes].sort((a, b) => a - b);
  const semitones = getIntervalSemitones();
  const melody = INTERVAL_MELODIES[semitones];
  if (!melody) return [...state.intervalNotes].sort((a, b) => a - b);
  const base = Math.min(...state.intervalNotes);
  // Mapear a null en vez de filtrar: preserva longitud de array y alineación con durations[]
  return melody.offsets.map((offset) => {
    if (offset === null) return null;
    const n = base + offset;
    return (n >= 0 && n <= 127) ? n : null;
  });
}

function getIntervalMelodySongName() {
  const semitones = getIntervalSemitones();
  if (semitones === null) return null;
  const entry = INTERVAL_MELODIES[semitones];
  if (!entry) return null;
  return state.language === "en" ? entry.name_en : entry.name_es;
}

/** Adds a MIDI note to the interval queue (keeps last 2, insertion order preserved for correct oldest-removal). */
function intervalAddNote(midi) {
  const note = Number(midi);
  if (!Number.isFinite(note)) return;
  state.intervalMelodyActive = false;
  state.intervalPlayGeneration++;
  state.intervalPlayingNote = null;
  state.intervalPlayingIdx = null;
  state.intervalNotes.push(note);
  if (state.intervalNotes.length > 2) state.intervalNotes.shift();
  // Do NOT sort in place — insertion order is needed so shift() always removes the oldest note.
}

/** Duración de cada símbolo en múltiplos de un tiempo (negra = 1). */
const DURATION_BEATS = { w: 4, "h.": 3, h: 2, "q.": 1.5, q: 1, "e.": 0.75, e: 0.5, "s.": 0.375, s: 0.25 };

/**
 * Devuelve los índices DESPUÉS de los cuales hay que dibujar una barra de compás.
 * Cuando una nota atraviesa el límite del compás, la barra se coloca antes de esa nota.
 */
/**
 * anacrusis: tiempos del compás de anacrusa (0 = sin anacrusa).
 * Con anacrusa, la primera barra cae en `anacrusis` tiempos; el resto en múltiplos de beatsPerBar.
 */
function getMelodyBarLines(durations, beatsPerBar, anacrusis = 0) {
  if (!beatsPerBar || beatsPerBar <= 0) return [];
  const result = [];
  let cumBeats = 0;
  // Inicializar lastBarBeat de forma que nextBoundary = anacrusis si hay anacrusa,
  // o = beatsPerBar si no la hay.
  let lastBarBeat = anacrusis > 0 ? anacrusis - beatsPerBar : 0;
  for (let i = 0; i < durations.length; i++) {
    const beats = DURATION_BEATS[durations[i]] ?? 1;
    cumBeats += beats;
    const nextBoundary = lastBarBeat + beatsPerBar;
    if (cumBeats >= nextBoundary - 0.001) {
      if (Math.abs(cumBeats - nextBoundary) < 0.001) {
        result.push(i); // nota acaba justo en el límite → barra después de ella
      } else if (i > 0) {
        result.push(i - 1); // nota atraviesa el límite → barra antes de ella
      }
      while (lastBarBeat + beatsPerBar <= cumBeats + 0.001) lastBarBeat += beatsPerBar;
    }
  }
  return result;
}

/** Plays notes one by one with piano/staff highlighting. Generation counter cancels previous runs.
 *  audioNotes: array paralela opcional (pitch de audio distinto al visual).
 *  durations:  array paralela con "w"/"h"/"q"/"e"/null; si se omite todas duran stepMs. */
function playIntervalNoteSequence(notes, stepMs, audioNotes = null, durations = null) {
  const gen = ++state.intervalPlayGeneration;
  state.intervalPlayingNote = null;
  state.intervalPlayingIdx = null;

  // Calcular tiempos acumulados de inicio para cada nota
  let cursor = 0;
  const startTimes = notes.map((midi, idx) => {
    const t = cursor;
    const beats = durations ? (DURATION_BEATS[durations[idx]] ?? 0.5) : 1;
    cursor += beats * stepMs;
    return t;
  });
  const totalMs = cursor;

  notes.forEach((midi, idx) => {
    const t = startTimes[idx];
    const beats = durations ? (DURATION_BEATS[durations[idx]] ?? 0.5) : 1;
    const noteMs = beats * stepMs;

    if (midi === null) {
      setTimeout(() => {
        if (state.intervalPlayGeneration !== gen) return;
        state.intervalPlayingNote = null;
        state.intervalPlayingIdx = null;
        renderInstrument();
        renderStaff();
      }, t);
      return;
    }

    const playMidi = (audioNotes && audioNotes[idx] != null) ? audioNotes[idx] : Number(midi);
    setTimeout(() => {
      if (state.intervalPlayGeneration !== gen) return;
      state.intervalPlayingNote = Number(midi);
      state.intervalPlayingIdx = idx;
      playSingle(playMidi, "piano");
      renderInstrument();
      renderStaff();
    }, t);
    setTimeout(() => {
      if (state.intervalPlayGeneration !== gen) return;
      if (state.intervalPlayingIdx === idx) {
        state.intervalPlayingNote = null;
        state.intervalPlayingIdx = null;
        renderInstrument();
        renderStaff();
      }
    }, t + Math.round(noteMs * 0.82));
  });

  setTimeout(() => {
    if (state.intervalPlayGeneration !== gen) return;
    state.intervalPlayingNote = null;
    state.intervalPlayingIdx = null;
    renderInstrument();
    renderStaff();
  }, totalMs);
}

function refreshIntervalButtonsState() {
  const hasTwo = state.intervalNotes.length >= 2;
  const playBtn = el("intervalPlay");
  const playRevBtn = el("intervalPlayReverse");
  const clearBtn = el("intervalClear");
  const recuerdaBtn = el("intervalRecuerdaBtn");
  if (playBtn) playBtn.disabled = !hasTwo;
  if (playRevBtn) playRevBtn.disabled = !hasTwo || !!state.intervalMelodyActive;
  if (clearBtn) clearBtn.disabled = state.intervalNotes.length === 0;
  if (recuerdaBtn) {
    const songName = hasTwo ? getIntervalMelodySongName() : null;
    recuerdaBtn.textContent = songName || "-";
    recuerdaBtn.disabled = !songName;
    recuerdaBtn.classList.toggle("active", !!state.intervalMelodyActive);
  }
}

function refreshIntervalResult() {
  refreshIntervalButtonsState();
  renderInstrument();
  renderStaff();

  const raw = state.intervalNotes;
  if (raw.length === 0) {
    el("intervalNoteNames").textContent = "-";
    el("intervalName").textContent = "-";
    el("intervalSemitones").textContent = "-";
    return;
  }
  const n = [...raw].sort((a, b) => a - b);
  if (n.length === 1) {
    el("intervalNoteNames").textContent = noteNameWithOctave(n[0]);
    el("intervalName").textContent = "-";
    el("intervalSemitones").textContent = "-";
    return;
  }
  const rawSt = Math.abs(n[1] - n[0]);
  const mod = rawSt % 12;
  const semitones = (mod === 0 && rawSt > 0) ? 12 : mod;
  el("intervalNoteNames").textContent = noteNameWithOctave(n[0]) + " – " + noteNameWithOctave(n[1]);
  el("intervalName").textContent = getIntervalName(semitones);
  el("intervalSemitones").textContent = String(rawSt);
}

function noteNameWithOctave(midi) {
  const m = Number(midi);
  const octave = Math.floor(m / 12) - 1;
  return noteNameFromPc(m % 12) + octave;
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
  const generationPianoMode = isChordGenerationLikeMode() && state.instrument === "piano" && state.generatedChord;
  const generationCurrentMidi = isChordGenerationLikeMode() ? Number(state.generationCurrentNote) : null;
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
      if (generationCurrentMidi != null && Number(midi) === generationCurrentMidi) key.classList.add("active");
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
    key.innerHTML = pianoKeyLabelHtml(pc);

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
  const generationCurrentMidi = isChordGenerationLikeMode() ? Number(state.generationCurrentNote) : null;
  const drawnPcs = state.mode === "detection" ? null : activePcs;
  const generationVariationMode = isChordGenerationLikeMode() && state.instrument === "guitar" && state.guitarSelectedVariationIdx != null
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
      const idxsByFinger = new Map();
      for (let i = 0; i < displayFrets.length; i += 1) {
        if (Number(displayFrets[i]) !== Number(fretValue)) continue;
        const finger = Number(displayFingers[i]);
        if (!Number.isFinite(finger) || finger <= 0) continue;
        const arr = idxsByFinger.get(finger) || [];
        arr.push(i);
        idxsByFinger.set(finger, arr);
      }

      idxsByFinger.forEach((idxs, finger) => {
        if (!Array.isArray(idxs) || idxs.length < 2) return;

        // Full barre: first and last sounding strings are covered at same fret and same finger.
        if (idxs[0] === minSounded && idxs[idxs.length - 1] === maxSounded) {
          const covered = new Set(idxs);
          barreSegments.push({ fret: Number(fretValue), finger: Number(finger), start: idxs[0], end: idxs[idxs.length - 1], covered });
          idxs.forEach((idx) => barreCovered.add(idx));
          return;
        }

        // Partial barre(s): contiguous runs with at least 2 strings, same fret and same finger.
        let runStart = idxs[0];
        let runPrev = idxs[0];
        for (let j = 1; j < idxs.length; j += 1) {
          const idx = idxs[j];
          if (idx === runPrev + 1) {
            runPrev = idx;
            continue;
          }
          if ((runPrev - runStart + 1) >= 2) {
            const covered = new Set();
            for (let s = runStart; s <= runPrev; s += 1) covered.add(s);
            barreSegments.push({ fret: Number(fretValue), finger: Number(finger), start: runStart, end: runPrev, covered });
            for (let s = runStart; s <= runPrev; s += 1) barreCovered.add(s);
          }
          runStart = idx;
          runPrev = idx;
        }
        if ((runPrev - runStart + 1) >= 2) {
          const covered = new Set();
          for (let s = runStart; s <= runPrev; s += 1) covered.add(s);
          barreSegments.push({ fret: Number(fretValue), finger: Number(finger), start: runStart, end: runPrev, covered });
          for (let s = runStart; s <= runPrev; s += 1) barreCovered.add(s);
        }
      });
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
        const isCurrentGeneration = isChordGenerationLikeMode()
          && generationCurrentMidi != null
          && Number(note) === Number(generationCurrentMidi);
        const finger = Number(displayFingers[i] || 0);
        const coveredByBarre = fret > 0 && barreCovered.has(i);
        state.guitarHitRegions.push({ note, x: cx, y, r: 12, tonic: false });
        if (coveredByBarre) continue;
        ctx.fillStyle = isCurrentGeneration ? "#2faeff" : (isRoot ? "#b35f00" : "#f4a742");
        ctx.strokeStyle = isCurrentGeneration ? "#4fd4ff" : "#f1c27d";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(cx, y, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = (isRoot || isCurrentGeneration) ? "#ffffff" : "#1f1200";
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
      const isRoot = (isChordGenerationLikeMode() && chordRootPc !== null && pc === chordRootPc)
        || (state.mode === "scales" && tonicPc !== null && pc === tonicPc);
      const isCurrentScale = state.mode === "scales"
        && state.scaleCurrentNote != null
        && Number(note) === Number(state.scaleCurrentNote);
      const isCurrentGeneration = isChordGenerationLikeMode()
        && generationCurrentMidi != null
        && Number(note) === generationCurrentMidi;

      if (detectionMode && !inSet) {
        ctx.fillStyle = "#e5e7eb";
        ctx.strokeStyle = "#aab1bc";
      } else if (isCurrentGeneration) {
        ctx.fillStyle = "#2faeff";
        ctx.strokeStyle = "#4fd4ff";
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
        ctx.fillStyle = (isCurrentScale || isCurrentGeneration) ? "#f2f8ff" : "#121a26";
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

  // Repaint barres above strings so cejilla stays clearly visible.
  barreSegments.forEach((seg) => {
    const x = fretCenterX(seg.fret);
    const y1 = top + (seg.start * yGap);
    const y2 = top + (seg.end * yGap);
    const barW = Math.max(13, Math.min(20, yGap * 0.78));
    ctx.strokeStyle = "#6b4a00";
    ctx.lineWidth = barW + 2;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.stroke();
    ctx.strokeStyle = "#f7b500";
    ctx.lineWidth = barW;
    ctx.beginPath();
    ctx.moveTo(x, y1);
    ctx.lineTo(x, y2);
    ctx.stroke();
    ctx.lineCap = "butt";

    // On barres, draw one marker per covered string after repainting the bar,
    // so circles remain visible.
    for (let stringIdx = seg.start; stringIdx <= seg.end; stringIdx += 1) {
      if (!seg.covered.has(stringIdx)) continue;
      const note = Number(tuning[stringIdx]) + Number(seg.fret);
      const pc = ((note % 12) + 12) % 12;
      const y = top + (stringIdx * yGap);
      const isRoot = chordRootPc !== null && pc === chordRootPc;
      const isCurrentGeneration = isChordGenerationLikeMode()
        && generationCurrentMidi != null
        && Number(note) === Number(generationCurrentMidi);
      ctx.fillStyle = isCurrentGeneration ? "#2faeff" : (isRoot ? "#b35f00" : "#f4a742");
      ctx.strokeStyle = isCurrentGeneration ? "#4fd4ff" : "#2e2e2e";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(x, y, 10.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = (isRoot || isCurrentGeneration) ? "#ffffff" : "#1f1200";
      ctx.font = "bold 10px sans-serif";
      ctx.fillText(String(seg.finger > 0 ? seg.finger : 1), x - 3, y + 3);
    }
  });

  const releaseCanvasPress = () => endInputDrag();
  const armSuppressNextGuitarClick = () => {
    state.guitarSuppressNextClick = true;
    if (state.guitarSuppressNextClickTimer != null) {
      clearTimeout(state.guitarSuppressNextClickTimer);
      state.guitarSuppressNextClickTimer = null;
    }
    // Synthetic click after mouse/touch release can arrive with noticeable delay.
    state.guitarSuppressNextClickTimer = setTimeout(() => {
      state.guitarSuppressNextClick = false;
      state.guitarSuppressNextClickTimer = null;
    }, 1400);
  };
  const triggerGuitarPress = (event) => {
    const rect = canvas.getBoundingClientRect();
    const point = event.touches && event.touches.length ? event.touches[0] : event;
    const x = ((point.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((point.clientY - rect.top) / rect.height) * canvas.height;
    return state.guitarHitRegions.find((h) => ((x - h.x) ** 2) + ((y - h.y) ** 2) <= (h.r ** 2)) || null;
  };
  canvas.onmousedown = (event) => {
    if (Number(event.button) !== 0) return;
    event.preventDefault();
    const hit = triggerGuitarPress(event);
    if (hit && state.mode === "scales" && getScalePlaybackInstrument() === "guitar" && state.shiftPressed && hit.tonic) {
      setScaleGuitarStartNote(Number(hit.note));
    }
    if (hit) {
      armSuppressNextGuitarClick();
      beginInputDrag(Number(hit.note), "guitar");
      const onReleaseDoc = () => releaseCanvasPress();
      document.addEventListener("mouseup", onReleaseDoc, { once: true });
      document.addEventListener("touchend", onReleaseDoc, { once: true, passive: true });
      document.addEventListener("touchcancel", onReleaseDoc, { once: true, passive: true });
    }
  };
  canvas.ontouchstart = (event) => {
    event.preventDefault();
    const hit = triggerGuitarPress(event);
    if (hit) {
      armSuppressNextGuitarClick();
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
    if (state.guitarSuppressNextClick) {
      state.guitarSuppressNextClick = false;
      if (state.guitarSuppressNextClickTimer != null) {
        clearTimeout(state.guitarSuppressNextClickTimer);
        state.guitarSuppressNextClickTimer = null;
      }
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
  if (state.mode === "interval_detection") {
    if (pressed || (!pressed && !released)) {
      intervalAddNote(note);
      playSingle(Number(note), "piano");
      refreshIntervalResult();
    }
    return;
  }
  if (isChordGenerationLikeMode() && state.generatedChord) {
    const setGenerationCurrent = (midi) => {
      if (state.generationCurrentClearTimer != null) {
        clearTimeout(state.generationCurrentClearTimer);
        state.generationCurrentClearTimer = null;
      }
      state.generationCurrentNote = Number(midi);
      renderInstrument();
      renderStaff();
      state.generationCurrentClearTimer = setTimeout(() => {
        state.generationCurrentNote = null;
        state.generationCurrentClearTimer = null;
        if (isChordGenerationLikeMode()) {
          renderInstrument();
          renderStaff();
        }
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

function keySignatureSharpFlatCounts(tonicPc, isMinor) {
  const pc = ((Number(tonicPc) % 12) + 12) % 12;
  const sharpMap = isMinor
    ? { 4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7 }
    : { 7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7 };
  const flatMap = isMinor
    ? { 2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6 }
    : { 5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6 };
  return { pc, sharpCount: sharpMap[pc], flatCount: flatMap[pc] };
}

/** Misma regla que el nombre del acorde en API/worker: menos alteraciones; empate → bemoles. */
function chordSymbolPreferFlat(rootPc, isMinor) {
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(rootPc, isMinor);
  if (sharpCount == null && flatCount == null) return false;
  if (sharpCount == null) return true;
  if (flatCount == null) return false;
  if (flatCount < sharpCount) return true;
  if (sharpCount < flatCount) return false;
  return true;
}

// tiePreferFlat: null/undefined → empate enarmónico a sostenidos. true/false → empate explícito (#/♭ o convención armónica).
function keySignatureCountForTonic(tonicPc, isMinor, tiePreferFlat = null) {
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(tonicPc, isMinor);
  if (sharpCount == null && flatCount == null) return { count: 0, preferFlats: false };
  if (sharpCount == null) return { count: flatCount, preferFlats: true };
  if (flatCount == null) return { count: sharpCount, preferFlats: false };
  if (flatCount < sharpCount) return { count: flatCount, preferFlats: true };
  if (sharpCount < flatCount) return { count: sharpCount, preferFlats: false };
  if (tiePreferFlat === true) return { count: flatCount, preferFlats: true };
  return { count: sharpCount, preferFlats: false };
}

/** Empate enarmónico (mismo nº de # y ♭): armadura bemol si el usuario eligió ♭ en el desplegable. */
function applyFlatKeySigIfUiFlatAndTie(sig, tonicPc, isMinor) {
  if (currentAccidentalValue() !== "flat") return sig;
  const { sharpCount, flatCount } = keySignatureSharpFlatCounts(tonicPc, isMinor);
  if (sharpCount != null && flatCount != null && sharpCount === flatCount) {
    return { count: flatCount, preferFlats: true };
  }
  return sig;
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
  const tieFromSelect = currentAccidentalValue() === "flat";
  if (state.mode === "scales" && state.generatedScale) {
    const isMinor = scalePrefersMinor(state.generatedScale.pattern_name);
    const tonic = Number(state.generatedScale.tonic_pc);
    let sig = keySignatureCountForTonic(tonic, isMinor, tieFromSelect);
    sig = applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
    return { signature: sig, tonicPc: tonic, isScale: true };
  }
  // Tonalidad = anillo (tónica + mayor/menor), no la raíz del acorde diatónico elegido.
  // Así la armadura se dibuja igual al cambiar solo de grado (Shift+clic) que al cambiar
  // de tónica; antes dependía de `generatedChord` y `tonicPc` usaba el root del acorde.
  if (state.mode === "circle_fifths") {
    const keyTonic = ((state.circleTonicPc % 12) + 12) % 12;
    const isMinorKey = state.circleKeyMode === "minor";
    let sig = keySignatureCountForTonic(keyTonic, isMinorKey, tieFromSelect);
    sig = applyFlatKeySigIfUiFlatAndTie(sig, keyTonic, isMinorKey);
    return { signature: sig, tonicPc: keyTonic, isScale: false };
  }
  if (state.mode === "generation" && state.generatedChord) {
    const isMinor = isMinorSuffix(state.generatedChord.suffix);
    const tonic = Number(state.generatedChord.root_pc);
    let sig = keySignatureCountForTonic(tonic, isMinor, tieFromSelect);
    sig = applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
    return { signature: sig, tonicPc: tonic, isScale: false };
  }
  if (state.mode === "detection" && state.detectionResult && Number.isFinite(Number(state.detectionResult.root_pc))) {
    const isMinor = isMinorSuffix(state.detectionResult.suffix);
    const tonic = Number(state.detectionResult.root_pc);
    const tieLikeChordName = chordSymbolPreferFlat(tonic, isMinor);
    let sig = keySignatureCountForTonic(tonic, isMinor, tieLikeChordName);
    sig = applyFlatKeySigIfUiFlatAndTie(sig, tonic, isMinor);
    return { signature: sig, tonicPc: tonic, isScale: false };
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

// Sostenidos: F# C# G# D# A# E# B# — altura Y con la misma función que las notas (evita
// desfase por textBaseline "alphabetic" vs Tk anchor center en escritorio).
const KEY_SIG_TREBLE_SHARP_MIDIS = [78, 73, 80, 75, 70, 76, 71];
const KEY_SIG_BASS_SHARP_MIDIS = [54, 49, 56, 51, 46, 52, 47];
// Bemoles: Bb Eb Ab Db Gb Cb Fb — offsets como render_mixin.py (treble_offsets / bass flat).
const KEY_SIG_TREBLE_FLAT_OFFSETS = [2, 0.5, 2.5, 1, 3, 1.5, 3.5];
const KEY_SIG_BASS_FLAT_OFFSETS = [3, 1.5, 3.5, 2, 4, 2.5, 4.5];

function drawKeySignatureOnStaff(ctx, x0, trebleTop, bassTop, gap, sig, bassClef) {
  if (!sig || !sig.count) return x0;
  const staffTop = bassClef ? bassTop : trebleTop;
  const step = 18;
  ctx.save();
  ctx.fillStyle = "#e9edf2";
  ctx.font = "24px serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  let x = x0;
  for (let i = 0; i < sig.count; i += 1) {
    let y;
    if (sig.preferFlats) {
      const offs = bassClef ? KEY_SIG_BASS_FLAT_OFFSETS[i] : KEY_SIG_TREBLE_FLAT_OFFSETS[i];
      y = staffTop + gap * offs;
    } else {
      const midi = bassClef ? KEY_SIG_BASS_SHARP_MIDIS[i] : KEY_SIG_TREBLE_SHARP_MIDIS[i];
      y = bassClef ? midiToBassY(midi, bassTop, gap) : midiToTrebleY(midi, trebleTop, gap);
    }
    ctx.fillText(sig.preferFlats ? "♭" : "♯", x + step / 2, y);
    x += step;
  }
  ctx.restore();
  return x;
}

function drawGrandKeySignature(ctx, trebleTop, bassTop, gap, sig) {
  if (!sig || !sig.count) return 132;
  const xStart = 138;
  const xTrebleEnd = drawKeySignatureOnStaff(ctx, xStart, trebleTop, bassTop, gap, sig, false);
  const xBassEnd = drawKeySignatureOnStaff(ctx, xStart, trebleTop, bassTop, gap, sig, true);
  return Math.max(xTrebleEnd, xBassEnd) + 10;
}

function midiToDiatonicIndex(midi, preferFlat = false) {
  const note = Number(midi);
  const pc = ((note % 12) + 12) % 12;
  const octave = Math.floor(note / 12) - 1;
  const map = preferFlat ? PC_TO_DIATONIC_FLAT : PC_TO_DIATONIC_LETTER;
  return (octave * 7) + map[pc];
}

function midiToTrebleY(midi, trebleTop, gap, preferFlat = false) {
  const trebleBottomLineDiatonic = (4 * 7) + 2; // E4
  const diatonicIdx = midiToDiatonicIndex(midi, preferFlat);
  const staffBaseY = trebleTop + (4 * gap);
  return staffBaseY - ((diatonicIdx - trebleBottomLineDiatonic) * (gap / 2));
}

function midiToBassY(midi, bassTop, gap, preferFlat = false) {
  const bassBottomLineDiatonic = (2 * 7) + 4; // G2
  const diatonicIdx = midiToDiatonicIndex(midi, preferFlat);
  const staffBaseY = bassTop + (4 * gap);
  return staffBaseY - ((diatonicIdx - bassBottomLineDiatonic) * (gap / 2));
}

function drawLedgerLines(ctx, x, y, staffTop, gap, strokeColor = "#cad3e0") {
  const staffBottom = staffTop + gap * 4;
  ctx.strokeStyle = strokeColor;
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

/**
 * duration: null = nota normal sin duración explícita (comportamiento original)
 *   "w"=redonda  "h"=blanca  "q"=negra  "e"=corchea  "s"=semicorchea
 *   Añadir "." para puntillo: "q."=negra con puntillo, "h."=blanca con puntillo, "e."=corchea con puntillo
 */
function drawNote(ctx, x, y, staffTop, gap, extra = false, tonic = false, current = false, currentStroke = null, ghost = false, duration = null, beamed = false) {
  const isDotted = typeof duration === "string" && duration.endsWith(".");
  const base = isDotted ? duration.slice(0, -1) : duration;
  const isMelodic = base != null;
  const isOpen = base === "w" || base === "h";
  const hasStem = base === "h" || base === "q" || base === "e" || base === "s";
  const hasFlag = !beamed && (base === "e" || base === "s");
  const flagCount = base === "s" ? 2 : 1;

  let stroke, fill;
  if (current) {
    stroke = currentStroke || "#6fe0ff";
    fill = isOpen ? "rgba(0,0,0,0)" : (currentStroke || "#6fe0ff");
  } else if (ghost) {
    stroke = "#768496";
    fill = isOpen ? "rgba(0,0,0,0)" : "#768496";
  } else if (extra) {
    stroke = "#ff9a9a";
    fill = (isMelodic && !isOpen) ? "#ff9a9a" : "rgba(0,0,0,0)";
  } else {
    stroke = "#d7dde7";
    fill = (isMelodic && !isOpen) ? "#d7dde7" : "rgba(0,0,0,0)";
  }

  ctx.beginPath();
  ctx.ellipse(x, y, 9, 6.5, -0.35, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 2;
  ctx.stroke();

  drawLedgerLines(ctx, x, y, staffTop, gap, ghost ? "#768496" : "#cad3e0");

  if (isDotted) {
    ctx.beginPath();
    ctx.arc(x + 13, y - 2, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = stroke;
    ctx.fill();
  }

  if (hasStem) {
    const staffMiddle = staffTop + gap * 2;
    const stemUp = y >= staffMiddle;
    const stemX = stemUp ? x + 8 : x - 8;
    const stemStartY = stemUp ? y - 5 : y + 5;
    const stemEndY = stemUp ? y - gap * 3.5 : y + gap * 3.5;
    ctx.beginPath();
    ctx.moveTo(stemX, stemStartY);
    ctx.lineTo(stemX, stemEndY);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    if (hasFlag) {
      const d = stemUp ? 1 : -1;
      for (let f = 0; f < flagCount; f++) {
        const fOff = f * d * gap * 0.65;
        ctx.beginPath();
        ctx.moveTo(stemX, stemEndY + fOff);
        ctx.bezierCurveTo(
          stemX + gap * 1.2, stemEndY + d * gap * 0.6 + fOff,
          stemX + gap * 1.4, stemEndY + d * gap * 1.5 + fOff,
          stemX + gap * 0.4, stemEndY + d * gap * 2.4 + fOff,
        );
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }

    ctx.lineWidth = 2;
  }
}

/** Dibuja un símbolo de silencio. duration igual que en drawNote (base + puntillo opcional). */
function drawRest(ctx, x, staffTop, gap, duration, stroke) {
  const isDotted = typeof duration === "string" && duration.endsWith(".");
  const base = isDotted ? duration.slice(0, -1) : (duration || "q");
  ctx.fillStyle = stroke;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 1.5;
  const midY = staffTop + gap * 2;

  if (base === "w") {
    // Silencio de redonda: rectángulo colgando bajo la 4ª línea
    ctx.fillRect(x - 7, staffTop + gap * 3, 14, gap * 0.55);
  } else if (base === "h") {
    // Silencio de blanca: rectángulo sentado sobre la 3ª línea
    ctx.fillRect(x - 7, staffTop + gap * 2 - gap * 0.55, 14, gap * 0.55);
  } else if (base === "q") {
    // Silencio de negra: zigzag simplificado
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x + 3, midY - gap * 0.9);
    ctx.lineTo(x - 3, midY - gap * 0.3);
    ctx.lineTo(x + 4, midY + gap * 0.1);
    ctx.bezierCurveTo(x + 6, midY + gap * 0.35, x - 2, midY + gap * 0.7, x - 1, midY + gap * 0.9);
    ctx.stroke();
    ctx.lineWidth = 1.5;
  } else {
    // Silencio de corchea/semicorchea: punto + trazo diagonal + banderita(s)
    const flagCount = base === "s" ? 2 : 1;
    const flagY = midY - gap * 0.6;
    ctx.beginPath();
    ctx.arc(x + 4, flagY, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x + 4, flagY);
    ctx.lineTo(x - 4, midY + gap * 0.6);
    ctx.stroke();
    for (let f = 0; f < flagCount; f++) {
      const fy = flagY + f * gap * 0.5;
      ctx.beginPath();
      ctx.moveTo(x + 4, fy);
      ctx.bezierCurveTo(x + 12, fy + gap * 0.4, x + 12, fy + gap * 0.9, x + 4, fy + gap * 1.1);
      ctx.stroke();
    }
  }

  if (isDotted) {
    ctx.beginPath();
    ctx.arc(x + 14, midY - gap * 0.1, 2, 0, Math.PI * 2);
    ctx.fill();
  }
}

/**
 * Dibuja la barra (beam) entre notas barradas (corcheas/semicorcheas unidas).
 * positions: array de {stemX, stemEndY, stemUp, base} para cada nota del grupo.
 */
function drawBeam(ctx, positions, stroke) {
  if (positions.length < 2) return;
  const p0 = positions[0];
  const pN = positions[positions.length - 1];
  const bh = 4;    // grosor de cada barra
  const bGap = 3;  // separación entre barras
  const dir = p0.stemUp ? 1 : -1; // 1 = barras hacia el pentagrama (abajo); -1 = hacia arriba

  const drawBar = (xa, ya, xb, yb) => {
    ctx.fillStyle = stroke;
    ctx.beginPath();
    ctx.moveTo(xa, ya);
    ctx.lineTo(xb, yb);
    ctx.lineTo(xb, yb + dir * bh);
    ctx.lineTo(xa, ya + dir * bh);
    ctx.closePath();
    ctx.fill();
  };

  // Barra primaria: recorre todo el grupo
  drawBar(p0.stemX, p0.stemEndY, pN.stemX, pN.stemEndY);

  // Barras secundarias: para semicorcheas (2 banderas → 2 barras)
  const dx = pN.stemX - p0.stemX;
  const dy = pN.stemEndY - p0.stemEndY;
  positions.forEach((p, i) => {
    if (p.base !== "s") return;
    const adj = i > 0 ? positions[i - 1] : positions[i + 1];
    const halfX = (p.stemX + adj.stemX) / 2;
    const t = dx !== 0 ? (halfX - p0.stemX) / dx : 0;
    const halfY = p0.stemEndY + t * dy;
    const off = dir * (bh + bGap);
    if (i > 0) {
      drawBar(halfX, halfY + off, p.stemX, p.stemEndY + off);
    } else {
      drawBar(p.stemX, p.stemEndY + off, halfX, halfY + off);
    }
  });
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

  const current = ((Number(state.metronomeDisplayBeat) || 0) % beats + beats) % beats;
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

  state.staff.metronomeRegions = {
    yellowPoints: {
      x: left - activeR - 6,
      y: yTop - activeR - 6,
      w: (right - left) + ((activeR + 6) * 2),
      h: (activeR + 6) * 2,
    },
    scaleAxis: {
      x: left,
      y: axisY - 18,
      w: right - left,
      h: 36,
    },
    redBall: {
      x: redX - redR - 6,
      y: axisY - redR - 6,
      w: (redR + 6) * 2,
      h: (redR + 6) * 2,
    },
  };
  if (state.help.active && state.mode === "metronome") syncMetronomeHelpHotspots();

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

  const bins = state.tuner.freqData;
  const audioCtx = state.tuner.audioCtx;
  const nyq = (audioCtx?.sampleRate || 44100) / 2;

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

  if (bins && audioCtx) {
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
  } else {
    ctx.fillStyle = "#8796ab";
    ctx.font = "bold 14px Helvetica";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("-", (x1 + x2) / 2, (y1 + y2) / 2);
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
  if (state.mode === "interval_detection") {
    if (state.intervalMelodyActive) return getIntervalMelodyNotes();
    return [...state.intervalNotes].sort((a, b) => a - b);
  }
  if (isChordGenerationLikeMode() && state.generatedChord) {
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
  if (!(isChordGenerationLikeMode() && state.instrument === "guitar")) return null;
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
  if (!(isChordGenerationLikeMode() && state.generatedChord)) return [];
  const selectedVariation = getSelectedGuitarVariation();
  const variationNotes = getVariationNotes(selectedVariation);
  if (variationNotes.length) return variationNotes;
  return (state.generatedChord.notes_midi || [])
    .map((n) => Number(n))
    .filter((n) => Number.isFinite(n))
    .sort((a, b) => a - b);
}

/** Divide texto para canvas (measureText) en líneas que caben en maxWidth px. */
function wrapCanvasTextLines(ctx, text, maxWidth) {
  const words = String(text).split(/\s+/).filter(Boolean);
  if (!words.length) return [];
  const lines = [];
  let line = words[0];
  for (let i = 1; i < words.length; i += 1) {
    const test = `${line} ${words[i]}`;
    if (ctx.measureText(test).width <= maxWidth) {
      line = test;
    } else {
      lines.push(line);
      line = words[i];
    }
  }
  lines.push(line);
  return lines;
}

/** Dibuja la indicación de compás (p.ej. 3/4 o 4/4) en un pentagrama. */
function drawTimeSignature(ctx, x, staffTop, gap, numerator, denominator, color) {
  ctx.save();
  ctx.fillStyle = color || "#cad3e0";
  ctx.font = `bold ${Math.round(gap * 1.9)}px serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(String(numerator),   x, staffTop + gap * 1);
  ctx.fillText(String(denominator), x, staffTop + gap * 3);
  ctx.restore();
}

/**
 * Devuelve el símbolo de alteración necesario para una nota dado la armadura activa,
 * o null si la nota es natural o está cubierta por la armadura.
 */
function getNoteAccidental(midi, signature) {
  const pc = ((midi % 12) + 12) % 12;
  const NATURAL_PCS = new Set([0, 2, 4, 5, 7, 9, 11]); // C D E F G A B
  if (NATURAL_PCS.has(pc)) return null;
  const SHARP_PC_ORDER = [6, 1, 8, 3, 10]; // F# C# G# D# A#
  const FLAT_PC_ORDER  = [10, 3, 8, 1, 6]; // Bb Eb Ab Db Gb
  // For C major (0 accidentals) respect the user's UI preference; otherwise follow key sig
  const useFlat = signature.count > 0 ? signature.preferFlats : currentIsFlat();
  if (useFlat) {
    const covered = new Set(FLAT_PC_ORDER.slice(0, signature.count));
    if (covered.has(pc)) return null;
    return "♭";
  } else {
    const covered = new Set(SHARP_PC_ORDER.slice(0, signature.count));
    if (covered.has(pc)) return null;
    return "♯";
  }
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
  const compactChordStaff = isChordGenerationLikeMode();
  const detectionStaff = state.mode === "detection";
  const intervalDetectionStaff = state.mode === "interval_detection";
  const intervalMelodyStaff = intervalDetectionStaff && !!state.intervalMelodyActive;
  const generationStaff = isChordGenerationLikeMode();
  const scaleStaff = state.mode === "scales";
  state.staff.scaleRegions = [];
  if ((detectionStaff || intervalDetectionStaff) && notes.length === 0) {
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
  const generationCurrentMidi = isChordGenerationLikeMode() ? state.generationCurrentNote : null;
  const generationPlaying = isChordGenerationLikeMode() ? state.generationPlayingNotes : new Set();
  const generationPlayingDisplay = new Set(Array.from(generationPlaying).map((n) => Number(n)));
  const generationRhDisplayNotes = isChordGenerationLikeMode() && state.generatedChord
    ? new Set(getGenerationBaseNotes())
    : new Set();
  const generationLhDisplayNotes = isChordGenerationLikeMode() && state.generatedChord
    ? new Set((state.generatedChord.notes_midi || []).map((n) => Number(n) - 12).filter((n) => n >= 0))
    : new Set();
  let generationCurrentDisplayMidi = generationCurrentMidi;
  if (isChordGenerationLikeMode() && state.instrument === "piano" && generationCurrentDisplayMidi != null) {
    const staffSet = new Set(notes.map((n) => Number(n)));
    // Keyboard LH taps are an octave lower than the LH voice drawn in staff.
    if (!staffSet.has(Number(generationCurrentDisplayMidi)) && staffSet.has(Number(generationCurrentDisplayMidi) + 12)) {
      generationCurrentDisplayMidi = Number(generationCurrentDisplayMidi) + 12;
    }
  }
  if (isChordGenerationLikeMode() && state.instrument === "piano" && generationPlayingDisplay.size) {
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
  if (scaleStaff || detectionStaff) {
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
  const intervalMelodyDurations = (() => {
    if (!intervalMelodyStaff) return [];
    const sem = getIntervalSemitones();
    const mel = sem != null ? INTERVAL_MELODIES[sem] : null;
    return mel ? mel.durations : [];
  })();
  const intervalMelodyJumpAt = (() => {
    if (!intervalMelodyStaff) return 0;
    const sem = getIntervalSemitones();
    const mel = sem != null ? INTERVAL_MELODIES[sem] : null;
    return mel ? (mel.jumpAt ?? 0) : 0;
  })();
  // Grupos de barras (beams) para la melodía del intervalo
  const melodyBeamGroups = (() => {
    if (!intervalMelodyStaff) return [];
    const sem = getIntervalSemitones();
    const mel = sem != null ? INTERVAL_MELODIES[sem] : null;
    return mel?.beams || [];
  })();
  const beamedIdxSet = new Set(melodyBeamGroups.flat());
  const beamStemData = new Map(); // idx → {stemX, stemEndY, stemUp, base}

  // Espaciado adaptativo: reduce el paso si la melodía tiene muchas notas
  const intervalNoteStep = intervalDetectionStaff && notes.length > 1
    ? Math.min(42, Math.floor((width - startX - 66) / (notes.length - 1)))
    : 42;

  // Guardar posiciones de notas de setup para dibujar ligadura después
  const setupNotePositions = [];
  let lastRestClef = "treble"; // para colocar silencios en la clave correcta
  notes.forEach((midi, idx) => {
    if (midi === null) {
      // Silencio: dibujar símbolo en la clave del último contexto visto
      if (intervalMelodyStaff) {
        const restX = startX + 46 + idx * intervalNoteStep;
        const dur = intervalMelodyDurations[idx] || "q";
        const restColor = "#768496";
        const restStaffTop = lastRestClef === "bass" ? bassTop : trebleTop;
        drawRest(ctx, restX, restStaffTop, gap, dur, restColor);
      }
      return;
    }

    // Determinar alteración antes de calcular la posición Y (la convención #/b afecta la altura)
    const noteAcc = (intervalDetectionStaff || detectionStaff)
      ? getNoteAccidental(Number(midi), staffCtx.signature)
      : null;
    const notePreferFlat = noteAcc === "♭";

    const useTreble = Number(midi) >= 60;
    lastRestClef = useTreble ? "treble" : "bass";
    const y = useTreble
      ? midiToTrebleY(midi, trebleTop, gap, notePreferFlat)
      : midiToBassY(midi, bassTop, gap, notePreferFlat);
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
    } else if (intervalDetectionStaff) {
      x = startX + 46 + idx * intervalNoteStep;
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
      || (isChordGenerationLikeMode() && generationPlayingDisplay.has(Number(midi)))
      || (intervalDetectionStaff && state.intervalPlayingIdx != null && idx === state.intervalPlayingIdx);
    const currentStroke = current
      ? (
          ((isChordGenerationLikeMode()
            && state.instrument === "piano"
            && generationLhDisplayNotes.has(Number(midi))
            && !generationRhDisplayNotes.has(Number(midi)))
            || (scaleStaff && scalePlaybackInstrument === "piano" && scaleLhSet.has(Number(midi)) && !scaleRhSet.has(Number(midi))))
            ? "#ff8a3d"
            : "#6fe0ff"
        )
      : null;
    const ghost = intervalMelodyStaff && idx > intervalMelodyJumpAt + 1;
    const duration = intervalMelodyStaff ? (intervalMelodyDurations[idx] || "q") : null;
    const beamedNote = intervalMelodyStaff && beamedIdxSet.has(idx);

    // Dibujar alteración (sostenido/bemol) antes de la cabeza si la nota lo requiere
    if (noteAcc) {
      const accColor = current ? (currentStroke || "#6fe0ff")
                     : ghost   ? "#768496"
                     : extra   ? "#ff9a9a"
                     : "#d7dde7";
      ctx.save();
      ctx.font = `bold ${Math.round(gap * 1.4)}px serif`;
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      ctx.fillStyle = accColor;
      ctx.fillText(noteAcc, x - 11, y);
      ctx.restore();
    }

    drawNote(ctx, x, y, staffTop, gap, extra, tonic, current, currentStroke, ghost, duration, beamedNote);

    // Registrar datos de stem para notas barradas
    if (beamedNote) {
      const bStaffMiddle = staffTop + gap * 2;
      const bStemUp = y >= bStaffMiddle;
      const bStemX = bStemUp ? x + 8 : x - 8;
      const bStemEndY = bStemUp ? y - gap * 3.5 : y + gap * 3.5;
      const bBase = typeof duration === "string" && duration.endsWith(".") ? duration.slice(0, -1) : duration;
      beamStemData.set(idx, { stemX: bStemX, stemEndY: bStemEndY, stemUp: bStemUp, base: bBase });
    }

    // Guardar posición de notas de setup para ligadura
    if (intervalMelodyStaff && idx <= intervalMelodyJumpAt && intervalMelodyJumpAt > 0) {
      setupNotePositions.push({ x, y });
    }

    if (scaleStaff || generationStaff) {
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

    if (!compactChordStaff && !detectionStaff && !intervalDetectionStaff) {
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

  // Dibujar barras (beams) entre notas barradas
  if (intervalMelodyStaff && melodyBeamGroups.length > 0) {
    melodyBeamGroups.forEach((group) => {
      const positions = group.map((i) => beamStemData.get(i)).filter(Boolean);
      if (positions.length >= 2) {
        const isGhost = group[0] > intervalMelodyJumpAt + 1;
        drawBeam(ctx, positions, isGhost ? "#768496" : "#d7dde7");
      }
    });
  }

  // Dibujar indicación de compás y barras de compás
  if (intervalMelodyStaff) {
    const mel = INTERVAL_MELODIES[getIntervalSemitones()];
    const bpb = mel?.beatsPerBar;
    if (bpb) {
      // Indicación de compás (p.ej. 3/4 o 4/4) en clave de sol y fa
      const timeSigX = startX + 22;
      drawTimeSignature(ctx, timeSigX, trebleTop, gap, bpb, 4, "#8fa1b7");
      drawTimeSignature(ctx, timeSigX, bassTop,   gap, bpb, 4, "#8fa1b7");

      // Barras de compás (líneas verticales entre los dos pentagramas)
      const barLineIdxs = getMelodyBarLines(intervalMelodyDurations, bpb, mel?.anacrusis ?? 0);
      ctx.strokeStyle = "#8fa1b7";
      ctx.lineWidth = 1.2;
      barLineIdxs.forEach((afterIdx) => {
        const bx = Math.round(startX + 46 + afterIdx * intervalNoteStep + intervalNoteStep / 2);
        ctx.beginPath();
        ctx.moveTo(bx, trebleTop);
        ctx.lineTo(bx, bassTop + gap * 4);
        ctx.stroke();
      });
    }
  }

  // Dibujar ligadura entre notas de setup (cuando jumpAt > 0)
  if (intervalMelodyStaff && intervalMelodyJumpAt > 0 && setupNotePositions.length >= 1) {
    const from = setupNotePositions[0];
    // La nota de llegada (interval lower, idx=jumpAt) se calcula a partir de su posición X
    const toX = startX + 46 + intervalMelodyJumpAt * intervalNoteStep;
    const noteAtJumpAt = notes[intervalMelodyJumpAt];
    if (noteAtJumpAt != null) {
      const toY = Number(noteAtJumpAt) >= 60
        ? midiToTrebleY(noteAtJumpAt, trebleTop, gap)
        : midiToBassY(noteAtJumpAt, bassTop, gap);
      const midX = (from.x + toX) / 2;
      const arcHeight = -14;
      ctx.beginPath();
      ctx.moveTo(from.x, from.y + 10);
      ctx.quadraticCurveTo(midX, Math.min(from.y, toY) + 10 + arcHeight, toX, toY + 10);
      ctx.strokeStyle = "#768496";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }

  if (scaleStaff && scalePlaybackInstrument === "guitar") {
    ctx.fillStyle = "#8fa1b7";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.fillText(tr("scale_staff_guitar_shift_hint"), width / 2, height - 10);
    ctx.textAlign = "start";
    ctx.textBaseline = "alphabetic";
  }

  if (scaleStaff || detectionStaff || generationStaff) {
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
        if (detectionStaff) {
          handleInstrumentNote(Number(state.staff.scalePressedNote), {
            pressed: false,
            released: true,
            instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
          });
        }
        state.staff.scalePressedNote = Number(hit.note);
        state.staff.scalePressedDegree = Number(hit.degree);
        if (detectionStaff) {
          handleInstrumentNote(Number(hit.note), {
            pressed: true,
            instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
          });
        } else {
          handleInstrumentNote(Number(hit.note));
        }
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
      if (detectionStaff) {
        handleInstrumentNote(Number(hit.note), {
          pressed: true,
          instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
        });
      } else {
        handleInstrumentNote(Number(hit.note));
      }
      renderStaff();
    };
    canvas.onmouseup = () => {
      if (detectionStaff && state.staff.scalePressedNote != null) {
        handleInstrumentNote(Number(state.staff.scalePressedNote), {
          pressed: false,
          released: true,
          instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
        });
      }
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
      if (detectionStaff) {
        handleInstrumentNote(Number(hit.note), {
          pressed: true,
          instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
        });
        handleInstrumentNote(Number(hit.note), {
          pressed: false,
          released: true,
          instrumentHint: state.instrument === "guitar" ? "guitar" : "piano",
        });
      } else {
        handleInstrumentNote(Number(hit.note));
      }
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
  try {
    const data = await fetchJson(`/api/meta?language=${state.language}`);
    state.appVersion = data.app_version || WEB_APP_VERSION_FALLBACK;
    state.chordPatterns = data.chord_patterns || [];
    state.scalePatterns = data.scale_patterns || [];
  } catch (err) {
    console.warn("Failed to load /api/meta:", err);
    state.chordPatterns = state.chordPatterns || [];
    state.scalePatterns = state.scalePatterns || [];
  }
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
    accidental: currentAccidentalValue(),
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
    accidental: currentAccidentalValue(),
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
    const notes = getGenerationBaseNotes();
    if (notes.length) {
      playChordMidi(notes, { instrument: state.instrument === "guitar" ? "guitar" : "piano" });
    }
  }
}

async function runGenerateScale() {
  const restartLoop = state.scaleLoop.active;
  stopScaleLoop();
  const payload = {
    tonic_pc: Number(el("scaleRoot").value),
    pattern_name: el("scaleType").value,
    language: state.language,
    accidental: currentAccidentalValue(),
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

function ensureMetronomeNoiseBuffer(ctx) {
  if (state.metronomeNoiseBuffer && state.metronomeNoiseBuffer.sampleRate === ctx.sampleRate) {
    return state.metronomeNoiseBuffer;
  }
  const size = Math.max(512, Math.floor(ctx.sampleRate * 0.025));
  const buffer = ctx.createBuffer(1, size, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < size; i += 1) {
    data[i] = (Math.random() * 2) - 1;
  }
  state.metronomeNoiseBuffer = buffer;
  return buffer;
}

function nearestSampleRoot(note, sampleMap) {
  const midi = Number(note);
  const roots = Object.keys(sampleMap || {}).map((k) => Number(k)).filter((n) => Number.isFinite(n));
  if (!roots.length) return null;
  return roots.reduce((best, cur) => (
    best == null || Math.abs(cur - midi) < Math.abs(best - midi) ? cur : best
  ), null);
}

async function decodeSampleBuffer(ctx, url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`sample fetch failed: ${url} (${response.status})`);
  const bytes = await response.arrayBuffer();
  return await ctx.decodeAudioData(bytes.slice(0));
}

function normalizeAudioBuffer(ctx, buffer, { targetPeak = 0.98, extraGain = 1.0 } = {}) {
  if (!buffer) return buffer;
  const channels = buffer.numberOfChannels || 1;
  const length = buffer.length || 0;
  if (!length) return buffer;
  let peak = 0;
  for (let ch = 0; ch < channels; ch += 1) {
    const data = buffer.getChannelData(ch);
    for (let i = 0; i < data.length; i += 1) {
      const v = Math.abs(data[i]);
      if (v > peak) peak = v;
    }
  }
  const safePeak = Math.max(1e-6, peak);
  const gain = Math.max(0, (targetPeak / safePeak) * Math.max(0, Number(extraGain) || 1));
  const out = ctx.createBuffer(channels, length, buffer.sampleRate);
  for (let ch = 0; ch < channels; ch += 1) {
    const src = buffer.getChannelData(ch);
    const dst = out.getChannelData(ch);
    for (let i = 0; i < src.length; i += 1) {
      const v = src[i] * gain;
      dst[i] = Math.max(-1, Math.min(1, v));
    }
  }
  return out;
}

async function preloadAudioSamples() {
  const ctx = ensureAudioCtx();
  if (state.audioSampleLoadPromise) return state.audioSampleLoadPromise;
  state.audioSampleLoadPromise = (async () => {
    const urls = new Set([
      METRONOME_SAMPLE_URL,
      ...Object.values(PIANO_SAMPLE_URLS),
      ...Object.values(GUITAR_SAMPLE_URLS),
    ]);
    const out = {};
    await Promise.all(Array.from(urls).map(async (url) => {
      try {
        const decoded = await decodeSampleBuffer(ctx, url);
        out[url] = url === METRONOME_SAMPLE_URL
          ? normalizeAudioBuffer(ctx, decoded, { targetPeak: 0.98, extraGain: 1.8 })
          : decoded;
      } catch (err) {
        console.warn("Sample load failed:", url, err);
      }
    }));
    state.audioSampleCache = out;
    return out;
  })();
  return state.audioSampleLoadPromise;
}

function sampleBuffer(url) {
  if (!state.audioSampleCache || typeof state.audioSampleCache !== "object") return null;
  return state.audioSampleCache[url] || null;
}

function playInstrumentSampleAt(midi, startTime = null, durationSeconds = 0.46, instrument = "piano") {
  const sampleMap = instrument === "guitar" ? GUITAR_SAMPLE_URLS : PIANO_SAMPLE_URLS;
  const root = nearestSampleRoot(midi, sampleMap);
  if (root == null) return null;
  const url = sampleMap[root];
  const buffer = sampleBuffer(url);
  if (!buffer) {
    void preloadAudioSamples();
    return null;
  }

  const ctx = ensureAudioCtx();
  const t = startTime == null ? ctx.currentTime : Number(startTime);
  const src = ctx.createBufferSource();
  src.buffer = buffer;
  src.playbackRate.setValueAtTime(2 ** ((Number(midi) - Number(root)) / 12), t);

  const gain = ctx.createGain();
  const baseDur = Math.max(0.16, Number(durationSeconds) || 0.46);
  const sustainEnd = t + (instrument === "guitar" ? (baseDur * 1.9) : (baseDur * 1.7));
  gain.gain.setValueAtTime(0.0001, t);
  gain.gain.exponentialRampToValueAtTime(instrument === "guitar" ? 0.96 : 0.88, t + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, sustainEnd + (instrument === "guitar" ? 0.62 : 0.48));

  src.connect(gain);
  gain.connect(ensureAudioBus(ctx));
  src.start(t);
  src.stop(sustainEnd + 0.75);
  return { source: src, gain };
}

function beep(freq = 1000, durationMs = 70, gain = 0.1) {
  const ctx = ensureAudioCtx();
  const t = ctx.currentTime;
  const inputGain = Math.max(0, Number(gain) || 0.1);
  if (inputGain <= 0) return;
  // Keep metronome click under clipping so volume changes remain perceptible.
  const amp = Math.min(1.0, inputGain * 0.34);
  const dur = Math.max(0.035, Number(durationMs || 70) / 1000);
  const isBar = Number(freq) >= 1700;
  const isAccent = isBar || Number(freq) >= 1300;

  const out = ctx.createGain();
  out.gain.value = 1.0;
  out.connect(ctx.destination);

  // Percussive "tick": short noise burst filtered as woodblock-like click.
  const noise = ctx.createBufferSource();
  noise.buffer = ensureMetronomeNoiseBuffer(ctx);
  const hp = ctx.createBiquadFilter();
  hp.type = "highpass";
  hp.frequency.value = isAccent ? 1300 : 1050;
  const bp = ctx.createBiquadFilter();
  bp.type = "bandpass";
  bp.frequency.value = isBar ? 2400 : (isAccent ? 2100 : 1750);
  bp.Q.value = isBar ? 2.2 : 1.8;
  const nGain = ctx.createGain();
  nGain.gain.setValueAtTime(0.0001, t);
  nGain.gain.exponentialRampToValueAtTime(amp * (isBar ? 1.12 : (isAccent ? 0.96 : 0.82)), t + 0.0015);
  nGain.gain.exponentialRampToValueAtTime(0.0001, t + (dur * 0.42));
  noise.connect(hp);
  hp.connect(bp);
  bp.connect(nGain);
  nGain.connect(out);
  noise.start(t);
  noise.stop(t + Math.min(0.06, dur));

  // Resonant body for a natural metronome "toc".
  const osc = ctx.createOscillator();
  const oGain = ctx.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(isBar ? 1820 : (isAccent ? 1520 : 1260), t);
  oGain.gain.setValueAtTime(0.0001, t);
  oGain.gain.exponentialRampToValueAtTime(amp * (isBar ? 0.44 : (isAccent ? 0.36 : 0.30)), t + 0.001);
  oGain.gain.exponentialRampToValueAtTime(0.0001, t + (dur * 0.6));
  osc.connect(oGain);
  oGain.connect(out);
  osc.start(t);
  osc.stop(t + Math.min(0.08, dur * 1.1));
}

function playPianoAt(midi, startTime = null, durationSeconds = 0.46) {
  playInstrumentSampleAt(midi, startTime, durationSeconds, "piano");
}

function playGuitarAt(midi, startTime = null, durationSeconds = 0.9) {
  playInstrumentSampleAt(midi, startTime, durationSeconds, "guitar");
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
  if (isChordGenerationLikeMode()) {
    if (state.generationPlayClearTimer != null) {
      clearTimeout(state.generationPlayClearTimer);
      state.generationPlayClearTimer = null;
    }
    state.generationPlayingNotes = new Set(normalizedNotes);
    renderStaff();
  }
  const t = ctx.currentTime + 0.005;
  if (instrument === "guitar") {
    // Mismo ataque simultáneo que startHeldChord / botón Play (sin desfase tipo rasgueo).
    normalizedNotes.forEach((midi) => playSingleAt(Number(midi), t, 1.35, "guitar"));
  } else {
    normalizedNotes.forEach((midi) => playSingleAt(Number(midi), t, 1.65, "piano"));
  }
  if (isChordGenerationLikeMode() && normalizedNotes.length) {
    const clearMs = instrument === "guitar" ? 1700 : 1500;
    state.generationPlayClearTimer = setTimeout(() => {
      state.generationPlayingNotes.clear();
      state.generationPlayClearTimer = null;
      if (isChordGenerationLikeMode()) renderStaff();
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
    if (isChordGenerationLikeMode()) renderStaff();
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
  const played = playInstrumentSampleAt(
    note,
    null,
    instrument === "guitar" ? 1.05 : 0.95,
    instrument,
  );
  if (!played) return;
  state.heldMidiInputVoices.set(note, {
    gain: played.gain,
    oscs: [played.source],
    noise: null,
    instrument,
  });
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
  const played = playInstrumentSampleAt(
    note,
    null,
    instrument === "guitar" ? 1.05 : 0.95,
    instrument,
  );
  if (!played) return;
  state.heldInputVoices.set(note, {
    gain: played.gain,
    oscs: [played.source],
    noise: null,
    instrument,
  });
}

function startHeldVoice(midi, instrument = "piano") {
  const note = Number(midi);
  if (!Number.isFinite(note)) return;
  if (!(state.heldChordVoices instanceof Map)) state.heldChordVoices = new Map();
  if (state.heldChordVoices.has(note)) return;
  const played = playInstrumentSampleAt(
    note,
    null,
    instrument === "guitar" ? 1.2 : 1.35,
    instrument,
  );
  if (!played) return;
  state.heldChordVoices.set(note, {
    gain: played.gain,
    oscs: [played.source],
    noise: null,
    instrument,
  });
}

function startHeldChord(notes, instrument = "piano") {
  stopHeldChord();
  const normalizedNotes = Array.from(new Set((notes || []).map((midi) => Number(midi))))
    .filter((midi) => Number.isFinite(midi));
  normalizedNotes.forEach((midi) => startHeldVoice(midi, instrument));
  if (isChordGenerationLikeMode() && normalizedNotes.length) {
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
    beep((idx === 0 && state.scaleLoop.direction > 0) ? 1720 : 1120, 70, 0.46 * metronomeVolumeGain());
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
    if (i === state.metronomeDisplayBeat) d.classList.add("active");
    if (i === 0) d.classList.add("accent");
    d.textContent = String(i + 1);
    dots.appendChild(d);
  }
}

function metronomeVisualDelayMs() {
  const ctx = state.metronomeCtx;
  const latencySec = ctx
    ? Math.max(Number(ctx.baseLatency) || 0, Number(ctx.outputLatency) || 0)
    : 0;
  return Math.max(18, Math.min(60, Math.round(latencySec * 1000) + 10));
}

function clearMetronomeVisualDelayTimer() {
  if (state.metronomeVisualDelayTimer != null) {
    clearTimeout(state.metronomeVisualDelayTimer);
    state.metronomeVisualDelayTimer = null;
  }
}

function syncMetronomeVisualBeat(beat) {
  clearMetronomeVisualDelayTimer();
  const delayMs = metronomeVisualDelayMs();
  if (!state.metronomeRunning || delayMs <= 1) {
    state.metronomeDisplayBeat = beat;
    renderMetronomeDots();
    if (state.mode === "metronome") renderStaff();
    return;
  }
  state.metronomeVisualDelayTimer = setTimeout(() => {
    state.metronomeVisualDelayTimer = null;
    if (!state.metronomeRunning) return;
    state.metronomeDisplayBeat = beat;
    renderMetronomeDots();
    if (state.mode === "metronome") renderStaff();
  }, delayMs);
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
    state.metronomeMotionStartTs = performance.now() + metronomeVisualDelayMs();
    syncMetronomeVisualBeat(state.currentBeat);
  }

  const accent = state.currentSubclick === 0;
  const barAccent = accent && state.currentBeat === 0 && state.metronomeBarAccentEnabled;
  beep(
    barAccent ? 1780 : (accent ? 1360 : 980),
    72,
    (barAccent ? 0.58 : 0.46) * metronomeVolumeGain(),
  );

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
  state.metronomeVolume = Math.max(
    0,
    Math.min(100, Number(el("metroVolume")?.value) || Number(el("scaleMetroVolume")?.value) || 100),
  );
}

async function toggleMetronome() {
  if (state.metronomeRunning) {
    state.metronomeRunning = false;
    if (state.metronomeTimer != null) clearTimeout(state.metronomeTimer);
    state.metronomeTimer = null;
    state.currentBeat = -1;
    state.metronomeDisplayBeat = -1;
    state.currentSubclick = 0;
    state.metronomeTickCount = 0;
    clearMetronomeVisualDelayTimer();
    stopMetronomeAnimation();
    renderMetronomeDots();
    updateMetronomeMotion();
    setMetronomeToggleButtonState(false);
    return;
  }

  syncMetronomeInputsToState();
  try {
    const ctx = ensureAudioCtx();
    if (ctx.state !== "running") await ctx.resume();
  } catch (_e) {}
  void preloadAudioSamples();
  state.metronomeRunning = true;
  state.currentBeat = 0;
  state.metronomeDisplayBeat = -1;
  state.currentSubclick = 0;
  state.metronomeTickCount = 0;
  state.metronomeDirection = 1;
  state.metronomeMotionStartTs = performance.now() + metronomeVisualDelayMs();
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

async function refreshTunerInputs() {
  if (!TUNER_FEATURE_ENABLED) return;
  const select = el("tunerInput");
  if (!select) return;
  if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = tr("tuner_no_permission");
    select.appendChild(opt);
    select.disabled = true;
    return;
  }
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const inputs = devices.filter((d) => d.kind === "audioinput");
    const previous = state.tuner.inputDeviceId || select.value || "";
    select.innerHTML = "";
    if (!inputs.length) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = tr("tuner_no_permission");
      select.appendChild(opt);
      select.disabled = true;
      state.tuner.inputDeviceId = "";
      return;
    }
    inputs.forEach((d, idx) => {
      const opt = document.createElement("option");
      opt.value = String(d.deviceId || "");
      opt.textContent = d.label || `${tr("label_tuner_input")} ${idx + 1}`;
      select.appendChild(opt);
    });
    const resolved = inputs.some((d) => String(d.deviceId || "") === previous)
      ? previous
      : String(inputs[0].deviceId || "");
    select.value = resolved;
    state.tuner.inputDeviceId = resolved;
    select.disabled = false;
  } catch (_e) {
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = tr("tuner_no_permission");
    select.appendChild(opt);
    select.disabled = true;
  }
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
  if (!TUNER_FEATURE_ENABLED) return;
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
    const requestedDevice = String(state.tuner.inputDeviceId || "").trim();
    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia(
        requestedDevice
          ? { audio: { deviceId: { exact: requestedDevice } } }
          : { audio: true },
      );
    } catch (_deviceErr) {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }
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
    await refreshTunerInputs();
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

const MIDI_SCREEN_WAKE_MS = 3 * 60 * 1000;

async function acquireMidiScreenWakeLock() {
  if (!("wakeLock" in navigator)) return;
  try {
    if (state.midiScreenWakeLock && !state.midiScreenWakeLock.released) return;
    state.midiScreenWakeLock = await navigator.wakeLock.request("screen");
    state.midiScreenWakeLock.addEventListener("release", () => {
      state.midiScreenWakeLock = null;
    });
  } catch (_e) {
    state.midiScreenWakeLock = null;
  }
}

function releaseMidiScreenWakeLock() {
  const lock = state.midiScreenWakeLock;
  state.midiScreenWakeLock = null;
  if (lock && typeof lock.release === "function") {
    try {
      void lock.release();
    } catch (_e) {
      /* ignore */
    }
  }
}

function cancelMidiScreenWakeLockTimer() {
  if (state.midiScreenWakeLockTimer != null) {
    clearTimeout(state.midiScreenWakeLockTimer);
    state.midiScreenWakeLockTimer = null;
  }
}

function resetMidiScreenWakeLockFully() {
  state.midiScreenWakeLockWanted = false;
  cancelMidiScreenWakeLockTimer();
  releaseMidiScreenWakeLock();
}

async function bumpMidiScreenWakeLockFromMidi() {
  if (state.mode !== "detection" || !state.midi.enabled) return;
  state.midiScreenWakeLockWanted = true;
  await acquireMidiScreenWakeLock();
  cancelMidiScreenWakeLockTimer();
  state.midiScreenWakeLockTimer = setTimeout(() => {
    state.midiScreenWakeLockTimer = null;
    state.midiScreenWakeLockWanted = false;
    releaseMidiScreenWakeLock();
  }, MIDI_SCREEN_WAKE_MS);
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
    void bumpMidiScreenWakeLockFromMidi();
    return;
  }

  if (state.mode === "interval_detection") {
    if (isNoteOn) {
      intervalAddNote(note);
      if (state.midiInputSoundEnabled) startHeldMidiInputNote(note, "piano");
      refreshIntervalResult();
    } else {
      stopHeldMidiInputNote(note);
    }
    void bumpMidiScreenWakeLockFromMidi();
    return;
  }

  if (state.mode === "metronome") {
    if (isNoteOn) {
      state.activeMidiLiveNotes.add(note);
      if (state.midiInputSoundEnabled) startHeldMidiInputNote(note, "piano");
    } else {
      state.activeMidiLiveNotes.delete(note);
      stopHeldMidiInputNote(note);
    }
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
    if (state.mode === "interval_detection") refreshIntervalResult();
    if (state.mode === "metronome") renderInstrument();
    resetMidiScreenWakeLockFully();
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
  const helpToggle = el("helpToggle");
  if (helpToggle) {
    helpToggle.addEventListener("click", () => {
      setHelpActive(!state.help.active);
    });
  }
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
  const feedbackOpenBtn = el("feedbackOpenBtn");
  if (feedbackOpenBtn) {
    feedbackOpenBtn.addEventListener("click", () => {
      showFeedbackModal();
    });
  }
  const downloadsOpenBtn = el("downloadsOpenBtn");
  if (downloadsOpenBtn) {
    downloadsOpenBtn.addEventListener("click", () => {
      showDownloadsModal();
    });
  }
  const feedbackCloseBtn = el("feedbackCloseBtn");
  if (feedbackCloseBtn) {
    feedbackCloseBtn.addEventListener("click", () => {
      hideFeedbackModal();
    });
  }
  const downloadsCloseBtn = el("downloadsCloseBtn");
  if (downloadsCloseBtn) {
    downloadsCloseBtn.addEventListener("click", () => {
      hideDownloadsModal();
    });
  }
  const feedbackModal = el("feedbackModal");
  if (feedbackModal) {
    feedbackModal.addEventListener("click", (event) => {
      if (event.target === feedbackModal) hideFeedbackModal();
    });
  }
  const downloadsModal = el("downloadsModal");
  if (downloadsModal) {
    downloadsModal.addEventListener("click", (event) => {
      if (event.target === downloadsModal) hideDownloadsModal();
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
    applySeoMeta();
    renderInstrument();
    if (state.mode === "detection") await runDetection();
    if (state.mode === "generation" && state.generatedChord) await runGenerateChord();
    if (state.mode === "circle_fifths" && state.generatedChord) await runGenerateChordCircle();
    if (state.mode === "scales" && state.generatedScale) await runGenerateScale();
    renderStaff();
  });

  el("accidental").addEventListener("change", async (e) => {
    state.accidental = e.target.value;
    await loadMeta();
    renderInstrument();
    if (state.mode === "detection") await runDetection();
    if (state.mode === "generation" && state.generatedChord) await runGenerateChord();
    if (state.mode === "circle_fifths" && state.generatedChord) await runGenerateChordCircle();
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
  const toggleMidiInputSound = async () => {
    state.midiInputSoundEnabled = !state.midiInputSoundEnabled;
    if (state.midiInputSoundEnabled) {
      try {
        const ctx = ensureAudioCtx();
        if (ctx.state !== "running") await ctx.resume();
      } catch (_e) {}
    }
    if (!state.midiInputSoundEnabled) stopAllHeldMidiInputNotes();
    refreshMidiInputSoundToggleButton();
  };
  if (detectMidiSoundToggle) detectMidiSoundToggle.addEventListener("click", toggleMidiInputSound);
  const metroMidiSoundToggle = el("metroMidiSoundToggle");
  if (metroMidiSoundToggle) metroMidiSoundToggle.addEventListener("click", toggleMidiInputSound);
  const intervalMidiSoundToggle = el("intervalMidiSoundToggle");
  if (intervalMidiSoundToggle) intervalMidiSoundToggle.addEventListener("click", toggleMidiInputSound);

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

  el("intervalClear").addEventListener("click", () => {
    state.intervalPlayGeneration++;
    state.intervalPlayingNote = null;
    state.intervalPlayingIdx = null;
    state.intervalMelodyActive = false;
    stopAllHeldInputNotes();
    stopAllHeldMidiInputNotes();
    state.intervalNotes = [];
    refreshIntervalResult();
  });

  bindImmediatePress(el("intervalPlayReverse"), () => {
    if (state.intervalNotes.length < 2) return;
    playIntervalNoteSequence([...state.intervalNotes].sort((a, b) => b - a), 500);
  }, { highlightWhilePressed: true });

  bindImmediatePress(el("intervalPlay"), () => {
    if (state.intervalMelodyActive) {
      const melodyNotes = getIntervalMelodyNotes();
      if (!melodyNotes.length) return;
      const sem = getIntervalSemitones();
      const melodyDurs = sem != null ? (INTERVAL_MELODIES[sem]?.durations || null) : null;
      playIntervalNoteSequence(melodyNotes, 420, null, melodyDurs);
    } else {
      if (state.intervalNotes.length < 2) return;
      playIntervalNoteSequence([...state.intervalNotes].sort((a, b) => a - b), 500);
    }
  }, { highlightWhilePressed: true });

  const intervalRecuerdaBtn = el("intervalRecuerdaBtn");
  if (intervalRecuerdaBtn) {
    intervalRecuerdaBtn.addEventListener("click", () => {
      if (state.intervalNotes.length < 2) return;
      if (!INTERVAL_MELODIES[getIntervalSemitones()]) return;
      state.intervalMelodyActive = !state.intervalMelodyActive;
      if (!state.intervalMelodyActive) {
        state.intervalPlayGeneration++;
        state.intervalPlayingNote = null;
        state.intervalPlayingIdx = null;
        refreshIntervalButtonsState();
        renderInstrument();
        renderStaff();
      } else {
        refreshIntervalButtonsState();
        renderInstrument();
        renderStaff();
        const mn = getIntervalMelodyNotes();
        const semAuto = getIntervalSemitones();
        const mdAuto = semAuto != null ? (INTERVAL_MELODIES[semAuto]?.durations || null) : null;
        playIntervalNoteSequence(mn, 420, null, mdAuto);
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !el("downloadsModal")?.classList.contains("hidden")) {
      hideDownloadsModal();
      return;
    }
    if (event.key === "Escape" && !el("feedbackModal")?.classList.contains("hidden")) {
      hideFeedbackModal();
      return;
    }
    if (event.key === "Escape" && state.help.active) {
      setHelpActive(false);
      return;
    }
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

  bindCircleFifthsCanvas();
  const circlePlayBtn = el("circlePlay");
  if (circlePlayBtn) {
    bindImmediatePress(circlePlayBtn, () => {
      if (!state.generatedChord || state.mode !== "circle_fifths") return;
      const notes = getGenerationBaseNotes();
      if (!notes.length) return;
      playChordMidi(notes, { instrument: state.instrument === "guitar" ? "guitar" : "piano" });
    }, {
      highlightWhilePressed: true,
      onPress: () => {
        if (!state.generatedChord || state.mode !== "circle_fifths") return;
        const notes = getGenerationBaseNotes();
        if (!notes.length) return;
        startHeldChord(notes, state.instrument === "guitar" ? "guitar" : "piano");
      },
      onRelease: () => {
        stopHeldChord();
      },
    });
  }

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
  el("metroVolume").addEventListener("input", () => {
    refreshMetronomeVolumeInfo();
  });
  const scaleMetroVolume = el("scaleMetroVolume");
  if (scaleMetroVolume) {
    scaleMetroVolume.addEventListener("input", () => {
      refreshMetronomeVolumeInfo();
    });
  }

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

  if (TUNER_FEATURE_ENABLED) {
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
    const tunerInput = el("tunerInput");
    if (tunerInput) {
      tunerInput.addEventListener("change", async (e) => {
        state.tuner.inputDeviceId = String(e.target.value || "");
        if (state.tuner.running) {
          await toggleTuner();
          await toggleTuner();
        }
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
  } else {
    const panelTuner = el("panelTuner");
    if (panelTuner) panelTuner.classList.add("hidden");
  }

  window.addEventListener("resize", () => {
    if (activeModeSupportsStaff()) renderStaff();
    if (state.mode === "circle_fifths") scheduleCircleFifthsLayout();
    if (TUNER_FEATURE_ENABLED && state.mode === "tuner") renderTunerSpectrumPanel();
    if (state.help.active) refreshHelpOverlay();
  });
  window.addEventListener("scroll", () => {
    if (state.help.active) refreshHelpOverlay();
  }, true);
  window.addEventListener("blur", () => {
    stopHeldChord();
    stopAllHeldInputNotes();
    if (state.help.active) setHelpActive(false);
  });

  el("metroToggle").addEventListener("click", toggleMetronome);
  if (TUNER_FEATURE_ENABLED) {
    el("tunerToggle").addEventListener("click", toggleTuner);
  }
  const feedbackForm = el("feedbackForm");
  if (feedbackForm) feedbackForm.addEventListener("submit", submitFeedbackForm);

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && state.midiScreenWakeLockWanted) {
      void acquireMidiScreenWakeLock();
    }
  });
}

async function main() {
  initStaffAssets();
  void preloadAudioSamples();
  bindEvents();
  const accInit = el("accidental");
  if (accInit && (accInit.value === "flat" || accInit.value === "sharp")) state.accidental = accInit.value;
  applyTranslations();
  syncLeftPanelHeader();
  if (el("scaleBpm") && el("bpm")) {
    el("scaleBpm").value = el("bpm").value;
    el("scaleBpmValue").textContent = `${el("scaleBpm").value} ${tempoUnitLabel()}`;
  }
  refreshMetronomeTempoInfo();
  if (el("metroMotionDot")) updateMetronomeMotion();
  renderMetronomeTimerDisplay();
  setMode("detection");
  renderMetronomeDots();
  renderStaff();

  try {
    await loadMeta();
  } catch (err) {
    console.warn("Failed to load /api/meta during startup:", err);
  }

  if (TUNER_FEATURE_ENABLED) {
    try {
      await refreshTunerInputs();
    } catch (err) {
      console.warn("Failed to refresh tuner inputs during startup:", err);
    }
  }

  applyTranslations();
  applySeoMeta();

  try {
    await runGenerateChord();
  } catch (err) {
    console.warn("Failed to run initial chord generation:", err);
  }
  try {
    await runGenerateScale();
  } catch (err) {
    console.warn("Failed to run initial scale generation:", err);
  }
  try {
    await runDetection();
  } catch (err) {
    console.warn("Failed to run initial detection:", err);
  }

  refreshDetectionButtonsState();
  refreshIntervalButtonsState();
  setMode("detection");
  showMidiStartupModal();
  renderMetronomeDots();
  renderStaff();
}

main();
