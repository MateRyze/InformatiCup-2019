#!/usr/bin/env python3
import os
import csv
import random
import argparse
from collections import namedtuple

DatasetEntry = namedtuple('DatasetEntry', 'filename x1 y1 x2 y2 class_id')

# we make some hardcoded assumptions about the dataset in this script
num_classes = 43

# commandline interface
parser = argparse.ArgumentParser()
parser.add_argument('trainset', type=str)
parser.add_argument('testset', type=str)
parser.add_argument('-g', '--ngpus', default=1, type=int,
    help='Count of GPUs to use for training.')
parser.add_argument('-e', '--epochs', default=10, type=int,
    help='How many epochs to train for.')
parser.add_argument('-b', '--batch-size', default=32, type=int,
    help='Size of individual training batches.')
parser.add_argument('-m', '--multiprocessing', default=False, action='store_true',
    help='Load data using a separate process.')
parser.add_argument('-a', '--application', default='idsia',
    help='Network to use for training.')
parser.add_argument('-s', '--save', default='exported', type=str,
    help='Where to store the trained network.')
parser.add_argument('-w', '--weights', default='', type=str,
    help='Use previously saves weights (i.e. to continue training).')
args = parser.parse_args()

import keras
import numpy as np
import skimage

def read_GTSRB_train(directory, shuffle = True):
    """
    Read the training portion of GTSRB database.
    Each class has an own index file.
    """
    print('Reading trainset index...')
    entries = []
    for class_id in range(num_classes):
        # each class is in a separate folder
        print('\r%i%%'%(int((class_id/num_classes) * 100)), end='')
        class_str = str(class_id).zfill(5)
        class_directory = os.path.join(directory, class_str)
        # each class has an own indes file
        index_filename = os.path.join(class_directory, 'GT-%s.csv'%class_str)
        index = csv.DictReader(open(index_filename, 'r'), delimiter=';')
        for line in index:
            filename = os.path.join(class_directory, line['Filename'])
            x1 = int(line['Roi.X1'])
            y1 = int(line['Roi.Y1'])
            x2 = int(line['Roi.X2'])
            y2 = int(line['Roi.Y2'])
            # there is no need to use the class_id from the csv file
            # we can be sure that it corresponds to the folder
            entries.append(DatasetEntry(filename, x1, y1, x2, y2, class_id))
    print('\rdone')
    if shuffle: random.shuffle(entries)
    return entries

def read_GTSRB_test(directory, shuffle = True):
    """
    Read testing portion of the GTSRB database.
    Only one index file is used.
    """
    print('Reading testset index...')
    entries = []
    # one folder for all classes
    index_filename = os.path.join(directory, 'GT-final_test.csv')
    # also only one index file
    index = csv.DictReader(open(index_filename, 'r'), delimiter=';')
    max_entry = 12630
    for line in index:
        print('\r%i%%'%(int((len(entries)/max_entry) * 100)), end='')
        filename = os.path.join(directory, line['Filename'])
        x1 = int(line['Roi.X1'])
        y1 = int(line['Roi.Y1'])
        x2 = int(line['Roi.X2'])
        y2 = int(line['Roi.Y2'])
        class_id = int(line['ClassId'])
        # here, the index file contains the class id to use
        entries.append(DatasetEntry(filename, x1, y1, x2, y2, class_id))
    print('\rdone')
    if shuffle: random.shuffle(entries)
    return entries

def dataset_generator(dataset, batch_size = 32):
    """
    Receives an array of DatasetEntries and returns an tuple containing inputs and targets to be
    used as input for Keras.
    """
    while True:
        inputs = []
        targets = []
        for entry in trainset:
            # read image and cut out the portion containing the traffic sign
            data = skimage.io.imread(entry.filename)
            data = data[entry.x1:entry.x2, entry.y1:entry.y2]
            # resize the data to a fixed size
            data = skimage.transform.resize(data, (64, 64))
            inputs.append(data)
            # turn class id into a binary class vector
            # e.g.:    3 -> [0, 0, 0, 1, 0, 0, 0]
            targets.append(keras.utils.to_categorical(entry.class_id, num_classes=num_classes))
            if len(targets) >= batch_size:
                # yield allows this function to run continuall and be used similarly to a list,
                # which can be read sequentially
                yield (np.array(inputs), np.array(targets))
                inputs = []
                targets = []
        yield (np.array(inputs), np.array(targets))

def dataset_into_memory(dataset):
    """
    Receives an array of DatasetEntries and returns an tuple containing inputs and targets to be
    used as input for Keras.
    """
    inputs = []
    targets = []
    for entry in trainset:
        # read image and cut out the portion containing the traffic sign
        data = skimage.io.imread(entry.filename)
        data = data[entry.x1:entry.x2, entry.y1:entry.y2]
        # resize the data to a fixed size
        data = skimage.transform.resize(data, (64, 64))
        inputs.append(data)
        targets.append(keras.utils.to_categorical(entry.class_id, num_classes=num_classes))
    return (np.array(inputs), np.array(targets))

def makenet_idsia(weights, input_shape, classes):
    input_activation = 'relu'
    hidden_activation = 'relu'
    output_activation = 'softmax'
    model = keras.models.Sequential()

    model.add(keras.layers.Conv2D(100, input_shape=input_shape, kernel_size=(7, 7), activation=input_activation))
    model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(keras.layers.Dropout(0.15))

    model.add(keras.layers.Conv2D(150, kernel_size=(4, 4), activation=hidden_activation))
    model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(keras.layers.Dropout(0.15))

    model.add(keras.layers.Conv2D(250, kernel_size=(4, 4), activation=hidden_activation))
    model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))
    model.add(keras.layers.Dropout(0.15))

    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(300, activation='relu'))
    model.add(keras.layers.Dense(classes, activation=output_activation))
    return model

trainset = read_GTSRB_train(args.trainset)
testset = read_GTSRB_test(args.testset)

# all models we could use
applications = {
    'vgg16': keras.applications.vgg16.VGG16,
    'vgg19': keras.applications.vgg19.VGG19,
    'idsia': makenet_idsia,
}

model = applications[args.application](weights=None, input_shape=(64, 64, 3), classes=num_classes)

if args.weights != '':
    model.load_weights(args.weights)

if args.ngpus > 1:
    pmodel = keras.utils.multi_gpu_model(model, gpus=args.ngpus)
else:
    pmodel = model

#X_train, Y_train = dataset_into_memory(trainset)
#X_test, Y_test = dataset_into_memory(testset)

pmodel.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(pmodel.summary())
batch_size = args.batch_size
try:
    model.save('%s.json'%args.save)
except:
    print('Failed to save model architecture, check your code if you want to restore :D')
for epoch in range(args.epochs):
    pmodel.fit_generator(
        generator = dataset_generator(trainset, batch_size=batch_size),
        steps_per_epoch = len(trainset)//batch_size,
        # don't use the complete test portion of the dataset for each epoch, as it would take very long
        # instead, only test 256 elements per batch in 4 batches
        validation_data = dataset_generator(testset, batch_size=256),
        validation_steps = 4,
        epochs = 1,
        use_multiprocessing = args.multiprocessing,
    )
    """
    pmodel.fit(
        x = X_train,
        y = Y_train,
        validation_data = (X_test, Y_test),
        epochs = 1,
    )
    """
    model.save_weights('%s.h5'%args.save)
