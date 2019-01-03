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
SHAPE_POINTS_COUNT = (10, 15)

# defined constraints/aspects for the generation
COLORS_RANGE = ((0, 255), (0, 255), (0, 255))
CONTRAST_RANGE = (100, 765)

# init parameters
INITIAL_POPULATION = 20  # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.9  # specification


def randomCoord():
    return (random.randrange(0, 64), random.randrange(0, 64))


# initial random generation of an image
def generateImage():
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    # how many colors do we need?
    colors = generateColorsWithContrast(2)
    # init shape
    shapes = []
    pointCount = random.randrange(SHAPE_POINTS_COUNT[0], SHAPE_POINTS_COUNT[1])
    shape = []
    for i in range(pointCount):
        shape.insert(i, (randomCoord()))
    shapes.append(shape)
    drawShapes(draw, colors, shapes)

    return {
        "image": img,
        "confidence": 0,
        "colors": colors,
        "class": "",
        "shapes": shapes,
        "lastCrossover": False
    }


def drawShapes(draw, colors, shapes):
    background = colors[0]
    draw.rectangle(((0, 0), (64, 64)), background)
    # all other colors are for the shapes (polygons)
    for color, shape in zip(colors[1:], shapes):
        draw.polygon(shape, color)


# generate colors with distributed contrast
def generateColorsWithContrast(count):
    colors = []
    for i in range(count):
        color = (
            random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
            random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
            random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1]))
        if(i > 0):
            # distribute the contrast between the colors
            while(
                contrast(color, colors[i-1]) < CONTRAST_RANGE[0]/(count-1) or
                contrast(color, colors[i-1]) > CONTRAST_RANGE[1]/(count-1)
            ):
                color = (
                    random.randint(COLORS_RANGE[0][0], COLORS_RANGE[0][1]),
                    random.randint(COLORS_RANGE[1][0], COLORS_RANGE[1][1]),
                    random.randint(COLORS_RANGE[2][0], COLORS_RANGE[2][1]))
        colors.append(color)
    return colors


def contrast(color1, color2):
    return (
        abs(color1[0] - color2[0]) +
        abs(color1[1] - color2[1]) +
        abs(color1[2] - color2[2])
    )


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
                    r = requests.post(
                        'https://phinau.de/trasi',
                        data=payload,
                        files={'image': open(name, 'rb')}
                    )
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
            # TODO: check count that match and break if goal achieved
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
    classesContained = []
    selectedPopulation = []
    for individual in population:
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
    population = selectedPopulation
    # reduce individuals -> reduce API calls
    if sameClassCount is 2:
        # del population[int(INITIAL_POPULATION/2):]
        print("no individuals deleted from selection")
    elif sameClassCount is 1:
        del population[bestCount:]


# crossover between individuals in the population
def crossover():
    print("doing crossover")
    # use only for same classes from inital population
    # sort duplicates with same classes like [vorfahrt99%, vorfahrt97%, ...]
    seen = []  # helper list
    duplicates = []
    # append one individual from every class
    for individual in population:
        if individual["class"] not in seen:
            duplicates.append([individual])
            seen.append(individual["class"])
    # print(duplicates)
    # append other individuals from same class
    for index, entry in enumerate(duplicates):
        for individual in population:
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
        drawShapes(draw, colors, shapes)
        newIndividual = {
            "image": image,
            "confidence": 0,
            "colors": colors,
            "class": "",
            "shapes": shapes,
            "lastCrossover": True
        }
        afterCrossover.append(newIndividual)
        population.append(newIndividual)
        # add second crossover child
        image = Image.new('RGB', (64, 64))
        draw = ImageDraw.Draw(image)
        shapes = entry[1]["shapes"] + entry[0]["shapes"]
        colors = entry[1]["colors"] + entry[0]["colors"][1:]
        drawShapes(draw, colors, shapes)
        newIndividual = {
            "image": image,
            "confidence": 0,
            "colors": colors,
            "class": "",
            "shapes": shapes,
            "lastCrossover": True
        }
        afterCrossover.append(newIndividual)
        population.append(newIndividual)

        newImagesAppended += 2
        # remove parents
        # population.remove(entry[0])
        # population.remove(entry[1])

    print("crossover, appended and deleted images: " + str(newImagesAppended))

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
        # use only for confidence < 90% and crossovered individuals
        if(
            population[i]["confidence"] < 0.9 and
            population[i]["lastCrossover"] is True
        ):
            img = Image.new('RGB', (64, 64), color='black')
            draw = ImageDraw.Draw(img)
            # mutate colors
            colors = population[i]["colors"]
            colors = list(
                map(lambda color: (
                    color[0] + random.randint(-MUTATION_RATE, MUTATION_RATE),
                    color[1] + random.randint(-MUTATION_RATE, MUTATION_RATE),
                    color[2] + random.randint(-MUTATION_RATE, MUTATION_RATE)
                ), colors)
            )
            # mutate shapes
            shapes = population[i]["shapes"]
            newShapes = []
            for shape in shapes:
                # add or delete point
                if random.random() < 0.5:
                    idx = random.randrange(0, len(shape))
                    if (
                        len(shape) > SHAPE_POINTS_COUNT[1] and
                        random.random() < 0.5
                    ):
                        del shape[idx]
                    else:
                        shape.insert(idx, randomCoord())
                # mutate point
                shape = list(
                    map(
                        lambda x: (mutateCoord(x[0]), mutateCoord(x[1])), shape
                    )
                )
                newShapes.append(shape)
            drawShapes(draw, colors, newShapes)
            population[i]["lastCrossover"] = False
            population.append({
                "image": img,
                "confidence": 0,
                "colors": colors,
                "class": "",
                "shapes": newShapes,
                "lastCrossover": False
            })
            newImagesAppended += 1
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
        if(
            individual["confidence"] >= confidence and
            individual["class"] not in seen
        ):
            seen.append(individual["class"])
            count += 1
    return count


def addRandomImage():
    population.append(generateImage())
    print("add one new random image (avoid local maxima)")


# run evolutionary algorithm until confidence matches all images
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
    printResults()


# save generated images
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


# for testing init population
def evalInitialPopulation():
    global population
    initPopulation(INITIAL_POPULATION)
    evalFitness(population)
    selection(SELECTED_COUNT, 1)
    printResults()
    saveImages("init")


if __name__ == '__main__':
    runEvoAlgorithm()
    saveImages("final")
    # evalInitialPopulation()
    print("api calls: ", api_calls)
