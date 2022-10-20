import os
import random
import subprocess
import sys
import re
from typing import Union

from src.global_constants import CONSOLE_UPDATE_TICK_INTERVAL, MIN_TIMER_TICK_INTERVAL
from ..print_lib import print_d, print_i, ConsoleColors

from PyQt5.QtCore import Qt, QEvent, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent, QColor, QBrush, QResizeEvent, QTextBlockFormat, QTextCursor, \
    QPaintEvent, QPainter, QFont, QShowEvent, QCloseEvent, QCursor, QFocusEvent
from PyQt5.QtWidgets import QPushButton, QLabel, QWidget, QListWidget, QListWidgetItem, QMenu, QFrame, QTextEdit, \
    QVBoxLayout, QScrollArea, QApplication, QCheckBox, QSpinBox

from src.enums.ConsoleLogMode import ConsoleLogMode


class ConsoleWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Консоль разработчика")

        self.resize(800, 300)
        self.text_buffer: str = ""
        self.selected_flag = "ALL"
        self.text_size_of: int = 0
        self.last_line: int = 0
        self.always_top: bool = True
        self.resize_mode: bool = False
        self.old_cursor_pos: QPoint = QPoint()
        self.timer_tick = CONSOLE_UPDATE_TICK_INTERVAL

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(lambda: self.update_console(self.selected_flag))

        self.setStyleSheet("""
            color: white; 
            background-color: rgb(30, 30, 40);
        """)

        self.counter: dict = {"ERROR": 0, "INFO": 0, "DEBUG": 0, "ALL": 0}

        self.v_line_layout = QVBoxLayout(self)
        self.v_line_layout.setSpacing(1)
        # self.v_line_layout.setContentsMargins(0, 0, 0, 0)

        self.line_frame = QFrame()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.line_frame)
        self.scroll_area.move(0, 40)
        self.line_frame.setLayout(self.v_line_layout)

        self.button_update = QPushButton("UPDATE", self)
        self.button_update.clicked.connect(lambda: self.update_console("ALL"))
        self.button_update.move(5, 10)

        self.button_debug = QPushButton("DEBUG", self)
        self.button_debug.clicked.connect(lambda: self.update_console("DEBUG"))
        self.button_debug.move(90, 10)

        self.button_info = QPushButton("INFO", self)
        self.button_info.clicked.connect(lambda: self.update_console("INFO"))
        self.button_info.move(175, 10)

        self.button_error = QPushButton("ERROR", self)
        self.button_error.clicked.connect(lambda: self.update_console("ERROR"))
        self.button_error.move(260, 10)

        self.button_close = QPushButton("x", self)
        self.button_close.clicked.connect(lambda: self.close())
        self.button_close.resize(30, 20)

        self.move_line_frame = QFrame(self)
        self.move_line_frame.setFrameShape(QFrame.HLine)
        self.move_line_frame.setFrameShadow(QFrame.Sunken)
        self.move_line_frame.setCursor(QCursor(Qt.SizeVerCursor))

        self.always_on_top_checkbox = QCheckBox("Прокручивать", self)
        self.always_on_top_checkbox.move(350, 10)
        self.always_on_top_checkbox.setChecked(True)
        self.always_on_top_checkbox.stateChanged.connect(self.always_top_signal)

        self.spin_update_tick = QSpinBox(self)
        self.spin_update_tick.move(450, 10)
        self.spin_update_tick.setMinimum(MIN_TIMER_TICK_INTERVAL)
        self.spin_update_tick.setMaximum(1000 * 60)
        self.spin_update_tick.setValue(CONSOLE_UPDATE_TICK_INTERVAL)
        self.spin_update_tick.valueChanged.connect(self.tick_interval_signal)

    def print_text(self, text: str):
        self.text_buffer += text

    def always_top_signal(self, val):
        self.always_top = val

    def tick_interval_signal(self, val):
        self.timer_tick = val
        if self.update_timer.isActive():
            self.update_timer.setInterval(val)

    def paintEvent(self, e: QPaintEvent) -> None:
        super(ConsoleWidget, self).paintEvent(e)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor(30, 30, 40)))

    def update_console(self, flag: str = ""):
        self.selected_flag = flag
        count = 0
        old_count = self.v_line_layout.count()

        for i, line in enumerate(self.text_buffer.split('\n')):
            if count < self.v_line_layout.count():
                count += 1
                continue
            if line == '':
                continue
            count += 1
            mode = ConsoleLogMode.NONE
            self.counter["ALL"] += 1
            for flag_text in ["DEBUG", "INFO", "ERROR"]:
                if re.search(r'\[' + flag_text + r'\]', line):
                    self.counter[flag_text] += 1
                    mode = ConsoleLogMode[flag_text]
                    break
            item: ConsoleLineItemWidget = ConsoleLineItemWidget(line, mode, self)
            last_item: Union[ConsoleLineItemWidget, QWidget]
            if self.v_line_layout.count() > 0:
                last_item = self.v_line_layout.itemAt(self.v_line_layout.count()-1).widget()
            else:
                last_item = item
            if self.v_line_layout.count() == 0 or last_item.message != item.message:
                item.update()
                self.v_line_layout.addWidget(item)
                self.line_frame.resize(self.width() - 18, 50 * (self.v_line_layout.count()))
            else:
                del item
                last_item.increment_msg_count()

        count = 0
        max_width = 0
        for i in range(self.v_line_layout.count()):
            item: Union[ConsoleLineItemWidget, QWidget] = self.v_line_layout.itemAt(i).widget()
            max_width = max(max_width, item.label_text.width())
            if self.selected_flag != "ALL" and item.mode != ConsoleLogMode[self.selected_flag]:
                item.setVisible(False)
            else:
                item.setVisible(True)
                count += 1
        self.line_frame.resize(max(self.width() - 20, max_width + 5), 50 * count)

        if self.always_top and old_count != self.v_line_layout.count():
            self.scroll_area.verticalScrollBar().setValue(self.line_frame.height())

        self.button_debug.setText(f"ДЕБАГ ({self.counter.get('DEBUG')})")
        self.button_info.setText(f"ИНФО ({self.counter.get('INFO')})")
        self.button_error.setText(f"ОШИБКИ ({self.counter.get('ERROR')})")
        self.button_update.setText(f"ВСЕ ({self.counter.get('ALL')})")

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.scroll_area.resize(self.width(), self.height() - 40)
        self.button_close.move(self.width() - 30, 10)
        self.move_line_frame.resize(self.width(), 10)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if 0 <= event.x() <= self.width() and 0 <= event.y() <= 10:
            self.resize_mode = True
            self.old_cursor_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.resize_mode = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.resize_mode:
            sub_y = self.old_cursor_pos.y() - event.y()
            if self.height() + sub_y > 100:
                self.resize(self.width(), self.height() + sub_y)
                self.move(self.x(), self.y() - sub_y)

    def showEvent(self, e: QShowEvent) -> None:
        super(ConsoleWidget, self).showEvent(e)
        self.update_console('ALL')
        if not self.update_timer.isActive():
            self.update_timer.start(self.timer_tick)

    def closeEvent(self, e: QCloseEvent) -> None:
        self.update_timer.stop()


