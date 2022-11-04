import cv2

from .CorrectionLevels import CorrectionLevels


class CorrectionSettings:
    def __init__(self):
        self.levels = CorrectionLevels()
        self.bright: float = 1.0
        self.contrast: int = 255
        self.color_mode = cv2.COLOR_BGR2RGB
        self.device = 'GPU'
