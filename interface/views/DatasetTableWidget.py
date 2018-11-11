import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu
from interface.util import api

class DatasetTableWidget(QTableWidget):
    def __init__(self, mainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mainWindow = mainWindow
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
        self.__dataset = None
        self.displayDatasetFromFile('dataset.json')

    def contextMenuEvent(self, event):
        tableMenu = QMenu()
        tableMenu.addAction('Generate Fooling Image')
        sendSampleAction = tableMenu.addAction('Send Sample to API')
        sendSampleAction.triggered.connect(self.classifySelected)
        tableMenu.exec_(QCursor.pos())

    def getSelectedClasses(self):
        indexes = self.selectionModel().selection().indexes()
        if indexes:
            rows = set()
            classes = []
            for i in indexes:
                rows.add(i.row())
            for row in rows:
                classes.append(self.__dataset['classes'][row])
            return classes
        return []

    def classifySelected(self):
        classes = self.getSelectedClasses()
        for c in classes:
            res = api.classifyFile(c['thumbnail'])
            self.mainWindow.log(res)

    def displayDatasetFromFile(self, filename):
        with open(filename, 'r') as fo:
            self.__dataset = json.load(fo)
            i = 0
            self.setRowCount(len(self.__dataset['classes']))
            for classdef in self.__dataset['classes']:
                classId = QTableWidgetItem(str(classdef['classId']))
                classId.setFlags(classId.flags() ^ Qt.ItemIsEditable);

                preview = QTableWidgetItem()
                preview.setData(Qt.DecorationRole, QPixmap(classdef['thumbnail']))
                preview.setFlags(preview.flags() ^ Qt.ItemIsEditable);

                name = QTableWidgetItem(classdef['name'])
                name.setFlags(name.flags() ^ Qt.ItemIsEditable);

                self.setItem(i, 0, classId)
                self.setItem(i, 1, preview)
                self.setItem(i, 2, name)
                self.setRowHeight(i, 64)
                i += 1

    def tableClick(self, x, y):
        self.selectRow(x)
