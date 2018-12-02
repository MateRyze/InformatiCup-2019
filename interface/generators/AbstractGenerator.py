from interface.util import api

class AbstractGenerator():
    def __init__(self):
        self.__finished = False

    def hasFinished(self):
        return self.__finished

    def getImage(self):
        return None

    def generate(self, onStep, onFinished, onFailure):
        pass
