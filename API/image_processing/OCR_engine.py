import cv2
import pytesseract
from PIL import Image, ImageFilter
import numpy as np
from threading import Thread
from API.image_processing.resize import resize


def resize_photo(np_img):
    shape = np_img.shape
    if min(shape) >= 800:
        new_shape = np.array(shape) / 2
        int_new_shape = new_shape.astype(int)
        return resize(matrix=np_img, size=tuple(int_new_shape))
    else:
        return np_img


def process_photo(np_img):
    img = np.array(Image.fromarray(np_img).filter(ImageFilter.SHARPEN))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # for less noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = resize_photo(img)
    return img


def run_ocr_core(img, lang, tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    result = pytesseract.image_to_string(Image.fromarray(img), lang=lang)
    return result


def clear_string(string):
    return string.lower().replace('\n', ' ').replace('*', '').replace('$', '')


def prepare_pic(img):
    img = process_photo(img)
    img = resize_photo(img)
    return img


def pic2string(img, lang, tesseract_path):
    description = run_ocr_core(img, lang, tesseract_path)
    return clear_string(description)


class OcrThread(Thread):
    def __init__(self, lang, prepared_img, tesseract_path):
        self.lang = lang
        self.prepared_img = prepared_img
        self.tesseract_path = tesseract_path
        self._return = None
        Thread.__init__(self)

    def run(self):
        self._return = pic2string(self.prepared_img, self.lang, self.tesseract_path)

    def join(self, *args):
        Thread.join(self)
        return self._return


def threading_description(img, tesseract_path):
    results = []
    prepared_img = prepare_pic(img)
    for lang in ['rus', 'eng']:
        thread = OcrThread(lang, prepared_img, tesseract_path)
        thread.start()
        results.append(thread.join())
    return results


def teserract_description(img, tesseract_path):
    prepared_img = prepare_pic(img)
    try:
        return [pic2string(prepared_img, 'rus', tesseract_path), pic2string(prepared_img, 'eng', tesseract_path)]
    except:
        return ['', '']
