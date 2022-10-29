from typing import TYPE_CHECKING, Union

from PyQt5.QtGui import QPaintEvent, QPainter, QBrush, QColor, QShowEvent, QResizeEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QFrame, QPushButton, QLabel

from src.global_constants import VERSION
from .LastFileGrid import LastFileGrid

if TYPE_CHECKING:
    from forms.MainForm import MainForm


class HomePage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mf: Union[MainForm, QWidget] = self.parent()
        "#001D3D"
        "#003566"
        "35313D"
        "555366"

        self.setStyleSheet("""
        QLabel#Title{
            font-size: 18pt;
            color: white;
            font-family: Arial;
        }
        QLabel#Footer{
            font-size: 8pt;
            color: gray;
        }
        QPushButton#OpenButton{
            border: 0px solid black;
            background-color: #35313D;
            color: white;
            font-size: 16px;
            margin: 0px;
            padding: 10px;
            text-align: left;
        }
        QPushButton#OpenButton:hover{
            background-color: #555366;
        }
        """)

        self.last_grid_shift: int = 250

        # region UI
        self.last_grid = LastFileGrid(self)

        self.push_new_file = QPushButton("New file", self)
        self.push_new_file.setObjectName("OpenButton")
        icon = QPixmap(self.mf.resource_icon_dir + "add_photo_white_opsz48.png")
        self.push_new_file.setIcon(QIcon(icon))
        self.push_new_file.resize(200, 40)
        self.push_new_file.move(int(self.last_grid_shift / 2 - self.push_new_file.width() / 2), 80)

        self.push_open_file = QPushButton(self.mf.lang("OpenFileMenu"), self)
        self.push_open_file.setObjectName("OpenButton")
        icon = QPixmap(self.mf.resource_icon_dir + "file_open_white_24dp.png")
        self.push_open_file.setIcon(QIcon(icon))
        self.push_open_file.clicked.connect(self.mf.open_file_dialog)
        self.push_open_file.resize(200, 40)
        self.push_open_file.move(int(self.last_grid_shift / 2 - self.push_open_file.width() / 2),
                                 self.push_new_file.y() + self.push_new_file.height() + 10)

        self.label_title = QLabel("Главная", self)
        self.label_title.setObjectName("Title")
        self.label_title.move(20, 20)

        self.label_title = QLabel("Последние файлы", self)
        self.label_title.setObjectName("Title")
        self.label_title.move(self.last_grid_shift, 20)

        self.label_footer = QLabel(f"PhotoDraw ({VERSION})", self)
        self.label_footer.setObjectName("Footer")
        # endregion

    def resizeEvent(self, event: QResizeEvent) -> None:
        super(HomePage, self).resizeEvent(event)
        self.last_grid.move(self.last_grid_shift, 80)
        self.last_grid.resize(self.width() - self.last_grid_shift, self.height() - 80)
        self.label_footer.move(10, self.height() - 30)

    def showEvent(self, event: QShowEvent) -> None:
        self.setGeometry(*self.mf.work_area)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QBrush(QColor("#03031D")))
