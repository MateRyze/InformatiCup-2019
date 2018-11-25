import matplotlib.pyplot as plt
import requests
import os
import skimage
import random
import json
import webbrowser
import pandas as pd
import numpy as np
import time
from PIL import Image, ImageDraw
from ast import literal_eval as make_tuple

global population
global api_calls
global stop
global MUTATION_RATE
population = []
lastEvaluatedPopulation = []
api_calls = 0
stop = False
MUTATION_RATE = 10

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
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle(position, fill=color)
        colors.append(color)

    return {"image": img, "confidence": 0, "colors": colors, "class": ""}

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
        population.append(generateImageOneRect())

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
        population.append({"image": img, "confidence": 0, "colors": colors, "class": ""})


# mutate each individual in the population and delete old population
def mutate(confidence):
    # mutate colors of random rectangle
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
                colors[rect][0] + 1 + random.randint(-10, 10) * MUTATION_RATE,
                colors[rect][1] + 1 + random.randint(-10, 10) * MUTATION_RATE,
                colors[rect][2] + 1 + random.randint(-10, 10) * MUTATION_RATE)

        for i in range(4):
            draw.rectangle(positions[i], fill=colors[i])
        population.append({"image": img, "confidence": 0, "colors": colors, "class": ""})
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
INITIAL_POPULATION = 5 # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.20 # specification

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)
def runEvoAlgorithm():
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT and stop == False and api_calls < 50:
        #crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness()
        selection(SELECTED_COUNT)
        if (stop == False):
            printResults()    



# save generated images with desired confidence
def saveImages():
    for i in range(len(population)):
        if(population[i]["confidence"] > 0.05):
            image = population[i]["image"]
            name = "img" + \
                str(i) + "_" + str(population[i]["confidence"]
                                    ) + "_" + str(population[i]["class"]) + ".png"
            image.save(name)
            webbrowser.open(name)



# make request with 1000 single color images and save results to CSV file
def getApiResultsForSingleColors():
    # set image format
    color = (0, 0, 0)
    img = Image.new('RGB', (64, 64), color=color)
    
    for i in range(10):
        for j in range(10):
            for k in range(10):
                color = (i*25, j*25, k*25)
                img = Image.new('RGB', (64, 64), color=color)
                individual = {"image": img, "confidence": 0, "color": color, "class": ""}
                # eval
                name = 'toEval.png'
                image = img
                image.save(name)
                payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
                r = requests.post('https://phinau.de/trasi', data=payload, files={'image': open(name, 'rb')})
                time.sleep(1)
                try:
                    individual["confidence"] = r.json()[0]["confidence"]
                    individual["class"] = r.json()[0]["class"]
                    population.append(individual)
                    df = pd.DataFrame(population, columns=["class", "confidence", "color"])
                    print(df)
                    df.to_csv("results_uni_color.csv")
                except ValueError:
                    print("Decoding JSON failed -> hit API rate :(")
                    stop = True
                    break

# varying marker colors (= generated image colors)
def scatterPlot():
    df = pd.read_csv("results_uni_color.csv")
    print(df)
    colors = [make_tuple(row) for row in df["color"]]
    colors = [[elem/255 for elem in row] for row in colors]
    colorsSummed = [(row[0] + row[1] + row[2])*255 for row in colors]
    print(colors)
    plt.scatter(df["confidence"], colorsSummed, c=colors, s=2000, marker=[(1,3), (0,3), (0,0), (1,0)])
    plt.title('Einfarbige Bilder, 1000 Stück')
    plt.xlabel('Konfidenz')
    plt.ylabel('Summe der Farbwerte (R + G + B)')
    plt.show()


if __name__ == '__main__':
    #generateAndEval()
    #runEvoAlgorithm()
    #saveImages()
    #print("api calls: ", api_calls)
    scatterPlot()
