import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent, QShowEvent, QPaintEvent, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QFrame, QPushButton


class LastFileGrid(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet("""
        QScrollArea{
            background-color: transparent;
        }
        QFrame{
            background-color: transparent;
        }
        """)

        self.item_count: int = 13
        self.col_count: int = 5

        self.grid_layer = QGridLayout()

        self.grid_frame = QFrame()
        self.grid_frame.setLayout(self.grid_layer)
        self.grid_layer.setContentsMargins(10, 10, 10, 10)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.grid_frame)
        self.scroll_area.move(0, 0)
        self.scroll_area.resize(self.width(), self.height())
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in range(self.item_count):
            widget = LastFileItem()
            self.grid_layer.addWidget(widget, i // self.col_count, i % self.col_count)

    def showEvent(self, event: QShowEvent) -> None:
        self.call_resize()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.call_resize()

    def call_resize(self):
        self.scroll_area.resize(self.width(),  self.height())
        width: float = 220.0
        loc_col_count: int = math.ceil(self.width() / 250)
        if loc_col_count != self.col_count:
            for i in reversed(range(self.grid_layer.count())):
                widget = self.grid_layer.itemAt(i)
                self.grid_layer.removeItem(widget)
                self.grid_layer.addWidget(widget.widget(), i // loc_col_count, i % loc_col_count)
        self.col_count = loc_col_count
        if self.grid_layer.count() > 0:
            width = (self.width() - 20) / self.col_count
        if self.scroll_area.verticalScrollBar().isVisible():
            self.grid_frame.resize(self.width() - self.scroll_area.verticalScrollBar().width(),
                                   int(math.ceil(self.item_count / self.col_count) * width))
        else:
            self.grid_frame.resize(self.width(), int(math.ceil(self.item_count / self.col_count) * width))


class LastFileItem(QWidget):
    def __init__(self, *args, **kwargs):
        super(LastFileItem, self).__init__(*args, **kwargs)

        self.resize(200, 200)

    def paintEvent(self, event: QPaintEvent) -> None:
        super(LastFileItem, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.begin(self)

        path = QPainterPath()
        margin: int = 5
        path.addRoundedRect(margin, margin, self.width() - margin*2, self.height() - margin*2, 10, 10)

        painter.fillPath(path, Qt.gray)
        painter.end()


