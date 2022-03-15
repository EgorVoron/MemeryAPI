import numpy as np
from API.image_processing.resize import resize

MAX_HUE_INDEX = 2.0


def rgb_to_hsv(x):
    r = float(x[0])
    g = float(x[1])
    b = float(x[2])
    high = max(r, g, b)
    low = min(r, g, b)
    h, s, v = high, high, high

    d = high - low
    s = 0 if high == 0 else d / high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s, v


def get_mean(arr):
    return np.mean(np.mean(arr, axis=1), axis=0)


def get_hue(arr):
    mean = get_mean(arr)
    h = rgb_to_hsv(mean)[0]
    return h * 100


def same_hue(hue_1, hue_2):
    return abs(hue_1 - hue_2) < MAX_HUE_INDEX


def pic2parts(img_array, num_of_squares):
    div_by = round(num_of_squares ** 0.5)
    if img_array.shape[0] != img_array.shape[1]:
        img_array = resize(img_array)
    squares = []
    for line in np.array(np.split(img_array, div_by)):
        splitted_line = np.split(np.array(line), div_by, axis=1)
        for square in splitted_line:
            squares.append(np.array(square))
    return squares


def get_hue_16(img_array):
    parts = pic2parts(img_array, num_of_squares=16)
    hues = [get_hue(part) for part in parts]
    return hues


def same_hue_16(hue_1, hue_2):
    hue_1, hue_2 = np.array(hue_1), np.array(hue_2)
    return max(np.abs(hue_1 - hue_2)) < MAX_HUE_INDEX
