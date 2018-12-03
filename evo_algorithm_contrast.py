import requests
import os
import skimage
import random
import json
import webbrowser
import time
import itertools
import pandas as pd
from PIL import Image, ImageDraw

global population
global api_calls
global stop
global MUTATION_RATE
shape = ((16, 16), (48,16), (16,48), (48,48))
population = []
api_calls = 0
stop = False
MUTATION_RATE = 10


def contrast(color1, color2):
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])


def generateImage(foreground, background):
    # set image format
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)

    #background fill
    draw.rectangle(((0,0),(64,64)), background)
    #draw shape
    draw.polygon(shape, foreground)
    
    return {"image": img, "confidence": 0, "background": background, "foreground": foreground, "class": "", "contrast": contrast(foreground, background)}


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
        if api_calls >= 60:
            #print(individual["foreground"])
            time.sleep(60)
            api_calls = 0
        try:
            individual["confidence"] = r.json()[0]["confidence"]
            individual["class"] = r.json()[0]["class"].encode('utf-8')
        except ValueError:
            print("Decoding JSON failed -> hit API rate :(")
            stop = True
            break
        
        
# create initial population
def initPopulation(count):
    for i in range(count):
        population.append(generateImage())

#create population of contrast combinations
def initConstrastPopulation():
    seq = [ 28 * i for i in range(10)]
    for (r, g, b) in itertools.product(seq, seq, seq):
        population.append(generateImage( (r, g, b), (255 - r, 255 - g, 255 - b) ))
        
# select best individuals from population
def selection(bestCount):
    population.sort(key=lambda individual: individual["confidence"], reverse=True)
    del population[bestCount:]

# crossover between individuals in the population
def crossover():
    # IMPLEMENT HERE YOUR CROSSOVER FUNCTION
    # EXAMPLE: cross rectangles, generate new images
    for j in range(len(population)-1):
        background = population[0 + j]["background"]
        foreground = population[1 + j]["foreground"]
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        
        draw.rectangle(((0,0),(64,64)), background)
        
        draw.polygon(shape, foreground)
    
        population.append({"image": img, "confidence": 0, "background": background, "foreground": foreground, "class": ""})

# mutate each individual in the population and delete old population
def mutate(confidence):
    # IMPLEMENT HERE YOUR MUTATION FUNCTION
    # EXAMPLE: mutate colors of random rectangle
    population_size = len(population)
    for j in range(len(population)):
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        background = population[j]["background"]
        foreground = population[j]["foreground"]
        if(population[j]["confidence"] < confidence):
            
            background = (
                background[0] + random.randint(-10, 10) * MUTATION_RATE,
                background[1] + random.randint(-10, 10) * MUTATION_RATE,
                background[2] + random.randint(-10, 10) * MUTATION_RATE)
            foreground = (
                foreground[0] + random.randint(-10, 10) * MUTATION_RATE,
                foreground[1] + random.randint(-10, 10) * MUTATION_RATE,
                foreground[2] + random.randint(-10, 10) * MUTATION_RATE)
        
        draw.rectangle(((0,0),(64,64)), background)
        draw.polygon(shape, foreground)
        
        population.append({"image": img, "confidence": 0, "background": background, "foreground": foreground, "class": ""})
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
DESIRED_CONFIDENCE = 0.50 # specification

# run evolutionary algorithm (init -> selection -> loop(crossover-> mutate -> selection) until confidence matches all images)
def runEvoAlgorithm():
    initPopulation(INITIAL_POPULATION)
    evalFitness()
    selection(SELECTED_COUNT)
    printResults()
    while getCountThatMatch(DESIRED_CONFIDENCE) < SELECTED_COUNT and stop == False:
        crossover()
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
            name = (str(shape) + ';' + str(population[i]["confidence"]) + ';' + str(population[i]["background"])
                    + ';' + str(population[i]["foreground"]) + ';' + population[i]["class"]).encode('utf-8')
            image.save(name + ".png")
            webbrowser.open(name + ".png")


def saveResults():
    df = pd.DataFrame(population, columns=["class", "confidence", "background", "foreground", "contrast"])
    print(df)
    df.to_csv("results_contrast_color.csv")

if __name__ == '__main__':
    initConstrastPopulation()
    evalFitness()
    saveResults()
    print("api calls: ", api_calls)
    
