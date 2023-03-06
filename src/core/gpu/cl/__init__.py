import os
import numpy as np

from src.core.log import print_e, print_d

try:
    os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
    from .get_info import print_all_device_info
    from .bright_contrast import set_bright_contrast
    from .levels import set_levels

    OPENCL_ENABLED: bool = True
except Exception as e:
    print_e(e)
    OPENCL_ENABLED: bool = False

if not OPENCL_ENABLED:

    # region get_info.py
    def print_all_device_info() -> None:
        """
        Print all gpu device info
        """
        pass
    # endregion

    # region bright_contrast.py
    def set_bright_contrast(image: np.ndarray, bright: float, contrast: float) -> np.ndarray:
        pass
    # endregion

    # region levels.py
    def set_levels(image: np.ndarray, max_v: int, min_v: int, mid_v: int, gamma: float, other_max_v: int,
                   other_min_v: int) -> np.ndarray:
        pass
    # endregion

