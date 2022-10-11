import ctypes
import os
import sys

from PyQt5 import QtWidgets, QtCore

# region Forms imports
from forms.MainForm import MainForm
# endregion

# region src imports
from src.core.Log import except_hook
# endregion

import tracemalloc
tracemalloc.start(1)


if __name__ == '__main__':
    # std overwrite
    sys.excepthook = except_hook

    # region dpi correct
    default_pdi = 96
    user32 = ctypes.windll.user32
    w_curr = user32.GetSystemMetrics(0)
    user32.SetProcessDPIAware()
    w_phys = user32.GetSystemMetrics(0)
    curr_dpi = round(w_phys * default_pdi / w_curr, 0)

    os.environ["QT_SCALE_FACTOR"] = str(curr_dpi / default_pdi)
    os.environ["QT_FONT_DPI"] = "96"
    # endregion

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PhotoDraw")

    screen = app.primaryScreen()
    size = screen.size()
    params_dist: dict = {"size_width": size.width(), "size_height": size.height()}

    # region Run App
    form = MainForm(params_dist)
    form.show()
    # endregion

    app.exec_()
