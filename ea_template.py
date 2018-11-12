import requests
import os
import skimage
import random
from PIL import Image, ImageDraw


population = []

def generateImage():
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    positions = [
        ((0, 0), (32, 32)),
        ((32, 0), (64, 32)),
        ((0, 32), (32, 64)),
        ((32, 32), (64, 64)),
    ]
    colors = []
    for position in positions:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
        draw.rectangle(position, fill=color)
        colors.append(color)
    return {"image": img, "confidence": 0, "colors": colors}

# eval fitness for each individual
def evalFitness():
    for individual in population:
        name = 'toEval.png'
        image = individual["image"]
        image.save(name)
        payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
        r = requests.post('https://phinau.de/trasi', data=payload, files={'image': open(name, 'rb')})
        #print(r.json()[0]["confidence"])
        individual["confidence"] = r.json()[0]["confidence"]

def initPopulation(count):
    for i in range(count):
        population.append(generateImage())

def selection(bestCount):
    population.sort(key=lambda individual: individual["confidence"], reverse=True)
    del population[bestCount:]

def crossover():
    # cross rectangles, generate new images
    # TODO: fit for more individuals
    for j in range(2):
        colorsFirst = population[0 + j]["colors"]
        colorsSecond = population[1 + j]["colors"]
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        positions = [
            ((0, 0), (32, 32)),
            ((32, 0), (64, 32)),
            ((0, 32), (32, 64)),
            ((32, 32), (64, 64)),
        ]
        colors = [colorsFirst[0], colorsFirst[1], colorsSecond[2], colorsSecond[3]]
        for i in range(4):
            draw.rectangle(positions[i], fill=colors[i])
        population.append({"image": img, "confidence": 0, "colors": colors})

def mutate():
    for j in range(len(population)):
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        positions = [
            ((0, 0), (32, 32)),
            ((32, 0), (64, 32)),
            ((0, 32), (32, 64)),
            ((32, 32), (64, 64)),
        ]
        colors = population[j]["colors"]
        rect = random.randint(0, 3)
        colors[rect] = (colors[rect][0] + 1, colors[rect][1] + 1, colors[rect][2] + 1, 255)
        for i in range(4):
            draw.rectangle(positions[i], fill=colors[i])
        population.append({"image": img, "confidence": 0, "colors": colors})
    #DELETE OR NOT?
    del population[:5]

def printResults():
    for individual in population:
        print(individual["confidence"])
    print("..")

def getBestResult():
    best = 0
    for individual in population:
        if(individual["confidence"] > best):
            best = individual["confidence"]
    return best

def getCountThatMatch(confidence):
    count = 0
    for individual in population:
        if(individual["confidence"] >= confidence):
            count += 1
    return count

INITIAL_POPULATION = 10
SELECTED_COUNT = 5
DESIRED_CONFIDENCE = 0.90

initPopulation(INITIAL_POPULATION)
evalFitness()
selection(SELECTED_COUNT)
printResults()
while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT:
    crossover()
    mutate()
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
for i in range(len(population)):
    image = population[i]["image"]
    image.save("img" + str(i) + ".png")

#TODO: add test functions and calculate API callss


