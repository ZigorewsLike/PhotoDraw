from PyQt5.QtWidgets import QMainWindow

# region src imports
from src.core.point_system import Point
# endregion


class MainForm(QMainWindow):
    def __init__(self, params: dict):
        super().__init__()

        self.params = params
        self.form_position: Point = Point(-1., -1.)
        self.form_width = 1200
        self.form_height = 700

        self.init_ui()

    def init_ui(self):
        if self.form_position == Point(-1, -1):
            self.form_position.x = self.params.get("size_width", 1920) / 2 - self.form_width / 2
            self.form_position.y = self.params.get("size_height", 1080) / 2 - self.form_height / 2
        self.setGeometry(self.form_position.ix, self.form_position.iy, self.form_width, self.form_height)
        self.setWindowTitle("PhotoDraw")
