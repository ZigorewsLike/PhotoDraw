from math import sqrt
from multipledispatch import dispatch

from PyQt5.QtCore import QPoint


class Point:
    def __init__(self, x: float = 0., y: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.scale_val = 1

    def __add__(self, other):
        if type(other) != Point:
            return Point(self.x + other, self.y + other)
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        if type(other) != Point:
            return Point(self.x - other, self.y - other)
        return Point(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        return self - other

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __truediv__(self, other):
        if type(other) != Point:
            return Point(self.x / other, self.y / other)
        return Point(self.x / other.x, self.y / other.y)

    def __mul__(self, other):
        if type(other) != Point:
            return Point(self.x * other, self.y * other)
        return Point(self.x * other.x, self.y * other.y)

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __lt__(self, other):
        if type(other) != Point:
            return self.x < other and self.y < other
        return self.x < other.x and self.y < other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y

    def __round__(self, n=None):
        point = self.copy()
        point.x = round(point.x, n)
        point.y = round(point.y, n)
        return point

    def __neg__(self):
        return Point(-self.x, -self.y)

    def convert(self, point: QPoint):
        self.x = float(point.x())
        self.y = float(point.y())

    def qt(self):
        return QPoint(self.x, self.y)

    # Length between points
    def lbp(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_list(self):
        return [self.x, self.y]

    def to_list_2d(self):
        return [self.x, self.y]

    def scale(self, val):
        self.scale_val = val

    def get_x(self):
        return self.x * self.scale_val

    def get_y(self):
        return self.y * self.scale_val

    def copy(self):
        point = Point(self.x, self.y)
        point.scale_val = self.scale_val
        return point

    def set_shift(self, shift_point):
        self.x += shift_point.x
        self.y += shift_point.y

    @property
    def ix(self) -> int:
        """
        `self.x` as int
        :return: int
        """
        return int(self.x)

    @property
    def iy(self) -> int:
        """
        `self.y` as int
        :return: int
        """
        return int(self.y)


# Future use
class Point3d:
    def __init__(self, x=0., y=0., z=0.):
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __str__(self):
        return f"Point3d({self.x}, {self.y}, {self.z})"

    def __truediv__(self, other):
        if not isinstance(other, Point3d):
            return Point3d(self.x / other, self.y / other, self.z / other)
        return Point3d(self.x / other.x, self.y / other.y, self.z / other.z)

    def __itruediv__(self, other):
        if not isinstance(other, Point3d):
            return Point3d(self.x / other, self.y / other, self.z / other)
        return Point3d(self.x / other.x, self.y / other.y, self.z / other.z)

    def from_str(self, string: str) -> None:
        string_array = string.replace("Point3d(", "").replace(")", "").split(', ')
        self.x, self.y, self.z = [float(val) for val in string_array]


@dispatch(Point, Point)
def lbp(point1: Point, point2: Point) -> float:
    """
    Length between two points
    :param point1: Point
    :param point2: Point
    :return: float
    """
    return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


@dispatch(QPoint, QPoint)
def lbp(point1: QPoint, point2: QPoint) -> float:
    """
    Length between two points
    :param point1: QPoint
    :param point2: QPoint
    :return: float
    """
    return sqrt((point1.x() - point2.x()) ** 2 + (point1.y() - point2.y()) ** 2)
