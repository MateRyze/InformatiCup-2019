import sys
import os
import time
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTableWidget, QVBoxLayout, QAction, QDialog, QTableWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 600
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Penis')
        self.setGeometry(10, 10, 1280, 720)

        self.statusBar().showMessage('Message in statusbar.')

        self.table = QTableWidget(self)
        self.table.verticalHeader().setVisible(False)
        self.table.setGeometry(32, 32,300, 300)
        self.table.setColumnCount(3)
        self.table.setColumnWidth(0, 64)
        self.table.setColumnWidth(1, 64)
        self.table.setColumnWidth(2, 500)
        self.table.setRowCount(43)
        self.table.setHorizontalHeaderLabels([
            'ClassID',
            'Preview',
            'Textual Name',
        ])
        self.insertClasses()

        viewHelp = QAction('View Documentation', self)
        viewHelp.triggered.connect(self.help)

        menu = self.menuBar()
        menu.addMenu('File')
        menu.addMenu('Generation')
        menu.addMenu('Preferences')
        menuHelp = menu.addMenu('Help')
        menuHelp.addAction(viewHelp)

        self.setCentralWidget(self.table)
        self.show()

    def insertClasses(self):
        for i in range(43):
            classId = QTableWidgetItem('%i'%i)
            preview = QTableWidgetItem()
            preview.setData(Qt.DecorationRole, QPixmap(os.path.join('res', 'class_images', '%02i.png'%i)))
            name = QTableWidgetItem('Ein großer Penis')
            self.table.setItem(i, 0, classId)
            self.table.setItem(i, 1, preview)
            self.table.setItem(i, 2, name)

    def help(self):
        self.statusBar().showMessage('%f'%time.time())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    sys.exit(app.exec_())
