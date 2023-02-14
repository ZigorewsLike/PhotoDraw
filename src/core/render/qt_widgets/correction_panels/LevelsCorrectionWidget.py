from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout, QFrame

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.core.render.CorrectionSettings import CorrectionSettings
from src.enums import CorrectionResetItem
from .GraphPanelLevels import GraphPanelLevels


class LevelsCorrectionWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(LevelsCorrectionWidget, self).__init__(*args, **kwargs)
        self.block_applying: bool = False
        self._options: CorrectionSettings = CorrectionSettings()
        self.mf: MainForm = main_form

        self.resize(200, 200)

        self.paint_levels = GraphPanelLevels(self.mf, self)
        self.paint_levels.setMinimumHeight(160)
        self.paint_levels.setOptions.connect(self.set_options)

        self.slider_min_v = QSlider(Qt.Horizontal, self)
        self.slider_min_v.setMaximum(255)
        self.slider_min_v.setMinimum(0)
        self.slider_min_v.setToolTip("Значение тени")
        self.slider_min_v.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.MIN_V)
        self.slider_min_v.valueChanged.connect(self.apply_options)

        self.slider_mid_v = QSlider(Qt.Horizontal, self)
        self.slider_mid_v.setMaximum(255)
        self.slider_mid_v.setMinimum(0)
        self.slider_mid_v.setValue(128)
        self.slider_mid_v.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.MID_V)
        self.slider_mid_v.setToolTip("Средние тона")
        self.slider_mid_v.valueChanged.connect(self.apply_options)

        self.slider_max_v = QSlider(Qt.Horizontal, self)
        self.slider_max_v.setMaximum(255)
        self.slider_max_v.setMinimum(0)
        self.slider_max_v.setValue(255)
        self.slider_max_v.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.MAX_V)
        self.slider_max_v.setToolTip("Значение света")
        self.slider_max_v.valueChanged.connect(self.apply_options)

        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.paint_levels)
        self.vbl.addWidget(self.slider_min_v)
        self.vbl.addWidget(self.slider_mid_v)
        self.vbl.addWidget(self.slider_max_v)
        self.vbl.addStretch(1)

        self.setLayout(self.vbl)

    def paintEvent(self, event: QPaintEvent) -> None:
        super(LevelsCorrectionWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#1D1D1D")))

    def reset_options(self):
        self._options.levels.max_v = 255
        self.slider_max_v.setValue(255)
        self._options.levels.mid_tone = 128
        self.slider_mid_v.setValue(128)
        self._options.levels.min_v = 0
        self.slider_min_v.setValue(0)

    def reset_self(self, reset_type: CorrectionResetItem):
        if reset_type is CorrectionResetItem.MIN_V:
            self.slider_min_v.setValue(0)
        elif reset_type is CorrectionResetItem.MID_V:
            self.slider_mid_v.setValue(127)
        elif reset_type is CorrectionResetItem.MAX_V:
            self.slider_max_v.setValue(255)
        self.apply_options()

    @pyqtSlot()
    def set_options(self):
        self.block_applying = True
        self.slider_min_v.setValue(self.options.levels.min_v)
        self.slider_mid_v.setValue(self.options.levels.mid_tone)
        self.slider_max_v.setValue(self.options.levels.max_v)
        self.block_applying = False
        self.apply_options()

    @property
    def options(self) -> CorrectionSettings:
        return self._options

    @options.setter
    def options(self, opt: CorrectionSettings) -> None:
        self._options = opt
        self.slider_max_v.blockSignals(True)
        self.slider_max_v.setValue(opt.levels.max_v)
        self.slider_max_v.blockSignals(False)

        self.slider_min_v.blockSignals(True)
        self.slider_min_v.setValue(opt.levels.min_v)
        self.slider_min_v.blockSignals(False)

        self.slider_mid_v.blockSignals(True)
        self.slider_mid_v.setValue(opt.levels.mid_tone)
        self.slider_mid_v.blockSignals(False)

    def apply_options(self):
        if not self.block_applying:
            self._options.levels.max_v = max(self.slider_max_v.value(), self.slider_min_v.value())
            self._options.levels.mid_tone = self.slider_mid_v.value()
            self._options.levels.min_v = min(self.slider_max_v.value(), self.slider_min_v.value())

            self.mf.update_buffer()
            self.mf.update()

