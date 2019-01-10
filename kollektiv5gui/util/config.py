import os
import shutil
import configparser
from kollektiv5gui.util.paths import getResourcePath

__DEFAULT_CONFIG_FILENAME = os.path.join(getResourcePath(), 'default.ini')
__USER_CONFIG_FILENAME = os.path.expanduser('~/.kollektiv5.ini')
__DEFAULT_CONFIG = None
__CONFIG = None


def __loadConfig():
    """
    Load an .ini based config file.
    """
    global __CONFIG, __DEFAULT_CONFIG
    if not os.path.exists(__USER_CONFIG_FILENAME):
        # if the user has no config,
        # copy the default one to the expected location
        shutil.copy(__DEFAULT_CONFIG_FILENAME, __USER_CONFIG_FILENAME)
    __CONFIG = configparser.ConfigParser()
    __CONFIG.read(__USER_CONFIG_FILENAME, encoding='utf8')

    # the default config is also always loaded to try
    # and fall back to its values
    # if sections or keys are missing from the user config
    __DEFAULT_CONFIG = configparser.ConfigParser()
    __DEFAULT_CONFIG.read(__DEFAULT_CONFIG_FILENAME, encoding='utf8')


def get(section, option, type=str):
    """
    Get a value from the config file. If no config was loaded before,
    __DEFAULT_FILENAME is read and stored before the
    value is extracted from it.
    """
    if __CONFIG is None:
        __loadConfig()
    if (not __CONFIG.has_section(section) or
            not __CONFIG.has_option(section, option)):
        # value is not preset in user config,
        # try and return it from the default one
        return type(__DEFAULT_CONFIG.get(section, option))
    return type(__CONFIG.get(section, option))


def set(section, option, value):
    if __CONFIG is None:
        __loadConfig()
    if not __CONFIG.has_section(section):
        __CONFIG.add_section(section)
    __CONFIG.set(section, option, str(value))


def removeSection(section):
    if __CONFIG is None:
        __loadConfig()
    if __CONFIG.has_section(section):
        __CONFIG.remove_section(section)


def flush():
    global __CONFIG
    if __CONFIG is not None:
        with open(__USER_CONFIG_FILENAME, 'w') as configfile:
            __CONFIG.write(configfile)
