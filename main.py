# windows/main.py
from gui import SpotlightApp
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    window = SpotlightApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
