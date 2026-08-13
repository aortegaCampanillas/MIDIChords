"""Desktop interval ear-training mode."""

from __future__ import annotations

import random

from PySide6.QtCore import Qt

import midichords.qt.tk_compat as tk
from midichords.core.interval_data import INTERVAL_ALT_NAMES, INTERVAL_GRID_COLUMNS


class IntervalPracticeMixin:
    """Exercise flow, UI and playback for interval practice."""

    def _init_interval_practice_state(self) -> None:
        self.interval_practice_started = False
        self.interval_practice_running = False
        self.interval_practice_root = 60
        self.interval_practice_semitones = 0
        self.interval_practice_direction = 1
        self.interval_practice_column_key = "perfect"
        self.interval_practice_answer: dict | None = None
        self.interval_practice_correct = 0
        self.interval_practice_total = 0
        self.interval_practice_repetitions = 10
        self.interval_practice_random_tonic = False
        self.interval_practice_ascending_only = True
        self.interval_practice_playback_mode = "melodic"
        self.interval_practice_allowed_semitones = set(range(13))
        self.interval_practice_deck: list[int] = []
        self.interval_practice_last_semitones: int | None = None
        self.interval_practice_history: list[dict] = []
        self.interval_practice_review_index: int | None = None
        self.interval_practice_review_timer = None
        self.interval_practice_single_timer = None

    def _interval_practice_text(self, key: str) -> str:
        from midichords.core.i18n import UI_TEXTS

        lang = self._interval_gen_language()
        return UI_TEXTS.get(lang, UI_TEXTS["es"]).get(key, key)

    def interval_practice_question_notes(self) -> list[int]:
        if not self.interval_practice_started:
            return []
        root = int(self.interval_practice_root)
        return [root, root + int(self.interval_practice_direction) * int(self.interval_practice_semitones)]

    def interval_practice_display_notes(self) -> list[int]:
        notes = self.interval_practice_question_notes()
        if not notes:
            return []
        answer = self.interval_practice_answer
        if not answer:
            return [notes[0]]
        if answer.get("correct"):
            return notes
        return [notes[0], int(answer["note"]), notes[1]]

    def _interval_practice_choices(self) -> list[dict]:
        roots = list(range(60, 72)) if self.interval_practice_random_tonic else [60]
        result = []
        for column in INTERVAL_GRID_COLUMNS:
            for semitones in column["cells_by_semitone"]:
                if int(semitones) not in self.interval_practice_allowed_semitones:
                    continue
                directions = [1] if self.interval_practice_ascending_only or semitones == 0 else [1, -1]
                for root in roots:
                    for direction in directions:
                        result.append({
                            "root": root,
                            "semitones": int(semitones),
                            "column_key": column["key"],
                            "direction": direction,
                        })
        return result

    def _draw_interval_practice_choice(self) -> dict | None:
        choices = self._interval_practice_choices()
        if not choices:
            return None
        distances = sorted({int(choice["semitones"]) for choice in choices})
        self.interval_practice_deck = [n for n in self.interval_practice_deck if n in distances]
        if not self.interval_practice_deck:
            self.interval_practice_deck = distances[:]
            random.shuffle(self.interval_practice_deck)
            if len(self.interval_practice_deck) > 1 and self.interval_practice_deck[0] == self.interval_practice_last_semitones:
                self.interval_practice_deck[0], self.interval_practice_deck[1] = self.interval_practice_deck[1], self.interval_practice_deck[0]
        semitones = self.interval_practice_deck.pop(0)
        matching = [choice for choice in choices if choice["semitones"] == semitones]
        self.interval_practice_last_semitones = semitones
        return random.choice(matching)

    def _start_interval_practice(self) -> None:
        if self.interval_practice_running:
            self._stop_interval_practice()
            return
        if self.interval_practice_review_timer:
            try:
                self.after_cancel(self.interval_practice_review_timer)
            except Exception:
                pass
            self.interval_practice_review_timer = None
        try:
            repetitions = int(self.interval_practice_repetitions_var.get())
        except (TypeError, ValueError):
            repetitions = 10
        self.interval_practice_repetitions = max(1, min(100, repetitions))
        self.interval_practice_repetitions_var.set(str(self.interval_practice_repetitions))
        self.interval_practice_started = True
        self.interval_practice_running = True
        self.interval_practice_correct = 0
        self.interval_practice_total = 0
        self.interval_practice_history = []
        self.interval_practice_review_index = None
        self.interval_practice_deck = []
        self.interval_practice_last_semitones = None
        self._next_interval_practice_question()

    def _stop_interval_practice(self) -> None:
        self.interval_practice_running = False
        for timer_name in (
            "interval_gen_playback_timer",
            "interval_practice_review_timer",
            "interval_practice_single_timer",
        ):
            timer = getattr(self, timer_name, None)
            if timer:
                try:
                    self.after_cancel(timer)
                except Exception:
                    pass
                setattr(self, timer_name, None)
        for note in list(self.sounding_notes):
            self.stop_note(note)
        self.interval_gen_playing_note = None
        self.interval_gen_playing_idx = None
        self.interval_gen_playing_notes.clear()
        if self.interval_practice_history:
            self._show_interval_practice_history(0)
            return
        self._refresh_interval_practice_ui()

    def _next_interval_practice_question(self) -> None:
        if self.interval_practice_started and self.interval_practice_answer is None and self.interval_practice_total > 0:
            return
        if self.interval_practice_total >= self.interval_practice_repetitions and self.interval_practice_started:
            return
        if self.interval_practice_review_timer:
            try:
                self.after_cancel(self.interval_practice_review_timer)
            except Exception:
                pass
            self.interval_practice_review_timer = None
        choice = self._draw_interval_practice_choice()
        if not choice:
            return
        self.interval_practice_root = choice["root"]
        self.interval_practice_semitones = choice["semitones"]
        self.interval_practice_column_key = choice["column_key"]
        self.interval_practice_direction = choice["direction"]
        self.interval_practice_answer = None
        self.interval_practice_review_index = None
        self._refresh_interval_practice_ui()
        self._play_interval_practice_question()

    def _play_interval_practice_notes(self, notes: list[int], *, hide_second: bool = False) -> None:
        # Una audición manual realizada tras responder deja programada una
        # limpieza breve. Si el usuario pulsa Siguiente antes de que venza,
        # aquella callback no debe borrar el resaltado del nuevo intervalo.
        for timer_name in (
            "interval_practice_single_timer",
            "interval_gen_input_clear_timer",
        ):
            timer = getattr(self, timer_name, None)
            if timer:
                try:
                    self.after_cancel(timer)
                except Exception:
                    pass
                setattr(self, timer_name, None)
        if self.interval_practice_playback_mode == "harmonic":
            if self.interval_gen_playback_timer:
                try:
                    self.after_cancel(self.interval_gen_playback_timer)
                except Exception:
                    pass
                self.interval_gen_playback_timer = None
            self.interval_gen_playing_note = int(notes[0]) if hide_second else None
            self.interval_gen_playing_idx = 0 if hide_second else None
            self.interval_gen_playing_notes = {int(notes[0])} if hide_second else {int(note) for note in notes}
            for note in notes:
                self.play_note(int(note), velocity=80)
            self.update_music_views()
            self.interval_gen_playback_timer = self.after(460, lambda: self._clear_interval_practice_playback(notes))
            return
        self._interval_practice_hide_second = bool(hide_second)
        self._play_interval_gen_sequence([int(note) for note in notes])

    def _clear_interval_practice_playback(self, notes: list[int]) -> None:
        for note in notes:
            self.stop_note(int(note))
        self.interval_gen_playing_note = None
        self.interval_gen_playing_idx = None
        self.interval_gen_playing_notes.clear()
        self.update_music_views()

    def _play_interval_practice_question(self) -> None:
        notes = self.interval_practice_question_notes()
        if len(notes) == 2:
            self._play_interval_practice_notes(notes, hide_second=True)

    def _repeat_interval_practice(self) -> None:
        if self.interval_practice_answer:
            self._replay_interval_practice_result()
        elif self.interval_practice_running:
            self._play_interval_practice_question()

    def _answer_interval_practice(self, *, note: int | None = None, semitones: int | None = None) -> bool:
        if not self.interval_practice_running or self.interval_practice_answer:
            return False
        if semitones is not None and int(semitones) not in self.interval_practice_allowed_semitones:
            return False
        root, correct_note = self.interval_practice_question_notes()
        guessed_note = int(note) if note is not None else root + self.interval_practice_direction * int(semitones)
        guessed_semitones = abs(guessed_note - root) if semitones is None else int(semitones)
        correct = guessed_note == correct_note if note is not None else guessed_semitones == self.interval_practice_semitones
        self.interval_practice_total += 1
        self.interval_practice_correct += int(correct)
        self.interval_practice_answer = {
            "note": guessed_note,
            "semitones": guessed_semitones,
            "correct": correct,
        }
        self.interval_practice_history.append({
            "root": root,
            "semitones": self.interval_practice_semitones,
            "column_key": self.interval_practice_column_key,
            "direction": self.interval_practice_direction,
            "answer": dict(self.interval_practice_answer),
            "score_correct": self.interval_practice_correct,
            "score_total": self.interval_practice_total,
        })
        if self.interval_practice_total >= self.interval_practice_repetitions:
            self.interval_practice_running = False
        self._play_interval_practice_notes([root, guessed_note])
        self._refresh_interval_practice_ui()
        return True

    def _handle_interval_practice_input(self, note: int, *, source: str = "mouse") -> bool:
        note = int(note)
        if not self.interval_practice_answer:
            return self._answer_interval_practice(note=note)
        allowed = set(self.interval_practice_display_notes())
        if note not in allowed:
            self._show_forbidden_note_feedback(note)
            return False
        self.play_note(note, velocity=100)
        self.interval_gen_playing_note = note
        self.update_music_views()
        if self.interval_practice_single_timer:
            try:
                self.after_cancel(self.interval_practice_single_timer)
            except Exception:
                pass
        self.interval_practice_single_timer = self.after(
            460, lambda: self._clear_interval_practice_single(note)
        )
        return True

    def _clear_interval_practice_single(self, note: int) -> None:
        self.interval_practice_single_timer = None
        self.stop_note(int(note))
        if self.interval_gen_playing_note == int(note):
            self.interval_gen_playing_note = None
        self.update_music_views()

    def _replay_interval_practice_result(self) -> None:
        if not self.interval_practice_answer:
            return
        root, correct_note = self.interval_practice_question_notes()
        self._play_interval_practice_notes([root, correct_note])
        if not self.interval_practice_answer["correct"]:
            wrong = int(self.interval_practice_answer["note"])
            self.interval_practice_review_timer = self.after(
                1150, lambda: self._play_interval_practice_notes([root, wrong])
            )

    def _show_interval_practice_history(self, delta: int) -> None:
        if not self.interval_practice_history:
            return
        index = self.interval_practice_review_index
        if index is None:
            index = len(self.interval_practice_history) - 1
        index = max(0, min(len(self.interval_practice_history) - 1, index + delta))
        entry = self.interval_practice_history[index]
        self.interval_practice_review_index = index
        self.interval_practice_root = entry["root"]
        self.interval_practice_semitones = entry["semitones"]
        self.interval_practice_column_key = entry["column_key"]
        self.interval_practice_direction = entry["direction"]
        self.interval_practice_answer = dict(entry["answer"])
        self.interval_practice_correct = entry["score_correct"]
        self.interval_practice_total = entry["score_total"]
        self._refresh_interval_practice_ui()

    def _toggle_interval_practice_option(self, name: str) -> None:
        if self.interval_practice_running:
            return
        variable = getattr(self, f"{name}_var", None)
        if variable is not None:
            variable.set(not bool(variable.get()))
        else:
            setattr(self, name, not bool(getattr(self, name)))
        self._refresh_interval_practice_ui()

    def _toggle_interval_practice_playback(self) -> None:
        if self.interval_practice_running:
            return
        self.interval_practice_playback_mode = "harmonic" if self.interval_practice_playback_mode == "melodic" else "melodic"
        self._refresh_interval_practice_ui()
        self.update_music_views()

    def _interval_practice_name(self) -> str:
        if not self.interval_practice_answer:
            return "-"
        lang = self._interval_gen_language()
        selected = ""
        names = []
        for column in INTERVAL_GRID_COLUMNS:
            cell = column["cells_by_semitone"].get(int(self.interval_practice_semitones))
            if not cell:
                continue
            name = cell["name"].get(lang) or cell["name"]["es"]
            if column["key"] == self.interval_practice_column_key:
                selected = name
            elif name not in names:
                names.append(name)
        for name in INTERVAL_ALT_NAMES.get(lang, {}).get(int(self.interval_practice_semitones), []):
            if name != selected and name not in names:
                names.append(name)
        return ", ".join([selected or names.pop(0), *names])

    def _show_interval_practice_filter(self) -> None:
        if self.interval_practice_running:
            return
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

        dialog = QDialog(self)
        dialog.setWindowTitle(self._interval_practice_text("interval_practice_filter_title"))
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background:#263041; color:#e8effa; } QCheckBox { padding:8px; }" )
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(self._interval_practice_text("interval_practice_filter_text")))
        actions = QHBoxLayout()
        select_all = QPushButton(self._interval_practice_text("interval_practice_filter_select_all"))
        clear = QPushButton(self._interval_practice_text("interval_practice_filter_clear"))
        actions.addWidget(select_all); actions.addWidget(clear); layout.addLayout(actions)
        piano = QWidget(dialog)
        piano.setFixedSize(760, 132)
        piano.setStyleSheet("background:#101923; border:1px solid #65758c;")
        checks = []
        white_steps = [0, 2, 4, 5, 7, 9, 11, 12]
        for index, semitones in enumerate(white_steps):
            key = QPushButton(self.note_name(60 + semitones), piano)
            key.setCheckable(True); key.setChecked(semitones in self.interval_practice_allowed_semitones)
            key.setProperty("semitones", semitones); key.setGeometry(index * 95, 0, 95, 132)
            key.setStyleSheet(
                "QPushButton { background:#f4f6f8; color:#1b2735; border:1px solid #8593a5; padding-top:90px; }"
                "QPushButton:checked { background:#79dfa0; border:3px solid #2ebf69; }"
            )
            checks.append(key)
        for semitones, boundary in ((1, 1), (3, 2), (6, 4), (8, 5), (10, 6)):
            key = QPushButton(self.note_name(60 + semitones), piano)
            key.setCheckable(True); key.setChecked(semitones in self.interval_practice_allowed_semitones)
            key.setProperty("semitones", semitones); key.setGeometry(boundary * 95 - 28, 0, 56, 82)
            key.setStyleSheet(
                "QPushButton { background:#101820; color:#f2f5f8; border:1px solid #05080c; padding-top:48px; }"
                "QPushButton:checked { background:#238d55; border:3px solid #69e69b; }"
            )
            key.raise_(); checks.append(key)
        layout.addWidget(piano, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons = QHBoxLayout()
        accept = QPushButton(self._interval_practice_text("interval_practice_filter_accept"))
        cancel = QPushButton(self._interval_practice_text("interval_practice_filter_cancel"))
        buttons.addWidget(accept); buttons.addWidget(cancel); layout.addLayout(buttons)

        def refresh_accept_state(*_args) -> None:
            accept.setEnabled(any(check.isChecked() for check in checks))

        for check in checks:
            check.toggled.connect(refresh_accept_state)
        select_all.clicked.connect(lambda: [check.setChecked(True) for check in checks])
        clear.clicked.connect(lambda: [check.setChecked(False) for check in checks])
        cancel.clicked.connect(dialog.reject)
        refresh_accept_state()

        def apply_filter():
            selected = {int(check.property("semitones")) for check in checks if check.isChecked()}
            if not selected:
                return
            self.interval_practice_allowed_semitones = selected
            self.interval_practice_deck = []
            dialog.accept()
            self._refresh_interval_practice_ui()
        accept.clicked.connect(apply_filter)
        dialog.resize(820, 280)
        dialog.exec()

    def _show_interval_practice_help(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            self._interval_practice_text("interval_practice_help_title"),
            self._interval_practice_text("interval_practice_help_text") + "\n\n" + self._interval_practice_text("interval_practice_help_next"),
        )

    def _setup_interval_practice_ui(self) -> None:
        if hasattr(self, "_interval_practice_panel_created"):
            self._refresh_interval_practice_ui()
            return
        from midichords.ui.widgets_qt import GrayRoundedButton

        bg = self.color_surface_alt
        panel = tk.Frame(self.tab_interval_practice_frame, bg=bg)
        self.interval_practice_panel = panel
        self.interval_practice_i18n_labels = []
        title = tk.Label(panel, text="", bg=bg, fg=self.color_text, font=(self.ui_font_family, 22, "bold"))
        title.pack(anchor="w", pady=(0, 6)); self.interval_practice_i18n_labels.append((title, "heading_interval_practice"))
        actions = tk.Frame(panel, bg=bg); actions.pack(anchor="w", pady=(0, 8))
        self.interval_practice_start_btn = GrayRoundedButton(actions, text="", command=self._start_interval_practice, width=88, height=34, radius=14, font_size=13)
        self.interval_practice_start_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.interval_practice_repeat_btn = GrayRoundedButton(actions, text="↻", command=self._repeat_interval_practice, width=44, height=34, radius=14, font_size=13)
        self.interval_practice_repeat_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.interval_practice_next_btn = GrayRoundedButton(actions, text="", command=self._next_interval_practice_question, width=96, height=34, radius=14, font_size=13)
        self.interval_practice_next_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.interval_practice_help_btn = GrayRoundedButton(actions, text="?", command=self._show_interval_practice_help, width=40, height=34, radius=14, font_size=13)
        self.interval_practice_help_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.interval_practice_review_label = tk.Label(actions, text="", bg=bg, fg=self.color_muted, font=(self.ui_font_family, 13))
        self.interval_practice_review_label.pack(side=tk.LEFT, padx=(10, 4))
        self.interval_practice_prev_btn = GrayRoundedButton(actions, text="◀", command=lambda: self._show_interval_practice_history(-1), width=42, height=34, radius=14)
        self.interval_practice_prev_btn.pack(side=tk.LEFT, padx=4)
        self.interval_practice_review_next_btn = GrayRoundedButton(actions, text="▶", command=lambda: self._show_interval_practice_history(1), width=42, height=34, radius=14)
        self.interval_practice_review_next_btn.pack(side=tk.LEFT)

        options = tk.Frame(panel, bg=bg); options.pack(anchor="w", pady=(0, 8))
        self.interval_practice_random_tonic_var = tk.BooleanVar(value=self.interval_practice_random_tonic)
        self.interval_practice_ascending_only_var = tk.BooleanVar(value=self.interval_practice_ascending_only)
        self.interval_practice_random_option = self._build_checkbox_row(
            options, "", self.interval_practice_random_tonic_var
        )
        self.interval_practice_random_option.pack(side=tk.LEFT, padx=(0, 20))
        self.interval_practice_ascending_option = self._build_checkbox_row(
            options, "", self.interval_practice_ascending_only_var
        )
        self.interval_practice_ascending_option.pack(side=tk.LEFT)
        self.interval_practice_random_tonic_var.trace_add(
            "write", lambda *_args: setattr(self, "interval_practice_random_tonic", bool(self.interval_practice_random_tonic_var.get()))
        )
        self.interval_practice_ascending_only_var.trace_add(
            "write", lambda *_args: setattr(self, "interval_practice_ascending_only", bool(self.interval_practice_ascending_only_var.get()))
        )

        settings = tk.Frame(panel, bg=bg); settings.pack(anchor="w", pady=(0, 8))
        self.interval_practice_repetitions_label = tk.Label(settings, text="", bg=bg, fg=self.color_muted, font=(self.ui_font_family, 13))
        self.interval_practice_repetitions_label.pack(side=tk.LEFT, padx=(0, 6))
        self.interval_practice_repetitions_var = tk.StringVar(value="10")
        self.interval_practice_repetitions_entry = tk.Entry(settings, textvariable=self.interval_practice_repetitions_var, width=5)
        self.interval_practice_repetitions_entry.setFixedSize(58, 30)
        self.interval_practice_repetitions_entry._entry.setText("10")
        self.interval_practice_repetitions_entry._entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.interval_practice_repetitions_entry._entry.setStyleSheet(
            "QLineEdit { background:#17273a; color:#e8effa; "
            "border:1px solid #5a6a82; border-radius:5px; padding:2px 6px; } "
            "QLineEdit:disabled { color:#7f8894; background:#1f252d; border-color:#434a54; }"
        )
        self.interval_practice_repetitions_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.interval_practice_filter_btn = GrayRoundedButton(settings, text="", command=self._show_interval_practice_filter, width=82, height=30, radius=14, font_size=12)
        self.interval_practice_filter_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.interval_practice_playback_btn = GrayRoundedButton(settings, text="", command=self._toggle_interval_practice_playback, width=96, height=30, radius=14, font_size=12)
        self.interval_practice_playback_btn.pack(side=tk.LEFT)

        result_bg = "#17273a"
        result = tk.Frame(panel, bg=result_bg); result.pack(fill=tk.X, pady=(0, 8))
        self.interval_practice_score_label = tk.Label(result, text="", bg=result_bg, fg=self.color_text, font=(self.ui_font_family, 14, "bold"), anchor="w")
        self.interval_practice_score_label.pack(fill=tk.X, padx=8, pady=(5, 2))
        self.interval_practice_name_label = tk.Label(result, text="", bg=result_bg, fg=self.color_accent, font=(self.ui_font_family, 14, "bold"), anchor="w")
        self.interval_practice_name_label.pack(fill=tk.X, padx=8, pady=(2, 5))

        self._build_interval_practice_table(panel)
        panel.pack(fill=tk.BOTH, expand=True)
        self._interval_practice_panel_created = True
        self._refresh_interval_practice_ui_language()
        self._refresh_interval_practice_ui()

    def _build_interval_practice_table(self, panel) -> None:
        grid_line, header_bg, cell_bg = "#5a6a82", "#17273a", "#0f1c2c"
        table = tk.Frame(panel, bg=self.color_surface_alt, highlightthickness=1, highlightbackground=grid_line)
        table.pack(fill=tk.X, expand=True, pady=(2, 0))
        self.interval_practice_table_frame = table
        self.interval_practice_cells = {}
        self.interval_practice_headers = {}
        table.columnconfigure(0, weight=0)

        corner = tk.Frame(table, bg=header_bg, highlightthickness=1, highlightbackground=grid_line)
        corner.grid(row=0, column=0, sticky="nsew")
        layout = table.layout()
        if layout is not None:
            layout.setSpacing(0)
        for semitones in range(13):
            header_cell = tk.Frame(table, bg=header_bg, highlightthickness=1, highlightbackground=grid_line)
            header_cell.grid(row=0, column=semitones + 1, sticky="nsew")
            header = tk.Label(header_cell, text=str(semitones), bg=header_bg, fg=self.color_muted, font=(self.ui_font_family, 11, "bold"), anchor="center")
            header.pack(anchor="center", pady=2)
            self.interval_practice_headers[semitones] = header
            table.columnconfigure(semitones + 1, weight=1)

        from PySide6.QtGui import QFont, QFontMetrics
        title_metrics = QFontMetrics(QFont(self.ui_font_family, 12))
        title_col_w = max(
            title_metrics.horizontalAdvance(column["title"].get(self._interval_gen_language(), column["title"]["es"]))
            for column in INTERVAL_GRID_COLUMNS
        ) + 80
        self.interval_practice_row_titles = []
        for row, column in enumerate(INTERVAL_GRID_COLUMNS, 1):
            title_cell = tk.Frame(table, bg=header_bg, highlightthickness=1, highlightbackground=grid_line)
            title_cell.setMinimumWidth(title_col_w)
            title_cell.grid(row=row, column=0, sticky="nsew")
            title = tk.Label(title_cell, text="", bg=header_bg, fg=self.color_text, font=(self.ui_font_family, 12), anchor="center")
            title.pack(anchor="center", pady=2)
            self.interval_practice_row_titles.append((column, title_cell, title))
            for semitones in range(13):
                cell = column["cells_by_semitone"].get(semitones)
                cell_frame = tk.Frame(table, bg=cell_bg, highlightthickness=1, highlightbackground=grid_line)
                cell_frame.grid(row=row, column=semitones + 1, sticky="nsew")
                label = tk.Label(cell_frame, text=cell["short"] if cell else "", bg=cell_bg, fg=self.color_text, font=(self.ui_font_family, 12), anchor="center")
                label.pack(anchor="center", pady=2)
                if cell:
                    cell_frame.bind("<Button-1>", lambda _e, s=semitones: self._answer_interval_practice(semitones=s))
                    label.bind("<Button-1>", lambda _e, s=semitones: self._answer_interval_practice(semitones=s))
                    cell_frame.configure(cursor="pointinghand")
                    label.configure(cursor="pointinghand")
                self.interval_practice_cells[(column["key"], semitones)] = (cell_frame, label, bool(cell))

    def _refresh_interval_practice_ui_language(self) -> None:
        for label, key in getattr(self, "interval_practice_i18n_labels", []):
            label.configure(text=self._interval_practice_text(key))
        for column, _title_cell, label in getattr(self, "interval_practice_row_titles", []):
            label.configure(text=column["title"].get(self._interval_gen_language(), column["title"]["es"]))

    def _refresh_interval_practice_ui(self) -> None:
        if not hasattr(self, "_interval_practice_panel_created"):
            return
        t = self._interval_practice_text
        self.interval_practice_start_btn.set_text(t("interval_practice_stop") if self.interval_practice_running else t("interval_practice_start"))
        self.interval_practice_next_btn.set_text(t("interval_practice_next"))
        self.interval_practice_random_option.set_text(t("interval_practice_random_tonic"))
        self.interval_practice_ascending_option.set_text(t("interval_practice_ascending_only"))
        if bool(self.interval_practice_random_tonic_var.get()) != self.interval_practice_random_tonic:
            self.interval_practice_random_tonic_var.set(self.interval_practice_random_tonic)
        if bool(self.interval_practice_ascending_only_var.get()) != self.interval_practice_ascending_only:
            self.interval_practice_ascending_only_var.set(self.interval_practice_ascending_only)
        self.interval_practice_repetitions_label.configure(text=t("interval_practice_repetitions"))
        self.interval_practice_filter_btn.set_text(t("interval_practice_filter"))
        self.interval_practice_playback_btn.set_text(t("interval_practice_playback_harmonic") if self.interval_practice_playback_mode == "harmonic" else t("interval_practice_playback_melodic"))
        self.interval_practice_playback_btn.set_selected(False)
        self.interval_practice_review_label.configure(text=t("interval_practice_review"))
        answered = self.interval_practice_answer is not None
        self.interval_practice_repeat_btn.set_enabled(self.interval_practice_running or bool(self.interval_practice_history))
        self.interval_practice_next_btn.set_enabled(self.interval_practice_running and answered and self.interval_practice_total < self.interval_practice_repetitions)
        for widget in (self.interval_practice_random_option, self.interval_practice_ascending_option, self.interval_practice_filter_btn, self.interval_practice_playback_btn):
            widget.set_enabled(not self.interval_practice_running)
        self.interval_practice_repetitions_entry.configure(state="disabled" if self.interval_practice_running else "normal")
        reviewing = not self.interval_practice_running and bool(self.interval_practice_history)
        review_widgets = (
            self.interval_practice_review_label,
            self.interval_practice_prev_btn,
            self.interval_practice_review_next_btn,
        )
        if reviewing:
            if self.interval_practice_review_label.isHidden():
                self.interval_practice_review_label.pack(side=tk.LEFT, padx=(10, 4))
                self.interval_practice_prev_btn.pack(side=tk.LEFT, padx=4)
                self.interval_practice_review_next_btn.pack(side=tk.LEFT)
        else:
            for widget in review_widgets:
                widget.pack_forget()
        index = self.interval_practice_review_index if self.interval_practice_review_index is not None else len(self.interval_practice_history) - 1
        self.interval_practice_prev_btn.set_enabled(reviewing and index > 0)
        self.interval_practice_review_next_btn.set_enabled(reviewing and index < len(self.interval_practice_history) - 1)
        self.interval_practice_score_label.configure(text=f"{t('interval_practice_score')} {self.interval_practice_correct}/{self.interval_practice_total}")
        self.interval_practice_name_label.configure(text=f"{t('label_interval_name')} {self._interval_practice_name()}")
        for (column_key, semitones), (cell_frame, label, exists) in self.interval_practice_cells.items():
            allowed = semitones in self.interval_practice_allowed_semitones
            bg, fg = "#0f1c2c", self.color_text if allowed else self.color_muted
            if answered and semitones == self.interval_practice_semitones:
                bg, fg = "#39c66d", "#17273a"
            elif answered and not self.interval_practice_answer["correct"] and semitones == self.interval_practice_answer["semitones"]:
                bg, fg = "#e35d67", "#ffffff"
            cursor = "pointinghand" if exists and allowed and not answered else ""
            cell_frame.configure(bg=bg, cursor=cursor)
            label.configure(bg=bg, fg=fg, cursor=cursor)
        for semitones, header in self.interval_practice_headers.items():
            header.configure(fg=self.color_muted if semitones in self.interval_practice_allowed_semitones else "#536174")
        self.update_music_views()
