import requests
import os
import random
import json
import webbrowser
import time

from PIL import Image, ImageDraw
from kollektiv5gui.util import api
from kollektiv5gui.generators.AbstractGenerator import AbstractGenerator
from PyQt5.QtWidgets import QMessageBox, QColorDialog, QLineEdit, QWidget, QDialog, QLabel, QGroupBox, QPushButton, QSizePolicy, QFileDialog, QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout
from kollektiv5gui.views.EaOptionsWidget import Ui_Options

class EAGenerator(AbstractGenerator):

    IMAGE_COUNT = 5

    def __init__(self):
        super().__init__()
        self.population = []
        self.colors = []
        self.initialized = False
        self.__currentGeneration = 0
        self.__totalMutationCount = 0
        # defined constraints/aspects for the generation
        self.colorMutationRate = 10
        self.shapeMutationRate = 4
        self.colors_range = ((0, 150), (0, 150), (0, 150))
        self.contrast_range = (25, 400)

        # init parameters
        self.initialPopulationSize = 5  # EXPERIMENT
        self.targetPopulationSize = 5  # specification
        self.targetConfidence = 0.9  # specification
    
    def openOptionsDialog(self):
        self.optionsWidget = QWidget()
        self.ui = Ui_Options()
        self.ui.setupUi(self.optionsWidget)
        self.optionsWidget.show()
        self.ui.newPresetButton.clicked.connect(self.__openSavePresetDialog)
        self.ui.setOptionsButton.clicked.connect(self.__setOptions)
        self.ui.presetComboBox.currentIndexChanged.connect(self.__selectPreset)

    def __openSavePresetDialog(self):
        alert = QDialog()
        alert.setWindowTitle("Save Preset")
        nameField = QLineEdit()
        nameField.setFixedSize(150, 25)
        nameField.setPlaceholderText("Enter preset name")
        button = QPushButton()
        button.setText("Save")
        button.clicked.connect(self.__savePreset)
        layout = QGridLayout()
        layout.addWidget(nameField, 0,0)
        layout.addWidget(button)
        alert.setLayout(layout)
        alert.exec_()
    
    def __savePreset(self):
        # TODO save preset
        print("TODO: save")

    def __selectPreset(self):
        # TODO: load preset
        print(self.ui.presetComboBox.currentText())

    def __setOptions(self):
        self.colorMutationRate = self.ui.colorMutationRateSpinBox.value()
        self.colorsRange = (
            (self.ui.colorsFromRSpinBox.value(), self.ui.colorsToRSpinBox.value()),
            (self.ui.colorsFromGSpinBox.value(), self.ui.colorsToGSpinBox.value()),
            (self.ui.colorsFromBSpinBox.value(), self.ui.colorsToBSpinBox.value()),
        )
        self.contrastRange = (self.ui.contrastFromSpinBox.value(), self.ui.contrastToSpinBox.value())
        self.shapeMutationRate = self.ui.shapeMutationRateSpinBox.value()
        self.shapePolygonCount = self.ui.colorMutationRateSpinBox.value()
        self.shapePolygonPointCount = self.ui.colorMutationRateSpinBox.value()
        self.initialPopulationSize = self.ui.initialPopulationSizeSpinBox.value()
        self.targetConfidence = self.ui.targetConfidenceSpinBox.value()
        self.targetPopulationSize = self.ui.targetPopulationSizeSpinBox.value()

    def randomCoord(self):
        return (random.randrange(0, 64),random.randrange(0, 64))

    # initial random generation of an image
    def generateImage(self):
        # set image format
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        # how many colors do we need?
        self.generateColorsWithContrast(2)
        shape = [self.randomCoord(), self.randomCoord(), self.randomCoord(), self.randomCoord()]
        self.drawShapes(draw, self.colors, shape)

        return {"image": img, "confidence": 0, "colors": self.colors, "class": "", "shape": shape}

    def drawShapes(self, draw, colors, shape):
        background = colors[0]
        draw.rectangle(((0, 0), (64, 64)), background)
        foreground = colors[1]
        draw.polygon(shape, foreground)

    def contrast(self, color1, color2):
        return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])

    # generate colors with distributed contrast
    def generateColorsWithContrast(self, count):
        self.colors = []
        for i in range(count):
            color = (
                random.randint(self.colors_range[0][0], self.colors_range[0][1]),
                random.randint(self.colors_range[1][0], self.colors_range[1][1]),
                random.randint(self.colors_range[2][0], self.colors_range[2][1]))
            if(i > 0):
                # distribute the contrast between the colors 
                while(self.contrast(color, self.colors[i-1]) < self.contrast_range[0]/(count-1) or self.contrast(color, self.colors[i-1]) > self.contrast_range[1]/(count-1)):
                    color = (
                        random.randint(self.colors_range[0][0], self.colors_range[0][1]),
                        random.randint(self.colors_range[1][0], self.colors_range[1][1]),
                        random.randint(self.colors_range[2][0], self.colors_range[2][1]))
            self.colors.append(color)

    # eval fitness for each individual
    def evalFitness(self):
        for individual in self.population:
            if(individual["class"] == ""):
                name = 'toEval.png'
                image = individual["image"]
                image.save(name)
                r = api.classifyPILImage(image)
                self._countApiCall()
                individual["confidence"] = r[0]["confidence"]
                individual["class"] = str(r[0]["class"])
        self.callOnStepCallback()

    # create initial population
    def initPopulation(self, count):
        for i in range(count):
            self.population.append(self.generateImage())

    # select best individuals from population
    def selection(self, bestCount):
        # sort by confidence
        self.population.sort(key=lambda individual: individual["confidence"], reverse=True)
        # take best individuals from same classes
        classesContained = []
        selectedPopulation = []
        for individual in self.population:
            if(classesContained.count(individual["class"]) < 1):
                selectedPopulation.append(individual)
                classesContained.append(individual["class"])
        self.population = selectedPopulation
        # reduce individuals -> reduce API calls
        del self.population[bestCount*2:]

    def mutateCoord(self, oldCoord):
        return min(63, max(1, oldCoord + random.randint(-self.shapeMutationRate, self.shapeMutationRate)))

    # mutate each individual in the population and delete old population
    def mutate(self, confidence):
        # IMPLEMENT HERE YOUR MUTATION FUNCTION
        population_size = len(self.population)
        for i in range(population_size):
            if(self.population[i]["confidence"] < 0.9):
                img = Image.new('RGB', (64, 64), color='black')
                draw = ImageDraw.Draw(img)
                # mutate colors
                colors = self.population[i]["colors"]
                colors = list(
                    map(
                        lambda color: (
                            color[0] + random.randint(-self.colorMutationRate, self.colorMutationRate),
                            color[1] + random.randint(-self.colorMutationRate, self.colorMutationRate),
                            color[2] + random.randint(-self.colorMutationRate, self.colorMutationRate),
                        ),
                    colors)
                )
                #mutate shape
                shape = self.population[i]["shape"]
                if random.random() < 0.5:
                    idx = random.randrange(0, len(shape))
                    if len(shape) > 3 and random.random() < 0.5:
                        del shape[idx]
                    else:
                        shape.insert(idx,self.randomCoord())
                shape = list(map(lambda x: (self.mutateCoord(x[0]), self.mutateCoord(x[1])), shape))

                self.drawShapes(draw, colors, shape)
                self.population.append({"image": img, "confidence": 0,
                                "colors": colors, "class": "", "shape": shape})
                self.__totalMutationCount += 1

    # get the count of images that match the confidence
    def getCountThatMatch(self, confidence):
        count = 0
        for individual in self.population:
            if(individual["confidence"] >= confidence):
                count += 1
        return count

    def addRandomImage(self):
        self.population.append(self.generateImage())

    def getBestIndividials(self, amount):
        return list(reversed(sorted(self.population, key=lambda individual: individual["confidence"])))[:amount]

    def getAdditionalStatistics(self):
        return '\n'.join([
            'Individuals: %d'%len(self.population),
            'Generations: %d'%self.__currentGeneration,
            'Mutations: %d'%self.__totalMutationCount,
        ])

    def getImage(self, i):
        best = self.getBestIndividials(self.IMAGE_COUNT)
        return best[i]["image"].tobytes('raw', 'RGB')

    def callOnStepCallback(self):
        best = self.getBestIndividials(self.IMAGE_COUNT)
        self.onStep([(b['class'], b['confidence']) for b in best])

    def step(self):
        if not self.initialized:
            self.initPopulation(self.initialPopulationSize)
            self.evalFitness()
            self.selection(self.targetPopulationSize)
            self.matchCount = self.getCountThatMatch(self.targetConfidence)
            self.initialized = True

        self.mutate(self.targetConfidence)
        self.evalFitness()
        self.__currentGeneration += 1
        self.selection(self.targetPopulationSize)

        newMatchCount = self.getCountThatMatch(self.targetConfidence)
        if newMatchCount == self.matchCount:
            self.addRandomImage()
        self.matchCount = newMatchCount

        if self.matchCount > self.targetPopulationSize:
            self.finish()
