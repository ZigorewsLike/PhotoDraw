import gc
import gettext
import os
import tracemalloc
from typing import Optional

from PyQt5.QtCore import QRect, QRectF, pyqtSlot, QTimer, QSize, Qt, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QResizeEvent, QPixmap, QIcon, QKeySequence, QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QLabel, QMenu, QAction, QFileDialog

# region src imports
from src.global_constants import APP_NAME, CONFIGURATION, USAGE_TIMER_TICK_INTERVAL
from src.core.point_system import Point, CRect
from src.core.log import print_i, print_e, print_d
from src.core.render import RenderFrame, RenderImage, Camera
# endregion


# region SizeClass
class SizeCollector:
    # left panel
    draw_toolbar_panel: int = 0
    # top panel
    menu_toolbar_panel: int = 30
    # right panel
    correction_panel: int = 0
    # bottom panel
    footer_panel: int = 20
# endregion


# region Lang installation
lang = gettext.translation('mainForm', localedir='locales', languages=['ru'])
lang.install()
_ = lang.gettext
# endregion


class MainForm(QMainWindow):
    resource_dir: str = "resources/"
    resource_icon_dir: str = f"{resource_dir}icons/"

    def __init__(self, params: dict):
        super().__init__()
        self.setStyleSheet("""
        QMainWindow{
            background-color: #0E0C1B;
        }
        QLabel#StatusBarLabel{
            color: white;
            margin-left: 10px;
            margin-right: 10px;
        }
        """)

        self.params = params
        self.form_position: Point = Point(-1., -1.)
        self.form_size = QSize(1200, 700)
        self.size_collector = SizeCollector()

        self.init_ui()

        self.work_area = CRect.from_sides(self.size_collector.draw_toolbar_panel,
                                          self.size_collector.menu_toolbar_panel,
                                          self.width() - self.size_collector.correction_panel,
                                          self.height() - self.size_collector.footer_panel)

        # region Render vars
        self.render_image = RenderImage()
        self.camera = Camera()
        # endregion

        # region UI widgets
        self.create_menu_bars()

        self.render_frame = RenderFrame(self)
        self.render_frame.setGeometry(*self.work_area)

        self.label_ram_memory = QLabel("RAM: ...", self)
        self.label_ram_memory.setObjectName("StatusBarLabel")

        self.label_mouse_pos = QLabel("Mouse pos: ...", self)
        self.label_mouse_pos.setObjectName("StatusBarLabel")

        self.label_image_size = QLabel("Image size: ...", self)
        self.label_image_size.setObjectName("StatusBarLabel")

        self.label_camera_scale = QLabel("Scale: 100%", self)
        self.label_camera_scale.setObjectName("StatusBarLabel")

        self.usage_timer = QTimer(self)
        self.usage_timer.timeout.connect(self.get_ram_usage)
        self.usage_timer.start(USAGE_TIMER_TICK_INTERVAL)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addWidget(self.label_mouse_pos)
        self.status_bar.addWidget(self.label_image_size)
        self.status_bar.addWidget(self.label_camera_scale)
        self.status_bar.addWidget(self.label_ram_memory)
        # endregion

        print_d(self.work_area)

    def init_ui(self):
        if self.form_position == Point(-1, -1):
            self.form_position.x = self.params.get("size_width", 1920) / 2 - self.form_size.width() / 2
            self.form_position.y = self.params.get("size_height", 1080) / 2 - self.form_size.height() / 2
        self.setGeometry(self.form_position.ix, self.form_position.iy, self.form_size.width(), self.form_size.height())

        self.setMinimumSize(self.size_collector.draw_toolbar_panel + self.size_collector.correction_panel + 200,
                            self.size_collector.menu_toolbar_panel + self.size_collector.footer_panel + 200)

        self.setWindowTitle(f"{APP_NAME} | {CONFIGURATION.name}")

    def resizeEvent(self, e: QResizeEvent) -> None:
        super(MainForm, self).resizeEvent(e)

        self.work_area.right = self.width() - self.size_collector.correction_panel
        self.work_area.bottom = self.height() - self.size_collector.footer_panel

        self.render_frame.setGeometry(*self.work_area)

    def update(self) -> None:
        super(MainForm, self).update()
        self.render_frame.update()

    def create_menu_bars(self):
        menu_bar = self.menuBar()
        file_menu = QMenu("File", self)

        menu_bar.addMenu(file_menu)

        open_file = QAction(_("OpenFileMenu"), self)
        open_file.triggered.connect(self.open_file_dialog)
        open_file.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        icon = QPixmap(self.resource_icon_dir + "baseline_file_open_black_24dp.png")
        open_file.setIcon(QIcon(icon))

        file_menu.addAction(open_file)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O:
            self.open_file_dialog()

    def scale_image(self, scale_val: Optional[float] = None) -> None:
        if scale_val is None:
            scale_val = self.camera.scale_factor
        else:
            self.camera.scale_factor = scale_val
        self.render_image.update_image(scale_val)
        self.label_camera_scale.setText(f"Scale: {round(scale_val * 100)}%")
        self.update()

    @pyqtSlot()
    def get_ram_usage(self):
        current, peak = tracemalloc.get_traced_memory()
        self.label_ram_memory.setText(
            f"RAM: {round(current / 10 ** 6)}Mb"
        )
        self.label_ram_memory.adjustSize()

    @pyqtSlot()
    def open_file_dialog(self) -> None:
        dialog_filter = f"{_('FilterImages')}(*.jpg *.jpeg *.png *tif *tiff);;" \
                        f"JPEG (*.jpg *.jpeg);;PNG (*.png);;" \
                        f"{_('FilterAll')} (*.*)"
        filename = QFileDialog.getOpenFileName(self, _("OpenFileTitle"), os.getcwd(),
                                               dialog_filter)[0]
        if filename != "":
            self.open_file(filename)

    def open_file(self, path: str) -> None:
        self.render_image.init_image(path)
        self.camera.reset()

        self.label_image_size.setText(f"Image size: {self.render_image.size.width()}x{self.render_image.size.height()}")

        gc.collect()
