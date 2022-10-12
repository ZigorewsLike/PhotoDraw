from typing import TYPE_CHECKING, Union

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QBrush
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    from forms.MainForm import MainForm


class RenderFrame(QWidget):

    def __init__(self, *args, **kwargs):
        super(RenderFrame, self).__init__(*args, **kwargs)
        self.mf: Union[MainForm, QWidget] = self.parent()

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(self.geometry(), QBrush(QColor("333333")))

