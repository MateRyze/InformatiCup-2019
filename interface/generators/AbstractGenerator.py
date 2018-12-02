from threading import Thread
from interface.util import api

class AbstractGenerator(Thread):
    def __init__(self):
        super().__init__()
        self.__finished = False
        self.__stopped = False
        self.onStep = None
        self.onFinished = None
        self.onFailure = None

    def setCallbacks(self, onStep, onFinished, onFailure):
        self.onStep = onStep
        self.onFinished = onFinished
        self.onFailure = onFailure

    def stop(self):
        self.__stopped = True

    def finish(self):
        self.__finished = True
        self.onFinished()

    def hasFinished(self):
        return self.__finished

    def getImage(self):
        return None

    def run(self):
        self.__stopped = False
        while not self.__stopped and not self.__finished:
            self.step()

    def step(self):
        pass
