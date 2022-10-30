from PyQt5.QtCore import QPoint

from src.core.point_system import Point
from src.enums import CameraModes


class Camera:
    def __init__(self):
        self.position: Point = Point(0, 0)
        self.fix_position: QPoint = QPoint(0, 0)
        self.shift_position: Point = Point(0, 0)
        self.fix_position: QPoint = QPoint(0, 0)
        self.event_position: QPoint = QPoint(0, 0)
        self.scale_factor: float = 1.0
        self.limit: float = 50.0
        self.mode: CameraModes = CameraModes.MOVE
        self.free_control: bool = True
        self.scale_step: float = 10000

    def reset(self):
        self.position = Point(0, 0)
        self.fix_position = QPoint(0, 0)
        self.fix_position = QPoint(0, 0)
