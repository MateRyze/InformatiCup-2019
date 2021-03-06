import os
import time
import webbrowser
from PyQt5.QtCore import QUrl, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QMenu, QSplitter
from PyQt5.QtWidgets import QHBoxLayout, QPushButton
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

    # Signal used to append logging output, allows printing from another thread
    sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.__initDataset()
        self.__initWindow()
        self.__initTopBar()
        self.__initMenuBar()
        self.__initTable()
        self.__initConsole()
        # Sizes of the splitterWidget (the vertical splitter) need to be set
        # after all elements have been added to it. This is slightly ugly,
        # but the best way to solve this (I think).
        self.splitterWidget.setSizes([512, 128])
        self.show()

        logging.setLoggingFunction(lambda x: self.sig.emit(x))
        self.sig.connect(self.log)

    def __initWindow(self):
        """
        Initialize the main properties of the window.
        """
        self.setWindowTitle('Kollektiv 5 GUI')
        self.resize(1280, 720)

        self.mainWidget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setDirection(QVBoxLayout.BottomToTop)
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

        self.splitterWidget = QSplitter()
        self.splitterWidget.setOrientation(Qt.Vertical)
        self.splitterWidgetLayout = QVBoxLayout(self.splitterWidget)
        self.splitterWidget.setLayout(self.splitterWidgetLayout)
        self.layout.addWidget(self.splitterWidget)

    def __initMenuBar(self):
        """
        Initialize the menu bar for the window.
        """
        self.menu = self.menuBar()

        actionQuit = QAction('Close', self)
        actionQuit.triggered.connect(self.close)

        actionViewHelp = QAction('View Documentation', self)
        actionViewHelp.triggered.connect(self.help)

        actionApiPrefs = QAction('API', self)
        actionApiPrefs.triggered.connect(self.openApiSettings)

        # top-level menus
        menuFile = self.menu.addMenu('File')
        menuPrefs = self.menu.addMenu('Preferences')
        menuHelp = self.menu.addMenu('Help')

        # "File" menu
        menuFile.addAction(actionQuit)

        # "Preferences" menu
        menuPrefs.addAction(actionApiPrefs)

        # "Help" menu
        menuHelp.addAction(actionViewHelp)

    def __initTopBar(self):
        """
        Initialize the two buttons atop the dataset table
        """
        self.topBar = QHBoxLayout()

        self.generateButtonAny = QPushButton('Generate Any')
        self.generateButtonAny.clicked.connect(
            self.openGeneratingWindowNoTarget
        )
        self.topBar.addWidget(self.generateButtonAny)

        self.generateButtonSelected = QPushButton('Generate Selected')
        self.generateButtonSelected.setEnabled(False)
        self.generateButtonSelected.clicked.connect(
            self.openGeneratingWindow
        )
        self.topBar.addWidget(self.generateButtonSelected)

        self.layout.addLayout(self.topBar)

    def __initTable(self):
        """
        Create the dataset table and place it at the top of the vertical
        splitter.
        """
        self.table = DatasetTableWidget(self, self.splitterWidget)
        self.splitterWidgetLayout.addWidget(self.table)

    def __initConsole(self):
        """
        Create a read-only textbox at the bottom of the vertical splitter.
        It is used to print text-based information.
        """

        self.console = QTextEdit(self.splitterWidget)
        self.console.setReadOnly(True)
        self.log('Started...')
        self.splitterWidgetLayout.addWidget(self.console)

    def __initDataset(self):
        """
        Load the dataset from the default path
        """
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
        """
        Open the window to modify the API settings
        """
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
        """
        Open the handbook in the system's PDF reader
        """
        # webbrowser.open does not necessarily open the file in a webbrowser
        # it opens it in whatever program the user has set as their pdf reader
        webbrowser.open(
            'file://%s' % os.path.join(getResourcePath(), 'handbook.pdf'))
