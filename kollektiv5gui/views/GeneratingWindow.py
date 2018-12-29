import os
import time
import webbrowser
from collections import namedtuple
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QGroupBox, QPushButton, QSizePolicy, QFileDialog, QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout
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

    Preview = namedtuple('PreviewContainer', 'generatedImageLabel detectedImageLabel classnameLabel confidenceLabel saveButton')

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        self.selectedGeneratorId = 0
        self.previews = []
        self.previewsContainer = None
        self.generator = None
        self.generatedPixmap = None

        self.__initWindow()
        self.__initLayout()
        self.__selectGenerator(self.selectedGeneratorId)
        self.show()

    def closeEvent(self, event):
        if not self.generator is None and self.generator.isAlive():
            self.generator.stop()

    def __initWindow(self):
        self.setWindowTitle('Generate Fooling Image')
        #self.setSize(730, 360)

    def __clearPreviews(self):
        self.previews = []
        if self.previewsContainer is not None:
            for i in reversed(range(self.previewsContainer.count())):
                self.previewsContainer.itemAt(i).widget().setParent(None)
            self.previewsContainer.setParent(None)

    def __initLayout(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttonsContainer = QHBoxLayout()

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

        self.layout.addLayout(self.buttonsContainer)

        self.outputLabel = QLabel()
        self.outputLabel.setWordWrap(True)
        self.outputLabel.setText('')
        self.outputLabel.setText("OUTPUT")
        self.layout.addWidget(self.outputLabel)

    def __initPreviews(self):
        self.previews = []
        self.previewsContainer = QGridLayout()
        for i in range(self.GENERATORS[self.selectedGeneratorId][1].IMAGE_COUNT):
            boxLeft = QGroupBox()
            boxLeftLayout = QVBoxLayout()
            boxLeft.setLayout(boxLeftLayout)

            boxRight = QGroupBox()
            boxRightLayout = QVBoxLayout()
            boxRight.setLayout(boxRightLayout)

            # This way the heading is only on the leftmost image
            # However, we still need to reserve space for the heading label for all other images
            if i == 0:
                boxLeft.setTitle('Generated')
                boxRight.setTitle('Detected')
            else:
                boxLeft.setTitle('')
                boxRight.setTitle('')

            generatedImageLabel = QLabel(boxLeft)
            generatedImageLabel.setScaledContents(True)
            generatedImageLabel.setFixedSize(160, 160)
            generatedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            boxLeftLayout.addWidget(generatedImageLabel)

            detectedImageLabel = QLabel(boxRight)
            detectedImageLabel.setScaledContents(True)
            detectedImageLabel.setFixedSize(160, 160)
            detectedImageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            boxRightLayout.addWidget(detectedImageLabel)

            classnameLabel = QLabel()
            classnameLabel.setText('')

            confidenceLabel = QLabel()
            confidenceLabel.setText('')

            saveButton = QPushButton('Save Image')
            clickedFunction = lambda _, num=i: self.__saveGenerated(num)
            saveButton.clicked.connect(clickedFunction)
            saveButton.setEnabled(False)

            self.previewsContainer.addWidget(boxLeft, 0, i)
            self.previewsContainer.addWidget(boxRight, 1, i)
            self.previewsContainer.addWidget(classnameLabel, 2, i)
            self.previewsContainer.addWidget(confidenceLabel, 3, i)
            self.previewsContainer.addWidget(saveButton, 4, i)

            self.previews.append(self.Preview(
                generatedImageLabel,
                detectedImageLabel,
                classnameLabel,
                confidenceLabel,
                saveButton,
            ))

        self.layout.addLayout(self.previewsContainer)

    def printStatistics(self, apiCalls, startTime, additionalStatistics):
        stats = '\n'.join([
            'API Calls: %d'%apiCalls,
            'Runtime: %.0fs'%(time.time() - startTime),
        ])
        if len(additionalStatistics) > 0:
            stats += '\n' + additionalStatistics
        self.outputLabel.setText(stats)

    def __onStepCallback(self, classes):
        for i in range(len(classes)):
            classname = classes[i][0]
            shortenedClassname = classname[:20] + '...' if len(classname) > 20 else classname
            confidence = classes[i][1]
            self.previews[i].classnameLabel.setText(shortenedClassname)
            self.previews[i].confidenceLabel.setText('%d%%'%(confidence*100))

            previewPixmap = self.generator.getImage(i)
            tempQImage = QImage(previewPixmap, 64, 64, QImage.Format_RGB888)
            generatedPixmap = QPixmap.fromImage(tempQImage)
            self.previews[i].generatedImageLabel.setPixmap(generatedPixmap)

            c = self.mainWindow.getDataset().getClassByName(classname)
            self.previews[i].detectedImageLabel.setPixmap(QPixmap(c.thumbnailPath))

        self.printStatistics(self.generator.getApiCalls(), self.generator.getStartTime(), self.generator.getAdditionalStatistics())

    def __onFailureCallback(self):
        pass

    def __onFinishedCallback(self):
        self.generateButton.setEnabled(True)
        for preview in self.previews: preview.saveButton.setEnabled(True)

    def __generate(self):
        self.generateButton.setEnabled(False)
        for preview in self.previews: preview.saveButton.setEnabled(False)
        # currying of the callback functions to pass the "self" parameter
        stepCallback = lambda *args, **kwargs: self.__onStepCallback(*args, **kwargs)
        finishedCallback = lambda *args, **kwargs: self.__onFinishedCallback(*args, **kwargs)
        failureCallback = lambda *args, **kwargs: self.__onFailureCallback(*args, **kwargs)
        self.generator = self.GENERATORS[self.selectedGeneratorId][1]()
        self.generator.setCallbacks(stepCallback, finishedCallback, failureCallback)
        self.generator.start()

    def __saveGenerated(self, i):
        filename = QFileDialog.getSaveFileName(self, filter='Image Files (*.png *.jpg *.bmp)')[0]
        self.previews[i].generatedImageLabel.pixmap().save(filename)

    def __selectGenerator(self, generatorId):
        self.selectedGeneratorId = generatorId
        self.__clearPreviews()
        self.__initPreviews()
