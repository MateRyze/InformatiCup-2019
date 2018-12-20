import requests
import os
import skimage
import random
import json
import webbrowser
import time
from PIL import Image, ImageDraw

global population
global api_calls
global stop
global MUTATION_RATE
population = []
api_calls = 0
stop = False
MUTATION_RATE = 10
SHAPE_MUTATION_RATE = 4
SHAPE_POINTS_COUNT = (5,10)
SHAPE_COUNT = 2

# defined constraints/aspects for the generation 
COLORS_RANGE = ((0,150), (0,150), (0, 150))
CONTRAST_RANGE = (100, 300)
FRAME_SHAPE = [[(16, 16), (48, 16), (48, 48), (16, 48)],
          [(16, 16), (48, 16), (16, 48), (48, 48)]]

colors = []

def randomCoord():
    return (random.randrange(0, 64),random.randrange(0, 64))

# initial random generation of an image
def generateImage():
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    # how many colors do we need?
    generateColorsWithContrast(2)
    # init shape
    shape = []
    pointCount = random.randrange(SHAPE_POINTS_COUNT[0], SHAPE_POINTS_COUNT[1])
    for i in range(pointCount): 
        #idx = random.randrange(0, len(shape))
        shape.insert(i,(random.randrange(0, 64),random.randrange(0, 64)))
        shape = list(map(lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape))
    drawShapes(draw, colors, shape)

    return {"image": img, "confidence": 0, "colors": colors, "class": "", "shape": shape}

def drawShapes(draw, colors, shape):
    background = colors[0]
    draw.rectangle(((0, 0), (64, 64)), background)
    foreground = colors[1]
    draw.polygon(shape, foreground)

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
        if(individual["class"] == ""):
            name = 'toEval.png'
            image = individual["image"]
            image.save(name)
            while(True):
                payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
                r = requests.post('https://phinau.de/trasi', data=payload, files={'image': open(name, 'rb')})
                api_calls += 1
                # if(api_calls >= 60):
                #     time.sleep(60)
                #     api_calls = 0
                # time.sleep(1)
                try:
                    individual["confidence"] = r.json()[0]["confidence"]
                    individual["class"] = str(r.json()[0]["class"])
                    break
                except ValueError:
                    time.sleep(1)
                    # print("Decoding JSON failed -> hit API rate :(")
                    # stop = True
                    
        
        
# create initial population
def initPopulation(count):
    for i in range(count):
        population.append(generateImage())

# select best individuals from population
def selection(bestCount):
    global population
    # sort by confidence
    population.sort(key=lambda individual: individual["confidence"], reverse=True)
    # take best individuals from same classes  
    classesContained = []
    selectedPopulation = []
    for individual in population:
        if(classesContained.count(individual["class"]) < 1):
            selectedPopulation.append(individual)
            classesContained.append(individual["class"])
    population = selectedPopulation
    # reduce individuals -> reduce API calls
    del population[bestCount*2:]

# crossover between individuals in the population
def crossover():
    # use only for same classes from inital population
    img = None
    population_size = len(population)
    for i in range(population_size):
        print("do crossover")

        

def mutateCoord(oldCoord):
    return min(63, max(1, oldCoord + random.randint(-SHAPE_MUTATION_RATE, SHAPE_MUTATION_RATE)))

# mutate each individual in the population and delete old population
def mutate(confidence):
    population_size = len(population)
    for i in range(population_size):
        if(population[i]["confidence"] < 0.9):
            img = Image.new('RGB', (64, 64), color='black')
            draw = ImageDraw.Draw(img)
            # mutate colors
            colors = population[i]["colors"]
            colors = list(map(lambda color: (color[0] + random.randint(-MUTATION_RATE, MUTATION_RATE), color[1] + random.randint(-MUTATION_RATE, MUTATION_RATE), color[2] + random.randint(-MUTATION_RATE, MUTATION_RATE)), colors))
            #mutate shape
            shape = population[i]["shape"]
            if random.random() < 0.5:
                idx = random.randrange(0, len(shape))
                if len(shape) > SHAPE_POINTS_COUNT and random.random() < 0.5:
                    del shape[idx]
                else:
                    shape.insert(idx,randomCoord())
            shape = list(map(lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape))
            
            drawShapes(draw, colors, shape)
            population.append({"image": img, "confidence": 0,
                            "colors": colors, "class": "", "shape": shape})
            """ # distribute the contrast between the colors
            while(contrast(colors[0], colors[1]) < CONTRAST_RANGE[0] or contrast(colors[0], colors[1]) > CONTRAST_RANGE[1]):
                    colors = (
                        random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                        random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                        random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1])) """

            # TODO: add fancy stuff for creativity
    #del population[:population_size]

    

        

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
INITIAL_POPULATION = 60 # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.9 # specification

def addRandomImage():
    population.append(generateImage())

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)
def runEvoAlgorithm():
    global population
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    matchCount = getCountThatMatch(DESIRED_CONFIDENCE)
    while matchCount < SELECTED_COUNT and stop == False:
        # crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness()
        selection(SELECTED_COUNT)
        if (stop == False):
            printResults()
        newMatchCount = getCountThatMatch(DESIRED_CONFIDENCE)
        if newMatchCount == matchCount:
            addRandomImage()
        matchCount = newMatchCount

# save generated images with desired confidence
def saveImages():
    directory = "generated_api_calls_" + str(api_calls)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in range(len(population)):
        image = population[i]["image"]
        name = str(directory) + "/" + "img" + \
            str(i) + "_" + str(population[i]["confidence"]
                                ) + "_" + str(population[i]["class"].encode('utf-8')) + ".png"
        image.save(name)
        webbrowser.open(name)

def evalInitialPopulation():
    global population
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    saveImages()

if __name__ == '__main__':
    runEvoAlgorithm()
    saveImages()
    #evalInitialPopulation()
    print("api calls: ", api_calls)
