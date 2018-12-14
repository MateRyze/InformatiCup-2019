import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu
from kollektiv5gui.util import api
from kollektiv5gui.models.Dataset import Dataset

class DatasetTableWidget(QTableWidget):
    """
    This table displays contains all classes of a dataset. It displays a preview image, the class ids and a textual
    description of the classes.
    """

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
        self.__dataset = mainWindow.getDataset()
        self.renderDataset()

    def contextMenuEvent(self, event):
        """
        Right click anywhere on the table.
        We only care about the current row however, as this defines the used class id.
        """
        tableMenu = QMenu()
        generateAction = tableMenu.addAction('Generate Fooling Image')
        generateAction.triggered.connect(self.mainWindow.openGeneratingWindow)

        sendSampleAction = tableMenu.addAction('Send Sample to API')
        sendSampleAction.triggered.connect(self.classifySelected)

        tableMenu.exec_(QCursor.pos())

    def getSelectedClasses(self):
        """
        Returns a list of all selected class ids.
        """
        indexes = self.selectionModel().selection().indexes()
        if indexes:
            rows = set()
            classes = []
            for i in indexes:
                rows.add(i.row())
            for row in rows:
                classes.append(self.__dataset.getClasses()[row])
            return classes
        return []

    def classifySelected(self):
        """
        Sends the preview images of all selected classes to the API and prints the classification result.
        """
        classes = self.getSelectedClasses()
        for c in classes:
            res = api.classifyFile(c.thumbnailPath)
            self.mainWindow.log(json.dumps(res))

    def renderDataset(self):
        """
        Open a json formatted dataset specification from a file and display the contained information.
        """
        self.setRowCount(self.__dataset.getClassesCount())
        i = 0
        for c in self.__dataset.getClasses():
            classId = QTableWidgetItem(str(c.id))
            # disable editing of the class id
            # this is done for all cells within this row (and for every row)
            classId.setFlags(classId.flags() ^ Qt.ItemIsEditable)

            preview = QTableWidgetItem()
            # c.thumbnailPath contains a filename, passing this value to the constructor of QPixmap
            # automatically loads an image
            preview.setData(Qt.DecorationRole, QPixmap(c.thumbnailPath))
            preview.setFlags(preview.flags() ^ Qt.ItemIsEditable)

            name = QTableWidgetItem(c.name)
            name.setFlags(name.flags() ^ Qt.ItemIsEditable)

            self.setItem(i, 0, classId)
            self.setItem(i, 1, preview)
            self.setItem(i, 2, name)
            # make sure the row is as large as the image within (we just assume a height of 64 pixels)
            self.setRowHeight(i, 64)
            i += 1

    def tableClick(self, x, y):
        self.selectRow(x)
