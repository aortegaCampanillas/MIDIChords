part of 'main.dart';

extension _HomeScreenHelp on _HomeScreenState {
  GlobalKey _helpAnchorKey(String id) =>
      _helpAnchors.putIfAbsent(id, () => GlobalKey(debugLabel: 'help_$id'));

  Widget _helpAnchor(String id, Widget child) {
    return RepaintBoundary(key: _helpAnchorKey(id), child: child);
  }

  Widget _helpFixedHeightAnchor(String id, Widget child, {double height = 56}) {
    return SizedBox(key: _helpAnchorKey(id), height: height, child: child);
  }

  List<_HelpStep> _helpStepsForCurrentMode() {
    final modeSelectBodyEs = _kEnableMobileTuner
        ? 'Aqui cambias entre deteccion de notas, deteccion de acordes, deteccion de intervalos, '
              'generacion, practica de intervalos, circulo de quintas, escalas, metronomo y afinador.'
        : 'Aqui cambias entre deteccion de notas, deteccion de acordes, deteccion de intervalos, '
              'generacion, practica de intervalos, circulo de quintas, escalas y metronomo.';
    final modeSelectBodyEn = _kEnableMobileTuner
        ? 'Switch between note detection, chord detection, interval detection, generation, '
              'interval practice, circle of fifths, scales, metronome, and tuner here.'
        : 'Switch between note detection, chord detection, interval detection, generation, '
              'interval practice, circle of fifths, scales, and metronome here.';
    final common = <_HelpStep>[
      _HelpStep(
        id: 'mode_select',
        titleEs: 'Selector de modo',
        titleEn: 'Mode selector',
        bodyEs: modeSelectBodyEs,
        bodyEn: modeSelectBodyEn,
        highlightPadding: 4,
      ),
      _HelpStep(
        id: 'midi_toggle',
        titleEs: 'Entrada MIDI',
        titleEn: 'MIDI input',
        bodyEs:
            'Activa o desactiva la entrada de un teclado o controlador MIDI.',
        bodyEn: 'Enable or disable input from a MIDI keyboard or controller.',
        highlightPadding: -3,
      ),
      _HelpStep(
        id: 'sound_output',
        titleEs: 'Salida Audio/MIDI',
        titleEn: 'Audio/MIDI output',
        bodyEs:
            'Con MIDI activado, elige si las notas suenan con el audio local '
            'de la app o se envían al dispositivo MIDI conectado.',
        bodyEn:
            'With MIDI enabled, choose whether notes play through the app\'s '
            'local audio or get sent to the connected MIDI device.',
        highlightPadding: -3,
      ),
      _HelpStep(
        id: 'accidental',
        titleEs: 'Sostenidos o bemoles',
        titleEn: 'Sharps or flats',
        bodyEs:
            'Elige si prefieres nombres de notas con sostenidos (#) o bemoles (b).',
        bodyEn:
            'Choose whether note names should prefer sharps (#) or flats (b).',
        highlightPadding: -3,
      ),
      _HelpStep(
        id: 'settings',
        titleEs: 'Configuracion',
        titleEn: 'Settings',
        bodyEs:
            'Abre el panel de configuracion general, incluido el idioma de la interfaz.',
        bodyEn:
            'Open the general settings panel, including interface language.',
        side: _HelpCalloutSide.left,
        highlightPadding: -2,
      ),
    ];
    final modeSpecific = switch (_tabIndex) {
      9 => <_HelpStep>[
        _HelpStep(
          id: 'interval_practice_staff',
          titleEs: 'Pentagrama del ejercicio',
          titleEn: 'Exercise staff',
          bodyEs:
              'Muestra la primera nota y un interrogante hasta responder; después presenta la corrección con sus colores.',
          bodyEn:
              'Shows the first note and a question mark until you answer; afterwards it displays the colour-coded correction.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'interval_practice_start_stop',
          titleEs: 'Iniciar o parar',
          titleEn: 'Start or stop',
          bodyEs: 'Inicia una prueba nueva o termina la prueba actual.',
          bodyEn: 'Starts a new test or ends the current test.',
        ),
        _HelpStep(
          id: 'interval_practice_repeat',
          titleEs: 'Repetir',
          titleEn: 'Repeat',
          bodyEs:
              'Vuelve a escuchar el intervalo actual o la corrección de una respuesta.',
          bodyEn: 'Plays the current interval or an answer correction again.',
        ),
        _HelpStep(
          id: 'interval_practice_next',
          titleEs: 'Siguiente',
          titleEn: 'Next',
          bodyEs: 'Prepara y reproduce el siguiente intervalo del ejercicio.',
          bodyEn: 'Prepares and plays the next interval in the exercise.',
        ),
        _HelpStep(
          id: 'interval_practice_help',
          titleEs: 'Ayuda del ejercicio',
          titleEn: 'Exercise help',
          bodyEs: 'Abre una explicación general del proceso de práctica.',
          bodyEn: 'Opens a general explanation of the practice process.',
        ),
        _HelpStep(
          id: 'interval_practice_random_tonic',
          titleEs: 'Tónica aleatoria',
          titleEn: 'Random tonic',
          bodyEs: 'Varía la primera nota entre los ejercicios.',
          bodyEn: 'Varies the first note between exercises.',
        ),
        _HelpStep(
          id: 'interval_practice_ascending',
          titleEs: 'Solo ascendentes',
          titleEn: 'Ascending only',
          bodyEs:
              'Limita la práctica a intervalos ascendentes; al quitarlo también pueden aparecer descendentes.',
          bodyEn:
              'Limits practice to ascending intervals; clearing it also allows descending intervals.',
        ),
        _HelpStep(
          id: 'interval_practice_repetitions',
          titleEs: 'Repeticiones',
          titleEn: 'Repetitions',
          bodyEs: 'Define el número de ejercicios de la prueba.',
          bodyEn: 'Sets the number of exercises in the test.',
        ),
        _HelpStep(
          id: 'interval_practice_filter',
          titleEs: 'Filtrar',
          titleEn: 'Filter',
          bodyEs:
              'Selecciona las notas que pueden aparecer como segunda nota del intervalo.',
          bodyEn:
              'Selects the notes that may appear as the interval’s second note.',
        ),
        _HelpStep(
          id: 'interval_practice_playback_mode',
          titleEs: 'Melódico o armónico',
          titleEn: 'Melodic or harmonic',
          bodyEs:
              'Elige si las dos notas suenan sucesivamente o al mismo tiempo.',
          bodyEn:
              'Chooses whether the two notes sound successively or together.',
        ),
        _HelpStep(
          id: 'interval_practice_previous_result',
          titleEs: 'Resultado anterior',
          titleEn: 'Previous result',
          bodyEs: 'Muestra la respuesta anterior de la prueba terminada.',
          bodyEn: 'Shows the previous answer from the completed test.',
        ),
        _HelpStep(
          id: 'interval_practice_next_result',
          titleEs: 'Resultado siguiente',
          titleEn: 'Next result',
          bodyEs: 'Muestra la respuesta siguiente de la prueba terminada.',
          bodyEn: 'Shows the next answer from the completed test.',
        ),
        _HelpStep(
          id: 'interval_practice_result',
          titleEs: 'Resultado',
          titleEn: 'Result',
          bodyEs: 'Muestra los aciertos y el nombre completo del intervalo.',
          bodyEn: 'Shows the score and the interval’s full name.',
        ),
        _HelpStep(
          id: 'interval_practice_table',
          titleEs: 'Tabla de intervalos',
          titleEn: 'Interval table',
          bodyEs:
              'Selecciona aquí el intervalo que has escuchado. Las opciones excluidas por el filtro se muestran deshabilitadas.',
          bodyEn:
              'Select the interval you heard here. Options excluded by the filter appear disabled.',
        ),
        _HelpStep(
          id: 'interval_practice_piano',
          titleEs: 'Piano',
          titleEn: 'Piano',
          bodyEs:
              'Permite responder con la segunda nota y muestra las notas de la corrección mientras se reproducen.',
          bodyEn:
              'Lets you answer with the second note and shows correction notes while they play.',
          side: _HelpCalloutSide.top,
        ),
      ],
      8 => <_HelpStep>[
        _HelpStep(
          id: 'note_detection_staff',
          titleEs: 'Pentagrama',
          titleEn: 'Staff',
          bodyEs:
              'Muestra la última nota en la clave correspondiente, sin armadura y con su alteración escrita directamente.',
          bodyEn:
              'Shows the last note in the appropriate clef, without a key signature and with its accidental written directly.',
        ),
        _HelpStep(
          id: 'note_detection_play_button',
          titleEs: 'Repetir nota',
          titleEn: 'Repeat note',
          bodyEs: 'Repite la última nota mientras mantienes pulsado el botón.',
          bodyEn: 'Repeats the last note while you hold the button down.',
        ),
        _HelpStep(
          id: 'note_detection_clear_button',
          titleEs: 'Limpiar',
          titleEn: 'Clear',
          bodyEs: 'Borra la última nota detectada.',
          bodyEn: 'Clears the last detected note.',
        ),
        _HelpStep(
          id: 'note_detection_details_toggle',
          titleEs: 'Ocultar o mostrar',
          titleEn: 'Hide or show',
          bodyEs:
              'Con fines didácticos, oculta el nombre detectado y las etiquetas del piano para reconocer la nota por ti mismo; vuelve a mostrarlos para comprobarla.',
          bodyEn:
              'For learning purposes, hides the detected name and piano labels so you can identify the note yourself; show them again to check it.',
        ),
        _HelpStep(
          id: 'note_detection_result',
          titleEs: 'Nota detectada',
          titleEn: 'Detected note',
          bodyEs: 'Muestra el nombre de la última nota tocada.',
          bodyEn: 'Shows the name of the last note played.',
        ),
        _HelpStep(
          id: 'note_detection_piano',
          titleEs: 'Piano y MIDI',
          titleEn: 'Piano and MIDI',
          bodyEs:
              'Toca una nota en el piano o mediante MIDI; solo la última queda marcada.',
          bodyEn:
              'Play a note on the piano or via MIDI; only the last one remains highlighted.',
        ),
      ],
      0 => <_HelpStep>[
        _HelpStep(
          id: 'detection_staff',
          titleEs: 'Pentagrama de deteccion',
          titleEn: 'Detection staff',
          bodyEs:
              'Muestra las notas activas, las extras y el resultado detectado.',
          bodyEn: 'Shows active notes, extras, and the detected result.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'detection_controls',
          titleEs: 'Panel de deteccion',
          titleEn: 'Detection panel',
          bodyEs:
              'Aqui se ve el resultado y los controles principales del modo deteccion.',
          bodyEn:
              'This panel contains the current result and main detection controls.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'detection_play_button',
          titleEs: 'Boton reproducir',
          titleEn: 'Play button',
          bodyEs:
              'Reproduce o mantiene sonando las notas detectadas mientras mantienes pulsado.',
          bodyEn:
              'Plays or sustains the detected notes while you keep it pressed.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'detection_variant_theory',
          titleEs: 'Teoría de la variante',
          titleEn: 'Variant theory',
          bodyEs:
              'Abre la fórmula, la explicación teórica y la descripción de la inversión del acorde detectado.',
          bodyEn:
              'Opens the formula, theory explanation, and inversion description for the detected chord.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'detection_clear_button',
          titleEs: 'Boton limpiar',
          titleEn: 'Clear button',
          bodyEs:
              'Borra las notas introducidas y recalcula la deteccion desde cero.',
          bodyEn:
              'Clears the entered notes and recalculates detection from scratch.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'detection_details_toggle',
          titleEs: 'Ocultar o mostrar',
          titleEn: 'Hide or show',
          bodyEs:
              'Con fines didácticos, oculta la información para intentar identificar el acorde por ti mismo y vuelve a mostrarla para comprobar la respuesta.',
          bodyEn:
              'For learning purposes, hide the information to identify the chord yourself, then show it again to check your answer.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'detection_midi_sound_button',
          titleEs: 'Boton MIDI',
          titleEn: 'MIDI button',
          bodyEs:
              'Activa o silencia el sonido local al tocar notas desde MIDI o desde el piano en pantalla.',
          bodyEn:
              'Enables or mutes local sound when you play notes from MIDI or the on-screen piano.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'detection_result_chord',
          titleEs: 'Fila de acorde',
          titleEn: 'Chord row',
          bodyEs: 'Muestra el acorde detectado actualmente.',
          bodyEn: 'Shows the currently detected chord.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'detection_result_notes',
          titleEs: 'Fila de notas',
          titleEn: 'Notes row',
          bodyEs: 'Muestra el listado de notas que participan en el resultado.',
          bodyEn: 'Shows the list of notes that make up the result.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'detection_result_extras',
          titleEs: 'Fila de sobrantes',
          titleEn: 'Extras row',
          bodyEs: 'Muestra las notas que no encajan en el acorde principal.',
          bodyEn: 'Shows notes that do not fit the main chord.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'detection_result_formula',
          titleEs: 'Fila de fórmula',
          titleEn: 'Formula row',
          bodyEs:
              'Grados del acorde respecto a la tónica (p. ej. 1 - 3 - 5). En una inversión se añade entre paréntesis la fórmula de esa inversión.',
          bodyEn:
              "The chord's degrees relative to the tonic (e.g. 1 - 3 - 5). For an inversion, that inversion's formula is added in parentheses.",
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'detection_result_construction',
          titleEs: 'Fila de construcción',
          titleEn: 'Construction row',
          bodyEs:
              'Intervalos apilados entre notas consecutivas del acorde (p. ej. M3 + m3). En una inversión se añade entre paréntesis la construcción de esa inversión.',
          bodyEn:
              "Stacked intervals between consecutive chord notes (e.g. M3 + m3). For an inversion, that inversion's construction is added in parentheses.",
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'detection_instrument',
          titleEs: 'Piano interactivo',
          titleEn: 'Interactive piano',
          bodyEs:
              'Toca en el piano para introducir notas y reflejarlas en el pentagrama.',
          bodyEn: 'Play the piano to enter notes and mirror them on the staff.',
          side: _HelpCalloutSide.top,
        ),
      ],
      1 => <_HelpStep>[
        _HelpStep(
          id: 'generation_staff',
          titleEs: 'Pentagrama del acorde',
          titleEn: 'Chord staff',
          bodyEs:
              'Muestra el acorde generado y resalta lo que estas reproduciendo.',
          bodyEn:
              'Shows the generated chord and highlights what is being played.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'generation_controls',
          titleEs: 'Panel de generacion',
          titleEn: 'Generation panel',
          bodyEs:
              'Configura tonica, tipo e inversion del acorde que quieres generar.',
          bodyEn:
              'Configure root, type, and inversion of the chord you want to generate.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'generation_play_button',
          titleEs: 'Boton reproducir',
          titleEn: 'Play button',
          bodyEs:
              'Reproduce o mantiene sonando el acorde generado mientras mantienes pulsado.',
          bodyEn:
              'Plays or sustains the generated chord while you keep it pressed.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_tonic',
          titleEs: 'Tonica',
          titleEn: 'Tonic',
          bodyEs: 'Aqui eliges la nota base del acorde que quieres generar.',
          bodyEn:
              'Choose the root note of the chord you want to generate here.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_variant',
          titleEs: 'Variante',
          titleEn: 'Variant',
          bodyEs:
              'Define el tipo de acorde, como mayor, menor, disminuido o sus variaciones.',
          bodyEn:
              'Defines the chord type, such as major, minor, diminished, or its variations.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_variant_theory',
          titleEs: 'Teoría de la variante',
          titleEn: 'Variant theory',
          bodyEs:
              'Abre la fórmula, la explicación teórica y la descripción de la inversión seleccionada.',
          bodyEn:
              'Opens the formula, theory explanation, and description of the selected inversion.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_inversion',
          titleEs: 'Inversion',
          titleEn: 'Inversion',
          bodyEs:
              'Cambia el orden de las notas del acorde manteniendo su misma funcion armonica.',
          bodyEn:
              'Changes the order of chord notes while keeping the same harmonic function.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_hand',
          titleEs: 'Mano',
          titleEn: 'Hand',
          bodyEs:
              'Elige si el acorde se muestra y suena con la mano izquierda, la derecha o ambas.',
          bodyEn:
              'Choose whether the chord is shown and played with the left hand, right hand, or both.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_result_chord',
          titleEs: 'Resultado del acorde',
          titleEn: 'Chord result',
          bodyEs: 'Muestra el nombre del acorde generado actualmente.',
          bodyEn: 'Shows the currently generated chord name.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'generation_result_notes',
          titleEs: 'Notas del acorde',
          titleEn: 'Chord notes',
          bodyEs: 'Muestra las notas que forman el acorde generado.',
          bodyEn: 'Shows the notes that make up the generated chord.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'generation_result_formula',
          titleEs: 'Fórmula del acorde',
          titleEn: 'Chord formula',
          bodyEs:
              'Grados del acorde respecto a la tónica (p. ej. 1 - 3 - 5). En una inversión se añade entre paréntesis la fórmula de esa inversión.',
          bodyEn:
              "The chord's degrees relative to the tonic (e.g. 1 - 3 - 5). For an inversion, that inversion's formula is added in parentheses.",
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'generation_result_construction',
          titleEs: 'Construcción del acorde',
          titleEn: 'Chord construction',
          bodyEs:
              'Intervalos apilados entre notas consecutivas del acorde (p. ej. M3 + m3). En una inversión se añade entre paréntesis la construcción de esa inversión.',
          bodyEn:
              "Stacked intervals between consecutive chord notes (e.g. M3 + m3). For an inversion, that inversion's construction is added in parentheses.",
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'generation_instrument_piano',
          titleEs: 'Boton Piano',
          titleEn: 'Piano button',
          bodyEs: 'Cambia la vista y la reproduccion del acorde al piano.',
          bodyEn: 'Switches the chord view and playback to piano.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_instrument_guitar',
          titleEs: 'Boton Guitarra',
          titleEn: 'Guitar button',
          bodyEs: 'Cambia la vista y la reproduccion del acorde a la guitarra.',
          bodyEn: 'Switches the chord view and playback to guitar.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_guitar_hand',
          titleEs: 'Mano de la guitarra',
          titleEn: 'Guitar handedness',
          bodyEs:
              'Ajusta la visualizacion para diestro o zurdo en la guitarra.',
          bodyEn: 'Adjusts the guitar display for right- or left-handed view.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_guitar_variant',
          titleEs: 'Variantes de acorde',
          titleEn: 'Chord variations',
          bodyEs:
              'Permite recorrer distintas posiciones o variantes del mismo acorde en la guitarra.',
          bodyEn:
              'Lets you cycle through different positions or variants of the same chord on guitar.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'generation_instrument',
          titleEs: 'Piano o guitarra',
          titleEn: 'Piano or guitar',
          bodyEs:
              'Muestra el acorde generado en el instrumento seleccionado. Usa el boton de reproduccion para escucharlo.',
          bodyEn:
              'Shows the generated chord on the selected instrument. Use the play button to hear it.',
          side: _HelpCalloutSide.top,
        ),
      ],
      2 => <_HelpStep>[
        _HelpStep(
          id: 'circle_staff',
          titleEs: 'Pentagrama',
          titleEn: 'Staff',
          bodyEs:
              'Muestra el acorde generado desde el circulo segun la tonalidad elegida.',
          bodyEn:
              'Shows the chord generated from the circle for the selected key.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'circle_canvas',
          titleEs: 'Circulo de quintas',
          titleEn: 'Circle of fifths',
          bodyEs:
              'Toca el anillo: elige un acorde diatónico (triada sobre un '
              'grado de la escala); no cambia la tónica. Mantén pulsado: '
              'fija la tónica y la tonalidad (mayor en el exterior, menor '
              'natural relativa en el interior; misma armadura).',
          bodyEn:
              'Tap: choose a diatonic chord—a triad on a scale degree '
              '(major, minor, or diminished); does not change the tonic. '
              'Long-press: sets the tonic and key (major on the outer '
              'ring, relative natural minor on the inner; same key '
              'signature).',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'circle_play',
          titleEs: 'Reproducir',
          titleEn: 'Play',
          bodyEs:
              'Mantén pulsado el botón de reproducción para oír el acorde en el instrumento.',
          bodyEn: 'Hold the play button to hear the chord on the instrument.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'circle_instrument_piano_btn',
          titleEs: 'Piano',
          titleEn: 'Piano',
          bodyEs: 'Muestra el teclado de piano en el círculo de quintas.',
          bodyEn: 'Show the piano keyboard in the circle of fifths.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'circle_instrument_guitar_btn',
          titleEs: 'Guitarra',
          titleEn: 'Guitar',
          bodyEs: 'Muestra el diapasón de guitarra en el círculo de quintas.',
          bodyEn: 'Show the guitar fretboard in the circle of fifths.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'circle_instrument',
          titleEs: 'Instrumento del círculo',
          titleEn: 'Circle instrument',
          bodyEs:
              'Al tocar una nota se resalta en el círculo la tonalidad correspondiente.',
          bodyEn:
              'Playing a note highlights the corresponding key in the circle.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'circle_guitar_hand',
          titleEs: 'Mano de la guitarra',
          titleEn: 'Guitar handedness',
          bodyEs:
              'Ajusta la visualizacion para diestro o zurdo en la guitarra.',
          bodyEn: 'Adjusts the guitar display for right- or left-handed view.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'circle_guitar_variant',
          titleEs: 'Variantes de acorde',
          titleEn: 'Chord variations',
          bodyEs:
              'Permite recorrer distintas posiciones o variantes del mismo acorde en la guitarra.',
          bodyEn:
              'Lets you cycle through different positions or variants of the same chord on guitar.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
      ],
      3 => <_HelpStep>[
        _HelpStep(
          id: 'scales_staff',
          titleEs: 'Pentagrama de escala',
          titleEn: 'Scale staff',
          bodyEs:
              'Muestra las notas de la escala y la nota actual durante la reproduccion.',
          bodyEn: 'Shows scale notes and the current note during playback.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'scales_controls',
          titleEs: 'Panel de escalas',
          titleEn: 'Scales panel',
          bodyEs:
              'Configura tonica, tipo, velocidad y reproduccion de la escala.',
          bodyEn: 'Configure tonic, type, speed, and playback of the scale.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'scales_tonic',
          titleEs: 'Tonica',
          titleEn: 'Tonic',
          bodyEs: 'Aqui eliges la nota base de la escala.',
          bodyEn: 'Choose the root note of the scale here.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_accidental',
          titleEs: 'Alteración y armadura',
          titleEn: 'Accidental and key signature',
          bodyEs:
              'Elige la alteración de la tónica. La armadura del pentagrama se actualiza para la escala seleccionada.',
          bodyEn:
              'Choose the tonic accidental. The staff key signature updates for the selected scale.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_pattern',
          titleEs: 'Tipo de escala',
          titleEn: 'Scale type',
          bodyEs:
              'Selecciona el patron o modo de escala que quieres estudiar o reproducir.',
          bodyEn: 'Select the scale pattern or mode you want to study or play.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_filter',
          titleEs: 'Básicas / Todas',
          titleEn: 'Basic / All',
          bodyEs:
              'Alterna entre el conjunto de escalas más habituales (Básicas) '
              'y la lista completa (Todas).',
          bodyEn:
              'Toggle between the most common scales (Basic) and the full '
              'list (All).',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_play_button',
          titleEs: 'Boton reproducir',
          titleEn: 'Play button',
          bodyEs: 'Inicia o detiene la reproduccion automatica de la escala.',
          bodyEn: 'Starts or stops automatic scale playback.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_metronome_only',
          titleEs: 'Modo metrico',
          titleEn: 'Metronome mode',
          bodyEs:
              'Activa un modo simplificado para practicar la escala con pulso y tempo.',
          bodyEn:
              'Enables a simplified mode to practice the scale with pulse and tempo.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_volume',
          titleEs: 'Volumen',
          titleEn: 'Volume',
          bodyEs:
              'Controla el volumen cuando el modo metrico de escalas esta activo.',
          bodyEn: 'Controls volume when scale metronome mode is active.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_bpm',
          titleEs: 'Velocidad',
          titleEn: 'Speed',
          bodyEs: 'Ajusta la velocidad de reproduccion de la escala en BPM.',
          bodyEn: 'Adjusts scale playback speed in BPM.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_result_scale',
          titleEs: 'Resultado de la escala',
          titleEn: 'Scale result',
          bodyEs: 'Muestra la escala seleccionada actualmente.',
          bodyEn: 'Shows the currently selected scale.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'scales_result_notes',
          titleEs: 'Notas de la escala',
          titleEn: 'Scale notes',
          bodyEs: 'Muestra las notas que forman la escala.',
          bodyEn: 'Shows the notes that make up the scale.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'scales_result_formula',
          titleEs: 'Fórmula de la escala',
          titleEn: 'Scale formula',
          bodyEs:
              'Grados de la escala respecto a la tónica (p. ej. 1 2 3 4 5 6 7 en Do jónico).',
          bodyEn:
              "The scale's degrees relative to the tonic (e.g. 1 2 3 4 5 6 7 for C Ionian).",
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'scales_result_pattern',
          titleEs: 'Patrón de la escala',
          titleEn: 'Scale pattern',
          bodyEs:
              'Pasos entre notas consecutivas en tonos (T) y semitonos (S), p. ej. T T S T T T S en Do jónico.',
          bodyEn:
              'Steps between consecutive notes in whole tones (T) and semitones (S), e.g. T T S T T T S for C Ionian.',
          side: _HelpCalloutSide.left,
          highlightPadding: -2,
        ),
        _HelpStep(
          id: 'scales_instrument_piano',
          titleEs: 'Boton Piano',
          titleEn: 'Piano button',
          bodyEs: 'Cambia la vista de la escala al piano.',
          bodyEn: 'Switches the scale view to piano.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_instrument_guitar',
          titleEs: 'Boton Guitarra',
          titleEn: 'Guitar button',
          bodyEs: 'Cambia la vista de la escala a la guitarra.',
          bodyEn: 'Switches the scale view to guitar.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_guitar_hand',
          titleEs: 'Mano de la guitarra',
          titleEn: 'Guitar handedness',
          bodyEs:
              'Ajusta la visualizacion de la guitarra para diestro o zurdo.',
          bodyEn: 'Adjusts the guitar display for right- or left-handed view.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_instrument',
          titleEs: 'Instrumento de escala',
          titleEn: 'Scale instrument',
          bodyEs:
              'Permite tocar y seguir visualmente la escala en piano o guitarra.',
          bodyEn:
              'Lets you play and visually follow the scale on piano or guitar.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'scales_octaves',
          titleEs: 'Número de octavas',
          titleEn: 'Number of octaves',
          bodyEs:
              'Muestra la escala en 1, 2 o 3 octavas sobre el teclado. Con 2 octavas se añade la octava inferior; con 3 también la superior.',
          bodyEn:
              'Displays the scale over 1, 2, or 3 octaves on the keyboard. With 2 octaves a lower octave is added; with 3 also an upper one.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'scales_fingering',
          titleEs: 'Digitación',
          titleEn: 'Fingering',
          bodyEs:
              'Selecciona la mano para ver la numeración de los dedos encima (subida) y debajo (bajada) del teclado. Los números en rojo/azul oscuro indican un cruce de dedos.',
          bodyEn:
              'Select a hand to see finger numbers above (ascending) and below (descending) the keyboard. Numbers in dark red/blue indicate a finger crossing.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
      ],
      4 => <_HelpStep>[
        _HelpStep(
          id: 'metronome_bead_row',
          titleEs: 'Bolas de pulso',
          titleEn: 'Beat balls',
          bodyEs:
              'Muestran los pulsos del compas y resaltan el pulso actual mientras corre el metronomo.',
          bodyEn:
              'They show the beats of the bar and highlight the current beat while the metronome runs.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_motion_axis',
          titleEs: 'Eje de movimiento',
          titleEn: 'Motion axis',
          bodyEs:
              'Marca el recorrido de la bola roja que acompasa visualmente el pulso.',
          bodyEn:
              'Marks the path of the red ball that visually follows the pulse.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_timer_display',
          titleEs: 'Zona del temporizador',
          titleEn: 'Timer area',
          bodyEs:
              'Aqui aparece la cuenta atras cuando activas el temporizador del metronomo.',
          bodyEn:
              'The countdown appears here when you enable the metronome timer.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_toggle_left',
          titleEs: 'Boton del metronomo',
          titleEn: 'Metronome button',
          bodyEs:
              'Inicia o detiene el metronomo directamente desde la vista principal.',
          bodyEn: 'Starts or stops the metronome directly from the main view.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_controls',
          titleEs: 'Panel del metronomo',
          titleEn: 'Metronome panel',
          bodyEs:
              'Aqui ajustas tempo, compas, subdivision, acento y temporizador.',
          bodyEn: 'Adjust tempo, meter, subdivision, accent, and timer here.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'metronome_volume',
          titleEs: 'Volumen',
          titleEn: 'Volume',
          bodyEs: 'Controla el volumen general del metronomo.',
          bodyEn: 'Controls the overall metronome volume.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_tempo',
          titleEs: 'Tempo',
          titleEn: 'Tempo',
          bodyEs: 'Ajusta la velocidad del metronomo en BPM.',
          bodyEn: 'Adjusts metronome speed in BPM.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_beats',
          titleEs: 'Pulsos por compas',
          titleEn: 'Beats per bar',
          bodyEs: 'Define cuantas pulsaciones tiene cada compas.',
          bodyEn: 'Defines how many beats there are in each bar.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_subdivision',
          titleEs: 'Subdivision',
          titleEn: 'Subdivision',
          bodyEs: 'Elige cuantas subdivisiones sonaran dentro de cada pulso.',
          bodyEn: 'Choose how many subdivisions sound within each beat.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_accent',
          titleEs: 'Acento',
          titleEn: 'Accent',
          bodyEs:
              'Activa o desactiva el acento del primer pulso de cada compas.',
          bodyEn:
              'Enables or disables the accent on the first beat of each bar.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_timer',
          titleEs: 'Temporizador',
          titleEn: 'Timer',
          bodyEs:
              'Permite limitar la duracion del metronomo con minutos y segundos.',
          bodyEn: 'Lets you limit metronome duration with minutes and seconds.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'metronome_instrument',
          titleEs: 'Piano del metronomo',
          titleEn: 'Metronome piano',
          bodyEs:
              'Mientras corre el metronomo puedes seguir viendo y tocando notas en el piano.',
          bodyEn:
              'While the metronome runs you can still view and play notes on the piano.',
          side: _HelpCalloutSide.top,
        ),
      ],
      5 => <_HelpStep>[
        _HelpStep(
          id: 'interval_detection_staff',
          titleEs: 'Pentagrama de intervalos',
          titleEn: 'Interval staff',
          bodyEs: 'Muestra las dos últimas notas pulsadas.',
          bodyEn: 'Shows the two latest pressed notes.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'interval_notes_row',
          titleEs: 'Notas',
          titleEn: 'Notes',
          bodyEs: 'Las dos últimas notas pulsadas.',
          bodyEn: 'The two latest pressed notes.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_name_row',
          titleEs: 'Intervalo',
          titleEn: 'Interval',
          bodyEs:
              'Nombre del intervalo detectado seguido de sus nombres alternativos.',
          bodyEn:
              'Name of the detected interval followed by its alternative names.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_semitones_row',
          titleEs: 'Semitonos',
          titleEn: 'Semitones',
          bodyEs: 'Número de semitonos entre las dos notas.',
          bodyEn: 'Number of semitones between the two notes.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_melody_row',
          titleEs: 'Canción mnemotécnica',
          titleEn: 'Mnemonic song',
          bodyEs:
              'Pulsa el nombre para activar la melodía de referencia y reproducirla.',
          bodyEn: 'Tap the name to activate the reference melody and play it.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_play_btn',
          titleEs: 'Reproducir',
          titleEn: 'Play',
          bodyEs: 'Reproduce las dos notas del intervalo de forma melódica.',
          bodyEn: 'Play the two interval notes melodically.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_play_reverse_btn',
          titleEs: 'Descendente',
          titleEn: 'Reverse',
          bodyEs:
              'Reproduce el intervalo de forma descendente (nota alta → nota baja).',
          bodyEn: 'Play the interval descending (high note → low note).',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_clear_btn',
          titleEs: 'Limpiar',
          titleEn: 'Clear',
          bodyEs: 'Limpia las notas activas para comenzar de nuevo.',
          bodyEn: 'Clear active notes and start over.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_details_toggle',
          titleEs: 'Ocultar o mostrar',
          titleEn: 'Hide or show',
          bodyEs:
              'Con fines didácticos, oculta la información para intentar identificar el intervalo por ti mismo y vuelve a mostrarla para comprobar la respuesta.',
          bodyEn:
              'For learning purposes, hide the information to identify the interval yourself, then show it again to check your answer.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_detection_instrument',
          titleEs: 'Teclado interactivo',
          titleEn: 'Interactive keyboard',
          bodyEs:
              'Pulsa notas para detectar intervalos (también vía MIDI). '
              'Cada pulsación añade la nota al par; la más antigua se '
              'descarta automáticamente.',
          bodyEn:
              'Press notes to detect intervals (also via MIDI). Each '
              'press adds a note to the pair; the oldest is '
              'automatically discarded.',
          side: _HelpCalloutSide.top,
        ),
      ],
      7 => <_HelpStep>[
        _HelpStep(
          id: 'interval_generation_staff',
          titleEs: 'Pentagrama del intervalo generado',
          titleEn: 'Generated interval staff',
          bodyEs:
              'Pentagrama del intervalo generado: muestra las dos notas elegidas en la tabla. Pulsa una para previsualizarla y resaltarla en el piano o la guitarra.',
          bodyEn:
              'Generated interval staff: shows the two notes selected in the table. Tap one to preview it and highlight it on the piano or guitar.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'interval_generation_instrument_piano',
          titleEs: 'Botón Piano',
          titleEn: 'Piano button',
          bodyEs: 'Cambia la representación del instrumento a teclado.',
          bodyEn: 'Switch the instrument representation to piano.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'interval_generation_instrument_guitar',
          titleEs: 'Botón Guitarra',
          titleEn: 'Guitar button',
          bodyEs: 'Cambia la representación del instrumento a guitarra.',
          bodyEn: 'Switch the instrument representation to guitar.',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'interval_generation_guitar_hand',
          titleEs: 'Orientación de la guitarra',
          titleEn: 'Guitar handedness',
          bodyEs: 'Ajusta la orientación de la guitarra (diestro/zurdo).',
          bodyEn: 'Set guitar orientation (right-handed/left-handed).',
          side: _HelpCalloutSide.top,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'interval_generation_root',
          titleEs: 'Tónica',
          titleEn: 'Tonic',
          bodyEs:
              'Tónica desde la que se genera el intervalo elegido en la tabla.',
          bodyEn: 'Tonic from which the chosen table interval is generated.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_playback_mode',
          titleEs: 'Melódico o armónico',
          titleEn: 'Melodic or harmonic',
          bodyEs:
              'Elige si las notas del intervalo suenan una después de otra o simultáneamente.',
          bodyEn:
              'Choose whether the interval notes sound one after another or simultaneously.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_play_reverse',
          titleEs: 'Reproducción descendente',
          titleEn: 'Descending playback',
          bodyEs:
              'Reproduce el intervalo de forma descendente (nota alta → nota baja) y fija ese patrón para las reproducciones posteriores.',
          bodyEn:
              'Play the interval descending (high note → low note) and set that pattern for subsequent playback.',
          side: _HelpCalloutSide.bottom,
        ),
        _HelpStep(
          id: 'interval_generation_play',
          titleEs: 'Reproducción ascendente',
          titleEn: 'Ascending playback',
          bodyEs:
              'Reproduce el intervalo de forma ascendente y fija ese patrón para las reproducciones posteriores.',
          bodyEn:
              'Play the interval ascending and set that pattern for subsequent playback.',
          side: _HelpCalloutSide.bottom,
        ),
        _HelpStep(
          id: 'interval_generation_notes',
          titleEs: 'Notas',
          titleEn: 'Notes',
          bodyEs:
              'Notas: la tónica y la nota resultante del intervalo elegido.',
          bodyEn:
              'Notes: the tonic and the resulting note of the chosen interval.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_name',
          titleEs: 'Intervalo',
          titleEn: 'Interval',
          bodyEs: 'Nombre del intervalo seleccionado en la tabla.',
          bodyEn: 'Name of the interval selected in the table.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_semitones',
          titleEs: 'Semitonos',
          titleEn: 'Semitones',
          bodyEs: 'Número de semitonos entre las dos notas.',
          bodyEn: 'Number of semitones between the two notes.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_table',
          titleEs: 'Tabla de intervalos',
          titleEn: 'Interval table',
          bodyEs:
              'Tabla de intervalos: cada columna es un número de semitonos y cada fila una categoría (disminuida, menor, mayor, justa, aumentada). Pulsa una celda para generar ese intervalo desde la tónica.',
          bodyEn:
              'Interval table: each column is a number of semitones and each row a category (diminished, minor, major, perfect, augmented). Tap a cell to generate that interval from the tonic.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'interval_generation_instrument',
          titleEs: 'Piano o guitarra',
          titleEn: 'Piano or guitar',
          bodyEs:
              'Vista del intervalo generado en piano o guitarra. Las dos notas se muestran como referencia; usa los botones de reproducción ascendente o descendente para escucharlas.',
          bodyEn:
              'Piano or guitar view of the generated interval. The two notes are shown as a reference; use the ascending or descending playback buttons to hear them.',
          side: _HelpCalloutSide.top,
        ),
      ],
      6 => <_HelpStep>[
        _HelpStep(
          id: 'tuner_staff',
          titleEs: 'Vista del afinador',
          titleEn: 'Tuner view',
          bodyEs: 'Muestra afinacion, desviacion en cents y cuerda objetivo.',
          bodyEn: 'Shows tuning, cents deviation, and target string.',
          side: _HelpCalloutSide.top,
        ),
        _HelpStep(
          id: 'tuner_controls',
          titleEs: 'Panel del afinador',
          titleEn: 'Tuner panel',
          bodyEs: 'Configura la afinacion, la entrada y el rango del analisis.',
          bodyEn: 'Configure tuning, input, and analysis range here.',
          side: _HelpCalloutSide.left,
        ),
        _HelpStep(
          id: 'tuner_toggle',
          titleEs: 'Boton del afinador',
          titleEn: 'Tuner button',
          bodyEs: 'Inicia o detiene la escucha del microfono para afinar.',
          bodyEn: 'Starts or stops microphone listening for tuning.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'tuner_tuning_select',
          titleEs: 'Afinacion',
          titleEn: 'Tuning',
          bodyEs: 'Selecciona la afinacion objetivo del instrumento.',
          bodyEn: 'Selects the target tuning of the instrument.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'tuner_gain',
          titleEs: 'Ganancia',
          titleEn: 'Gain',
          bodyEs: 'Ajusta la sensibilidad de entrada del afinador.',
          bodyEn: 'Adjusts the tuner input sensitivity.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'tuner_range',
          titleEs: 'Rango de frecuencia',
          titleEn: 'Frequency range',
          bodyEs: 'Define el rango de frecuencias que el afinador analizara.',
          bodyEn: 'Defines the frequency range the tuner will analyze.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
        _HelpStep(
          id: 'tuner_readout',
          titleEs: 'Lectura del afinador',
          titleEn: 'Tuner readout',
          bodyEs:
              'Muestra la nota detectada, la desviacion y la frecuencia actual.',
          bodyEn: 'Shows the detected note, deviation, and current frequency.',
          side: _HelpCalloutSide.left,
          highlightPadding: 2,
        ),
      ],
      _ => const <_HelpStep>[],
    };
    return <_HelpStep>[...common, ...modeSpecific];
  }

  bool _helpAvailableForCurrentMode() => _helpStepsForCurrentMode().isNotEmpty;

  void _setHelpMode(bool enabled) {
    _helpActive = enabled && _helpAvailableForCurrentMode();
    _helpSelectedId = null;
    _helpBannerTimer?.cancel();
    if (_helpActive) {
      _helpBannerVisible = true;
      _helpOverlayController.repeat();
      _helpBannerTimer = Timer(const Duration(seconds: 15), () {
        if (mounted) _updateState(() => _helpBannerVisible = false);
      });
    } else {
      _helpOverlayController.stop();
      _helpOverlayController.value = 0;
    }
  }

  void _toggleHelpMode() {
    if (!_helpActive) {
      _cacheHelpAnchorRects();
    }
    _updateState(() {
      _setHelpMode(!_helpActive);
    });
  }

  void _cacheHelpAnchorRects() {
    final screenBounds = Offset.zero & MediaQuery.sizeOf(context);
    for (final entry in _helpAnchors.entries) {
      final target = entry.value.currentContext?.findRenderObject();
      if (target is! RenderBox || target.debugNeedsLayout || !target.hasSize) {
        continue;
      }
      final viewportBounds = <Rect>[];
      RenderObject? ancestor = target.parent;
      while (ancestor != null) {
        if (ancestor is RenderAbstractViewport && ancestor is RenderBox) {
          final viewport = ancestor as RenderBox;
          if (!viewport.debugNeedsLayout && viewport.hasSize) {
            viewportBounds.add(
              viewport.localToGlobal(Offset.zero) & viewport.size,
            );
          }
        }
        ancestor = ancestor.parent;
      }
      _helpGlobalRectCache[entry.key] = visibleHelpRect(
        target: target.localToGlobal(Offset.zero) & target.size,
        overlayBounds: screenBounds,
        viewportBounds: viewportBounds,
      );
    }
  }

  Rect? _helpRectFor(
    BuildContext overlayContext,
    String id, {
    required Rect overlayBounds,
  }) {
    final key = _helpAnchors[id];
    if (key == null) return null;
    final targetContext = key.currentContext;
    if (targetContext == null) return null;
    final targetBox = targetContext.findRenderObject();
    final overlayBox = overlayContext.findRenderObject();
    if (targetBox is! RenderBox || overlayBox is! RenderBox) {
      return null;
    }
    if (targetBox.debugNeedsLayout || !targetBox.hasSize) {
      final cached = _helpGlobalRectCache[id];
      if (cached == null) return null;
      final overlayOrigin = overlayBox.localToGlobal(Offset.zero);
      return cached.shift(-overlayOrigin);
    }
    final offset = targetBox.localToGlobal(Offset.zero, ancestor: overlayBox);
    final viewportBounds = <Rect>[];
    RenderObject? ancestor = targetBox.parent;
    while (ancestor != null && ancestor != overlayBox) {
      if (ancestor is RenderAbstractViewport && ancestor is RenderBox) {
        final viewportBox = ancestor as RenderBox;
        if (viewportBox.debugNeedsLayout || !viewportBox.hasSize) {
          ancestor = ancestor.parent;
          continue;
        }
        final viewportOffset = viewportBox.localToGlobal(
          Offset.zero,
          ancestor: overlayBox,
        );
        viewportBounds.add(viewportOffset & viewportBox.size);
      }
      ancestor = ancestor.parent;
    }
    final resolved = visibleHelpRect(
      target: offset & targetBox.size,
      overlayBounds: overlayBounds,
      viewportBounds: viewportBounds,
    );
    final overlayOrigin = overlayBox.localToGlobal(Offset.zero);
    _helpGlobalRectCache[id] = resolved.shift(overlayOrigin);
    return resolved;
  }

  List<_ResolvedHelpStep> _resolvedHelpSteps(
    BuildContext overlayContext, {
    required Rect overlayBounds,
  }) {
    return _helpStepsForCurrentMode()
        .map((step) {
          final rect = _helpRectFor(
            overlayContext,
            step.id,
            overlayBounds: overlayBounds,
          );
          if (rect == null || rect.width <= 0 || rect.height <= 0) {
            return null;
          }
          return _ResolvedHelpStep(
            step: step,
            rect: rect,
            highlightRect: rect.inflate(step.highlightPadding),
          );
        })
        .whereType<_ResolvedHelpStep>()
        .toList(growable: false);
  }

  _ResolvedHelpStep? _selectedHelpStep(List<_ResolvedHelpStep> resolved) {
    if (resolved.isEmpty) return null;
    if (_helpSelectedId == null) return null;
    for (final item in resolved) {
      if (item.step.id == _helpSelectedId) return item;
    }
    return null;
  }

  Rect _helpCalloutRect({
    required Rect target,
    required Size screenSize,
    required _HelpCalloutSide side,
    required EdgeInsets safePadding,
  }) {
    const margin = 16.0;
    const gap = 12.0;
    final width = math.min(screenSize.width - (margin * 2), 344.0);
    final largeScreen = screenSize.shortestSide >= 700.0;
    final height = math.min(
      math.max(
        screenSize.height * (largeScreen ? 0.255 : 0.225),
        largeScreen ? 232.0 : 196.0,
      ),
      largeScreen ? 300.0 : 248.0,
    );
    var left = target.left;
    var top = target.bottom + gap;
    switch (side) {
      case _HelpCalloutSide.top:
        left = target.center.dx - (width / 2);
        top = target.top - height - gap;
      case _HelpCalloutSide.right:
        left = target.right + gap;
        top = target.center.dy - (height / 2);
      case _HelpCalloutSide.bottom:
        left = target.center.dx - (width / 2);
        top = target.bottom + gap;
      case _HelpCalloutSide.left:
        left = target.left - width - gap;
        top = target.center.dy - (height / 2);
    }
    left = left.clamp(margin, screenSize.width - width - margin);
    top = top.clamp(
      safePadding.top + margin,
      screenSize.height - height - safePadding.bottom - margin,
    );
    return Rect.fromLTWH(left, top, width, height);
  }

  Rect _metronomeBeatRowRect(Size size) {
    final count = math.max(1, _metroBeatsPerBar);
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final spacing = count == 1 ? (right - left) : (right - left) / (count - 1);
    final baseR = (30 - (count * 0.75)).clamp(7.0, 24.0);
    final maxRBySpacing = (spacing * 0.42 - 2).clamp(6.0, 1000.0);
    final normalR = math.min(baseR, maxRBySpacing);
    final activeR = math.min(normalR + 2.0, maxRBySpacing + 1.5);
    return Rect.fromLTRB(
      left - activeR,
      yTop - activeR,
      right + activeR,
      yTop + activeR,
    );
  }

  Rect _metronomeMotionAxisRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    return Rect.fromLTRB(left - 12, axisY - 16, right + 12, axisY + 16);
  }

  Rect _metronomeTimerRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final yTop = math.max(44.0, size.height * 0.30);
    final yBot = math.min(size.height - 56.0, yTop + 74.0);
    final axisY = yBot + 18.0;
    final fontSize = math.min(44.0, size.height * 0.24);
    final centerY = axisY + ((size.height - axisY) * 0.5);
    final rectHeight = math.max(52.0, fontSize + 10.0);
    final rawTop = centerY - (rectHeight / 2);
    final minTop = axisY + 56.0;
    final maxTop = size.height - rectHeight - 16.0;
    // En algunos dispositivos/tamaños (Android 14) el rango puede invertirse
    // y `clamp` lanza ArgumentError si min > max.
    final top = maxTop >= minTop
        ? rawTop.clamp(minTop, maxTop)
        : math.max(0.0, math.min(rawTop, maxTop));
    final rectWidth = math.min(220.0, math.max(160.0, size.width * 0.26));
    final centerX = (left + right) / 2;
    return Rect.fromLTWH(centerX - (rectWidth / 2), top, rectWidth, rectHeight);
  }

  Rect _metronomeCenterButtonRect(Size size) {
    final left = 34.0;
    final right = math.max(left + 1.0, size.width - 34.0);
    final axisRect = _metronomeMotionAxisRect(size);
    final timerRect = _metronomeTimerRect(size);
    final buttonHeight = 46.0;
    final buttonWidth = math.min(286.0, math.max(210.0, size.width * 0.34));
    final centerY = (axisRect.bottom + timerRect.top) / 2;
    final minTop = axisRect.bottom + 6.0;
    final maxTop = timerRect.top - buttonHeight - 6.0;
    final idealTop = centerY - (buttonHeight / 2);
    final top = maxTop >= minTop
        ? idealTop.clamp(minTop, maxTop)
        : math.max(axisRect.bottom + 2.0, idealTop);
    final leftPos = ((left + right) / 2) - (buttonWidth / 2);
    return Rect.fromLTWH(leftPos, top, buttonWidth, buttonHeight);
  }

  String _staffHelpIdForCurrentMode() => switch (_tabIndex) {
    0 => 'detection_staff',
    1 => 'generation_staff',
    2 => 'circle_staff',
    3 => 'scales_staff',
    4 => 'metronome_bead_row',
    5 => 'interval_detection_staff',
    6 => 'tuner_staff',
    7 => 'interval_generation_staff',
    9 => 'interval_practice_staff',
    8 => 'note_detection_staff',
    _ => 'detection_staff',
  };
}
