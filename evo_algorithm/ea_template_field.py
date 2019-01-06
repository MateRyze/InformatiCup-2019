# -*- coding: utf-8 -*-
import requests
import os
import skimage
import random
import json
import webbrowser
import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from PIL import Image, ImageDraw

global population
global api_calls
global stop
global MUTATION_RATE
classList = []
confidenceList = []
confidenzList = []
population = []
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
        ((0, 0), (16, 16)), 
        ((16, 0), (32, 16)), 
        ((0, 16), (16, 32)), 
        ((16, 16), (32, 32)),
        ((0, 32), (16, 48)),
        ((16, 32), (32, 48)),
        ((0, 48), (16, 64)),
        ((16, 48), (32, 64)), 
        ((32,0), (48, 16)),
        ((48, 0), (64, 16)),
        ((32, 16), (48, 32)),
        ((48, 16), (64, 32)),
        ((32, 32), (48, 48)),
        ((48, 32), (64, 48)),
        ((32, 48), (48, 64)),
        ((48, 48), (64, 64)),
    ]
    #positions = generateFields(4)
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
    global classList
    global confidenceList
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
                    classList.append(individual["class"])
                    confidenceList.append(individual["confidence"])
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


        
        
# create initial population
def initPopulation(count):
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
    # IMPLEMENT HERE YOUR CROSSOVER FUNCTION
    # EXAMPLE: cross rectangles, generate new images
    for j in range(len(population)-1):
        colorsFirst = population[0 + j]["colors"]# + population[0 + j]["colors"] + population[0 + j]["colors"] + population[0 + j]["colors"]
        colorsSecond = population[1 + j]["colors"]# + population[1 + j]["colors"] + population[1 + j]["colors"] + population[1 + j]["colors"]
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        
        positions = [
            ((0, 0), (16, 16)), 
            ((16, 0), (32, 16)), 
            ((0, 16), (16, 32)), 
            ((16, 16), (32, 32)),
            ((0, 32), (16, 48)),
            ((16, 32), (32, 48)),
            ((0, 48), (16, 64)),
            ((16, 48), (32, 64)), 
            ((32,0), (48, 16)),
            ((48, 0), (64, 16)),
            ((32, 16), (48, 32)),
            ((48, 16), (64, 32)),
            ((32, 32), (48, 48)),
            ((48, 32), (64, 48)),
            ((32, 48), (48, 64)),
            ((48, 48), (64, 64)),
        ]
        colors = colorsFirst[:8] + colorsSecond[:8]##[colorsFirst[0], colorsFirst[1], colorsSecond[2], colorsSecond[3]]
        for i in range(16):
            draw.rectangle(positions[i], fill=colors[i])
        population.append({"image": img, "confidence": 0, "colors": colors, "class": ""})

# mutate each individual in the population and delete old population
def mutate(confidence):
    # IMPLEMENT HERE YOUR MUTATION FUNCTION
    # EXAMPLE: mutate colors of random rectangle
    population_size = len(population)
    for j in range(len(population)):
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        positions = [
            ((0, 0), (16, 16)), 
            ((16, 0), (32, 16)), 
            ((0, 16), (16, 32)), 
            ((16, 16), (32, 32)),
            ((0, 32), (16, 48)),
            ((16, 32), (32, 48)),
            ((0, 48), (16, 64)),
            ((16, 48), (32, 64)), 
            ((32,0), (48, 16)),
            ((48, 0), (64, 16)),
            ((32, 16), (48, 32)),
            ((48, 16), (64, 32)),
            ((32, 32), (48, 48)),
            ((48, 32), (64, 48)),
            ((32, 48), (48, 64)),
            ((48, 48), (64, 64)),
        ]
        
        colors = population[j]["colors"]# + population[j]["colors"] + population[j]["colors"] + population[j]["colors"] + population[j]["colors"]
        if(population[j]["confidence"] < confidence):
            # change the color of a random square
            rect = random.randint(0, 3)
            colors[rect] = (
                colors[rect][0] + 1 + random.randint(-10, 10) * MUTATION_RATE,
                colors[rect][1] + 1 + random.randint(-10, 10) * MUTATION_RATE,
                colors[rect][2] + 1 + random.randint(-10, 10) * MUTATION_RATE
                )
                

        for i in range(16):
            draw.rectangle(positions[i], fill=colors[i])
            
        population.append({"image": img, "confidence": 0, "colors": colors, "class": ""})
    # delete old
    del population[:population_size]


