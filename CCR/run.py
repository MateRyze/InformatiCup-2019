import requests
import os
import skimage
import time
import csv
from PIL import Image
import pandas as pd
# dir with test images
rootdir = './Images' 

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
	limit = 100
	for subdir, dirs, files in os.walk(rootdir):
		for file in files:
			if (i < limit):
				path = os.path.join(subdir, file)
				if '.png' in path:
					print(path)
					image = Image.open(path)
					payload= {'key': 'Engeibei1uok4xaecahChug6eihos0wo'}
					r = requests.post('https://phinau.de/trasi', data=payload, files= {'image': open(path, 'rb')})
					# get all classes from the API
					for name in r.json():
						names.add(name.get('class'))
						print(names, len(names))
					time.sleep(1)
					i = i + 1
						
					'''
					try:
						names.add(r.json()[0].get('class'))
						d = {"filename": path, "class": r.json()[0].get('class'), "confidence": r.json()[0].get('confidence')}
						print(names, len(names))
						list.append(d)
						print(i, len(names))
						time.sleep(1)
						i = i + 1
					except:
						with open('results.csv', 'w') as f:
							w = csv.DictWriter(f, list[0].keys(), delimiter =';')
							for item in list:
								w.writerow(item)
					'''

def mapResults():
	with open('results.csv', 'r') as f:
		df = pd.read_csv(f)
		print(df)
		with open('results_mapping.csv', 'r') as idFile:
			idFileDF = pd.read_csv(idFile)
			print(idFileDF)
			for index, row in idFileDF.iterrows():
				name = row[0]
				df.loc[df['class'] == name, ['actual_id']] = row[1]
			df.to_csv('results_mapped.csv')

# calculate the Correct Classification Rate (CCR) from a CSV file
def calculateCCR():
	cumulatedResult = 0
	with open('results_mapped.csv', 'r') as f:
		df = pd.read_csv(f)
		print(df)
		for index, row in df.iterrows():
			if(row[5] == row[6]):
				#print(row[5], row[6])
				cumulatedResult += 1
		print "CCR: ", float(cumulatedResult)/len(df.index)	
		
#convertImages()
#getClasses()
#mapResults() 
# FOR RESULTS SEE: results_mapped.csv
calculateCCR()	
		


