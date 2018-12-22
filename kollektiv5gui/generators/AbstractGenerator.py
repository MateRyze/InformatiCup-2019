import time
from multiprocessing import Process
from threading import Thread
from kollektiv5gui.util import api

#class AbstractGenerator(Process):
class AbstractGenerator(Thread):

    IMAGE_COUNT = 1

    def __init__(self):
        super().__init__()
        self.__finished = False
        self.__stopped = False
        self.onStep = None
        self.onFinished = None
        self.onFailure = None

        self.__startTime = 0
        self.__endTime = 0
        self.__apiCalls = 0

    def setCallbacks(self, onStep, onFinished, onFailure):
        self.onStep = onStep
        self.onFinished = onFinished
        self.onFailure = onFailure

    def start(self):
        super().start()
        self.__startTime = time.time()

    def stop(self):
        self.__endTime = time.time()
        self.__stopped = True

    def finish(self):
        self.__finished = True
        self.onFinished()

    def hasFinished(self):
        return self.__finished

    def _countApiCall(self):
        self.__apiCalls += 1

    def getImage(self):
        return None

    def getStartTime(self):
        return self.__startTime

    def getTotalRuntime(self):
        return self.__endTime - self.__startTime

    def getApiCalls(self):
        return self.__apiCalls

    def run(self):
        self.__stopped = False
        while not self.__stopped and not self.__finished:
            self.step()

    def step(self):
        pass
