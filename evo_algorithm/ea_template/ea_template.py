import requests
import os
import random
import json
import webbrowser
import math
import copy
from PIL import Image, ImageDraw

global population
global api_calls
global stop
global MUTATION_RATE
population = []
api_calls = 0
stop = False
MUTATION_RATE = 10

class Polygon():
    """
    This class represents a single polygon, which can be colored, moved about and resized.
    It is initialised with a random amount of edges forming a circle, a fixed color and a random position.
    Each mutation causes the polygon to move randomly about, modify its color, be resized and move its individual 
    edges. New edges may also be added and existing edges may be removed.
    """

    def __init__(self):
        self.edges = []
        self.scale = 1.0
        self.position = (0, 0)
        self.color = (128, 128, 128)
        edgesCount = random.randint(3, 8)
        for i in range(edgesCount):
            step = (i / edgesCount) * math.pi * 2
            edge = (math.cos(step), math.sin(step))
            self.edges.append(edge)
        self.color = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
        self.scale = 8.0
        self.position = (
            random.randint(0, 64),
            random.randint(0, 64),
        )

    def __moveEdge(self):
        """
        Moves a random edge into a random direction.
        """
        i = random.randint(0, len(self.edges) - 1)
        self.edges[i] = (
            self.edges[i][0] + random.random() * 0.2 - 0.1,
            self.edges[i][1] + random.random() * 0.2 - 0.1,
        )

    def __insertEdge(self):
        """
        Insert a new edge between to randomly selected existing ones. Its position will be fully arbitrary.
        """
        edge = (random.randrange(-1.0, 1.0), random.randrange(-1.0, 1.0))
        self.edges.insert(random.randint(0, len(self.edges) + 1), edge)

    def __removeEdge(self):
        """
        Remove a random edge of the polygon.
        """
        if len(self.edges) > 3:
            del self.edges[random.randint(0, len(self.edges) - 1)]

    def getScaledEdges(self):
        """
        Returns a list of edges, which were transformed from the polygon's internal space, to the world space.
        I.e.: The position and scale values are applied.
        """
        scaledEdges = []
        for edge in self.edges:
            scaledEdge = (edge[0] * self.scale + self.position[0], edge[1] * self.scale + self.position[1])
            scaledEdges.append(scaledEdge)
        return scaledEdges

    def mutate(self, factor = 1.0):
        """
        Mutate the polygon.
        """
        changeEdges = random.random()
        if changeEdges > 0.9:
            if random.random() > 0.5:
                self.__insertEdge()
            else:
                self.__removeEdge()
        for i in range(random.randint(0, len(self.edges))):
            self.__moveEdge()
        self.color = (
            self.color[0] + random.randint(-1, 1),
            self.color[1] + random.randint(-1, 1),
            self.color[2] + random.randint(-1, 1),
        )
        self.position = (
            self.position[0] + random.randint(-1, 1),
            self.position[1] + random.randint(-1, 1),
        )
        self.scale += random.random() * 2 - 1

    def render(self, draw):
        """
        Render the polygon onto the PIL surface given in "draw".
        """
        draw.polygon(self.getScaledEdges(), fill=self.color)

class PolygonField():
    """
    A polygon field represents a collection of polygons. It is initialised with random polygons.
    Each mutation, the individual polygons and the background color will be mutated. Polygons may also be added
    or removed.
    """

    def __init__(self, polygons = None, background = None):
        if polygons == None:
            self.polygons = []
            for i in range(random.randint(10, 20)):
                self.polygons.append(Polygon())
        else:
            self.polygons = polygons

        if background == None:
            self.background = (0, 0, 0)
            self.background = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
        else:
            self.background = background

    def __insertPolygon(self):
        polygon = Polygon()
        self.polygons.insert(random.randint(0, len(self.polygons) + 1), polygon)

    def __removePolygon(self):
        if len(self.polygons) > 3:
            del self.polygons[random.randint(0, len(self.polygons) - 1)]

    def mutate(self, factor = 1.0):
        # have a higher chance of inserting a polygon
        # the API net REALLY seems to like multiple polygons in an image
        if random.random() > 0.75:
            self.__removePolygon()
        else:
            self.__insertPolygon()
        for polygon in self.polygons:
            polygon.mutate(factor)
        self.background = (
            self.background[0] + random.randint(-1, 1),
            self.background[1] + random.randint(-1, 1),
            self.background[2] + random.randint(-1, 1),
        )

    def render(self):
        img = Image.new('RGB', (64, 64), color=self.background)
        draw = ImageDraw.Draw(img)
        for polygon in self.polygons:
            polygon.render(draw)
        return img

    @staticmethod
    def crossover(a, b):
        newPoly = copy.deepcopy(a.polygons) + copy.deepcopy(b.polygons)
        random.shuffle(newPoly)
        del newPoly[:len(newPoly)//2]
        return PolygonField(newPoly)

# initial random generation of an image
def generateField():
    field = PolygonField()
    return {"field": field, "confidence": 0}

 # eval fitness for each individual
def evalFitness():
    global api_calls
    global stop
    for individual in population:
        name = 'toEval.png'
        image = individual["field"].render()
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
        population.append(generateField())

# select best individuals from population
def selection(bestCount):
    population.sort(key=lambda individual: individual["confidence"], reverse=True)
    del population[bestCount:]

# crossover between individuals in the population
def crossover():
    # IMPLEMENT HERE YOUR CROSSOVER FUNCTION
    # EXAMPLE: cross rectangles, generate new images
    for i in range(len(population)-1):
        a = population[i + 0]["field"]
        b = population[i + 1]["field"]
        c = PolygonField.crossover(a, b)
        population.append({"field": c, "confidence": 0})

# mutate each individual in the population and delete old population
def mutate(confidence):
    population_size = len(population)
    for i in range(population_size):
        newField = copy.deepcopy(population[i]["field"])
        newField.mutate()
        population.append({"field": newField, "confidence": 0})
    #DELETE OR NOT?
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
            image = population[i]["field"].render()
            name = "img" + \
                str(i) + "_" + str(population[i]["confidence"]
                                    ) + "_" + str(population[i]["class"]) + ".png"
            image.save(name)
            webbrowser.open(name)

if __name__ == '__main__':
    runEvoAlgorithm()
    saveImages()
    print("api calls: ", api_calls)
