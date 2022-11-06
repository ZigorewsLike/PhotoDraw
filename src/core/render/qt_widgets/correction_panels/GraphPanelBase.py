from typing import TYPE_CHECKING, List, Tuple

import numpy as np

from PyQt5.QtCore import QLine, QPointF, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QWidget
if TYPE_CHECKING:
    from forms.MainForm import MainForm


class GraphPanelBase(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(GraphPanelBase, self).__init__(*args, **kwargs)
        self.mf: MainForm = main_form
        # QColor("#A0A0A0")
        # self.colors = [QColor("#A03438"), QColor("#2546A0"), QColor("#2DA02D")]
        self.colors = [QColor("#FF0300"), QColor("#0010FF"), QColor("#00FF17")]
        self.lines = List[Tuple[np.ndarray]]

    def set_polyline_list(self):
        if self.mf.render_image.is_valid and self.mf.render_image.unique_pixels:
            self.lines = []
            for color_ind, unique in enumerate(self.mf.render_image.unique_pixels):
                r_color, r_count = unique
                self.lines.append((r_color / 256, r_count / r_count.max()))

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.isVisible():
            painter = QPainter(self)
            painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#4B4B4B")))

            if self.mf.render_image.is_valid and self.mf.render_image.unique_pixels:
                painter.setCompositionMode(QPainter.CompositionMode_SoftLight)
                for color_ind, color_tuple in enumerate(self.lines):
                    painter.setPen(QPen(self.colors[color_ind], 0, Qt.SolidLine))
                    painter.setBrush(QBrush(self.colors[color_ind], Qt.SolidPattern))
                    lines = [QPointF(0, self.height())]
                    lines += [QPointF(color_tuple[0][i] * self.width(),
                                      self.height() - color_tuple[1][i] * self.height())
                              for i in range(color_tuple[0].size)]
                    lines += [QPointF(self.width(), self.height())]

                    painter.drawPolygon(lines)
            painter.setCompositionMode(QPainter.CompositionMode_Source)

