from typing import Union

from PyQt5.QtCore import QPoint
from multipledispatch import dispatch


@dispatch(float, float, float)
def median(a: float, x: float, b: float) -> float:
    return min(max(x, a), b)


@dispatch(int, int, int)
def median(a: int, x: int, b: int) -> int:
    return min(max(x, a), b)


@dispatch(QPoint, QPoint, QPoint)
def median(a: QPoint, x: QPoint, b: QPoint) -> QPoint:
    median_x = min(max(x.x(), a.x()), b.x())
    median_y = min(max(x.y(), a.y()), b.y())
    return QPoint(median_x, median_y)


def fixed_hash(text: str) -> int:
    hash_text = 0
    for ch in text:
        hash_text = (hash_text * 754645 ^ ord(ch) * 32454645) & 0xFAFAFA3434
    return hash_text
