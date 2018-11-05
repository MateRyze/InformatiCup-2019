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
					# get all classes from the API and map images with confidence > 90 %
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

	output = [u'Zul\xe4ssige H\xf6chstgeschwindigkeit (20)', u'Vorfahrt', u'Kreisverkehr', u'Ende des \xdcberholverbotes f\xfcr Kraftfahrzeuge mit einer zul\xe4ssigen Gesamtmasse \xfcber 3,5t', u'Fu\xdfg\xe4nger', u'Gefahrenstelle', u'Einmalige Vorfahrt', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (30)', u'Fahrradfahrer', u'Verbot f\xfcr Kraftfahrzeuge mit einer zul\xe4ssigen Gesamtmasse von 3,5t', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (50)', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (120)', u'Ausschlie\xdflich rechts', u'Baustelle', u'Ende der Geschwindigkeitsbegrenzung (80)', u'Stoppschild', u'Unebene Fahrbahn', u'Kurve (links)', u'Ende aller Streckenverbote', u'Kurve (rechts)', u'Doppelkurve (zun\xe4chst links)', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (70)', u'Wildwechsel', u'Ausschlie\xdflich geradeaus', u'\xdcberholverbot f\xfcr Kraftfahrzeuge mit einer zul\xe4ssigen Gesamtmasse \xfcber 3,5t', u'Verbot der Einfahrt', u'Vorfahrt gew\xe4hren', u'\xdcberholverbot f\xfcr Kraftfahrzeuge aller Art', u'Schleudergefahr bei N\xe4sse oder Schmutz', u'Verbot f\xfcr Fahrzeuge aller Art', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (60)', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (100)', u'Rechts vorbei', u'Zul\xe4ssige H\xf6chstgeschwindigkeit (80)', u'Ende des \xdcberholverbotes f\xfcr Kraftfahrzeuge aller Art']	
	with open('results2.txt', 'wt') as f:
		for name in output:
			f.write(name + "\n")
		'''
	print(names, len(names))
	#file = open("classes.txt", "w")
	#file.write(names, len(names))

def mapResults():
	with open('results.csv', 'r') as f:
		df = pd.read_csv(f, delimiter=";", names=['name', 'class', 'confidence'], header=None)
		print(df.loc[df['name'] == "./test\\.png"])

	
#convertImages()
getClasses()
#mapResults()
	
		