def generateFields(n):
    positions = [
        ((0, 0), (16, 16)), 
        ((16, 0), (32, 16)), 
        ((0, 16), (16, 32)), 
        ((16, 16), (32, 32)),
        ((0, 32), (16, 48)),
        ((16, 32), (32, 48)),
        ((0, 48), (16, 64)),
        ((16, 48), (32, 64)), 
        ((32,0), (48, 16)),
        ((48, 0), (64, 16)),
        ((32, 16), (48, 32)),
        ((48, 16), (64, 32)),
        ((32, 32), (48, 48)),
        ((48, 32), (64, 48)),
        ((32, 48), (48, 64)),
        ((48, 48), (64, 64)),
    ]
    # beschreibt die Ursprungsform des geteilten Bildes mit vier gleichgroßen Rechtecken
    positions_origin = [
        ((0, 0), (32, 32)),
        ((32, 0), (64, 32)),
        ((0, 32), (32, 64)),
        ((32, 32), (64, 64)),
    ]
    dimension = 16
    #die Ursprungsform wird skaliert, um diese dann als Grundlage für die Generierung weiterer Rechtecke zu benutzen
    position_scaled = [[(point[0]/dimension, point[1]/dimension) for point in row] for row in positions_origin]
    #print(position_scaled)
    positions = []
    #die weiteren Rechtecke werden generiert und in der Variable position als eine Liste mit Listen aus Tupeln gespeichert
    for i in range(dimension):
        for j in range(dimension):
            offset = 64/dimension
            position= [tuple([(point[0] + offset*i, point[1] + offset*j) for point in k]) for k in position_scaled]
            positions.append(position)
    # keine Endlosschleife :D sondern die Konsolenausgabe war sehr gross
    # print(positions)
    return positions

def saveResults():
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    colors = [(255,0,0), (0,255,0), (0,0,255), (0,0,0)]
    
    for i in range(32):
        for fields in generateFields(i+1):
            for j in range(len(fields)):
                draw.rectangle(fields[j], fill=colors[j])

    evalFitness()

        #Antwort in Liste
        #in csv
        # i, anzahl der felder, klasse, konfidenz


def printResults():
    global confidenzList
    for individual in population:
        print("confidence: ", individual["confidence"], " class: ", individual["class"])
        confidenzList.append(individual["confidence"])
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



# init parameters
INITIAL_POPULATION = 20 # EXPERIMENT
SELECTED_COUNT = 5  # specification
DESIRED_CONFIDENCE = 0.90 # specification

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)
def runEvoAlgorithm():
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT, 2)
    printResults()
    while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT and stop == False:
        crossover()
        mutate(DESIRED_CONFIDENCE)
        evalFitness()
        selection(SELECTED_COUNT, 2)
        if (stop == False):
            printResults()
    selection(SELECTED_COUNT, 1)
    printResults()
    print(api_calls)

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
def clearList(listy):
    data = []
    counter = len(listy)
    print(counter)
    for i in range(counter):
        string = listy[i]
        print(string)
        data.append(string.encode("utf-8"))
    return data

def listToCSV():
    new_class = clearList(classList)
    data = zip(confidenceList, new_class)
    df = pd.DataFrame(data)
    df.to_csv('result.csv', index=False)
    print(df)
    plt.title('Einfarbige Bilder')
    plt.xlabel('Konfidenz')
    plt.ylabel('Klassifikation')
    plt.scatter(df[0], df[1])
    plt.show()


if __name__ == '__main__':
    runEvoAlgorithm()
    saveImages()
    print("api calls: ", api_calls)
    # generateFields(4)
    # saveResults()
    # listToCSV()
    
