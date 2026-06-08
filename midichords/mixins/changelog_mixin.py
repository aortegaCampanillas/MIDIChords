"""Mixin para mostrar el panel de novedades/changelog."""

import midichords.qt.tk_compat as tk
from midichords.core.changelog import get_changelog_items_for_platform


class ChangelogMixin:
    """Proporciona funcionalidad de panel de novedades para la app."""

    def open_changelog_dialog(self) -> None:
        """Abre un diálogo flotante con el changelog de desktop."""
        # Si ya hay un diálogo abierto, cerrarlo
        if hasattr(self, "_changelog_overlay") and self._changelog_overlay is not None:
            self._close_changelog_dialog()
            return

        # Crear overlay
        overlay = tk.Frame(
            self.chord_panel,
            bg="#2a2f36",
            highlightthickness=1,
            highlightbackground="#505864",
            bd=0,
        )
        overlay.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.90)
        self._changelog_overlay = overlay

        # Header
        header = tk.Frame(overlay, bg="#2a2f36")
        header.pack(fill=tk.X, padx=10, pady=(10, 4))
        tk.Label(
            header,
            text=self.tr("label_whats_new") if hasattr(self, "tr") and "label_whats_new" in str(self.tr("label_whats_new")) else "What's New",
            bg="#2a2f36",
            fg="#f0f0f0",
            font=(self.ui_font_family, 15, "bold"),
        ).pack(side=tk.LEFT)

        # Body
        body = tk.Frame(overlay, bg="#2a2f36")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))

        # Scrollable area
        canvas = tk.Canvas(body, bg="#2a2f36", highlightthickness=0)
        scrollbar = tk.Scrollbar(body, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2a2f36")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Cargar items del changelog
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
            # Agrupar por versión
            versions_dict = {}
            for item in items:
                version = item.get("version", "Unknown")
                if version not in versions_dict:
                    versions_dict[version] = []
                versions_dict[version].append(item)

            # Renderizar por versión
            for version in sorted(versions_dict.keys(), reverse=True):
                version_items = versions_dict[version]
                if version_items:
                    version_date = version_items[0].get("version_date", "")
                    version_label = f"{version} — {version_date}"
                    tk.Label(
                        scrollable_frame,
                        text=version_label,
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
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _close_changelog_dialog(self) -> None:
        """Cierra el diálogo del changelog."""
        if hasattr(self, "_changelog_overlay") and self._changelog_overlay is not None:
            self._changelog_overlay.destroy()
            self._changelog_overlay = None
