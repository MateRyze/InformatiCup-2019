#!/usr/bin/env python3
"""
Mit den Funktionen in dieser Datei können Eingabedaten mit Hilfe von neuronalen Netzen klassifiziert/erzeugt/verändert werden.
"""

import sys
from collections import namedtuple
import numpy as np
import keras
from keras import backend as K
import skimage

num_classes = 43

def normalizeTensor(x):
    # utility function to normalize a tensor by its L2 norm
    return x / (K.sqrt(K.mean(K.square(x))) + K.epsilon())

def synthesize(model, c, max_iter=200):
    """
    Erzeugt eine Eingabe, die eine bestimmte Klasse für ein Model maximieren.
    """
    out_layer = model.layers[-1]
    numClasses = out_layer.output_shape[-1]
    loss = keras.losses.mean_squared_error(keras.utils.to_categorical(c, num_classes = numClasses), out_layer.output)
    grads = K.gradients(loss, model.input)[0]
    grads = normalizeTensor(grads)
    shape = (1,) + model.input_shape[1:]
    in_data = np.random.random(shape)
    iterate = K.function([model.input], [loss, grads])
    step = -0.01
    for j in range(max_iter):
        loss_value, grads_value = iterate([in_data])
        if np.max(grads_value) == 0.0:
            break
        grads_value -= np.min(grads_value)
        grads_value /= np.max(grads_value)
        grads_value -= np.mean(grads_value)
        # loss may be unrealistically small
        if loss_value <= 0:
            if j < 100:
                # if we have enough iterations left, we just restart with a new random image
                in_data = np.random.random(shape)
            else:
                # otherwise the current image is returned
                break
        in_data += grads_value * step
    image = in_data[0]
    image /= np.max(image)
    return image

def synthesize_multinets(models, c, base=None, max_iter=40, step=0.01, init_func=np.random.random):
    """
    Erzeugt eine Eingabe, die für mehrere Modelle eine gegebene Klasse maximiert.
    Dabei ist nicht unbedingt gegeben, dass die Eingabe für alle Modelle die gewünschte Klasse maximiert, da ein
    Mittelwert gefunden wird.
    """
    GradientAscentNet = namedtuple('GradientAscentNet', 'out_layer num_classes loss grads iterate')
    nets = []

    for model in models:
        out_layer = model.layers[-1]
        num_classes = out_layer.output_shape[-1]
        loss = keras.losses.mean_squared_error(keras.utils.to_categorical(c, num_classes = num_classes), out_layer.output)
        grads = K.gradients(loss, model.input)[0]
        grads = normalizeTensor(grads)
        iterate = K.function([model.input], [loss, grads])
        net = GradientAscentNet(out_layer, num_classes, loss, grads, iterate)
        nets.append(net)

    shape = (1,) + model.input_shape[1:]
    if base is None:
        in_data = init_func(shape)
    else:
        in_data = np.array([base])
    for j in range(max_iter):
        print('\r%i%%'%(int(j/max_iter*100)), end='')
        for net in nets:
            loss_value, grads_value = iterate([in_data])
            if loss_value <= 0 or np.max(grads_value) == 0.0:
                continue
            grads_value -= np.min(grads_value)
            grads_value /= np.max(grads_value)
            grads_value -= np.mean(grads_value)

            in_data -= grads_value * step
    print('\rdone!')
    image = in_data[0]
    image -= np.min(image)
    image /= np.max(image)
    return image

def add_loss(model, c, base, iterations=200):
    """
    Modifiziert Eingabedaten so, dass eine bestimmte alternative Klasse maximiert wird.
    """
    out_layer = model.layers[-1]
    numClasses = out_layer.output_shape[-1]
    #loss = keras.losses.mean_squared_error(keras.utils.to_categorical(c, num_classes = numClasses), out_layer.output)
    loss = keras.losses.categorical_crossentropy(keras.utils.to_categorical(c, num_classes = numClasses), out_layer.output)
    #loss = K.mean(out_layer.output[:c])
    grads = K.gradients(loss, model.input)[0]
    grads = normalizeTensor(grads)
    shape = (1,) + model.input_shape[1:]
    in_data = np.array([base])
    #in_data = np.random.random(shape)
    iterate = K.function([model.input], [loss, grads])
    step = 1.0 / iterations
    for i in range(iterations):
        loss_value, grads_value = iterate([in_data])
        print(loss_value)
        print(np.max(grads_value))
        if np.max(grads_value) == 0.0:
            for pixel in range(10):
                x = int(np.random.rand() * shape[1])
                y = int(np.random.rand() * shape[2])
                for c in range(3):
                    in_data[0,x,y,c] = np.random.rand()
        else:
            grads_value -= np.min(grads_value)
            grads_value /= np.max(grads_value)
            grads_value -= np.mean(grads_value)
            in_data += grads_value * step
            print(":)")
            break
    image = in_data[0]
    image -= np.min(image)
    image /= np.max(image)
    return image

