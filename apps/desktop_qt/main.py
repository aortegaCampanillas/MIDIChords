import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from midichords.qt_app import run_qt_detection_app


if __name__ == "__main__":
    run_qt_detection_app()

import os
import sys


# Asegura que el directorio raíz del proyecto esté en sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from midichords.qt_app import run_qt_app


if __name__ == "__main__":
    run_qt_app()

