from typing import TYPE_CHECKING, Union

from PyQt5.QtCore import QRectF, Qt, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QBrush, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget

from src.core.render.Camera import CameraModes
from src.core.point_system import Point
from src.function_lib import median

if TYPE_CHECKING:
    from forms.MainForm import MainForm


class RenderFrame(QWidget):

    def __init__(self, *args, **kwargs):
        super(RenderFrame, self).__init__(*args, **kwargs)
        self.mf: Union[MainForm, QWidget] = self.parent()
        self.setMouseTracking(True)
        self.mouse_press: bool = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_press = True
            if self.mf.camera.mode is CameraModes.MOVE:
                self.mf.camera.event_position = event.pos()
                self.mf.camera.fix_position = self.mf.camera.position.qt()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.x() > 0 and event.y() > 0:
            self.mf.label_mouse_pos.setText(f"Mouse pos {event.x()}:{event.y()}")
            self.mf.label_mouse_pos.adjustSize()
        if self.mouse_press:
            if self.mf.camera.mode is CameraModes.MOVE:
                self.mf.camera.position = Point.from_qt(event.pos() - self.mf.camera.event_position +
                                                        self.mf.camera.fix_position)
                self.mf.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouse_press = False
        if event.button() == Qt.LeftButton:
            self.mf.camera.event_position = event.pos()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#111111")))

        if self.mf.render_image.is_valid:
            painter.drawImage(self.mf.camera.position.ix, self.mf.camera.position.iy, self.mf.render_image.qt_image)

    def wheelEvent(self, event: QWheelEvent):
        self.mf.scale_image(self.mf.camera.scale_factor + event.angleDelta().y() / 1000)

