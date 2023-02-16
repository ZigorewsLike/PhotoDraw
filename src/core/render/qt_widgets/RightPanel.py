from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QResizeEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from .correction_panels.ImageCorrection import ImageCorrection
from .LayerContainerWidget import LayerContainerWidget
from src.function_lib import median


class RightPanelWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(RightPanelWidget, self).__init__(*args, **kwargs)
        self.mf: MainForm = main_form
        self.resize(self.mf.size_collector.right_panel, 500)
        self.min_width: int = self.mf.size_collector.right_panel

        self.line_width: int = 10
        self.widget_margin: int = 15
        self.resize_mode: bool = False
        self.old_cursor_pos: QPoint = QPoint()

        self.image_correction_widget = ImageCorrection(self.mf, self)
        self.layer_container_widget = LayerContainerWidget(self.mf, self)

        self.move_line_frame = QFrame(self)
        self.move_line_frame.setFrameShape(QFrame.VLine)
        # self.move_line_frame.setFrameShadow(QFrame.Sunken)
        self.move_line_frame.setCursor(QCursor(Qt.SplitHCursor))
        self.move_line_frame.setStyleSheet("""
        QFrame[frameShape="5"]
        {
            color: #989D9B;
        }
        """)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(RightPanelWidget, self).resizeEvent(event)
        self.mf.size_collector.right_panel = self.width()
        self.move_line_frame.resize(self.line_width, self.height())
        self.image_correction_widget.resize(self.width() - self.line_width, self.image_correction_widget.height())
        self.layer_container_widget.resize(self.width() - self.line_width, self.layer_container_widget.height())
        self.image_correction_widget.move(self.line_width, 0)
        self.layer_container_widget.move(self.line_width, self.image_correction_widget.height() + self.widget_margin)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if 0 <= event.x() <= self.line_width and 0 <= event.y() <= self.height():
            self.resize_mode = True
            self.old_cursor_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.resize_mode = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.resize_mode:
            sub_x = min(self.old_cursor_pos.x() - event.x(), self.mf.width() - self.width() - 400)
            # self.resize(self.width() + sub_x, self.height())
            self.resize(median(self.min_width, self.width() + sub_x, self.mf.width() + sub_x), self.height())
            self.move(self.x() - sub_x, self.y())
            self.mf.size_collector.right_panel = self.width()
            self.mf.recalculate_size(call_buffer_update=True, call_buffer_scale=False)

