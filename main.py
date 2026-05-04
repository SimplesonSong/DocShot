"""DocShot application entry point."""

import sys
import os


class NullWriter:
    def write(self, text):
        pass

    def flush(self):
        pass

    def isatty(self):
        return False


if sys.stdout is None:
    sys.stdout = NullWriter()

if sys.stderr is None:
    sys.stderr = NullWriter()

if sys.stdin is None:
    sys.stdin = open(os.devnull, "r")

import sys
from pathlib import Path


def main() -> None:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from app.ui import MainWindow

    app = QApplication(sys.argv)
    icon_path = Path(__file__).resolve().parent / "assets" / "icon.png"
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
    else:
        icon = QIcon()

    window = MainWindow()
    if not icon.isNull():
        window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
