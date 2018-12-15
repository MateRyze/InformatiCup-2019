import os
import shutil
import configparser
from kollektiv5gui.util.paths import getResourcePath

__DEFAULT_CONFIG_FILENAME = os.path.join(getResourcePath(), 'default.ini')
__USER_CONFIG_FILENAME = os.path.expanduser('~/.kollektiv5.ini')
__CONFIG = None

def load_config(filename):
    """
    Load an .ini based config file.
    """
    global __CONFIG
    __CONFIG = configparser.ConfigParser()
    __CONFIG.read(filename)

def get(section, option):
    """
    Get a value from the config file. If no config was loaded before, __DEFAULT_FILENAME is read and stored before the
    value is extracted from it.
    """
    if __CONFIG is None:
        if not os.path.exists(__USER_CONFIG_FILENAME):
            # if the user has no config, copy the default one to the expected location
            shutil.copy(__DEFAULT_CONFIG_FILENAME, __USER_CONFIG_FILENAME)
        load_config(__USER_CONFIG_FILENAME)
    return __CONFIG.get(section, option)
