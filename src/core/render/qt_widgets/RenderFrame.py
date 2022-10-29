from typing import TYPE_CHECKING, Union

from PyQt5.QtCore import QRectF, Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QBrush, QMouseEvent, QWheelEvent, QResizeEvent, QTextOption, \
    QFont
from PyQt5.QtWidgets import QWidget, QOpenGLWidget, QScrollBar

from core.log import print_i
from src.global_constants import DEBUG
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

        self.setStyleSheet("""
        QScrollBar{
            background-color: #333333;
            color: black;
        }
        QWidget#Empty{
            background-color: #333333;
        }
        """)

        self.scroll_size: int = 15

        self.vertical_scroll_bar = QScrollBar(self)
        self.vertical_scroll_bar.setMaximum(100)
        self.vertical_scroll_bar.setMinimum(0)
        self.vertical_scroll_bar.setValue(0)
        self.vertical_scroll_bar.valueChanged.connect(self.vertical_scroll_change)

        self.horizontal_scroll_bar = QScrollBar(Qt.Horizontal, self)
        self.horizontal_scroll_bar.setMaximum(100)
        self.horizontal_scroll_bar.setMinimum(0)
        self.horizontal_scroll_bar.setValue(0)
        self.horizontal_scroll_bar.valueChanged.connect(self.horizontal_scroll_change)

        self.empty_rect = QWidget(self)
        self.empty_rect.setObjectName("Empty")
        self.empty_rect.resize(self.scroll_size, self.scroll_size)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(RenderFrame, self).resizeEvent(event)
        self.vertical_scroll_bar.resize(self.scroll_size, self.height() - self.scroll_size)
        self.vertical_scroll_bar.move(self.width() - self.scroll_size, 0)

        self.horizontal_scroll_bar.resize(self.width() - self.scroll_size, self.scroll_size)
        self.horizontal_scroll_bar.move(0, self.height() - self.scroll_size)

        self.empty_rect.move(self.width() - self.scroll_size, self.height() - self.scroll_size)

    # region ScrollBar functions
    def show_scroll_bars(self, visible: bool = True) -> None:
        if self.vertical_scroll_bar.isVisible() != visible:
            self.vertical_scroll_bar.setVisible(visible)
            self.horizontal_scroll_bar.setVisible(visible)
            self.empty_rect.setVisible(visible)
            if visible:
                self.scroll_value_update(True)

    def scroll_value_update(self, update_max: bool = False) -> None:
        if self.horizontal_scroll_bar.isVisible():
            self.horizontal_scroll_bar.setValue(max(0, -self.mf.camera.position.ix))
            self.vertical_scroll_bar.setValue(max(0, -self.mf.camera.position.iy))
            if update_max:
                self.vertical_scroll_bar.setMaximum(
                    int(self.mf.render_image.size.height() * self.mf.camera.scale_factor - self.height()))
                self.horizontal_scroll_bar.setMaximum(
                    int(self.mf.render_image.size.width() * self.mf.camera.scale_factor - self.width()))
                self.vertical_scroll_bar.setMinimum(0)
                self.horizontal_scroll_bar.setMinimum(0)

    @pyqtSlot()
    def vertical_scroll_change(self):
        self.mf.camera.position.y = -self.vertical_scroll_bar.value()
        self.call_update()

    @pyqtSlot()
    def horizontal_scroll_change(self):
        self.mf.camera.position.x = -self.horizontal_scroll_bar.value()
        self.call_update()
    # endregion

    def call_update(self):
        self.mf.adjust_camera_position()
        if self.mf.camera.position != self.mf.render_image.shift_pos:
            self.mf.update_buffer(self.mf.camera.position)
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        # self.mf.open_file_dialog()
        pass

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_press = True
            if self.mf.render_image.is_valid:
                if self.mf.camera.mode is CameraModes.MOVE:
                    self.mf.camera.fix_position = event.pos() - self.mf.camera.position.qt()
                    if self.mf.camera.scale_factor < 1.0:
                        self.mf.render_image.buffer_settings.render_scale = 2
                    self.mf.render_image.scale_buffer()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.x() > 0 and event.y() > 0:
            if DEBUG:
                self.mf.label_mouse_pos.setText(f"Camera pos {self.mf.camera.position.ix}:{self.mf.camera.position.iy}")
            else:
                self.mf.label_mouse_pos.setText(f"Mouse pos {event.x()}:{event.y()}")
            self.mf.label_mouse_pos.adjustSize()
            self.mf.camera.event_position = event.pos()
        if self.mouse_press and self.mf.render_image.is_valid:
            if self.mf.camera.mode is CameraModes.MOVE:
                if self.mf.camera.free_control:
                    self.mf.camera.position.convert(event.pos() - self.mf.camera.fix_position)
                    self.scroll_value_update()
                    self.call_update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouse_press = False
        if event.button() == Qt.LeftButton:
            if self.mf.render_image.is_valid:
                if self.mf.camera.mode is CameraModes.MOVE:
                    self.mf.render_image.buffer_settings.render_scale = 1
                    self.mf.render_image.scale_buffer()
                    self.call_update()

    def paintEvent(self, event: QPaintEvent) -> None:
        # !! OpenGL Warning
        # !! State changes are expensive, so make sure you batch the operations that use the same pen/brush etc. !!
        painter = QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(0x01)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # painter.scale(0.75, 0.75)

        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#111111")))

        if self.mf.render_image.is_valid:
            img_pos_x: int = 0
            img_pos_y: int = 0

            if self.mf.render_image.buffer_size.left < 0:
                img_pos_x = -self.mf.render_image.buffer_size.left
            if self.mf.render_image.buffer_size.top < 0:
                img_pos_y = -self.mf.render_image.buffer_size.top

            painter.drawImage(img_pos_x, img_pos_y, self.mf.render_image.qt_image)
        else:
            option = QTextOption(Qt.AlignCenter)
            font = QFont('Arial', 20)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#c8c8c8"))
            text_rect = QRectF(self.width()//2 - 200, self.height()//2 - 20, 400, 40)
            # painter.drawRect(text_rect)
            painter.drawText(text_rect, "Открыть файл (Ctrl+O)", option)
        painter.end()

    def wheelEvent(self, event: QWheelEvent):
        if self.mf.render_image.is_valid:
            new_scale = self.mf.camera.scale_factor + event.angleDelta().y() / self.mf.camera.scale_step
            if new_scale > 0:
                self.mf.scale_image(new_scale)

