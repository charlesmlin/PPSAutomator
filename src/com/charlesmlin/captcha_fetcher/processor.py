import glob
import os
from pathlib import Path
from typing import List

import cv2
import numpy

from src.com.charlesmlin.captcha_fetcher.util import CaptchaUtils
from src.com.charlesmlin.pps_automator.util import Utils


def extract_single_letter_image(image_path: Path) -> None:
    output_folder: Path = Path.joinpath(image_path.parent.parent, 'output')
    text = image_path.name.split('.')[0]
    letter_images: List[numpy.ndarray] = CaptchaUtils.separate_letters(image_path)
    if len(letter_images) != 4:
        print(f'[WARN] Error processing {str(image_path)}, {len(letter_images)} letters are retrieved')
        return
    for (letter_image, letter) in zip(letter_images, text):
        target_folder = output_folder.joinpath(letter)
        if not os.path.exists(str(target_folder)):
            os.makedirs(str(target_folder))
        counter = len(glob.glob(str(target_folder.joinpath("*"))))
        target_file = str(target_folder.joinpath(f'{"{:05d}".format(counter + 1)}.jpg'))
        print(f'{target_file} - letter:{letter}, text:{text}')
        cv2.imwrite(target_file, letter_image)


if __name__ == '__main__':
    path: Path = Utils.get_project_path()
    captchas = glob.glob(str(path.joinpath("captcha", "*")))
    for captcha in captchas:
        extract_single_letter_image(Path(captcha))
