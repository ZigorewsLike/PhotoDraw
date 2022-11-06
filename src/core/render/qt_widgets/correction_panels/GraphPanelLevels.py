from typing import TYPE_CHECKING, List

from PyQt5.QtCore import QLine, QPointF, Qt, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QPen, QPolygon
from PyQt5.QtWidgets import QWidget

from .GraphPanelBase import GraphPanelBase


class GraphPanelLevels(GraphPanelBase):
    def __init__(self, main_form, *args, **kwargs):
        super().__init__(main_form, *args, **kwargs)

    def paintEvent(self, event: QPaintEvent) -> None:
        super(GraphPanelLevels, self).paintEvent(event)

        if self.mf.render_image.is_valid:
            scale_factor_x = self.width() / 255
            painter = QPainter(self)
            painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            painter.drawLine(int(self.mf.options.levels.min_v * scale_factor_x), 0,
                             int(self.mf.options.levels.min_v * scale_factor_x), self.height())

            painter.drawLine(int(self.mf.options.levels.max_v * scale_factor_x), 0,
                             int(self.mf.options.levels.max_v * scale_factor_x), self.height())

            _width = self.mf.options.levels.max_v * scale_factor_x - self.mf.options.levels.min_v * scale_factor_x
            _slider_width = 8
            _calc_width = self.mf.options.levels.min_v * scale_factor_x + self.mf.options.levels.mid_tone / 255 * _width - _slider_width / 2
            points = QPolygon([
                QPoint(int(_calc_width), 0),
                QPoint(int(_calc_width + _slider_width / 2), _slider_width - 1),
                QPoint(int(_calc_width + _slider_width), 0),
            ])
            painter.drawPolygon(points)

            painter.setPen(QPen(Qt.white, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            x1 = self.mf.options.levels.min_v * scale_factor_x
            if self.mf.options.levels.min_v > 35:
                x1 -= 20
            else:
                x1 += 5
            painter.drawText(int(x1), 10, str(self.mf.options.levels.min_v))
            x2 = self.mf.options.levels.max_v * scale_factor_x
            if self.mf.options.levels.max_v < 220:
                x2 += 5
            else:
                x2 -= 22
            painter.drawText(int(x2), 10, str(self.mf.options.levels.max_v))
