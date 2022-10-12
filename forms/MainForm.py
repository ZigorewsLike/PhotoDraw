from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QResizeEvent
from PyQt5.QtWidgets import QMainWindow

# region src imports
from src.global_constants import APP_NAME, CONFIGURATION
from src.core.point_system import Point, CRect
from src.core.log import print_i, print_e, print_d
from src.core.render import RenderFrame
# endregion


# region SizeClass
class SizeCollector:
    # left panel
    draw_toolbar_panel: int = 40
    # top panel
    menu_toolbar_panel: int = 30
    # right panel
    correction_panel: int = 200
    # bottom panel
    footer_panel: int = 20
# endregion


class MainForm(QMainWindow):
    def __init__(self, params: dict):
        super().__init__()
        self.setStyleSheet("""
        QMainWindow{
            background-color: #0E0C1B;
        }
        """)

        self.params = params
        self.form_position: Point = Point(-1., -1.)
        self.form_width = 1200
        self.form_height = 700
        self.size_collector = SizeCollector()

        self.init_ui()

        self.work_area = CRect.from_sides(self.size_collector.draw_toolbar_panel,
                                          self.size_collector.menu_toolbar_panel,
                                          self.width() - self.size_collector.correction_panel,
                                          self.height() - self.size_collector.footer_panel)
        self.render_frame = RenderFrame(self)
        self.render_frame.setGeometry(*self.work_area)

        print_d(self.work_area)

    def init_ui(self):
        if self.form_position == Point(-1, -1):
            self.form_position.x = self.params.get("size_width", 1920) / 2 - self.form_width / 2
            self.form_position.y = self.params.get("size_height", 1080) / 2 - self.form_height / 2
        self.setGeometry(self.form_position.ix, self.form_position.iy, self.form_width, self.form_height)

        self.setMinimumSize(self.size_collector.draw_toolbar_panel + self.size_collector.correction_panel + 200,
                            self.size_collector.menu_toolbar_panel + self.size_collector.footer_panel + 200)

        self.setWindowTitle(f"{APP_NAME} | {CONFIGURATION.name}")

    def resizeEvent(self, e: QResizeEvent) -> None:
        super(MainForm, self).resizeEvent(e)

        self.work_area.right = self.width() - self.size_collector.correction_panel
        self.work_area.bottom = self.height() - self.size_collector.footer_panel

        self.render_frame.setGeometry(*self.work_area)

