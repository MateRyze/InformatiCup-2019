import json
from collections import namedtuple

DatasetClass = namedtuple('DatasetClass', 'id name thumbnailPath')

class Dataset():
    def __init__(self):
        self.__classes = []

    def getClasses(self):
        return self.__classes

    def getClassesCount(self):
        return len(self.__classes)

    def getClassByName(self, name):
        return list(filter(lambda x: x.name == name, self.__classes))[0]

    def getClassById(self, id):
        return list(filter(lambda x: x.id == id, self.__classes))[0]

    def loadFromFile(self, filename):
        """
        Open a json formatted dataset specification from a file and display the contained information.
        """
        with open(filename, 'r') as fo:
            dataset = json.load(fo)
            # the amount of rows in the table needs to be set first, thus we use the length of the 'classes' array
            for classdef in dataset['classes']:
                self.__classes.append(DatasetClass(
                    id=classdef['classId'],
                    name=classdef['name'],
                    thumbnailPath=classdef['thumbnail']
                ))
