import math
from typing import List, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QMouseEvent, QFontMetrics, QResizeEvent
from PyQt5.QtWidgets import QWidget, QToolTip, QLabel

from src.core.log import print_d
from src.function_lib import median
from src.core.point_system import Point


class VBoxContainerItem:
    __slots__ = ["widget", "auto_width"]

    def __init__(self, widget: QWidget, auto_width: bool = True):
        self.widget = widget
        self.auto_width = auto_width


class VBoxContainer(QWidget):
    def __init__(self, *args, **kwargs):
        super(VBoxContainer, self).__init__(*args, **kwargs)
        self.padding_left: int = 5
        self.padding_right: int = 5
        self.padding_top: int = 5
        self.padding_bottom: int = 5

        self.setObjectName("VBoxContainer")

        self.setStyleSheet("""
        QWidget#VBoxContainer{
            background: transparent;
        }
        """)

        self._widget_spacing: int = 5

        if self.parent() is not None:
            self.resize(self.parent().width(), self.height())

        self._container: List[VBoxContainerItem] = []
        self._box_height: int = self.padding_top

    def add_widget(self, widget: QWidget, auto_width: bool = True) -> None:
        widget.setParent(self)
        widget.move(self.padding_left, self._box_height)
        self._box_height += widget.height() + self._widget_spacing
        item = VBoxContainerItem(widget, auto_width)
        self._container.append(item)
        self.resize(self.width(), self._box_height + self.padding_bottom)

    def recalculate_positions(self) -> None:
        self._box_height: int = self.padding_top
        for item in self._container:
            item.widget.move(self.padding_left, self._box_height)
            self._box_height += item.widget.height() + self._widget_spacing
        self.resize(self.width(), self._box_height + self.padding_bottom)

    def set_width(self, width: int) -> None:
        self.resize(width, self._box_height + self.padding_bottom)

    def set_widget_spacing(self, spacing) -> None:
        self._widget_spacing = spacing
        self.recalculate_positions()

    def set_paddings(self, left: Optional[int] = None, top: Optional[int] = None, right: Optional[int] = None,
                     bottom: Optional[int] = None) -> None:
        if left is not None:
            self.padding_left = left
        if top is not None:
            self.padding_top = top
        if right is not None:
            self.padding_right = right
        if bottom is not None:
            self.padding_bottom = bottom
        self.recalculate_positions()


    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        for item in self._container:
            if item.auto_width:
                item.widget.resize(self.width() - self.padding_left - self.padding_right, item.widget.height())

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        # painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#456754")))