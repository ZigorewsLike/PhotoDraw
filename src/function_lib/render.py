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
    pos = np.array([i for i in range(array[:, :, channel].flatten().min(), array[:, :, channel].flatten().max())])
    return pos, counts


