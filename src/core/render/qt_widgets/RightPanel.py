from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from .correction_panels.ImageCorrection import ImageCorrection


class RightPanelWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(RightPanelWidget, self).__init__(*args, **kwargs)
        self.mf: MainForm = main_form
        self.resize(200, 500)

        self.line_width: int = 10
        self.resize_mode: bool = False
        self.old_cursor_pos: QPoint = QPoint()

        self.image_correction_widget = ImageCorrection(self.mf, self)

        self.move_line_frame = QFrame(self)
        self.move_line_frame.setFrameShape(QFrame.VLine)
        self.move_line_frame.setFrameShadow(QFrame.Sunken)
        self.move_line_frame.setCursor(QCursor(Qt.SplitHCursor))

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(RightPanelWidget, self).resizeEvent(event)
        self.mf.size_collector.right_panel = self.width()
        self.move_line_frame.resize(self.line_width, self.height())
        self.image_correction_widget.resize(self.width() - self.line_width, self.image_correction_widget.height())
        self.image_correction_widget.move(self.line_width, 0)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if 0 <= event.x() <= self.line_width and 0 <= event.y() <= self.height():
            self.resize_mode = True
            self.old_cursor_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.resize_mode = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.resize_mode:
            sub_x = min(self.old_cursor_pos.x() - event.x(), self.mf.width() - self.width() - 400)
            if self.mf.width() + sub_x > self.width() + sub_x > 200:
                self.resize(self.width() + sub_x, self.height())
                self.move(self.x() - sub_x, self.y())
                self.mf.size_collector.right_panel = self.width()
                self.mf.recalculate_size()

