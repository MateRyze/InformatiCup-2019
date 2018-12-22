import requests
import os
import skimage
import random
import json
import webbrowser
import time

from PIL import Image, ImageDraw
from kollektiv5gui.util import api
from kollektiv5gui.generators.AbstractGenerator import AbstractGenerator

class EAGenerator(AbstractGenerator):

    IMAGE_COUNT = 5

    # defined constraints/aspects for the generation
    MUTATION_RATE = 10
    SHAPE_MUTATION_RATE = 4
    COLORS_RANGE = ((0,150), (0,150), (0, 150))
    CONTRAST_RANGE = (25, 400)
    SHAPES = [[(16, 16), (48, 16), (48, 48), (16, 48)],
              [(16, 16), (48, 16), (16, 48), (48, 48)]]

    # init parameters
    INITIAL_POPULATION = 5 # EXPERIMENT
    SELECTED_COUNT = 5  # specification
    DESIRED_CONFIDENCE = 0.9 # specification

    def __init__(self):
        super().__init__()
        self.population = []
        self.colors = []
        self.initialized = False

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
                random.randint(self.COLORS_RANGE[0][0], self.COLORS_RANGE[0][1]),
                random.randint(self.COLORS_RANGE[1][0], self.COLORS_RANGE[1][1]),
                random.randint(self.COLORS_RANGE[2][0], self.COLORS_RANGE[2][1]))
            if(i > 0):
                # distribute the contrast between the colors 
                while(self.contrast(color, self.colors[i-1]) < self.CONTRAST_RANGE[0]/(count-1) or self.contrast(color, self.colors[i-1]) > self.CONTRAST_RANGE[1]/(count-1)):
                    color = (
                        random.randint(self.COLORS_RANGE[0][0], self.COLORS_RANGE[0][1]),
                        random.randint(self.COLORS_RANGE[1][0], self.COLORS_RANGE[1][1]),
                        random.randint(self.COLORS_RANGE[2][0], self.COLORS_RANGE[2][1]))
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
        return min(63, max(1, oldCoord + random.randint(-self.SHAPE_MUTATION_RATE, self.SHAPE_MUTATION_RATE)))

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
                            color[0] + random.randint(-self.MUTATION_RATE, self.MUTATION_RATE),
                            color[1] + random.randint(-self.MUTATION_RATE, self.MUTATION_RATE),
                            color[2] + random.randint(-self.MUTATION_RATE, self.MUTATION_RATE),
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

    # get the count of images that match the confidence
    def getCountThatMatch(self, confidence):
        count = 0
        for individual in self.population:
            if(individual["confidence"] >= confidence):
                count += 1
        return count

    def getBestResult(self):
        best = {"confidence": 0}
        for individual in self.population:
            if(individual["confidence"] > best["confidence"]):
                best = individual
        return best

    def addRandomImage(self):
        self.population.append(self.generateImage())

    def getImage(self):
        best = self.getBestResult()
        print(best)
        return best["image"].tobytes('raw', 'RGB')

    def callOnStepCallback(self):
        best = self.getBestResult()
        self.onStep(best["class"], best["confidence"])

    def step(self):
        if not self.initialized:
            self.initPopulation(self.INITIAL_POPULATION)
            self.evalFitness()
            self.selection(self.SELECTED_COUNT)
            self.matchCount = self.getCountThatMatch(self.DESIRED_CONFIDENCE)
            self.initialized = True

        self.mutate(self.DESIRED_CONFIDENCE)
        self.evalFitness()
        self.selection(self.SELECTED_COUNT)

        newMatchCount = self.getCountThatMatch(self.DESIRED_CONFIDENCE)
        if newMatchCount == self.matchCount:
            self.addRandomImage()
        self.matchCount = newMatchCount

        if self.matchCount > self.SELECTED_COUNT:
            self.finish()
