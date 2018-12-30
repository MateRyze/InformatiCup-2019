import os
import shutil
import configparser
from kollektiv5gui.util.paths import getResourcePath

__DEFAULT_CONFIG_FILENAME = os.path.join(getResourcePath(), 'default.ini')
__USER_CONFIG_FILENAME = os.path.expanduser('~/.kollektiv5.ini')
__CONFIG = None

def __loadConfig():
    """
    Load an .ini based config file.
    """
    global __CONFIG
    if not os.path.exists(__USER_CONFIG_FILENAME):
        # if the user has no config, copy the default one to the expected location
        shutil.copy(__DEFAULT_CONFIG_FILENAME, __USER_CONFIG_FILENAME)
    __CONFIG = configparser.ConfigParser()
    __CONFIG.read(__USER_CONFIG_FILENAME)

def get(section, option, type = str):
    """
    Get a value from the config file. If no config was loaded before, __DEFAULT_FILENAME is read and stored before the
    value is extracted from it.
    """
    if __CONFIG is None:
        __loadConfig()
    return type(__CONFIG.get(section, option))

def set(section, option, value):
    if __CONFIG is None:
        __loadConfig()
    if not __CONFIG.has_section(section):
        __CONFIG.add_section(section)
    __CONFIG.set(section, option, str(value))

def flush():
    global __CONFIG
    if __CONFIG is not None:
        with open(__USER_CONFIG_FILENAME, 'w') as configfile:
            __CONFIG.write(configfile)
