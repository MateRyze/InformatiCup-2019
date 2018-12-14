#!/usr/bin/env python3
import os
import time
import webbrowser
import threading
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QGroupBox, QVBoxLayout, QPushButton, QSizePolicy, QFileDialog, QComboBox
from kollektiv5gui.generators.SpammingGenerator import SpammingGenerator

class GeneratingWindow(QDialog):
    """
    This window allows generating and previewing images for the dataset. It displays the generated image on one side
    and an example image of the detected class on the other side.
    """

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.generator = None
        self.generatedPixmap = None

        self.__initWindow()
        self.__initLayout()
        self.show()

    def closeEvent(self, event):
        if not self.generator is None and self.generator.isAlive():
            self.generator.stop()

    def __initWindow(self):
        self.setWindowTitle('Generate Fooling Image')
        self.setGeometry(0, 0, 640, 360)

    def __initLayout(self):
        self.boxLeft = QGroupBox(self)
        self.boxLeft.setGeometry(32, 32, 200, 200)
        self.boxLeft.setTitle('Generated')
        self.boxLeftLayout = QVBoxLayout()
        self.boxLeft.setLayout(self.boxLeftLayout)

        self.boxRight = QGroupBox(self)
        self.boxRight.setGeometry(264, 32, 200, 200)
        self.boxRight.setTitle('Detected')
        self.boxRightLayout = QVBoxLayout()
        self.boxRight.setLayout(self.boxRightLayout)

        self.generatedImageLabel = QLabel(self.boxLeft)
        self.generatedImage = QImage()
        self.generatedImageLabel.setPixmap(QPixmap.fromImage(self.generatedImage))
        self.generatedImageLabel.setScaledContents(True)
        self.generatedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.boxLeftLayout.addWidget(self.generatedImageLabel)

        self.detectedImageLabel = QLabel(self.boxRight)
        self.detectedImageLabel.setPixmap(QPixmap('res/class_images/00.png'))
        self.detectedImageLabel.setScaledContents(True)
        self.detectedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.boxRightLayout.addWidget(self.detectedImageLabel)

        self.detectedLabel = QLabel(self)
        self.detectedLabel.setText('123123')
        self.detectedLabel.setGeometry(32, 232, 600, 32)

        self.generatorSelection = QComboBox(self)
        self.generatorSelection.addItem('Spamming')
        self.generatorSelection.setGeometry(64, 0, 200, 24)

        self.generateButton = QPushButton('Generate Image', self)
        self.generateButton.setGeometry(264, 296, 200, 32)
        self.generateButton.clicked.connect(self.__generate)

        self.saveButton = QPushButton('Save Image', self)
        self.saveButton.setGeometry(32, 296, 200, 32)
        self.saveButton.clicked.connect(self.__saveGenerated)
        self.saveButton.setEnabled(False)

    def __onStepCallback(self, classId, confidence):
        self.detectedLabel.setText('(%03i%%) %s'%(confidence*100, classId))
        self.updatePreview(classId, self.generator.getImage())

    def __onFailureCallback(self):
        pass

    def __onFinishedCallback(self):
        self.generateButton.setEnabled(True)
        self.saveButton.setEnabled(True)

    def __generate(self):
        self.generateButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        # currying of the callback functions to pass the "self" parameter
        stepCallback = lambda *args, **kwargs: self.__onStepCallback(*args, **kwargs)
        finishedCallback = lambda *args, **kwargs: self.__onFinishedCallback(*args, **kwargs)
        failureCallback = lambda *args, **kwargs: self.__onFailureCallback(*args, **kwargs)
        self.generator = SpammingGenerator()
        self.generator.setCallbacks(stepCallback, finishedCallback, failureCallback)
        self.generator.start()

    def __saveGenerated(self):
        filename = QFileDialog.getSaveFileName(self, filter='Image Files (*.png *.jpg *.bmp)')[0]
        self.generatedPixmap.save(filename)

    def updatePreview(self, classname, previewPixmap):
        tempQImage = QImage(previewPixmap, 64, 64, QImage.Format_RGB888)
        self.generatedPixmap = QPixmap.fromImage(tempQImage)
        self.generatedImageLabel.setPixmap(self.generatedPixmap)

        c = self.mainWindow.getDataset().getClassByName(classname)
        self.detectedImageLabel.setPixmap(QPixmap(c.thumbnailPath))
