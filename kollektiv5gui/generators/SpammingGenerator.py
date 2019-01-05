"""
This approach draws random shapes onto a black surface.
After every drawing step, the picture is sent to the API and classified.
Once the API returns a high enough confidence value,
the image is saved under the prediced class's name.
The method will pretty much always find an answer,
though the amount of API calls required varies a lot.
"""

import requests
import os
import tempfile
import math
import time
import random
import copy
import json
import io
from PIL import Image, ImageDraw
from kollektiv5gui.util import api, logging
from kollektiv5gui.generators.AbstractGenerator import AbstractGenerator


class SpammingGenerator(AbstractGenerator):
    # Some shapes may be based on masks as given by image files on disk.
    shapes = {
    }
    # Drawing text is also supported.
    # The text will be randomly selected from this list:
    texts = [
        'ROFL',
        'LOL',
        'xD',
        'BUTT',
        ':D',
    ]

    def __init__(self):
        super().__init__()
        self.image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        for i in range(random.randrange(1, 5)):
            self.createRandomShape()

    def getRandomColor(self):
        return (
            random.randint(0, 256),
            random.randint(0, 256),
            random.randint(0, 256),
        )

    def getRandomPosition(self, topX=0, topY=0):
        return (
            random.randint(0 + topX, 64 + topY),
            random.randint(0 + topX, 64 + topY),
        )

    def getRandom2DPosition(self):
        return [
            self.getRandomPosition(),
            self.getRandomPosition(),
        ]

    def createRectangle(self):
        self.draw.rectangle(
            self.getRandom2DPosition(), fill=self.getRandomColor()
        )

    def createEllipse(self):
        self.draw.ellipse(
            self.getRandom2DPosition(), fill=self.getRandomColor()
        )

    def createShape(self, shape):
        self.draw.bitmap(
            self.getRandomPosition(-16, -16),
            self.shapes[shape],
            fill=self.getRandomColor(),
        )

    def createText(self):
        text = self.texts[random.randrange(0, len(self.texts))]
        self.draw.text(
            self.getRandomPosition(-16, -16),
            text,
            fill=self.getRandomColor(),
        )

    def createRandomShape(self):
        """
        Draws a random shape onto the image.
        """
        drawFunc = random.random()
        if drawFunc < 0.4:
            self.createRectangle()
        elif drawFunc < 0.8:
            self.createEllipse()
        else:
            self.createText()

    def getImage(self, i):
        return self.image.tobytes('raw', 'RGB')

    def step(self):
        self.createRandomShape()
        classification = api.classifyPILImage(self.image)
        self._countApiCall()

        classId = ''
        confidence = 0

        if len(self._targetClasses) == 0:
            # no specific target class is specified
            # use the one with the highest confidence (already sorted by API)
            classId = str(classification[0]["class"])
            confidence = classification[0]["confidence"]
        else:
            for c in classification:
                if c["class"] in self._targetClasses:
                    classId = c["class"]
                    confidence = c["confidence"]
                    break
                    # break as soon as a matching class is found
                    # confidences are sorted by the api,
                    # so we've selected the highest possible confidence here
            classId = self._targetClasses[
                random.randrange(0, len(self._targetClasses))
            ]

        logging.log(confidence)
        if confidence > 0.9:
            self.finish()
        self.onStep([(classId, confidence)])
