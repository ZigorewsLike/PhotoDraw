from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.core.render.CorrectionSettings import CorrectionSettings
from src.enums import CorrectionResetItem


class BrightCorrectionWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(BrightCorrectionWidget, self).__init__(*args, **kwargs)
        self.block_applying: bool = False
        self.options: CorrectionSettings = CorrectionSettings()
        self.mf: MainForm = main_form

        self.label_bright_header = QLabel("Яркость: 1.0", self)
        self.label_contrast_header = QLabel("Контраст: 255", self)

        self.slider_bright = QSlider(Qt.Horizontal, self)
        self.slider_bright.setMaximum(200)
        self.slider_bright.setMinimum(1)
        self.slider_bright.setValue(100)
        self.slider_bright.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.BRIGHT)
        self.slider_bright.valueChanged.connect(self.apply_options)

        self.slider_contrast = QSlider(Qt.Horizontal, self)
        self.slider_contrast.setMaximum(511)
        self.slider_contrast.setMinimum(0)
        self.slider_contrast.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.CONTRAST)
        self.slider_contrast.setValue(255)
        self.slider_contrast.valueChanged.connect(self.apply_options)

        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.label_bright_header)
        self.vbl.addWidget(self.slider_bright)
        self.vbl.addWidget(self.label_contrast_header)
        self.vbl.addWidget(self.slider_contrast)
        self.vbl.addStretch(1)
        self.setLayout(self.vbl)

    def paintEvent(self, event: QPaintEvent) -> None:
        super(BrightCorrectionWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#1D1D1D")))

    def reset_options(self):
        self.options.bright = 1.0
        self.slider_bright.setValue(100)
        self.options.contrast = 255
        self.slider_contrast.setValue(255)

    def reset_self(self, reset_type: CorrectionResetItem):
        if reset_type is CorrectionResetItem.BRIGHT:
            self.slider_bright.setValue(100)
        elif reset_type is CorrectionResetItem.CONTRAST:
            self.slider_contrast.setValue(255)
        self.apply_options()

    def apply_options(self):
        if not self.block_applying:
            self.options.bright = self.slider_bright.value() / 100
            self.options.contrast = self.slider_contrast.value()

            self.label_bright_header.setText(f"Яркость: {self.options.bright}")
            self.label_contrast_header.setText(f"Контраст: {self.options.contrast}")

            self.mf.update_buffer()
            self.mf.update()
