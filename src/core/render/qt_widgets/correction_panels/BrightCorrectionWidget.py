from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QResizeEvent
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout

if TYPE_CHECKING:
    from forms.MainForm import MainForm

from src.core.render.CorrectionSettings import CorrectionSettings
from src.enums import CorrectionResetItem
from src.core.qt_components import SimpleSlider, VBoxContainer
from src.core.log import print_d


class BrightCorrectionWidget(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(BrightCorrectionWidget, self).__init__(*args, **kwargs)
        self.block_applying: bool = False
        self._options: CorrectionSettings = CorrectionSettings()
        self.mf: MainForm = main_form

        self.vbox_cont = VBoxContainer(self)
        self.vbox_cont.set_width(self.width())
        self.vbox_cont.set_widget_spacing(10)

        self.label_bright_header = QLabel("Яркость: 1.0")
        self.label_bright_header.adjustSize()

        self.label_contrast_header = QLabel("Контраст: 255")
        self.label_contrast_header.adjustSize()
        # self.label_contrast_header.move(0, 50)

        self.slider_bright = SimpleSlider(Qt.Horizontal)
        self.slider_bright.maximum = 200
        self.slider_bright.minimum = 1
        self.slider_bright.set_value(100)
        self.slider_bright.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.BRIGHT)
        self.slider_bright.valueChanged.connect(self.apply_options)
        self.slider_bright.move(0, 20)

        self.slider_contrast = SimpleSlider(Qt.Horizontal)
        self.slider_contrast.maximum = 511
        self.slider_contrast.minimum = 0
        self.slider_contrast.mouseDoubleClickEvent = lambda x: self.reset_self(CorrectionResetItem.CONTRAST)
        self.slider_contrast.set_value(255)
        self.slider_contrast.valueChanged.connect(self.apply_options)
        self.slider_contrast.move(0, 70)

        self.vbox_cont.add_widget(self.label_bright_header)
        self.vbox_cont.add_widget(self.slider_bright)
        self.vbox_cont.add_widget(self.label_contrast_header)
        self.vbox_cont.add_widget(self.slider_contrast)

        # self.vbl = QVBoxLayout()
        # self.vbl.addWidget(self.label_bright_header)
        # self.vbl.addWidget(self.slider_bright)
        # self.vbl.addWidget(self.label_contrast_header)
        # self.vbl.addWidget(self.slider_contrast)
        # self.vbl.addStretch(1)
        # self.setLayout(self.vbl)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.vbox_cont.set_width(self.width())

    def paintEvent(self, event: QPaintEvent) -> None:
        super(BrightCorrectionWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#1D1D1D")))

    def reset_options(self):
        self._options.bright = 1.0
        self.slider_bright.set_value(100)
        self._options.contrast = 255
        self.slider_contrast.set_value(255)

    def reset_self(self, reset_type: CorrectionResetItem):
        if reset_type is CorrectionResetItem.BRIGHT:
            self.slider_bright.set_value(100)
        elif reset_type is CorrectionResetItem.CONTRAST:
            self.slider_contrast.set_value(255)
        self.apply_options()

    @property
    def options(self) -> CorrectionSettings:
        return self._options

    @options.setter
    def options(self, opt: CorrectionSettings) -> None:
        self._options = opt
        self.slider_bright.blockSignals(True)
        self.slider_bright.set_value(int(opt.bright * 100))
        self.slider_bright.blockSignals(False)

        self.slider_contrast.blockSignals(True)
        self.slider_contrast.set_value(opt.contrast)
        self.slider_contrast.blockSignals(False)

        self.label_bright_header.setText(f"Яркость: {self._options.bright}")
        self.label_contrast_header.setText(f"Контраст: {self._options.contrast}")

    def apply_options(self):
        if not self.block_applying:
            self._options.bright = self.slider_bright.value / 100
            self._options.contrast = self.slider_contrast.value

            self.label_bright_header.setText(f"Яркость: {self._options.bright}")
            self.label_contrast_header.setText(f"Контраст: {self._options.contrast}")

            self.mf.update_buffer()
            self.mf.update()
