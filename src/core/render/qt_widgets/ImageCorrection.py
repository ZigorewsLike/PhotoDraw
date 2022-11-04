from enum import Enum
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from ..CorrectionSettings import CorrectionSettings


class ResetItem(Enum):
    MIN_V = 0
    MID_V = 1
    MAX_V = 2
    BRIGHT = 3
    CONTRAST = 4


class ImageCorrection(QWidget):

    def __init__(self, main_form, *args, **kwargs):
        super(ImageCorrection, self).__init__(*args, **kwargs)
        self.resize(200, 200)

        self.setStyleSheet("""
        QLabel{
            color: white;
        }
        """)

        self.options: CorrectionSettings = CorrectionSettings()
        self.block_applying: bool = False
        self.mf: MainForm = main_form

        self.label_bright_header = QLabel("Яркость:     1.0", self)
        self.label_contrast_header = QLabel("Контраст:    255", self)

        self.slider_min_v = QSlider(Qt.Horizontal, self)
        self.slider_min_v.setMaximum(255)
        self.slider_min_v.setMinimum(0)
        self.slider_min_v.setToolTip("Значение тени")
        self.slider_min_v.mouseDoubleClickEvent = lambda x: self.reset_self(ResetItem.MIN_V)
        self.slider_min_v.valueChanged.connect(self.apply_options)

        self.slider_mid_v = QSlider(Qt.Horizontal, self)
        self.slider_mid_v.setMaximum(255)
        self.slider_mid_v.setMinimum(0)
        self.slider_mid_v.setValue(128)
        self.slider_mid_v.mouseDoubleClickEvent = lambda x: self.reset_self(ResetItem.MID_V)
        self.slider_mid_v.setToolTip("Средние тона")
        self.slider_mid_v.valueChanged.connect(self.apply_options)

        self.slider_max_v = QSlider(Qt.Horizontal, self)
        self.slider_max_v.setMaximum(255)
        self.slider_max_v.setMinimum(0)
        self.slider_max_v.setValue(255)
        self.slider_max_v.mouseDoubleClickEvent = lambda x: self.reset_self(ResetItem.MAX_V)
        self.slider_max_v.setToolTip("Значение света")
        self.slider_max_v.valueChanged.connect(self.apply_options)

        self.slider_bright = QSlider(Qt.Horizontal, self)
        self.slider_bright.setMaximum(200)
        self.slider_bright.setMinimum(1)
        self.slider_bright.setValue(100)
        self.slider_bright.mouseDoubleClickEvent = lambda x: self.reset_self(ResetItem.BRIGHT)
        self.slider_bright.valueChanged.connect(self.apply_options)

        self.slider_contrast = QSlider(Qt.Horizontal, self)
        self.slider_contrast.setMaximum(511)
        self.slider_contrast.setMinimum(0)
        self.slider_contrast.mouseDoubleClickEvent = lambda x: self.reset_self(ResetItem.CONTRAST)
        self.slider_contrast.setValue(255)
        self.slider_contrast.valueChanged.connect(self.apply_options)

        self.hbl = QHBoxLayout()

        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.slider_min_v)
        self.vbl.addWidget(self.slider_mid_v)
        self.vbl.addWidget(self.slider_max_v)
        self.vbl.addWidget(self.label_bright_header)
        self.vbl.addWidget(self.slider_bright)
        self.vbl.addWidget(self.label_contrast_header)
        self.vbl.addWidget(self.slider_contrast)
        self.vbl.addLayout(self.hbl)
        self.setLayout(self.vbl)

    def reset_options(self):
        self.options.bright = 1.0
        self.slider_bright.setValue(100)
        self.options.levels.max_v = 255
        self.slider_max_v.setValue(255)
        self.options.levels.mid_tone = 128
        self.slider_mid_v.setValue(128)
        self.options.levels.min_v = 0
        self.slider_min_v.setValue(0)
        self.options.contrast = 255
        self.slider_contrast.setValue(255)

    def reset_self(self, reset_type: ResetItem):
        if reset_type is ResetItem.MIN_V:
            self.slider_min_v.setValue(0)
        elif reset_type is ResetItem.MID_V:
            self.slider_mid_v.setValue(127)
        elif reset_type is ResetItem.MAX_V:
            self.slider_max_v.setValue(255)
        elif reset_type is ResetItem.BRIGHT:
            self.slider_bright.setValue(100)
        elif reset_type is ResetItem.CONTRAST:
            self.slider_contrast.setValue(255)
        self.apply_options()

    def apply_options(self):
        if not self.block_applying:
            self.options.bright = self.slider_bright.value() / 100
            self.options.levels.max_v = max(self.slider_max_v.value(), self.slider_min_v.value())
            self.options.levels.mid_tone = self.slider_mid_v.value()
            self.options.levels.min_v = min(self.slider_max_v.value(), self.slider_min_v.value())
            self.options.contrast = self.slider_contrast.value()

            self.label_bright_header.setText("Яркость:     " + str(self.options.bright))
            self.label_contrast_header.setText("Контраст:    " + str(self.options.contrast))

            self.mf.update_buffer()
            self.mf.update()

