#!/usr/bin/env python3
"""
This approach draws random shapes onto a black surface. After every drawing step, the picture is sent to the API and
classified. Once the API returns a high enough confidence value, the image is saved under the prediced class's name.
The method will pretty much always find an answer, though the amount of API calls required varies a lot.
"""

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

# Some shapes may be based on masks as given by image files on disk.
shapes = {
    'paprika': Image.open(os.path.join('brushes', 'paprika.png')),
}
# Drawing text is also supported. The text will be randomly selected from this list:
texts = [
    'ROFL',
    'LOL',
    'xD',
    'BUTT',
    ':D',
]

image = Image.new('RGB', (64, 64), color=(0, 0, 0))
draw = ImageDraw.Draw(image)
# imageBuffer is used to export the temporary .png files for the API calls. This way, We can keep this file in-memory.
imageBuffer = io.BytesIO()
outDir = os.path.join('.', 'output')
# If rate limiting was detected, the program will sleep for 1 second between each call.
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

def createRandomShape():
    """
    Draws a random shape onto the image.
    """
    drawFunc = random.random()
    if drawFunc < 0.4:
        createRectangle()
    elif drawFunc < 0.8:
        createEllipse()
    else:
        createText()

def step():
    """
    Classify the current image and return the confidence and detected class.
    """
    image.save(imageBuffer, format='png')
    imageBuffer.seek(0)
    payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
    res = requests.post('https://phinau.de/trasi', data=payload, files={'image': imageBuffer})
    imageBuffer.seek(0)
    #print(r.json()[0]['confidence'])
    classification = res.json()[0]
    print(classification)
    return classification

fitness = 0
classname = ''
# Draw some initial shapes onto the image
for i in range(random.randrange(1, 20)):
    createRandomShape()
while fitness < 0.9:
    try:
        result = step()
        # createRandomShape() is called AFTER the step function.
        # If we'd hit the rate limit, we don't want to keep drawing without the API having seen the image.
        # For the first classification,  some shapes will already have been drawn..
        createRandomShape()
        fitness = result['confidence']
        classname = result['class']
    except json.JSONDecodeError:
        # Due to the way the api works, once we don't receive valid JSON anymore, we have hit the rate limit.
        if not rateLimited:
            print('Hit the rate limit')
        rateLimited = True
    if rateLimited:
        time.sleep(1)

# output the final image to disk
if not os.path.exists(outDir):
    os.makedirs(outDir)
image.save(os.path.join(outDir, '%s.png'%classname))
