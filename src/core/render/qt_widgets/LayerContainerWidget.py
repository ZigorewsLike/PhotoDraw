from typing import TYPE_CHECKING, List, Tuple

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QResizeEvent
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame, QPushButton

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.global_style_sheets import TAB_STYLE
from .correction_panels.LayerTabWidget import LayerTabWidget

class LayerContainerWidget(QWidget):

    def __init__(self, main_form, *args, **kwargs):
        super(LayerContainerWidget, self).__init__(*args, **kwargs)
        self.resize(200, 300)

        self.setStyleSheet("""
        QLabel{
            color: white;
        }
        %s
        """ % TAB_STYLE)

        self.mf: MainForm = main_form

        self.tabs = QTabWidget(self)
        self.tabs.addTab(LayerTabWidget(self.mf), "Слои")
        self.tabs.addTab(QWidget(), "Каналы")

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(LayerContainerWidget, self).resizeEvent(event)
        self.tabs.resize(self.width(), self.height())