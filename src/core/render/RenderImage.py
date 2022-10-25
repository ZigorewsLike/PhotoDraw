from typing import Optional
import numpy as np
import cv2
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage

from src.core.log import print_d
from src.core.point_system import CRect, Point
from src.function_lib import np_to_qt_image, get_part
from .BufferSettings import BufferSettings


class RenderImage:

    def __init__(self, path: Optional[str] = None):
        self.is_valid: bool = path is not None
        self.size: QSize = QSize()
        self.original_image: np.ndarray = np.array([])
        self.buffer: np.ndarray = np.array([])
        self.buffer_size: CRect = CRect(0, 0, 500, 500)
        self.buffer_settings: BufferSettings = BufferSettings()
        self.shift_pos: Point = Point(self.buffer_size.width,
                                      self.buffer_size.height)
        self.qt_image: QImage = QImage()
        self.camera_scale_factor: float = 1.0
        self.scale_factor: float = 1.0
        self.scale_ratio: int = 1
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

        self.is_valid = True

    def scale_buffer(self, scale_val: Optional[float] = None, camera_pos: Optional[Point] = None,
                     update_buffer: bool = True):
        if scale_val is not None:
            self.camera_scale_factor = scale_val
        self.scale_ratio = max(1, int(1 / self.camera_scale_factor)) * self.buffer_settings.render_scale
        self.scale_factor = float(self.camera_scale_factor * self.scale_ratio)
        if update_buffer:
            self.update_buffer(camera_pos)

    def update_buffer(self, camera_pos: Optional[Point] = None):
        if self.is_valid:
            if camera_pos is not None:
                self.shift_pos = camera_pos.copy()
                self.buffer_size.shift(-camera_pos)

            self.buffer = get_part(self.buffer_size, self.original_image, self.camera_scale_factor, self.scale_ratio)
            image_width = int(self.buffer.shape[1] * self.scale_factor)
            image_height = int(self.buffer.shape[0] * self.scale_factor)
            if image_height > 0 and image_width > 0:
                resampling = cv2.INTER_CUBIC if self.buffer_settings.resampling else cv2.INTER_NEAREST
                self.buffer = cv2.resize(self.buffer, (image_width, image_height), interpolation=resampling)
                pass

            self.qt_image = np_to_qt_image(self.buffer, self.image_format)