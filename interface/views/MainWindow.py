#!/usr/bin/env python3
import os
import time
import webbrowser
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, QDialog, QVBoxLayout, QTextEdit, QMenu, QSplitter
from interface.views.DatasetTableWidget import DatasetTableWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initWindow()
        self.__initMenuBar()
        self.__initTable()
        self.__initConsole()
        self.main_widget.setSizes([512, 128])
        self.show()

    def __initWindow(self):
        self.setWindowTitle('Penis')
        self.setGeometry(10, 10, 1280, 720)

        self.main_widget = QSplitter()
        self.main_widget.setOrientation(Qt.Vertical)
        self.layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def __initMenuBar(self):
        self.menu = self.menuBar()

        actionLoadDataset = QAction('Open Dataset Specification', self)
        actionQuit = QAction('Close', self)
        actionViewHelp = QAction('View Documentation', self)
        actionViewHelp.triggered.connect(self.help)
        actionGenerationPrefs = QAction('Data Generation', self)
        actionApiPrefs = QAction('API', self)
        actionGuiPrefs = QAction('GUI', self)

        menuFile = self.menu.addMenu('File')
        menuPrefs = self.menu.addMenu('Preferences')
        menuHelp = self.menu.addMenu('Help')

        menuFile.addAction(actionLoadDataset)
        menuFile.addSeparator()
        menuFile.addAction(actionQuit)
        menuPrefs.addAction(actionGenerationPrefs)
        menuPrefs.addAction(actionApiPrefs)
        menuPrefs.addAction(actionGuiPrefs)
        menuHelp.addAction(actionViewHelp)

    def __initTable(self):
        self.table = DatasetTableWidget(self, self.main_widget)
        self.layout.addWidget(self.table)

    def __initConsole(self):
        self.console = QTextEdit(self.main_widget)
        self.console.setReadOnly(True)
        self.log('Started...')
        self.layout.addWidget(self.console)

    def log(self, text):
        date = time.strftime('%H:%M:%S')
        self.console.setText('%s\n%s: %s'%(self.console.toPlainText(), date, text))
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        self.statusBar().showMessage(text)

    def help(self, x = 0, y = 1):
        webbrowser.open('https://google.com')
