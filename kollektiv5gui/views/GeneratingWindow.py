import os
import time
import webbrowser
from collections import namedtuple
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QFileDialog, QComboBox, QHBox
from kollektiv5gui.generators.SpammingGenerator import SpammingGenerator
from kollektiv5gui.generators.EAGenerator import EAGenerator

class GeneratingWindow(QDialog):
    """
    This window allows generating and previewing images for the dataset. It displays the generated image on one side
    and an example image of the detected class on the other side.
    """

    GENERATORS = [
        ('Evolutionary Algorithm', EAGenerator),
        ('Spamming', SpammingGenerator),
    ]

    PreviewContainer = namedtuple('PreviewContainer', 'boxLeft boxLeftLayout boxRight boxRightLayout generatedImage generatedImageLabel detectedImageLabel classnameLabel')

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        self.generator = None
        self.selectedGeneratorId = 0
        self.generatedPixmap = None

        self.__initWindow()
        self.__initLayout()
        self.show()

    def closeEvent(self, event):
        if not self.generator is None and self.generator.isAlive():
            self.generator.stop()

    def __initWindow(self):
        self.setWindowTitle('Generate Fooling Image')
        self.setFixedSize(730, 360)

    def __clearPreviews(self):
        for preview in self.previews:
            preview.boxLeft.setParent(None)

    def __initLayout(self):
        self.layout = QVBoxLayout()

        self.buttonsContainer = QHBox()

        self.generatorSelection = QComboBox()
        for generator in self.GENERATORS:
            self.generatorSelection.addItem(generator[0])
        self.generatorSelection.setGeometry(32, 32, 200, 32)
        self.generatorSelection.currentIndexChanged.connect(self.__selectGenerator)
        self.generatorSelection.setCurrentIndex(self.selectedGeneratorId)
        self.buttonsContainer.addWidget(self.generatorSelection)

        self.generateButton = QPushButton('Generate Image')
        self.generateButton.setGeometry(264, 32, 200, 32)
        self.generateButton.clicked.connect(self.__generate)
        self.buttonsContainer.addWidget(self.generateButton)

        self.saveButton = QPushButton('Save Image')
        self.saveButton.setGeometry(496, 32, 200, 32)
        self.saveButton.clicked.connect(self.__saveGenerated)
        self.saveButton.setEnabled(False)
        self.buttonsContainer.addWidget(self.saveButton)

        self.layout.addWidget(self.buttonsContainer)

        self.previews = []
        for i in range(self.GENERATORS[self.selectedGeneratorId][1].IMAGE_COUNT):
            x = i % 3
            y = i // 3
            xPos = 32 + x * 200
            yPos = 96 + y * 116

            boxLeft = QGroupBox(self)
            boxLeft.setGeometry(xPos, yPos, 100, 100)
            boxLeft.setTitle('Generated')
            boxLeftLayout = QVBoxLayout()
            boxLeft.setLayout(boxLeftLayout)

            boxRight = QGroupBox(self)
            boxRight.setGeometry(xPos + 100, yPos, 100, 100)
            boxRight.setTitle('Detected')
            boxRightLayout = QVBoxLayout()
            boxRight.setLayout(boxRightLayout)

            generatedImageLabel = QLabel(boxLeft)
            generatedImage = QImage()
            generatedImageLabel.setPixmap(QPixmap.fromImage(generatedImage))
            generatedImageLabel.setScaledContents(True)
            generatedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            boxLeftLayout.addWidget(generatedImageLabel)

            detectedImageLabel = QLabel(boxRight)
            detectedImageLabel.setPixmap(QPixmap('res/class_images/00.png'))
            detectedImageLabel.setScaledContents(True)
            detectedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            boxRightLayout.addWidget(detectedImageLabel)

            classnameLabel = QLabel(self)
            classnameLabel.setText('')
            classnameLabel.setGeometry(32, 300, 500, 32)

            self.previews.append(self.PreviewContainer(
                boxLeft,
                boxLeftLayout,
                boxRight,
                boxRightLayout,
                generatedImage,
                generatedImageLabel,
                detectedImageLabel,
                classnameLabel,
            ))

        self.outputLabel = QLabel(self)
        self.outputLabel.setWordWrap(True)
        self.outputLabel.setText('')
        self.outputLabel.setGeometry(500, 96, 500, 100)

    def printStatistics(self, classname, confidence, apiCalls, startTime):
        stats = ('Confidence: %i%%\n'%(confidence*100) +
            'API Calls: %d\n'%(apiCalls) +
            'Runtime: %.0fs\n'%(time.time() - startTime))
        self.outputLabel.setText(stats)
        self.classnameLabel.setText(classname)

    def __onStepCallback(self, classId, confidence):
        self.printStatistics(classId, confidence, self.generator.getApiCalls(), self.generator.getStartTime())
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
        self.generator = self.GENERATORS[self.selectedGeneratorId][1]()
        self.generator.setCallbacks(stepCallback, finishedCallback, failureCallback)
        self.generator.start()

    def __saveGenerated(self):
        filename = QFileDialog.getSaveFileName(self, filter='Image Files (*.png *.jpg *.bmp)')[0]
        self.generatedPixmap.save(filename)

    def __selectGenerator(self, generatorId):
        self.selectedGeneratorId = generatorId
        self.__clearPreviews()
        self.__initLayout()

    def updatePreview(self, classname, previewPixmap):
        tempQImage = QImage(previewPixmap, 64, 64, QImage.Format_RGB888)
        self.generatedPixmap = QPixmap.fromImage(tempQImage)
        self.generatedImageLabel.setPixmap(self.generatedPixmap)

        c = self.mainWindow.getDataset().getClassByName(classname)
        self.detectedImageLabel.setPixmap(QPixmap(c.thumbnailPath))
