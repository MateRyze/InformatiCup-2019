import os
import time
import webbrowser
import threading
from collections import namedtuple
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QCursor, QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox, QColorDialog, QLineEdit, QWidget
from PyQt5.QtWidgets import QDialog, QLabel, QGroupBox, QPushButton
from PyQt5.QtWidgets import QSizePolicy, QFileDialog, QComboBox, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from kollektiv5gui.generators.SpammingGenerator import SpammingGenerator
from kollektiv5gui.generators.EAGenerator import EAGenerator
from kollektiv5gui.generators.EAGeneratorFields import EAGeneratorFields
from kollektiv5gui.views.EaOptionsWidget import Ui_Options


class GeneratingWindow(QDialog):
    """
    This window allows generating and previewing images for the dataset. It
    displays the generated image on one side and an example image of the
    detected class on the other side.
    """

    # All generators selectable in the dropdown
    GENERATORS = [
        ('Evolutionary Algorithm: Polygons', EAGenerator),
        ('Evolutionary Algorithm: Fields', EAGeneratorFields),
        ('Spamming', SpammingGenerator),
    ]

    Preview = namedtuple('PreviewContainer', [
        'generatedImageLabel',
        'detectedImageLabel',
        'classnameLabel',
        'confidenceLabel',
        'saveButton']
    )

    __lock = threading.Lock()

    def __init__(self, mainWindow, targetClasses):
        super().__init__(mainWindow)
        self.mainWindow = mainWindow
        self.targetClasses = targetClasses

        self.selectedGeneratorId = 0
        self.previews = []
        self.previewsContainer = None
        self.generatedPixmap = None

        self.__initWindow()
        self.__initLayout()
        self.show()
        self.__selectGenerator(self.selectedGeneratorId)

    def closeEvent(self, event):
        """
        Called by Qt when the window is closed, makes sure that the generator
        thread closes.
        """
        if self.generator is not None and self.generator.isAlive():
            self.generator.stop()

    def __initWindow(self):
        """
        Sets the base attributes for the window
        """
        self.setWindowTitle('Generate Fooling Image')

    def __clearPreviews(self):
        """
        Clears the image preview containers.
        Should be called at the start of every generation.
        """
        self.previews = []
        if self.previewsContainer is not None:
            for i in reversed(range(self.previewsContainer.count())):
                self.previewsContainer.itemAt(i).widget().setParent(None)
            self.previewsContainer.setParent(None)

    def __initLayout(self):
        """
        Constructs the main layout of the window. Should only be called once
        during its lifetime.
        """
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.buttonsContainer = QHBoxLayout()

        self.generatorSelection = QComboBox()
        # Add the name of every selectable generator to the dropdown menu
        for generator in self.GENERATORS:
            self.generatorSelection.addItem(generator[0])
        self.generatorSelection.currentIndexChanged.connect(
            self.__selectGenerator
        )
        self.generatorSelection.setCurrentIndex(self.selectedGeneratorId)
        self.buttonsContainer.addWidget(self.generatorSelection)

        self.optionsButton = QPushButton('Open Options Menu')
        self.optionsButton.setVisible(False)
        self.buttonsContainer.addWidget(self.optionsButton)

        self.generateButton = QPushButton('Start Generation')
        self.generateButton.clicked.connect(self.__generate)
        self.buttonsContainer.addWidget(self.generateButton)

        self.stopButton = QPushButton('Stop Generation')
        self.stopButton.clicked.connect(self.__stop)
        self.stopButton.setEnabled(False)
        self.buttonsContainer.addWidget(self.stopButton)

        self.layout.addLayout(self.buttonsContainer)

        self.outputLabel = QLabel()
        self.outputLabel.setWordWrap(True)
        self.outputLabel.setText('')
        self.outputLabel.setText("OUTPUT")
        self.layout.addWidget(self.outputLabel)

    def __initPreviews(self):
        """
        Initializes the image preview containers.
        Should be called at the start of every generation.
        """
        self.previews = []
        self.previewsContainer = QGridLayout()
        for i in range(
                self.GENERATORS[self.selectedGeneratorId][1].IMAGE_COUNT):
            boxLeft = QGroupBox()
            boxLeftLayout = QVBoxLayout()
            boxLeft.setLayout(boxLeftLayout)

            boxRight = QGroupBox()
            boxRightLayout = QVBoxLayout()
            boxRight.setLayout(boxRightLayout)

            # This way the heading is only on the leftmost image
            # However, we still need to reserve space for the heading label
            # for all other images
            if i == 0:
                boxLeft.setTitle('Generated')
                boxRight.setTitle('Detected')
            else:
                boxLeft.setTitle('')
                boxRight.setTitle('')

            generatedImageLabel = QLabel(boxLeft)
            generatedImageLabel.setScaledContents(True)
            generatedImageLabel.setFixedSize(160, 160)
            generatedImageLabel.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
            boxLeftLayout.addWidget(generatedImageLabel)

            detectedImageLabel = QLabel(boxRight)
            detectedImageLabel.setScaledContents(True)
            detectedImageLabel.setFixedSize(160, 160)
            detectedImageLabel.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
            boxRightLayout.addWidget(detectedImageLabel)

            classnameLabel = QLabel()
            classnameLabel.setText('')

            confidenceLabel = QLabel()
            confidenceLabel.setText('')

            saveButton = QPushButton('Save Image')

            # the image index needs to be passed to the click handler
            # function of the save button.
            # this has to be done by currying the function call.
            def curryedClickedFunction(_, num=i):
                self.__saveGenerated(num)
            clickedFunction = curryedClickedFunction
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

    def __initGenerator(self):
        """
        Initializes a new generator instance, based on the currently
        selected index.
        """
        self.generator = self.GENERATORS[self.selectedGeneratorId][1]()
        # connect the options button to the newly created generator
        try:
            self.optionsButton.clicked.disconnect()
        except Exception:
            # clicked.disconnect() throws an exception of the button is not
            # connected to anything. this is the case if the window is newly
            # opened.
            pass
        self.optionsButton.clicked.connect(self.generator.openOptionsDialog)

    def __printStatistics(self, apiCalls, startTime, additionalStatistics):
        """
        Print the statistics. This function is called after every step
        callback.
        api calls and start time are automatically formatted.
        additionalStatistics is a preformatted string by the generator.
        """
        stats = '\n'.join([
            'API Calls: %d' % apiCalls,
            'Runtime: %.0fs' % (time.time() - startTime),
        ])
        if len(additionalStatistics) > 0:
            stats += '\n' + additionalStatistics
        self.outputLabel.setText(stats)

    def __onStepCallback(self, classes):
        """
        Called by the generator after every iteration.
        classes is an array of tuples. Each tuple contains the detected
        classname and confidence.
        """
        # force the preview images to be fetched within a thread-lock
        # I encountered a segmentation without this
        with self.__lock:
            previewPixmaps = [
                self.generator.getImage(i) for i in range(len(classes))
            ]
        for i in range(len(classes)):
            classname = classes[i][0]
            shortenedClassname = classname[:20] +\
                '...' if len(classname) > 20 else classname
            confidence = classes[i][1]
            # set the labels of the previews
            self.previews[i].classnameLabel.setText(shortenedClassname)
            self.previews[i].confidenceLabel.setText('%d%%' % (confidence*100))

            # create QImage from the generator's preview image
            # previewPixmaps[i] contains a raw 2D, RGB bytes array
            tempQImage = QImage(
                previewPixmaps[i],
                64,
                64,
                QImage.Format_RGB888
            )
            generatedPixmap = QPixmap.fromImage(tempQImage)
            self.previews[i].generatedImageLabel.setPixmap(generatedPixmap)

            c = self.mainWindow.getDataset().getClassByName(classname)
            self.previews[i].detectedImageLabel.setPixmap(
                QPixmap(c.thumbnailPath)
            )

        self.__printStatistics(
            self.generator.getApiCalls(),
            self.generator.getStartTime(),
            self.generator.getAdditionalStatistics()
        )

    def __onFailureCallback(self):
        """
        Called when the generator fails
        """
        # unimplemented
        pass

    def __onFinishedCallback(self):
        """
        Called when the generator has finished.
        Activates the safe image buttons and enables
        starting another generation.
        """
        self.generateButton.setEnabled(True)
        self.optionsButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        for preview in self.previews:
            preview.saveButton.setEnabled(True)

    def __generate(self):
        """
        Start the generation of an image
        """
        self.generateButton.setEnabled(False)
        self.optionsButton.setEnabled(False)
        for preview in self.previews:
            preview.saveButton.setEnabled(False)

        # currying of the callback functions to pass the "self" parameter
        def stepCallback(*args, **kwargs):
            self.__onStepCallback(*args, **kwargs)

        def finishedCallback(*args, **kwargs):
            self.__onFinishedCallback(*args, **kwargs)

        def failureCallback(*args, **kwargs):
            self.__onFailureCallback(*args, **kwargs)

        self.__selectGenerator(self.selectedGeneratorId)
        self.generator.setCallbacks(
            stepCallback,
            finishedCallback,
            failureCallback
        )
        self.generator.setTargetClasses(self.targetClasses)
        self.generator.start()
        self.stopButton.setEnabled(True)

    def __stop(self):
        """
        Stop the generation.
        """
        self.generator.stop()
        self.generator.finish()

    def __saveGenerated(self, i):
        """
        Saves one of the preview images (as given by the index i).
        The filename is determined by a QFileDialog 
        """
        filename = QFileDialog.getSaveFileName(
            self,
            filter='Image Files (*.png *.jpg *.bmp)'
        )[0]
        self.previews[i].generatedImageLabel.pixmap().save(filename)

    def __selectGenerator(self, generatorId):
        """
        Select a generator by its index.
        Instantiates is and prepares the GUI accordingly.
        """
        self.selectedGeneratorId = generatorId
        self.__initGenerator()
        self.__clearPreviews()
        self.__initPreviews()
        self.optionsButton.setVisible(self.generator.PROVIDES_OPTIONS)
