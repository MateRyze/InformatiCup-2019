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
from kollektiv5gui.util import config


class EAGenerator(AbstractGenerator):

    IMAGE_COUNT = 5
    PROVIDES_OPTIONS = True

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
        self.colorsRange = ((0, 150), (0, 150), (0, 150))
        self.contrastRange = (25, 400)
        # 5 is minimum, because shapes with 3 and 4 points looks like road signs
        self.MINIMUM_SHAPE_POINTS_COUNT = 5
        self.shapePolygonCount = 2
        self.shapePolygonPointCount = 5

        # init parameters
        self.initialPopulationSize = 10  # EXPERIMENT
        self.targetPopulationSize = 5  # specification
        self.targetConfidence = 0.9  # specification

        # init options dialog
        # this loads the pre-defined values into the ui
        self.initOptionsDialog()
        # __setOptions() applies the values from the (invisible) ui
        self.__setOptions()

    # create options dialog from widget
    def initOptionsDialog(self):
        self.optionsWidget = QWidget()
        self.ui = Ui_Options()
        self.ui.setupUi(self.optionsWidget)
        self.ui.newPresetButton.clicked.connect(self.__openSavePresetDialog)
        self.ui.removePresetButton.clicked.connect(self.__removePreset)
        self.ui.setOptionsButton.clicked.connect(self.__setOptions)
        self.ui.presetComboBox.currentIndexChanged.connect(self.__selectPreset)
        presets = [name.strip() for name in config.get(
            "EAGenerator", "presets").split(",")]
        selectedPreset = config.get("EAGenerator", "preset")
        for preset in zip(presets, range(len(presets))):
            self.ui.presetComboBox.addItem(preset[0])
            if preset[0] == selectedPreset:
                self.ui.presetComboBox.setCurrentIndex(preset[1])

    def openOptionsDialog(self):
        self.optionsWidget.show()

    # open dialog for setting preset name
    def __openSavePresetDialog(self):
        alert = QDialog(self.optionsWidget)
        alert.setWindowTitle("Save Preset")
        nameField = QLineEdit()
        nameField.setFixedSize(150, 25)
        nameField.setPlaceholderText("Enter preset name")
        button = QPushButton()
        button.setText("Save")
        button.clicked.connect(lambda: self.__savePreset(alert, nameField))
        layout = QGridLayout()
        layout.addWidget(nameField, 0, 0)
        layout.addWidget(button)
        alert.setLayout(layout)
        alert.exec_()

    def __savePreset(self, alert, nameField):
        preset = nameField.text()
        presetsList = config.get("EAGenerator", "presets")
        presets = [name.strip() for name in presetsList.split(",")]
        if preset not in presets:
            # append preset's name to the comma separated list
            presetsList += "," + preset
            config.set("EAGenerator", "presets", presetsList)
            config.flush()
            # reflect changes in ui
            self.ui.presetComboBox.addItem(preset)
            self.ui.presetComboBox.setCurrentIndex(
                self.ui.presetComboBox.count() - 1)
        self.__savePresetFromUi(preset)
        alert.close()

    def __removePreset(self):
        preset = self.ui.presetComboBox.currentText()
        section = "EAGenerator_Preset:" + preset
        presets = [name.strip() for name in config.get(
            "EAGenerator", "presets").split(",")]
        if preset in presets and len(presets) > 1:
            delIndex = presets.index(preset)
            del presets[delIndex]
            config.set("EAGenerator", "presets", ",".join(presets))
            # either select previous preset or the first one
            newIndex = max(0, delIndex - 1)
            config.set("EAGenerator", "preset", presets[newIndex])
            config.removeSection(section)
            config.flush()
            # reflect changes in ui
            self.ui.presetComboBox.removeItem(
                self.ui.presetComboBox.currentIndex())
            self.ui.presetComboBox.setCurrentIndex(newIndex)

    def __selectPreset(self):
        preset = self.ui.presetComboBox.currentText()
        try:
            self.__loadPresetIntoUi(preset)
        except Exception:
            # fallback: if the currently selected preset has no values in the configuration file:
            # store the default values from the gui
            self.__savePresetFromUi(preset)
        config.set("EAGenerator", "preset", preset)
        config.flush()

    def __savePresetFromUi(self, preset):
        section = "EAGenerator_Preset:" + preset

        config.set(section, "colorMutationRate",
                   self.ui.colorMutationRateSpinBox.value())

        config.set(section, "colorsRangeFromR",
                   self.ui.colorsFromRSpinBox.value())
        config.set(section, "colorsRangeToR", self.ui.colorsToRSpinBox.value())
        config.set(section, "colorsRangeFromG",
                   self.ui.colorsFromGSpinBox.value())
        config.set(section, "colorsRangeToG", self.ui.colorsToGSpinBox.value())
        config.set(section, "colorsRangeFromB",
                   self.ui.colorsFromBSpinBox.value())
        config.set(section, "colorsRangeToB", self.ui.colorsToBSpinBox.value())

        config.set(section, "contrastRangeFrom",
                   self.ui.contrastFromSpinBox.value())
        config.set(section, "contrastRangeTo",
                   self.ui.contrastToSpinBox.value())

        config.set(section, "shapeMutationRate",
                   self.ui.shapeMutationRateSpinBox.value())
        config.set(section, "shapePolygonCount",
                   self.ui.shapePolygonCountSpinBox.value())
        config.set(section, "shapePolygonPointCount",
                   self.ui.shapePolygonPointCountSpinBox.value())
        config.set(section, "initialPopulationSize",
                   self.ui.initialPopulationSizeSpinBox.value())
        config.set(section, "targetConfidence",
                   self.ui.targetConfidenceSpinBox.value())
        config.set(section, "targetPopulationSize",
                   self.ui.targetPopulationSizeSpinBox.value())

        config.flush()

    def __loadPresetIntoUi(self, preset):
        section = "EAGenerator_Preset:" + preset

        self.ui.colorMutationRateSpinBox.setValue(
            config.get(section, "colorMutationRate", int))

        self.ui.colorsFromRSpinBox.setValue(
            config.get(section, "colorsRangeFromR", int))
        self.ui.colorsToRSpinBox.setValue(
            config.get(section, "colorsRangeToR", int))
        self.ui.colorsFromGSpinBox.setValue(
            config.get(section, "colorsRangeFromG", int))
        self.ui.colorsToGSpinBox.setValue(
            config.get(section, "colorsRangeToG", int))
        self.ui.colorsFromBSpinBox.setValue(
            config.get(section, "colorsRangeFromB", int))
        self.ui.colorsToBSpinBox.setValue(
            config.get(section, "colorsRangeToB", int))

        self.ui.contrastFromSpinBox.setValue(
            config.get(section, "contrastRangeFrom", int))
        self.ui.contrastToSpinBox.setValue(
            config.get(section, "contrastRangeTo", int))

        self.ui.shapeMutationRateSpinBox.setValue(
            config.get(section, "shapeMutationRate", int))
        self.ui.shapePolygonCountSpinBox.setValue(
            config.get(section, "shapePolygonCount", int))
        self.ui.shapePolygonPointCountSpinBox.setValue(
            config.get(section, "shapePolygonPointCount", int))
        self.ui.initialPopulationSizeSpinBox.setValue(
            config.get(section, "initialPopulationSize", int))
        self.ui.targetConfidenceSpinBox.setValue(
            config.get(section, "targetConfidence", int))
        self.ui.targetPopulationSizeSpinBox.setValue(
            config.get(section, "targetPopulationSize", int))

    # apply values from ui to the generator algorithm
    def __setOptions(self):
        self.colorMutationRate = self.ui.colorMutationRateSpinBox.value()
        self.colorsRange = (
            (self.ui.colorsFromRSpinBox.value(), self.ui.colorsToRSpinBox.value()),
            (self.ui.colorsFromGSpinBox.value(), self.ui.colorsToGSpinBox.value()),
            (self.ui.colorsFromBSpinBox.value(), self.ui.colorsToBSpinBox.value()),
        )
        self.contrastRange = (
            self.ui.contrastFromSpinBox.value(), self.ui.contrastToSpinBox.value())
        self.shapeMutationRate = self.ui.shapeMutationRateSpinBox.value()
        self.shapePolygonCount = self.ui.shapePolygonCountSpinBox.value()
        self.shapePolygonPointCount = self.ui.shapePolygonPointCountSpinBox.value()
        self.initialPopulationSize = self.ui.initialPopulationSizeSpinBox.value()
        # division by 100, because the target confidence is given in percent in the gui
        self.targetConfidence = self.ui.targetConfidenceSpinBox.value() / 100
        self.targetPopulationSize = self.ui.targetPopulationSizeSpinBox.value()
        self.optionsWidget.close()
        # save the current values into the configuration file
        preset = self.ui.presetComboBox.currentText()
        self.__savePresetFromUi(preset)

    def randomCoord(self):
        return (random.randrange(0, 64), random.randrange(0, 64))

    # initial random generation of an image
    def generateImage(self):
        # set image format
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        # how many colors do we need?
        colors = self.generateColorsWithContrast(2)
        # init shape
        shapes = []
        pointCount = self.shapePolygonPointCount
        shape = []
        for i in range(pointCount):
            shape.insert(i, (self.randomCoord()))
        shapes.append(shape)
        self.drawShapes(draw, colors, shapes)

        return {
            "image": img,
            "confidence": 0,
            "colors": colors,
            "class": "",
            "shapes": shapes,
            "lastCrossover": False
        }

    def drawShapes(self, draw, colors, shapes):
        background = colors[0]
        draw.rectangle(((0, 0), (64, 64)), background)
        # all other colors are for the shapes (polygons)
        for color, shape in zip(colors[1:], shapes):
            draw.polygon(shape, color)

    def contrast(self, color1, color2):
        return (
            abs(color1[0] - color2[0]) +
            abs(color1[1] - color2[1]) +
            abs(color1[2] - color2[2])
        )

    # generate colors with distributed contrast

    def generateColorsWithContrast(self, count):
        colors = []
        for i in range(count):
            color = (
                random.randint(self.colorsRange[0][0], self.colorsRange[0][1]),
                random.randint(self.colorsRange[1][0], self.colorsRange[1][1]),
                random.randint(self.colorsRange[2][0], self.colorsRange[2][1]))
            if(i > 0):
                # distribute the contrast between the colors
                while(
                    self.contrast(color, colors[i-1]) < self.contrastRange[0]/(count-1) or
                    self.contrast(
                        color, colors[i-1]) > self.contrastRange[1]/(count-1)
                ):
                    color = (
                        random.randint(
                            self.colorsRange[0][0], self.colorsRange[0][1]),
                        random.randint(
                            self.colorsRange[1][0], self.colorsRange[1][1]),
                        random.randint(self.colorsRange[2][0], self.colorsRange[2][1]))
            colors.append(color)
        return colors

    # eval fitness for each individual
    def evalFitness(self):
        for individual in self.population:
            if(
                individual["class"] == "" and
                self.getCountThatMatch(self.targetConfidence) < self.targetPopulationSize
            ):
                name = 'toEval.png'
                image = individual["image"]
                image.save(name)
                r = api.classifyPILImage(image)
                self._countApiCall()
                confidence = 0
                if len(self._targetClasses) == 0:
                    # no specific target class is specified
                    # use the one with the highest confidence (already sorted by API)
                    individual["class"] = str(r[0]["class"])
                    confidence = r[0]["confidence"]
                else:
                    for c in r:
                        if c["class"] in self._targetClasses:
                            individual["class"] = c["class"]
                            confidence = c["confidence"]
                            break
                            # break as soon as a matching class is found
                            # confidences are sorted by the api, so we've selected the highest possible confidence here
                    individual["class"] = self._targetClasses[random.randrange(
                        0, len(self._targetClasses))]
                individual["confidence"] = confidence
            else:
                self.callOnStepCallback()
                self.finish()
                return
        self.callOnStepCallback()

    # create initial population
    def initPopulation(self, count):
        self.population = []
        for i in range(count):
            self.population.append(self.generateImage())

    # select best individuals from population
    def selection(self, bestCount, sameClassCount):
        print("doing selection")
        # sort by confidence
        self.population.sort(
            key=lambda individual: individual["confidence"],
            reverse=True
        )
        classesContained = []
        selectedPopulation = []
        for individual in self.population:
            # limit count of individuals with same class
            if(classesContained.count(individual["class"]) < sameClassCount):
                # do not take individuals with confidence > 90 %
                if(not any(
                    selectedIndividual["confidence"] >= 0.9 and
                    selectedIndividual["class"] == individual["class"]
                    for selectedIndividual in selectedPopulation
                )):
                    selectedPopulation.append(individual)
                classesContained.append(individual["class"])
        self.population = selectedPopulation
        # reduce individuals -> reduce API calls
        if sameClassCount is 2:
            # del population[int(INITIAL_POPULATION/2):]
            print("no individuals deleted from selection")
        elif sameClassCount is 1:
            del self.population[bestCount:]

    def mutateCoord(self, oldCoord):
        return min(63, max(1, oldCoord + random.randint(-self.shapeMutationRate, self.shapeMutationRate)))

    # mutate each individual in the population and delete old population
    def mutate(self, confidence):
        print("doing mutation of crossover images")
        population_size = len(self.population)
        for i in range(population_size):
            # use only for confidence < 90% and crossovered individuals
            if(
                self.population[i]["confidence"] < 0.9 and
                self.population[i]["lastCrossover"] is True
            ):
                img = Image.new('RGB', (64, 64), color='black')
                draw = ImageDraw.Draw(img)
                # mutate colors
                colors = self.population[i]["colors"]
                colors = list(
                    map(lambda color: (
                        color[0] + random.randint(-self.colorMutationRate,
                                                  self.colorMutationRate),
                        color[1] + random.randint(-self.colorMutationRate,
                                                  self.colorMutationRate),
                        color[2] + random.randint(-self.colorMutationRate,
                                                  self.colorMutationRate)
                    ), colors)
                )
                # mutate shapes
                shapes = self.population[i]["shapes"]
                newShapes = []
                for shape in shapes:
                    # add or delete point
                    if random.random() < 0.5:
                        idx = random.randrange(0, len(shape))
                        if (
                            len(shape) > self.shapePolygonPointCount and
                            random.random() < 0.5
                        ):
                            del shape[idx]
                        else:
                            shape.insert(idx, self.randomCoord())
                    # mutate point
                    shape = list(
                        map(
                            lambda x: (self.mutateCoord(
                                x[0]), self.mutateCoord(x[1])), shape
                        )
                    )
                    newShapes.append(shape)
                self.drawShapes(draw, colors, newShapes)
                self.population[i] = {
                    "image": img,
                    "confidence": 0,
                    "colors": colors,
                    "class": "",
                    "shapes": newShapes,
                    "lastCrossover": False
                }
                self.__totalMutationCount += 1

    # crossover between individuals in the population
    def crossover(self):
        print("doing crossover")
        # use only for same classes from inital population
        # sort duplicates with same classes like [vorfahrt99%, vorfahrt97%, ...]
        seen = []  # helper list
        duplicates = []
        # append one individual from every class
        for individual in self.population:
            if individual["class"] not in seen:
                duplicates.append([individual])
                seen.append(individual["class"])
        # print(duplicates)
        # append other individuals from same class
        for index, entry in enumerate(duplicates):
            for individual in self.population:
                if (
                    individual not in entry and
                    individual["class"] == entry[0]["class"]
                ):
                    duplicates[index] = duplicates[index] + [individual]
        # filter duplicates for crossover by confidence and length
        # crossover makes sense for at least two individuals and confidence < 90%
        duplicates = [
            entry for entry in duplicates
            if len(entry) > 1 and entry[0]["confidence"] < 0.90
        ]
        # print(duplicates)
        beforeCrossover = duplicates  # for testing function
        afterCrossover = []
        newImagesAppended = 0
        # crossover by adding polygons points
        for entry in duplicates:
            # remove every other point
            # shape = shape[1::2]
            image = Image.new('RGB', (64, 64))
            draw = ImageDraw.Draw(image)
            shapes = entry[0]["shapes"] + entry[1]["shapes"]
            colors = entry[0]["colors"] + entry[1]["colors"][1:]
            self.drawShapes(draw, colors, shapes)
            newIndividual = {
                "image": image,
                "confidence": 0,
                "colors": colors,
                "class": "",
                "shapes": shapes,
                "lastCrossover": True
            }
            afterCrossover.append(newIndividual)
            self.population.append(newIndividual)
            # add second crossover child
            image = Image.new('RGB', (64, 64))
            draw = ImageDraw.Draw(image)
            shapes = entry[1]["shapes"] + entry[0]["shapes"]
            colors = entry[1]["colors"] + entry[0]["colors"][1:]
            self.drawShapes(draw, colors, shapes)
            newIndividual = {
                "image": image,
                "confidence": 0,
                "colors": colors,
                "class": "",
                "shapes": shapes,
                "lastCrossover": True
            }
            afterCrossover.append(newIndividual)
            self.population.append(newIndividual)

            newImagesAppended += 2
            # remove parents
            # population.remove(entry[0])
            # population.remove(entry[1])

        print("crossover, appended images: " + str(newImagesAppended))

        # for testing crossover method
        return {"before": beforeCrossover, "after": afterCrossover}

    # get the count of images that match the confidence
    def getCountThatMatch(self, confidence):
        count = 0
        seen = []
        for individual in self.population:
            if(
                individual["confidence"] >= confidence and
                individual["class"] not in seen
            ):
                seen.append(individual["class"])
                count += 1
        return count

    def addRandomImage(self):
        self.population.append(self.generateImage())

    def getBestIndividials(self, amount):
        return list(reversed(sorted(self.population, key=lambda individual: individual["confidence"])))[:amount]

    def getAdditionalStatistics(self):
        return '\n'.join([
            'Individuals: %d' % len(self.population),
            'Generations: %d' % self.__currentGeneration,
            'Mutations: %d' % self.__totalMutationCount,
        ])

    def getImage(self, i):
        best = self.getBestIndividials(self.targetPopulationSize)
        return best[i]["image"].tobytes('raw', 'RGB')

    def callOnStepCallback(self):
        best = self.getBestIndividials(self.targetPopulationSize)
        self.onStep([(b['class'], b['confidence']) for b in best])

    def step(self):
        if not self.initialized:
            self.initPopulation(self.initialPopulationSize)
            self.evalFitness()
            self.selection(self.targetPopulationSize, 2)
            self.matchCount = self.getCountThatMatch(self.targetConfidence)
            self.initialized = True

        self.crossover()
        self.mutate(self.targetConfidence)
        self.evalFitness()
        self.__currentGeneration += 1
        self.selection(self.targetPopulationSize, 2)

        newMatchCount = self.getCountThatMatch(self.targetConfidence)
        if newMatchCount == self.matchCount:
            self.addRandomImage()
        self.matchCount = newMatchCount

        if self.matchCount > self.targetPopulationSize:
            self.finish()
