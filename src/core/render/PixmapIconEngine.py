from PyQt5.QtCore import QRect, QSize, Qt, QPoint
from PyQt5.QtGui import QIconEngine, QPainter, QIcon, QImage, QPixmap


class PixmapIconEngine(QIconEngine):
    def __init__(self, path: str):
        self.path = path
        super().__init__()

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.drawImage(rect, QImage(self.path))

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        self.paint(QPainter(pixmap), QRect(QPoint(0, 0), size), mode, state)
        return pixmap
