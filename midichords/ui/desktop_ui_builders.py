from __future__ import annotations

from typing import Optional

import midichords.qt.tk_compat as tk
from PySide6.QtWidgets import QHBoxLayout

from midichords.ui.widgets_qt import RoundedPanel


def build_top_bar(app: object, container: tk.Widget) -> None:
    """Build the desktop header and publish its stable widgets on ``app``."""
    bg = app.cget("background")
    mode_bar = tk.Frame(container, bg=bg, bd=0, highlightthickness=0)
    mode_bar.pack(fill=tk.X, pady=(0, 6))
    for column in range(3):
        mode_bar.columnconfigure(column, weight=1)

    title_col = tk.Frame(mode_bar, bg=bg, bd=0, highlightthickness=0)
    title_col.grid(row=0, column=0, sticky="w")
    app.top_title_label = tk.Label(
        title_col, text="", bg=bg, fg=app.color_text,
        font=(app.ui_font_family, 20, "bold"),
    )
    app.top_title_label.pack(side=tk.LEFT, padx=(16, 0))

    mode_center = tk.Frame(mode_bar, bg=bg, bd=0, highlightthickness=0)
    mode_center.grid(row=0, column=1, sticky="ns")
    app.mode_trigger_var = tk.StringVar(value="")
    app._mode_picker_hover = False
    app.mode_picker_trigger = tk.Canvas(
        mode_center, width=240, height=40, bg="transparent",
        highlightthickness=0, bd=0, cursor="hand2",
    )
    app.mode_picker_trigger.pack(side=tk.LEFT)
    try:
        app.mode_picker_trigger.setMaximumWidth(280)
    except Exception:
        pass

    try:
        app._mode_picker_card = getattr(app, "color_card", "#3a4452")
        app._mode_picker_border = getattr(app, "color_border", "#56627a")
        app._mode_picker_hover_border = getattr(app, "color_border_hover", "#6a7a98")
        app.mode_picker_trigger.setStyleSheet(f"""
            background-color: {app._mode_picker_card};
            border: 1px solid {app._mode_picker_border};
            border-radius: 8px;
            color: {getattr(app, 'color_text', '#e9edf2')};
        """)
    except Exception:
        pass

    app._mode_picker_text_id = app.mode_picker_trigger.create_text(
        120, 20, anchor="center", text="", fill=app.color_text,
        font=(app.ui_font_family, 15, "bold"),
    )
    app._mode_picker_arrow_id = app.mode_picker_trigger.create_text(
        0, 20, anchor="e", text="▼", fill=app.color_muted,
        font=(app.ui_font_family, 11),
    )

    def redraw(_event: Optional[tk.Event] = None) -> None:
        width = max(120, int(app.mode_picker_trigger.winfo_width()))
        height = max(34, int(app.mode_picker_trigger.winfo_height()))
        app.mode_picker_trigger.delete("mode_picker_bg")
        app.mode_picker_trigger.coords(app._mode_picker_text_id, width / 2, height / 2)
        app.mode_picker_trigger.coords(app._mode_picker_arrow_id, width - 14, height / 2)
        try:
            border = app._mode_picker_hover_border if app._mode_picker_hover else app._mode_picker_border
            app.mode_picker_trigger.setStyleSheet(f"""
                background-color: {app._mode_picker_card};
                border: 1px solid {border};
                border-radius: 8px;
            """)
        except Exception:
            pass

    def refresh_text(*_args: object) -> None:
        app.mode_picker_trigger.itemconfigure(
            app._mode_picker_text_id, text=app.mode_trigger_var.get()
        )

    app.mode_picker_trigger.bind("<Configure>", redraw)
    app.mode_picker_trigger.bind("<Button-1>", app._toggle_mode_selector)
    app.mode_picker_trigger.bind(
        "<Enter>", lambda _event: (setattr(app, "_mode_picker_hover", True), redraw())
    )
    app.mode_picker_trigger.bind(
        "<Leave>", lambda _event: (setattr(app, "_mode_picker_hover", False), redraw())
    )
    app.mode_trigger_var.trace_add("write", refresh_text)
    refresh_text()
    redraw()

    app.top_right_controls = tk.Frame(mode_bar, bg=bg, bd=0, highlightthickness=0)
    app.top_right_controls.grid(row=0, column=2, sticky="e")
    app.top_right_mode_controls = tk.Frame(
        app.top_right_controls, bg=bg, bd=0, highlightthickness=0
    )
    app.top_right_mode_controls.pack(side=tk.LEFT, padx=(0, 8))
    app._help_active = False

    app.help_icon_btn = tk.Label(
        app.top_right_controls, text="?", fg=app.color_muted, bg=bg,
        font=(app.ui_font_family, 18, "bold"), cursor="hand2",
    )
    app.help_icon_btn.pack(side=tk.LEFT, padx=(0, 8))
    app.help_icon_btn.bind("<Button-1>", lambda _event: app._toggle_help_mode())
    app.help_icon_btn.bind("<Enter>", lambda _event: app._on_help_btn_enter())
    app.help_icon_btn.bind("<Leave>", lambda _event: app._on_help_btn_leave())

    app.config_icon_btn = tk.Label(
        app.top_right_controls, text="⚙", fg=app.color_accent, bg=bg,
        font=(app.ui_font_family, 22, "bold"), cursor="hand2",
    )
    app.config_icon_btn.pack(side=tk.LEFT, padx=(0, 16))
    app.config_icon_btn.bind("<Button-1>", lambda _event: app.open_settings_dialog())
    app.config_icon_btn.bind(
        "<Enter>", lambda _event: app.config_icon_btn.configure(fg=app.color_accent_soft)
    )
    app.config_icon_btn.bind(
        "<Leave>", lambda _event: app.config_icon_btn.configure(fg=app.color_accent)
    )