def bruteforce(model, c, max_iter=1000):
    """
    Generiere Zufallsdaten, bis diese eine Klasse maximieren oder die maximale Anzahl an Iterationen verbraucht ist.
    """
    shape = (1,) + model.input_shape[1:]
    for i in range(max_iter):
        image = np.random.random(shape)
        prediction = model.predict(image, batch_size=1)[0]
        pred_c = np.argmax(prediction)
        if pred_c == c:
            return image[0]
        print('%i/%i'%(i, max_iter), end='\r')
    raise ValueError('no suitable image found')

def makenet_idsia(weights, input_shape, classes):
    """
    Erzeuge ein Netz mit dem korrekten Aufbau für die IDSIA Gruppe.
    """
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

def test_create(model):
    image_orig = skimage.io.imread('vorfahrt.png')
    image = add_loss(model, 1, image_orig)
    #image = bruteforce(model, 1)
    #image = synthesize(model, 1)

    skimage.io.imsave('created.png', image)

def test_add_loss(model):
    image_orig = skimage.io.imread('vorfahrt.png')
    image_orig = image_orig / 255.0
    image = add_loss(model, 30, image_orig)
    faked = synthesize(model, 31)
    predictions = model.predict(np.array([image_orig, image, faked]), batch_size=32)
    for prediction in predictions:
        pred = np.argmax(prediction)
        print(pred)
    skimage.io.imsave('modified.png', image)

def predict_class(model, data):
    return np.argmax(model.predict(np.array([data]), batch_size=1)[0])

def test_create_multinets(models):
    c = 40
    image = synthesize_multinets(models, c, base=None, init_func=np.random.random)
    predictions = []
    good_models = []
    for model in models:
        prediction = predict_class(model, image)
        predictions.append(prediction)
        if prediction == c:
            good_models.append(model)
    correct_preds = len(list(filter(lambda x: x == c, predictions)))
    print(correct_preds)
    skimage.io.imsave('created.png', image)
    image = synthesize_multinets(good_models, c, base=None, init_func=np.ones)
    skimage.io.imsave('created_good.png', image)

def test_predict(model, fname):
    """
    Verwendet ein Netz, um den Inhalt eines Bildes zu klassifizieren.
    """
    image = skimage.io.imread(fname)
    image = skimage.transform.resize(image, (64, 64))
    images = np.array([image])

    predictions = model.predict(images, batch_size=1)
    for prediction in predictions:
        pred = np.argmax(prediction)
        print(pred)

def test_predict_multinets(models, fname):
    """
    Verwendet mehrere Netze, um den Inhalt eines Bildes zu klassifizieren.
    Dabei werden die einzelnen Predictions, sowie die häufigste ausgegeben.
    """
    image = skimage.io.imread(fname)
    image = skimage.transform.resize(image, (64, 64))
    images = np.array([image])

    commitee = [0] * num_classes
    for model in models:
        predictions = model.predict(images, batch_size=1)
        for prediction in predictions:
            pred = np.argmax(prediction)
            conf = prediction[pred]
            print('Class: %i (%i%%)'%(pred, int(conf*100)))
            commitee[pred] += 1
    print('Majority: %i'%np.argmax(commitee))

"""
Hier werden alle verfügbaren Netze initialisiert und trainierte Kantengewichte werden eingelesen.
"""
models = []
for i in range(16):
    model = makenet_idsia(None, (64, 64, 3), 43)
    model.load_weights('trained/idsia-%i.h5'%i)
    models.append(model)

"""
Joa, einfach immer das einkommentieren, was man testen will :)
"""
test_predict_multinets(models, sys.argv[1])
#test_add_loss(models[0])
#test_create(model)
#test_predict(model)
