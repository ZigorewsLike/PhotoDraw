import gc
import gettext
import os
import sys
import tracemalloc
from datetime import datetime
from typing import Optional
import pickle

import numpy as np
import cv2

from PyQt5.QtCore import pyqtSlot, QTimer, QSize, Qt
from PyQt5.QtGui import QColor, QResizeEvent, QPixmap, QIcon, QKeySequence, QKeyEvent, QShowEvent
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QLabel, QMenu, QAction, QFileDialog, QToolBar, QSplitter

# region src imports
from src.global_constants import APP_NAME, CONFIGURATION, USAGE_TIMER_TICK_INTERVAL, LOG_SHOW_CONSOLE, DEBUG, \
    PATH_TO_LAST_FILES, PATH_TO_LAST_PREVIEW
from src.core.point_system import Point, CRect, SizeCollector
from src.core.log import print_e, print_d, ConsoleWidget, StatusBarLogElement
from src.core.render import RenderFrame, RenderImage, Camera, CorrectionSettings, RightPanelWidget
from src.enums import StateMode
from src.core.file_system import HomePage, LastFileContainer, LastFileProp
from core.gpu.cl import print_all_device_info, OPENCL_ENABLED

# endregion


# region Lang installation
lang = gettext.translation('mainForm', localedir='locales', languages=['ru'])
lang.install()
_ = lang.gettext
# endregion

if DEBUG:
    print_all_device_info()