class ConsoleLineItemWidget(QWidget):
    def __init__(self, text: str, mode: ConsoleLogMode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode: str = ""
        self.time: str = ""
        self.code_line: str = ""
        self.message: str = ""
        self.mode: ConsoleLogMode = mode
        self.message_count: int = 1
        self.width_shift: int = 0

        self.resize(self.parent().width(), 40)
        self.color_message: str = "white"
        self.setStyleSheet("""
        QWidget{
            color: white;
            font-family: Arial;
            margin-left: 10px;
            margin-right: 10px;
            border: 0px;
        }
        QLabel{
            background: transparent;
        }

        QLabel#LabelMessage{
            color: white;
            font-size: 11pt;
        }
        QLabel#LabelCodeLine{
            color: #CFCFCF;
            padding-left: 15px;
            font-size: 9pt;
        }
        """)

        self.label_text = QLabel("", self)
        self.label_text.move(0, 5)
        self.label_text.setObjectName("LabelMessage")

        self.code_label = QLabel("", self)
        self.code_label.move(0, 25)
        self.code_label.setObjectName("LabelCodeLine")

        self.parse_text(text)

    def parse_text(self, text: str):
        if self.mode == ConsoleLogMode.NONE:
            self.message = text
        else:
            text_split = text.split(ConsoleColors.SIMPLE)
            self.message = text_split[1]
            self.time, self.code_line = text_split[0].split(f"[{self.mode.name}]")
            self.code_line = self.code_line.replace(" :", "")
            if self.mode == ConsoleLogMode.DEBUG:
                self.time = self.time.replace(ConsoleColors.DEBUG, '')
                self.color_message = "#4da415"
            elif self.mode == ConsoleLogMode.INFO:
                self.time = self.time.replace(ConsoleColors.INFO, '')
                self.color_message = "#2585fc"
            elif self.mode == ConsoleLogMode.ERROR:
                self.time = self.time.replace(ConsoleColors.ERROR_HEADER, '')
                self.message = self.message.replace(ConsoleColors.ERROR, '')
                self.color_message = "#ff5449"

            self.code_label.setText(f"{self.time} : {self.code_line}")
            self.code_label.adjustSize()

        self.label_text.setStyleSheet("""
            QLabel#LabelMessage{
                color: """ + self.color_message + """;
                font-size: 11pt;
            }
        """)

        self.label_text.setText(f"{self.message}")
        self.label_text.adjustSize()

    def increment_msg_count(self):
        self.message_count += 1
        self.update()
        self.width_shift = QPainter(self).fontMetrics().boundingRect(str(self.message_count)).width()
        self.label_text.move(self.width_shift+10 + 5, self.label_text.y())
        self.code_label.move(self.width_shift+10 + 5, self.code_label.y())

    def paintEvent(self, e: QPaintEvent) -> None:
        super(ConsoleLineItemWidget, self).paintEvent(e)
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#1D253A")))

        if self.message_count > 1:
            painter.drawText(15, 23, str(self.message_count))

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        copy_action = context_menu.addAction("Копировать")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == copy_action:
            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(f"{self.code_line} {self.message}", mode=cb.Clipboard)
