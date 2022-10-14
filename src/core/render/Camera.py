from PyQt5.QtCore import QPoint

from src.core.point_system import Point
from src.enums import CameraModes


class Camera:
    def __init__(self):
        self.position: Point = Point(0, 0)
        self.fix_position: QPoint = QPoint(0, 0)
        self.event_position: QPoint = QPoint(0, 0)
        self.scale_factor: float = 1.0
        self.mode: CameraModes = CameraModes.MOVE

    def reset(self):
        self.position = Point(0, 0)
        self.fix_position = QPoint(0, 0)
        self.event_position = QPoint(0, 0)
