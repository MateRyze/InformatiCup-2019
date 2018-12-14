import sys
import os
from PyQt5.QtWidgets import QApplication
from kollektiv5gui.views.MainWindow import MainWindow

# store the path to the module's root directory
__ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def getModuleRoot():
    return __ROOT_DIR

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())
