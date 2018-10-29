import requests
import json
payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo', 'image':open('test.png', 'rb')}
headers = {'Content-Type': 'multipart/form-data'}
r = requests.post('https://phinau.de/trasi', data=payload, headers=headers)
print(r.text, r.json) 
