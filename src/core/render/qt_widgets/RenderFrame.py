from typing import TYPE_CHECKING, Union

from PyQt5.QtCore import QRectF, Qt, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QBrush, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget

from src.core.log import print_d
from src.core.render.Camera import CameraModes
from src.core.point_system import Point
from src.function_lib import median

if TYPE_CHECKING:
    from forms.MainForm import MainForm


class RenderFrame(QOpenGLWidget):

    def __init__(self, *args, **kwargs):
        super(RenderFrame, self).__init__(*args, **kwargs)
        self.mf: Union[MainForm, QWidget] = self.parent()
        self.setMouseTracking(True)
        self.mouse_press: bool = False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.mf.open_file_dialog()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_press = True
            if self.mf.render_image.is_valid:
                if self.mf.camera.mode is CameraModes.MOVE:
                    self.mf.camera.event_position = event.pos() - self.mf.camera.position.qt()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.x() > 0 and event.y() > 0:
            self.mf.label_mouse_pos.setText(f"Mouse pos {event.x()}:{event.y()}")
            self.mf.label_mouse_pos.adjustSize()
        if self.mouse_press and self.mf.render_image.is_valid:
            if self.mf.camera.mode is CameraModes.MOVE:
                self.mf.camera.position.convert(event.pos() - self.mf.camera.event_position)
                # new_pos: Point = Point.from_qt(event.pos() - self.mf.camera.event_position +
                #                                self.mf.camera.fix_position)
                # self.mf.camera.position = new_pos
                if self.mf.camera.position != self.mf.render_image.shift_pos:
                    self.mf.render_image.update_buffer(self.mf.camera.position)
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouse_press = False
        if event.button() == Qt.LeftButton:
            if self.mf.render_image.is_valid:
                if self.mf.camera.mode is CameraModes.MOVE:
                    # self.mf.camera.event_position = event.pos()
                    # if self.mf.camera.position != self.mf.render_image.shift_pos:
                    #     self.mf.render_image.update_buffer(self.mf.camera.position)
                    self.mf.render_image.update_buffer(self.mf.camera.position)
                    self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        # !! OpenGL Warning
        # !! State changes are expensive, so make sure you batch the operations that use the same pen/brush etc. !!
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#111111")))

        if self.mf.render_image.is_valid:
            img_pos_x: int = 0
            img_pos_y: int = 0

            # img_pos_x: int = self.mf.camera.position.ix - self.mf.render_image.shift_pos.ix
            # img_pos_y: int = self.mf.camera.position.iy - self.mf.render_image.shift_pos.iy
            if self.mf.render_image.buffer_size.left < 0:
                img_pos_x = -self.mf.render_image.buffer_size.left
            if self.mf.render_image.buffer_size.top < 0:
                img_pos_y = -self.mf.render_image.buffer_size.top
            # painter.drawImage(self.mf.camera.position.ix, self.mf.camera.position.iy, self.mf.render_image.qt_image)
            # img_width: int = self.mf.render_image.buffer.shape[1] * self.mf.render_image.scale_factor
            # img_height: int = self.mf.render_image.buffer.shape[0] * self.mf.render_image.scale_factor
            # rect: QRectF = QRectF(img_pos_x, img_pos_y, img_width, img_height)

            painter.drawImage(img_pos_x, img_pos_y, self.mf.render_image.qt_image)
            # painter.drawImage(rect, self.mf.render_image.qt_image)

    def wheelEvent(self, event: QWheelEvent):
        if self.mf.render_image.is_valid:
            self.mf.scale_image(self.mf.camera.scale_factor + event.angleDelta().y() / 1000)

