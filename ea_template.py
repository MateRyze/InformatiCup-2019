import requests
import os
import skimage
import random
import unittest
import json
from PIL import Image, ImageDraw

# initial random generation of an image
def generateImage():
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)

    # draw four rectangles with random colors
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
        except ValueError:
            print("Decoding JSON failed", api_calls)
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
    # cross rectangles, generate new images
    for j in range(len(population)-1):
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

# mutate each individual in the population and delete old population
def mutate(confidence):
    population_size = len(population)
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
        if(population[j]["confidence"] < confidence):
            # change the color of a random square
            rect = random.randint(0, 3)
            colors[rect] = (
                colors[rect][0] + random.randint(-10, 10),
                colors[rect][1] + random.randint(-10, 10),
                colors[rect][2] + random.randint(-10, 10),
                255)

        for i in range(4):
            draw.rectangle(positions[i], fill=colors[i])
        population.append({"image": img, "confidence": 0, "colors": colors})
    # delete old
    del population[:population_size]

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


# init parameters
population = []
global api_calls
stop = False
api_calls = 0
INITIAL_POPULATION = 10
SELECTED_COUNT = 5
DESIRED_CONFIDENCE = 0.90

#TODO: add more test functions
class MyTest(unittest.TestCase):
    def test(self):
        initPopulation(INITIAL_POPULATION)
        self.assertEqual(len(population), INITIAL_POPULATION)

if __name__ == '__main__':
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT and stop == False:
        crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness()
        selection(SELECTED_COUNT)
        printResults()
    for i in range(len(population)):
        image = population[i]["image"]
        image.save("img" + str(i) + ".png")
    print(api_calls)
else:
    unittest.main()






