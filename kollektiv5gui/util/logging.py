def default_logger(x):
    print(x)


__logging_function = default_logger


def setLoggingFunction(func):
    global __logging_function
    __logging_function = func


def log(text):
    if type(text) is not str:
        text = str(text)
    __logging_function(text)
