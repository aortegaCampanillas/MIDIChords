part of 'main.dart';

extension _HomeScreenPages on _HomeScreenState {
  Widget _buildIntervalPracticePage() {
    final answered = _intervalPracticeAnswerCorrect != null;
    final reviewing =
        !_intervalPracticeRunning && _intervalPracticeHistory.isNotEmpty;
    final intervalName = answered
        ? <String>[
            intervalNames[_language]?[_intervalPracticeSemitones] ?? '-',
            ...?intervalAltNames[_language]?[_intervalPracticeSemitones],
          ].join(', ')
        : '-';
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                if (!compactLandscape) ...<Widget>[
                  Text(
                    _ui('Practicar Intervalos', 'Interval Practice'),
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 4),
                ],
                Wrap(
                  spacing: compactPhone ? 4 : 8,
                  runSpacing: compactPhone ? 4 : 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: <Widget>[
                    _helpAnchor(
                      'interval_practice_start_stop',
                      FilledButton(
                        onPressed: _toggleIntervalPractice,
                        style: compactPhone
                            ? FilledButton.styleFrom(
                                minimumSize: const Size(0, 36),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(
                          _intervalPracticeRunning
                              ? _ui('Parar', 'Stop')
                              : _ui('Iniciar', 'Start'),
                        ),
                      ),
                    ),
                    _helpAnchor(
                      'interval_practice_repeat',
                      IconButton.outlined(
                        tooltip: answered
                            ? _ui('Volver a escuchar', 'Listen again')
                            : _ui('Repetir', 'Repeat'),
                        onPressed: _intervalPracticeStarted
                            ? (answered
                                  ? _replayIntervalPracticeResult
                                  : _playIntervalPracticeQuestion)
                            : null,
                        style: compactPhone
                            ? IconButton.styleFrom(
                                minimumSize: const Size(36, 36),
                                padding: const EdgeInsets.all(6),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        icon: const Icon(Icons.replay),
                      ),
                    ),
                    _helpAnchor(
                      'interval_practice_next',
                      OutlinedButton(
                        onPressed:
                            _intervalPracticeRunning &&
                                answered &&
                                _intervalPracticeTotal <
                                    _intervalPracticeRepetitions
                            ? _nextIntervalPracticeQuestion
                            : null,
                        style: compactPhone
                            ? OutlinedButton.styleFrom(
                                minimumSize: const Size(0, 36),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(_ui('Siguiente', 'Next')),
                      ),
                    ),
                    _helpAnchor(
                      'interval_practice_help',
                      IconButton.outlined(
                        tooltip: _ui('Ayuda', 'Help'),
                        onPressed: _showIntervalPracticeHelp,
                        style: compactPhone
                            ? IconButton.styleFrom(
                                minimumSize: const Size(36, 36),
                                padding: const EdgeInsets.all(6),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        icon: const Icon(Icons.question_mark),
                      ),
                    ),
                    Wrap(
                      spacing: compactPhone ? 6 : 16,
                      runSpacing: 4,
                      children: <Widget>[
                        _helpAnchor(
                          'interval_practice_random_tonic',
                          _practiceCheckbox(
                            _ui('Tónica aleatoria', 'Random tonic'),
                            _intervalPracticeRandomTonic,
                            (value) => _updateState(
                              () =>
                                  _intervalPracticeRandomTonic = value ?? false,
                            ),
                            compact: compactPhone,
                          ),
                        ),
                        _helpAnchor(
                          'interval_practice_ascending',
                          _practiceCheckbox(
                            _ui('Solo ascendentes', 'Ascending only'),
                            _intervalPracticeAscendingOnly,
                            (value) => _updateState(
                              () => _intervalPracticeAscendingOnly =
                                  value ?? false,
                            ),
                            compact: compactPhone,
                          ),
                        ),
                      ],
                    ),
                    if (reviewing) ...<Widget>[
                      const SizedBox(width: 8),
                      Text(_ui('Ver resultados', 'View results')),
                      _helpAnchor(
                        'interval_practice_previous_result',
                        IconButton.outlined(
                          onPressed: (_intervalPracticeReviewIndex ?? 0) > 0
                              ? () => _reviewIntervalPractice(-1)
                              : null,
                          icon: const Icon(Icons.arrow_left),
                        ),
                      ),
                      _helpAnchor(
                        'interval_practice_next_result',
                        IconButton.outlined(
                          onPressed:
                              (_intervalPracticeReviewIndex ?? 0) <
                                  _intervalPracticeHistory.length - 1
                              ? () => _reviewIntervalPractice(1)
                              : null,
                          icon: const Icon(Icons.arrow_right),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 2),
                Wrap(
                  spacing: compactPhone ? 4 : 8,
                  runSpacing: compactPhone ? 4 : 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: <Widget>[
                    _helpAnchor(
                      'interval_practice_repetitions',
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: <Widget>[
                          Text(_ui('Repeticiones', 'Repetitions')),
                          const SizedBox(width: 8),
                          SizedBox(
                            width: compactPhone ? 54 : 64,
                            height: compactPhone ? 36 : 40,
                            child: TextFormField(
                              key: ValueKey<int>(_intervalPracticeRepetitions),
                              initialValue: '$_intervalPracticeRepetitions',
                              enabled: !_intervalPracticeRunning,
                              keyboardType: TextInputType.number,
                              textAlign: TextAlign.center,
                              textAlignVertical: TextAlignVertical.center,
                              decoration: const InputDecoration(
                                isDense: true,
                                contentPadding: EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 9,
                                ),
                              ),
                              onChanged: (value) {
                                final parsed = int.tryParse(value);
                                if (parsed != null) {
                                  _intervalPracticeRepetitions = parsed.clamp(
                                    1,
                                    100,
                                  );
                                }
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                    _helpAnchor(
                      'interval_practice_filter',
                      OutlinedButton(
                        onPressed: _intervalPracticeRunning
                            ? null
                            : _showIntervalPracticeFilter,
                        style: compactPhone
                            ? OutlinedButton.styleFrom(
                                minimumSize: const Size(0, 36),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(_ui('Filtrar', 'Filter')),
                      ),
                    ),
                    _helpAnchor(
                      'interval_practice_playback_mode',
                      OutlinedButton(
                        onPressed: _intervalPracticeRunning
                            ? null
                            : () => _updateState(
                                () => _intervalPracticeHarmonic =
                                    !_intervalPracticeHarmonic,
                              ),
                        style: compactPhone
                            ? OutlinedButton.styleFrom(
                                minimumSize: const Size(0, 36),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(
                          _intervalPracticeHarmonic
                              ? _ui('Armónico', 'Harmonic')
                              : _ui('Melódico', 'Melodic'),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                _helpAnchor(
                  'interval_practice_result',
                  Container(
                    width: double.infinity,
                    padding: EdgeInsets.all(compactPhone ? 6 : 10),
                    decoration: BoxDecoration(
                      color: _HomeScreenState._surfaceDark,
                      border: Border.all(color: _HomeScreenState._border),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: <Widget>[
                        Text(
                          '${_ui('Aciertos', 'Score')}: '
                          '$_intervalPracticeCorrect/$_intervalPracticeTotal',
                        ),
                        const SizedBox(width: 20),
                        Expanded(
                          child: Text(
                            '${_ui('Intervalo', 'Interval')}: $intervalName',
                            textAlign: TextAlign.right,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                if (!compactPhone) ...<Widget>[
                  const SizedBox(height: 6),
                  _helpAnchor(
                    'interval_practice_table',
                    _buildIntervalPracticeTable(constraints.maxWidth),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _practiceCheckbox(
    String label,
    bool value,
    ValueChanged<bool?> onChanged, {
    bool compact = false,
  }) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Checkbox(
          value: value,
          onChanged: _intervalPracticeRunning ? null : onChanged,
          visualDensity: compact ? VisualDensity.compact : null,
          materialTapTargetSize: compact
              ? MaterialTapTargetSize.shrinkWrap
              : null,
        ),
        GestureDetector(
          onTap: _intervalPracticeRunning ? null : () => onChanged(!value),
          child: Text(label),
        ),
      ],
    );
  }

  Widget _buildIntervalPracticeTable(double availableWidth) {
    final tableWidth = math.max(650.0, availableWidth);
    Widget cell(
      String text, {
      bool header = false,
      Color? color,
      VoidCallback? onTap,
    }) {
      final content = Container(
        height: 34,
        alignment: Alignment.center,
        color:
            color ??
            (header ? const Color(0xFF17273A) : _HomeScreenState._surfaceDark),
        padding: const EdgeInsets.symmetric(horizontal: 3),
        child: Text(
          text,
          style: TextStyle(
            color: color != null
                ? const Color(0xFF101010)
                : onTap == null && !header
                ? const Color(0xFF607086)
                : _HomeScreenState._text,
            fontWeight: header ? FontWeight.w700 : FontWeight.w600,
            fontSize: header ? 11 : 12,
          ),
        ),
      );
      return onTap == null ? content : InkWell(onTap: onTap, child: content);
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: tableWidth,
        child: Table(
          border: TableBorder.all(color: const Color(0xFF5A6A82)),
          columnWidths: const <int, TableColumnWidth>{0: FixedColumnWidth(104)},
          defaultColumnWidth: const FlexColumnWidth(),
          children: <TableRow>[
            TableRow(
              children: <Widget>[
                cell('', header: true),
                for (var semitones = 0; semitones <= 12; semitones += 1)
                  cell('$semitones', header: true),
              ],
            ),
            for (final category in intervalGridCategories)
              TableRow(
                children: <Widget>[
                  cell(category.name(_language), header: true),
                  for (var semitones = 0; semitones <= 12; semitones += 1)
                    () {
                      final matches = category.cells.where(
                        (item) => item.semitones == semitones,
                      );
                      if (matches.isEmpty) return cell('');
                      final item = matches.first;
                      final allowed = _intervalPracticeAllowedSemitones
                          .contains(semitones);
                      Color? color;
                      if (_intervalPracticeAnswerCorrect != null &&
                          semitones == _intervalPracticeSemitones) {
                        color = const Color(0xFF39C66D);
                      } else if (_intervalPracticeAnswerCorrect == false &&
                          (_intervalPracticeAnswerNote! - _intervalPracticeRoot)
                                  .abs() ==
                              semitones) {
                        color = const Color(0xFFE35D67);
                      }
                      return cell(
                        item.label,
                        color: color,
                        onTap:
                            (_intervalPracticeAnswerCorrect == null
                                ? allowed && _intervalPracticeRunning
                                : semitones == _intervalPracticeSemitones ||
                                      semitones ==
                                          (_intervalPracticeAnswerNote! -
                                                  _intervalPracticeRoot)
                                              .abs())
                            ? () => _selectIntervalPracticeTableCell(semitones)
                            : null,
                      );
                    }(),
                ],
              ),
          ],
        ),
      ),
    );
  }

  void _showIntervalPracticeHelp() {
    final compactPhone = _isCompactPhone(context);
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          _ui('Cómo practicar intervalos', 'How to practice intervals'),
        ),
        content: SingleChildScrollView(
          child: Text(
            _ui(
              '1. Pulsa Iniciar para escuchar un intervalo. En el pentagrama y el piano solo se muestra la primera nota.\n\n'
                  '2. ${compactPhone ? 'Responde pulsando la segunda nota en el piano o MIDI.' : 'Responde pulsando la segunda nota en el piano o MIDI, o eligiendo el intervalo en la tabla.'} Si Solo ascendentes está desmarcado, la segunda nota también puede ser más grave que la tónica.\n\n'
                  '3. La respuesta correcta se muestra en verde. Si fallas, tu nota aparece en rojo y la correcta en verde; el contador Aciertos se actualiza en ambos casos.\n\n'
                  '4. Durante la corrección o la revisión puedes pulsar las notas mostradas en el pentagrama, el piano o MIDI para escucharlas. Las demás notas se rechazan con el símbolo de prohibido.\n\n'
                  'Repetir reproduce de nuevo el ejercicio o su corrección. Siguiente genera y reproduce otro intervalo. Ver resultados permite recorrer con ◀ y ▶ los ejercicios contestados.',
              '1. Press Start to hear an interval. Only the first note is shown on the staff and piano.\n\n'
                  '2. ${compactPhone ? 'Answer by pressing the second note on the piano or MIDI.' : 'Answer by pressing the second note on the piano or MIDI, or by choosing the interval in the table.'} If Ascending only is unchecked, the second note may also be lower than the tonic.\n\n'
                  '3. A correct answer is shown in green. If you miss, your note appears in red and the correct one in green; the score is updated in both cases.\n\n'
                  '4. During correction or review, press the displayed notes on the staff, piano, or MIDI to hear them. Other notes are rejected with the forbidden symbol.\n\n'
                  'Repeat plays the exercise or its correction again. Next creates and plays another interval. View results lets you browse answered exercises with ◀ and ▶.',
            ),
          ),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(_ui('Cerrar', 'Close')),
          ),
        ],
      ),
    );
  }

  void _showIntervalPracticeFilter() {
    final compactPhone = _isCompactPhone(context);
    final draft = Set<int>.from(_intervalPracticeAllowedSemitones);
    showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          titlePadding: compactPhone
              ? const EdgeInsets.fromLTRB(16, 12, 16, 4)
              : null,
          contentPadding: compactPhone
              ? const EdgeInsets.symmetric(horizontal: 16, vertical: 4)
              : null,
          actionsPadding: compactPhone
              ? const EdgeInsets.fromLTRB(8, 0, 8, 6)
              : null,
          title: Text(
            _ui('Filtrar intervalos', 'Filter intervals'),
            style: compactPhone
                ? const TextStyle(fontSize: 20, fontWeight: FontWeight.w600)
                : null,
          ),
          content: SizedBox(
            width: 520,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    spacing: 8,
                    children: <Widget>[
                      TextButton(
                        onPressed: () => setDialogState(() {
                          draft
                            ..clear()
                            ..addAll(List<int>.generate(13, (index) => index));
                        }),
                        style: compactPhone
                            ? TextButton.styleFrom(
                                minimumSize: const Size(0, 32),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(_ui('Seleccionar todo', 'Select all')),
                      ),
                      TextButton(
                        onPressed: () => setDialogState(draft.clear),
                        style: compactPhone
                            ? TextButton.styleFrom(
                                minimumSize: const Size(0, 32),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                ),
                                visualDensity: VisualDensity.compact,
                              )
                            : null,
                        child: Text(
                          _ui('Eliminar selección', 'Clear selection'),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: compactPhone ? 2 : 12),
                  Text(
                    _ui(
                      'Selecciona las posibles segundas notas:',
                      'Select the possible second notes:',
                    ),
                    style: compactPhone ? const TextStyle(fontSize: 13) : null,
                  ),
                  SizedBox(height: compactPhone ? 2 : 8),
                  _buildIntervalFilterKeyboard(
                    draft,
                    (semitones) => setDialogState(() {
                      if (!draft.remove(semitones)) {
                        draft.add(semitones);
                      }
                    }),
                  ),
                ],
              ),
            ),
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              style: compactPhone
                  ? TextButton.styleFrom(
                      minimumSize: const Size(0, 32),
                      visualDensity: VisualDensity.compact,
                    )
                  : null,
              child: Text(_ui('Cancelar', 'Cancel')),
            ),
            FilledButton(
              onPressed: draft.isEmpty
                  ? null
                  : () {
                      _updateState(() {
                        _intervalPracticeAllowedSemitones
                          ..clear()
                          ..addAll(draft);
                        _intervalPracticeDeck.reset();
                      });
                      Navigator.of(dialogContext).pop();
                    },
              style: compactPhone
                  ? FilledButton.styleFrom(
                      minimumSize: const Size(0, 32),
                      visualDensity: VisualDensity.compact,
                    )
                  : null,
              child: Text(_ui('Aceptar', 'Accept')),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIntervalFilterKeyboard(
    Set<int> selected,
    ValueChanged<int> onToggle,
  ) {
    final compactPhone = _isCompactPhone(context);
    final whiteKeyHeight = compactPhone ? 96.0 : 112.0;
    final blackKeyHeight = compactPhone ? 58.0 : 68.0;
    const whiteNotes = <int>[0, 2, 4, 5, 7, 9, 11, 12];
    const blackNotes = <int, int>{1: 1, 3: 2, 6: 4, 8: 5, 10: 6};
    return LayoutBuilder(
      builder: (context, constraints) {
        final whiteWidth = constraints.maxWidth / whiteNotes.length;
        final blackWidth = whiteWidth * 0.58;
        return SizedBox(
          height: whiteKeyHeight,
          child: Stack(
            children: <Widget>[
              Row(
                children: <Widget>[
                  for (final semitones in whiteNotes)
                    GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () => onToggle(semitones),
                      child: Container(
                        width: whiteWidth,
                        height: whiteKeyHeight,
                        alignment: Alignment.bottomCenter,
                        padding: EdgeInsets.only(bottom: compactPhone ? 3 : 7),
                        decoration: BoxDecoration(
                          color: selected.contains(semitones)
                              ? const Color(0xFF8BE3A5)
                              : const Color(0xFFF5F4EF),
                          border: Border.all(color: const Color(0xFF718096)),
                        ),
                        child: Text(
                          _pcLabel(semitones % 12),
                          style: const TextStyle(
                            color: Color(0xFF15202C),
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              for (final entry in blackNotes.entries)
                Positioned(
                  left: entry.value * whiteWidth - blackWidth / 2,
                  top: 0,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => onToggle(entry.key),
                    child: Container(
                      width: blackWidth,
                      height: blackKeyHeight,
                      alignment: Alignment.bottomCenter,
                      padding: EdgeInsets.only(bottom: compactPhone ? 3 : 5),
                      decoration: BoxDecoration(
                        color: selected.contains(entry.key)
                            ? const Color(0xFF39C66D)
                            : const Color(0xFF111A25),
                        border: Border.all(color: const Color(0xFF718096)),
                        borderRadius: const BorderRadius.vertical(
                          bottom: Radius.circular(5),
                        ),
                      ),
                      child: Text(
                        _pcLabel(entry.key),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 9,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildNoteDetectionPage() {
    final note = _noteDetectionNote;
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactLandscape =
              constraints.maxWidth > constraints.maxHeight &&
              (_isCompactPhone(context) || constraints.maxHeight < 300);
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                if (!compactLandscape) ...<Widget>[
                  Text(
                    _ui('Detección de Notas', 'Note Detection'),
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
                Wrap(
                  spacing: compactLandscape ? 4 : 8,
                  runSpacing: compactLandscape ? 4 : 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: <Widget>[
                    _helpAnchor(
                      'note_detection_play_button',
                      _holdPlayButton(
                        enabled: note != null,
                        active: _noteDetectionPlayPressed,
                        label: null,
                        compact: compactLandscape,
                        onDown: () async {
                          if (note == null) return;
                          _updateState(() => _noteDetectionPlayPressed = true);
                          await _startHeldChord(<int>[
                            note,
                          ], instrument: 'piano');
                        },
                        onUp: () {
                          _stopHeldChord();
                          if (mounted) {
                            _updateState(
                              () => _noteDetectionPlayPressed = false,
                            );
                          }
                        },
                      ),
                    ),
                    _helpAnchor(
                      'note_detection_clear_button',
                      OutlinedButton.icon(
                        onPressed: note == null
                            ? null
                            : () {
                                _stopHeldChord();
                                _stopHeldMidiInputs();
                                _updateState(() {
                                  _noteDetectionNote = null;
                                  _noteDetectionPlayPressed = false;
                                });
                              },
                        icon: Icon(
                          Icons.clear_all,
                          size: compactLandscape ? 16 : 24,
                        ),
                        label: Text(
                          _ui('Limpiar', 'Clear'),
                          style: TextStyle(
                            fontSize: compactLandscape ? 11 : 14,
                          ),
                        ),
                        style: OutlinedButton.styleFrom(
                          minimumSize: Size(0, compactLandscape ? 34 : 40),
                          padding: EdgeInsets.symmetric(
                            horizontal: compactLandscape ? 8 : 12,
                          ),
                          visualDensity: compactLandscape
                              ? VisualDensity.compact
                              : null,
                        ),
                      ),
                    ),
                    _helpAnchor(
                      'note_detection_details_toggle',
                      OutlinedButton.icon(
                        onPressed: () => _updateState(
                          () => _noteDetectionDetailsVisible =
                              !_noteDetectionDetailsVisible,
                        ),
                        icon: Icon(
                          _noteDetectionDetailsVisible
                              ? Icons.visibility
                              : Icons.visibility_off,
                          size: compactLandscape ? 16 : 24,
                        ),
                        label: Text(
                          _noteDetectionDetailsVisible
                              ? _ui('Ocultar', 'Hide')
                              : _ui('Mostrar', 'Show'),
                          style: TextStyle(
                            fontSize: compactLandscape ? 11 : 14,
                          ),
                        ),
                        style: OutlinedButton.styleFrom(
                          minimumSize: Size(0, compactLandscape ? 34 : 40),
                          padding: EdgeInsets.symmetric(
                            horizontal: compactLandscape ? 8 : 12,
                          ),
                          visualDensity: compactLandscape
                              ? VisualDensity.compact
                              : null,
                          backgroundColor: _noteDetectionDetailsVisible
                              ? null
                              : _HomeScreenState._accent,
                          foregroundColor: _noteDetectionDetailsVisible
                              ? null
                              : _HomeScreenState._surfaceDark,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: compactLandscape ? 6 : 12),
                if (_noteDetectionDetailsVisible)
                  _helpAnchor(
                    'note_detection_result',
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.all(compactLandscape ? 8 : 16),
                      decoration: BoxDecoration(
                        color: _HomeScreenState._surfaceDark,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: _HomeScreenState._border),
                      ),
                      child: RichText(
                        text: TextSpan(
                          children: <InlineSpan>[
                            TextSpan(
                              text: '${_ui('Nota', 'Note')}: ',
                              style: TextStyle(
                                color: _HomeScreenState._muted,
                                fontWeight: FontWeight.w800,
                                fontSize: compactLandscape ? 12 : 16,
                                height: 1.25,
                              ),
                            ),
                            TextSpan(
                              text: note == null
                                  ? '-'
                                  : noteNameLocal(
                                      note,
                                      language: _language,
                                      preferFlat: _accidental == 'flat',
                                      withOctave: false,
                                    ),
                              style: TextStyle(
                                color: _HomeScreenState._accent,
                                fontWeight: FontWeight.w800,
                                fontSize: compactLandscape ? 14 : 18,
                                height: 1.25,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDetectionPage() {
    final hasNotes = _hasDetectionNotes;
    final detectedSuffix = _detectionResultJson?['suffix'];
    final hasDetectedChord =
        detectedSuffix is String && _detectionResultJson?['root_pc'] is num;
    final detectedInversion =
        (_detectionResultJson?['inversion'] as num?)?.toInt() ?? 0;
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape =
              constraints.maxWidth > constraints.maxHeight &&
              (compactPhone || constraints.maxHeight < 300);
          final resultHeight = compactLandscape
              ? math.max(120.0, constraints.maxHeight - 78.0)
              : _compactResultHeight(constraints, minHeight: 140);
          final content = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              if (!compactLandscape) ...<Widget>[
                Text(
                  _ui('Detección de Acordes', 'Chord Detection'),
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 8),
              ],
              Wrap(
                spacing: compactLandscape ? 4 : 8,
                runSpacing: 4,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: <Widget>[
                  _helpAnchor(
                    'detection_play_button',
                    _holdPlayButton(
                      enabled: hasNotes,
                      active: _detectionPlayPressed,
                      label: null,
                      onDown: () async {
                        final notes = _activeDetectionNotes.toList()..sort();
                        if (notes.isEmpty) return;
                        _updateState(() {
                          _detectionPlayPressed = true;
                          _detectionPlayHeldNotes
                            ..clear()
                            ..addAll(notes);
                        });
                        await _startHeldChord(notes, instrument: 'piano');
                      },
                      onUp: () {
                        _stopHeldChord();
                        if (mounted) {
                          _updateState(() {
                            _detectionPlayPressed = false;
                            _detectionPlayHeldNotes.clear();
                          });
                        }
                      },
                      compact: compactLandscape,
                    ),
                  ),
                  _buildChordVariantTheoryButton(
                    helpId: 'detection_variant_theory',
                    suffix: detectedSuffix is String ? detectedSuffix : '',
                    inversion: detectedInversion,
                    enabled: hasDetectedChord,
                    compact: compactLandscape,
                  ),
                  _helpAnchor(
                    'detection_clear_button',
                    OutlinedButton.icon(
                      onPressed: !hasNotes
                          ? null
                          : () {
                              _updateState(
                                () => _detectionSelectedNotes.clear(),
                              );
                              _detectionMidiHeldNotes.clear();
                              _stopHeldMidiInputs();
                              if (!_requestInFlight) {
                                unawaited(_callDetect());
                              }
                            },
                      icon: Icon(
                        Icons.clear_all,
                        size: compactLandscape ? 16 : 24,
                      ),
                      label: Text(
                        _ui('Limpiar', 'Clear'),
                        style: TextStyle(fontSize: compactLandscape ? 11 : 14),
                      ),
                      style: OutlinedButton.styleFrom(
                        minimumSize: Size(0, compactLandscape ? 34 : 40),
                        padding: EdgeInsets.symmetric(
                          horizontal: compactLandscape ? 8 : 12,
                        ),
                        visualDensity: compactLandscape
                            ? VisualDensity.compact
                            : null,
                      ),
                    ),
                  ),
                  _helpAnchor(
                    'detection_details_toggle',
                    OutlinedButton.icon(
                      onPressed: () => _updateState(
                        () => _detectionDetailsVisible =
                            !_detectionDetailsVisible,
                      ),
                      icon: Icon(
                        Icons.visibility,
                        size: compactLandscape ? 16 : 24,
                      ),
                      label: Text(
                        _detectionDetailsVisible
                            ? _ui('Ocultar', 'Hide')
                            : _ui('Mostrar', 'Show'),
                        style: TextStyle(fontSize: compactLandscape ? 11 : 14),
                      ),
                      style: OutlinedButton.styleFrom(
                        minimumSize: Size(0, compactLandscape ? 34 : 40),
                        padding: EdgeInsets.symmetric(
                          horizontal: compactLandscape ? 8 : 12,
                        ),
                        visualDensity: compactLandscape
                            ? VisualDensity.compact
                            : null,
                        backgroundColor: _detectionDetailsVisible
                            ? null
                            : _HomeScreenState._accent,
                        foregroundColor: _detectionDetailsVisible
                            ? null
                            : _HomeScreenState._surfaceDark,
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: compactLandscape ? 6 : 12),
              if (_detectionDetailsVisible)
                if (compactPhone || compactLandscape)
                  SizedBox(
                    height: resultHeight,
                    child: _buildDetectionResultBlock(
                      compact: compactLandscape,
                    ),
                  )
                else
                  Expanded(child: _buildDetectionResultBlock()),
            ],
          );
          if (!compactLandscape) {
            return content;
          }
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: content,
            ),
          );
        },
      ),
    );
  }

  Widget _buildChordGenerationPage() {
    return _buildModeScaffold(
      compactRightPanel: _buildChordResultBlock(compact: true),
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          final resultHeight = compactLandscape
              ? math.max(84.0, constraints.maxHeight - 156.0)
              : _compactResultHeight(constraints);
          final compactGenerationLayout =
              compactLandscape || (compactPhone && constraints.maxWidth < 700);
          final content = Column(
            children: <Widget>[
              if (!compactLandscape) ...<Widget>[
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    _ui('Generación de acordes', 'Chord generation'),
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: 18,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
              ],
              if (compactGenerationLayout)
                Column(
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        _helpAnchor(
                          'generation_play_button',
                          _holdPlayButton(
                            enabled:
                                _generatedChordJson != null &&
                                _extractMidiList(_generatedChordJson!, <String>[
                                  'notes_midi',
                                ]).isNotEmpty,
                            active: _generationPlayPressed,
                            label: null,
                            compact: compactLandscape,
                            onDown: () async {
                              final notes = _generationPlaybackNotes();
                              if (notes.isEmpty) return;
                              _updateState(() => _generationPlayPressed = true);
                              await _startHeldChord(
                                notes,
                                instrument: _instrumentView == 'guitar'
                                    ? 'guitar'
                                    : 'piano',
                              );
                            },
                            onUp: () {
                              _stopHeldChord();
                              if (mounted) {
                                _updateState(
                                  () => _generationPlayPressed = false,
                                );
                              }
                            },
                          ),
                        ),
                        SizedBox(width: compactLandscape ? 4 : 8),
                        _buildChordVariantTheoryButton(
                          compact: compactLandscape,
                        ),
                        SizedBox(width: compactLandscape ? 4 : 8),
                        Expanded(
                          child: _helpAnchor(
                            'generation_tonic',
                            _buildTonicLetterAccidentalDropdowns(
                              rootPc: _chordRootPc,
                              savedLetterPc: _chordRootLetterPc,
                              savedAccidental: _chordRootAccidental,
                              onPc: (pc, letterPc, accidental) {
                                _updateState(() {
                                  _chordRootPc = pc;
                                  _chordRootLetterPc = letterPc;
                                  _chordRootAccidental = accidental;
                                });
                                if (!_requestInFlight) {
                                  unawaited(
                                    _callGenerateChord(playPreview: true),
                                  );
                                }
                              },
                              compact: compactLandscape,
                              hideLabel: compactLandscape,
                            ),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: compactLandscape ? 4 : 8),
                    Row(
                      children: <Widget>[
                        Expanded(
                          flex: 2,
                          child: _helpAnchor(
                            'generation_variant',
                            DropdownButtonFormField<String>(
                              key: ValueKey<String>('suffix_$_chordSuffix'),
                              initialValue: _chordSuffix,
                              isExpanded: true,
                              dropdownColor: _HomeScreenState._surfaceDark,
                              style: TextStyle(
                                color: _HomeScreenState._text,
                                fontSize: compactLandscape ? 11 : null,
                              ),
                              decoration: InputDecoration(
                                labelText: compactLandscape
                                    ? null
                                    : _ui('Variante', 'Variant'),
                                isDense: compactLandscape,
                                contentPadding: compactLandscape
                                    ? const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 8,
                                      )
                                    : null,
                              ),
                              items: buildChordVariantDropdownItems(
                                catalog: _chordTheoryCatalog,
                                patterns: _chordPatterns,
                                language: _language,
                              ),
                              selectedItemBuilder: (context) =>
                                  buildChordVariantDropdownItems(
                                    catalog: _chordTheoryCatalog,
                                    patterns: _chordPatterns,
                                    language: _language,
                                  ).map((item) {
                                    final value = item.value ?? '';
                                    return Align(
                                      alignment: Alignment.centerLeft,
                                      child: Text(
                                        item.enabled
                                            ? (value.isEmpty ? 'maj' : value)
                                            : '',
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: 1,
                                      ),
                                    );
                                  }).toList(),
                              onChanged: (value) {
                                if (value == null) {
                                  return;
                                }
                                _updateState(() {
                                  _chordSuffix = value;
                                  _chordGuitarVariant = 0;
                                  _recomputeMaxInversion();
                                });
                                if (!_requestInFlight) {
                                  unawaited(
                                    _callGenerateChord(playPreview: true),
                                  );
                                }
                              },
                            ),
                          ),
                        ),
                        SizedBox(width: compactLandscape ? 4 : 8),
                        Expanded(
                          child: _helpAnchor(
                            'generation_inversion',
                            DropdownButtonFormField<int>(
                              key: ValueKey<String>(
                                'inv_$_chordInversion/$_chordMaxInversion',
                              ),
                              initialValue: _chordInversion.clamp(
                                0,
                                _chordMaxInversion,
                              ),
                              isExpanded: true,
                              dropdownColor: _HomeScreenState._surfaceDark,
                              style: TextStyle(
                                color: _HomeScreenState._text,
                                fontSize: compactLandscape ? 11 : null,
                              ),
                              decoration: InputDecoration(
                                labelText: compactLandscape
                                    ? null
                                    : _ui('Inversión', 'Inversion'),
                                isDense: compactLandscape,
                                contentPadding: compactLandscape
                                    ? const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 8,
                                      )
                                    : null,
                              ),
                              items: List<DropdownMenuItem<int>>.generate(
                                _chordMaxInversion + 1,
                                (i) => DropdownMenuItem<int>(
                                  value: i,
                                  child: Text(_inversionLabel(i)),
                                ),
                              ),
                              selectedItemBuilder: (context) =>
                                  List<Widget>.generate(
                                    _chordMaxInversion + 1,
                                    (i) => Align(
                                      alignment: Alignment.centerLeft,
                                      child: Text(
                                        _inversionLabel(i, compact: true),
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: 1,
                                      ),
                                    ),
                                  ),
                              onChanged: _instrumentView == 'guitar'
                                  ? null
                                  : (value) {
                                      if (value == null) return;
                                      _updateState(
                                        () => _chordInversion = value,
                                      );
                                      if (!_requestInFlight) {
                                        unawaited(
                                          _callGenerateChord(playPreview: true),
                                        );
                                      }
                                    },
                            ),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: compactLandscape ? 4 : 8),
                    _buildGenerationHandRow(compact: compactLandscape),
                  ],
                )
              else
                Row(
                  children: <Widget>[
                    Expanded(
                      flex: 4,
                      child: _helpAnchor(
                        'generation_tonic',
                        _buildTonicLetterAccidentalDropdowns(
                          rootPc: _chordRootPc,
                          savedLetterPc: _chordRootLetterPc,
                          savedAccidental: _chordRootAccidental,
                          onPc: (pc, letterPc, accidental) {
                            _updateState(() {
                              _chordRootPc = pc;
                              _chordRootLetterPc = letterPc;
                              _chordRootAccidental = accidental;
                            });
                            if (!_requestInFlight) {
                              unawaited(_callGenerateChord(playPreview: true));
                            }
                          },
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 5,
                      child: _helpAnchor(
                        'generation_variant',
                        DropdownButtonFormField<String>(
                          key: ValueKey<String>('suffix_$_chordSuffix'),
                          initialValue: _chordSuffix,
                          isExpanded: true,
                          dropdownColor: _HomeScreenState._surfaceDark,
                          style: const TextStyle(color: _HomeScreenState._text),
                          decoration: InputDecoration(
                            labelText: _ui('Variante', 'Variant'),
                          ),
                          items: buildChordVariantDropdownItems(
                            catalog: _chordTheoryCatalog,
                            patterns: _chordPatterns,
                            language: _language,
                          ),
                          selectedItemBuilder: (context) =>
                              buildChordVariantDropdownItems(
                                catalog: _chordTheoryCatalog,
                                patterns: _chordPatterns,
                                language: _language,
                              ).map((item) {
                                final value = item.value ?? '';
                                return Align(
                                  alignment: Alignment.centerLeft,
                                  child: Text(
                                    item.enabled
                                        ? (value.isEmpty ? 'maj' : value)
                                        : '',
                                    overflow: TextOverflow.ellipsis,
                                    maxLines: 1,
                                  ),
                                );
                              }).toList(),
                          onChanged: (value) {
                            if (value == null) {
                              return;
                            }
                            _updateState(() {
                              _chordSuffix = value;
                              _chordGuitarVariant = 0;
                              _recomputeMaxInversion();
                            });
                            if (!_requestInFlight) {
                              unawaited(_callGenerateChord(playPreview: true));
                            }
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              SizedBox(height: compactLandscape ? 4 : 12),
              if (!compactGenerationLayout) ...<Widget>[
                Row(
                  children: <Widget>[
                    _helpAnchor(
                      'generation_play_button',
                      _holdPlayButton(
                        enabled:
                            _generatedChordJson != null &&
                            _extractMidiList(_generatedChordJson!, <String>[
                              'notes_midi',
                            ]).isNotEmpty,
                        active: _generationPlayPressed,
                        label: null,
                        onDown: () async {
                          final notes = _generationPlaybackNotes();
                          if (notes.isEmpty) return;
                          _updateState(() => _generationPlayPressed = true);
                          await _startHeldChord(
                            notes,
                            instrument: _instrumentView == 'guitar'
                                ? 'guitar'
                                : 'piano',
                          );
                        },
                        onUp: () {
                          _stopHeldChord();
                          if (mounted) {
                            _updateState(() => _generationPlayPressed = false);
                          }
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    _buildChordVariantTheoryButton(),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _helpAnchor(
                        'generation_inversion',
                        DropdownButtonFormField<int>(
                          key: ValueKey<String>(
                            'inv_$_chordInversion/$_chordMaxInversion',
                          ),
                          initialValue: _chordInversion.clamp(
                            0,
                            _chordMaxInversion,
                          ),
                          isExpanded: true,
                          dropdownColor: _HomeScreenState._surfaceDark,
                          style: const TextStyle(color: _HomeScreenState._text),
                          decoration: InputDecoration(
                            labelText: _ui('Inversión', 'Inversion'),
                          ),
                          items: List<DropdownMenuItem<int>>.generate(
                            _chordMaxInversion + 1,
                            (i) => DropdownMenuItem<int>(
                              value: i,
                              child: Text(_inversionLabel(i)),
                            ),
                          ),
                          selectedItemBuilder: (context) =>
                              List<Widget>.generate(
                                _chordMaxInversion + 1,
                                (i) => Align(
                                  alignment: Alignment.centerLeft,
                                  child: Text(
                                    _inversionLabel(i, compact: true),
                                    overflow: TextOverflow.ellipsis,
                                    maxLines: 1,
                                  ),
                                ),
                              ),
                          onChanged: _instrumentView == 'guitar'
                              ? null
                              : (value) {
                                  if (value == null) return;
                                  _updateState(() => _chordInversion = value);
                                  if (!_requestInFlight) {
                                    unawaited(
                                      _callGenerateChord(playPreview: true),
                                    );
                                  }
                                },
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                _buildGenerationHandRow(),
              ],
              if (!compactLandscape) ...<Widget>[
                const SizedBox(height: 8),
                if (compactPhone)
                  SizedBox(
                    height: resultHeight,
                    child: _buildChordResultBlock(),
                  )
                else
                  Expanded(child: _buildChordResultBlock()),
              ],
            ],
          );
          if (!compactLandscape) {
            return content;
          }
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: content,
            ),
          );
        },
      ),
    );
  }

  Widget _buildCircleOfFifthsPage() {
    return _buildModeScaffold(
      showInstrument: false,
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final circleBox = math.min(
            520.0,
            math.max(
              200.0,
              math.min(constraints.maxWidth, constraints.maxHeight),
            ),
          );
          final media = MediaQuery.of(context);
          final dpr = media.devicePixelRatio;
          final circleStack = Stack(
            children: <Widget>[
              Positioned.fill(
                child: LayoutBuilder(
                  builder: (context, c) {
                    final sz = Size(c.maxWidth, c.maxHeight);
                    Offset? downLocal;
                    return GestureDetector(
                      onTapDown: (TapDownDetails d) =>
                          downLocal = d.localPosition,
                      onTap: () {
                        if (downLocal != null) {
                          _onCircleCanvasInteraction(
                            downLocal!,
                            sz,
                            longPress: false,
                          );
                        }
                      },
                      onLongPress: () {
                        if (downLocal != null) {
                          _onCircleCanvasInteraction(
                            downLocal!,
                            sz,
                            longPress: true,
                          );
                        }
                      },
                      child: CustomPaint(
                        painter: CircleOfFifthsPainter(
                          devicePixelRatio: dpr,
                          circleTonicPc: _circleTonicPc,
                          circleKeyMode: _circleKeyMode,
                          circleChordRootPc: _circleChordRootPc,
                          generatedChord: _generatedChordJson,
                          noteNameFromPc: _pcLabel,
                        ),
                        child: const SizedBox.expand(),
                      ),
                    );
                  },
                ),
              ),
              Positioned(
                top: 4,
                left: 4,
                child: _helpAnchor(
                  'circle_play',
                  _holdPlayButton(
                    enabled:
                        _generatedChordJson != null &&
                        _extractMidiList(_generatedChordJson!, <String>[
                          'notes_midi',
                        ]).isNotEmpty,
                    active: _generationPlayPressed,
                    label: null,
                    onDown: () async {
                      final notes = <int>[
                        if (_generatedChordJson != null)
                          ...(_instrumentView == 'guitar'
                              ? _selectedChordGuitarNotes()
                              : _extractMidiList(_generatedChordJson!, <String>[
                                  'notes_midi',
                                ])),
                      ]..sort();
                      if (notes.isEmpty) return;
                      _updateState(() => _generationPlayPressed = true);
                      await _startHeldChord(
                        notes,
                        instrument: _instrumentView == 'guitar'
                            ? 'guitar'
                            : 'piano',
                      );
                    },
                    onUp: () {
                      _stopHeldChord();
                      if (mounted) {
                        _updateState(() => _generationPlayPressed = false);
                      }
                    },
                  ),
                ),
              ),
            ],
          );
          final content = Center(
            child: _helpAnchor(
              'circle_canvas',
              SizedBox(width: circleBox, height: circleBox, child: circleStack),
            ),
          );
          if (compactPhone) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: content,
            );
          }
          return SizedBox(height: constraints.maxHeight, child: content);
        },
      ),
    );
  }

  Widget _buildScaleGenerationPage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          final metroLabelWidth = compact ? 96.0 : 110.0;
          final resultHeight = _scaleMetronomeOnly
              ? math.max(80.0, constraints.maxHeight - 310.0)
              : math.max(80.0, constraints.maxHeight - 270.0);
          final filteredPatterns = _getFilteredScalePatterns();
          // Ensure current pattern is valid for current filter
          final currentPatternValid = filteredPatterns.any(
            (p) => (p['name'] as String?) == _scalePatternName,
          );

          return Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              Expanded(
                child: SingleChildScrollView(
                  controller: _scaleControlsScrollController,
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        const SizedBox(height: 4),
                        // Row 1: Tonic selector
                        _buildTonicLetterAccidentalDropdowns(
                          rootPc: _scaleTonicPc,
                          savedLetterPc: _scaleTonicLetterPc,
                          savedAccidental: _scaleTonicAccidental,
                          letterHelpId: 'scales_tonic',
                          accidentalHelpId: 'scales_accidental',
                          helpAnchorHeight: 48,
                          onPc: (pc, letterPc, accidental) {
                            _updateState(() {
                              _scaleTonicPc = pc;
                              _scaleTonicLetterPc = letterPc;
                              _scaleTonicAccidental = accidental;
                            });
                            if (!_requestInFlight) {
                              unawaited(_callGenerateScale());
                            }
                          },
                        ),
                        const SizedBox(height: 4),
                        // Row 2: Scale type + Básicas/Todas toggle
                        Row(
                          children: <Widget>[
                            Expanded(
                              child: _helpFixedHeightAnchor(
                                'scales_pattern',
                                DropdownButtonFormField<String>(
                                  key: ValueKey<String>(
                                    'scale_${_scalePatternName}_$_scaleFilterMode',
                                  ),
                                  initialValue: currentPatternValid
                                      ? _scalePatternName
                                      : (filteredPatterns.isNotEmpty
                                            ? (filteredPatterns.first['name']
                                                      as String? ??
                                                  'Ionian')
                                            : 'Ionian'),
                                  isExpanded: true,
                                  dropdownColor: _HomeScreenState._surfaceDark,
                                  style: const TextStyle(
                                    color: _HomeScreenState._text,
                                  ),
                                  decoration: InputDecoration(
                                    labelText: _ui('Tipo', 'Type'),
                                    isDense: true,
                                    contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 10,
                                      vertical: 10,
                                    ),
                                  ),
                                  items: buildScaleDropdownItems(
                                    patterns: filteredPatterns,
                                    language: _language,
                                  ),
                                  onChanged: (value) {
                                    if (value == null) return;
                                    _updateState(
                                      () => _scalePatternName = value,
                                    );
                                    if (!_requestInFlight) {
                                      unawaited(_callGenerateScale());
                                    }
                                  },
                                ),
                                height: 48,
                              ),
                            ),
                            const SizedBox(width: 8),
                            _helpAnchor(
                              'scales_filter',
                              OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  backgroundColor: _scaleFilterMode == 'basic'
                                      ? _HomeScreenState._accent
                                      : _HomeScreenState._surfaceDark,
                                  foregroundColor: _scaleFilterMode == 'basic'
                                      ? const Color(0xFF1A222D)
                                      : _HomeScreenState._text,
                                  side: BorderSide(
                                    color: _scaleFilterMode == 'basic'
                                        ? _HomeScreenState._accent
                                        : _HomeScreenState._border,
                                  ),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 12,
                                  ),
                                ),
                                onPressed: () {
                                  _updateState(() {
                                    _scaleFilterMode =
                                        _scaleFilterMode == 'basic'
                                        ? 'all'
                                        : 'basic';
                                  });
                                },
                                child: Text(
                                  _scaleFilterMode == 'basic'
                                      ? _ui('Básicas', 'Basic')
                                      : _ui('Todas', 'All'),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        // Row 3: Play + Metro buttons (left) + Octaves selector (right)
                        Row(
                          children: <Widget>[
                            _helpAnchor(
                              'scales_play_button',
                              OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  backgroundColor: _scaleLoopRunning
                                      ? _HomeScreenState._accent
                                      : _HomeScreenState._surfaceDark,
                                  foregroundColor: _scaleLoopRunning
                                      ? const Color(0xFF1A222D)
                                      : _HomeScreenState._text,
                                  side: BorderSide(
                                    color: _scaleLoopRunning
                                        ? _HomeScreenState._accent
                                        : _HomeScreenState._border,
                                  ),
                                  padding: const EdgeInsets.all(10),
                                  minimumSize: const Size(40, 40),
                                ),
                                onPressed: _toggleScaleLoop,
                                child: Icon(
                                  _scaleLoopRunning
                                      ? Icons.stop
                                      : Icons.play_arrow,
                                  size: 20,
                                ),
                              ),
                            ),
                            const SizedBox(width: 6),
                            _helpAnchor(
                              'scales_metronome_only',
                              OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  backgroundColor: _scaleMetronomeOnly
                                      ? _HomeScreenState._accent
                                      : _HomeScreenState._surfaceDark,
                                  foregroundColor: _scaleMetronomeOnly
                                      ? const Color(0xFF1A222D)
                                      : _HomeScreenState._text,
                                  side: BorderSide(
                                    color: _scaleMetronomeOnly
                                        ? _HomeScreenState._accent
                                        : _HomeScreenState._border,
                                  ),
                                  padding: const EdgeInsets.all(10),
                                  minimumSize: const Size(40, 40),
                                ),
                                onPressed: () => _updateState(
                                  () => _scaleMetronomeOnly =
                                      !_scaleMetronomeOnly,
                                ),
                                child: const Text(
                                  '⏱',
                                  style: TextStyle(fontSize: 16),
                                ),
                              ),
                            ),
                            const Spacer(),
                            // Octaves: 1 / 2 / 3 — only for piano
                            if (_instrumentView != 'guitar')
                              _helpAnchor(
                                'scales_octaves',
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: <Widget>[
                                    Text(
                                      _ui('Octavas:', 'Octaves:'),
                                      style: const TextStyle(
                                        color: _HomeScreenState._muted,
                                        fontSize: 12,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    ...List<Widget>.generate(3, (i) {
                                      final oct = i + 1;
                                      final active = _scaleOctaves == oct;
                                      return Padding(
                                        padding: const EdgeInsets.only(left: 4),
                                        child: SizedBox(
                                          width: 32,
                                          height: 32,
                                          child: OutlinedButton(
                                            style: OutlinedButton.styleFrom(
                                              backgroundColor: active
                                                  ? _HomeScreenState._accent
                                                  : _HomeScreenState
                                                        ._surfaceDark,
                                              foregroundColor: active
                                                  ? const Color(0xFF1A222D)
                                                  : _HomeScreenState._text,
                                              side: BorderSide(
                                                color: active
                                                    ? _HomeScreenState._accent
                                                    : _HomeScreenState._border,
                                              ),
                                              padding: EdgeInsets.zero,
                                            ),
                                            onPressed: () {
                                              if (_scaleOctaves == oct) return;
                                              _updateState(() {
                                                _scaleOctaves = oct;
                                                _updateScaleFingeringsMap();
                                                _needsPianoScrollSync = true;
                                              });
                                              _savePrefs();
                                              if (_scaleLoopRunning) {
                                                _stopScaleLoop();
                                                unawaited(
                                                  Future<void>.delayed(
                                                    const Duration(
                                                      milliseconds: 50,
                                                    ),
                                                    _toggleScaleLoop,
                                                  ),
                                                );
                                              }
                                            },
                                            child: Text(
                                              '$oct',
                                              style: const TextStyle(
                                                fontSize: 13,
                                              ),
                                            ),
                                          ),
                                        ),
                                      );
                                    }),
                                  ],
                                ),
                              ),
                          ],
                        ),
                        if (_scaleMetronomeOnly) ...<Widget>[
                          const SizedBox(height: 8),
                          _helpAnchor(
                            'scales_volume',
                            Row(
                              children: <Widget>[
                                SizedBox(
                                  width: metroLabelWidth,
                                  child: Text(
                                    _ui('Volumen', 'Volume'),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      color: _HomeScreenState._muted,
                                    ),
                                  ),
                                ),
                                Expanded(
                                  child: Slider(
                                    min: 0,
                                    max: 100,
                                    divisions: 100,
                                    value: _metroVolume.toDouble(),
                                    onChanged: (value) => _updateState(
                                      () => _metroVolume = value.round(),
                                    ),
                                  ),
                                ),
                                SizedBox(
                                  width: compact ? 72 : 80,
                                  child: Text(
                                    '$_metroVolume%',
                                    textAlign: TextAlign.right,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                        const SizedBox(height: 2),
                        _helpAnchor(
                          'scales_bpm',
                          Row(
                            children: <Widget>[
                              SizedBox(
                                width: metroLabelWidth,
                                child: const Text(
                                  'BPM',
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Expanded(
                                child: Slider(
                                  min: 1,
                                  max: 300,
                                  divisions: 299,
                                  value: _scaleBpm.toDouble(),
                                  onChanged: (value) => _updateState(
                                    () => _scaleBpm = value.round(),
                                  ),
                                ),
                              ),
                              SizedBox(
                                width: compact ? 92 : 100,
                                child: Text(
                                  '$_scaleBpm BPM',
                                  textAlign: TextAlign.right,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 6),
                        ConstrainedBox(
                          constraints: BoxConstraints(maxHeight: resultHeight),
                          child: _buildScaleResultBlock(),
                        ),
                        if (_instrumentView != 'guitar') ...<Widget>[
                          const SizedBox(height: 10),
                          _helpAnchor(
                            'scales_fingering',
                            _buildScaleFingeringRow(),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 6),
              SizedBox(
                width: 8,
                child: RawScrollbar(
                  controller: _scaleControlsScrollController,
                  thumbVisibility: true,
                  thickness: 5,
                  radius: const Radius.circular(3),
                  thumbColor: const Color(0xFF6B7A99),
                  child: const SizedBox.expand(),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildGenerationHandRow({bool compact = false}) {
    const options = <(String, String, String)>[
      ('left', 'Izquierda', 'Left'),
      ('right', 'Derecha', 'Right'),
      ('both', 'Ambas', 'Both'),
    ];
    final enabled = _instrumentView == 'piano';
    return _helpAnchor(
      'generation_hand',
      Opacity(
        opacity: enabled ? 1 : 0.42,
        child: IgnorePointer(
          ignoring: !enabled,
          child: Container(
            padding: EdgeInsets.symmetric(
              horizontal: compact ? 8 : 12,
              vertical: compact ? 5 : 8,
            ),
            decoration: BoxDecoration(
              color: _HomeScreenState._surfaceDark,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _HomeScreenState._border),
            ),
            child: Row(
              children: <Widget>[
                Text(
                  _ui('Mano:', 'Hand:'),
                  maxLines: 1,
                  softWrap: false,
                  style: TextStyle(
                    color: _HomeScreenState._muted,
                    fontSize: compact ? 9 : 12,
                  ),
                ),
                SizedBox(width: compact ? 6 : 12),
                Expanded(
                  child: Wrap(
                    spacing: compact ? 7 : 12,
                    runSpacing: compact ? 3 : 6,
                    children: options.map((opt) {
                      final value = opt.$1;
                      final active = _generationHand == value;
                      return GestureDetector(
                        onTap: () =>
                            _updateState(() => _generationHand = value),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            Container(
                              width: compact ? 16 : 20,
                              height: compact ? 16 : 20,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: active
                                    ? _HomeScreenState._accent
                                    : Colors.transparent,
                                border: Border.all(
                                  color: active
                                      ? _HomeScreenState._accent
                                      : _HomeScreenState._muted,
                                  width: active ? 2 : 1.5,
                                ),
                              ),
                              child: active
                                  ? const Center(
                                      child: SizedBox(
                                        width: 8,
                                        height: 8,
                                        child: DecoratedBox(
                                          decoration: BoxDecoration(
                                            shape: BoxShape.circle,
                                            color: Color(0xFF1A222D),
                                          ),
                                        ),
                                      ),
                                    )
                                  : null,
                            ),
                            SizedBox(width: compact ? 3 : 6),
                            Text(
                              _language == 'en' ? opt.$3 : opt.$2,
                              maxLines: 1,
                              softWrap: false,
                              style: TextStyle(
                                color: _HomeScreenState._text,
                                fontSize: compact ? 9 : 12,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildScaleFingeringRow() {
    const options = <(String, String, String)>[
      ('none', 'Sin', 'None'),
      ('left', 'Izquierda', 'Left'),
      ('right', 'Derecha', 'Right'),
    ];
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: _HomeScreenState._surfaceDark,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _HomeScreenState._border),
      ),
      child: Row(
        children: <Widget>[
          Text(
            _ui('Digitación:', 'Fingering:'),
            style: const TextStyle(
              color: _HomeScreenState._muted,
              fontSize: 12,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Wrap(
              spacing: 8,
              runSpacing: 6,
              children: options.map(((String, String, String) opt) {
                final value = opt.$1;
                final label = _language == 'en' ? opt.$3 : opt.$2;
                final active = (_scaleFingeringHand ?? 'none') == value;
                return GestureDetector(
                  onTap: () {
                    final hand = value == 'none' ? null : value;
                    _updateState(() {
                      _scaleFingeringHand = hand;
                      _updateScaleFingeringsMap();
                      // Activar/desactivar las tiras cambia la altura
                      // disponible del piano y por tanto el ancho de tecla;
                      // hay que recentrar el scroll para que las tiras y
                      // las teclas queden alineadas de nuevo.
                      _needsPianoScrollSync = true;
                    });
                    _savePrefs();
                  },
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: active
                                ? _HomeScreenState._accent
                                : Colors.transparent,
                            border: Border.all(
                              color: active
                                  ? _HomeScreenState._accent
                                  : _HomeScreenState._muted,
                              width: active ? 2 : 1.5,
                            ),
                          ),
                          child: active
                              ? const Center(
                                  child: SizedBox(
                                    width: 8,
                                    height: 8,
                                    child: DecoratedBox(
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Color(0xFF1A222D),
                                      ),
                                    ),
                                  ),
                                )
                              : const SizedBox.shrink(),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(label, style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIntervalDetectionPage() {
    final intervalAlternativeNames = _getIntervalAltNames();
    final intervalDisplayName = _intervalNotes.length < 2
        ? '-'
        : <String>[
            _getIntervalName(),
            if (intervalAlternativeNames.isNotEmpty &&
                intervalAlternativeNames != '-')
              intervalAlternativeNames,
          ].join(', ');
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  if (!compactLandscape) ...<Widget>[
                    Text(
                      _ui('Detección de Intervalos', 'Interval Detection'),
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  if (compactLandscape) ...<Widget>[
                    _buildCompactIntervalDetectionButtons(),
                    const SizedBox(height: 6),
                  ],
                  if (_intervalDetailsVisible)
                    Container(
                      padding: EdgeInsets.all(compactLandscape ? 6 : 12),
                      decoration: BoxDecoration(
                        color: _HomeScreenState._surfaceDark,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: _HomeScreenState._border,
                          width: 1,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          // Notes display
                          _helpAnchor(
                            'interval_notes_row',
                            Row(
                              children: <Widget>[
                                Text(
                                  '${_ui('Notas', 'Notes')}:',
                                  style: TextStyle(
                                    color: _HomeScreenState._muted,
                                    fontSize: compactLandscape ? 10 : 12,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  _intervalNotes.isEmpty
                                      ? '-'
                                      : (List<int>.from(_intervalNotes)..sort())
                                            .map(_midiNoteWithOctave)
                                            .join(' – '),
                                  style: TextStyle(
                                    color: _HomeScreenState._accent,
                                    fontSize: compactLandscape ? 11 : 14,
                                    fontFamily: 'Courier',
                                  ),
                                ),
                              ],
                            ),
                          ),
                          SizedBox(height: compactLandscape ? 4 : 12),
                          // Interval name
                          _helpAnchor(
                            'interval_name_row',
                            Row(
                              children: <Widget>[
                                Text(
                                  '${_ui('Intervalo', 'Interval')}:',
                                  style: TextStyle(
                                    color: _HomeScreenState._muted,
                                    fontSize: compactLandscape ? 10 : 12,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    intervalDisplayName,
                                    textAlign: TextAlign.left,
                                    softWrap: true,
                                    maxLines: compactLandscape ? 2 : null,
                                    overflow: compactLandscape
                                        ? TextOverflow.ellipsis
                                        : null,
                                    style: TextStyle(
                                      color: _HomeScreenState._accent,
                                      fontSize: compactLandscape ? 11 : 14,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          SizedBox(height: compactLandscape ? 4 : 12),
                          // Semitones
                          _helpAnchor(
                            'interval_semitones_row',
                            Row(
                              children: <Widget>[
                                Text(
                                  '${_ui('Semitonos', 'Semitones')}:',
                                  style: TextStyle(
                                    color: _HomeScreenState._muted,
                                    fontSize: compactLandscape ? 10 : 12,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  _intervalNotes.length >= 2
                                      ? (_getIntervalSemitones()?.toString() ??
                                            '-')
                                      : '-',
                                  style: TextStyle(
                                    color: _HomeScreenState._accent,
                                    fontSize: compactLandscape ? 11 : 14,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          SizedBox(height: compactLandscape ? 4 : 12),
                          // Melody name — tappable toggle
                          _helpAnchor(
                            'interval_melody_row',
                            Row(
                              children: <Widget>[
                                Text(
                                  '${_ui('Ejemplo', 'Example')}:',
                                  style: TextStyle(
                                    color: _HomeScreenState._muted,
                                    fontSize: compactLandscape ? 10 : 12,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: GestureDetector(
                                    onTap: _intervalNotes.length >= 2
                                        ? _toggleIntervalMelodyMode
                                        : null,
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 6,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: _intervalMelodyMode
                                            ? const Color(0x26F3BF2F)
                                            : Colors.transparent,
                                        borderRadius: BorderRadius.circular(6),
                                        border: Border.all(
                                          color: _intervalMelodyMode
                                              ? _HomeScreenState._accent
                                              : _HomeScreenState._border,
                                        ),
                                      ),
                                      child: Text(
                                        _intervalNotes.length >= 2
                                            ? _getIntervalMelodyName()
                                            : '-',
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          color: _intervalMelodyMode
                                              ? _HomeScreenState._accent
                                              : const Color(0xFFE9EDF2),
                                          fontSize: compactLandscape ? 10 : 13,
                                        ),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  if (!compactLandscape) const SizedBox(height: 16),
                  // Buttons
                  if (!compactLandscape)
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: <Widget>[
                        _helpAnchor(
                          'interval_play_btn',
                          ElevatedButton.icon(
                            onPressed: _intervalNotes.length >= 2
                                ? () => _playIntervalMelody()
                                : null,
                            icon: const Icon(Icons.play_arrow),
                            label: Text(_ui('Reproducir', 'Play')),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _HomeScreenState._accent,
                              foregroundColor: Colors.black,
                              disabledBackgroundColor: _HomeScreenState._panelA,
                            ),
                          ),
                        ),
                        _helpAnchor(
                          'interval_play_reverse_btn',
                          ElevatedButton.icon(
                            onPressed:
                                _intervalNotes.length >= 2 &&
                                    !_intervalMelodyMode
                                ? () => _playIntervalMelody(reversed: true)
                                : null,
                            icon: const Icon(Icons.play_arrow),
                            label: Text(_ui('Desc.', 'Rev.')),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: _HomeScreenState._accent,
                              foregroundColor: Colors.black,
                              disabledBackgroundColor: _HomeScreenState._panelA,
                            ),
                          ),
                        ),
                        _helpAnchor(
                          'interval_clear_btn',
                          OutlinedButton(
                            onPressed: _intervalNotes.isEmpty
                                ? null
                                : _clearIntervalNotes,
                            child: Text(_ui('Limpiar', 'Clear')),
                          ),
                        ),
                        _helpAnchor(
                          'interval_details_toggle',
                          OutlinedButton.icon(
                            onPressed: () => _updateState(
                              () => _intervalDetailsVisible =
                                  !_intervalDetailsVisible,
                            ),
                            icon: const Icon(Icons.visibility),
                            label: Text(
                              _intervalDetailsVisible
                                  ? _ui('Ocultar', 'Hide')
                                  : _ui('Mostrar', 'Show'),
                            ),
                            style: OutlinedButton.styleFrom(
                              backgroundColor: _intervalDetailsVisible
                                  ? null
                                  : _HomeScreenState._accent,
                              foregroundColor: _intervalDetailsVisible
                                  ? null
                                  : _HomeScreenState._surfaceDark,
                            ),
                          ),
                        ),
                      ],
                    ),
                  if (!compactLandscape) ...<Widget>[
                    const SizedBox(height: 12),
                    Text(
                      _ui(
                        'Pulsa dos notas en el piano para detectar el intervalo',
                        'Press two notes on the piano to detect the interval',
                      ),
                      style: const TextStyle(
                        color: _HomeScreenState._muted,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCompactIntervalDetectionButtons() {
    ButtonStyle style({bool filled = false}) => OutlinedButton.styleFrom(
      minimumSize: const Size(0, 32),
      padding: const EdgeInsets.symmetric(horizontal: 7),
      visualDensity: VisualDensity.compact,
      backgroundColor: filled ? _HomeScreenState._accent : null,
      foregroundColor: filled ? Colors.black : null,
      disabledBackgroundColor: filled ? _HomeScreenState._panelA : null,
      textStyle: const TextStyle(fontSize: 10),
    );

    return Wrap(
      spacing: 4,
      runSpacing: 4,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: <Widget>[
        _helpAnchor(
          'interval_play_btn',
          OutlinedButton.icon(
            onPressed: _intervalNotes.length >= 2
                ? () => _playIntervalMelody()
                : null,
            icon: const Icon(Icons.play_arrow, size: 15),
            label: Text(_ui('Reproducir', 'Play')),
            style: style(filled: true),
          ),
        ),
        _helpAnchor(
          'interval_play_reverse_btn',
          OutlinedButton.icon(
            onPressed: _intervalNotes.length >= 2 && !_intervalMelodyMode
                ? () => _playIntervalMelody(reversed: true)
                : null,
            icon: const Icon(Icons.play_arrow, size: 15),
            label: Text(_ui('Desc.', 'Rev.')),
            style: style(filled: true),
          ),
        ),
        _helpAnchor(
          'interval_clear_btn',
          OutlinedButton(
            onPressed: _intervalNotes.isEmpty ? null : _clearIntervalNotes,
            style: style(),
            child: Text(_ui('Limpiar', 'Clear')),
          ),
        ),
        _helpAnchor(
          'interval_details_toggle',
          OutlinedButton.icon(
            onPressed: () => _updateState(
              () => _intervalDetailsVisible = !_intervalDetailsVisible,
            ),
            icon: const Icon(Icons.visibility, size: 15),
            label: Text(
              _intervalDetailsVisible
                  ? _ui('Ocultar', 'Hide')
                  : _ui('Mostrar', 'Show'),
            ),
            style: style(filled: !_intervalDetailsVisible),
          ),
        ),
      ],
    );
  }

  Widget _buildIntervalGenerationPage() {
    final notes = _intervalGenerationNotes();
    final generatedIntervalName = _intervalGenSelected
        ? intervalGridDisplayNames(
            selectedCategoryKey: _intervalGenCategoryKey,
            selectedLabel: _intervalGenLabel,
            semitones: _intervalGenSemitones,
            language: _language,
          ).join(', ')
        : '-';
    return _buildModeScaffold(
      showInstrument: false,
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactPhone = _isCompactPhone(context);
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  if (!compactLandscape) ...<Widget>[
                    Text(
                      _ui('Generación de Intervalos', 'Interval Generation'),
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 4),
                  ],
                  Row(
                    children: <Widget>[
                      Expanded(
                        child: _helpAnchor(
                          'interval_generation_root',
                          _buildTonicLetterAccidentalDropdowns(
                            rootPc: _intervalGenRootPc,
                            savedLetterPc: _intervalGenRootLetterPc,
                            savedAccidental: _intervalGenRootAccidental,
                            onPc: (pc, letterPc, accidental) {
                              _intervalGenPlaybackTimer?.cancel();
                              _updateState(() {
                                _intervalGenRootPc = pc;
                                _intervalGenRootLetterPc = letterPc;
                                _intervalGenRootAccidental = accidental;
                                _intervalGenPlayingIdx = null;
                              });
                              _playGeneratedInterval();
                            },
                            compact: compactPhone,
                            hideLabel: compactPhone,
                          ),
                        ),
                      ),
                      SizedBox(width: compactPhone ? 4 : 8),
                      _helpAnchor(
                        'interval_generation_playback_mode',
                        OutlinedButton(
                          onPressed: _toggleIntervalGenerationPlaybackMode,
                          style: compactPhone
                              ? OutlinedButton.styleFrom(
                                  minimumSize: const Size(0, 40),
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 10,
                                  ),
                                  visualDensity: VisualDensity.compact,
                                )
                              : null,
                          child: Text(
                            _intervalGenHarmonic
                                ? _ui('Armónico', 'Harmonic')
                                : _ui('Melódico', 'Melodic'),
                          ),
                        ),
                      ),
                      SizedBox(width: compactPhone ? 4 : 6),
                      _intervalGenerationPlayButton(
                        helpId: 'interval_generation_play_reverse',
                        tooltip: _ui(
                          'Reproducir descendente y mantener ese patrón',
                          'Play descending and keep that pattern',
                        ),
                        icon: Icons.arrow_left,
                        compact: compactPhone,
                        selected: _intervalGenLastPlayReversed == true,
                        onPressed: !_intervalGenSelected || _intervalGenHarmonic
                            ? null
                            : () => _playGeneratedIntervalFromButton(
                                reversed: true,
                              ),
                      ),
                      SizedBox(width: compactPhone ? 4 : 6),
                      _intervalGenerationPlayButton(
                        helpId: 'interval_generation_play',
                        tooltip: _ui(
                          'Reproducir ascendente y mantener ese patrón',
                          'Play ascending and keep that pattern',
                        ),
                        icon: Icons.arrow_right,
                        compact: compactPhone,
                        selected: _intervalGenLastPlayReversed == false,
                        onPressed: _intervalGenSelected
                            ? () => _playGeneratedIntervalFromButton(
                                reversed: false,
                              )
                            : null,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: _HomeScreenState._surfaceDark,
                      border: Border.all(color: _HomeScreenState._border),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: <Widget>[
                        Row(
                          children: <Widget>[
                            Expanded(
                              flex: 2,
                              child: _intervalGenerationResultRow(
                                _ui('Notas', 'Notes'),
                                notes.isEmpty
                                    ? '-'
                                    : notes
                                          .map(_midiNoteWithOctave)
                                          .join(' – '),
                                helpId: 'interval_generation_notes',
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _intervalGenerationResultRow(
                                _ui('Semitonos', 'Semitones'),
                                _intervalGenSelected
                                    ? '$_intervalGenSemitones'
                                    : '-',
                                helpId: 'interval_generation_semitones',
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        _intervalGenerationResultRow(
                          _ui('Intervalo', 'Interval'),
                          generatedIntervalName,
                          helpId: 'interval_generation_name',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 6),
                  if (!_isCompactPhone(context)) ...<Widget>[
                    Text(
                      _ui('Selecciona un intervalo', 'Select an interval'),
                      style: const TextStyle(
                        color: _HomeScreenState._muted,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 2),
                  ],
                  _helpAnchor(
                    'interval_generation_table',
                    _buildIntervalGenerationTable(constraints.maxWidth),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildIntervalGenerationTable(double availableWidth) {
    final compactPhone = _isCompactPhone(context);
    final tableWidth = compactPhone
        ? availableWidth
        : math.max(650.0, availableWidth);
    final cellHeight = compactPhone ? 28.0 : 34.0;
    final cellHorizontalPadding = compactPhone ? 0.0 : 3.0;
    final categoryColumnWidth = compactPhone ? 76.0 : 104.0;
    Widget tableCell(
      String text, {
      bool header = false,
      bool selected = false,
      VoidCallback? onTap,
    }) {
      final content = Container(
        height: cellHeight,
        alignment: Alignment.center,
        color: selected
            ? _HomeScreenState._accent
            : (header
                  ? const Color(0xFF17273A)
                  : _HomeScreenState._surfaceDark),
        padding: EdgeInsets.symmetric(horizontal: cellHorizontalPadding),
        child: Text(
          text,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: selected
                ? Colors.black
                : (header ? _HomeScreenState._muted : _HomeScreenState._text),
            fontSize: compactPhone ? (header ? 10 : 11) : (header ? 11 : 12),
            fontWeight: selected || header ? FontWeight.w700 : FontWeight.w600,
          ),
        ),
      );
      if (onTap == null) return content;
      return GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: content,
      );
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: tableWidth,
        child: Table(
          border: TableBorder.all(color: const Color(0xFF5A6A82), width: 1),
          columnWidths: <int, TableColumnWidth>{
            0: FixedColumnWidth(categoryColumnWidth),
          },
          defaultColumnWidth: const FlexColumnWidth(),
          children: <TableRow>[
            TableRow(
              children: <Widget>[
                tableCell('', header: true),
                for (var semitones = 0; semitones <= 12; semitones += 1)
                  tableCell('$semitones', header: true),
              ],
            ),
            for (final category in intervalGridCategories)
              TableRow(
                children: <Widget>[
                  tableCell(category.name(_language), header: true),
                  for (var semitones = 0; semitones <= 12; semitones += 1)
                    () {
                      final matching = category.cells
                          .where((cell) => cell.semitones == semitones)
                          .toList();
                      if (matching.isEmpty) return tableCell('');
                      final cell = matching.first;
                      final selected =
                          _intervalGenSelected &&
                          category.key == _intervalGenCategoryKey &&
                          cell.label == _intervalGenLabel;
                      return tableCell(
                        cell.label,
                        selected: selected,
                        onTap: () => _selectGeneratedInterval(category, cell),
                      );
                    }(),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _intervalGenerationPlayButton({
    required String helpId,
    required String tooltip,
    required IconData icon,
    required bool compact,
    required bool selected,
    required VoidCallback? onPressed,
  }) {
    return _helpAnchor(
      helpId,
      Tooltip(
        message: tooltip,
        child: SizedBox(
          width: compact ? 38 : 46,
          height: compact ? 40 : 48,
          child: ElevatedButton(
            onPressed: onPressed,
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.zero,
              backgroundColor: selected
                  ? _HomeScreenState._accent
                  : _HomeScreenState._surfaceDark,
              foregroundColor: selected ? Colors.black : _HomeScreenState._text,
              side: BorderSide(
                color: selected
                    ? _HomeScreenState._accent
                    : _HomeScreenState._border,
              ),
            ),
            child: Icon(icon, size: compact ? 28 : 34),
          ),
        ),
      ),
    );
  }

  Widget _intervalGenerationResultRow(
    String label,
    String value, {
    required String helpId,
  }) {
    return _helpAnchor(
      helpId,
      Row(
        children: <Widget>[
          Text(
            '$label:',
            style: const TextStyle(
              color: _HomeScreenState._muted,
              fontSize: 12,
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.left,
              style: const TextStyle(
                color: _HomeScreenState._accent,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _midiNoteWithOctave(int midiNote) {
    final octave = (midiNote ~/ 12) - 1;
    return '${_pcLabel(midiNote % 12)}$octave';
  }

  Widget _buildMetronomePage() {
    return _buildModeScaffold(
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          final iphoneCompact = Platform.isIOS && _isCompactPhone(context);
          final sliderWidth = math.max(
            60.0,
            compact ? constraints.maxWidth - 24 : constraints.maxWidth - 170,
          );
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  if (!compactLandscape) ...<Widget>[
                    Text(
                      _ui('Configuración de Metrónomo', 'Metronome settings'),
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 6),
                  ],
                  _helpAnchor(
                    'metronome_volume',
                    Wrap(
                      spacing: 12,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: <Widget>[
                        SizedBox(
                          width: compact ? constraints.maxWidth : 84,
                          child: Text(
                            _ui('Volumen', 'Volume'),
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: _HomeScreenState._muted,
                            ),
                          ),
                        ),
                        SizedBox(
                          width: sliderWidth,
                          child: Row(
                            children: <Widget>[
                              Expanded(
                                child: Slider(
                                  min: 0,
                                  max: 100,
                                  divisions: 100,
                                  value: _metroVolume.toDouble(),
                                  onChanged: (value) {
                                    _updateState(
                                      () => _metroVolume = value.round(),
                                    );
                                  },
                                ),
                              ),
                              SizedBox(
                                width: 72,
                                child: Text(
                                  '$_metroVolume%',
                                  textAlign: TextAlign.right,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_tempo',
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          _ui('Tempo (BPM)', 'Tempo (BPM)'),
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            color: _HomeScreenState._muted,
                          ),
                        ),
                        Row(
                          children: <Widget>[
                            IconButton(
                              onPressed: () {
                                _updateState(
                                  () => _metroBpm = (_metroBpm - 1).clamp(
                                    40,
                                    220,
                                  ),
                                );
                                if (_metroRunning) _startMetronome();
                              },
                              icon: const Icon(Icons.remove),
                            ),
                            Expanded(
                              child: Slider(
                                min: 40,
                                max: 220,
                                divisions: 180,
                                value: _metroBpm.toDouble(),
                                onChanged: (value) {
                                  _updateState(() => _metroBpm = value.round());
                                  if (_metroRunning) {
                                    _startMetronome();
                                  }
                                },
                              ),
                            ),
                            IconButton(
                              onPressed: () {
                                _updateState(
                                  () => _metroBpm = (_metroBpm + 1).clamp(
                                    40,
                                    220,
                                  ),
                                );
                                if (_metroRunning) _startMetronome();
                              },
                              icon: const Icon(Icons.add),
                            ),
                            SizedBox(
                              width: 72,
                              child: Text(
                                '$_metroBpm',
                                textAlign: TextAlign.right,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_beats',
                    Wrap(
                      spacing: 10,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: <Widget>[
                        Text(_ui('Pulsos por compás:', 'Beats per bar:')),
                        if (!iphoneCompact)
                          IconButton(
                            onPressed: () {
                              _updateState(() {
                                _metroBeatsPerBar = (_metroBeatsPerBar - 1)
                                    .clamp(1, 16);
                                _metroCurrentBeat = -1;
                              });
                              if (_metroRunning) _startMetronome();
                            },
                            icon: const Icon(Icons.remove),
                          ),
                        SizedBox(
                          width: 72,
                          child: DropdownButton<int>(
                            isExpanded: true,
                            value: _metroBeatsPerBar,
                            items: List<DropdownMenuItem<int>>.generate(
                              16,
                              (i) => DropdownMenuItem<int>(
                                value: i + 1,
                                child: Text('${i + 1}'),
                              ),
                            ),
                            onChanged: (value) {
                              if (value == null) {
                                return;
                              }
                              _updateState(() {
                                _metroBeatsPerBar = value;
                                _metroCurrentBeat = -1;
                              });
                              if (_metroRunning) {
                                _startMetronome();
                              }
                            },
                          ),
                        ),
                        if (!iphoneCompact)
                          IconButton(
                            onPressed: () {
                              _updateState(() {
                                _metroBeatsPerBar = (_metroBeatsPerBar + 1)
                                    .clamp(1, 16);
                                _metroCurrentBeat = -1;
                              });
                              if (_metroRunning) _startMetronome();
                            },
                            icon: const Icon(Icons.add),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_subdivision',
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: <Widget>[
                        Text(_ui('Subdivisión:', 'Subdivision:')),
                        const SizedBox(width: 10),
                        Expanded(
                          child: SingleChildScrollView(
                            scrollDirection: Axis.horizontal,
                            child: Row(
                              children: <Widget>[
                                ...<int>[1, 2, 3, 4, 6].map((n) {
                                  final active = _metroClicksPerBeat == n;
                                  return Padding(
                                    padding: const EdgeInsets.only(right: 8),
                                    child: ChoiceChip(
                                      selected: active,
                                      label: _metronomeSubdivisionFigure(
                                        n,
                                        active: active,
                                      ),
                                      labelPadding: const EdgeInsets.symmetric(
                                        horizontal: 4,
                                      ),
                                      visualDensity: VisualDensity.compact,
                                      materialTapTargetSize:
                                          MaterialTapTargetSize.shrinkWrap,
                                      onSelected: (_) {
                                        _updateState(
                                          () => _metroClicksPerBeat = n,
                                        );
                                        if (_metroRunning) _startMetronome();
                                      },
                                    ),
                                  );
                                }),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'metronome_HomeScreenState._accent',
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: <Widget>[
                        Checkbox(
                          visualDensity: VisualDensity.compact,
                          materialTapTargetSize:
                              MaterialTapTargetSize.shrinkWrap,
                          value: _metroBarAccent,
                          onChanged: (value) {
                            _updateState(() => _metroBarAccent = value ?? true);
                          },
                        ),
                        Flexible(
                          child: Text(_ui('Acento de compás', 'Bar accent')),
                        ),
                      ],
                    ),
                  ),
                  _helpAnchor(
                    'metronome_timer',
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: <Widget>[
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: <Widget>[
                            Checkbox(
                              visualDensity: VisualDensity.compact,
                              materialTapTargetSize:
                                  MaterialTapTargetSize.shrinkWrap,
                              value: _metroTimerEnabled,
                              onChanged: (value) {
                                _updateState(
                                  () => _metroTimerEnabled = value ?? false,
                                );
                              },
                            ),
                            Text(
                              _isCompactPhone(context)
                                  ? _ui('Timer', 'Timer')
                                  : _ui('Temporizador', 'Timer'),
                            ),
                          ],
                        ),
                        SizedBox(
                          width: 78,
                          child: DropdownButton<int>(
                            isExpanded: true,
                            value: _metroTimerMinutes.clamp(0, 99),
                            items: List<DropdownMenuItem<int>>.generate(
                              100,
                              (i) => DropdownMenuItem<int>(
                                value: i,
                                child: Text(i.toString().padLeft(2, '0')),
                              ),
                            ),
                            onChanged: (value) {
                              if (value != null) {
                                _updateState(() => _metroTimerMinutes = value);
                              }
                            },
                          ),
                        ),
                        const Text(':'),
                        SizedBox(
                          width: 78,
                          child: DropdownButton<int>(
                            isExpanded: true,
                            value: _metroTimerSeconds.clamp(0, 59),
                            items: List<DropdownMenuItem<int>>.generate(
                              60,
                              (i) => DropdownMenuItem<int>(
                                value: i,
                                child: Text(i.toString().padLeft(2, '0')),
                              ),
                            ),
                            onChanged: (value) {
                              if (value != null) {
                                _updateState(() => _metroTimerSeconds = value);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _metronomeSubdivisionFigure(int clicks, {required bool active}) {
    final fg = active ? const Color(0xFF1A222D) : _HomeScreenState._text;
    if (clicks == 3 || clicks == 6) {
      final glyph = clicks == 3 ? '♪♪♪' : '♬♬';
      return Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.only(right: 2),
            child: Text(
              '$clicks',
              style: TextStyle(
                color: fg,
                fontSize: 10,
                fontWeight: FontWeight.w800,
                height: 1.0,
              ),
            ),
          ),
          Text(
            glyph,
            style: TextStyle(
              color: fg,
              fontSize: 14,
              fontWeight: FontWeight.w700,
              height: 1.0,
            ),
          ),
        ],
      );
    }
    final glyph = switch (clicks) {
      1 => '♩',
      2 => '♪♪',
      4 => '♬',
      _ => '$clicks',
    };
    return Text(
      glyph,
      style: TextStyle(
        color: fg,
        fontSize: 17,
        fontWeight: FontWeight.w700,
        height: 1.0,
      ),
    );
  }

  Widget _buildTunerPage() {
    final meter = (_tunerCents + 50) / 100.0;
    return _buildModeScaffold(
      showInstrument: false,
      bottomPanel: _buildTunerSpectrumPanel(),
      controls: LayoutBuilder(
        builder: (context, constraints) {
          final compactLandscape = _isCompactLandscapePhoneForConstraints(
            context,
            constraints,
          );
          return SingleChildScrollView(
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: constraints.maxHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  if (!compactLandscape) ...<Widget>[
                    Text(
                      _ui('Configuración de Afinador', 'Tuner settings'),
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],
                  _helpAnchor(
                    'tuner_toggle',
                    FilledButton.icon(
                      onPressed: _toggleTuner,
                      icon: Icon(_tunerRunning ? Icons.stop : Icons.play_arrow),
                      label: Text(
                        _tunerRunning
                            ? _ui('Detener afinador', 'Stop tuner')
                            : _ui('Iniciar afinador', 'Start tuner'),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'tuner_tuning_select',
                    Row(
                      children: <Widget>[
                        SizedBox(
                          width: 96,
                          child: Text(
                            _ui('Afinación', 'Tuning'),
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: _HomeScreenState._muted,
                            ),
                          ),
                        ),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            key: ValueKey<String>('tuner_tuning_$_tunerTuning'),
                            initialValue: _tunerTuning,
                            dropdownColor: _HomeScreenState._surfaceDark,
                            decoration: const InputDecoration(isDense: true),
                            items: <DropdownMenuItem<String>>[
                              DropdownMenuItem<String>(
                                value: 'standard_e',
                                child: Text(
                                  _language == 'en'
                                      ? 'Standard E'
                                      : 'E estándar',
                                ),
                              ),
                              const DropdownMenuItem<String>(
                                value: 'drop_d',
                                child: Text('Drop D'),
                              ),
                              DropdownMenuItem<String>(
                                value: 'half_step_down',
                                child: Text(
                                  _language == 'en'
                                      ? 'Half-step down'
                                      : '1/2 tono abajo',
                                ),
                              ),
                            ],
                            onChanged: (value) {
                              if (value != null) {
                                _updateState(() => _tunerTuning = value);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  _helpAnchor(
                    'tuner_gain',
                    Row(
                      children: <Widget>[
                        SizedBox(
                          width: 96,
                          child: Text(
                            _ui('Ganancia', 'Gain'),
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: _HomeScreenState._muted,
                            ),
                          ),
                        ),
                        IconButton(
                          onPressed: () => _updateState(
                            () => _tunerInputGain = (_tunerInputGain - 0.01)
                                .clamp(0.0, 2.0),
                          ),
                          icon: const Icon(Icons.remove),
                        ),
                        Expanded(
                          child: Slider(
                            min: 0.0,
                            max: 2.0,
                            divisions: 200,
                            value: _tunerInputGain,
                            onChanged: (value) =>
                                _updateState(() => _tunerInputGain = value),
                          ),
                        ),
                        IconButton(
                          onPressed: () => _updateState(
                            () => _tunerInputGain = (_tunerInputGain + 0.01)
                                .clamp(0.0, 2.0),
                          ),
                          icon: const Icon(Icons.add),
                        ),
                        SizedBox(
                          width: 54,
                          child: Text('${(_tunerInputGain * 100).round()}%'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 6),
                  _helpAnchor(
                    'tuner_range',
                    Row(
                      children: <Widget>[
                        SizedBox(
                          width: 96,
                          child: Text(
                            _ui('Rango Hz', 'Hz range'),
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              color: _HomeScreenState._muted,
                            ),
                          ),
                        ),
                        SizedBox(
                          width: 74,
                          child: DropdownButton<int>(
                            value: _tunerRangeMin,
                            dropdownColor: _HomeScreenState._surfaceDark,
                            items: List<DropdownMenuItem<int>>.generate(
                              300,
                              (i) => DropdownMenuItem<int>(
                                value: i * 10,
                                child: Text('${i * 10}'),
                              ),
                            ),
                            onChanged: (value) {
                              if (value == null) return;
                              _updateState(() {
                                _tunerRangeMin = value.clamp(0, 2990);
                                if (_tunerRangeMax <= _tunerRangeMin) {
                                  _tunerRangeMax = (_tunerRangeMin + 10).clamp(
                                    10,
                                    3000,
                                  );
                                }
                              });
                            },
                          ),
                        ),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 8),
                          child: Text('-'),
                        ),
                        SizedBox(
                          width: 74,
                          child: DropdownButton<int>(
                            value: _tunerRangeMax,
                            dropdownColor: _HomeScreenState._surfaceDark,
                            items: List<DropdownMenuItem<int>>.generate(
                              300,
                              (i) => DropdownMenuItem<int>(
                                value: (i + 1) * 10,
                                child: Text('${(i + 1) * 10}'),
                              ),
                            ),
                            onChanged: (value) {
                              if (value == null) return;
                              _updateState(() {
                                _tunerRangeMax = value.clamp(
                                  _tunerRangeMin + 1,
                                  3000,
                                );
                              });
                            },
                          ),
                        ),
                        const SizedBox(width: 6),
                        const Text(
                          'Hz',
                          style: TextStyle(color: _HomeScreenState._muted),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  _helpAnchor(
                    'tuner_readout',
                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: _HomeScreenState._surfaceDark,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: _HomeScreenState._border),
                      ),
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: <Widget>[
                          Text('Nota: $_tunerNote'),
                          const SizedBox(height: 4),
                          Text(
                            'Desviación: ${_tunerCents >= 0 ? '+' : ''}$_tunerCents cents',
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Frecuencia: ${_tunerFreq.toStringAsFixed(1)} Hz',
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    height: 20,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(10),
                      color: const Color(0xFFCBD3DD),
                    ),
                    child: Stack(
                      children: <Widget>[
                        Positioned.fill(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 2),
                            child: LayoutBuilder(
                              builder: (context, constraints) {
                                final knobX =
                                    (constraints.maxWidth - 16) * meter;
                                return Stack(
                                  children: <Widget>[
                                    Positioned(
                                      left: knobX,
                                      top: 2,
                                      child: Container(
                                        width: 16,
                                        height: 16,
                                        decoration: const BoxDecoration(
                                          shape: BoxShape.circle,
                                          color: Colors.blue,
                                        ),
                                      ),
                                    ),
                                  ],
                                );
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (_tunerError.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Error: $_tunerError',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTunerSpectrumPanel() {
    return _panel(
      child: SizedBox(
        height: 220,
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF0B1018),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF2F3743)),
          ),
          child: CustomPaint(
            painter: _MiniTunerSpectrumPainter(
              rangeMinHz: _tunerRangeMin.toDouble(),
              rangeMaxHz: _tunerRangeMax.toDouble(),
              currentFreq: _tunerFreq,
              currentStringIdx: _tunerCurrentStringIdx,
              tuningLabels: _tunerOpenLabelsForCurrentTuning(),
              tuningFreqs: _tunerOpenFreqsForCurrentTuning(),
              spectrumBins: _tunerSpectrumBins,
            ),
            child: const SizedBox.expand(),
          ),
        ),
      ),
    );
  }

  Widget _panel({required Widget child}) {
    final compactLandscape =
        _isCompactPhone(context) &&
        MediaQuery.of(context).orientation == Orientation.landscape;
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: <Color>[_HomeScreenState._panelA, _HomeScreenState._panelB],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _HomeScreenState._border),
      ),
      padding: EdgeInsets.all(compactLandscape ? 8 : 12),
      child: child,
    );
  }

  Widget _holdPlayButton({
    required bool enabled,
    required bool active,
    required Future<void> Function() onDown,
    required VoidCallback onUp,
    String? label,
    bool compact = false,
  }) {
    final hasLabel = (label != null && label.trim().isNotEmpty);
    return Listener(
      onPointerDown: (_) {
        if (!enabled) return;
        unawaited(onDown());
      },
      onPointerUp: (_) {
        if (!enabled) return;
        onUp();
      },
      onPointerCancel: (_) {
        if (!enabled) return;
        onUp();
      },
      child: hasLabel
          ? FilledButton.icon(
              style: FilledButton.styleFrom(
                backgroundColor: active
                    ? _HomeScreenState._accent
                    : _HomeScreenState._surfaceDark,
                foregroundColor: active
                    ? const Color(0xFF1A222D)
                    : _HomeScreenState._text,
              ),
              onPressed: enabled ? () {} : null,
              icon: const Icon(Icons.play_arrow),
              label: Text(label),
            )
          : FilledButton(
              style: FilledButton.styleFrom(
                minimumSize: Size(compact ? 34 : 46, compact ? 34 : 42),
                padding: EdgeInsets.symmetric(
                  horizontal: compact ? 6 : 10,
                  vertical: compact ? 6 : 10,
                ),
                backgroundColor: active
                    ? _HomeScreenState._accent
                    : _HomeScreenState._surfaceDark,
                foregroundColor: active
                    ? const Color(0xFF1A222D)
                    : _HomeScreenState._text,
              ),
              onPressed: enabled ? () {} : null,
              child: Icon(Icons.play_arrow, size: compact ? 18 : 24),
            ),
    );
  }
}
