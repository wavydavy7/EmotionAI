from matplotlib import pyplot as plt
import pandas as pd
import sys
import os
import numpy as np
import csv
import os
import time
import pandas as pd
import tensorflow as tf
from keras import layers, models, callbacks
from keras.layers import Dense, Activation, Dropout, Flatten, BatchNormalization, Conv2D, MaxPool2D
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split

emotions = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']

def main():
    # Ensure tensorflow is utilizing the GPU
    if (len(tf.config.list_physical_devices('GPU')) == 0):
        quit()

    df = pd.read_csv("./dataset/data.csv").drop(columns=["Usage"])

    df = df[df["emotion"].isin([3, 4])]
    
    labels = df["emotion"].apply(lambda x: x-3).values
    image_strings = df["pixels"].values
    image_vector = np.array([int(x) for s in image_strings for x in s.split()])
    images = image_vector.reshape(labels.shape[0], 48, 48)

    # print(images.shape)
    # print(labels.shape)
    # print(labels[0])
    # plt.imshow(images[0], cmap='gray')  # You can change the colormap as needed
    # plt.axis('off')  # Turn off axis
    # plt.show()

    train_images, test_images, train_labels, test_labels \
        = train_test_split(images, labels, test_size=0.1, random_state=42)

    model = models.Sequential()
    model.add(Conv2D(32, 3, input_shape=(48, 48, 1), padding='same', 
                    activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(32, 3, padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    # 2nd stage
    model.add(Conv2D(64, 3, padding='same', 
                    activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, 3, padding='same', 
                    activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))
    model.add(Dropout(0.25))

    # 3rd stage
    model.add(Conv2D(128, 3, padding='same', 
                    activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(128, 3, padding='same', 
                    activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))
    model.add(Dropout(0.25))

    # FC layers
    model.add(Flatten())
    model.add(Dense(256))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(256))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(256))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(2))
    model.add(Activation('softmax'))

    callback = callbacks.EarlyStopping(
        monitor="val_accuracy", baseline=0.8, verbose=1, 
        patience=30, restore_best_weights=True)

    model.compile(optimizer="adam",
            loss=tf.keras.losses.SparseCategoricalCrossentropy(
                from_logits=True),
            metrics=["accuracy"])

    # Number of epochs
    NUM_EPOCHS = 200

    # Get training start time
    start_time = time.time()

    # Train the model
    model.fit(train_images, train_labels, epochs=NUM_EPOCHS, 
            validation_data=(test_images, test_labels), 
            callbacks=[callback])
    
    # Get training end time
    end_time = time.time()

    # Test the model and get metrics
    test_loss, test_acc = model.evaluate(test_images, test_labels, 
                                        verbose=2)

    # Update console
    print(f"Average test accuracy: {test_acc}")
    print(f"Average test loss: {test_loss}")
    print(f"Average Fit time: {end_time - start_time}")

    # Create a dataframe to store results to be saved into file
    results = pd.DataFrame()
    results["Number of Epochs"] = [NUM_EPOCHS]
    results["Fit Time"] = [end_time - start_time]
    results["Test Accuracy"] = [test_acc]
    results["Test Loss"] = [test_loss]
    
    # Transpose the dataframe to get metrics as rows
    results = results.T

    # Update console
    print("Results: ")
    print(results)

    # Save df to csv
    dir = f"./model/"
    print(f"Storing model and results in {dir}")
    if not os.path.exists(dir): os.makedirs(dir)
    model.save_weights(f'{dir}weights.h5')
    model.save(f'{dir}model.h5')
    results.to_csv(f"{dir}evaluation.csv", header=False)

if __name__ == '__main__':
    main()

