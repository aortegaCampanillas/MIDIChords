"""Mixin para mostrar el panel de novedades/changelog."""

import midichords.qt.tk_compat as tk
from midichords.core.changelog import get_changelog_items_for_platform, load_changelog


class ChangelogMixin:
    """Proporciona funcionalidad de panel de novedades para la app."""

    def _get_latest_changelog_version(self) -> str:
        changelog = load_changelog()
        if not changelog:
            return ""
        return str(changelog[0].get("version", ""))

    def maybe_show_startup_changelog(self) -> None:
        latest = self._get_latest_changelog_version()
        last_seen = str(self.config_data.get("last_seen_changelog_version", ""))
        if last_seen == latest:
            return
        if self.config_data.get("changelog_dont_show", False):
            return
        items = get_changelog_items_for_platform("desktop")
        if not items:
            return
        self.show_startup_changelog_window()

    def show_startup_changelog_window(self) -> None:
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QCheckBox, QScrollArea, QWidget, QFrame,
        )
        from PySide6.QtCore import Qt

        latest = self._get_latest_changelog_version()
        language = str(self.config_data.get("language", "es"))

        # --- Ventana ---
        win = QDialog(self)
        win.setWindowTitle(self.tr("label_whats_new") if hasattr(self, "tr") else "Novedades")
        win.setFixedSize(540, 520)
        win.setWindowModality(Qt.WindowModality.ApplicationModal)
        win.setStyleSheet("QDialog { background-color: #1e2228; }")

        # Centrar respecto al padre
        try:
            pg = self.frameGeometry()
            win.move(pg.x() + (pg.width() - 540) // 2, pg.y() + (pg.height() - 520) // 2)
        except Exception:
            pass

        root_layout = QVBoxLayout(win)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Área scrollable ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: #1e2228; border: none; }
            QScrollBar:vertical { background: #1e2228; width: 8px; }
            QScrollBar::handle:vertical { background: #3a4050; border-radius: 4px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        content = QWidget()
        content.setStyleSheet("background-color: #1e2228;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        items = get_changelog_items_for_platform("desktop")

        if not items:
            msg = "No hay novedades disponibles." if language == "es" else "No updates available."
            lbl = QLabel(msg)
            lbl.setStyleSheet("color: #888888; font-size: 12px; background: transparent;")
            content_layout.addWidget(lbl)
        else:
            versions_dict: dict[str, list] = {}
            for item in items:
                v = item.get("version", "Unknown")
                versions_dict.setdefault(v, []).append(item)

            for version in sorted(versions_dict.keys(), reverse=True):
                version_items = versions_dict[version]
                version_date = version_items[0].get("version_date", "")

                ver_lbl = QLabel(f"{version}  —  {version_date}")
                ver_lbl.setStyleSheet("color: #f3bf2f; font-size: 11px; font-weight: bold; background: transparent;")
                ver_lbl.setContentsMargins(0, 14, 0, 6)
                content_layout.addWidget(ver_lbl)

                for item in version_items:
                    text = item.get(language, item.get("es", ""))
                    item_lbl = QLabel(f"•  {text}")
                    item_lbl.setStyleSheet("color: #dde3ed; font-size: 10px; background: transparent;")
                    item_lbl.setWordWrap(True)
                    item_lbl.setContentsMargins(12, 2, 0, 2)
                    content_layout.addWidget(item_lbl)

        content_layout.addStretch()
        scroll.setWidget(content)
        root_layout.addWidget(scroll, stretch=1)

        # --- Footer ---
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet("background-color: #252a31;")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(16, 0, 16, 0)

        dont_show_label = "No volver a mostrar" if language == "es" else "Don't show again"
        chk = QCheckBox(dont_show_label)
        chk.setChecked(bool(self.config_data.get("changelog_dont_show", False)))
        chk.setStyleSheet("""
            QCheckBox { color: #a0a8b4; font-size: 10px; background: transparent; }
            QCheckBox::indicator { width: 14px; height: 14px; }
            QCheckBox::indicator:unchecked { border: 1px solid #56627a; background: #1e2228; border-radius: 3px; }
            QCheckBox::indicator:checked { border: 1px solid #f3bf2f; background: #f3bf2f; border-radius: 3px; }
        """)
        f_layout.addWidget(chk)
        f_layout.addStretch()

        close_label = "Cerrar" if language == "es" else "Close"
        close_btn = QPushButton(close_label)
        close_btn.setFixedSize(90, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a7bd5; color: #ffffff;
                border: none; border-radius: 5px;
                font-size: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2e6bc4; }
            QPushButton:pressed { background-color: #2560b0; }
        """)
        f_layout.addWidget(close_btn)
        root_layout.addWidget(footer)

        def on_close() -> None:
            self.config_data["last_seen_changelog_version"] = latest
            self.config_data["changelog_dont_show"] = chk.isChecked()
            self.save_config()
            win.accept()

        close_btn.clicked.connect(on_close)
        win.rejected.connect(on_close)

        self._startup_modal_open = True
        try:
            win.exec()
        finally:
            self._startup_modal_open = False

    def open_changelog_dialog(self) -> None:
        """Abre un diálogo flotante con el changelog de desktop (desde menú)."""
        if hasattr(self, "_changelog_overlay") and self._changelog_overlay is not None:
            self._close_changelog_dialog()
            return

        overlay = tk.Frame(
            self.chord_panel,
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self._changelog_overlay = overlay

        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_whats_new") if hasattr(self, "tr") else "What's New",
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)

        body = tk.Frame(overlay, bg="#2a2f36")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))

        canvas = tk.Canvas(body, bg="#2a2f36", highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg="#2a2f36")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        items = get_changelog_items_for_platform("desktop")

        if not items:
            tk.Label(
                scrollable_frame,
                text="No hay novedades disponibles",
                bg="#2a2f36",
                fg="#888888",
                font=(self.ui_font_family, 12),
            ).pack(pady=20)
        else:
            versions_dict: dict[str, list] = {}
            for item in items:
                version = item.get("version", "Unknown")
                versions_dict.setdefault(version, []).append(item)

            for version in sorted(versions_dict.keys(), reverse=True):
                version_items = versions_dict[version]
                if not version_items:
                    continue
                version_date = version_items[0].get("version_date", "")
                tk.Label(
                    scrollable_frame,
                    text=f"{version} — {version_date}",
                    bg="#2a2f36",
                    fg="#f3bf2f",
                    font=(self.ui_font_family, 12, "bold"),
                ).pack(anchor="w", padx=10, pady=(15, 8))

                for item in version_items:
                    language = str(self.config_data.get("language", "es"))
                    text = item.get(language, item.get("es", ""))
                    tk.Label(
                        scrollable_frame,
                        text=f"• {text}",
                        bg="#2a2f36",
                        fg="#e0e0e0",
                        font=(self.ui_font_family, 10),
                        wraplength=400,
                        justify=tk.LEFT,
                    ).pack(anchor="w", padx=20, pady=4)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _close_changelog_dialog(self) -> None:
        if hasattr(self, "_changelog_overlay") and self._changelog_overlay is not None:
            self._changelog_overlay.destroy()
            self._changelog_overlay = None
