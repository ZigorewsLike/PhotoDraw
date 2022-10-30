import ctypes
import os
import sys

from PyQt5 import QtWidgets, QtCore
import gettext

# region Forms imports
from forms.MainForm import MainForm
# endregion

# region src imports
from src.global_constants import APP_NAME, CONFIGURATION, ConfigurationMode
from src.core.log import print_i, print_e, print_d
from src.core.log import except_hook, OutputBuffer
# endregion

import tracemalloc
tracemalloc.start(1)


if __name__ == '__main__':

    # std overwrite
    sys.excepthook = except_hook
    sys.stdout = OutputBuffer()
    if CONFIGURATION is ConfigurationMode.RELEASE:
        os.system('cls')  # For Release

    # region Lang installation
    lang = gettext.translation('base', localedir='locales', languages=['ru'])
    lang.install()
    _ = lang.gettext
    # endregion

    print_i(_("Run app ..."))

    for _dir in ['logs', 'data', 'data/preview']:
        if not os.path.exists(_dir):
            os.makedirs(_dir)

    # region dpi correct
    default_pdi = 96
    user32 = ctypes.windll.user32
    w_curr = user32.GetSystemMetrics(0)
    user32.SetProcessDPIAware()
    w_phys = user32.GetSystemMetrics(0)
    curr_dpi = round(w_phys * default_pdi / w_curr, 0)

    # TODO: The scale of rendering the image with HighDPI has wrong value.
    os.environ["QT_SCALE_FACTOR"] = str(curr_dpi / default_pdi)
    os.environ["QT_FONT_DPI"] = "96"
    # endregion

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")

    screen = app.primaryScreen()
    size = screen.size()
    params_dist: dict = {"size_width": size.width(), "size_height": size.height()}

    # region Run App
    form = MainForm(params_dist)
    form.show()
    # endregion

    app.exec_()
    print_i("Safe exit")
