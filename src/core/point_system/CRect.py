"""
Custom Rect class
"""

from .Point import Point
from PyQt5.QtCore import QPoint


class CRect:
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.left_side: int = x
        self.top_side: int = y
        self.width: int = width
        self.height: int = height
        self.right_side: int = width + self.left_side
        self.bottom_side: int = height + self.top_side
        self.shift_pos: Point = Point(0., 0.)

    @classmethod
    def from_sides(cls, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        return cls(left, top, right - left, bottom - top)

    def __str__(self):
        return f"left: {self.left_side}; right: {self.right_side}; top: {self.top_side}; bottom: {self.bottom_side}"

    def __iter__(self):
        return iter([min(self.left_side, self.right_side), min(self.top_side, self.bottom_side), self.width, self.height])

    def copy(self):
        copy_box = CRect(self.left_side, self.top_side, self.width, self.height)
        copy_box.shift_pos = self.shift_pos.copy()
        return copy_box

    def reset(self):
        self.left_side, self.right_side, self.top_side, self.bottom_side, self.width, self.height = 0, 0, 0, 0, 0, 0
        self.shift_pos = Point()

    def shift(self, pos: Point):
        self.left_side += int(pos.x - self.shift_pos.x)
        self.right_side += int(pos.x - self.shift_pos.x)
        self.top_side += int(pos.y - self.shift_pos.y)
        self.bottom_side += int(pos.y - self.shift_pos.y)
        self.shift_pos = pos.copy()

    def get_size(self):
        return self.width, self.height

    # region get/set left, right, top, bottom
    @property
    def right(self):
        return self.right_side

    @right.setter
    def right(self, val: int):
        self.right_side = val
        self.width = abs(self.right_side - self.left_side)

    @property
    def bottom(self):
        return self.bottom_side

    @bottom.setter
    def bottom(self, val: int):
        self.bottom_side = val
        self.height = abs(self.bottom_side - self.top_side)

    @property
    def top(self):
        return self.top_side

    @top.setter
    def top(self, val: int):
        self.top_side = val
        self.height = abs(self.bottom_side - self.top_side)

    @property
    def left(self):
        return self.left_side

    @left.setter
    def left(self, val: int):
        self.left_side = val
        self.width = abs(self.right_side - self.left_side)
    # endregion

    @property
    def area(self):
        return self.width * self.height

    @property
    def fp(self) -> [int, int]:
        """
        First point (left, top)
        :return: [left, top] or [x, y]
        """
        return [self.left_side, self.top_side]

    @fp.setter
    def fp(self, point: QPoint):
        self.left_side, self.top_side = point.x(), point.y()

    @property
    def sp(self) -> [int, int]:
        """
        Second point (right, bottom)
        :return: [right, bottom] or [x + w, y + h]
        """
        return [self.right_side, self.bottom_side]

    @sp.setter
    def sp(self, point: QPoint):
        self.right_side, self.bottom_side = point.x(), point.y()
        self.width = abs(self.right_side - self.left_side)
        self.height = abs(self.bottom_side - self.top_side)
