import pickle
from pathlib import Path
from typing import List

import numpy
import cv2
from keras import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

from src.com.charlesmlin.captcha_fetcher.util import CaptchaUtils
from src.com.charlesmlin.pps_automator.util import Utils

MODEL_FILENAME = "captcha_model.hdf5"
MODEL_DIGITS_FILENAME = "model_digits.dat"

if __name__ == '__main__':
    path: Path = Utils.get_project_path()
    output_path = path.joinpath('output')
    data: List[numpy.ndarray] = []
    digits: List[str] = []
    for output_folder in output_path.glob('*'):
        digit = output_folder.name
        for image_file in output_folder.glob('*'):
            image = cv2.imread(str(image_file))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = CaptchaUtils.resize_to_fit(image, 20, 20)
            image = numpy.expand_dims(image, axis=2)
            data.append(image)
            digits.append(digit)
    data: numpy.ndarray = numpy.array(data, dtype="float") / 255.0
    digits: numpy.ndarray = numpy.array(digits)

    (X_train, X_test, Y_train, Y_test) = train_test_split(data, digits, test_size=0.25, random_state=0)
    lb = LabelBinarizer().fit(Y_train)
    Y_train = lb.transform(Y_train)
    Y_test = lb.transform(Y_test)

    with open(str(path.joinpath('libs', MODEL_DIGITS_FILENAME)), "wb") as f:
        pickle.dump(lb, f)

    model = Sequential()
    model.add(Conv2D(20, (5, 5), padding="same", input_shape=(20, 20, 1), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
    model.add(Conv2D(50, (5, 5), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
    model.add(Flatten())
    model.add(Dense(500, activation="relu"))
    model.add(Dense(len(set(digits)), activation="softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test), batch_size=32, epochs=10, verbose=1)
    model.save(str(path.joinpath('libs', MODEL_FILENAME)))
