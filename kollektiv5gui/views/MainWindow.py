import os
import time
import webbrowser
from PyQt5.QtCore import QUrl, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QMenu, QSplitter
from kollektiv5gui.util import logging
from kollektiv5gui.util.paths import getResourcePath
from kollektiv5gui.views.DatasetTableWidget import DatasetTableWidget
from kollektiv5gui.views.GeneratingWindow import GeneratingWindow
from kollektiv5gui.views.ConfigureApiWindow import ConfigureApiWindow
from kollektiv5gui.models.Dataset import Dataset


class MainWindow(QMainWindow):
    """
    This class represents the main window of the kollektiv5gui. It contains a
    table, which displays an overview of all classes in the dataset, a menu
    at the top, and a read-only textbox below the table.
    """

    sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.__initDataset()
        self.__initWindow()
        self.__initMenuBar()
        self.__initTable()
        self.__initConsole()
        # Sizes of the mainWidget (the vertical splitter) need to be set after
        # all elements have been added to it. This is slightly ugly,
        # but the best way to solve this (I think).
        self.mainWidget.setSizes([512, 128])
        self.show()

        logging.setLoggingFunction(lambda x: self.sig.emit(x))
        self.sig.connect(self.log)

    def __initWindow(self):
        """
        Initialize the main properties of the window.
        """
        self.setWindowTitle('Kollektiv 5 GUI')
        self.resize(1280, 720)

        self.mainWidget = QSplitter()
        self.mainWidget.setOrientation(Qt.Vertical)
        self.layout = QVBoxLayout(self.mainWidget)
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

    def __initMenuBar(self):
        """
        Initialize the menu bar for the window.
        """
        self.menu = self.menuBar()

        actionLoadDataset = QAction('Open Dataset Specification', self)

        actionQuit = QAction('Close', self)
        actionQuit.triggered.connect(self.close)

        actionOpenGeneratorWindow = QAction('Generate Fooling Image', self)
        actionOpenGeneratorWindow.triggered.connect(
            self.openGeneratingWindowNoTarget
        )

        actionViewHelp = QAction('View Documentation', self)
        actionViewHelp.triggered.connect(self.help)

        actionApiPrefs = QAction('API', self)
        actionApiPrefs.triggered.connect(self.openApiSettings)

        # top-level menus
        menuFile = self.menu.addMenu('File')
        menuTools = self.menu.addMenu('Tools')
        menuPrefs = self.menu.addMenu('Preferences')
        menuHelp = self.menu.addMenu('Help')

        # "File" menu
        menuFile.addAction(actionLoadDataset)
        menuFile.addSeparator()
        menuFile.addAction(actionQuit)

        # "Tools" menu
        menuTools.addAction(actionOpenGeneratorWindow)

        # "Preferences" menu
        menuPrefs.addAction(actionApiPrefs)

        # "Help" menu
        menuHelp.addAction(actionViewHelp)

    def __initTable(self):
        """
        Create the dataset table and place it at the top of the vertical
        splitter.
        """
        self.table = DatasetTableWidget(self, self.mainWidget)
        self.layout.addWidget(self.table)

    def __initConsole(self):
        """
        Create a read-only textbox at the bottom of the vertical splitter.
        It is used to print text-based information.
        """

        self.console = QTextEdit(self.mainWidget)
        self.console.setReadOnly(True)
        self.log('Started...')
        self.layout.addWidget(self.console)

    def __initDataset(self):
        self.__dataset = Dataset()
        self.__dataset.loadFromFile(
            os.path.join(getResourcePath(), 'dataset.json')
        )

    def getDataset(self):
        return self.__dataset

    def openGeneratingWindowNoTarget(self):
        """
        Open the generating window without any target classes specified.
        """
        self.generatingWindow = GeneratingWindow(self, [])

    def openGeneratingWindow(self):
        """
        Open the generating window with a set of target classes specified.
        """
        selectedClasses = self.table.getSelectedClasses()
        selectedClassesNames = [c.name for c in selectedClasses]
        unknownClasses = list(filter(lambda x: not x.known, selectedClasses))

        if len(unknownClasses) > 0:
            # display a warning if classes may be unknown in the API
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText(
                'At least one of the classes you are trying to '
                'generate may not be recognized by the API!'
            )
            msg.setWindowTitle('Warning!')
            msg.setDetailedText('\n'.join([c.name for c in unknownClasses]))
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()
            if retval & QMessageBox.Ok == 0:
                return

        self.generatingWindow = GeneratingWindow(self, selectedClassesNames)

    def openApiSettings(self):
        self.configureApiWindow = ConfigureApiWindow(self)

    def log(self, text):
        """
        Print a text to the read-only textbox at the bottom of the window.
        """
        date = time.strftime('%H:%M:%S')
        text = '%s: %s' % (date, text)
        print(text)
        self.console.setText('%s\n%s' % (self.console.toPlainText(), text))
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )
        self.statusBar().showMessage(text)

    def help(self):
        webbrowser.open('https://lmgtfy.com/?s=d&q=Wie+schreibt+man+eine+gute+Dokumentation%3F')
