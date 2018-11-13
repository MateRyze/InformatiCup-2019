import requests
import os
import tempfile
import math
import time
import skimage
import random
import copy
import json
import io
from PIL import Image, ImageDraw

shapes = {
    'paprika': Image.open(os.path.join('brushes', 'paprika.png')),
}
texts = [
    'ROFL',
    'LOL',
    'xD',
    'BUTT',
    ':D',
]

image = Image.new('RGB', (64, 64), color=(0, 0, 0))
imageBuffer = io.BytesIO()
draw = ImageDraw.Draw(image)
outDir = os.path.join('.', 'output')
rateLimited = False

def getRandomColor():
    return (
        random.randint(0, 256),
        random.randint(0, 256),
        random.randint(0, 256),
    )

def getRandomPosition(topX = 0, topY = 0):
    return (random.randint(0 + topX, 64 + topY), random.randint(0 + topX, 64 + topY))

def getRandom2DPosition():
    return [
        getRandomPosition(),
        getRandomPosition(),
    ]

def createRectangle():
    draw.rectangle(getRandom2DPosition(), fill=getRandomColor())

def createEllipse():
    draw.ellipse(getRandom2DPosition(), fill=getRandomColor())

def createShape(shape):
    draw.bitmap(getRandomPosition(-16, -16), shapes[shape], fill=getRandomColor())

def createText():
    text = texts[random.randrange(0, len(texts))]
    draw.text(getRandomPosition(-16, -16), text, fill=getRandomColor())

def step():
    image.save(imageBuffer, format='png')
    imageBuffer.seek(0)
    payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
    res = requests.post('https://phinau.de/trasi', data=payload, files={'image': imageBuffer})
    imageBuffer.seek(0)
    #print(r.json()[0]['confidence'])
    classification = res.json()[0]
    confidence = classification['confidence']
    print((confidence, classification['class']))
    return (confidence, classification['class'])

fitness = 0
classname = ''
while fitness < 0.9:
    drawFunc = random.random()
    if drawFunc < 0.4:
        createRectangle()
    elif drawFunc < 0.8:
        createEllipse()
    else:
        createText()
    try:
        result = step()
        fitness = result[0]
        classname = result[1]
    except json.JSONDecodeError:
        if not rateLimited:
            print('Hit the rate limit')
        rateLimited = True
    if rateLimited:
        time.sleep(1)
if not os.path.exists(outDir):
    os.makedirs(outDir)
image.save(os.path.join(outDir, '%s.png'%classname))
