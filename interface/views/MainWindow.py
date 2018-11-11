#!/usr/bin/env python3
import os
import time
import json
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidget, QVBoxLayout, QAction, QDialog, QTableWidgetItem, QVBoxLayout, QTextEdit, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView

class DatasetTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnCount(3)
        self.setColumnWidth(0, 48)
        self.setColumnWidth(1, 64)
        self.setColumnWidth(2, 256)
        self.setHorizontalHeaderLabels([
            'ClassID',
            'Preview',
            'Textual Name',
        ])

    def showContextMenu(self, pos):
        tableMenu = QMenu()
        tableMenu.addAction('Generate Fooling Image')
        tableMenu.addAction('Send Sample to API')
        tableMenu.addAction('Edit Entry...')
        tableMenu._exec()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 600
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Penis')
        self.setGeometry(10, 10, 1280, 720)

        self.statusBar().showMessage('Message in statusbar.')

        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(layout)

        self.table = DatasetTable(self.main_widget)
        self.table.setRowCount(43)
        layout.addWidget(self.table)

        self.console = QTextEdit(self.main_widget)
        self.console.setMaximumHeight(128)
        self.console.setReadOnly(True)
        self.console.setText(':D')
        layout.addWidget(self.console)

        self.displayDatasetFromFile('dataset.json')

        viewHelp = QAction('View Documentation', self)
        viewHelp.triggered.connect(self.help)

        menu = self.menuBar()
        menu.addMenu('File')
        menu.addMenu('Generation')
        menu.addMenu('Preferences')
        menuHelp = menu.addMenu('Help')
        menuHelp.addAction(viewHelp)

        self.setCentralWidget(self.main_widget)
        self.show()

    def displayDatasetFromFile(self, filename):
        with open(filename, 'r') as fo:
            dataset = json.load(fo)
            i = 0
            for classdef in dataset['classes']:
                classId = QTableWidgetItem(str(classdef['classId']))
                classId.setFlags(classId.flags() ^ Qt.ItemIsEditable);

                preview = QTableWidgetItem()
                preview.setData(Qt.DecorationRole, QPixmap(classdef['thumbnail']))
                preview.setFlags(preview.flags() ^ Qt.ItemIsEditable);

                name = QTableWidgetItem(classdef['name'])
                name.setFlags(name.flags() ^ Qt.ItemIsEditable);

                self.table.setItem(i, 0, classId)
                self.table.setItem(i, 1, preview)
                self.table.setItem(i, 2, name)
                self.table.setRowHeight(i, 64)
                i += 1

    def tableClick(self, x, y):
        self.table.selectRow(x)
        self.console.setText('%i/%i\n'%(x, y))

    def help(self, x = 0, y = 1):
        self.statusBar().showMessage('%i/%i'%(x, y))
