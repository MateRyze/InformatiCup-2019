import io
import requests
import json
import random
import time
import threading
from PIL import Image
from kollektiv5gui.util import config, logging

__lock = threading.Lock()


def __sendToApi(data):
    """
    Classify an image using the API.
    data needs to contain the bytes of a png formatted image.
    """
    key = config.get('API', 'key')
    url = config.get('API', 'url')
    success = False
    resJson = None
    printedRateLimitingMessage = False
    with __lock:
        while not success:
            try:
                res = requests.post(
                    url,
                    data={'key': key},
                    files={'image': data}
                )
                resJson = res.json()
                success = True
            except json.decoder.JSONDecodeError:
                if not printedRateLimitingMessage:
                    logging.log('API: Rate limiting detected, retrying...')
                    printedRateLimitingMessage = True
                time.sleep(1)
            except Exception:
                logging.log('API: Unexpected Error, retrying...')
                time.sleep(1)
    return resJson


def classifyFile(path):
    """
    Send an image to the API using its filename.
    """
    return __sendToApi(open(path, 'rb'))


def classifyPILImage(image):
    """
    Send an image to the API, which is represented
    as an instance of the PIL library's Image class.
    """
    buf = io.BytesIO()
    image.save(buf, format='png')
    buf.seek(0)
    return __sendToApi(buf.read())
