from skimage.metrics import structural_similarity
import cv2
from API.image_processing.resize import load_resized_matrix

MIN_SSIM_INDEX = 0.2


def get_ssim(im1, im2):
    im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    score, _ = structural_similarity(im1, im2, full=True)
    return score


def high_ssim(resized_img_path, resized_matrix):
    return get_ssim(load_resized_matrix(resized_img_path), resized_matrix) >= MIN_SSIM_INDEX
