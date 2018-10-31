import requests
import os
import skimage
import time
from PIL import Image
rootdir = './signs'
names = set([])
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		path = os.path.join(subdir, file)
		print(path)
		'''
		# resize images to 64x64
		data = skimage.io.imread(path)
		data = skimage.transform.resize(data, (64, 64))
		skimage.io.imsave(path, data)
		'''
		image = Image.open(path)
		payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
		r = requests.post('https://phinau.de/trasi', data=payload, files= {'image': open(path, 'rb')})
		# get all classes from the API and map images with confidence > 90 %
		for obj in r.json():
			names.add(obj.get('class'))
			if(obj.get('confidence') > 0.90):
				image.save('./recognized/' + obj.get('class') + '.png')
		time.sleep(1)
print(names, len(names))
		


