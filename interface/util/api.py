import io
import requests
from PIL import Image
from interface.util import config

__RATE_LIMITED = False

def __sendToApi(data):
    """
    Classify an image using the API.
    data needs to contain the bytes of a png formatted image.
    """
    key = config.get('API', 'key')
    url = config.get('API', 'url')
    res = requests.post(url, data={'key': key}, files={'image': data})
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
