from copy import copy
from typing import TYPE_CHECKING, List, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import QLine, QPointF, Qt, QPoint, QRectF, QEvent, pyqtSlot
from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QPen, QPolygon, QMouseEvent, QTextOption
from PyQt5.QtWidgets import QWidget, QPushButton

from src.core.log import print_d
from .GraphPanelBase import GraphPanelBase
from src.enums import GraphInteractiveMode
from src.function_lib import median


class GraphPanelLevels(GraphPanelBase):
    setOptions = QtCore.pyqtSignal()

    def __init__(self, main_form, *args, **kwargs):
        super().__init__(main_form, *args, **kwargs)
        self.move_mode: GraphInteractiveMode = GraphInteractiveMode.NOWAY
        self.scaler: float = 255 / self.width()
        self.click_pos: QPoint = QPoint(0, 0)
        self.old_options = self.mf.options.copy()
        self.clicked = False
        self.setMouseTracking(True)

        # region channel buttons
        self.button_container: List[QPushButton] = []
        channel_label: List[str] = ['R', 'G', 'B']
        border_color: List[str] = ["#FF8375", "#8DFF83", "#78D1FF"]
        for i in range(self.channel_count):
            button_style: str = """
                QPushButton[color_visible="true"]{
                    background-color: rgba(0, 0, 0, 90);
                    color: %s;
                    border: 2px solid %s;
                }
                QPushButton[color_visible="false"]{
                    background-color: rgba(0, 0, 0, 90);
                    color: gray;
                    border: 2px solid gray;
                }
                QPushButton:hover{
                    background-color: rgba(255, 255, 255, 90);
                }
                QPushButton[color_visible="false"]:hover{
                    color: white;
                }
                """ % (border_color[i], border_color[i])
            button = QPushButton(channel_label[i], self)

            button.setProperty("color_visible", "true")
            button.setStyleSheet(button_style)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

            button.move(20 * i, 0)
            button.resize(20, 20)
            button.setVisible(False)
            button.clicked.connect(lambda _, index=i: self.set_channel_visible(index))
            self.button_container.append(button)


        # endregion

    def paintEvent(self, event: QPaintEvent) -> None:
        super(GraphPanelLevels, self).paintEvent(event)

        if self.mf.render_image.is_valid:
            scale_factor_x = self.width() / 255
            painter = QPainter(self)

            painter.fillRect(0, 0, int(self.mf.options.levels.min_v / 255 * self.width()), self.height(),
                             QBrush(QColor(0, 0, 0, 150)))
            painter.fillRect(int(self.mf.options.levels.max_v / 255 * self.width()), 0, self.width(), self.height(),
                             QBrush(QColor(0, 0, 0, 150)))

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
            y1 = 10 if x1 > 70 or not self.button_container[0].isVisible() else 35
            painter.drawText(int(x1), y1, str(self.mf.options.levels.min_v))
            x2 = self.mf.options.levels.max_v * scale_factor_x
            if self.mf.options.levels.max_v < 220:
                x2 += 5
            else:
                x2 -= 22
            y2 = 10 if x2 > 70 or not self.button_container[0].isVisible() else 35
            painter.drawText(int(x2), y2, str(self.mf.options.levels.max_v))

            if self.move_mode is GraphInteractiveMode.CENTER or self.move_mode is GraphInteractiveMode.LEFT:
                painter.drawLine(int(self.mf.options.levels.min_v * scale_factor_x), 0,
                                 int(self.mf.options.levels.min_v * scale_factor_x), self.height())
            if self.move_mode is GraphInteractiveMode.CENTER or self.move_mode is GraphInteractiveMode.RIGHT:
                painter.drawLine(int(self.mf.options.levels.max_v * scale_factor_x), 0,
                                 int(self.mf.options.levels.max_v * scale_factor_x), self.height())
            if self.move_mode is GraphInteractiveMode.MIDDLE:
                painter.setOpacity(1)
                x3 = _calc_width + _slider_width / 2 - 30
                y3 = 5 if x3 > 50 or not self.button_container[0].isVisible() else 15
                text_rect = QRectF(x3, y3, 60, 30)
                option = QTextOption(Qt.AlignCenter)
                # painter.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
                painter.drawText(text_rect, str(self.mf.options.levels.mid_tone), option)
                # painter.setCompositionMode(QPainter.CompositionMode_Source)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.old_options.levels.max_v = self.mf.options.levels.max_v
        self.old_options.levels.min_v = self.mf.options.levels.min_v
        self.clicked = True

        self.click_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:

        if not self.button_container[0].isVisible():
            for button in self.button_container:
                button.setVisible(True)

        self.scaler = 255 / self.width()
        pos_x = event.x() * self.scaler

        _width = self.mf.options.levels.max_v - self.mf.options.levels.min_v
        _calc_width = self.mf.options.levels.min_v + self.mf.options.levels.mid_tone / 255 * _width

        if not self.clicked:
            if self.mf.options.levels.min_v - 10 <= pos_x <= self.mf.options.levels.min_v + 10:
                self.move_mode = GraphInteractiveMode.LEFT
                self.update()
            elif self.mf.options.levels.max_v - 10 <= pos_x <= self.mf.options.levels.max_v + 10:
                self.move_mode = GraphInteractiveMode.RIGHT
                self.update()
            elif _calc_width - 10 <= pos_x <= _calc_width + 10 and event.y() < 30:
                self.move_mode = GraphInteractiveMode.MIDDLE
                self.update()
            elif self.mf.options.levels.min_v <= pos_x <= self.mf.options.levels.max_v:
                self.move_mode = GraphInteractiveMode.CENTER
                self.update()
            else:
                self.move_mode = GraphInteractiveMode.NOWAY
                self.update()
        else:
            old_pos_x = self.click_pos.x() * self.scaler
            if self.move_mode is GraphInteractiveMode.CENTER or self.move_mode is GraphInteractiveMode.LEFT:
                self.mf.options.levels.min_v = median(0, int(self.old_options.levels.min_v - (old_pos_x - pos_x)), 255)
                if self.move_mode != GraphInteractiveMode.CENTER:
                    self.setOptions.emit()
            if self.move_mode is GraphInteractiveMode.CENTER or self.move_mode is GraphInteractiveMode.RIGHT:
                self.mf.options.levels.max_v = median(0, int(self.old_options.levels.max_v - (old_pos_x - pos_x)), 255)
                if self.move_mode != GraphInteractiveMode.CENTER:
                    self.setOptions.emit()
            if self.move_mode is GraphInteractiveMode.MIDDLE:
                _width = (self.old_options.levels.max_v - self.old_options.levels.min_v)
                self.mf.options.levels.mid_tone = median(0, int((pos_x - self.old_options.levels.min_v) / _width * 255), 255)
                self.setOptions.emit()
            if self.move_mode is GraphInteractiveMode.CENTER:
                self.setOptions.emit()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        self.clicked = False
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        for button in self.button_container:
            button.setVisible(False)
        self.update()

    @pyqtSlot(int)
    def set_channel_visible(self, color_index: int, visible: Optional[bool] = None) -> None:
        print_d(color_index)
        if visible is None:
            # FlipFlop mode
            visible = not self.channel_visible[color_index]
        self.channel_visible[color_index] = visible

        property_text = 'true' if visible else 'false'
        self.button_container[color_index].setProperty("color_visible", property_text)
        self.button_container[color_index].style().unpolish(self.button_container[color_index])
        self.button_container[color_index].style().polish(self.button_container[color_index])
        self.button_container[color_index].update()

        self.update()



