import requests
import os
import tempfile
import math
import time
import skimage
import random
import copy
from PIL import Image, ImageDraw

image = Image.new('RGB', (64, 64), color=(0, 0, 0))
draw = ImageDraw.Draw(image)
tmpDir = tempfile.mkdtemp()

def getFitness():
    name = os.path.join(tmpDir, 'classify.png')
    image.save(name)
    payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
    r = requests.post('https://phinau.de/trasi', data=payload, files={'image': open(name, 'rb')})
    #print(r.json()[0]["confidence"])
    confidence = r.json()[0]["confidence"]
    time.sleep(1)
    return confidence

fitness = 0
while fitness < 0.9:
    color = (
        random.randint(0, 256),
        random.randint(0, 256),
        random.randint(0, 256),
    )
    xy = [
        (random.randint(0, 64), random.randint(0, 64)),
        (random.randint(0, 64), random.randint(0, 64)),
    ]
    draw.rectangle(xy, fill=color)
    fitness = getFitness()
    print(fitness)
image.save('final.png')
