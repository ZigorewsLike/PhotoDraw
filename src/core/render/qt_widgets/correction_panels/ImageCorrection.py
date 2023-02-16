from typing import TYPE_CHECKING, List, Tuple

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QResizeEvent
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFrame, QPushButton

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.core.render.CorrectionSettings import CorrectionSettings
from src.global_style_sheets import TAB_STYLE
from .BrightCorrectionWidget import BrightCorrectionWidget
from .LevelsCorrectionWidget import LevelsCorrectionWidget


class ImageCorrection(QWidget):

    def __init__(self, main_form, *args, **kwargs):
        super(ImageCorrection, self).__init__(*args, **kwargs)
        self.resize(200, 340)

        self.setStyleSheet("""
        QLabel{
            color: white;
        }
        %s
        """ % TAB_STYLE)

        self._options: CorrectionSettings = CorrectionSettings()
        self.block_applying: bool = False
        self.mf: MainForm = main_form
        self.bright_correction = BrightCorrectionWidget(main_form, self)
        self.levels_correction = LevelsCorrectionWidget(main_form, self)

        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.levels_correction, "Уровни")
        self.tabs.addTab(self.bright_correction, "Яркость и контраст")

        self.levels_correction.move(0, self.bright_correction.height())

    def set_polyline_list(self, unique_pixels: List[Tuple[np.ndarray, np.ndarray]]):
        self.levels_correction.paint_levels.set_polyline_list(unique_pixels)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(ImageCorrection, self).resizeEvent(event)
        self.tabs.resize(self.width(), self.height())

    @property
    def options(self) -> CorrectionSettings:
        return self._options

    @options.setter
    def options(self, opt: CorrectionSettings) -> None:
        self._options = opt
        self.bright_correction.options = opt
        self.levels_correction.options = opt
        self.levels_correction.set_options()

    def reset_options(self):
        self.levels_correction.reset_options()
        self.bright_correction.reset_options()