def build_mode_frames(app: object) -> None:
    """Create the mutually exclusive right-panel roots for every desktop mode."""
    specs = (
        ("tab_detection_frame", 0, 3),
        ("tab_generation_frame", 6, 4),
        ("tab_circle_frame", 6, 4),
        ("tab_scale_frame", 6, 4),
        ("tab_metronome_frame", 6, 6),
        ("tab_tuner_frame", 6, 6),
        ("tab_interval_frame", 6, 4),
    )
    for attribute, padx, pady in specs:
        setattr(
            app,
            attribute,
            tk.Frame(
                app.chord_panel,
                bg=app.color_surface_alt,
                bd=0,
                highlightthickness=0,
                padx=padx,
                pady=pady,
            ),
        )

    app.tab_detection_frame.pack(fill=tk.X, expand=False, anchor="nw")
    # Unmanaged Qt children remain visible by default and would cover the active mode.
    for hidden_tab in (
        app.tab_generation_frame,
        app.tab_circle_frame,
        app.tab_scale_frame,
        app.tab_metronome_frame,
        app.tab_tuner_frame,
        app.tab_interval_frame,
    ):
        hidden_tab.setVisible(False)


def build_main_panel_shell(app: object, container: tk.Widget) -> None:
    """Build the responsive staff/result shell that owns all mode panels."""
    top_area = tk.Canvas(container, bg=app.color_bg, bd=0, highlightthickness=0)
    top_area.pack(fill=tk.BOTH, expand=True, pady=(0, 2))
    app.left_panel = RoundedPanel(
        top_area, radius=12, bg_color=app.color_surface_alt,
        border_color=app.color_border, border_width=1.2,
        padding=(12, 12, 12, 12),
    )
    app.right_panel = RoundedPanel(
        top_area, radius=12, bg_color=app.color_surface_alt,
        border_color=app.color_border, border_width=1.2,
        padding=(10, 8, 10, 8),
    )

    def layout_panels(_event: Optional[tk.Event] = None) -> None:
        app._draw_vertical_gradient(
            top_area, app.color_bg_gradient_top, app.color_bg_gradient_bottom
        )
        width = max(1, int(top_area.winfo_width()))
        height = max(1, int(top_area.winfo_height()))
        usable_width = max(1, width - 12)
        left_width = max(1, int(usable_width * 0.58))
        right_width = max(480, usable_width - left_width)
        left_width = max(1, usable_width - right_width)
        app.left_panel.place(x=0, y=0, width=left_width, height=height)
        app.right_panel.place(x=left_width + 12, y=0, width=right_width, height=height)

    top_area.bind("<Configure>", layout_panels)
    layout_panels()

    app.staff_canvas = tk.Canvas(
        app.left_panel.content, bg="#0f1621", highlightthickness=1,
        highlightbackground="#3a4558",
    )
    app.left_panel_title_label = tk.Label(
        app.left_panel.content, text="", bg=app.color_surface_alt,
        fg=app.color_muted, font=(app.ui_font_family, 14, "bold"), anchor="w",
    )
    app.left_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 5))

    app.generated_chord_var = tk.StringVar(value="-")
    app.staff_generated_chord_frame = tk.Frame(
        app.left_panel.content, bg="#1a2330", bd=0, highlightthickness=0
    )
    app.staff_generated_chord_caption = tk.Label(
        app.staff_generated_chord_frame, text="", bg="transparent",
        fg=app.color_muted, font=(app.ui_font_family, 14), highlightthickness=0,
    )
    app.staff_generated_chord_caption.pack(side=tk.LEFT, padx=(2, 4), pady=2)
    app.staff_generated_chord_value = tk.Label(
        app.staff_generated_chord_frame, textvariable=app.generated_chord_var,
        bg="transparent", fg=app.color_accent,
        font=(app.ui_font_family, 20, "bold"), anchor="w", highlightthickness=0,
    )
    app.staff_generated_chord_value.pack(
        side=tk.LEFT, fill=tk.X, expand=True, pady=2, padx=(0, 2)
    )
    try:
        app.staff_generated_chord_frame.setStyleSheet(
            "background-color: #1a2330; border: 1px solid #4a5668;"
        )
        layout = app.staff_generated_chord_frame.layout()
        if isinstance(layout, QHBoxLayout):
            layout.setContentsMargins(8, 4, 8, 4)
    except Exception:
        pass
    app.staff_generated_chord_frame.pack(fill=tk.X, anchor="w", pady=(0, 8))
    try:
        policy = app.staff_generated_chord_frame.sizePolicy()
        policy.setRetainSizeWhenHidden(False)
        app.staff_generated_chord_frame.setSizePolicy(policy)
        app.staff_generated_chord_frame.setVisible(False)
    except Exception:
        app.staff_generated_chord_frame.pack_forget()
    app.staff_canvas.pack(fill=tk.BOTH, expand=True)

    app.right_panel_title_label = tk.Label(
        app.right_panel.content, text="", bg=app.color_surface_alt,
        fg=app.color_muted, font=(app.ui_font_family, 14, "bold"), anchor="w",
    )
    app.right_panel_title_label.pack(fill=tk.X, anchor="w", pady=(0, 5))
    app.right_side_panel = tk.Frame(
        app.right_panel.content, bg=app.color_surface_alt, bd=0,
        highlightthickness=0, padx=0,
    )
    app.right_side_panel.pack(fill=tk.BOTH, expand=True)
    app.right_side_panel.columnconfigure(0, weight=1)
    app.chord_panel = tk.Frame(
        app.right_side_panel, bg=app.color_surface_alt, bd=0,
        highlightthickness=0, padx=0, pady=0,
    )
    app.chord_panel.grid(row=0, column=0, sticky="nsew")
    app.right_side_panel.rowconfigure(0, weight=1)
    build_mode_frames(app)
