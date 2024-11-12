# main.py
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt  # Added this import
import sys
from gui import SpotlightApp


def main():
    # Enable High DPI display support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = SpotlightApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()