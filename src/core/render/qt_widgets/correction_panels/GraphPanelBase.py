from typing import TYPE_CHECKING, List

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

    # TODO: Buffer lines. Call function `calc line`, get normalized lines, draw as generator QPoinF
    def paintEvent(self, event: QPaintEvent) -> None:
        if self.isVisible():
            painter = QPainter(self)
            painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#4B4B4B")))

            if self.mf.render_image.is_valid and self.mf.render_image.unique_pixels:
                painter.setCompositionMode(QPainter.CompositionMode_SoftLight)
                for color_ind, unique in enumerate(self.mf.render_image.unique_pixels):
                    r_color, r_count = unique
                    scale_factor_w: float = self.width() / 255
                    scale_factor_h: float = self.height() / r_count.max()
                    lines: List[QPointF] = [QPointF(0, self.height())]
                    for ind, color in enumerate(r_color):
                        lines.append(QPointF(color * scale_factor_w, self.height() - r_count[ind] * scale_factor_h))
                    lines.append(QPointF(self.width(), self.height()))
                    painter.setPen(QPen(self.colors[color_ind], 0, Qt.SolidLine))
                    painter.setBrush(QBrush(self.colors[color_ind], Qt.SolidPattern))
                    painter.drawPolygon(lines)
            painter.setCompositionMode(QPainter.CompositionMode_Source)

