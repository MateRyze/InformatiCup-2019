import configparser

__DEFAULT_FILENAME = './config.ini'
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
        load_config(__DEFAULT_FILENAME)
    return __CONFIG.get(section, option)
