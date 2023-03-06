import math
import os
from datetime import datetime
from typing import List, Optional, Union, TYPE_CHECKING

import cv2
import numpy as np

from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QResizeEvent, QShowEvent, QPaintEvent, QPainter, QPainterPath, QImage, QMouseEvent, QColor, \
    QTextOption, QFont, QPen
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QFrame, QPushButton, QLabel

from src.global_constants import PATH_TO_LAST_PREVIEW, PROJECT_EXTENSION
from ..LastFileContainer import LastFileProp
from src.core.log import print_d
from src.function_lib.render import np_to_qt_image

if TYPE_CHECKING:
    from src.core.file_system import HomePage


class LastFileGrid(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.home_page: Union[HomePage, QWidget] = self.parent()

        self.setStyleSheet("""
        QScrollArea{
            background-color: transparent;
        }
        QFrame{
            background-color: transparent;
        }
        """)

        self.item_count: int = 0
        self.col_count: int = 5
        self.top_panel: int = 0

        self.grid_container: List[LastFileItem] = []

        self.grid_frame = QFrame()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.grid_frame)
        self.scroll_area.move(0, 0)
        self.scroll_area.resize(self.width(), self.height())
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.call_resize()

    def sort_container(self):
        self.grid_container.sort(key=lambda x: x.prop.last_date, reverse=True)

    def generate_grid(self, props: List[LastFileProp]) -> None:
        self.item_count = len(props)
        for i, widget in enumerate(reversed(self.grid_container)):
            widget.deleteLater()
            self.grid_container.pop(len(self.grid_container) - 1)
        props.reverse()
        for i in range(self.item_count):
            widget = LastFileItem(props[i], self, self.grid_frame)
            widget.setParent(self.grid_frame)
            widget.setVisible(True)
            self.grid_container.append(widget)

        self.sort_container()
        self.call_resize()
        self.update()

    def call_resize(self) -> None:
        self.scroll_area.resize(self.width(), self.height())
        widget_size: QSize = QSize(220, 260)
        loc_col_count: int = max(1, math.ceil(self.width() / widget_size.width()) - 1)
        self.grid_frame.resize(min(loc_col_count * widget_size.width(), self.item_count * widget_size.width()),
                               widget_size.height() * math.ceil(self.item_count / loc_col_count) + self.top_panel)
        for i, widget in enumerate(self.grid_container):
            widget.move(widget_size.width() * (i % loc_col_count),
                        widget_size.height() * (i // loc_col_count) + self.top_panel)

    def update(self) -> None:
        super(LastFileGrid, self).update()

    def call_open_file(self, path: str) -> None:
        self.home_page.mf.open_file(path)

    def clear_background(self):
        for i, widget in enumerate(self.grid_container):
            widget.background_color = widget.colors[0]
            widget.update()


class LastFileItem(QWidget):
    def __init__(self, prop: LastFileProp, parent, *args, **kwargs):
        super(LastFileItem, self).__init__(*args, **kwargs)
        self.prop: LastFileProp = prop
        self.qt_image = self.open_preview()
        self.container: Union[LastFileGrid, QWidget] = parent

        self.setStyleSheet("""
        QLabel#Filename{
            color: #c8c8c8;
            font-family: Arial;
            font-size: 10pt;
        }
        QLabel#Date{
            color: #c8c8c8;
            font-family: Arial;
            font-size: 8pt;
        }
        """)

        self.setMouseTracking(True)

        self.colors: List[QColor] = [QColor("#2D2E2E"), QColor("#494B4B"), QColor("#313D54"), QColor("#27542F")]
        self.background_color: QColor = self.colors[0]
        self.project_color: QColor = self.colors[3]
        self.file_color: QColor = self.colors[2]

        self.resize(200, 240)

        self.is_project_file: bool = os.path.splitext(self.prop.path)[1].lower() == f'.{PROJECT_EXTENSION}'

        self.label_filename = QLabel(os.path.basename(self.prop.path), self)
        self.label_filename.setGeometry(0, self.width() + 5, self.width()-5, 20)
        self.label_filename.setToolTip(os.path.basename(self.prop.path))
        self.label_filename.setObjectName("Filename")

        self.label_last_date = QLabel(datetime.strftime(self.prop.last_date, '%Y-%m-%d %H:%M:%S'), self)
        self.label_last_date.setGeometry(0, self.width() + 25, self.width() - 5, 20)
        self.label_last_date.setObjectName("Date")

    def open_preview(self) -> Optional[QImage]:
        qt_image = None
        if os.path.exists(f'{PATH_TO_LAST_PREVIEW}{self.prop.hash_path}.jpg'):
            image: np.ndarray = cv2.imdecode(np.fromfile(f'{PATH_TO_LAST_PREVIEW}{self.prop.hash_path}.jpg', np.uint8),
                                             cv2.IMREAD_COLOR)
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
            qt_image = np_to_qt_image(image, QImage.Format_RGB888)
        return qt_image

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.container.call_open_file(self.prop.path)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.container.clear_background()
        self.background_color = self.colors[1]
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super(LastFileItem, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        path = QPainterPath()
        margin: int = 0
        path.addRoundedRect(margin, margin, self.width() - margin*2, self.width() - margin*2, 15, 15)
        margin = 15

        painter.fillPath(path, self.background_color)

        if self.qt_image is not None:
            scale = self.qt_image.width() / self.qt_image.height()
            x_shift: int = 0
            y_shift: int = 0
            widget_size = min(self.width(), self.height())
            if scale > 1:
                width = widget_size
                height = widget_size / scale
                y_shift = int(abs(width - height) / 2)
                x_shift = int(abs(width - self.width())/2)
            else:
                width = widget_size * scale
                height = widget_size
                x_shift = (abs(width - height) / 2)
            rect = QRectF(margin + x_shift, margin + y_shift, width - margin*2, height - margin*2)
            painter.drawImage(rect, self.qt_image)

        if self.is_project_file:
            painter.setPen(QPen(self.project_color, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(self.file_color, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)


