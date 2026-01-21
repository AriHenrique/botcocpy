import cv2
import numpy as np


def find_template(screen, template, threshold=0.8, region=None):
    img = cv2.imread(screen, cv2.IMREAD_GRAYSCALE)
    tmp = cv2.imread(template, cv2.IMREAD_GRAYSCALE)

    if img is None or tmp is None:
        raise Exception("Template or screen not found")

    search_img = img
    offset_x = 0
    offset_y = 0

    if region:
        x1, y1, x2, y2 = region
        search_img = img[y1:y2, x1:x2]
        offset_x = x1
        offset_y = y1

    res = cv2.matchTemplate(search_img, tmp, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        return None

    h, w = tmp.shape
    x = max_loc[0] + w // 2 + offset_x
    y = max_loc[1] + h // 2 + offset_y

    return x, y
