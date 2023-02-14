import cv2
import copy

from .CorrectionLevels import CorrectionLevels


class CorrectionSettings:
    def __init__(self):
        self.levels = CorrectionLevels()
        self.bright: float = 1.0
        self.contrast: int = 255
        self.saturation: float = 1.0
        self.color_mode = cv2.COLOR_BGR2RGB
        self.device = 'GPU'

    def reset(self):
        self.__init__()

    def copy(self):
        return copy.deepcopy(self)
