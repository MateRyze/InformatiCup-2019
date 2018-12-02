import io
import requests
import json
import random
from PIL import Image
from interface.util import config

def __sendToApi(data):
    """
    Classify an image using the API.
    data needs to contain the bytes of a png formatted image.
    """
    key = config.get('API', 'key')
    url = config.get('API', 'url')
    success = False
    while not success:
        try:
            res = requests.post(url, data={'key': key}, files={'image': data})
            success = True
        except json.decoder.JSONDecodeError:
            sleepTime = random.randrange(10, 30)
            print('Rate limiting detected!')
            print('Sleeping for %i seconds'%sleepTime)
            time.sleep(sleepTime)
    return res.json()

def classifyFile(path):
    """
    Send an image to the API using its filename.
    """
    return __sendToApi(open(path, 'rb'))

def classifyPILImage(image):
    """
    Send an image to the API, which is represented as an instance of the PIL library's Image class.
    """
    buf = io.BytesIO()
    image.save(buf, format='png')
    buf.seek(0)
    return __sendToApi(buf.read())
