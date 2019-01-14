import os

# store the path to the module's root directory
# this assumes that this file resides exactly
# one folder above the module's root
__ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
__RESOURCE_DIR = os.path.join(__ROOT_DIR, 'resources')


def getModuleRoot():
    """
    Returns the path to the module's root directory
    """
    return __ROOT_DIR


def getResourcePath():
    """
    Returns the path to the project's resource directory
    """
    return __RESOURCE_DIR
