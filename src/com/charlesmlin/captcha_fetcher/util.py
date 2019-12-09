import pickle
from pathlib import Path
from typing import List, Tuple
from keras.models import load_model

import imutils
import cv2
import numpy

from src.com.charlesmlin.pps_automator.util import Utils

AVERAGE_WIDTH = 50
AVERAGE_HEIGHT = 50
MIN_RATIO = 0.75
EDGE = 2
MODEL_CAPTCHA_FILENAME = "captcha_model.hdf5"
MODEL_DIGITS_FILENAME = "model_digits.dat"


class CaptchaUtils:
    @staticmethod
    def resize_to_fit(image, width, height):
        (h, w) = image.shape[:2]
        if w > h:
            image = imutils.resize(image, width=width)
        else:
            image = imutils.resize(image, height=height)
        pad_w = int((width - image.shape[1]) / 2.0)
        pad_h = int((height - image.shape[0]) / 2.0)
        image = cv2.copyMakeBorder(image, pad_h, pad_h, pad_w, pad_w,
                                   cv2.BORDER_REPLICATE)
        image = cv2.resize(image, (width, height))
        return image

    @staticmethod
    def separate_letters(image_path: Path) -> List[numpy.ndarray]:
        original_image = cv2.imread(str(image_path))
        gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        black_and_white = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        contours = cv2.findContours(black_and_white.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0]
        letter_image_regions: List[Tuple[int, int, int, int]] = []
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if w < AVERAGE_WIDTH * MIN_RATIO or h < AVERAGE_HEIGHT * MIN_RATIO:
                continue
            image_count = round(w / AVERAGE_WIDTH)
            average_width = round(w / image_count)
            for i in range(image_count):
                letter_image_regions.append((x + i * average_width, y, min(average_width, w - i * average_width), h))
        letter_image_regions = sorted(letter_image_regions, key=lambda tuples: tuples[0])
        return list(
            map(lambda x, y, w, h: gray[y - EDGE: y + h + EDGE, x - EDGE: x + w + EDGE],
                *Utils.flip(letter_image_regions)))

    @staticmethod
    def predict(image_path: Path) -> str:
        path: Path = Utils.get_project_path()
        with open(str(path.joinpath('libs', MODEL_DIGITS_FILENAME)), "rb") as f:
            lb = pickle.load(f)
        model = load_model(str(path.joinpath('libs', MODEL_CAPTCHA_FILENAME)))

        letter_images: List[numpy.ndarray] = CaptchaUtils.separate_letters(image_path)
        captcha_text = ''
        if len(letter_images) == 4:
            for letter_image in letter_images:
                letter_image = CaptchaUtils.resize_to_fit(letter_image, 20, 20)
                letter_image = numpy.expand_dims(letter_image, axis=2)
                letter_image = numpy.expand_dims(letter_image, axis=0)
                prediction = model.predict(letter_image)
                letter = lb.inverse_transform(prediction)[0]
                captcha_text += letter
        else:
            print(f'[WARN] Error processing {str(image_path)}, {len(letter_images)} letters are retrieved')
        return captcha_text
