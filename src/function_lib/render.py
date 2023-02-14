from typing import Tuple

import numpy as np
from PyQt5.QtGui import QImage

from src.core.point_system import CRect
from .math import median


def np_to_qt_image(array: np.ndarray, image_format: QImage.Format) -> QImage:
    if array.ndim == 3:
        height, width, byte_value = array.shape
    else:
        height, width = array.shape
        byte_value = 1
    byte_value = byte_value * width
    if byte_value == 1:
        return QImage(array, width, height, image_format)
    return QImage(array, width, height, byte_value, image_format)


def get_part(slice_box: CRect, image: np.ndarray, factor: float, step: int) -> np.ndarray:
    x = median(0, int(slice_box.left / factor), image.shape[1])
    y = median(0, int(slice_box.top / factor), image.shape[0])
    y2 = median(0, int(slice_box.bottom / factor), image.shape[0])
    x2 = median(0, int(slice_box.right / factor), image.shape[1])
    return image[y:y2:step, x:x2:step].copy()


def array_to_8bit(array: np.ndarray, array_max: float, array_min: float = 0) -> np.ndarray:
    array = array.astype(np.float16)
    if array_max == 0:
        array_max = array.max()
    array = (array - array_min)
    array = (array / (array_max - array_min) * (2**8 - 1))
    array[array > 255] = 255
    array[array < 0.0] = 0.0
    return array.astype(np.uint8)


def get_unique(array: np.ndarray, channel: int) -> Tuple[np.ndarray, np.ndarray]:
    counts = np.bincount(array[:, :, channel].flatten())
    pos = np.array([i for i in range(array[:, :, channel].flatten().min(), array[:, :, channel].flatten().max() + 1)])
    return pos, counts


def rgb_to_hsl(r: int, g: int, b: int) -> (int, int, int):
    # Works with floats between 0 and 255
    r /= 255.0
    g /= 255.0
    b /= 255.0
    max_color: float = max(r, max(g, b))
    min_color: float = min(r, min(g, b))

    if r == g == b:
        h: float = 0
        s: float = 0
        l: float = r
    else:
        d: float = max_color - min_color
        l: float = (min_color + max_color) / 2
        s = d / (max_color + min_color) if l < 0.5 else d / (2.0 - max_color - min_color)
        if r == max_color:
            h = (g - b) / (max_color - min_color)
        elif g == max_color:
            h = 2.0 + (b - r) / (max_color - min_color)
        else:
            h = 4.0 + (r - g) / (max_color - min_color)
        h /= 6.0
        if h < 0:
            h += 1
    return int(h * 360.0), int(s * 255.0), int(l * 255.0)


def hsl_to_rgb(h: int, s: int, l: int) -> (int, int, int):
    def chanel_conversion(temp_ch: float) -> float:
        nonlocal temp1, temp2
        if temp_ch < 1.0 / 6.0:
            res = temp1 + (temp2 - temp1) * 6.0 * temp_ch
        elif temp_ch < 0.5:
            res = temp2
        elif temp_ch < 2.0 / 3.0:
            res = temp1 + (temp2 - temp1) * ((2.0 / 3.0) - temp_ch) * 6.0
        else:
            res = temp1
        return res

    h = (h % 260) / 360.0
    s = s / 256.0
    l = l / 256.0

    if s == 0:
        r = l
        g = l
        b = l
    else:
        # Set the temporary values
        if l < 0.5:
            temp2 = l * (1 + s)
        else:
            temp2 = (l + s) - (l * s)
        temp1 = 2 * l - temp2

        temp_r = h + 1.0 / 3.0
        if temp_r > 1:
            temp_r -= 1
        temp_g = h
        temp_b = h - 1.0 / 3.0
        if temp_b < 0:
            temp_b += 1

        r = chanel_conversion(temp_r)
        g = chanel_conversion(temp_g)
        b = chanel_conversion(temp_b)

    return int(r * 255), int(g * 255), int(b * 255)


vector_rgb_to_hsl = np.vectorize(rgb_to_hsl)
vector_hsl_to_rgb = np.vectorize(hsl_to_rgb)

