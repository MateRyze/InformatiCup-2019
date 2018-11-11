import requests
from interface.util import config

def classifyFile(path):
    key = config.get('API', 'key')
    url = config.get('API', 'url')
    res = requests.post(url, data={'key': key}, files={'image': open(path, 'rb')})
    return res.text
