#!/usr/bin/env python3
import os
import time
import webbrowser
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QGroupBox, QVBoxLayout, QPushButton

class GeneratingWindow(QDialog):
    """
    This window allows generating and previewing images for the dataset. It displays the generated image on one side
    and an example image of the detected class on the other side.
    """

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow

        self.__initWindow()
        self.__initLayout()
        self.show()

    def __initWindow(self):
        self.setWindowTitle('Generate Fooling Image')
        self.setGeometry(0, 0, 640, 360)

    def __initLayout(self):
        self.boxLeft = QGroupBox(self)
        self.boxLeft.setGeometry(32, 32, 200, 200)
        self.boxLeft.setTitle('Generated')

        self.boxRight = QGroupBox(self)
        self.boxRight.setGeometry(264, 32, 200, 200)
        self.boxRight.setTitle('Detected')
        self.boxRightLayout = QVBoxLayout()
        self.boxRight.setLayout(self.boxRightLayout)

        self.generatedLabel = QLabel(self.boxLeft)
        self.generatedImage = QImage()
        self.generatedLabel.setPixmap(QPixmap.fromImage(self.generatedImage))

        self.detectedLabel = QLabel(self.boxRight)
        self.detectedLabel.setPixmap(QPixmap('res/class_images/00.png'))
        self.boxRightLayout.addWidget(self.detectedLabel)

        self.generateButton = QPushButton('Generate Image', self)
        self.generateButton.setGeometry(32, 264, 200, 32)

    def updatePreview(self, classId, previewPixmap):
        pass
