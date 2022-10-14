import numpy as np
from PyQt5.QtGui import QImage


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


def array_to_8bit(array: np.ndarray, array_max: float, array_min: float = 0) -> np.ndarray:
    array = array.astype(np.float16)
    if array_max == 0:
        array_max = array.max()
    array = (array - array_min)
    array = (array / (array_max - array_min) * (2**8 - 1))
    array[array > 255] = 255
    array[array < 0.0] = 0.0
    return array.astype(np.uint8)


