from typing import TYPE_CHECKING, List, Tuple

import numpy as np

from PyQt5.QtCore import QLine, QPointF, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QPen, QShowEvent, QResizeEvent
from PyQt5.QtWidgets import QWidget
if TYPE_CHECKING:
    from forms.MainForm import MainForm


class GraphPanelBase(QWidget):
    def __init__(self, main_form, *args, **kwargs):
        super(GraphPanelBase, self).__init__(*args, **kwargs)
        self.mf: MainForm = main_form
        # QColor("#A0A0A0")
        self.colors = [QColor("#FF5458"), QColor("#4AFF4A"), QColor("#3c6eff")]
        # self.colors = [QColor("#FF0300"), QColor("#0010FF"), QColor("#00FF17")]
        # self.colors = [QColor("#D0D3C7"), QColor("#D0D3C7"), QColor("#D0D3C7")]
        self.lines: List[Tuple[np.ndarray, np.ndarray]] = []
        self.setMouseTracking(True)
        self.shift_left: float = 0
        self.shift_right: float = 1
        self.new_width: float = self.width()
        self.render_lines: List[List[QPointF]] = [[]]

        self.channel_count: int = 3
        self.channel_visible: List[bool] = [True] * self.channel_count

    def showEvent(self, event: QShowEvent) -> None:
        self.new_width = self.width()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(GraphPanelBase, self).resizeEvent(event)
        self.set_shift(self.shift_left, self.shift_right)
        self.update()

    def set_polyline_list(self, unique_pixels: List[Tuple[np.ndarray, np.ndarray]]):
        self.lines: List[Tuple[np.ndarray, np.ndarray]] = []
        for color_ind, unique in enumerate(unique_pixels):
            u_color, u_count = unique
            max_u_count: float
            if u_count.size > 2:
                sort_u_count: np.ndarray = u_count.copy()
                sort_u_count.sort()
                max_u_count = (sort_u_count[-1] + sort_u_count[-2]) / 2
                del sort_u_count
            else:
                max_u_count = u_count.max()
            self.lines.append((u_color, u_count / max_u_count))
        self.calculate_render_lines()
        self.update()

    def calculate_render_lines(self):
        self.render_lines: List[List[QPointF]] = [[]] * len(self.lines)  # Cont of channels
        for color_ind, color_tuple in enumerate(self.lines):
            color_slice = color_tuple[0]
            color_slice: np.ndarray = color_slice[color_slice >= int(self.shift_left * color_tuple[1].size)]
            color_slice: np.ndarray = color_slice[color_slice <= int(self.shift_right * color_tuple[1].size)]
            self.render_lines[color_ind] = [QPointF(0, self.height())]
            self.render_lines[color_ind] += [QPointF(((i / (color_tuple[1].size - 1) - self.shift_left) * self.new_width),
                                          self.height() - color_tuple[1][i] * self.height())
                                  for i in color_slice[::max(1, int(color_slice.size / self.width() / 2))]]
            self.render_lines[color_ind] += [QPointF(self.width(), self.height())]

    def set_shift(self, shift_left: float, shift_right: float):
        self.shift_left = shift_left
        self.shift_right = shift_right
        shift: float = (1 - self.shift_right) + self.shift_left
        self.new_width = self.width()
        if shift != 1:
            self.new_width *= abs(1 / (1 - shift))
        self.calculate_render_lines()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.isVisible():
            painter = QPainter(self)
            painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#4B4B4B")))

            if self.lines:
                for color_ind, color_tuple in enumerate(self.lines):
                    if self.channel_visible[color_ind]:
                        painter.setPen(QPen(self.colors[color_ind], 0, Qt.SolidLine))
                        painter.setBrush(QBrush(self.colors[color_ind], Qt.SolidPattern))
                        painter.drawPolygon(*self.render_lines[color_ind])



