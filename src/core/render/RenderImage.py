from typing import Optional
import numpy as np
import cv2
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage

from src.function_lib import np_to_qt_image, array_to_8bit


class RenderImage:

    def __init__(self, path: Optional[str] = None):
        self.is_valid: bool = path is not None
        self.size: QSize = QSize()
        self.original_image: np.ndarray = np.array([])
        self.buffer: np.ndarray = np.array([])
        self.qt_image: QImage = QImage()
        self.scale_factor: float = 0.0
        self.image_format: QImage.Format = QImage.Format_RGB888

        if path:
            self.init_image(path)

    def init_image(self, path: str) -> None:
        self.original_image: np.ndarray = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
        cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB, self.original_image)
        if self.original_image.ndim == 3:
            height, width, _ = self.original_image.shape
        else:
            height, width = self.original_image.shape
        self.size.setWidth(width)
        self.size.setHeight(height)

        self.qt_image = np_to_qt_image(self.original_image, self.image_format)

        self.is_valid = True

    def update_image(self, scale_val: Optional[float] = None):
        if scale_val is None:
            scale_val = self.scale_factor
        image_width = int(self.size.width() * scale_val)
        image_height = int(self.size.height() * scale_val)
        self.qt_image = np_to_qt_image(self.original_image, self.image_format)
        self.qt_image = self.qt_image.scaled(image_width, image_height, Qt.KeepAspectRatioByExpanding,
                                             Qt.FastTransformation)



