import requests
import os
import skimage
import time
import csv
from PIL import Image
# dir with test images
rootdir = './test' 

# resize images to 64x64 and convert from PPM to PNG format
def convertImages():
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
				path = os.path.join(subdir, file)
				print(path)
				data = skimage.io.imread(path)
				data = skimage.transform.resize(data, (64, 64))
				skimage.io.imsave(path.replace('.ppm', '.png'), data)

def getClasses():
	names = set([])
	list = []
	i = 0
	limit = 13000
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			if (i < limit):
				path = os.path.join(subdir, file)
				if '.png' in path:
					print(path)
					image = Image.open(path)
					payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
					r = requests.post('https://phinau.de/trasi', data=payload, files= {'image': open(path, 'rb')})
					# get all classes from the API and map images with confidence > 90 %
					try:
						names.add(r.json()[0].get('class'))
						d = {"filename": path, "class": r.json()[0].get('class'), "confidence": r.json()[0].get('confidence')}
						print(d)
						list.append(d)
						print(i, len(names))
						time.sleep(1)
						i = i + 1
					except:
						with open('results.csv', 'w') as f:
							w = csv.DictWriter(f, list[0].keys(), delimiter =';')
							for item in list:
								w.writerow(item)
		
	with open('results.csv', 'w') as f:
		w = csv.DictWriter(f, list[0].keys(), delimiter =';')
		for item in list:
			w.writerow(item)
	print(names, len(names))
	#file = open("classes.txt", "w")
	#file.write(names, len(names))
	
	
#convertImages()
getClasses()

	
		


