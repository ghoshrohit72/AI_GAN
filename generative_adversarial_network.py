# -*- coding: utf-8 -*-
"""Generative Adversarial Network.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M15qjajQ8Q3UCieHjJfCVIzYhQABIqsv
"""

# Commented out IPython magic to ensure Python compatibility.
import glob
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
from google.colab import output

!unzip roads.zip
output.clear()

image_path = "roads/*"
images_array= []
for image in glob.glob(image_path):
  img= Image.open(image)
  img =Image.Image.resize(img, (240,240))
  img= np.asarray(img)
  images_array.append(img)

images_array=np.asarray(images_array)
x_train = images_array.astype('float32')
x_train = (x_train-127.5)/127.5

#designing the archtecture of the generator and discriminiator

from keras.models import Model, Sequential
from keras.layers import *
from keras.layers.advanced_activations import LeakyReLU

generator = Sequential(
    [
     Dense(128*60*60, input_dim=100, activation =LeakyReLU(0.2)),
    BatchNormalization(),
    Reshape((60,60,128)),
    UpSampling2D(),
    Convolution2D(128,5,5, border_mode="same", activation =LeakyReLU(0.2)) ,
    BatchNormalization(),
    Convolution2D(56,3,3, border_mode="same", activation=LeakyReLU()),
    BatchNormalization(),
    UpSampling2D(),
    Convolution2D(3,5,5, border_mode="same", activation="tanh")
    ]
) 

generator.summary()

discriminator= Sequential([
    Convolution2D(124,5,5, subsample=(2,2), input_shape=(240,240,3), border_mode="same", activation=LeakyReLU(0.4)),
    Dropout(0.4),
    Convolution2D(124,5,5, subsample=(2,2), border_mode="same", activation=LeakyReLU(0.4)),
    Dropout(0.4),
    Flatten(),
    Dense(1, activation="sigmoid")
])

discriminator.summary()

#compiling the model

from tensorflow.keras.optimizers import Adam

adam= Adam(lr=0.001, beta_1=0.5)
discriminator.trainable= True
discriminator.compile(loss='binary_crossentropy' , optimizer=adam)

generator.compile(loss='binary_crossentropy' , optimizer=adam)
ganInput= Input(shape=(100,))
x =  generator(ganInput)

discriminator.trainable= False
ganOutput = discriminator(x)

gan =Model(input= ganInput, output=ganOutput)
gan.compile(loss='binary_crossentropy', optimizer=adam)

def train(num_epoch, batch_size):
  batch_count = x_train.shape[0] // batch_size  
  print("batch count: {}".format(batch_count))

  for epoch in range(num_epoch):
    print("Epoch number{}".format(epoch))
    
    for batch in range(batch_size):
        noise_input = np.random.rand(batch_size, 100)
        fake_images= generator.predict(noise_input, batch_size= batch_size)

        image_batch = x_train[np.random.randint(0, x_train.shape[0], size=batch_size)]
        images = np.concatenate([fake_images, image_batch])

        labels= [0.95] *batch_size + [0.05] *batch_size

        discriminator.trainable =True
        d =  discriminator.fit(images, labels, verbose = 0)

        y_generator = [0.05]* batch_size
        discriminator.trainable = False
        g= gan.fit(noise_input, y_generator, verbose=0)
        input_g = np.random.rand(1, 100)
        preds= (generator.predict(input_g)+1.0)/2.0

        if epoch%10 == 0:
          for pred in range(preds.shape[0]):
            plt.imshow(preds[pred])
            if epoch%30 == 0:
              plt.savefig("GAN_output/epoch{}.jpg".format(str(epoch)), dpi= 250)
          plt.show()

!mkdir GAN_output

train(50000, 5)

