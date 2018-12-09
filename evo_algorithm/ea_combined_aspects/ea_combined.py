import requests
import os
import skimage
import random
import json
import webbrowser
from PIL import Image, ImageDraw

global population
global api_calls
global stop
global MUTATION_RATE
population = []
api_calls = 0
stop = False
MUTATION_RATE = 10

# defined constraints/aspects for the generation 
COLORS_RANGE = ((0,150), (0,150), (0, 150))
CONTRAST_RANGE = (25, 400)
SHAPES = [((16, 16), (48, 16), (48, 48), (16, 48)),
          ((16, 16), (48, 16), (16, 48), (48, 48))]

colors = []

# initial random generation of an image
def generateImage():
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    # how many colors do we need?
    generateColorsWithContrast(2)
    drawShapes(draw, colors)

    return {"image": img, "confidence": 0, "colors": colors, "class": ""}

def drawShapes(draw, colors):
    background = colors[0]
    draw.rectangle(((0, 0), (64, 64)), background)
    foreground = colors[1]
    draw.polygon(SHAPES[0], foreground)

# generate colors with distributed contrast 
def generateColorsWithContrast(count):
    global colors
    colors = []
    for i in range(count):
        color = (
            random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
            random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
            random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1]))
        if(i > 0):
            # distribute the contrast between the colors 
            while(contrast(color, colors[i-1]) < CONTRAST_RANGE[0]/(count-1) or contrast(color, colors[i-1]) > CONTRAST_RANGE[1]/(count-1)):
                color = (
                    random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                    random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                    random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1]))
        colors.append(color)


def contrast(color1, color2):
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])


# eval fitness for each individual
def evalFitness():
    global api_calls
    global stop
    for individual in population:
        name = 'toEval.png'
        image = individual["image"]
        image.save(name)
        payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
        r = requests.post('https://phinau.de/trasi', data=payload, files={'image': open(name, 'rb')})
        api_calls += 1
        try:
            individual["confidence"] = r.json()[0]["confidence"]
            individual["class"] = r.json()[0]["class"]
        except ValueError:
            print("Decoding JSON failed -> hit API rate :(")
            stop = True
            break
        
        
# create initial population
def initPopulation(count):
    for i in range(count):
        population.append(generateImage())

# select best individuals from population
def selection(bestCount):
    population.sort(key=lambda individual: individual["confidence"], reverse=True)
    del population[bestCount:]

# crossover between individuals in the population
def crossover():
    img = None
    population.append({"image": img, "confidence": 0, "colors": colors, "class": ""})

# mutate each individual in the population and delete old population
def mutate(confidence):
    # IMPLEMENT HERE YOUR MUTATION FUNCTION
    population_size = len(population)
    for i in range(population_size):
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        colors = population[i]["colors"]
        colors = list(map(lambda color: (color[0] + 1, color[1] + 1, color[2] + 1), colors))
        drawShapes(draw, colors)
        population.append({"image": img, "confidence": 0,
                           "colors": colors, "class": ""})
        """ # distribute the contrast between the colors
        while(contrast(colors[0], colors[1]) < CONTRAST_RANGE[0] or contrast(colors[0], colors[1]) > CONTRAST_RANGE[1]):
                colors = (
                    random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                    random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                    random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1])) """
        
    # delete old
    del population[:population_size]

def printResults():
    for individual in population:
        print("confidence: ", individual["confidence"], " class: ", individual["class"])
    print("..")

def getBestResult():
    best = 0
    for individual in population:
        if(individual["confidence"] > best):
            best = individual["confidence"]
    return best
# get the count of images that match the confidence
def getCountThatMatch(confidence):
    count = 0
    for individual in population:
        if(individual["confidence"] >= confidence):
            count += 1
    return count


# init parameters
INITIAL_POPULATION = 10 # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.90 # specification

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)
def runEvoAlgorithm():
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT and stop == False:
        # crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness()
        selection(SELECTED_COUNT)
        if (stop == False):
            printResults()

# save generated images with desired confidence
def saveImages():
    for i in range(len(population)):
        if(population[i]["confidence"] > DESIRED_CONFIDENCE):
            image = population[i]["image"]
            name = "img" + \
                str(i) + "_" + str(population[i]["confidence"]
                                    ) + "_" + str(population[i]["class"]) + ".png"
            image.save(name)
            webbrowser.open(name)

def evalInitialPopulation():
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    printResults()

if __name__ == '__main__':
    runEvoAlgorithm()
    #saveImages()
    #evalInitialPopulation()
    print("api calls: ", api_calls)
