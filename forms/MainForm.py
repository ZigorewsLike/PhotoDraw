import gc
import gettext
import os
import sys
import tracemalloc
from typing import Optional

from PyQt5.QtCore import QRect, QRectF, pyqtSlot, QTimer, QSize, Qt, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QResizeEvent, QPixmap, QIcon, QKeySequence, QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QLabel, QMenu, QAction, QFileDialog

# region src imports
from PyQt5.QtWinExtras import QWinTaskbarProgress

from src.global_constants import APP_NAME, CONFIGURATION, USAGE_TIMER_TICK_INTERVAL, LOG_SHOW_CONSOLE
from src.core.point_system import Point, CRect
from src.core.log import print_i, print_e, print_d, ConsoleWidget, StatusBarLogElement
from src.core.render import RenderFrame, RenderImage, Camera, PixmapIconEngine
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
        self.form_size = QSize(1200, 900)
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

        self.console = ConsoleWidget()
        sys.stdout.widget_print.connect(self.console.print_text)
        self.console.setParent(self)
        self.console.setVisible(LOG_SHOW_CONSOLE)

        self.label_ram_memory = QLabel("RAM: ...", self)
        self.label_ram_memory.setObjectName("StatusBarLabel")

        self.label_mouse_pos = QLabel("Mouse pos: ...", self)
        self.label_mouse_pos.setObjectName("StatusBarLabel")

        self.label_image_size = QLabel("Image size: ...", self)
        self.label_image_size.setObjectName("StatusBarLabel")

        self.label_camera_scale = QLabel("Scale: 100%", self)
        self.label_camera_scale.setObjectName("StatusBarLabel")

        self.widget_error_count = StatusBarLogElement(self.resource_icon_dir + "baseline_error_white_24dp.png", "0",
                                                      self)
        self.widget_error_count.color = QColor("#00FE35")

        self.widget_warning_count = StatusBarLogElement(self.resource_icon_dir + "baseline_error_white_24dp.png", "0",
                                                        self)
        self.widget_warning_count.color = QColor("#FFFF4E")

        self.usage_timer = QTimer(self)
        self.usage_timer.timeout.connect(self.get_ram_usage)
        self.usage_timer.start(USAGE_TIMER_TICK_INTERVAL)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addWidget(self.label_mouse_pos)
        self.status_bar.addWidget(self.label_image_size)
        self.status_bar.addWidget(self.label_camera_scale)
        self.status_bar.addWidget(self.label_ram_memory)

        self.status_bar.addPermanentWidget(self.widget_error_count)
        self.status_bar.addPermanentWidget(self.widget_warning_count)
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
        self.recalculate_size()

    def recalculate_size(self):
        self.work_area.right = self.width() - self.size_collector.correction_panel
        self.work_area.bottom = self.height() - self.size_collector.footer_panel

        self.render_frame.setGeometry(*self.work_area)
        self.render_image.buffer_size = CRect(0, 0, self.render_frame.width(), self.render_frame.height())
        self.update_buffer(self.camera.position)

        self.console.move(self.work_area.left, self.height() - self.size_collector.footer_panel - self.console.height())
        self.console.resize(int(self.work_area.width), self.console.height())

        self.update_buffer()

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

        help_menu = menu_bar.addMenu("dev")

        console = QAction("Console", self)
        console.triggered.connect(lambda: self.open_console())
        console.setShortcut(QKeySequence(Qt.Key_F12))

        help_menu.addAction(console)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O:
            self.open_file_dialog()

    def update_buffer(self, camera_pos: Optional[Point] = None):
        if camera_pos is None:
            camera_pos = self.camera.position
        for layer in [self.render_image]:
            layer: RenderImage
            layer.update_buffer(camera_pos)

    def scale_image(self, scale_val: Optional[float] = None) -> None:
        if scale_val is None:
            scale_val = self.camera.scale_factor
        else:
            self.camera.scale_factor = scale_val
        self.render_image.scale_buffer(scale_val)
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
    def open_console(self):
        if not self.console.isVisible():
            self.console.show()
        else:
            self.console.close()
        self.recalculate_size()
        print_d("OPEN Console", self.console.isVisible())

    @pyqtSlot()
    def update_console_counter(self):
        self.widget_error_count.text.setText(str(self.console.counter.get("ERROR", 0)))
        self.widget_warning_count.text.setText(str(self.console.counter.get("WARNING", 1)))

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
        self.update()
        self.camera.reset()

        self.label_image_size.setText(f"Image size: {self.render_image.size.width()}x{self.render_image.size.height()}")

        gc.collect()
