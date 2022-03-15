import numpy as np
import cv2
from PIL import Image


def resize(matrix, size=(200, 200)):
    return cv2.resize(matrix, dsize=size)


def load_resized_matrix(path):
    return np.array(Image.open(path))