class MainForm(QMainWindow):
    resource_dir: str = "resources/"
    resource_icon_dir: str = f"{resource_dir}icons/"
    lang = _

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
        QToolBar{
            // Future styles 
        }
        """)

        self.params = params
        self.form_position: Point = Point(-1., -1.)
        self.form_size = QSize(1200, 900)
        self.state: StateMode = StateMode.HOME
        self.size_collector = SizeCollector(self.state)

        self.init_ui()

        self.work_area = CRect.from_sides(self.size_collector.draw_toolbar_panel,
                                          self.size_collector.menu_toolbar_panel,
                                          self.width() - self.size_collector.correction_panel,
                                          self.height() - self.size_collector.footer_panel)

        # region Render vars
        self.options: CorrectionSettings = CorrectionSettings()
        self.render_image = RenderImage()
        self.render_image.options = self.options
        self.camera = Camera()
        # endregion

        try:
            if os.path.exists(PATH_TO_LAST_FILES):
                with open(PATH_TO_LAST_FILES, "rb") as f:
                    self.last_files_props: LastFileContainer = pickle.load(f)
            else:
                raise FileNotFoundError("File last not found")
        except Exception as e:
            print_e(e)
            self.last_files_props = LastFileContainer()
        print_d(self.last_files_props.count)

        # region UI widgets
        self.create_menu_bars()

        self.render_frame = RenderFrame(self)
        self.render_frame.setGeometry(*self.work_area)

        self.right_panel_widget = RightPanelWidget(self, self)
        self.right_panel_widget.image_correction_widget.options = self.options

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

        self.home_page = HomePage(self)

        self.console = ConsoleWidget()
        sys.stdout.widget_print.connect(self.console.print_text)  # noqa
        self.console.setParent(self)
        self.console.setVisible(LOG_SHOW_CONSOLE)
        # endregion

    def init_ui(self):
        if self.form_position == Point(-1, -1):
            self.form_position.x = self.params.get("size_width", 1920) / 2 - self.form_size.width() / 2
            self.form_position.y = self.params.get("size_height", 1080) / 2 - self.form_size.height() / 2
        self.setGeometry(self.form_position.ix, self.form_position.iy, self.form_size.width(), self.form_size.height())

        self.setMinimumSize(600,
                            self.size_collector.menu_toolbar_panel + self.size_collector.footer_panel + 200)

        self.setWindowTitle(f"{APP_NAME} | {CONFIGURATION.name}")

    def showEvent(self, event: QShowEvent) -> None:
        self.render_frame.show_scroll_bars(False)
        self.home_page.last_grid.generate_grid(self.last_files_props.props)

    def resizeEvent(self, e: QResizeEvent) -> None:
        super(MainForm, self).resizeEvent(e)
        self.recalculate_size()

    def recalculate_size(self):
        self.work_area.right = self.width() - self.size_collector.correction_panel
        self.work_area.bottom = self.height() - self.size_collector.footer_panel
        self.work_area.left = self.size_collector.draw_toolbar_panel
        self.work_area.top = self.size_collector.menu_toolbar_panel

        self.right_panel_widget.resize(min(self.right_panel_widget.width(), self.width() - 400), self.height())
        self.right_panel_widget.move(self.work_area.right, self.work_area.top)

        self.render_frame.setGeometry(*self.work_area)
        self.render_image.buffer_size = CRect(0, 0, self.render_frame.width(), self.render_frame.height())
        # self.update_buffer(self.camera.position)
        if self.state is StateMode.HOME:
            self.home_page.setGeometry(*self.work_area)

        self.render_frame.scroll_value_update(update_max=True)

        self.console.move(self.work_area.left, self.height() - self.size_collector.footer_panel - self.console.height())
        self.console.resize(int(self.work_area.width), self.console.height())

        self.scale_image(self.camera.scale_factor)

    def set_state_mode(self, state: StateMode) -> None:
        self.state = state
        self.size_collector.state = self.state
        work_enabled = state is StateMode.HOME
        self.home_page.setVisible(work_enabled)
        self.home_page.last_grid.generate_grid(self.last_files_props.props)
        self.recalculate_size()

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

        home_menu = QAction('&Домашняя страница', self)
        home_menu.triggered.connect(lambda: self.set_state_mode(StateMode.HOME))
        icon = QPixmap(self.resource_icon_dir + "baseline_home_black_24dp.png")
        home_menu.setIcon(QIcon(icon))

        file_menu.addAction(home_menu)
        file_menu.addAction(open_file)
        file_menu.addSeparator()

        file_tool_bar = QToolBar("File")

        file_tool_bar.addAction(home_menu)
        file_tool_bar.addAction(open_file)
        file_tool_bar.setMovable(False)
        file_tool_bar.setContextMenuPolicy(Qt.NoContextMenu)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.addToolBar(file_tool_bar)

        help_menu = menu_bar.addMenu("dev")

        console = QAction("Console", self)
        console.triggered.connect(lambda: self.open_console())
        console.setShortcut(QKeySequence(Qt.Key_F12))

        help_menu.addAction(console)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O:
            self.open_file_dialog()

    # region Buffer functions
    def adjust_camera_position(self):
        return
        # print_d(self.render_image.size.width() * self.camera.scale_factor, self.render_image.buffer.shape, self.camera.scale_factor)
        # sub = (self.render_image.buffer.shape[1] - self.render_frame.width()) / self.render_image.scale_factor
        # print_d(sub)
        # print_d(self.render_image.size.width() * self.camera.scale_factor - self.render_image.buffer.shape[1], '\n')

        # if self.camera.free_control:
        #     self.camera.position.x = median(-(self.render_image.size.width() * self.camera.scale_factor +
        #                                       self.camera.limit - self.render_frame.width()),
        #                                     self.camera.position.x,
        #                                     self.camera.limit)
        #     self.camera.position.y = median(-(self.render_image.size.height() * self.camera.scale_factor +
        #                                       self.camera.limit - self.render_frame.height()),
        #                                     self.camera.position.y,
        #                                     self.camera.limit)
        pass

    def update_buffer(self, camera_pos: Optional[Point] = None):
        if camera_pos is None:
            camera_pos = self.camera.position
        for layer in [self.render_image]:
            layer: RenderImage
            layer.update_buffer(camera_pos)

    def scale_image(self, scale_val: Optional[float] = None) -> None:

        old_width = self.render_image.size.width() * self.camera.scale_factor
        old_height = self.render_image.size.height() * self.camera.scale_factor

        if scale_val is not None:
            self.camera.scale_factor = scale_val

            calc_width: int = int(self.render_image.size.width() * self.camera.scale_factor)
            calc_height: int = int(self.render_image.size.height() * self.camera.scale_factor)

            if calc_width < self.render_frame.width() and calc_height < self.render_frame.height():
                self.camera.free_control = False
                self.camera.position = Point((self.render_frame.width() - calc_width) / 2,
                                             (self.render_frame.height() - calc_height) / 2)
            else:
                self.camera.free_control = True

                # Ratio is the upper left normalised position
                ratio: Point = Point((max(0, self.render_image.buffer_size.left) +
                                      self.camera.event_position.x()) / old_width,
                                     (self.render_image.buffer_size.top +
                                      self.camera.event_position.y()) / old_height)

                new_pos: Point = Point((old_width - self.render_image.size.width() * scale_val) * ratio.x,
                                       (old_height - self.render_image.size.height() * scale_val) * ratio.y)
                self.camera.position += new_pos
            self.render_frame.show_scroll_bars(self.camera.free_control)
            self.render_frame.scroll_value_update(update_max=True)
            self.render_frame.scroll_value_update()

        self.render_image.scale_buffer(self.camera.scale_factor, update_buffer=False)
        if DEBUG:
            self.label_camera_scale.setText(f"Scale: {round(self.camera.scale_factor, 2)} | "
                                            f"{round(self.render_image.scale_factor, 2)}")
        else:
            self.label_camera_scale.setText(f"Scale: {round(self.camera.scale_factor * 100)}%")

        self.update_buffer(self.camera.position)

        self.update()

    # endregion

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
        # self.widget_warning_count.text.setText(str(self.console.counter.get("WARNING", 1)))

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
        self.camera.reset()
        self.set_state_mode(StateMode.WORK)

        self.render_image.init_image(path)
        self.render_image.get_unique_pixels()
        preview: np.ndarray = self.render_image.generate_preview()

        normal_scale = min(self.render_image.buffer_size.width / self.render_image.size.width(),
                           self.render_image.buffer_size.height / self.render_image.size.height())
        self.camera.scale_step = 1 / (normal_scale / 1000)
        if normal_scale < 1:
            self.scale_image(normal_scale - 0.01)
        else:
            self.scale_image(1)

        self.right_panel_widget.image_correction_widget.reset_options()

        self.label_image_size.setText(f"Image size: {self.render_image.size.width()}x{self.render_image.size.height()}")
        self.label_camera_scale.setText(f"Scale: {round(self.camera.scale_factor * 100)}%")

        file_item = LastFileProp(path, datetime.now())
        self.last_files_props.add(file_item)
        cv2.cvtColor(preview, cv2.COLOR_BGR2RGB, preview)
        cv2.imwrite(f'{PATH_TO_LAST_PREVIEW}{file_item.hash_path}.jpg', preview)

        gc.collect()
