import requests
import os
import skimage
import random
import json
import webbrowser
import time
import sys
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
SHAPE_POINTS_COUNT = (5, 10)
SHAPE_COUNT = 2

# defined constraints/aspects for the generation
COLORS_RANGE = ((0, 150), (0, 150), (0, 150))
CONTRAST_RANGE = (100, 300)
FRAME_SHAPE = [[(16, 16), (48, 16), (48, 48), (16, 48)],
               [(16, 16), (48, 16), (16, 48), (48, 48)]]

colors = []


def randomCoord():
    return (random.randrange(0, 64), random.randrange(0, 64))

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
        shape.insert(i, (randomCoord()))
        shape = list(
            map(lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape))
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
def evalFitness(population):
    global api_calls
    global stop
    print("doing api calls (evaluation)")
    for individual in population:
        if(individual["class"] == ""):
            name = 'toEval.png'
            image = individual["image"]
            image.save(name)
            while(True):
                try:
                    payload = {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
                    r = requests.post('https://phinau.de/trasi',
                                      data=payload, files={'image': open(name, 'rb')})
                    api_calls += 1
                    individual["confidence"] = r.json()[0]["confidence"]
                    individual["class"] = str(r.json()[0]["class"])
                    break
                except ValueError:
                    time.sleep(1)
                    # print("Decoding JSON failed -> hit API rate :(")
                    # stop = True
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    print("Retrying...")
                    time.sleep(1)
    print("api calls: " + str(api_calls))
    return population


# create initial population
def initPopulation(count):
    print("generating initial population")
    global population
    population = []
    for i in range(count):
        population.append(generateImage())


# select best individuals from population
def selection(bestCount, sameClassCount):
    print("doing selection")
    global population
    # sort by confidence
    population.sort(
        key=lambda individual: individual["confidence"],
        reverse=True
    )
    # take best individuals from same classes
    classesContained = []
    selectedPopulation = []
    for individual in population:
        if(classesContained.count(individual["class"]) < sameClassCount):
            if(not any(
                selectedIndividual["confidence"] >= 0.9 and
                selectedIndividual["class"] == individual["class"] for selectedIndividual in selectedPopulation
            )):
                selectedPopulation.append(individual)
            classesContained.append(individual["class"])
    population = selectedPopulation
    # reduce individuals -> reduce API calls
    if sameClassCount is 2:
        del population[int(INITIAL_POPULATION/2):]
        # print("no individuals deleted from selection")
    elif sameClassCount is 1:
        del population[bestCount:]


# crossover between individuals in the population
def crossover():
    print("doing crossover")
    # use only for same classes from inital population
    # sort duplicates with same classes like [vorfahrt99%, vorfahrt97%, ...]
    seen = []
    duplicates = []
    for indi in population:
        if indi["class"] not in seen:
            duplicates.append([indi])
            seen.append(indi["class"])
    # print(duplicates)
    for index, entry in enumerate(duplicates):
        for individual in population:
            if (
                individual not in entry and
                individual["class"] == entry[0]["class"]
            ):
                duplicates[index] = duplicates[index] + [individual]
    duplicates = [entry for entry in duplicates if len(
        entry) > 1 and entry[0]["confidence"] < 0.90]
    # print(duplicates)
    beforeCrossover = duplicates
    afterCrossover = []
    newImagesAppended = 0
    # crossover by adding polygons points
    for entry in duplicates:
        # add polygons
        shape = entry[0]["shape"] + entry[1]["shape"]
        # remove every other point
        # shape = shape[1::2]
        image = Image.new('RGB', (64, 64))
        draw = ImageDraw.Draw(image)
        drawShapes(draw, entry[0]["colors"], entry[0]["shape"])
        draw.polygon(entry[1]["shape"], entry[1]["colors"][1])
        # image.show()
        afterCrossover.append(
            {
                "image": image,
                "confidence": 0,
                "colors": entry[0]["colors"],
                "class": "",
                "shape": shape
            }
        )
        population.append(
            {
                "image": image,
                "confidence": 0,
                "colors": entry[0]["colors"],
                "colors2": entry[1]["colors"],
                "class": "",
                "shape": entry[0]["shape"],
                "shape2": entry[1]["shape"]
            }
        )
        # add second crossover child
        image = Image.new('RGB', (64, 64))
        draw = ImageDraw.Draw(image)
        drawShapes(draw, entry[1]["colors"], entry[1]["shape"])
        draw.polygon(entry[0]["shape"], entry[0]["colors"][1])
        afterCrossover.append(
            {
                "image": image,
                "confidence": 0,
                "colors": entry[1]["colors"],
                "class": "",
                "shape": shape
            }
        )
        population.append(
            {
                "image": image,
                "confidence": 0,
                "colors": entry[1]["colors"],
                "colors2": entry[0]["colors"],
                "class": "",
                "shape": entry[1]["shape"],
                "shape2": entry[0]["shape"]
            }
        )
        newImagesAppended += 2
    print("crossover, appended images: " + str(newImagesAppended))
    # for testing crossover method
    return {"before": beforeCrossover, "after": afterCrossover}


def mutateCoord(oldCoord):
    return min(
        63,
        max(
            1,
            oldCoord +
            random.randint(-SHAPE_MUTATION_RATE, SHAPE_MUTATION_RATE)
        )
    )


# mutate each individual in the population and delete old population
def mutate(confidence):
    print("doing mutation")
    population_size = len(population)
    newImagesAppended = 0
    for i in range(population_size):
        if(population[i]["confidence"] < 0.9):
            img = Image.new('RGB', (64, 64), color='black')
            draw = ImageDraw.Draw(img)
            # mutate colors
            colors = population[i]["colors"]
            colors = list(map(lambda color: (color[0] + random.randint(-MUTATION_RATE, MUTATION_RATE), color[1] + random.randint(
                -MUTATION_RATE, MUTATION_RATE), color[2] + random.randint(-MUTATION_RATE, MUTATION_RATE)), colors))
            # mutate shape
            shape = population[i]["shape"]
            if random.random() < 0.5:
                idx = random.randrange(0, len(shape))
                if len(shape) > SHAPE_POINTS_COUNT[1] and random.random() < 0.5:
                    del shape[idx]
                else:
                    shape.insert(idx, randomCoord())
            shape = list(
                map(lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape))

            drawShapes(draw, colors, shape)
            if("colors2" in population[i].keys()):
                # mutate colors
                colors2 = population[i]["colors2"]
                colors2 = list(map(lambda color: (color[0] + random.randint(-MUTATION_RATE, MUTATION_RATE), color[1] + random.randint(
                    -MUTATION_RATE, MUTATION_RATE), color[2] + random.randint(-MUTATION_RATE, MUTATION_RATE)), colors2))
                # mutate shape
                shape2 = population[i]["shape2"]
                if random.random() < 0.5:
                    idx = random.randrange(0, len(shape2))
                    if len(shape2) > SHAPE_POINTS_COUNT[1] and random.random() < 0.5:
                        del shape2[idx]
                    else:
                        shape2.insert(idx, randomCoord())
                shape2 = list(
                    map(lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape2))

                draw.polygon(shape2, colors2[1])
                population.append({
                    "image": img,
                    "confidence": 0,
                    "colors": colors,
                    "colors2": colors2,
                    "class": "",
                    "shape": shape,
                    "shape2": shape2
                })
            else:
                population.append({
                    "image": img,
                    "confidence": 0,
                    "colors": colors,
                    "class": "",
                    "shape": shape,
                })
            newImagesAppended += 1
            """ # distribute the contrast between the colors
            while(contrast(colors[0], colors[1]) < CONTRAST_RANGE[0] or contrast(colors[0], colors[1]) > CONTRAST_RANGE[1]):
                    colors = (
                        random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                        random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                        random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1])) """

            # TODO: add fancy stuff for creativity
    # del population[:population_size]
    print("mutate, appended images: " + str(newImagesAppended))


def printResults():
    for individual in population:
        print("confidence: ",
              individual["confidence"], " class: ", individual["class"])
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
    seen = []
    for individual in population:
        if(individual["confidence"] >= confidence and individual["class"] not in seen):
            seen.append(individual["class"])
            count += 1
    return count


# init parameters
INITIAL_POPULATION = 30  # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.9  # specification


def addRandomImage():
    population.append(generateImage())
    print("add one new random image (avoid local maxima)")

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)


