from PyQt5.QtWidgets import QAction, QDialog, QLabel, QLineEdit, QFormLayout, QHBoxLayout, QPushButton
from kollektiv5gui.util import config

class ConfigureApiWindow(QDialog):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow

        self.__initWindow()
        self.__initLayout()
        self.show()

    def __initWindow(self):
        self.setWindowTitle('Configure API Connection')
        self.setFixedSize(320, 120)

    def __initLayout(self):
        self.layout = QFormLayout(self)

        self.lineEditUrl = QLineEdit(config.get('API', 'url'))
        self.layout.addRow('URL', self.lineEditUrl)

        self.lineEditKey = QLineEdit(config.get('API', 'key'))
        self.layout.addRow('Key', self.lineEditKey)

        saveButton = QPushButton('Apply')
        saveButton.clicked.connect(self.save)
        self.layout.addRow(saveButton)

        self.setLayout(self.layout)

    def save(self):
        config.set('API', 'url', self.lineEditUrl.text())
        config.set('API', 'key', self.lineEditKey.text())
        config.flush()
        self.close()
