import math

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QMouseEvent, QFontMetrics
from PyQt5.QtWidgets import QWidget, QToolTip, QLabel

from src.core.log import print_d
from src.function_lib import median


class SimpleSlider(QWidget):
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, orientation: Qt.Orientation, *args, **kwargs):
        super(SimpleSlider, self).__init__(*args, **kwargs)
        self.minimum: int = 0
        self.maximum: int = 100
        self.value: int = 100
        self._slider_height: int = 5
        self.global_margin: int = 5

        self.is_hover: bool = False
        self.is_clicked: bool = False

        # region Настройка стилей
        self.background_color: QColor = QColor("#424242")
        self.simple_color: QColor = QColor("#DADADA")
        self.hover_color: QColor = QColor("#3980FF")
        self.flag_color: QColor = QColor("#86CFFF")
        self.front_color: QColor = self.simple_color
        self.tooltip_sub_text: str = ""
        self.tooltip_visible: bool = True

        local_text_container: QLabel = QLabel()
        local_text_container.setFont(QToolTip.font())
        self.tooltip_font_metrics: QFontMetrics = local_text_container.fontMetrics()
        # endregion

        if self.parent() is not None:
            self.resize(self.parent().width(), self._slider_height + self.global_margin * 2)
        else:
            self.resize(50, self._slider_height + self.global_margin * 2)
        self.setMouseTracking(True)
        self.valueChanged.connect(self._slider_val_change)

    @property
    def slider_height(self) -> int:
        return self._slider_height

    @slider_height.setter
    def slider_height(self, val: int) -> None:
        self._slider_height = val
        self.resize(self.parent().width(), self._slider_height + self.global_margin * 2)

    def set_global_margin(self, global_margin: int) -> None:
        self.global_margin = global_margin
        self.resize(self.parent().width(), self._slider_height + self.global_margin * 2)
        self.update()

    # region Методы QWidget
    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.global_margin, self.global_margin, self.width() - self.global_margin * 2,
                         self.height() - self.global_margin * 2, QBrush(self.background_color))
        calc_width: float = (self.width() - self.global_margin * 2) * (self.value / (self.maximum - self.minimum))
        painter.fillRect(self.global_margin, self.global_margin,
                         int(calc_width), self.height() - self.global_margin*2, QBrush(self.front_color))
        if self.is_hover:
            painter.fillRect(int(calc_width - 2 + self.global_margin), self.global_margin // 2,
                             5, self.height() - self.global_margin, QBrush(self.flag_color))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.is_clicked = True
        mouse_val: int = median(0, event.x() - self.global_margin, self.width() - self.global_margin * 2)
        mouse_val /= self.width() - self.global_margin * 2  # Normalisation
        self.valueChanged.emit(round((self.maximum - self.minimum) * mouse_val + self.minimum))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.is_clicked = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.front_color = self.hover_color
        self.is_hover = True
        if self.is_clicked:
            mouse_val: int = median(0, event.x() - self.global_margin, self.width() - self.global_margin * 2)
            mouse_val /= self.width() - self.global_margin * 2  # Normalisation
            self.valueChanged.emit(int((self.maximum - self.minimum) * mouse_val + self.minimum))
        self.update()

    def set_value(self, val: int) -> None:
        self.valueChanged.emit(val)
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        self.front_color = self.simple_color
        self.is_hover = False
        self.update()
    # endregion

    @pyqtSlot(int)
    def _slider_val_change(self, val: int) -> None:
        self.value = median(self.minimum, val, self.maximum)

        # region ToolTip
        if self.tooltip_visible and self.is_clicked:
            tooltip_text: str = f"{self.tooltip_sub_text + ' ' if self.tooltip_sub_text != '' else ''}{self.value}%"
            if self.parent() is not None:
                pos = self.parent().mapToGlobal(self.pos())
            else:
                pos = self.pos()
            text_width: int = self.tooltip_font_metrics.boundingRect(tooltip_text).width()
            calc_width: float = (self.width() - self.global_margin * 2) * (self.value / (self.maximum - self.minimum))
            pos.setX(int(pos.x() + calc_width - text_width // 2))
            pos.setY((pos.y() - (42 - self.global_margin)))
            QToolTip.showText(pos, tooltip_text)
        # endregion

        self.update()
