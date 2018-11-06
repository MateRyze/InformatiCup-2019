import configparser

__CONFIG = None

def load_config(filename):
    global __CONFIG
    __CONFIG = configparser.ConfigParser()
    __CONFIG.read(filename)

def get(section, option):
    if __CONFIG is None:
        load_config('config.ini')
    return __CONFIG.get(section, option)
