"""Interval generation mixin: pick a tonic and an interval from a grid to hear it."""

import midichords.qt.tk_compat as tk
from midichords.core.interval_data import INTERVAL_GRID_COLUMNS
from midichords.core.music_theory import (
    ROOT_LETTER_PCS,
    ROOT_LETTER_ACCIDENTALS,
    root_pc_from_letter_accidental,
)

ACCIDENTAL_SYMBOLS = {"natural": "♮", "sharp": "♯", "flat": "♭"}


class IntervalGenerationMixin:
    """Mixin providing the Interval Generation mode: tonic + grid -> hear + highlight."""

    def _init_interval_generation_state(self):
        """Initialize interval generation state."""
        self.interval_gen_root_letter_pc = 0
        self.interval_gen_root_accidental = "natural"
        self.interval_gen_semitones: int | None = None
        self.interval_gen_column_key: str | None = None
        self.interval_gen_reverse = False
        self.interval_gen_last_play_reverse: bool | None = None
        self.interval_gen_playing_note: int | None = None
        self.interval_gen_playing_idx: int | None = None
        self.interval_gen_playback_timer: object | None = None

    def interval_gen_root_pc(self) -> int:
        return root_pc_from_letter_accidental(
            int(self.interval_gen_root_letter_pc), str(self.interval_gen_root_accidental)
        )

    def interval_gen_notes(self) -> list[int]:
        """Tonic (C4=60) + the chosen semitone offset, or [] if nothing selected."""
        if self.interval_gen_semitones is None:
            return []
        tonic_midi = 60 + self.interval_gen_root_pc()
        return [tonic_midi, tonic_midi + int(self.interval_gen_semitones)]

    def _interval_gen_selected_column(self) -> dict | None:
        for col in INTERVAL_GRID_COLUMNS:
            if col["key"] == self.interval_gen_column_key:
                return col
        return None

    def _interval_gen_language(self) -> str:
        language = getattr(self, "language", None) or self.config_data.get(
            "language", "es"
        )
        return str(language) if str(language) in {"es", "en"} else "es"

    def _interval_gen_grid_title(self, column: dict) -> str:
        titles = column["title"]
        return str(titles.get(self._interval_gen_language(), titles["es"]))

    def get_interval_gen_name(self) -> str:
        """Name of the interval as picked from the grid (falls back to '-')."""
        if self.interval_gen_semitones is None:
            return "-"
        lang = self._interval_gen_language()
        col = self._interval_gen_selected_column()
        cell = col and col["cells_by_semitone"].get(int(self.interval_gen_semitones))
        if cell:
            return cell["name"].get(lang) or cell["name"]["es"]
        return "-"

    def get_interval_gen_alt_names(self) -> str:
        """Other valid names for the same semitone count, excluding the selected one."""
        if self.interval_gen_semitones is None:
            return "-"
        lang = self._interval_gen_language()
        semitones = int(self.interval_gen_semitones)
        selected = self.get_interval_gen_name()
        names = []
        for col in INTERVAL_GRID_COLUMNS:
            cell = col["cells_by_semitone"].get(semitones)
            if not cell:
                continue
            name = cell["name"].get(lang) or cell["name"]["es"]
            if name and name != selected:
                names.append(name)
        return ", ".join(names) if names else "-"

    def _set_interval_gen_semitones(self, semitones: int, column_key: str) -> None:
        self.interval_gen_semitones = int(semitones)
        self.interval_gen_column_key = column_key
        self._update_interval_generation_display()
        self._play_interval_gen_current()

    def _on_interval_gen_root_combo_changed(self, _event: tk.Event) -> None:
        label = str(self.interval_gen_root_var.get()).strip()
        letter_pc = getattr(self, "_interval_gen_root_label_to_pc", {}).get(label)
        if letter_pc is None:
            return
        prev_accidental = str(self.interval_gen_root_accidental)
        accidentals = ROOT_LETTER_ACCIDENTALS.get(int(letter_pc), ("natural",))
        accidental_value = prev_accidental if prev_accidental in accidentals else "natural"
        self._refresh_interval_gen_root_accidental_options(int(letter_pc), accidental_value)
        self.interval_gen_root_letter_pc = int(letter_pc)
        self.interval_gen_root_accidental = accidental_value
        self._update_interval_generation_display()
        self._play_interval_gen_current()

    def _on_interval_gen_root_accidental_combo_changed(self, _event: tk.Event) -> None:
        label = str(self.interval_gen_root_accidental_var.get()).strip()
        accidental = getattr(self, "_interval_gen_root_accidental_label_to_value", {}).get(label)
        if accidental is None:
            return
        self.interval_gen_root_accidental = str(accidental)
        self._update_interval_generation_display()
        self._play_interval_gen_current()

    def _refresh_interval_gen_root_accidental_options(self, letter_pc: int, accidental: str) -> None:
        if not hasattr(self, "interval_gen_root_accidental_combo"):
            return
        accidentals = ROOT_LETTER_ACCIDENTALS.get(int(letter_pc), ("natural",))
        self._interval_gen_root_accidental_label_to_value = {
            ACCIDENTAL_SYMBOLS[a]: a for a in accidentals
        }
        self.interval_gen_root_accidental_combo.configure(values=[ACCIDENTAL_SYMBOLS[a] for a in accidentals])
        chosen = accidental if accidental in accidentals else "natural"
        self.interval_gen_root_accidental_var.set(ACCIDENTAL_SYMBOLS[chosen])

    def _refresh_interval_gen_root_selector(self) -> None:
        if not (hasattr(self, "interval_gen_root_combo") and hasattr(self, "interval_gen_root_var")):
            return
        root_options = [
            (self.note_name(pc, with_octave=False), int(pc)) for pc in ROOT_LETTER_PCS
        ]
        self._interval_gen_root_label_to_pc = {label: pc for label, pc in root_options}
        self.interval_gen_root_combo.configure(values=[label for label, _ in root_options])
        letter_pc = int(self.interval_gen_root_letter_pc)
        self.interval_gen_root_var.set(self.note_name(letter_pc, with_octave=False))
        self._refresh_interval_gen_root_accidental_options(letter_pc, str(self.interval_gen_root_accidental))

    def _play_interval_gen_current(self) -> None:
        """Play the current interval in the remembered direction (ascending/descending)."""
        notes = self.interval_gen_notes()
        if len(notes) != 2:
            return
        ordered = sorted(notes, reverse=bool(self.interval_gen_reverse))
        self._play_interval_gen_sequence(ordered)

    def _play_interval_gen_reverse(self) -> None:
        self.interval_gen_reverse = True
        self.interval_gen_last_play_reverse = True
        self._refresh_interval_gen_buttons_state()
        self._play_interval_gen_current()

    def _play_interval_gen_forward(self) -> None:
        self.interval_gen_reverse = False
        self.interval_gen_last_play_reverse = False
        self._refresh_interval_gen_buttons_state()
        self._play_interval_gen_current()

    def _play_interval_gen_sequence(self, notes: list[int], index: int = 0) -> None:
        if self.interval_gen_playback_timer:
            self.after_cancel(self.interval_gen_playback_timer)
            self.interval_gen_playback_timer = None
        if index == 0:
            prev = {n for n in notes if n is not None} & set(self.sounding_notes)
            for note in prev:
                self.stop_note(note)
            self.sounding_notes -= prev
        if index >= len(notes):
            self.interval_gen_playing_note = None
            self.interval_gen_playing_idx = None
            self.update_music_views()
            return
        note = notes[index]
        self.interval_gen_playing_note = note
        self.interval_gen_playing_idx = index
        self.play_note(note, velocity=80)
        self.update_music_views()
        self.interval_gen_playback_timer = self.after(
            500,
            lambda: self._play_interval_gen_sequence_continue(notes, index, note),
        )

    def _play_interval_gen_sequence_continue(self, notes: list[int], index: int, prev_note: int) -> None:
        self.stop_note(prev_note)
        self._play_interval_gen_sequence(notes, index + 1)

    def _get_ui_text_interval_gen(self, key: str) -> str:
        from midichords.core.i18n import UI_TEXTS
        lang = self._interval_gen_language()
        texts = UI_TEXTS.get(lang, UI_TEXTS["es"])
        return texts.get(key, key)

    def _setup_interval_generation_ui(self):
        """Create the Interval Generation UI panel."""
        if hasattr(self, "_interval_generation_panel_created"):
            self._refresh_interval_gen_root_selector()
            self._update_interval_generation_display()
            return

        from midichords.ui.widgets_qt import GrayRoundedButton, PlayTransportButton
        import midichords.qt.ttk_compat as ttk

        bg = self.color_surface_alt
        self.interval_generation_panel = tk.Frame(self.tab_interval_generation_frame, bg=bg, bd=0, highlightthickness=0)

        tk.Label(
            self.interval_generation_panel,
            text=self._get_ui_text_interval_gen("heading_interval_generation"),
            bg=bg,
            fg=self.color_text,
            font=(self.ui_font_family, 22, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        root_row = tk.Frame(self.interval_generation_panel, bg=bg, bd=0, highlightthickness=0)
        root_row.pack(fill=tk.X, anchor="w", pady=(0, 8))

        tk.Label(
            root_row,
            text=self._get_ui_text_interval_gen("label_root_note"),
            bg=bg,
            fg=self.color_text,
            font=(self.ui_font_family, 14),
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.interval_gen_root_var = tk.StringVar(value="-")
        self.interval_gen_root_combo = ttk.Combobox(
            root_row,
            textvariable=self.interval_gen_root_var,
            state="readonly",
            values=["-"],
            font=(self.ui_font_family, 15),
            height=12,
        )
        self.interval_gen_root_combo.pack(side=tk.LEFT, padx=(0, 6))
        self.interval_gen_root_combo.bind("<<ComboboxSelected>>", self._on_interval_gen_root_combo_changed)
        self._qt_apply_dark_combobox_style(self.interval_gen_root_combo)

        self.interval_gen_root_accidental_var = tk.StringVar(value="♮")
        self.interval_gen_root_accidental_combo = ttk.Combobox(
            root_row,
            textvariable=self.interval_gen_root_accidental_var,
            state="readonly",
            values=["♮"],
            width=3,
            font=(self.ui_font_family, 15),
        )
        self.interval_gen_root_accidental_combo.pack(side=tk.LEFT, padx=(0, 12))
        self.interval_gen_root_accidental_combo.bind(
            "<<ComboboxSelected>>", self._on_interval_gen_root_accidental_combo_changed
        )
        self._qt_apply_dark_combobox_style(self.interval_gen_root_accidental_combo)

        self.interval_gen_play_reverse_btn = PlayTransportButton(
            root_row,
            command=self._play_interval_gen_reverse,
            width=48,
            height=34,
            reversed_=True,
        )
        self.interval_gen_play_reverse_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.interval_gen_play_btn = PlayTransportButton(
            root_row,
            command=self._play_interval_gen_forward,
            width=48,
            height=34,
        )
        self.interval_gen_play_btn.pack(side=tk.LEFT)

        result_box_bg = "#17273a"
        result_frame = tk.Frame(self.interval_generation_panel, bg=result_box_bg, bd=0, highlightthickness=0)
        result_frame.pack(fill=tk.X, expand=False, pady=(2, 8))

        def _result_row(parent, label_key, value_fg=None):
            row = tk.Frame(parent, bg=result_box_bg)
            row.pack(anchor="w", pady=(4, 0), padx=8, fill=tk.X)
            tk.Label(
                row, text=self._get_ui_text_interval_gen(label_key),
                bg=result_box_bg, fg=self.color_muted,
                font=(self.ui_font_family, 14),
            ).pack(side=tk.LEFT)
            val = tk.Label(
                row, text=" -",
                bg=result_box_bg, fg=value_fg or self.color_text,
                font=(self.ui_mono_font_family, 14),
            )
            val.pack(side=tk.LEFT, padx=(4, 0))
            return row, val

        self.interval_gen_notes_row, self.interval_gen_notes_display = _result_row(result_frame, "label_interval_notes")
        self.interval_gen_name_row, self.interval_gen_name_display = _result_row(
            result_frame, "label_interval_name", self.color_accent
        )
        self.interval_gen_alt_row, self.interval_gen_alt_display = _result_row(result_frame, "label_interval_alt")
        self.interval_gen_semitones_row, self.interval_gen_semitones_display = _result_row(
            result_frame, "label_interval_semitones"
        )
        tk.Frame(result_frame, bg=result_box_bg, height=8).pack(fill=tk.X)

        grid_line = "#5a6a82"
        header_bg = "#17273a"
        cell_bg = "#0f1c2c"
        table_frame = tk.Frame(self.interval_generation_panel, bg=bg, bd=0, highlightthickness=1, highlightbackground=grid_line)
        table_frame.pack(fill=tk.X, expand=True, pady=(2, 0))
        self.interval_gen_table_frame = table_frame

        table_frame.columnconfigure(0, weight=0)
        for col_idx in range(13):
            table_frame.columnconfigure(col_idx + 1, weight=1)

        corner = tk.Frame(
            table_frame, bg=header_bg, highlightthickness=1, highlightbackground=grid_line,
        )
        corner.grid(row=0, column=0, sticky="nsew")
        _grid_layout = table_frame.layout()
        if _grid_layout is not None:
            _grid_layout.setSpacing(0)

        for semitones in range(13):
            head_cell = tk.Frame(
                table_frame, bg=header_bg, highlightthickness=1, highlightbackground=grid_line,
            )
            head_cell.grid(row=0, column=semitones + 1, sticky="nsew")
            tk.Label(
                head_cell, text=str(semitones), bg=header_bg, fg=self.color_muted,
                font=(self.ui_font_family, 11, "bold"), anchor="center",
            ).pack(anchor="center", pady=2)

        self.interval_gen_cell_labels: dict[tuple[str, int], object] = {}
        self.interval_gen_title_labels: list[tuple[dict, object, object]] = []
        from PySide6.QtGui import QFont, QFontMetrics
        title_font = QFont(self.ui_font_family, 12)
        title_metrics = QFontMetrics(title_font)
        max_title_w = max(
            title_metrics.horizontalAdvance(self._interval_gen_grid_title(col))
            for col in INTERVAL_GRID_COLUMNS
        )
        title_col_w = max_title_w + 80

        for row_idx, col in enumerate(INTERVAL_GRID_COLUMNS):
            title_cell = tk.Frame(
                table_frame, bg=header_bg, highlightthickness=1, highlightbackground=grid_line,
            )
            title_cell.setMinimumWidth(title_col_w)
            title_cell.grid(row=row_idx + 1, column=0, sticky="nsew")
            title_lbl = tk.Label(
                title_cell, text=self._interval_gen_grid_title(col),
                bg=header_bg, fg=self.color_text, font=(self.ui_font_family, 12),
                anchor="center",
            )
            title_lbl.pack(anchor="center", pady=2)
            self.interval_gen_title_labels.append((col, title_cell, title_lbl))
            for semitones in range(13):
                cell = col["cells_by_semitone"].get(semitones)
                cell_frame = tk.Frame(
                    table_frame, bg=cell_bg, highlightthickness=1, highlightbackground=grid_line,
                )
                cell_frame.grid(row=row_idx + 1, column=semitones + 1, sticky="nsew")
                lbl = tk.Label(
                    cell_frame,
                    text=(cell["short"] if cell else ""),
                    bg=cell_bg, fg=self.color_text,
                    font=(self.ui_font_family, 12), anchor="center",
                )
                lbl.pack(anchor="center", pady=2)
                if cell:
                    cell_frame.bind(
                        "<Button-1>",
                        lambda _e, s=semitones, k=col["key"]: self._set_interval_gen_semitones(s, k),
                    )
                    cell_frame.configure(cursor="pointinghand")
                self.interval_gen_cell_labels[(col["key"], semitones)] = (cell_frame, lbl)

        self.interval_generation_panel.pack(fill=tk.BOTH, expand=True)
        self._interval_generation_panel_created = True
        self._refresh_interval_gen_root_selector()
        self._update_interval_generation_display()

    def _refresh_interval_gen_table_language(self) -> None:
        title_labels = getattr(self, "interval_gen_title_labels", None)
        if not title_labels:
            return
        from PySide6.QtGui import QFont, QFontMetrics

        title_metrics = QFontMetrics(QFont(self.ui_font_family, 12))
        title_col_w = max(
            title_metrics.horizontalAdvance(self._interval_gen_grid_title(column))
            for column, _title_cell, _title_label in title_labels
        ) + 80
        self._apply_interval_gen_table_titles(title_col_w)

    def _apply_interval_gen_table_titles(self, title_col_w: int) -> None:
        for column, title_cell, title_label in self.interval_gen_title_labels:
            title_cell.setMinimumWidth(title_col_w)
            title_label.configure(text=self._interval_gen_grid_title(column))

    def _refresh_interval_gen_buttons_state(self):
        if not hasattr(self, "_interval_generation_panel_created"):
            return
        has_selection = self.interval_gen_semitones is not None
        self.interval_gen_play_btn.set_enabled(has_selection)
        self.interval_gen_play_reverse_btn.set_enabled(has_selection)
        self.interval_gen_play_btn.set_selected(
            has_selection and self.interval_gen_last_play_reverse is False
        )
        self.interval_gen_play_reverse_btn.set_selected(
            has_selection and self.interval_gen_last_play_reverse is True
        )

    def _refresh_interval_gen_table_selection(self):
        if not hasattr(self, "interval_gen_cell_labels"):
            return
        bg = "#0f1c2c"
        for (col_key, semitones), (cell_frame, lbl) in self.interval_gen_cell_labels.items():
            selected = (
                self.interval_gen_semitones is not None
                and int(self.interval_gen_semitones) == semitones
                and self.interval_gen_column_key == col_key
            )
            if selected:
                cell_frame.configure(bg=self.color_accent)
                lbl.configure(bg=self.color_accent, fg="#17273a")
            else:
                cell_frame.configure(bg=bg)
                lbl.configure(bg=bg, fg=self.color_text)

    def _update_interval_generation_display(self):
        if not hasattr(self, "_interval_generation_panel_created"):
            return
        self._refresh_interval_gen_table_language()
        self._refresh_interval_gen_table_selection()
        self._refresh_interval_gen_buttons_state()
        notes = self.interval_gen_notes()
        if not notes:
            self.interval_gen_notes_display.configure(text="-")
            self.interval_gen_name_display.configure(text="-")
            self.interval_gen_alt_display.configure(text="-")
            self.interval_gen_semitones_display.configure(text="-")
            return
        semitones = int(self.interval_gen_semitones)
        self.interval_gen_notes_display.configure(
            text=f"{self.note_name(notes[0])} - {self.note_name(notes[1])}"
        )
        self.interval_gen_name_display.configure(text=self.get_interval_gen_name())
        self.interval_gen_alt_display.configure(text=self.get_interval_gen_alt_names())
        self.interval_gen_semitones_display.configure(text=str(semitones))
