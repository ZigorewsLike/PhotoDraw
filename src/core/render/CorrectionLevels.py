import numpy as np

from src.core.gpu.cl import OPENCL_ENABLED, set_levels


class CorrectionLevels:
    def __init__(self, min_v=0, max_v=255, gamma=1):
        self.gamma = gamma
        self.gamma_correction = 0
        self.max_v = max_v
        self.min_v = min_v
        self.mid_tone = 128
        self.calc_gamma_correction()

    def copy(self):
        return CorrectionLevels(self.min_v, self.max_v, self.gamma)

    def __ne__(self, other):
        return self.max_v != other.max_v or self.min_v != other.min_v or self.gamma != other.gamma or \
               self.mid_tone != other.mid_tone

    def calc_gamma_correction(self):
        mid_tone_norm = self.mid_tone / 255
        if self.mid_tone < 128:
            mid_tone_norm *= 2
            self.gamma = 1 + (9 * (1 - mid_tone_norm))
            self.gamma = min(self.gamma, 9.99)
        elif self.mid_tone > 128:
            mid_tone_norm = (mid_tone_norm * 2) - 1
            self.gamma = 1 - mid_tone_norm
            self.gamma = max(self.gamma, 0.01)
        self.gamma_correction = 1 / self.gamma

    # TODO: create Enum device. apply_correction(self, img: np.ndarray, min_v, max_v, `device`)
    def apply_correction(self, img: np.ndarray, min_v, max_v) -> np.ndarray:
        self.calc_gamma_correction()
        if OPENCL_ENABLED:
            return set_levels(img, self.max_v, self.min_v, self.mid_tone, self.gamma_correction, max_v,
                              min_v).astype(np.int8)
        else:
            img = img.astype(int)
            sub = (img - self.min_v)
            sub[sub < 0] = 0
            img = 255 * (sub / (self.max_v - self.min_v))
            img[img > 255] = 255
            if self.mid_tone != 128:
                img = 255 * ((img / 255) ** self.gamma_correction)
                img[img > 255] = 255
            img = img.astype(np.int8)
            img = (img / 255) * (max_v - min_v) + min_v
            img[img > 255] = 255
            return img.astype(np.uint8)