def runEvoAlgorithm():
    global population
    initPopulation(INITIAL_POPULATION)
    evalFitness(population)
    # saveImages("init")
    selection(SELECTED_COUNT, 2)
    # saveImages("selection")
    printResults()
    # evalFitness(population)
    # saveImages("crossover")
    # selection(SELECTED_COUNT, 1)
    # printResults()
    matchCount = getCountThatMatch(DESIRED_CONFIDENCE)
    while matchCount < SELECTED_COUNT and stop is False:
        crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness(population)
        # saveImages("mutate")
        selection(SELECTED_COUNT, 2)
        if stop is False:
            printResults()
        # avoid local maxima by adding new random image
        newMatchCount = getCountThatMatch(DESIRED_CONFIDENCE)
        if newMatchCount == matchCount:
            addRandomImage()
        matchCount = newMatchCount
    selection(SELECTED_COUNT, 1)  # for test function

# save generated images with desired confidence


def saveImages(type):
    directory = "generated_api_calls_" + str(api_calls)
    # directory = "images_for_visualization"
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in range(len(population)):
        image = population[i]["image"]
        name = str(directory) + "/" + type + \
            str(i) + "_" + str(population[i]["confidence"]
                               ) + "_" + str(population[i]["class"]) + ".png"
        image.save(name)
        # webbrowser.open(name)


def evalInitialPopulation():
    global population
    initPopulation(INITIAL_POPULATION)
    evalFitness(population)
    selection(SELECTED_COUNT)
    printResults()
    saveImages()


if __name__ == '__main__':
    runEvoAlgorithm()
    saveImages("final")
    # evalInitialPopulation()
    print("api calls: ", api_calls)
