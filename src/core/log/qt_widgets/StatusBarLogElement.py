from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QImage, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QLabel


class StatusBarLogElement(QWidget):
    def __init__(self, icon_path: str, text: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_path: str = icon_path
        self.text = QLabel(text, self)
        self.text.move(25, 0)
        self.text.setStyleSheet("""
        QLabel{
            color: white;
            font-size: 10pt;
        }
        """)
        self.text.adjustSize()
        self.setMinimumSize(25 + self.text.width(), 18)

        self.color: QColor = QColor(255, 0, 0, 255)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        # painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        rect = QRectF(1, 1, 18, 18)
        # painter.setPen(QPen(self.color, 20, Qt.SolidLine))
        # painter.setBrush(self.color)

        painter.drawImage(rect, QImage(self.icon_path))
        # painter.fillRect(rect, QBrush(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(rect)


