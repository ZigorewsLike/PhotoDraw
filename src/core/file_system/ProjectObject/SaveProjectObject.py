from typing import Tuple, TYPE_CHECKING, Optional

from src.core.render.BufferSettings import BufferSettings
from src.core.render.CorrectionSettings import CorrectionSettings


OBJECT_VERSION: str = "0.0.1"


class SaveProjectObject:
    """
    version: = A.B.C
        If the value has changed:
            A: Not backwards compatible (can't load file)
            B: Weak backwards compatibility (with data loss)
            C: Same support old versions
    """
    version: str
    bytes_array: bytes
    shape_array: Tuple[int, int, int]
    buffer_settings: Optional[BufferSettings] = None
    correction_settings: Optional[CorrectionSettings] = None

    def __init__(self):
        self.version = OBJECT_VERSION

