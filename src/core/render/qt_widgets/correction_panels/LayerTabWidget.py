from typing import TYPE_CHECKING, List, Tuple

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QResizeEvent
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame, QPushButton, \
    QScrollArea

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.global_style_sheets import TAB_STYLE, SCROLL_AREA


class LayerTabWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(LayerTabWidget, self).__init__(*args, **kwargs)
        self.setStyleSheet("""
        %s
        """ % SCROLL_AREA)

        self.mf: MainForm = main_form

        self.layer_frame = QFrame()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.layer_frame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.scroll_area.resize(self.width(), self.height())

