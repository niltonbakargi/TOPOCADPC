import sys
import os

# Garante que imports relativos funcionem ao rodar como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName('Topocad PC')
    app.setOrganizationName('Topocad')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
