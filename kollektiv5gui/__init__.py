import sys
from PyQt5.QtWidgets import QApplication
from kollektiv5gui.views.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
