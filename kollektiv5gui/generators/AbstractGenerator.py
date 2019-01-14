import time
from multiprocessing import Process
from threading import Thread
from kollektiv5gui.util import api, logging


class AbstractGenerator(Thread):
    """
    Base class for image generators
    """

    # How many images are created at once
    IMAGE_COUNT = 1
    # Does this generator provide options?
    PROVIDES_OPTIONS = False

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
        self._targetClasses = []

    def setCallbacks(self, onStep, onFinished, onFailure):
        """
        Called by the generator window, sets the callbacks to
        the correct values.
        """
        self.onStep = onStep
        self.onFinished = onFinished
        self.onFailure = onFailure

    def setTargetClasses(self, targetClasses):
        self._targetClasses = targetClasses

    def start(self):
        super().start()
        self.__startTime = time.time()
        logging.log("Started image generation")

    def stop(self):
        """
        To be called when the generation should be stopped.
        Not to be confused with finish(), which should be called if
        the implementation produced the correct results.s
        Either from inside the algorithm or from external sources.
        """
        self.__endTime = time.time()
        self.__stopped = True

    def finish(self):
        """
        To be called when the algorithm finished successfully.
        """
        self.__finished = True
        self.onFinished()
        logging.log("Finished image generation")

    def hasFinished(self):
        """
        Returns whether the algorithm has finished.
        """
        return self.__finished

    def _countApiCall(self):
        """
        To be called by the implementation whenever an API call should
        be counted.
        """
        self.__apiCalls += 1

    def getImage(self, i):
        """
        Should return one of the currently generated images of the generator
        as a 2D integer array representing the RGB pixels of the image.
        i is the index of the image and is range [0, IMAGE_COUNT)
        """
        return None

    def getStartTime(self):
        """
        When did the generation start?
        """
        return self.__startTime

    def getTotalRuntime(self):
        """
        For how long is the algorithm running?
        """
        return self.__endTime - self.__startTime

    def getApiCalls(self):
        """
        How many API calls has the algorithm used?
        """
        return self.__apiCalls

    def getAdditionalStatistics(self):
        """
        Arbitrary, preformatted statistics the generator may wants to
        display to the user.
        """
        return ''

    def run(self):
        self.__stopped = False
        while not self.__stopped and not self.__finished:
            self.step()

    def step(self):
        """
        This method represents one iteration of the implemented algorithm
        """
        pass

    def openOptionsDialog(self):
        """
        Handler function when the user clicks on the
        "Configure Generator" button in the GUI. The visibility of
        this button is determined by the value of PROVIDES_OPTIONS.
        """
        pass
