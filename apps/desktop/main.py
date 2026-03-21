from apps.desktop.darwin_frozen_bootstrap import bootstrap_before_qt

# Antes de importar PySide6 (vía main_app): plugins Qt en .app firmado / MAS.
bootstrap_before_qt()

from midichords.main_app import main


if __name__ == "__main__":
    main()

