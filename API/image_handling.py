import os
from time import time, sleep
from uuid import uuid4
import numpy as np
from PIL import Image
import requests
from API.text_processing import classify_lang, find_photos_by_text
from API.mongo_parser import MongoParser
from API.python_utils import timeit
from API.image_processing.OCR_engine import teserract_description
from API.image_processing.hue import get_hue, get_hue_16, same_hue_16
from API.image_processing.ssim import high_ssim
from API.image_processing.resize import resize
from API.config import db_name, tesseract_path, tmp_path, telegraph_url
from API.python_utils import api_ok, api_error

parser = MongoParser(db_name)


class ImageInfo:
    def __init__(self, file):
        self.file = file
        self.id = str(uuid4())
        self.image_bytes = self.file.read()
        pil_img = Image.open(self.file)
        self.pil_img = pil_img.convert("RGB")
        self.matrix = np.array(self.pil_img)
        self.size = list(self.pil_img.size)
        self.hue = get_hue(self.matrix)
        self.hue_16 = get_hue_16(self.matrix)
        self.resized_matrix = resize(self.matrix)
        self.telegraph_path = None
        self.resized_img_path = None

    @timeit
    def save_to_telegraph(self):
        files = {'upload_file': self.image_bytes}
        response = requests.post(
            telegraph_url,
            files=files
        ).json()
        self.telegraph_path = response[0]['src']
        return self.telegraph_path

    def save_resized_img(self, resized_img_dir='resized'):
        pil_img_resized = Image.fromarray(self.resized_matrix)
        self.resized_img_path = os.path.join(resized_img_dir, 'r' + self.telegraph_path[6:])
        pil_img_resized.save(self.resized_img_path)
        return self.resized_img_path

    @timeit
    def get_description(self):
        return teserract_description(img=self.matrix, tesseract_path=tesseract_path)

    def save_to_drive(self):
        self.pil_img.save(os.path.join(tmp_path, self.id + '.jpg'))


def presave_img(img: ImageInfo, save_resized=False):
    same_objects = parser.find_same_obj(hue=img.hue, figsize=img.size)
    if same_objects:
        return api_ok('ALREADY_EXISTS')

    ok = False
    for i in range(3):
        try:
            telegraph_path = img.save_to_telegraph()
            ok = True
            break
        except:
            sleep(0.1)
    if not ok:
        return api_error(500, 'TELEGRAPH_UNAVAILABLE')

    resized_path = img.save_resized_img() if save_resized else ''
    parser.save(id=img.id,
                img_path=telegraph_path,
                rus_descr='',
                eng_descr='',
                img_size=img.size,
                img_hue=img.hue,
                resized=resized_path,
                hue_array=img.hue_16,
                ready=False,
                saved_at=time())
    img.save_to_drive()
    return api_ok(True)


def right_candidate(candidate: dict, img: ImageInfo, include_ssim: bool):
    right_hue = same_hue_16(list(candidate['hue_array']), img.hue_16)
    if include_ssim:
        right_ssim = high_ssim(resized_img_path=candidate['resized_img_path'], resized_matrix=img.resized_matrix)
        return right_hue and right_ssim
    return right_hue


def text2pic(raw_text):
    if raw_text == '':
        return [i['img_path'] for i in parser.find_last_n(50)]
    search_text = raw_text.lower()
    lang = classify_lang(search_text)
    pic_names, descriptions = parser.all_names_and_descr(lang=lang)
    filenames = find_photos_by_text(pic_names=pic_names, descriptions=descriptions, search_text=search_text)
    return filenames


def pic2pic(file):
    img = ImageInfo(file)
    first_candidates = parser.find_obj_by_hue(hue=img.hue, max_hue_diff=2.5)
    filenames = []
    for candidate in first_candidates:
        if right_candidate(candidate, img, include_ssim=False):
            filenames.append(candidate['img_path'])
    return filenames
